#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Select a smaller curated OPML from a larger OPML.

Goal: produce a "starter pack" (~30 feeds) to avoid overload.
Heuristics:
- Keep a fixed quota per category based on domain/title keywords.
- Preserve original order within category.

Usage:
  python3 scripts/select_feeds.py \
    --in sources/hn-2025-popular-blogs.opml \
    --out curated/hn-2025-selected-30.opml \
    --md curated/hn-2025-selected-30.md
"""

import argparse
import re
import xml.etree.ElementTree as ET


def norm(s: str) -> str:
    return (s or "").strip()


def pick_category(title: str, html: str, xml: str) -> str:
    t = f"{title} {html} {xml}".lower()

    if any(k in t for k in ["krebson", "troyhunt", "security", "cve", "vuln"]):
        return "Security"

    if any(k in t for k in ["simonwillison", "ai", "llm", "ml", "machine learning", "data", "statistics", "dynomight", "minimaxir", "rag", "prompt"]):
        return "AI & Data"

    if any(k in t for k in ["crypto", "blockchain", "web3", "ethereum", "bitcoin", "solana", "defi"]):
        return "Crypto & Web3"

    if any(k in t for k in [
        "oldnewthing",
        "program",
        "dev",
        "engineering",
        "mitchellh",
        "matklad",
        "righto",
        "fabiensanglard",
        "beej",
        "jeffgeerling",
        "pocoo",
    ]):
        return "Software & Systems"

    if any(k in t for k in [
        "paulgraham",
        "daringfireball",
        "pluralistic",
        "substack",
        "newsletter",
        "essay",
        "bearblog",
        "theatlantic",
        "joanwestenberg",
        "derekthompson",
    ]):
        return "Writing & Essays"

    return "Misc"


def parse_opml(path: str):
    raw = open(path, "r", encoding="utf-8", errors="replace").read()
    m = re.search(r"<opml\b", raw)
    if not m:
        raise SystemExit(f"No <opml> tag found in {path}")
    root = ET.fromstring(raw[m.start():])

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

    return items


def build_opml(title: str, items):
    opml = ET.Element("opml", {"version": "2.0"})
    head = ET.SubElement(opml, "head")
    t = ET.SubElement(head, "title")
    t.text = title
    body = ET.SubElement(opml, "body")
    root_outline = ET.SubElement(body, "outline", {"text": "Blogs", "title": "Blogs"})

    for feed_title, html, xml in items:
        attrs = {
            "type": "rss",
            "text": feed_title or (html or xml),
            "title": feed_title or (html or xml),
            "xmlUrl": xml,
        }
        if html:
            attrs["htmlUrl"] = html
        ET.SubElement(root_outline, "outline", attrs)

    return opml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", required=True)
    ap.add_argument("--out", dest="out_path", required=True)
    ap.add_argument("--md", dest="md_path", required=True)
    ap.add_argument("--count", type=int, default=30)
    args = ap.parse_args()

    items = parse_opml(args.in_path)

    # Orange preference: AI/tech/frontier + some crypto/web3.
    quotas = {
        "AI & Data": 12,
        "Crypto & Web3": 2,
        "Software & Systems": 10,
        "Security": 3,
        "Writing & Essays": 3,
        "Misc": 0,
    }

    picked = []
    counts = {k: 0 for k in quotas}

    # Preserve original order, but enforce quota by category
    for title, html, xml in items:
        cat = pick_category(title, html, xml)
        if cat not in quotas:
            cat = "Misc"
        if counts[cat] >= quotas[cat]:
            continue
        picked.append((title, html, xml, cat))
        counts[cat] += 1
        if len(picked) >= args.count:
            break

    # If still short, fill from remaining in original order
    if len(picked) < args.count:
        seen = set(x[2] for x in picked)
        for title, html, xml in items:
            if xml in seen:
                continue
            cat = pick_category(title, html, xml)
            picked.append((title, html, xml, cat))
            seen.add(xml)
            if len(picked) >= args.count:
                break

    opml = build_opml(f"HN 2025 Popular Blogs — Selected {len(picked)} feeds", [(a, b, c) for a, b, c, _ in picked])

    ET.ElementTree(opml).write(args.out_path, encoding="utf-8", xml_declaration=True)

    with open(args.md_path, "w", encoding="utf-8") as f:
        f.write(f"# HN 2025 Popular Blogs — Selected {len(picked)} feeds (starter pack)\n\n")
        f.write("This is a curated subset to reduce overload. Import the OPML for RSS readers.\n\n")
        for cat in ["AI & Data", "Crypto & Web3", "Software & Systems", "Security", "Writing & Essays", "Misc"]:
            subset = [x for x in picked if x[3] == cat]
            if not subset:
                continue
            f.write(f"## {cat} ({len(subset)})\n\n")
            for title, html, xml, _ in subset:
                name = title or html or xml
                html_part = f" — {html}" if html else ""
                f.write(f"- **{name}**{html_part}\n  - feed: {xml}\n")
            f.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
