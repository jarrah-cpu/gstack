#!/usr/bin/env python3
"""Record a finished Apify run: download its dataset unedited into
research/apify/raw/<step>/, read the charged cost from the run record and
append a row to research/apify/runs.md and research/apify/runs.jsonl.

Both endpoints are read without a token (run and dataset IDs act as keys).

The run's own INPUT record is saved next to the prepared input, so the
ledger shows exactly what ran.

Usage: python3 research/tools/phase2_ledger.py <run_id> <step> <label> <input_file>
       python3 research/tools/phase2_ledger.py --rebuild   (rewrite runs.md from runs.jsonl)
  step   folder under raw/, e.g. google, ig-search, ig-profile, ig-posts, crawl
  label  short name for this run, e.g. handles-all
Prints the running total. Exits 2 when the total passes the cap.
"""
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APIFY = ROOT / "research" / "apify"
CAP_USD = 100.0


def write_table(rows):
    """Rewrite the table in runs.md from the JSON ledger rows."""
    md = APIFY / "runs.md"
    text = md.read_text()
    head = text[: text.index("|---|")] + "|---|---|---|---|---|---|---|---|---|---|---|\n"
    body = []
    for r in rows:
        est = "" if r.get("cost_basis", "charged") == "charged" else " (est.)"
        body.append(f"| {r['n']} | {r['date']} | {r['step']} | {r['actor']} | `{r['input']}` | {r['items']} | "
                    f"{r['cost_usd']:.4f}{est} | {r['running_total_usd']:.4f} | {r['run_id']} | {r['dataset_id']} | `{r['raw']}` |")
    md.write_text(head + "\n".join(body) + "\n")


SECRET_PATTERNS = [
    (re.compile(r"\b(sk|pk|tk)\.eyJ[A-Za-z0-9._\-]{20,}"), "<redacted-token>"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{35}"), "<redacted-key>"),
    (re.compile(r"(?i)\b(access_token|api_key|apikey|key|token|client_secret|signature|sig|auth)=([A-Za-z0-9._%\-]{12,})"),
     r"\1=<redacted>"),
]


def redact(text):
    """Remove credential-like strings that third-party pages embed (map tokens, API keys)."""
    for pat, rep in SECRET_PATTERNS:
        text = pat.sub(rep, text)
    return text


def project_page(it):
    """Keep the crawl fields used for extraction; drop headers, raw HTML and cookies."""
    crawl, meta = it.get("crawl") or {}, it.get("metadata") or {}
    return {"url": it.get("url"), "loadedUrl": crawl.get("loadedUrl"), "status": crawl.get("httpStatusCode"),
            "depth": crawl.get("depth"), "contentType": crawl.get("contentType"), "title": meta.get("title"),
            "description": meta.get("description"), "language": meta.get("languageCode"),
            "markdown": redact(it.get("markdown") or it.get("text") or "")}


def strip_profile(p):
    """Drop related profiles (often personal accounts) and comment text from profile records."""
    p.pop("relatedProfiles", None)
    for k in ("latestPosts", "latestIgtvVideos"):
        for post in p.get(k) or []:
            for c in [post] + (post.get("childPosts") or []):
                c.pop("firstComment", None)
                c.pop("latestComments", None)
    return p


def get(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


if sys.argv[1:] == ["--rebuild"]:
    write_table([json.loads(l) for l in (APIFY / "runs.jsonl").read_text().split("\n") if l.strip()])
    sys.exit(0)
run_id, step, label, input_file = sys.argv[1:5]
ledger_json = APIFY / "runs.jsonl"
done = [json.loads(l) for l in ledger_json.read_text().split("\n") if l.strip()] if ledger_json.exists() else []
if any(r["run_id"] == run_id for r in done):
    sys.exit(f"{run_id} already recorded")

run = json.loads(get(f"https://api.apify.com/v2/actor-runs/{run_id}"))["data"]
if run["status"] not in ("SUCCEEDED", "ABORTED", "TIMED-OUT", "FAILED"):
    sys.exit(f"{run_id} is still {run['status']}")
actor = json.loads(get(f"https://api.apify.com/v2/acts/{run['actId']}"))["data"]
dataset = run["defaultDatasetId"]
n = len(done) + 1
raw = APIFY / "raw" / step / f"{n:02d}-{label}-{run_id}.jsonl"
raw.parent.mkdir(parents=True, exist_ok=True)
# Post datasets carry commenters' usernames and comment text (private individuals, not needed
# here) and are large, so only the fields used for sponsor and engagement analysis are kept.
FIELDS = {"ig-posts": "id,type,shortCode,url,caption,timestamp,likesCount,commentsCount,videoViewCount,"
                      "videoPlayCount,ownerUsername,ownerFullName,paidPartnership,isPinned,productType,"
                      "locationName,mentions,hashtags,taggedUsers,coauthorProducers,childPosts"}
fields = FIELDS.get(step)
data = get(f"https://api.apify.com/v2/datasets/{dataset}/items?format=json&clean=true" + (f"&fields={fields}" if fields else ""))
items_json = json.loads(data)
if fields:
    keep_user = ("username", "full_name", "is_verified")
    for it in items_json:
        for k in ("taggedUsers", "coauthorProducers"):
            it[k] = [{x: u.get(x) for x in keep_user} for u in (it.get(k) or [])]
        it["childPosts"] = [{"taggedUsers": [{x: u.get(x) for x in keep_user} for u in (c.get("taggedUsers") or [])]}
                            for c in (it.get("childPosts") or []) if c.get("taggedUsers")]
if step == "crawl":
    items_json = [project_page(it) for it in items_json]
if step in ("ig-profile", "ig-search"):
    items_json = [strip_profile(it) for it in items_json]
raw.write_text(redact("".join(json.dumps(it, ensure_ascii=False) + "\n" for it in items_json)))
items = sum(1 for l in raw.read_text().split("\n") if l.strip())
actual_input = APIFY / "inputs" / f"{n:02d}-{label}.actual-input.json"
actual_input.write_bytes(get(f"https://api.apify.com/v2/key-value-stores/{run['defaultKeyValueStoreId']}/records/INPUT"))
CU_PRICE = 0.16  # Scale plan rate per compute unit, apify.com/pricing (20 Oct 2026)
if run.get("usageTotalUsd") is not None:
    cost, cost_basis = round(run["usageTotalUsd"], 4), "charged"
else:  # platform-billed actors do not expose usage without a token
    cost, cost_basis = round((run["stats"].get("computeUnits") or 0) * CU_PRICE, 4), "estimate: compute units x US$0.16"
total = round(sum(r["cost_usd"] for r in done) + cost, 4)

rec = {"n": n, "date": date.today().isoformat(), "step": step, "label": label,
       "actor": f"{actor['username']}/{actor['name']}", "status": run["status"],
       "input": input_file, "actual_input": str(actual_input.relative_to(ROOT)), "items": items, "cost_usd": cost, "cost_basis": cost_basis, "running_total_usd": total,
       "run_id": run_id, "dataset_id": dataset, "fields_kept": fields, "raw": str(raw.relative_to(ROOT)),
       "charged_events": run.get("chargedEventCounts")}
with ledger_json.open("a") as f:
    f.write(json.dumps(rec) + "\n")
write_table(done + [rec])
print(f"run {n} {rec['actor']} {run['status']}: {items} items, US${cost:.4f}, running total US${total:.4f} of US${CAP_USD:.0f}")
if total >= CAP_USD:
    print("CAP REACHED: stop all Apify runs")
    sys.exit(2)
