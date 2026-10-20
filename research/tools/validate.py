#!/usr/bin/env python3
"""Validate one or more JSONL files against data/schema.json.

Usage: python3 research/tools/validate.py <file.jsonl> [more.jsonl ...]
Exit 0 when every line is valid, 1 otherwise.
"""
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "data" / "schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)
EM_DASH = re.compile("[—–]")


def check_file(path: Path) -> int:
    errors = 0
    seen = set()
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"{path}:{n}: invalid JSON: {e}")
            errors += 1
            continue
        rid = rec.get("id", "?")
        for err in sorted(VALIDATOR.iter_errors(rec), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in err.path) or "(root)"
            print(f"{path}:{n} [{rid}] {loc}: {err.message}")
            errors += 1
        if rid in seen:
            print(f"{path}:{n} [{rid}] duplicate id in file")
            errors += 1
        seen.add(rid)
        if EM_DASH.search(line):
            print(f"{path}:{n} [{rid}] contains an em or en dash; use commas, colons or 'to'")
            errors += 1
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    total = sum(check_file(Path(p)) for p in sys.argv[1:])
    print("OK" if total == 0 else f"{total} problem(s)")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
