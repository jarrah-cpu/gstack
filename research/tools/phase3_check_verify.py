#!/usr/bin/env python3
"""Check Phase 3 verification patches (research/verify/<id>.json) in verify mode.

Usage: python3 research/tools/phase3_check_verify.py research/verify/<id>.json [...]
"""
import os
import runpy
from pathlib import Path

os.environ["PATCH_MODE"] = "verify"
runpy.run_path(str(Path(__file__).with_name("phase2_check_patch.py")), run_name="__main__")
