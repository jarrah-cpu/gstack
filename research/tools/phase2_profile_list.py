#!/usr/bin/env python3
"""Choose which candidate Instagram accounts to profile-scrape: up to three of
the strongest candidates per event, plus organiser accounts linked from
organiser websites. Accounts already returned with full profile data by the
Instagram search scraper are skipped.

Usage: python3 research/tools/phase2_profile_list.py <out.json>
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "research" / "apify"


def strength(c):
    s = c["sim"] * 3
    for e in c["evidence"]:
        t = e["type"]
        if t == "phase1-record":
            s += 3
        elif t == "site-event":
            s += 3 if e.get("n_links", 9) <= 2 else (1.5 if e.get("rank", 9) == 0 else 0.5)
        elif t == "google-profile":
            s += 2 + (1 if e.get("rank", 9) <= 3 else 0)
        elif t in ("google-mention", "google-title"):
            s += 0.5
    return s


have = set()
for f in glob.glob(str(A / "raw" / "ig-search" / "*.jsonl")) + glob.glob(str(A / "raw" / "ig-profile" / "*.jsonl")):
    for item in (json.loads(l) for l in Path(f).read_text().split("\n") if l.strip()):
        if item.get("username") and item.get("followersCount") is not None:
            have.add(item["username"].lower())

pick = {}
for r in (json.loads(l) for l in (A / "derived" / "handle_candidates.jsonl").read_text().split("\n") if l.strip()):
    ev = [c for c in r["candidates"] if any(e["type"] != "site-organiser" for e in c["evidence"])]
    ev = [c for c in ev if c["sim"] >= 0.35 or any(e["type"] in ("phase1-record", "google-profile") or
          (e["type"] == "site-event" and e.get("rank") == 0) for e in c["evidence"])]
    for c in sorted(ev, key=strength, reverse=True)[:3]:
        pick.setdefault(c["handle"], set()).add(r["id"])
    org = [c for c in r["candidates"] if any(e["type"] == "site-organiser" and e.get("n_links", 9) <= 3 for e in c["evidence"])]
    for c in org[:2]:
        pick.setdefault(c["handle"], set()).add(r["id"])

todo = sorted(h for h in pick if h not in have and "." not in h[-3:] or h.endswith("."))
todo = sorted(h for h in pick if h not in have and not h.endswith(".js"))
json.dump({"usernames": todo}, open(sys.argv[1], "w"))
print(f"{len(pick)} handles picked, {len(pick) - len(todo)} already have profile data, {len(todo)} to scrape")
