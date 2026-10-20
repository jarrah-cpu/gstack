#!/usr/bin/env python3
"""Check Phase 4 score files (research/score/<id>.json).

Usage: python3 research/tools/phase4_check_score.py research/score/<id>.json [...]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from phase4_scoring import check  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ids = {json.loads(l)["id"] for l in (ROOT / "data" / "events.jsonl").read_text().split("\n") if l.strip()}
bad = 0
for f in sys.argv[1:]:
    try:
        s = json.loads(Path(f).read_text())
    except json.JSONDecodeError as e:
        print(f"{f}: invalid JSON: {e}")
        bad += 1
        continue
    errs = check(s) + ([] if s.get("id") in ids else [f"unknown id {s.get('id')}"])
    print(f"{f}: " + ("OK" if not errs else "\n  " + "\n  ".join(errs)))
    bad += bool(errs)
sys.exit(1 if bad else 0)
