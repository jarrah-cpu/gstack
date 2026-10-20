#!/usr/bin/env python3
"""Write research/apify/targets.jsonl: the Phase 2 enrichment set.

Scope approved 20 Oct 2026: events with preliminary vibe 3+ and a confirmed
or expected next edition inside the 18-month window (checkpoint.py rule).

Usage: python3 research/tools/phase2_targets.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TODAY, HORIZON = "2026-10-20", "2028-04-20"


def in_window(rec):
    nxt = rec["dates"]["next_edition"]
    start = nxt["start"]
    return bool(start) and nxt["status"] in ("confirmed", "expected") and TODAY[: len(start)] <= start <= HORIZON


events = [json.loads(l) for l in (ROOT / "data" / "events.jsonl").read_text().split("\n") if l.strip()]
targets = [e for e in events if (e["vibe"]["score"] or 0) >= 3 and in_window(e)]
out = ROOT / "research" / "apify" / "targets.jsonl"
with out.open("w") as f:
    for e in targets:
        f.write(json.dumps({
            "id": e["id"],
            "region": e["region"],
            "name": e["name"],
            "city": e["location"]["city"],
            "country": e["location"]["country"],
            "website": e["website"],
            "handle": e["instagram"]["handle"],
            "organiser": e["organiser"]["name"],
            "organiser_website": e["organiser"]["website"],
            "next_edition": e["dates"]["next_edition"]["start"],
            "vibe": e["vibe"]["score"],
        }, ensure_ascii=False) + "\n")
print(f"{len(targets)} targets written to {out.relative_to(ROOT)}")
