#!/usr/bin/env python3
"""Write Phase 2 enrichment into the region candidates files (the source of truth).

For each of the 311 target events, in every region file that holds a copy
(directly or through research/tools/aliases.json):
  1. Instagram block from the resolved handles and Apify profile data
     (followers, posts, bio, mean likes plus comments over the last 12 posts).
  2. Website, when the record has none and the event's own Instagram profile
     links to a real site (research/apify/derived/new_websites.json).
  3. The agent patch research/apify/enrich/<id>.json, if present and valid, then any
     orchestrator fix in research/apify/fixes/<id>.json (verify mode).
  4. record_meta.phase = "enriched", record_meta.updated = today.
Invalid patches are skipped and reported. Run merge.py afterwards.

Usage: python3 research/tools/phase2_apply.py [--dry-run]
"""
import glob
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from phase2_patch import VALIDATOR, apply, problems  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "research" / "apify"
TODAY = date.today().isoformat()
DRY = "--dry-run" in sys.argv


def jl(p):
    return [json.loads(l) for l in Path(p).read_text().split("\n") if l.strip()]


aliases = json.loads((ROOT / "research" / "tools" / "aliases.json").read_text())
targets = {t["id"] for t in jl(A / "targets.jsonl")}
resolved = {r["id"]: r for r in jl(A / "derived" / "handles_resolved.jsonl")}
new_sites = json.loads((A / "derived" / "new_websites.json").read_text())
runs = {r["raw"]: r for r in jl(A / "runs.jsonl")}
prof = {}
for f in sorted(glob.glob(str(A / "raw" / "ig-search" / "*.jsonl"))) + sorted(glob.glob(str(A / "raw" / "ig-profile" / "*.jsonl"))):
    run = runs.get(str(Path(f).relative_to(ROOT)))
    for p in jl(f):
        if p.get("username") and p.get("followersCount") is not None:
            prof[p["username"].lower()] = (p, run)


def no_dashes(text):
    """House style: no em or en dashes. Ranges become 'to', other dashes a comma."""
    if not text:
        return text
    text = re.sub(r"(\d)\s*[\u2013\u2014]\s*(\d)", r"\1 to \2", text)
    return re.sub(r"\s*[\u2013\u2014]\s*", ", ", text)


def engagement(p):
    vals = [(x.get("likesCount") or 0) + (x.get("commentsCount") or 0) for x in (p.get("latestPosts") or [])[:12]
            if not x.get("isPinned") and (x.get("likesCount") or 0) >= 0]
    return round(sum(vals) / len(vals), 1) if vals else None


def instagram_block(rec, r):
    ig = dict(rec["instagram"])
    srcs, gaps = [], []
    h, oh = r["handle"], r["organiser_handle"]
    if h and h in prof:
        p, run = prof[h]
        ig.update({"handle": "@" + p["username"], "url": f"https://www.instagram.com/{p['username']}/",
                   "followers": p["followersCount"], "followers_as_of": run["date"],
                   "followers_source": f"apify-instagram-profile-scraper (run {run['run_id']})" if run["step"] == "ig-profile"
                   else f"apify-instagram-search-scraper (run {run['run_id']})",
                   "post_count": p.get("postsCount"), "bio": no_dashes(p.get("biography") or None),
                   "avg_recent_engagement": engagement(p)})
        srcs.append({"field": "instagram", "url": ig["url"],
                     "note": f"Apify {run['actor']} run {run['run_id']} on {run['date']}: followers, posts, bio; engagement = mean likes plus comments over the last 12 posts."
                             + (f" Account choice: {r['override_note']}" if r.get("override_note") else "")})
    elif not h:
        ig.update({"handle": None, "url": None, "followers": None, "followers_as_of": None, "followers_source": None})
        gaps.append("No Instagram account of the event's own found in Phase 2 (event site, Google and Instagram search)"
                    + (f"; {r['override_note']}" if r.get("override_note") else ""))
    if oh and oh in prof and oh != h:
        p, run = prof[oh]
        ig.update({"organiser_handle": "@" + p["username"], "organiser_url": f"https://www.instagram.com/{p['username']}/",
                   "organiser_followers": p["followersCount"]})
        srcs.append({"field": "instagram.organiser_handle", "url": ig["organiser_url"],
                     "note": f"Apify {run['actor']} run {run['run_id']} on {run['date']}."})
    return ig, srcs, gaps


IG_GAP = re.compile(r"instagram|\bIG\b|follower", re.I)
report = {"updated": 0, "patched": 0, "bad_patches": {}, "no_patch": []}
for f in sorted(glob.glob(str(ROOT / "research" / "*" / "candidates.jsonl"))):
    recs = jl(f)
    changed = False
    for i, rec in enumerate(recs):
        cid = aliases.get(rec["id"], rec["id"])
        if cid not in targets:
            continue
        new = json.loads(json.dumps(rec))
        r = resolved[cid]
        ig, srcs, gaps = instagram_block(new, r)
        new["instagram"] = ig
        if ig.get("handle"):
            new["gaps"] = [g for g in new["gaps"] if not IG_GAP.search(g)]
        seen = {(s["field"], s["url"]) for s in new["sources"]}
        new["sources"] += [s for s in srcs if (s["field"], s["url"]) not in seen]
        new["gaps"] += [g for g in gaps if g not in new["gaps"]]
        ns = new_sites.get(cid)
        if not new["website"] and ns and r["handle"] and ns["source"].endswith("@" + r["handle"]):
            new["website"] = ns["url"]
            new["sources"].append({"field": "website", "url": f"https://www.instagram.com/{r['handle']}/",
                                   "note": f"Official site taken from the event's Instagram profile link ({ns['url']})."})
        pf = A / "enrich" / f"{cid}.json"
        if pf.exists():
            patch = json.loads(pf.read_text())
            patch["id"] = new["id"]
            errs = problems(new, patch)
            if errs:
                report["bad_patches"][cid] = errs
            else:
                new = apply(new, patch)
                report["patched"] += 1
        else:
            report["no_patch"].append(cid)
        ff = A / "fixes" / f"{cid}.json"  # orchestrator corrections, verify mode (role changes, removals, renames)
        if ff.exists():
            fix = json.loads(ff.read_text())
            fix["id"] = new["id"]
            errs = problems(new, fix, "verify")
            if errs:
                report["bad_patches"][cid + " (fix)"] = errs
            else:
                new = apply(new, fix, "verify")
        new["record_meta"] = {**new["record_meta"], "phase": "enriched", "updated": TODAY}
        errs = list(VALIDATOR.iter_errors(new))
        if errs:
            report["bad_patches"].setdefault(cid, []).extend("final: " + e.message for e in errs)
            continue
        recs[i] = new
        changed = True
        report["updated"] += 1
    if changed and not DRY:
        Path(f).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in recs))
print(f"records updated {report['updated']}, patches applied {report['patched']}, "
      f"targets without a patch {len(set(report['no_patch']))}, bad patches {len(report['bad_patches'])}")
for k, v in report["bad_patches"].items():
    print(" ", k, v[:3])
