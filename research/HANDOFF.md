# Handoff: where the scan stopped (21 Oct 2026)

Stopped at the user's request to limit token cost. Phases 2 and 3 are done and committed; Phases 4 and 5 have not run.

## Done
- **Phase 2 (enrichment):** the 311 filtered events (vibe 3+, next edition by 20 Apr 2028). Apify spend US$61.35 of the US$100 cap, every run in `research/apify/runs.md`. Instagram on 279 events (follower counts on 240), websites on 269, attendance on 143, sponsors on 273 (3,365 entries), partnership contact on 214. Agent patches: `research/apify/enrich/`; orchestrator fixes: `research/apify/fixes/`; agent notes: `research/apify/enrich_notes.md`.
- **Phase 3 (verification):** seven separate verifier agents checked all 310 active targets; 121 patches in `research/verify/`, notes in `research/verify/verify_notes.md`. Records are marked `verified`.
  - HIGH GROUND name clash: a separate Melbourne winter music series run by Calibre (CLBR), 28 May to 29 Aug 2026, likely to recur in 2027; Leaps and Bounds co-presented one night. Flag on `leaps-and-bounds-music-festival`.
  - Soundrenaline: presented by Resonine in 2026; no current source names Sampoerna or A Mild, but unnamed partner logos mean tobacco backing cannot be ruled out.
  - Descend on Bend archived as discontinued.

## Not done
1. **Archive policy for long-dormant events.** Verifiers set dormant events to on-hiatus or unknown rather than discontinued, so `merge.py` keeps them active. The schema says long-dormant events also belong in `data/archived.jsonl`. Candidates include Mulafest, Musink, Pro Zarautz, Byron Bay Surf Festival, Here Comes The Sun Torquay, plus older non-target events (last edition before Oct 2023). Decide a rule, then extend `merge.py`.
2. **Phase 4 scoring.** Rules: `research/SCORE.md`. Batches: `research/score/batches/score-1..7.txt`. Checker: `research/tools/phase4_check_score.py`. Weights in `research/tools/phase4_scoring.py`. A script to write `research/score/*.json` into `scores`, `vibe` and `fit_notes` still needs writing.
3. **Phase 5 outputs.** `python research/tools/phase5_outputs.py` (venv) builds `output/events_master.csv`, `.xlsx`, `calendar.md`, `brand_map.md` and `shortlist_data.json` (works now, scores blank). `shortlist.md` and `method.md` still need writing; start method.md from `research/checkpoint-phase1.md`, `research/apify/runs.md` and the notes files.

## Method points to carry into method.md
- Instagram posts were scraped back to 1 Oct 2025 only (the latest edition for annual events), not two editions: two editions would have cost about US$98 for posts alone.
- Saved Instagram data drops comment text, commenters' usernames and related-profile lists (public repo); crawled pages have third-party tokens redacted.
- Verifier budgets ran out before every search-snippet note on vibe 3 events was opened; those remain marked "Google snippet" in `sources[].note`.

Python tools need the venv: `"/Users/jarrahkammoora/Documents/Claude/Personal/HG Event Planning/.venv/bin/python"`.
