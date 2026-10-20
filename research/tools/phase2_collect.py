#!/usr/bin/env python3
"""Record every finished run listed in research/apify/pending.tsv
(run_id, step, label, input file) with phase2_ledger.py, and keep the
unfinished ones in the file.

Usage: python3 research/tools/phase2_collect.py
"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PENDING = ROOT / "research" / "apify" / "pending.tsv"
keep, rc = [], 0
for line in PENDING.read_text().split("\n"):
    if not line.strip():
        continue
    run_id, step, label, inp = line.split("\t")
    with urllib.request.urlopen(f"https://api.apify.com/v2/actor-runs/{run_id}", timeout=60) as r:
        status = json.load(r)["data"]["status"]
    if status in ("READY", "RUNNING"):
        keep.append(line)
        print(f"{label}: still {status}")
        continue
    res = subprocess.run([sys.executable, str(ROOT / "research/tools/phase2_ledger.py"), run_id, step, label, inp],
                         capture_output=True, text=True)
    print(res.stdout.strip() or res.stderr.strip())
    rc = max(rc, res.returncode)
PENDING.write_text("\n".join(keep) + ("\n" if keep else ""))
sys.exit(rc)
