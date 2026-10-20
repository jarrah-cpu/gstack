#!/usr/bin/env python3
"""Shared helpers for the Phase 2 scripts: name normalising and matching."""
import re
import unicodedata
from difflib import SequenceMatcher

STOP = {"the", "festival", "fest", "of", "and", "de", "del", "la", "el", "market", "markets", "in", "by", "x"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def words(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return [w for w in re.findall(r"[a-z0-9]+", s) if w not in STOP]


def name_sim(name, handle, label=""):
    """0 to 1: how well a handle or profile label matches the event name."""
    n, h = norm(re.sub(r"\([^)]*\)", "", name)), norm(handle)
    core = "".join(words(re.sub(r"\([^)]*\)", "", name)))
    scores = [SequenceMatcher(None, n, h).ratio(), SequenceMatcher(None, core, h).ratio()]
    if core and (core in h or h in core) and len(h) >= 4:
        scores.append(0.9)
    if label:
        scores.append(SequenceMatcher(None, n, norm(label)).ratio())
    return round(max(scores), 3)
