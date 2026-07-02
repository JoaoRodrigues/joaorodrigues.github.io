#!/usr/bin/env python3
"""
Scrape publications from Google Scholar and write to data/publications.json.

Run from the site root:
    python3 scripts/fetch_publications.py
"""

import urllib.request
import http.cookiejar
import urllib.error
import re
import html as html_module
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

SCHOLAR_URL = (
    "https://scholar.google.com/citations"
    "?user=UeXRdzQAAAAJ&sortby=pubdate&cstart=0&pagesize=100"
)
SCHOLAR_BASE = "https://scholar.google.com"
OUTPUT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "data", "publications.json")
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

_jar = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_jar))


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with _opener.open(req, timeout=20) as resp:
        return resp.read().decode("utf-8")


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def clean(s: str) -> str:
    return html_module.unescape(strip_tags(s)).strip()


def parse_profile(page: str) -> list[dict]:
    publications = []
    rows = re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', page, re.DOTALL)
    for row in rows:
        m = re.search(r'<a href="(/citations\?[^"]+)" class="gsc_a_at">(.*?)</a>', row)
        if not m:
            continue
        scholar_url = SCHOLAR_BASE + html_module.unescape(m.group(1))
        title = clean(m.group(2))

        grays = re.findall(r'<div class="gs_gray">(.*?)</div>', row, re.DOTALL)
        authors = clean(grays[0]) if len(grays) > 0 else ""
        venue   = clean(grays[1]) if len(grays) > 1 else ""

        ym = re.search(r'<span class="gsc_a_h[^"]*"[^>]*>(\d{4})</span>', row)
        year = int(ym.group(1)) if ym else 0

        publications.append({
            "title": title,
            "authors": authors,
            "venue": venue,
            "year": year,
            "scholar_url": scholar_url,
            "url": None,
        })
    return publications


def fetch_article_url(scholar_url: str) -> str | None:
    """Fetch a Scholar citation page and return the direct article URL, if any."""
    try:
        page = fetch(scholar_url)
        m = re.search(r'<a[^>]+class="gsc_oci_title_link"[^>]+href="([^"]+)"', page)
        if m:
            return html_module.unescape(m.group(1))
    except Exception:
        pass
    return None


def enrich(pubs: list[dict]) -> list[dict]:
    """Add direct article URLs by fetching each Scholar citation page concurrently."""
    total = len(pubs)

    def worker(item):
        idx, pub = item
        return idx, fetch_article_url(pub["scholar_url"])

    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(worker, (i, p)): i for i, p in enumerate(pubs)}
        done = 0
        for fut in as_completed(futures):
            idx, url = fut.result()
            pubs[idx]["url"] = url
            done += 1
            print(f"  [{done}/{total}] {pubs[idx]['title'][:60]:60s}  {url or '(no link)'}")
            time.sleep(0.05)

    return pubs


def main():
    print("Fetching profile …")
    page = fetch(SCHOLAR_URL)
    pubs = parse_profile(page)
    if not pubs:
        print("ERROR: no publications parsed — Scholar may have blocked the request.", file=sys.stderr)
        sys.exit(1)
    print(f"Parsed {len(pubs)} publications. Fetching article URLs …")

    pubs = enrich(pubs)

    found = sum(1 for p in pubs if p["url"])
    print(f"\nArticle URLs found: {found}/{len(pubs)}")

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(pubs, f, indent=2, ensure_ascii=False)
    print(f"Written → {OUTPUT}")


if __name__ == "__main__":
    main()
