#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build Orange's preferred OPML (AI/tech/frontier + crypto + quantum).

Inputs:
- Base: curated/hn-2025-selected-30.opml (AI/tech heavy)
- Extras: hardcoded crypto/quantum feeds that are accessible from the server.

Output:
- curated/orange-ai-crypto-quantum-30.opml
- curated/orange-ai-crypto-quantum-30.md

Usage:
  python3 scripts/build_orange_opml.py
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_OPML = ROOT / "curated" / "hn-2025-selected-30.opml"
OUT_OPML = ROOT / "curated" / "orange-ai-crypto-quantum-30.opml"
OUT_MD = ROOT / "curated" / "orange-ai-crypto-quantum-30.md"


def parse_opml(path: Path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<opml\b", raw)
    if not m:
        raise SystemExit(f"No <opml> tag found in {path}")
    root = ET.fromstring(raw[m.start():])
    items = []
    for o in root.findall(".//outline"):
        if o.attrib.get("type") != "rss":
            continue
        title = (o.attrib.get("title") or o.attrib.get("text") or "").strip()
        xmlUrl = (o.attrib.get("xmlUrl") or "").strip()
        htmlUrl = (o.attrib.get("htmlUrl") or "").strip()
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
    root_outline = ET.SubElement(body, "outline", {"text": "Feeds", "title": "Feeds"})

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
    base = parse_opml(BASE_OPML)

    # Keep 18 from base (AI/tech) to leave room for crypto/quantum.
    base_keep = base[:18]

    extras = [
        # ---- Crypto / Bitcoin / Ethereum / Cardano / Dogecoin ----
        ("CoinDesk (Crypto News)", "https://www.coindesk.com", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("Bitcoin Optech", "https://bitcoinops.org", "https://bitcoinops.org/feed.xml"),
        ("Ethereum Foundation Blog", "https://blog.ethereum.org", "https://blog.ethereum.org/feed.xml"),
        ("Ethereum Research (ethresear.ch)", "https://ethresear.ch", "https://ethresear.ch/latest.rss"),
        ("r/ethereum (Reddit)", "https://www.reddit.com/r/ethereum/", "https://www.reddit.com/r/ethereum/.rss"),
        ("r/bitcoin (Reddit)", "https://www.reddit.com/r/bitcoin/", "https://www.reddit.com/r/bitcoin/.rss"),
        ("r/cardano (Reddit)", "https://www.reddit.com/r/cardano/", "https://www.reddit.com/r/cardano/.rss"),
        ("r/dogecoin (Reddit)", "https://www.reddit.com/r/dogecoin/", "https://www.reddit.com/r/dogecoin/.rss"),
        ("r/CryptoCurrency (Reddit)", "https://www.reddit.com/r/CryptoCurrency/", "https://www.reddit.com/r/CryptoCurrency/.rss"),

        # ---- Quantum computing / post-quantum crypto adjacent ----
        ("Quanta Magazine", "https://www.quantamagazine.org", "https://www.quantamagazine.org/feed/"),
        ("The Quantum Insider", "https://thequantuminsider.com", "https://thequantuminsider.com/feed/"),
        ("arXiv quant-ph RSS", "https://arxiv.org/list/quant-ph/recent", "https://export.arxiv.org/rss/quant-ph"),
        ("arXiv cs.CR RSS (crypto incl. PQC papers)", "https://arxiv.org/list/cs.CR/recent", "https://export.arxiv.org/rss/cs.CR"),

        # ---- Security/crypto engineering (often covers PQC) ----
        ("Cloudflare Blog", "https://blog.cloudflare.com", "https://blog.cloudflare.com/rss/"),
        ("Trail of Bits Blog", "https://blog.trailofbits.com", "https://blog.trailofbits.com/index.xml"),
    ]

    # De-dup by xmlUrl
    seen = set()
    items = []
    for t, h, x in base_keep + extras:
        if x in seen:
            continue
        seen.add(x)
        items.append((t, h, x))

    # Hard cap to 30
    items = items[:30]

    opml = build_opml("Orange — AI + Crypto + Quantum (30 feeds)", items)
    ET.ElementTree(opml).write(str(OUT_OPML), encoding="utf-8", xml_declaration=True)

    OUT_MD.write_text(
        "# Orange — AI + Crypto + Quantum (30 feeds)\n\n"
        "导入 OPML：`curated/orange-ai-crypto-quantum-30.opml`\n\n"
        "说明：包含一部分 AI/工程博客 + Bitcoin/Ethereum/Cardano/Dogecoin 信息源 + 量子计算/密码学（含可能的抗量子/PQC 论文源）。\n\n"
        + "\n".join([f"- **{t}** — {h}\n  - feed: {x}" for t, h, x in items])
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
