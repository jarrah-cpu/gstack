#!/usr/bin/env python3
"""Print the Phase 1 checkpoint table from data/events.jsonl and data/archived.jsonl.

Run research/tools/merge.py first. Usage: python3 research/tools/checkpoint.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TODAY, HORIZON = "2026-10-20", "2028-04-20"  # 18-month window from the brief


def load(name):
    path = ROOT / "data" / name
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def in_window(rec):
    nxt = rec["dates"]["next_edition"]
    start = nxt["start"]
    return bool(start) and nxt["status"] in ("confirmed", "expected") and TODAY[: len(start)] <= start <= HORIZON


active, archived = load("events.jsonl"), load("archived.jsonl")
rows = defaultdict(Counter)
for r in active:
    for region in r["region"].split("+"):
        c = rows[region]
        c["unique"] += 1
        c["confirmed"] += r["dates"]["next_edition"]["status"] == "confirmed"
        c["in_window"] += in_window(r)
        c["vibe4plus"] += (r["vibe"]["score"] or 0) >= 4
        c["hiatus_or_unknown"] += r["status"] in ("on-hiatus", "unknown")
for r in archived:
    for region in r["region"].split("+"):
        rows[region]["archived"] += 1

cols = ["unique", "confirmed", "in_window", "vibe4plus", "hiatus_or_unknown", "archived"]
print("| Region | Events | Next edition confirmed | Next edition in 18-month window | Vibe 4+ | Hiatus or unknown | Archived |")
print("|---|---|---|---|---|---|---|")
total = Counter()
for region in sorted(rows):
    c = rows[region]
    print(f"| {region} | " + " | ".join(str(c[k]) for k in cols) + " |")
for r in active:
    total["unique"] += 1
    total["confirmed"] += r["dates"]["next_edition"]["status"] == "confirmed"
    total["in_window"] += in_window(r)
    total["vibe4plus"] += (r["vibe"]["score"] or 0) >= 4
    total["hiatus_or_unknown"] += r["status"] in ("on-hiatus", "unknown")
total["archived"] = len(archived)
print("| **Total (deduped)** | " + " | ".join(f"**{total[k]}**" for k in cols) + " |")
print("\nNote: an event found by two regions counts once in each region row but once in the total.")

print("\nCategories:", ", ".join(f"{k} {v}" for k, v in Counter(r["category"] for r in active).most_common()))
tags = Counter(t for r in active for t in r["subculture_tags"])
print("Top subculture tags:", ", ".join(f"{k} {v}" for k, v in tags.most_common(25)))
fill = lambda f: sum(1 for r in active if f(r))
print(
    "Field fill (active):",
    f"website {fill(lambda r: r['website'])},",
    f"IG handle {fill(lambda r: r['instagram']['handle'])},",
    f"attendance {fill(lambda r: r['attendance']['figure'] is not None)},",
    f"sponsors {fill(lambda r: r['sponsors'])},",
    f"contact {fill(lambda r: any(r['partnership_contact'][k] for k in ('email', 'page_url', 'named_person')))},",
    f"ticket price {fill(lambda r: r['ticket_price']['min'] is not None or r['ticket_price']['free_entry'] is not None)},",
    f"demographics {fill(lambda r: r['audience']['age_range'] or r['audience']['gender_skew'])}",
)
