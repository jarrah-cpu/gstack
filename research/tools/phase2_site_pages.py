#!/usr/bin/env python3
"""Pick the pages worth crawling on each target's website: the homepage plus
internal links whose URL or link text points at partners, sponsors, about,
media kits, press, contact, FAQ, trade or vendor information. Works from the
homepage HTML fetched locally (free); page content is only parsed for links.

Usage: python3 research/tools/phase2_site_pages.py <websites.json>
  websites.json  {"event-id": "https://site/", ...}
Writes research/apify/derived/crawl_urls.jsonl (id, site, urls[])
"""
import json
import re
import ssl
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "apify" / "derived" / "crawl_urls.jsonl"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
LINK = re.compile(r"<a\b[^>]*?href\s*=\s*[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", re.I | re.S)
KEYWORDS = {
    # 3: partner and sponsor pages (English, Spanish, Portuguese, Catalan, Indonesian, Japanese romanised)
    "partner": 3, "sponsor": 3, "patrocin": 3, "parceir": 3, "colabora": 3, "mitra": 3, "kyosan": 3,
    "media-kit": 3, "mediakit": 3, "advertis": 3, "work-with": 3, "opportunit": 3, "supporter": 3,
    # 2: about, press, contact, FAQ
    "about": 2, "press": 2, "media": 2, "contact": 2, "faq": 2, "info": 2, "who-we-are": 2, "our-story": 2,
    "history": 2, "prensa": 2, "imprensa": 2, "contacto": 2, "contato": 2, "sobre": 2, "quienes": 2,
    "nosotros": 2, "tentang": 2, "kontak": 2, "gaiyo": 2, "outline": 2, "historia": 2,
    # 1: weaker signals
    "team": 1, "trade": 1, "stall": 1, "vendor": 1, "exhibit": 1, "attend": 1, "audience": 1, "brand": 1,
    "kit": 1, "collab": 1, "get-involved": 1, "expositor": 1, "marcas": 1, "company": 1, "socio": 1,
}
ITEM = re.compile(r"/\d+/?$|/(news|newsletter|blog|events?|shows?|artists?|stallholders?|product|products|shop)/[^/]+", re.I)
SKIP = re.compile(r"\.(jpg|jpeg|png|gif|webp|svg|mp4|zip|ics)$|^mailto:|^tel:|^javascript:|/wp-content/|/cart|/checkout|/account|/login|/tag/|/category/|/feed", re.I)
MAX_PAGES = 10


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
            return r.geturl(), r.read(3_000_000).decode("utf-8", "replace")
    except Exception:
        return None, ""


def pick(job):
    tid, site = job
    final, html = fetch(site)
    base = final or site
    host = urlparse(base).netloc.lower().removeprefix("www.")
    scored = {}
    for href, text in LINK.findall(html):
        url = urljoin(base, unescape(href.strip())).split("#")[0]
        p = urlparse(url)
        if p.scheme not in ("http", "https") or p.netloc.lower().removeprefix("www.") != host or SKIP.search(url):
            continue
        hay = (p.path + " " + re.sub(r"<[^>]+>", " ", text)).lower()
        hits = sum(w for k, w in KEYWORDS.items() if k in hay)
        if ITEM.search(p.path) and not any(k in p.path.lower() for k, w in KEYWORDS.items() if w == 3):
            continue
        if hits and url.rstrip("/") != base.rstrip("/"):
            scored[url] = max(scored.get(url, 0), hits)
    picked = sorted(scored, key=lambda u: (-scored[u], len(u)))[: MAX_PAGES - 1]
    return {"id": tid, "site": site, "final_url": final, "fetched": bool(html), "urls": [base] + picked}


sites = json.loads(Path(sys.argv[1]).read_text())
with ThreadPoolExecutor(max_workers=16) as pool:
    rows = list(pool.map(pick, sites.items()))
with OUT.open("w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(f"{len(rows)} sites, {sum(len(r['urls']) for r in rows)} pages picked, {sum(1 for r in rows if not r['fetched'])} homepages not fetched")
