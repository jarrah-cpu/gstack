#!/usr/bin/env python3
"""Propose an official website for target events that have none on record:
first the resolved Instagram profile's link when it is a real domain (not a
link aggregator, ticketing or social site), else a top-3 Google result whose
domain contains part of the event name.

Writes research/apify/derived/new_websites.json {"event-id": {"url", "source"}}.

Usage: python3 research/tools/phase2_new_websites.py
"""
import glob
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from phase2_common import words

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "research" / "apify"
AGG = re.compile(r"linktr\.ee|linkin\.bio|lnk\.bio|bio\.link|msha\.ke|beacons\.ai|taplink|hoo\.be|bit\.ly|tinyurl|"
                 r"instagram\.com|facebook\.com|youtube|youtu\.be|tiktok|twitter|x\.com|oztix|ticketek|moshtix|"
                 r"eventbrite|dice\.fm|tixr|universe\.com|humanitix|ticketplus|laruralticket|entryplus|forms\.gle|"
                 r"google\.com|spotify|linkpop|komi\.io|likeshop|shor\.by|sprout\.link|wa\.me|allevents|"
                 r"worldtattooevents|abnb\.me|triniq|tpvclub|athlete360|smarturl|lnk\.to|apple\.com|ra\.co", re.I)
prof = {}
for f in glob.glob(str(A / "raw" / "ig-profile" / "*.jsonl")) + glob.glob(str(A / "raw" / "ig-search" / "*.jsonl")):
    for l in Path(f).read_text().split("\n"):
        if l.strip():
            p = json.loads(l)
            if p.get("username"):
                prof[p["username"].lower()] = p
out = {}
cands = {r["id"]: r for r in (json.loads(l) for l in (A / "derived" / "handle_candidates.jsonl").read_text().split("\n") if l.strip())}
for r in (json.loads(l) for l in (A / "derived" / "handles_resolved.jsonl").read_text().split("\n") if l.strip()):
    if r["website"]:
        continue
    for h in (r["handle"], r["organiser_handle"]):
        p = prof.get(h or "")
        url = p and p.get("externalUrl")
        if url and not AGG.search(url):
            out[r["id"]] = {"url": url, "source": f"Instagram profile link of @{h}"}
            break
    if r["id"] in out:
        continue
    toks = [w for w in words(r["name"]) if len(w) >= 4]
    for u in cands[r["id"]].get("website_hits", []):
        d = urlparse(u).netloc.lower()
        if not AGG.search(u) and any(t in d.replace("-", "") for t in toks):
            out[r["id"]] = {"url": u, "source": "Google result for event name"}
            break
(A / "derived" / "new_websites.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), "websites proposed")
