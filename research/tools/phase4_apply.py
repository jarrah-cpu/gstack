#!/usr/bin/env python3
"""Write Phase 4 scores (research/score/<id>.json) into the region candidates files:
scores (with weighted_total from phase4_scoring.py), vibe (score = vibe_fit,
rationale, preliminary false) and fit_notes; record_meta.phase = "scored".

Usage: python3 research/tools/phase4_apply.py
"""
import glob
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from phase2_patch import VALIDATOR  # noqa: E402
from phase4_scoring import check, weighted_total  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
aliases = json.loads((ROOT / "research" / "tools" / "aliases.json").read_text())
scores, bad = {}, {}
for f in glob.glob(str(ROOT / "research" / "score" / "*.json")):
    s = json.loads(Path(f).read_text())
    errs = check(s)
    if errs:
        bad[Path(f).stem] = errs
    else:
        scores[s["id"]] = s
n = 0
for f in sorted(glob.glob(str(ROOT / "research" / "*" / "candidates.jsonl"))):
    recs = [json.loads(l) for l in Path(f).read_text().split("\n") if l.strip()]
    changed = False
    for i, r in enumerate(recs):
        s = scores.get(aliases.get(r["id"], r["id"]))
        if not s:
            continue
        new = json.loads(json.dumps(r))
        new["scores"] = {"vibe_fit": s["vibe_fit"], "audience_fit": s["audience_fit"], "scale_band": s["scale_band"],
                         "accessibility": s["accessibility"], "cost_signal": s["cost_signal"],
                         "weighted_total": weighted_total(s)}
        new["vibe"] = {"score": s["vibe_fit"], "rationale": s["vibe_rationale"], "preliminary": False}
        new["fit_notes"] = s["fit_notes"]
        new["record_meta"] = {**new["record_meta"], "phase": "scored", "updated": date.today().isoformat()}
        if list(VALIDATOR.iter_errors(new)):
            bad[r["id"]] = ["fails schema after scoring"]
            continue
        recs[i] = new
        changed = True
        n += 1
    if changed:
        Path(f).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in recs))
print(f"{len(scores)} score files valid, {n} record copies scored, {len(bad)} bad")
for k, v in bad.items():
    print(" ", k, v[:2])
