#!/usr/bin/env python3
"""Fetch and archive 小島凪紗 official blogs + member profile into local files.

Default behavior is incremental for blog posts: only fetch newly published posts.
Use --full to rebuild all posts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from html import unescape
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

BASE_URL = "https://sakurazaka46.com"
LIST_URL = BASE_URL + "/s/s46/diary/blog/list?ima=0000&ct=62&cd=blog"
LIST_URL_PAGED = BASE_URL + "/s/s46/diary/blog/list?ima=0000&ct=62&cd=blog&page={page}"
DETAIL_URL = BASE_URL + "/s/s46/diary/detail/{detail_id}?ima=0000&cd=blog"
MEMBER_URL = BASE_URL + "/s/s46/artist/62?ima=0000"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

DEFAULT_SINGLE_TITLES_PATH = Path("data/member_single_titles.json")
DEFAULT_SINGLE_TITLES: dict[str, str] = {
    "debut": "初披露",
    "6th": "Start over!",
    "7th": "承認欲求",
    "8th": "何歳の頃に戻りたいのか？",
    "9th": "自業自得",
    "10th": "I want tomorrow to come",
    "11th": "UDAGAWA GENERATION",
    "12th": "Make or Break",
    "13th": "Addiction",
    "14th": "The growing up train",
}


def fetch_text(url: str, timeout: int = 30, retries: int = 3, referer: str | None = None) -> str:
    for attempt in range(1, retries + 1):
        try:
            headers = {"User-Agent": USER_AGENT}
            if referer:
                headers["Referer"] = referer
            req = Request(url, headers=headers)
            with urlopen(req, timeout=timeout) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset, errors="replace")
        except (HTTPError, URLError, TimeoutError) as err:
            if attempt >= retries:
                raise RuntimeError(f"Failed to fetch {url}: {err}") from err
            time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}")


def fetch_bytes(url: str, timeout: int = 30, retries: int = 3, referer: str | None = None) -> bytes:
    for attempt in range(1, retries + 1):
        try:
            headers = {"User-Agent": USER_AGENT}
            if referer:
                headers["Referer"] = referer
            req = Request(url, headers=headers)
            with urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except (HTTPError, URLError, TimeoutError) as err:
            if attempt >= retries:
                raise RuntimeError(f"Failed to fetch binary {url}: {err}") from err
            time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch binary {url}")


def extract_main_list_detail_ids(list_html: str) -> list[str]:
    main_ul_match = re.search(r'<ul class="com-blog-part[^>]*>(.*?)</ul>', list_html, re.S)
    if not main_ul_match:
        return []

    main_ul = main_ul_match.group(1)
    return re.findall(r'href="/s/s46/diary/detail/(\d+)\?ima=0000&cd=blog"', main_ul)


def collect_all_detail_ids(max_pages: int = 100) -> list[str]:
    seen: set[str] = set()
    ordered_ids: list[str] = []

    for page in range(0, max_pages):
        url = LIST_URL if page == 0 else LIST_URL_PAGED.format(page=page)
        html = fetch_text(url)
        detail_ids = extract_main_list_detail_ids(html)

        if not detail_ids:
            break

        for detail_id in detail_ids:
            if detail_id in seen:
                continue
            seen.add(detail_id)
            ordered_ids.append(detail_id)

    return ordered_ids


def collect_new_detail_ids(existing_ids: set[int], max_pages: int = 100) -> list[str]:
    """Collect only newly published IDs, stopping when first known ID appears."""
    if not existing_ids:
        return collect_all_detail_ids(max_pages=max_pages)

    new_ids: list[str] = []
    seen: set[str] = set()
    stop = False

    for page in range(0, max_pages):
        url = LIST_URL if page == 0 else LIST_URL_PAGED.format(page=page)
        html = fetch_text(url)
        detail_ids = extract_main_list_detail_ids(html)

        if not detail_ids:
            break

        for detail_id in detail_ids:
            int_id = int(detail_id)
            if int_id in existing_ids:
                stop = True
                break
            if detail_id in seen:
                continue
            seen.add(detail_id)
            new_ids.append(detail_id)

        if stop:
            break

    return new_ids


def html_fragment_to_text(fragment: str) -> str:
    fragment = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", fragment)
    fragment = re.sub(r"(?i)<br\s*/?>", "\n", fragment)
    fragment = re.sub(r"(?is)<[^>]+>", "", fragment)

    text = unescape(fragment)
    text = text.replace("\r", "")
    text = text.replace("\uFFFC", "")
    text = text.replace("￼", "")

    lines = [line.strip() for line in text.split("\n")]
    compact_lines: list[str] = []
    last_empty = False

    for line in lines:
        if not line:
            if not last_empty:
                compact_lines.append("")
            last_empty = True
        else:
            compact_lines.append(line)
            last_empty = False

    return "\n".join(compact_lines).strip()


def normalize_member_name(raw_name: str) -> str:
    return re.sub(r"\s+", "", raw_name)


def extract_hashtags(text: str, limit: int = 6) -> list[str]:
    matches = re.findall(r"[#＃]([0-9A-Za-zぁ-んァ-ヶ一-龯ー_]+)", text)
    result: list[str] = []
    seen: set[str] = set()

    for tag in matches:
        cleaned = tag.strip("_")
        if not cleaned:
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
        if len(result) >= limit:
            break

    return result


def parse_date(raw_date: str) -> str:
    # Example: 2025/08/27 20:39 -> 2025-08-27
    date_only = raw_date.strip().split(" ")[0]
    return date_only.replace("/", "-")


def extract_image_src(img_tag: str) -> str | None:
    match = re.search(r'src\s*=\s*"([^"]+)"', img_tag, re.I)
    if not match:
        match = re.search(r"src\s*=\s*'([^']+)'", img_tag, re.I)
    if not match:
        return None

    src = match.group(1).strip()
    if not src:
        return None

    return urljoin(BASE_URL, src)


def parse_content_blocks(content_html: str) -> list[dict[str, str]]:
    cleaned_html = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", content_html)

    blocks: list[dict[str, str]] = []
    cursor = 0

    for img_match in re.finditer(r"(?is)<img[^>]*>", cleaned_html):
        start, end = img_match.span()

        text_chunk = cleaned_html[cursor:start]
        text_value = html_fragment_to_text(text_chunk)
        if text_value:
            blocks.append({"type": "text", "text": text_value})

        src = extract_image_src(img_match.group(0))
        if src:
            blocks.append({"type": "image", "src": src})

        cursor = end

    tail_chunk = cleaned_html[cursor:]
    tail_text = html_fragment_to_text(tail_chunk)
    if tail_text:
        blocks.append({"type": "text", "text": tail_text})

    return blocks


def merge_content_text(blocks: list[dict[str, str]]) -> str:
    texts = [block["text"] for block in blocks if block.get("type") == "text" and block.get("text")]
    return "\n\n".join(texts).strip()


def safe_filename(name: str, default: str) -> str:
    raw = unquote(name).strip()
    if not raw:
        raw = default
    raw = re.sub(r"[^A-Za-z0-9._-]+", "_", raw)
    raw = raw.strip("._")
    return raw or default


def resolve_ext_from_url(url: str, default_ext: str = ".jpg") -> str:
    ext = Path(urlparse(url).path).suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return ext
    return default_ext


def save_remote_image(
    remote_src: str,
    relative_path: Path,
    project_root: Path,
    image_sleep: float,
    referer: str,
    force_download: bool = False,
) -> bool:
    absolute_path = project_root / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)

    if (not force_download) and absolute_path.exists() and absolute_path.stat().st_size > 0:
        return True

    try:
        payload = fetch_bytes(remote_src, referer=referer)
        absolute_path.write_bytes(payload)
        time.sleep(max(0.0, image_sleep))
        return True
    except Exception as err:
        print(f"[warn] image download failed src={remote_src} err={err}", file=sys.stderr)
        return False


def localize_post_images(
    post: dict[str, object],
    project_root: Path,
    image_sleep: float,
) -> None:
    post_id = int(post["id"])
    blocks = post.get("contentBlocks", [])

    if not isinstance(blocks, list):
        return

    for index, block in enumerate(blocks, start=1):
        if not isinstance(block, dict):
            continue
        if block.get("type") != "image":
            continue

        remote_src = str(block.get("src", "")).strip()
        if not remote_src:
            continue

        ext = resolve_ext_from_url(remote_src)
        original_name = Path(urlparse(remote_src).path).name
        filename = safe_filename(original_name, f"image_{index:03d}{ext}")
        filename = f"{index:03d}_{filename}"

        relative_path = Path("data") / "images" / str(post_id) / filename
        success = save_remote_image(
            remote_src=remote_src,
            relative_path=relative_path,
            project_root=project_root,
            image_sleep=image_sleep,
            referer=DETAIL_URL.format(detail_id=post_id),
        )

        block["originalSrc"] = remote_src
        block["src"] = relative_path.as_posix() if success else remote_src


def parse_detail(detail_id: str, detail_html: str) -> dict[str, object]:
    title_match = re.search(r'<h1 class="title">(.*?)</h1>', detail_html, re.S)
    title = html_fragment_to_text(title_match.group(1)) if title_match else f"blog-{detail_id}"

    name_match = re.search(r'<p class="name">(.*?)</p>', detail_html, re.S)
    member_name = html_fragment_to_text(name_match.group(1)) if name_match else "小島凪紗"

    blog_foot_match = re.search(
        r'<div class="blog-foot">(.*?)</div>\s*<div class="blog-foot-nav">',
        detail_html,
        re.S,
    )
    blog_foot_html = blog_foot_match.group(1) if blog_foot_match else ""

    date_match = re.search(r'<p class="date wf-a">(.*?)</p>', blog_foot_html, re.S)
    raw_date = html_fragment_to_text(date_match.group(1)) if date_match else ""
    date_value = parse_date(raw_date) if raw_date else "1970-01-01"

    content_match = re.search(
        r'<div class="box-article">(.*?)</div>\s*<div class="blog-foot">',
        detail_html,
        re.S,
    )
    content_html = content_match.group(1) if content_match else ""

    content_blocks = parse_content_blocks(content_html)
    content_text = merge_content_text(content_blocks)

    tags: list[str] = []
    member_tag = normalize_member_name(member_name)
    if member_tag:
        tags.append(member_tag)

    if re.match(r"\d{4}-\d{2}-\d{2}", date_value):
        tags.append(date_value[:7])

    for hashtag in extract_hashtags(content_text):
        if hashtag not in tags:
            tags.append(hashtag)

    return {
        "id": int(detail_id),
        "title": title,
        "date": date_value,
        "tags": tags or ["小島凪紗"],
        "content": content_text,
        "contentBlocks": content_blocks,
        "sourceUrl": DETAIL_URL.format(detail_id=detail_id),
    }


def extract_text_by_pattern(pattern: str, html: str, default: str = "") -> str:
    match = re.search(pattern, html, re.S)
    if not match:
        return default
    return html_fragment_to_text(match.group(1))


def parse_member_profile(member_html: str) -> dict[str, object]:
    profile_block_match = re.search(
        r'<div class="col3-wrap wid1200 member-profcont">(.*?)</div>\s*<div class="member-recent',
        member_html,
        re.S,
    )
    if not profile_block_match:
        raise RuntimeError("Failed to parse member profile block")

    profile_block = profile_block_match.group(1)

    name = extract_text_by_pattern(r'<p class="name">(.*?)</p>', profile_block, "小島 凪紗")
    kana = extract_text_by_pattern(r'<p class="kana">(.*?)</p>', profile_block, "")
    roman = extract_text_by_pattern(r'<p class="eigo[^>]*">(.*?)</p>', profile_block, "")

    profile_img_match = re.search(r'<div class="col-c">.*?(<img[^>]*>)', profile_block, re.S)
    profile_image = extract_image_src(profile_img_match.group(1)) if profile_img_match else ""

    greeting_card_match = re.search(r'<p class="part-card">\s*(<img[^>]*>)\s*</p>', profile_block, re.S)
    greeting_card_image = extract_image_src(greeting_card_match.group(1)) if greeting_card_match else ""

    greeting_photo_match = re.search(r'<p class="part-cimg">\s*(<img[^>]*>)\s*</p>', profile_block, re.S)
    greeting_photo_image = extract_image_src(greeting_photo_match.group(1)) if greeting_photo_match else ""

    greeting_list_match = re.search(
        r'<p class="greeting_list_btn[^>]*>\s*<a[^>]*href="([^"]+)"',
        profile_block,
        re.S,
    )
    greeting_list_url = urljoin(BASE_URL, greeting_list_match.group(1)) if greeting_list_match else ""

    attributes: list[dict[str, str]] = []
    for label_html, value_html in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", profile_block, re.S):
        label = html_fragment_to_text(label_html)
        value = html_fragment_to_text(value_html)
        if label and value:
            attributes.append({"label": label, "value": value})

    return {
        "id": 62,
        "name": name,
        "kana": kana,
        "roman": roman,
        "sourceUrl": MEMBER_URL,
        "greetingListUrl": greeting_list_url,
        "attributes": attributes,
        "images": {
            "profile": profile_image,
            "greetingCard": greeting_card_image,
            "greetingPhoto": greeting_photo_image,
        },
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def localize_member_images(
    member: dict[str, object],
    project_root: Path,
    image_sleep: float,
    previous_member: dict[str, object] | None = None,
) -> None:
    image_map = member.get("images", {})
    if not isinstance(image_map, dict):
        member["images"] = {}
        return

    previous_images = {}
    if isinstance(previous_member, dict):
        raw_previous_images = previous_member.get("images", {})
        if isinstance(raw_previous_images, dict):
            previous_images = raw_previous_images

    localized: dict[str, dict[str, str]] = {}
    key_to_prefix = {
        "profile": "profile",
        "greetingCard": "greeting_card",
        "greetingPhoto": "greeting_photo",
    }

    for key, prefix in key_to_prefix.items():
        remote_src = str(image_map.get(key, "")).strip()
        if not remote_src:
            continue

        ext = resolve_ext_from_url(remote_src)
        original_name = Path(urlparse(remote_src).path).name
        filename = safe_filename(original_name, f"{prefix}{ext}")
        relative_path = Path("data") / "member" / f"{prefix}_{filename}"

        previous_remote = ""
        previous_item = previous_images.get(key, "")
        if isinstance(previous_item, dict):
            previous_remote = str(previous_item.get("originalSrc") or "").strip()
        elif isinstance(previous_item, str):
            previous_remote = previous_item.strip()
        force_download = bool(previous_remote) and previous_remote != remote_src

        success = save_remote_image(
            remote_src=remote_src,
            relative_path=relative_path,
            project_root=project_root,
            image_sleep=image_sleep,
            referer=MEMBER_URL,
            force_download=force_download,
        )

        local_src = relative_path.as_posix() if success else remote_src
        localized[key] = {
            "src": local_src,
            "originalSrc": remote_src,
        }

    member["images"] = localized


def ordinal_suffix(number: int) -> str:
    if 10 <= number % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")


def detect_single_label_from_image_url(remote_src: str) -> str | None:
    path = urlparse(remote_src).path
    match = re.search(r"/images/(\d+)/", path)
    if not match:
        return None

    try:
        single_number = int(match.group(1))
    except ValueError:
        return None

    return f"{single_number}{ordinal_suffix(single_number)}"


def load_single_titles(single_titles_path: Path) -> dict[str, str]:
    table = dict(DEFAULT_SINGLE_TITLES)
    if not single_titles_path.exists():
        return table

    try:
        payload = json.loads(single_titles_path.read_text(encoding="utf-8"))
    except Exception:
        return table

    if not isinstance(payload, dict):
        return table

    for key, value in payload.items():
        single_key = str(key).strip()
        title = str(value).strip()
        if single_key and title:
            table[single_key] = title
    return table


def resolve_single_title(single_label: str, single_titles: dict[str, str]) -> str:
    label = str(single_label).strip()
    if not label:
        return ""
    return str(single_titles.get(label, "")).strip()


def current_tokyo_month() -> str:
    # Official greeting card/photo updates are monthly in JST.
    return time.strftime("%Y-%m", time.gmtime(time.time() + 9 * 3600))


def load_member_history(history_output_path: Path) -> dict[str, object]:
    if not history_output_path.exists():
        return {"version": 1, "profileHistory": [], "greetingHistory": []}

    try:
        payload = json.loads(history_output_path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "profileHistory": [], "greetingHistory": []}

    if not isinstance(payload, dict):
        return {"version": 1, "profileHistory": [], "greetingHistory": []}

    profile_history = payload.get("profileHistory", [])
    greeting_history = payload.get("greetingHistory", [])

    return {
        "version": int(payload.get("version", 1)),
        "updatedAt": str(payload.get("updatedAt", "")).strip(),
        "profileHistory": profile_history if isinstance(profile_history, list) else [],
        "greetingHistory": greeting_history if isinstance(greeting_history, list) else [],
    }


def archive_member_image(
    remote_src: str,
    archive_group: str,
    archive_key: str,
    project_root: Path,
    image_sleep: float,
) -> str:
    if not remote_src:
        return ""

    ext = resolve_ext_from_url(remote_src)
    digest = hashlib.sha1(remote_src.encode("utf-8")).hexdigest()[:10]
    original_name = Path(urlparse(remote_src).path).name
    filename = safe_filename(original_name, f"{archive_group}{ext}")
    safe_key = re.sub(r"[^0-9A-Za-z_-]+", "_", archive_key).strip("_") or "unknown"
    relative_path = Path("data") / "member" / "archive" / archive_group / f"{safe_key}_{digest}_{filename}"

    success = save_remote_image(
        remote_src=remote_src,
        relative_path=relative_path,
        project_root=project_root,
        image_sleep=image_sleep,
        referer=MEMBER_URL,
    )
    return relative_path.as_posix() if success else remote_src


def extract_original_src(image_entry: object) -> str:
    if isinstance(image_entry, dict):
        return str(image_entry.get("originalSrc") or "").strip()
    if isinstance(image_entry, str):
        return image_entry.strip()
    return ""


def upsert_member_history(
    member: dict[str, object],
    history_output_path: Path,
    project_root: Path,
    image_sleep: float,
    single_titles: dict[str, str],
) -> dict[str, object]:
    history = load_member_history(history_output_path)
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    images = member.get("images", {})
    if not isinstance(images, dict):
        images = {}

    profile_history = history.get("profileHistory", [])
    if not isinstance(profile_history, list):
        profile_history = []

    greeting_history = history.get("greetingHistory", [])
    if not isinstance(greeting_history, list):
        greeting_history = []

    # Profile photo archive (single-based).
    profile_entry = images.get("profile", {})
    profile_remote = extract_original_src(profile_entry)
    if profile_remote:
        latest_profile = profile_history[0] if profile_history and isinstance(profile_history[0], dict) else None
        latest_remote = ""
        if isinstance(latest_profile, dict):
            latest_remote = extract_original_src(latest_profile.get("image"))

        if latest_remote != profile_remote:
            single_label = detect_single_label_from_image_url(profile_remote) or "unknown"
            archive_src = archive_member_image(
                remote_src=profile_remote,
                archive_group="profile",
                archive_key=f"{single_label}_{now_iso[:10]}",
                project_root=project_root,
                image_sleep=image_sleep,
            )
            profile_history.insert(
                0,
                {
                    "single": single_label,
                    "singleTitle": resolve_single_title(single_label, single_titles),
                    "updatedAt": now_iso,
                    "image": {
                        "src": archive_src,
                        "originalSrc": profile_remote,
                    },
                },
            )

    # Greeting card/photo archive (monthly-based, append when image set changes).
    greeting_card_entry = images.get("greetingCard", {})
    greeting_photo_entry = images.get("greetingPhoto", {})
    greeting_card_remote = extract_original_src(greeting_card_entry)
    greeting_photo_remote = extract_original_src(greeting_photo_entry)

    if greeting_card_remote or greeting_photo_remote:
        latest_greeting = greeting_history[0] if greeting_history and isinstance(greeting_history[0], dict) else None
        latest_card_remote = ""
        latest_photo_remote = ""
        if isinstance(latest_greeting, dict):
            latest_card_remote = extract_original_src(latest_greeting.get("greetingCard"))
            latest_photo_remote = extract_original_src(latest_greeting.get("greetingPhoto"))

        if latest_card_remote != greeting_card_remote or latest_photo_remote != greeting_photo_remote:
            month_key = current_tokyo_month()
            archived_card_src = archive_member_image(
                remote_src=greeting_card_remote,
                archive_group="greeting_card",
                archive_key=month_key,
                project_root=project_root,
                image_sleep=image_sleep,
            ) if greeting_card_remote else ""
            archived_photo_src = archive_member_image(
                remote_src=greeting_photo_remote,
                archive_group="greeting_photo",
                archive_key=month_key,
                project_root=project_root,
                image_sleep=image_sleep,
            ) if greeting_photo_remote else ""

            new_entry = {
                "month": month_key,
                "updatedAt": now_iso,
                "greetingCard": {
                    "src": archived_card_src,
                    "originalSrc": greeting_card_remote,
                } if greeting_card_remote else {},
                "greetingPhoto": {
                    "src": archived_photo_src,
                    "originalSrc": greeting_photo_remote,
                } if greeting_photo_remote else {},
            }

            same_month_index = next(
                (
                    idx
                    for idx, item in enumerate(greeting_history)
                    if isinstance(item, dict) and str(item.get("month", "")).strip() == month_key
                ),
                None,
            )
            if same_month_index is None:
                greeting_history.insert(0, new_entry)
            else:
                greeting_history[same_month_index] = new_entry
                if same_month_index != 0:
                    moved = greeting_history.pop(same_month_index)
                    greeting_history.insert(0, moved)

    # Keep the newest entries first and cap size for long-term use.
    for item in profile_history:
        if not isinstance(item, dict):
            continue
        single_label = str(item.get("single", "")).strip()
        if not single_label:
            continue
        if not str(item.get("singleTitle", "")).strip():
            title = resolve_single_title(single_label, single_titles)
            if title:
                item["singleTitle"] = title

    profile_history = profile_history[:36]
    greeting_history = greeting_history[:36]

    history["profileHistory"] = profile_history
    history["greetingHistory"] = greeting_history
    history["updatedAt"] = now_iso
    history["version"] = 1

    if profile_history and isinstance(profile_history[0], dict):
        member["profileSingle"] = str(profile_history[0].get("single", "")).strip()
        member["profileSingleTitle"] = str(profile_history[0].get("singleTitle", "")).strip()
    if greeting_history and isinstance(greeting_history[0], dict):
        member["greetingMonth"] = str(greeting_history[0].get("month", "")).strip()

    write_json(history, history_output_path)
    return history


def fetch_member_profile(
    project_root: Path,
    output_path: Path,
    history_output_path: Path,
    image_sleep: float,
    single_titles: dict[str, str],
) -> dict[str, object]:
    previous_member: dict[str, object] | None = None
    if output_path.exists():
        try:
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                previous_member = payload
        except Exception:
            previous_member = None

    member_html = fetch_text(MEMBER_URL)
    member = parse_member_profile(member_html)
    localize_member_images(
        member,
        project_root=project_root,
        image_sleep=image_sleep,
        previous_member=previous_member,
    )
    upsert_member_history(
        member=member,
        history_output_path=history_output_path,
        project_root=project_root,
        image_sleep=image_sleep,
        single_titles=single_titles,
    )
    write_json(member, output_path)
    return member


def load_existing_posts(output_path: Path) -> list[dict[str, object]]:
    if not output_path.exists():
        return []

    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(payload, list):
        return []

    result: list[dict[str, object]] = []
    for item in payload:
        if isinstance(item, dict) and "id" in item:
            result.append(item)
    return result


def merge_posts(new_posts: list[dict[str, object]], existing_posts: list[dict[str, object]]) -> list[dict[str, object]]:
    merged: dict[int, dict[str, object]] = {}

    for post in existing_posts:
        try:
            merged[int(post["id"])] = post
        except Exception:
            continue

    for post in new_posts:
        merged[int(post["id"])] = post

    def sort_key(post: dict[str, object]) -> tuple[str, int]:
        return (str(post.get("date", "")), int(post.get("id", 0)))

    return sorted(merged.values(), key=sort_key, reverse=True)


def fetch_posts(
    detail_ids: list[str],
    project_root: Path,
    sleep_seconds: float,
    image_sleep: float,
) -> list[dict[str, object]]:
    posts: list[dict[str, object]] = []
    total = len(detail_ids)

    for index, detail_id in enumerate(detail_ids, start=1):
        url = DETAIL_URL.format(detail_id=detail_id)
        print(f"[{index}/{total}] Fetch detail {url}", file=sys.stderr)
        detail_html = fetch_text(url)
        post = parse_detail(detail_id, detail_html)
        localize_post_images(post, project_root=project_root, image_sleep=image_sleep)
        posts.append(post)
        time.sleep(max(0.0, sleep_seconds))

    return posts


def write_json(payload: object, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_posts_json(posts: Iterable[dict[str, object]], output_path: Path) -> None:
    write_json(list(posts), output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and archive 小島凪紗 official blogs + member profile")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/posts.json"),
        help="Blog output json path (default: data/posts.json)",
    )
    parser.add_argument(
        "--member-output",
        type=Path,
        default=Path("data/member.json"),
        help="Member output json path (default: data/member.json)",
    )
    parser.add_argument(
        "--member-history-output",
        type=Path,
        default=Path("data/member_history.json"),
        help="Member history output json path (default: data/member_history.json)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.12,
        help="Sleep seconds between detail requests (default: 0.12)",
    )
    parser.add_argument(
        "--image-sleep",
        type=float,
        default=0.03,
        help="Sleep seconds between image downloads (default: 0.03)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Re-fetch all posts and rebuild archive",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Maximum list pages to scan (default: 100)",
    )
    parser.add_argument(
        "--skip-member",
        action="store_true",
        help="Skip member profile fetching",
    )
    parser.add_argument(
        "--member-only",
        action="store_true",
        help="Only update member profile + member history, skip blog posts",
    )
    parser.add_argument(
        "--single-titles",
        type=Path,
        default=DEFAULT_SINGLE_TITLES_PATH,
        help="Single title mapping json path (default: data/member_single_titles.json)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    output_path = args.output
    project_root = Path.cwd()
    single_titles = load_single_titles(args.single_titles)

    if args.member_only:
        print("Member-only mode: skip blog post sync", file=sys.stderr)
        if not args.skip_member:
            try:
                member = fetch_member_profile(
                    project_root=project_root,
                    output_path=args.member_output,
                    history_output_path=args.member_history_output,
                    image_sleep=max(0.0, args.image_sleep),
                    single_titles=single_titles,
                )
                print(f"Wrote member profile for {member.get('name', 'member')} to {args.member_output}")
                print(f"Wrote member archive history to {args.member_history_output}")
            except Exception as err:
                print(f"[warn] member profile update failed: {err}", file=sys.stderr)
        return 0

    existing_posts = [] if args.full else load_existing_posts(output_path)
    existing_ids = {int(post["id"]) for post in existing_posts if "id" in post}

    if args.full:
        detail_ids = collect_all_detail_ids(max_pages=max(1, args.max_pages))
        print(f"Full mode: discovered {len(detail_ids)} posts", file=sys.stderr)
    else:
        detail_ids = collect_new_detail_ids(existing_ids=existing_ids, max_pages=max(1, args.max_pages))
        print(f"Incremental mode: discovered {len(detail_ids)} new posts", file=sys.stderr)

    if detail_ids:
        fetched_posts = fetch_posts(
            detail_ids,
            project_root=project_root,
            sleep_seconds=max(0.0, args.sleep),
            image_sleep=max(0.0, args.image_sleep),
        )
    else:
        fetched_posts = []

    if args.full:
        final_posts = merge_posts(fetched_posts, [])
    else:
        final_posts = merge_posts(fetched_posts, existing_posts)

    write_posts_json(final_posts, output_path)
    print(f"Wrote {len(final_posts)} posts to {output_path}")

    if not args.skip_member:
        try:
            member = fetch_member_profile(
                project_root=project_root,
                output_path=args.member_output,
                history_output_path=args.member_history_output,
                image_sleep=max(0.0, args.image_sleep),
                single_titles=single_titles,
            )
            print(f"Wrote member profile for {member.get('name', 'member')} to {args.member_output}")
            print(f"Wrote member archive history to {args.member_history_output}")
        except Exception as err:
            print(f"[warn] member profile update failed: {err}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
