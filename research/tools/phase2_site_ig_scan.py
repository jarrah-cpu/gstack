#!/usr/bin/env python3
"""Fetch each target's event and organiser homepage and list the Instagram
accounts it links to. Free first pass of handle discovery (no Apify credits).

Page content is treated as data: only instagram.com links are extracted,
nothing is saved or executed.

Usage: python3 research/tools/phase2_site_ig_scan.py
Writes research/apify/derived/site_ig_links.jsonl
"""
import json
import re
import ssl
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = ROOT / "research" / "apify" / "targets.jsonl"
OUT = ROOT / "research" / "apify" / "derived" / "site_ig_links.jsonl"
IG = re.compile(r"(?:instagram\.com|instagr\.am)/([A-Za-z0-9._]{1,30})(?=[/?#\"'\s<>&\\]|$)", re.I)
RESERVED = {"p", "reel", "reels", "tv", "explore", "stories", "accounts", "about", "developer",
            "legal", "direct", "web", "sharer", "share", "intent", "oauth", "static", "embed",
            "instagram", "privacy", "terms", "help", "s", "invites", "_u", "ar"}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
CTX = ssl.create_default_context()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    try:
        with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
            body = r.read(3_000_000).decode("utf-8", "replace")
            return r.status, r.geturl(), body
    except Exception as e:  # network errors are recorded, not fatal
        return f"error: {type(e).__name__}: {str(e)[:120]}", None, ""


def scan(job):
    tid, kind, url = job
    status, final, body = fetch(url)
    handles = Counter(h.lower().rstrip(".") for h in IG.findall(body))
    handles = [h for h, _ in handles.most_common() if h not in RESERVED]
    return {"id": tid, "kind": kind, "url": url, "status": status, "final_url": final, "handles": handles}


jobs = []
for line in TARGETS.read_text().splitlines():
    t = json.loads(line)
    if t["website"]:
        jobs.append((t["id"], "event", t["website"]))
    if t["organiser_website"] and t["organiser_website"] != t["website"]:
        jobs.append((t["id"], "organiser", t["organiser_website"]))

with ThreadPoolExecutor(max_workers=16) as pool, OUT.open("w") as f:
    results = list(pool.map(scan, jobs))
    for r in results:
        f.write(json.dumps(r) + "\n")

ok = [r for r in results if r["status"] == 200]
print(f"{len(jobs)} pages, {len(ok)} fetched, {sum(1 for r in ok if r['handles'])} with Instagram links")
print("event pages with a link:", sum(1 for r in ok if r["kind"] == "event" and r["handles"]))
