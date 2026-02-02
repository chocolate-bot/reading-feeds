#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Categorize OPML feeds into rough buckets and emit Markdown.

Heuristic, intentionally simple:
- Categorize by domain / title keywords.
- Keep original ordering within each category.

Usage:
  python3 scripts/categorize_opml.py sources/hn-2025-popular-blogs.opml > curated/hn-2025-categorized.md
"""

import re
import sys
import xml.etree.ElementTree as ET


def norm(s: str) -> str:
    return (s or "").strip()


def pick_category(title: str, html: str, xml: str) -> str:
    t = f"{title} {html} {xml}".lower()

    # security first
    if any(k in t for k in ["security", "krebson", "troyhunt", "vulnerability", "cve"]):
        return "Security"

    # AI / data-ish
    if any(k in t for k in ["simonwillison", "machine", "llm", "ai", "data", "statistics", "dynomight", "minimaxir"]):
        return "AI & Data"

    # programming / software
    if any(k in t for k in ["program", "dev", "coding", "engineering", "pocoo", "mitchellh", "matklad", "righto", "fabiensanglard", "beej", "oldnewthing", "jeffgeerling"]):
        return "Software & Systems"

    # essays / writing / internet culture
    if any(k in t for k in ["paulgraham", "daringfireball", "pluralistic", "substack", "newsletter", "essay", "blogspot", "bearblog", "theatlantic", "derekthompson", "joanwestenberg"]):
        return "Writing & Essays"

    # misc
    return "Misc"


def main():
    if len(sys.argv) != 2:
        print("usage: categorize_opml.py <file.opml>", file=sys.stderr)
        return 2

    path = sys.argv[1]
    raw = open(path, "r", encoding="utf-8", errors="replace").read()
    # Some gists prepend a human-readable line before the XML. Strip until <opml...
    m = re.search(r"<opml\b", raw)
    if not m:
        raise SystemExit("No <opml> tag found")
    xml_text = raw[m.start():]

    root = ET.fromstring(xml_text)

    items = []
    for outline in root.findall(".//outline"):
        if outline.attrib.get("type") != "rss":
            continue
        title = norm(outline.attrib.get("title") or outline.attrib.get("text"))
        xmlUrl = norm(outline.attrib.get("xmlUrl"))
        htmlUrl = norm(outline.attrib.get("htmlUrl"))
        if not xmlUrl:
            continue
        items.append((title, htmlUrl, xmlUrl))

    cats = {}
    for title, html, xml in items:
        c = pick_category(title, html, xml)
        cats.setdefault(c, []).append((title, html, xml))

    order = ["AI & Data", "Security", "Software & Systems", "Writing & Essays", "Misc"]

    print("# HN 2025 Popular Blogs — Categorized OPML (quick browsing)\n")
    print("Source: https://gist.github.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b\n")
    print("This is an auto-categorized view (heuristics). For importing, use the OPML in `sources/`.\n")

    for cat in order:
        lst = cats.get(cat, [])
        if not lst:
            continue
        print(f"## {cat} ({len(lst)})\n")
        for title, html, xml in lst:
            name = title or html or xml
            html_part = f" — {html}" if html else ""
            print(f"- **{name}**{html_part}\n  - feed: {xml}")
        print()

    # sanity: count
    total = sum(len(v) for v in cats.values())
    print(f"---\nTotal feeds: {total}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
