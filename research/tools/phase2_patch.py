#!/usr/bin/env python3
"""Shared patch logic for Phase 2 enrichment patches (research/apify/enrich/<id>.json)."""
import copy
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "data" / "schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)
DASH = re.compile("[—–]")
SETTABLE = {"website", "attendance", "audience", "partnership_contact", "ticket_price", "organiser", "dates", "status",
            "location"}
KEYS = {"id", "set", "add_sponsors", "add_activation_formats", "add_sources", "add_gaps", "remove_gaps", "notes"}


def apply(rec, patch):
    """Return a patched copy of rec. Raises ValueError on a malformed patch."""
    extra = set(patch) - KEYS
    if extra:
        raise ValueError(f"unknown keys {sorted(extra)}")
    out = copy.deepcopy(rec)
    for k, v in (patch.get("set") or {}).items():
        if k not in SETTABLE:
            raise ValueError(f"set.{k} is not allowed")
        out[k] = v
    have = {(s["brand"].lower(), s.get("role")) for s in out["sponsors"]}
    for s in patch.get("add_sponsors") or []:
        same = [x for x in out["sponsors"] if x["brand"].lower() == s["brand"].lower()]
        if same:
            x = same[0]
            x["years"] = sorted(set(x["years"]) | set(s.get("years") or []))
            if x.get("role") in (None, "unknown") and s.get("role"):
                x["role"] = s["role"]
            if not x.get("source"):
                x["source"] = s.get("source")
        elif (s["brand"].lower(), s.get("role")) not in have:
            out["sponsors"].append(s)
    for f in patch.get("add_activation_formats") or []:
        if f not in out["activation_formats"]:
            out["activation_formats"].append(f)
    seen = {(s["field"], s["url"]) for s in out["sources"]}
    for s in patch.get("add_sources") or []:
        if (s.get("field"), s.get("url")) not in seen:
            out["sources"].append(s)
            seen.add((s.get("field"), s.get("url")))
    rm = set(patch.get("remove_gaps") or [])
    out["gaps"] = [g for g in out["gaps"] if g not in rm]
    for g in patch.get("add_gaps") or []:
        if g not in out["gaps"]:
            out["gaps"].append(g)
    return out


def problems(rec, patch):
    """List problems with a patch applied to rec (schema, dashes, unsourced claims)."""
    errs = []
    try:
        new = apply(rec, patch)
    except Exception as e:  # malformed patch
        return [str(e)]
    for err in VALIDATOR.iter_errors(new):
        errs.append("schema: " + ("/".join(str(p) for p in err.path) or "(root)") + ": " + err.message)
    if DASH.search(json.dumps(patch, ensure_ascii=False)):
        errs.append("contains an em or en dash")
    fields = {s.get("field", "").split(".")[0] for s in patch.get("add_sources") or []}
    for k in (patch.get("set") or {}):
        if k not in fields and k not in ("status",):
            errs.append(f"set.{k} has no matching add_sources entry (field '{k}...')")
    if patch.get("add_sponsors") and "sponsors" not in fields and not all(s.get("source") for s in patch["add_sponsors"]):
        errs.append("add_sponsors without a source")
    for s in patch.get("add_sponsors") or []:
        if not s.get("source"):
            errs.append(f"sponsor {s.get('brand')} has no source")
    return errs
