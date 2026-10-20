#!/usr/bin/env python3
"""Compile Instagram handle candidates per target event from:
  - research/apify/derived/site_ig_links.jsonl (links on event and organiser sites)
  - research/apify/raw/google/*handles*.jsonl (Google "<name> <city> instagram")
  - research/apify/raw/ig-search/*.jsonl (Instagram user search), when present

Writes research/apify/derived/handle_candidates.jsonl: one line per event with
every candidate handle, the evidence for it, and a name-similarity score.

Usage: python3 research/tools/phase2_handle_candidates.py
"""
import glob
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from phase2_common import name_sim

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "research" / "apify"
PROFILE_URL = re.compile(r"^https?://(?:www\.)?instagram\.com/([A-Za-z0-9._]{2,30})/?(?:reels/?|\?.*)?$", re.I)
TITLE_HANDLE = re.compile(r"\(@([A-Za-z0-9._]{2,30})\)")
RESERVED = {"p", "reel", "reels", "tv", "explore", "stories", "accounts", "about", "_t", "_u", "popular", "web"}
targets = [json.loads(l) for l in (A / "targets.jsonl").read_text().split("\n") if l.strip()]
by_id = {t["id"]: t for t in targets}
cands = {t["id"]: {} for t in targets}


def add(tid, handle, evidence, label=""):
    h = handle.lower().strip(".")
    if h in RESERVED or len(h) < 3:
        return
    c = cands[tid].setdefault(h, {"handle": h, "evidence": [], "labels": []})
    c["evidence"].append(evidence)
    if label and label not in c["labels"]:
        c["labels"].append(label)


for t in targets:
    if t["handle"]:
        add(t["id"], t["handle"].lstrip("@"), {"type": "phase1-record"})

site = A / "derived" / "site_ig_links.jsonl"
if site.exists():
    for r in (json.loads(l) for l in site.read_text().split("\n") if l.strip()):
        for rank, h in enumerate(r["handles"][:6]):
            add(r["id"], h, {"type": f"site-{r['kind']}", "url": r["final_url"] or r["url"], "rank": rank,
                             "n_links": len(r["handles"])})

qmap = {}
for m in ("02-google-handles.map.json", "07-google-ig-site.map.json"):
    if (A / "inputs" / m).exists():
        qmap.update(json.loads((A / "inputs" / m).read_text()))
for f in sorted(glob.glob(str(A / "raw" / "google" / "*handles*.jsonl")) + glob.glob(str(A / "raw" / "google" / "*ig-site*.jsonl"))):
    for item in (json.loads(l) for l in Path(f).read_text().split("\n") if l.strip()):
        tid = qmap.get(item["searchQuery"]["term"])
        if not tid:
            continue
        for o in item.get("organicResults", []):
            m = PROFILE_URL.match(o["url"].split("?")[0] if "?hl=" in o["url"] else o["url"])
            th = TITLE_HANDLE.search(o.get("title", ""))
            if m and m.group(1).lower() not in RESERVED:
                label = o["title"].split("(@")[0].strip()
                add(tid, m.group(1), {"type": "google-profile", "url": o["url"], "rank": o["position"]}, label)
            elif th:
                add(tid, th.group(1), {"type": "google-title", "url": o["url"], "rank": o["position"]})
            for h in re.findall(r"@([A-Za-z0-9._]{3,30})", (o.get("title") or "") + " " + (o.get("description") or "")):
                h = h.rstrip(".")
                if name_sim(by_id[tid]["name"], h) >= 0.6:
                    add(tid, h, {"type": "google-mention", "url": o["url"], "rank": o["position"]})
            if not by_id[tid]["website"] and "instagram.com" not in o["url"] and o["position"] <= 3:
                by_id[tid].setdefault("website_hits", []).append(o["url"])

term_map = {}
for m in glob.glob(str(A / "inputs" / "*ig-search*.map.json")):
    term_map.update(json.loads(Path(m).read_text()))
for f in sorted(glob.glob(str(A / "raw" / "ig-search" / "*.jsonl"))):
    for item in (json.loads(l) for l in Path(f).read_text().split("\n") if l.strip()):
        tid = term_map.get((item.get("searchTerm") or "").strip())
        if tid in cands and item.get("username"):
            add(tid, item["username"], {"type": "ig-search", "url": item.get("url"), "file": Path(f).name},
                item.get("fullName") or "")

out = A / "derived" / "handle_candidates.jsonl"
with out.open("w") as f:
    for t in targets:
        rows = []
        for c in cands[t["id"]].values():
            types = {e["type"] for e in c["evidence"]}
            c["sim"] = max([name_sim(t["name"], c["handle"])] + [name_sim(t["name"], c["handle"], l) for l in c["labels"]])
            c["sources"] = sorted(types)
            rows.append(c)
        rows.sort(key=lambda c: (-(len(c["sources"])), -c["sim"]))
        f.write(json.dumps({"id": t["id"], "name": t["name"], "city": t["city"], "website": t["website"],
                            "website_hits": t.get("website_hits", []), "candidates": rows}, ensure_ascii=False) + "\n")
print("written", out.relative_to(ROOT))
