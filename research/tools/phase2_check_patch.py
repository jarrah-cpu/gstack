#!/usr/bin/env python3
"""Check enrichment patch files against the event record and schema.

Usage: python3 research/tools/phase2_check_patch.py research/apify/enrich/<id>.json [...]
       (phase3_check_verify.py wraps this in verify mode)
Prints OK or the problems; exit 1 if any file has problems.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from phase2_patch import ROOT, problems  # noqa: E402

events = {}
for l in (ROOT / "data" / "events.jsonl").read_text().split("\n"):
    if l.strip():
        e = json.loads(l)
        events[e["id"]] = e
bad = 0
MODE = os.environ.get("PATCH_MODE", "enrich")
for f in sys.argv[1:]:
    try:
        patch = json.loads(Path(f).read_text())
    except json.JSONDecodeError as e:
        print(f"{f}: invalid JSON: {e}")
        bad += 1
        continue
    rec = events.get(patch.get("id"))
    if not rec:
        print(f"{f}: unknown id {patch.get('id')}")
        bad += 1
        continue
    errs = problems(rec, patch, MODE)
    print(f"{f}: " + ("OK" if not errs else "\n  " + "\n  ".join(errs)))
    bad += bool(errs)
sys.exit(1 if bad else 0)
