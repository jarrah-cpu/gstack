#!/usr/bin/env python3
"""Phase 4 scoring: shared weighting and score-file checks.

weighted_total = 0.35 vibe_fit + 0.35 audience_fit + 0.10 scale + 0.10 accessibility + 0.10 cost,
with scale, accessibility and cost mapped to 1 to 5 below. Mid-size events score best on scale:
big enough to matter, small enough for a brand to be part of the culture rather than a billboard.
"""
import re

WEIGHTS = {"vibe_fit": 0.35, "audience_fit": 0.35, "scale": 0.10, "accessibility": 0.10, "cost": 0.10}
SCALE = {"<1k": 2, "1k-5k": 4, "5k-20k": 5, "20k-50k": 4, "50k-100k": 3, "100k+": 2, "unknown": 3}
ACCESS = {"open": 5, "selective": 3, "locked": 1, "unknown": 3}
COST = {"low": 5, "medium": 3, "high": 1, "unknown": 3}
DASH = re.compile("[—–]")


def weighted_total(s):
    return round(WEIGHTS["vibe_fit"] * s["vibe_fit"] + WEIGHTS["audience_fit"] * s["audience_fit"]
                 + WEIGHTS["scale"] * SCALE[s["scale_band"]] + WEIGHTS["accessibility"] * ACCESS[s["accessibility"]]
                 + WEIGHTS["cost"] * COST[s["cost_signal"]], 2)


def check(s):
    errs = []
    need = {"id", "vibe_fit", "vibe_rationale", "audience_fit", "scale_band", "accessibility", "cost_signal", "fit_notes"}
    if set(s) != need:
        errs.append(f"keys must be exactly {sorted(need)}; got {sorted(s)}")
    for k in ("vibe_fit", "audience_fit"):
        if not isinstance(s.get(k), int) or not 1 <= s[k] <= 5:
            errs.append(f"{k} must be an integer 1 to 5")
    if s.get("scale_band") not in SCALE:
        errs.append(f"scale_band must be one of {list(SCALE)}")
    if s.get("accessibility") not in ACCESS:
        errs.append(f"accessibility must be one of {list(ACCESS)}")
    if s.get("cost_signal") not in COST:
        errs.append(f"cost_signal must be one of {list(COST)}")
    for k in ("vibe_rationale", "fit_notes"):
        if not isinstance(s.get(k), str) or len(s[k]) < 20:
            errs.append(f"{k} must be a sentence")
        elif DASH.search(s[k]):
            errs.append(f"{k} contains an em or en dash")
    return errs
