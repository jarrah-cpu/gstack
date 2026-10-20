#!/usr/bin/env python3
"""Pick each target event's Instagram account (and organiser account when
different) from the handle candidates, using profile data from the Apify
Instagram profile and search scrapers.

Writes research/apify/derived/handles_resolved.jsonl with the chosen handle,
a confidence label (high, medium, low, none), the reasons, and the runner-up
candidates. Manual overrides in research/apify/derived/handle_overrides.json
({"event-id": {"handle": "x" or null, "organiser_handle": "y", "note": "..."}})
win over the scoring.

Usage: python3 research/tools/phase2_resolve_handles.py
"""
import glob
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from phase2_common import name_sim  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "research" / "apify"
OVR = A / "derived" / "handle_overrides.json"


def dom(u):
    if not u:
        return None
    h = urlparse(u if "://" in u else "http://" + u).netloc.lower().removeprefix("www.")
    return h or None


profiles = {}
for f in sorted(glob.glob(str(A / "raw" / "ig-search" / "*.jsonl"))) + sorted(glob.glob(str(A / "raw" / "ig-profile" / "*.jsonl"))):
    for p in (json.loads(l) for l in Path(f).read_text().split("\n") if l.strip()):
        if p.get("username") and p.get("followersCount") is not None:
            p["_raw"] = str(Path(f).relative_to(ROOT))
            profiles[p["username"].lower()] = p

targets = {t["id"]: t for t in (json.loads(l) for l in (A / "targets.jsonl").read_text().split("\n") if l.strip())}
overrides = json.loads(OVR.read_text()) if OVR.exists() else {}
out = []
for r in (json.loads(l) for l in (A / "derived" / "handle_candidates.jsonl").read_text().split("\n") if l.strip()):
    t = targets[r["id"]]
    site_doms = {d for d in [dom(t["website"])] + [dom(u) for u in r.get("website_hits", [])] if d}
    city = (t["city"] or "").lower()
    scored = []
    for c in r["candidates"]:
        p = profiles.get(c["handle"])
        if not p:
            continue
        reasons, score = [], 0.0
        links = [p.get("externalUrl")] + [x.get("url") for x in (p.get("externalUrls") or [])]
        link_doms = {dom(u) for u in links if u}
        if t["website"] and dom(t["website"]) in link_doms:
            score += 4; reasons.append("profile link = event website")
        elif site_doms & link_doms:
            score += 2; reasons.append("profile link = site found by Google")
        sim = max(name_sim(t["name"], p["username"]), name_sim(t["name"], p["username"], p.get("fullName") or ""))
        score += sim * 3; reasons.append(f"name similarity {sim:.2f}")
        bio = (p.get("biography") or "").lower()
        core = [w for w in re.findall(r"[a-z0-9]{4,}", t["name"].lower()) if w not in ("festival", "market", "markets", "fest")]
        if core and sum(w in bio for w in core) >= max(1, len(core) // 2):
            score += 1; reasons.append("bio names the event")
        if city and city in bio:
            score += 0.5; reasons.append("bio names the city")
        types = {e["type"] for e in c["evidence"]}
        if "phase1-record" in types:
            score += 1.5; reasons.append("Phase 1 record")
        if any(e["type"] == "site-event" and e.get("n_links", 9) <= 2 for e in c["evidence"]):
            score += 2; reasons.append("only Instagram link on event site")
        elif "site-event" in types:
            score += 0.5; reasons.append("linked from event site")
        if any(e["type"] == "google-profile" and e.get("rank", 9) <= 3 for e in c["evidence"]):
            score += 1; reasons.append("top-3 Google profile result")
        if "ig-search" in types:
            score += 0.5; reasons.append("Instagram search hit")
        only_org = types == {"site-organiser"}
        scored.append({"handle": c["handle"], "score": round(score, 2), "sim": sim, "only_org": only_org,
                       "reasons": reasons, "followers": p.get("followersCount"), "full_name": p.get("fullName"),
                       "external_url": p.get("externalUrl"), "raw": p["_raw"], "private": p.get("private")})
    ev = sorted([s for s in scored if not s["only_org"]], key=lambda s: -s["score"])
    best = ev[0] if ev else None
    conf = "none"
    if best:
        web = any("profile link" in x for x in best["reasons"])
        if web or (best["sim"] >= 0.8 and best["score"] >= 4.5):
            conf = "high"
        elif best["sim"] >= 0.6 and best["score"] >= 3.5:
            conf = "medium"
        else:
            conf = "low"
    org_name = t["organiser"] or ""
    orgs = sorted([s for s in scored if s["only_org"] or (best and s["handle"] != best["handle"] and org_name and
                   name_sim(org_name, s["handle"], s["full_name"] or "") >= 0.6)], key=lambda s: -s["score"])
    org = next((s for s in orgs if not best or s["handle"] != best["handle"]), None)
    rec = {"id": r["id"], "name": t["name"], "city": t["city"], "website": t["website"],
           "handle": best["handle"] if best else None, "confidence": conf, "best": best,
           "runners_up": ev[1:3], "organiser": org_name or None,
           "organiser_handle": org["handle"] if org else None, "organiser_pick": org}
    if r["id"] in overrides:
        o = overrides[r["id"]]
        for k in ("handle", "organiser_handle"):
            if k in o:
                rec[k] = o[k]
        rec["confidence"] = "manual" if o.get("handle") else "none"
        rec["override_note"] = o.get("note")
    out.append(rec)

with (A / "derived" / "handles_resolved.jsonl").open("w") as f:
    for rec in out:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
from collections import Counter
print(Counter(r["confidence"] for r in out))
