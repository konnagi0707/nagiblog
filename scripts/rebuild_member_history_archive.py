#!/usr/bin/env python3
"""Rebuild member history archive (profile + monthly greeting) for 小島凪紗."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse
from urllib.request import Request, urlopen

BASE_URL = "https://sakurazaka46.com"
MEMBER_URL = BASE_URL + "/s/s46/artist/62?ima=0000"
GREETING_URL = BASE_URL + "/s/s46/page/greeting?ima=0000"
ARTIST_PATH_PATTERN = "sakurazaka46.com/s/s46/artist/62*"
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

# Community-collated official image URLs used only when official archives miss months.
# Source threads:
# - http://krsw.5ch.net/test/read.cgi/sakurazaka46/1723164478/
# - http://krsw.5ch.net/test/read.cgi/sakurazaka46/1759741575/
WEB_RECOVERED_GREETING_MONTHS: dict[str, dict[str, str]] = {
    "2023-07": {
        "cardOriginal": BASE_URL + "/images/14/65a/2175019b0807171c8afa3701f8b94.jpg",
        "photoOriginal": BASE_URL + "/images/14/65a/2175019b0807171c8afa3701f8b94-01.jpg",
        "sourceUrl": "http://krsw.5ch.net/test/read.cgi/sakurazaka46/1723164478/",
    },
    "2023-08": {
        "cardOriginal": BASE_URL + "/images/14/214/5514f902e2c48f8a6f56e2eeddbe8.jpg",
        "photoOriginal": BASE_URL + "/images/14/214/5514f902e2c48f8a6f56e2eeddbe8-01.jpg",
        "sourceUrl": "http://krsw.5ch.net/test/read.cgi/sakurazaka46/1723164478/",
    },
    "2023-09": {
        "cardOriginal": BASE_URL + "/images/14/462/e76c3ccbee98f95e08bb725f5fc0d.jpg",
        "photoOriginal": BASE_URL + "/images/14/462/e76c3ccbee98f95e08bb725f5fc0d-01.jpg",
        "sourceUrl": "http://krsw.5ch.net/test/read.cgi/sakurazaka46/1723164478/",
    },
    "2023-10": {
        "cardOriginal": BASE_URL + "/images/14/8af/92f1731e4a74bee5c5e2a8471765b.jpg",
        "photoOriginal": BASE_URL + "/images/14/8af/92f1731e4a74bee5c5e2a8471765b-01.jpg",
        "sourceUrl": "http://krsw.5ch.net/test/read.cgi/sakurazaka46/1723164478/",
    },
    "2024-02": {
        "cardOriginal": BASE_URL + "/images/14/0af/ea6443f6fbf4e6a372fe7761f8386.jpg",
        "photoOriginal": BASE_URL + "/images/14/0af/ea6443f6fbf4e6a372fe7761f8386-01.jpg",
        "sourceUrl": "http://krsw.5ch.net/test/read.cgi/sakurazaka46/1723164478/",
    },
    "2024-03": {
        "cardOriginal": BASE_URL + "/images/14/a3c/a6c1d5686c5f7ca21e8d7c8fc2bf8.jpg",
        "photoOriginal": BASE_URL + "/images/14/a3c/a6c1d5686c5f7ca21e8d7c8fc2bf8-01.jpg",
        "sourceUrl": "http://krsw.5ch.net/test/read.cgi/sakurazaka46/1723164478/",
    },
}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

WAYBACK_CDX_URL = "https://web.archive.org/cdx/search/cdx"

# Curated official profile-photo timeline:
# debut + 6th..14th (10 entries)
PROFILE_TIMELINE = [
    {
        "single": "debut",
        "date": "2023-03-05",
        "newsUrl": BASE_URL + "/s/s46/news/detail/O00056?ima=0000",
        "originalSrc": BASE_URL + "/images/14/ca0/572ecb7cb460dba8b46b387d34bd3/1000_1000_102400.jpg",
    },
    {
        "single": "6th",
        "date": "2023-06-07",
        "newsUrl": BASE_URL + "/s/s46/news/detail/R00229?ima=0000",
        "originalSrc": BASE_URL + "/images/14/af7/a0011a634fa1ccec92d152ee39c91/1000_1000_102400.jpg",
    },
    {
        "single": "7th",
        "date": "2023-10-01",
        "newsUrl": BASE_URL + "/s/s46/news/detail/R00260?ima=0000",
        "originalSrc": BASE_URL + "/images/14/842/73cd105bf3acf943503d8249d69e4/1000_1000_102400.jpg",
    },
    {
        "single": "8th",
        "date": "2024-02-04",
        "newsUrl": BASE_URL + "/s/s46/news/detail/R00299?ima=0000",
        "originalSrc": BASE_URL + "/images/14/180/606c2dc266ddd3747e7e21558556c/1000_1000_102400.jpg",
    },
    {
        "single": "9th",
        "date": "2024-06-06",
        "newsUrl": BASE_URL + "/s/s46/news/detail/R00337?ima=0000",
        "originalSrc": BASE_URL + "/images/14/be0/fe91190770835022bc200192706bb/1000_1000_102400.jpg",
    },
    {
        "single": "10th",
        "date": "2024-10-03",
        "newsUrl": BASE_URL + "/s/s46/news/detail/R00379?ima=0000",
        "originalSrc": BASE_URL + "/images/14/85d/f84df7c62d914449bce4c1fdc86ea/1000_1000_102400.jpg",
    },
    {
        "single": "11th",
        "date": "2025-02-03",
        "newsUrl": BASE_URL + "/s/s46/news/detail/R00411?ima=0000",
        "originalSrc": BASE_URL + "/images/14/ea5/a2067241562a73164d6dbee181f64/1000_1000_102400.jpg",
    },
    {
        "single": "12th",
        "date": "2025-06-04",
        "newsUrl": BASE_URL + "/s/s46/news/detail/R00461?ima=0000",
        "originalSrc": BASE_URL + "/images/14/708/a6b4e3b457ed47f5694338bc46491/1000_1000_102400.jpg",
    },
    {
        "single": "13th",
        "date": "2025-10-01",
        "newsUrl": BASE_URL + "/s/s46/news/detail/R00496?ima=0000",
        "originalSrc": BASE_URL + "/images/14/833/2715333dadd74a1157f37fdbf0108/1000_1000_102400.jpg",
    },
    {
        "single": "14th",
        "date": "2026-02-02",
        "newsUrl": BASE_URL + "/s/s46/news/detail/R00521?ima=0000",
        "originalSrc": BASE_URL + "/images/14/44a/4e7a8c8ab86faba15404dffa70f48/1000_1000_102400.jpg",
    },
]


def fetch_text(url: str, timeout: int = 40, retries: int = 3) -> str:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=timeout) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset, errors="replace")
        except Exception as exc:  # pragma: no cover - network I/O
            last_error = exc
            if attempt < retries - 1:
                time.sleep(0.5 * (attempt + 1))
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Unable to fetch text: {url}")


def fetch_bytes(url: str, referer: str, timeout: int = 40, retries: int = 3) -> bytes:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Referer": referer})
            with urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:  # pragma: no cover - network I/O
            last_error = exc
            if attempt < retries - 1:
                time.sleep(0.5 * (attempt + 1))
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Unable to fetch bytes: {url}")


def write_json(payload: object, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


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


def resolve_ext_from_url(url: str, default_ext: str = ".jpg") -> str:
    ext = Path(urlparse(url).path).suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return ext
    return default_ext


def safe_filename(name: str, default: str) -> str:
    raw = name.strip()
    if not raw:
        raw = default
    raw = re.sub(r"[^A-Za-z0-9._-]+", "_", raw)
    raw = raw.strip("._")
    return raw or default


def archive_image(
    remote_src: str,
    archive_group: str,
    archive_key: str,
    project_root: Path,
    image_sleep: float,
) -> str:
    ext = resolve_ext_from_url(remote_src)
    digest = hashlib.sha1(remote_src.encode("utf-8")).hexdigest()[:10]
    original_name = Path(urlparse(remote_src).path).name
    filename = safe_filename(original_name, f"{archive_group}{ext}")
    safe_key = re.sub(r"[^0-9A-Za-z_-]+", "_", archive_key).strip("_") or "unknown"
    relative_path = Path("data") / "member" / "archive" / archive_group / f"{safe_key}_{digest}_{filename}"
    absolute_path = project_root / relative_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)

    if not absolute_path.exists() or absolute_path.stat().st_size == 0:
        payload = fetch_bytes(remote_src, referer=MEMBER_URL)
        absolute_path.write_bytes(payload)
        time.sleep(max(0.0, image_sleep))

    return relative_path.as_posix()


def normalize_image_url(raw: str) -> str:
    value = raw.strip().strip("\"'")
    value = value.replace("\\/", "/")
    wayback_embed = re.search(r"/web/\d+(?:[a-z_]+)?/(https?://.+)$", value, re.I)
    if wayback_embed:
        value = wayback_embed.group(1)
    if value.startswith("//"):
        return f"https:{value}"
    if value.startswith("/"):
        return f"{BASE_URL}{value}"
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return urljoin(f"{BASE_URL}/", value)


def extract_candidate_images(fragment: str) -> list[str]:
    candidates: list[str] = []
    candidates.extend(re.findall(r"url\(([^)]+)\)", fragment, re.I))
    candidates.extend(re.findall(r"<img[^>]+src=[\"']([^\"']+)", fragment, re.I))
    candidates.extend(re.findall(r"https?://[^\"'\\s)]+/images/[^\"'\\s)]+\\.(?:jpg|jpeg|png|webp)", fragment, re.I))

    normalized: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        src = normalize_image_url(item)
        if "/images/" not in src:
            continue
        if not re.search(r"\.(?:jpg|jpeg|png|webp)(?:\?|$)", src, re.I):
            continue
        if src in seen:
            continue
        seen.add(src)
        normalized.append(src)
    return normalized


def choose_card_photo_pair(image_urls: list[str]) -> tuple[str, str] | None:
    if not image_urls:
        return None

    photo = next((u for u in image_urls if re.search(r"-01/[0-9_]+\.(?:jpg|jpeg|png|webp)(?:\?|$)", u, re.I)), None)
    card: str | None = None
    if photo and "-01/" in photo:
        base = photo.split("-01/")[0]
        card = next((u for u in image_urls if u.startswith(f"{base}/") and "-01/" not in u), None)

    if card is None:
        card = next((u for u in image_urls if "-01/" not in u), None)

    if photo is None:
        photo = next((u for u in image_urls if u != card), None)

    if card and photo and card != photo:
        return card, photo
    return None


def extract_member_block(page_html: str) -> str:
    patterns = [
        r"<li[^>]*class=\"[^\"]*card_62[^\"]*\"[^>]*>(.*?)</li>",
        r"<li[^>]*class=\"[^\"]*item_62[^\"]*\"[^>]*>(.*?)</li>",
    ]
    for pattern in patterns:
        match = re.search(pattern, page_html, re.S | re.I)
        if match:
            return match.group(0)

    marker = page_html.find("card_62")
    if marker < 0:
        marker = page_html.find("item_62")
    if marker < 0:
        return ""

    start = page_html.rfind("<li", 0, marker)
    if start < 0:
        start = max(0, marker - 5000)
    end = page_html.find("</li>", marker)
    if end < 0:
        end = min(len(page_html), marker + 7000)
    else:
        end += len("</li>")
    return page_html[start:end]


def parse_greeting_pair_from_html(page_html: str) -> tuple[str, str] | None:
    block = extract_member_block(page_html)
    pair = choose_card_photo_pair(extract_candidate_images(block))
    if pair:
        return pair
    return choose_card_photo_pair(extract_candidate_images(page_html))


def fetch_wayback_snapshot(ts: str, orig: str) -> tuple[str, str]:
    candidates = [
        f"https://web.archive.org/web/{ts}id_/{orig}",
        f"https://web.archive.org/web/{ts}/{orig}",
    ]
    if orig.startswith("https://"):
        alt = "http://" + orig[len("https://"):]
        candidates.append(f"https://web.archive.org/web/{ts}id_/{alt}")
        candidates.append(f"https://web.archive.org/web/{ts}/{alt}")
    elif orig.startswith("http://"):
        alt = "https://" + orig[len("http://"):]
        candidates.append(f"https://web.archive.org/web/{ts}id_/{alt}")
        candidates.append(f"https://web.archive.org/web/{ts}/{alt}")

    seen: set[str] = set()
    last_error: Exception | None = None
    for url in candidates:
        if url in seen:
            continue
        seen.add(url)
        try:
            return fetch_text(url, timeout=70, retries=4), url
        except Exception as exc:  # pragma: no cover - network I/O
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Unable to fetch snapshot: {ts} {orig}")


def collect_greeting_history_from_wayback() -> list[dict[str, str]]:
    query = (
        f"{WAYBACK_CDX_URL}?url="
        + quote("sakurazaka46.com/s/s46/page/greeting*", safe="")
        + "&output=json&fl=timestamp,original,statuscode,mimetype,digest"
        + "&from=2023&to=2026"
    )
    payload = json.loads(fetch_text(query, timeout=60, retries=5))
    if not isinstance(payload, list) or len(payload) < 2:
        return []

    rows = payload[1:]
    by_month: dict[str, list[tuple[str, str]]] = {}
    seen_snapshot: set[tuple[str, str]] = set()
    for row in rows:
        if not isinstance(row, list) or len(row) < 2:
            continue
        ts = str(row[0]).strip()
        orig = str(row[1]).strip()
        if not re.fullmatch(r"\d{14}", ts):
            continue

        key = (ts, orig)
        if key in seen_snapshot:
            continue
        seen_snapshot.add(key)
        month = f"{ts[:4]}-{ts[4:6]}"
        by_month.setdefault(month, []).append(key)

    month_items: list[dict[str, str]] = []
    for month in sorted(by_month.keys()):
        candidates = sorted(by_month[month], key=lambda item: item[0], reverse=True)
        for ts, orig in candidates:
            try:
                snapshot_html, snapshot_url = fetch_wayback_snapshot(ts=ts, orig=orig)
            except Exception:  # pragma: no cover - network I/O
                continue

            pair = parse_greeting_pair_from_html(snapshot_html)
            if not pair:
                continue

            card_src, photo_src = pair
            month_items.append(
                {
                    "timestamp": ts,
                    "month": month,
                    "updatedAt": f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}Z",
                    "snapshotUrl": snapshot_url,
                    "cardOriginal": card_src,
                    "photoOriginal": photo_src,
                }
            )
            time.sleep(0.03)
            break

    return sorted(month_items, key=lambda x: x["timestamp"])


def parse_greeting_pair_from_artist_html(page_html: str) -> tuple[str, str] | None:
    card_match = re.search(r'<p[^>]*class="part-card"[^>]*>\s*<img[^>]*src="([^"]+)"', page_html, re.I | re.S)
    photo_match = re.search(r'<p[^>]*class="part-cimg"[^>]*>\s*<img[^>]*src="([^"]+)"', page_html, re.I | re.S)
    if card_match and photo_match:
        return normalize_image_url(card_match.group(1)), normalize_image_url(photo_match.group(1))
    return parse_greeting_pair_from_html(page_html)


def collect_greeting_history_from_artist_wayback() -> list[dict[str, str]]:
    query = (
        f"{WAYBACK_CDX_URL}?url="
        + quote(ARTIST_PATH_PATTERN, safe="")
        + "&output=json&fl=timestamp,original,statuscode,mimetype,digest"
        + "&from=2023&to=2026"
    )
    payload = json.loads(fetch_text(query, timeout=60, retries=5))
    if not isinstance(payload, list) or len(payload) < 2:
        return []

    rows = payload[1:]
    by_month: dict[str, list[tuple[str, str]]] = {}
    seen_snapshot: set[tuple[str, str]] = set()
    for row in rows:
        if not isinstance(row, list) or len(row) < 2:
            continue
        ts = str(row[0]).strip()
        orig = str(row[1]).strip()
        if not re.fullmatch(r"\d{14}", ts):
            continue
        key = (ts, orig)
        if key in seen_snapshot:
            continue
        seen_snapshot.add(key)
        month = f"{ts[:4]}-{ts[4:6]}"
        by_month.setdefault(month, []).append(key)

    month_items: list[dict[str, str]] = []
    for month in sorted(by_month.keys()):
        candidates = sorted(by_month[month], key=lambda item: item[0], reverse=True)
        for ts, orig in candidates:
            try:
                snapshot_html, snapshot_url = fetch_wayback_snapshot(ts=ts, orig=orig)
            except Exception:  # pragma: no cover - network I/O
                continue

            pair = parse_greeting_pair_from_artist_html(snapshot_html)
            if not pair:
                continue

            card_src, photo_src = pair
            if "/images/" not in card_src or "/images/" not in photo_src:
                continue
            month_items.append(
                {
                    "timestamp": ts,
                    "month": month,
                    "updatedAt": f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}T{ts[8:10]}:{ts[10:12]}:{ts[12:14]}Z",
                    "snapshotUrl": snapshot_url,
                    "cardOriginal": card_src,
                    "photoOriginal": photo_src,
                }
            )
            time.sleep(0.02)
            break

    return sorted(month_items, key=lambda x: x["timestamp"])


def collect_greeting_history_from_web_recovery(
    existing_months: set[str],
) -> list[dict[str, str]]:
    recovered: list[dict[str, str]] = []
    for month, payload in WEB_RECOVERED_GREETING_MONTHS.items():
        if month in existing_months:
            continue
        card = str(payload.get("cardOriginal", "")).strip()
        photo = str(payload.get("photoOriginal", "")).strip()
        if not card or not photo:
            continue
        month_token = month.replace("-", "")
        recovered.append(
            {
                "timestamp": f"{month_token}01000000",
                "month": month,
                "updatedAt": f"{month}-01T00:00:00Z",
                "snapshotUrl": str(payload.get("sourceUrl", "")).strip(),
                "cardOriginal": card,
                "photoOriginal": photo,
            }
        )
    return sorted(recovered, key=lambda x: x["timestamp"])


def build_profile_history(
    project_root: Path,
    image_sleep: float,
    single_titles: dict[str, str],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for item in PROFILE_TIMELINE:
        single_label = str(item.get("single", "")).strip()
        local_src = archive_image(
            remote_src=item["originalSrc"],
            archive_group="profile",
            archive_key=f"{item['single']}_{item['date']}",
            project_root=project_root,
            image_sleep=image_sleep,
        )
        result.append(
            {
                "single": single_label,
                "singleTitle": resolve_single_title(single_label, single_titles),
                "updatedAt": f"{item['date']}T00:00:00Z",
                "sourceUrl": item["newsUrl"],
                "image": {
                    "src": local_src,
                    "originalSrc": item["originalSrc"],
                },
            }
        )
    return sorted(result, key=lambda x: x["updatedAt"], reverse=True)


def build_greeting_history(
    project_root: Path,
    image_sleep: float,
    member_data_path: Path,
) -> list[dict[str, object]]:
    entries = collect_greeting_history_from_wayback()
    fallback_entries = collect_greeting_history_from_artist_wayback()
    existing_months = {str(item.get("month", "")).strip() for item in entries if isinstance(item, dict)}
    for item in fallback_entries:
        month = str(item.get("month", "")).strip()
        if month and month not in existing_months:
            entries.append(item)
            existing_months.add(month)

    web_recovery_entries = collect_greeting_history_from_web_recovery(existing_months=existing_months)
    for item in web_recovery_entries:
        month = str(item.get("month", "")).strip()
        if month and month not in existing_months:
            entries.append(item)
            existing_months.add(month)

    # Always include current official pair.
    current_member = json.loads(member_data_path.read_text(encoding="utf-8"))
    current_images = current_member.get("images", {}) if isinstance(current_member, dict) else {}
    current_card = (
        current_images.get("greetingCard", {}).get("originalSrc", "")
        if isinstance(current_images.get("greetingCard"), dict)
        else ""
    )
    current_photo = (
        current_images.get("greetingPhoto", {}).get("originalSrc", "")
        if isinstance(current_images.get("greetingPhoto"), dict)
        else ""
    )

    current_month = time.strftime("%Y-%m", time.gmtime(time.time() + 9 * 3600))
    if current_card and current_photo:
        entries.append(
            {
                "timestamp": time.strftime("%Y%m%d%H%M%S", time.gmtime()),
                "month": current_month,
                "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "snapshotUrl": MEMBER_URL,
                "cardOriginal": current_card,
                "photoOriginal": current_photo,
            }
        )

    # Deduplicate by month; keep latest timestamp in month.
    unique_by_month: dict[str, dict[str, str]] = {}
    for item in entries:
        month = str(item.get("month", "")).strip()
        if not month:
            continue
        existing = unique_by_month.get(month)
        if existing is None or str(item.get("timestamp", "")) > str(existing.get("timestamp", "")):
            unique_by_month[month] = item

    deduped = sorted(unique_by_month.values(), key=lambda x: x["timestamp"], reverse=True)
    result: list[dict[str, object]] = []
    for item in deduped:
        card_local = archive_image(
            remote_src=item["cardOriginal"],
            archive_group="greeting_card",
            archive_key=item["month"],
            project_root=project_root,
            image_sleep=image_sleep,
        )
        photo_local = archive_image(
            remote_src=item["photoOriginal"],
            archive_group="greeting_photo",
            archive_key=item["month"],
            project_root=project_root,
            image_sleep=image_sleep,
        )
        result.append(
            {
                "month": item["month"],
                "updatedAt": item["updatedAt"],
                "sourceUrl": item["snapshotUrl"],
                "greetingCard": {
                    "src": card_local,
                    "originalSrc": item["cardOriginal"],
                },
                "greetingPhoto": {
                    "src": photo_local,
                    "originalSrc": item["photoOriginal"],
                },
            }
        )
    return result


def build_month_range(start_month: str, end_month: str) -> list[str]:
    sy, sm = map(int, start_month.split("-"))
    ey, em = map(int, end_month.split("-"))
    result: list[str] = []
    year, month = sy, sm
    while (year < ey) or (year == ey and month <= em):
        result.append(f"{year:04d}-{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild member history archive for 小島凪紗")
    parser.add_argument(
        "--member",
        type=Path,
        default=Path("data/member.json"),
        help="Current member json path (default: data/member.json)",
    )
    parser.add_argument(
        "--history",
        type=Path,
        default=Path("data/member_history.json"),
        help="Output history json path (default: data/member_history.json)",
    )
    parser.add_argument(
        "--image-sleep",
        type=float,
        default=0.03,
        help="Sleep seconds between image downloads",
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
    project_root = Path.cwd()
    if not args.member.exists():
        raise SystemExit(f"Missing member json: {args.member}")
    single_titles = load_single_titles(args.single_titles)

    profile_history = build_profile_history(
        project_root=project_root,
        image_sleep=max(0.0, args.image_sleep),
        single_titles=single_titles,
    )
    greeting_history = build_greeting_history(
        project_root=project_root,
        image_sleep=max(0.0, args.image_sleep),
        member_data_path=args.member,
    )

    payload = {
        "version": 2,
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "profileHistory": profile_history,
        "greetingHistory": greeting_history,
    }
    write_json(payload, args.history)

    print(f"Wrote {len(profile_history)} profile entries")
    print(f"Wrote {len(greeting_history)} greeting entries")
    covered_months = sorted({str(item.get("month", "")).strip() for item in greeting_history if isinstance(item, dict)})
    print(f"Greeting months covered ({len(covered_months)}): {', '.join(covered_months)}")
    expected_months = build_month_range("2023-03", "2026-02")
    missing_months = [month for month in expected_months if month not in set(covered_months)]
    print(f"Missing months in 2023-03..2026-02 ({len(missing_months)}): {', '.join(missing_months) if missing_months else 'none'}")
    print(f"History path: {args.history}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
