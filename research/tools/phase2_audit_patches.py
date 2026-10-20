#!/usr/bin/env python3
"""Audit enrichment patches for cross-event mix-ups.

For each research/apify/enrich/<id>.json: the id must match the file name, and
each cited URL is classed as own (in this event's evidence pack, or on one of
its own domains), foreign (in another event's pack only), or new (fetched by
the agent, in no pack). Patches citing foreign URLs are listed for review.

Usage: python3 research/tools/phase2_audit_patches.py
"""
import glob
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "research" / "apify"
URL = re.compile(r"https?://[^\s)\]|'\"<>]+")


def dom(u):
    return urlparse(u).netloc.lower().removeprefix("www.")


def norm(u):
    return u.rstrip("/.,;").split("#")[0].replace("http://", "https://").replace("://www.", "://")


packs = {Path(f).stem: Path(f).read_text() for f in glob.glob(str(A / "evidence" / "*" / "*.md"))}
url_events = defaultdict(set)
for eid, txt in packs.items():
    for u in URL.findall(txt):
        url_events[norm(u)].add(eid)
own_doms = defaultdict(set)
for eid, txt in packs.items():
    for u in URL.findall(txt.split("## Sponsor signals")[0]):
        d = dom(u)
        if d and "instagram.com" not in d and "google" not in d:
            own_doms[eid].add(d)

flagged = 0
for f in sorted(glob.glob(str(A / "enrich" / "*.json"))):
    p = json.loads(Path(f).read_text())
    eid = Path(f).stem
    probs = []
    if p.get("id") != eid:
        probs.append(f"id {p.get('id')} != file name")
    urls = set(norm(u) for u in URL.findall(json.dumps(p)))
    foreign = []
    for u in urls:
        evs = url_events.get(u, set())
        if eid in evs or dom(u) in own_doms[eid]:
            continue
        if evs:
            foreign.append((u, sorted(evs)[:2]))
    if foreign:
        probs.append(f"{len(foreign)} of {len(urls)} URLs only in other events' packs: " +
                     "; ".join(f"{u} ({', '.join(e)})" for u, e in foreign[:3]))
    if probs:
        flagged += 1
        print(eid, "|", " | ".join(probs))
print(f"{len(glob.glob(str(A / 'enrich' / '*.json')))} patches, {flagged} flagged")
