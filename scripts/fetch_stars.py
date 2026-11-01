#!/usr/bin/env python3
"""
Refresh GitHub star counts in data/packages.json.

Run from the site root:
    python3 scripts/fetch_stars.py

Set GITHUB_TOKEN to avoid unauthenticated rate limits (optional).
"""

import json
import os
import sys
import urllib.request

PACKAGES = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "data", "packages.json")
)


def fetch_stars(repo: str) -> int:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}",
        headers={"Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)["stargazers_count"]


def main():
    with open(PACKAGES, encoding="utf-8") as f:
        packages = json.load(f)

    for pkg in packages:
        try:
            pkg["stars"] = fetch_stars(pkg["repo"])
        except Exception as exc:
            print(f"WARNING: {pkg['repo']}: {exc}; keeping {pkg.get('stars')}", file=sys.stderr)
            continue
        print(f"{pkg['repo']:30s} {pkg['stars']}")

    with open(PACKAGES, "w", encoding="utf-8") as f:
        json.dump(packages, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Written → {PACKAGES}")


if __name__ == "__main__":
    main()
