#!/usr/bin/env python3
"""Fetch all official blogs for 小島 凪紗 and write data/posts.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from html import unescape
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

BASE_URL = "https://sakurazaka46.com"
LIST_URL = BASE_URL + "/s/s46/diary/blog/list?ima=0000&ct=62&cd=blog"
LIST_URL_PAGED = BASE_URL + "/s/s46/diary/blog/list?ima=0000&ct=62&cd=blog&page={page}"
DETAIL_URL = BASE_URL + "/s/s46/diary/detail/{detail_id}?ima=0000&cd=blog"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def fetch_text(url: str, timeout: int = 30, retries: int = 3) -> str:
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=timeout) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.read().decode(charset, errors="replace")
        except (HTTPError, URLError, TimeoutError) as err:
            if attempt >= retries:
                raise RuntimeError(f"Failed to fetch {url}: {err}") from err
            time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url}")


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


def html_fragment_to_text(fragment: str) -> str:
    fragment = re.sub(r'(?is)<(script|style).*?>.*?</\1>', '', fragment)
    fragment = re.sub(r'(?i)<br\s*/?>', '\n', fragment)
    fragment = re.sub(r'(?is)<img[^>]*>', '\n', fragment)
    fragment = re.sub(r'(?is)<[^>]+>', '', fragment)

    text = unescape(fragment)
    text = text.replace("\r", "")
    text = text.replace("\uFFFC", "")

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


def parse_detail(detail_id: str, detail_html: str) -> dict[str, object]:
    title_match = re.search(r'<h1 class="title">(.*?)</h1>', detail_html, re.S)
    title = html_fragment_to_text(title_match.group(1)) if title_match else f"blog-{detail_id}"

    name_match = re.search(r'<p class="name">(.*?)</p>', detail_html, re.S)
    member_name = html_fragment_to_text(name_match.group(1)) if name_match else "小島凪紗"

    blog_foot_match = re.search(r'<div class="blog-foot">(.*?)</div>\s*<div class="blog-foot-nav">', detail_html, re.S)
    blog_foot_html = blog_foot_match.group(1) if blog_foot_match else ""

    date_match = re.search(r'<p class="date wf-a">(.*?)</p>', blog_foot_html, re.S)
    raw_date = html_fragment_to_text(date_match.group(1)) if date_match else ""
    date_value = parse_date(raw_date) if raw_date else "1970-01-01"

    content_match = re.search(
        r'<div class="box-article">(.*?)</div>\s*<div class="blog-foot">',
        detail_html,
        re.S,
    )
    if content_match:
        content = html_fragment_to_text(content_match.group(1))
    else:
        content = ""

    tags: list[str] = []
    member_tag = normalize_member_name(member_name)
    if member_tag:
        tags.append(member_tag)

    if re.match(r"\d{4}-\d{2}-\d{2}", date_value):
        tags.append(date_value[:7])

    for hashtag in extract_hashtags(content):
        if hashtag not in tags:
            tags.append(hashtag)

    return {
        "id": int(detail_id),
        "title": title,
        "date": date_value,
        "tags": tags or ["小島凪紗"],
        "content": content,
        "sourceUrl": DETAIL_URL.format(detail_id=detail_id),
    }


def fetch_all_posts(sleep_seconds: float = 0.12) -> list[dict[str, object]]:
    detail_ids = collect_all_detail_ids()
    if not detail_ids:
        raise RuntimeError("No blog entries found for ct=62")

    posts: list[dict[str, object]] = []
    total = len(detail_ids)

    for index, detail_id in enumerate(detail_ids, start=1):
        url = DETAIL_URL.format(detail_id=detail_id)
        print(f"[{index}/{total}] Fetch {url}", file=sys.stderr)
        detail_html = fetch_text(url)
        post = parse_detail(detail_id, detail_html)
        posts.append(post)
        time.sleep(sleep_seconds)

    return posts


def write_posts_json(posts: Iterable[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = list(posts)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch all 小島凪紗 official blogs")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/posts.json"),
        help="Output json path (default: data/posts.json)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.12,
        help="Sleep seconds between detail requests (default: 0.12)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    posts = fetch_all_posts(sleep_seconds=max(0.0, args.sleep))
    write_posts_json(posts, args.output)
    print(f"Wrote {len(posts)} posts to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
