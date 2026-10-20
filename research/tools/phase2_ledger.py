#!/usr/bin/env python3
"""Record a finished Apify run: download its dataset unedited into
research/apify/raw/<step>/, read the charged cost from the run record and
append a row to research/apify/runs.md and research/apify/runs.jsonl.

Both endpoints are read without a token (run and dataset IDs act as keys).

The run's own INPUT record is saved next to the prepared input, so the
ledger shows exactly what ran.

Usage: python3 research/tools/phase2_ledger.py <run_id> <step> <label> <input_file>
  step   folder under raw/, e.g. google, ig-search, ig-profile, ig-posts, crawl
  label  short name for this run, e.g. handles-all
Prints the running total. Exits 2 when the total passes the cap.
"""
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APIFY = ROOT / "research" / "apify"
CAP_USD = 100.0


def get(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


run_id, step, label, input_file = sys.argv[1:5]
ledger_json = APIFY / "runs.jsonl"
done = [json.loads(l) for l in ledger_json.read_text().splitlines() if l.strip()] if ledger_json.exists() else []
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
raw.write_bytes(get(f"https://api.apify.com/v2/datasets/{dataset}/items?format=jsonl&clean=true"))
items = sum(1 for l in raw.read_text().splitlines() if l.strip())
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
       "run_id": run_id, "dataset_id": dataset, "raw": str(raw.relative_to(ROOT)),
       "charged_events": run.get("chargedEventCounts")}
with ledger_json.open("a") as f:
    f.write(json.dumps(rec) + "\n")
with (APIFY / "runs.md").open("a") as f:
    f.write(f"| {n} | {rec['date']} | {step} | {rec['actor']} | `{input_file}` | {items} | {cost:.4f}{'' if cost_basis == 'charged' else ' (est.)'} | {total:.4f} | "
            f"{run_id} | {dataset} | `{rec['raw']}` |\n")
print(f"run {n} {rec['actor']} {run['status']}: {items} items, US${cost:.4f}, running total US${total:.4f} of US${CAP_USD:.0f}")
if total >= CAP_USD:
    print("CAP REACHED: stop all Apify runs")
    sys.exit(2)
