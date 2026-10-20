#!/usr/bin/env python3
"""Merge every research/<region>/candidates.jsonl into data/events.jsonl.

- Skips records that fail schema validation (and reports them).
- Dedupes on id, then flags likely duplicates with different ids (same
  normalised name and country) for a human or verifier to resolve.
- When the same id comes from several regions, keeps the record with the
  most filled fields and unions sponsors, tags, formats, sources and gaps.
- Routes status "discontinued" to data/archived.jsonl.
- Prints a candidate count per region (the Phase 1 checkpoint table).

Usage: python3 research/tools/merge.py
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "data" / "schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)


def filled(value) -> int:
    if value is None:
        return 0
    if isinstance(value, dict):
        return sum(filled(v) for v in value.values())
    if isinstance(value, list):
        return sum(filled(v) for v in value) if value else 0
    return 1


def union(items, key=None):
    seen, out = set(), []
    for item in items:
        k = json.dumps(item if key is None else key(item), sort_keys=True)
        if k not in seen:
            seen.add(k)
            out.append(item)
    return out


def combine(records):
    records = sorted(records, key=filled, reverse=True)
    base = json.loads(json.dumps(records[0]))
    if len(records) == 1:
        return base
    regions = sorted({r["region"] for r in records})
    scopes = {r["scope"] for r in records}
    base["region"] = "+".join(regions)
    if ("A" in scopes and "B" in scopes) or "A+B" in scopes:
        base["scope"] = "A+B"
    base["subculture_tags"] = union(t for r in records for t in r["subculture_tags"])
    base["activation_formats"] = union(f for r in records for f in r["activation_formats"])
    base["sources"] = union((s for r in records for s in r["sources"]), key=lambda s: (s["field"], s["url"]))
    base["gaps"] = union(g for r in records for g in r["gaps"])
    sponsors = {}
    for r in records:
        for s in r["sponsors"]:
            k = s["brand"].casefold()
            if k in sponsors:
                sponsors[k]["years"] = sorted(set(sponsors[k]["years"]) | set(s["years"]))
                sponsors[k]["source"] = sponsors[k]["source"] or s["source"]
            else:
                sponsors[k] = dict(s)
    base["sponsors"] = list(sponsors.values())
    return base


def norm_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.casefold())


def main():
    by_id = defaultdict(list)
    per_region = Counter()
    invalid = []
    for path in sorted((ROOT / "research").glob("*/candidates.jsonl")):
        region = path.parent.name
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                invalid.append(f"{path.relative_to(ROOT)}:{n}: bad JSON ({e})")
                continue
            errs = list(VALIDATOR.iter_errors(rec))
            if errs:
                invalid.append(f"{path.relative_to(ROOT)}:{n} [{rec.get('id')}]: {errs[0].message}")
                continue
            per_region[region] += 1
            by_id[rec["id"]].append(rec)

    merged = [combine(recs) for recs in by_id.values()]
    merged.sort(key=lambda r: (r["region"], r["id"]))
    active = [r for r in merged if r["status"] != "discontinued"]
    archived = [r for r in merged if r["status"] == "discontinued"]

    with open(ROOT / "data" / "events.jsonl", "w") as f:
        for r in active:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(ROOT / "data" / "archived.jsonl", "w") as f:
        for r in archived:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    name_groups = defaultdict(list)
    for r in merged:
        name_groups[(norm_name(r["name"]), r["location"]["country"])].append(r["id"])
    likely_dupes = {k: v for k, v in name_groups.items() if len(v) > 1}

    print("Raw candidates per region:")
    for region, count in sorted(per_region.items()):
        print(f"  {region:28s} {count}")
    print(f"  {'TOTAL raw':28s} {sum(per_region.values())}")
    print(f"Unique ids: {len(merged)}  (cross-region id merges: {sum(1 for v in by_id.values() if len(v) > 1)})")
    print(f"Active/hiatus/unknown -> data/events.jsonl: {len(active)}")
    print(f"Discontinued -> data/archived.jsonl: {len(archived)}")
    if likely_dupes:
        print("Likely duplicates with different ids (resolve by hand):")
        for (_, country), ids in likely_dupes.items():
            print(f"  {country}: {', '.join(ids)}")
    if invalid:
        print(f"Skipped {len(invalid)} invalid record(s):")
        for line in invalid:
            print(f"  {line}")


if __name__ == "__main__":
    main()
