#!/usr/bin/env python3
"""Apply Phase 3 verification to the region candidates files.

Every event listed in research/verify/batches/verify-*.txt was checked by a
verifier. Its records get record_meta.phase = "verified"; where the verifier
wrote research/verify/<id>.json, that patch is applied in verify mode
(status and date corrections, sponsor fixes, verifier_flags). Events set to
"discontinued" move to data/archived.jsonl when merge.py runs.

Usage: python3 research/tools/phase3_apply.py [--dry-run]
"""
import glob
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from phase2_patch import VALIDATOR, apply, problems  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
V = ROOT / "research" / "verify"
TODAY = date.today().isoformat()
DRY = "--dry-run" in sys.argv
aliases = json.loads((ROOT / "research" / "tools" / "aliases.json").read_text())
checked = set()
for f in glob.glob(str(V / "batches" / "verify-*.txt")):
    for line in Path(f).read_text().split("\n"):
        if line.strip():
            checked.add(line.split("\t")[1])
patched, bad, marked = 0, {}, 0
for f in sorted(glob.glob(str(ROOT / "research" / "*" / "candidates.jsonl"))):
    recs = [json.loads(l) for l in Path(f).read_text().split("\n") if l.strip()]
    changed = False
    for i, rec in enumerate(recs):
        cid = aliases.get(rec["id"], rec["id"])
        if cid not in checked:
            continue
        new = rec
        pf = V / f"{cid}.json"
        if pf.exists():
            patch = json.loads(pf.read_text())
            patch["id"] = rec["id"]
            errs = problems(rec, patch, "verify")
            if errs:
                bad[cid] = errs
                continue
            new = apply(rec, patch, "verify")
            patched += 1
        new["record_meta"] = {**new["record_meta"], "phase": "verified", "updated": TODAY}
        if list(VALIDATOR.iter_errors(new)):
            bad[cid] = ["final record fails schema"]
            continue
        recs[i] = new
        changed = True
        marked += 1
    if changed and not DRY:
        Path(f).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in recs))
print(f"checked {len(checked)} events; {marked} record copies marked verified; {patched} patched; bad {len(bad)}")
for k, v in bad.items():
    print(" ", k, v[:3])
