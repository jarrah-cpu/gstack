# Handoff: scan complete (21 Oct 2026)

All five phases are done. Deliverables are in `output/`: events_master.csv, events_master.xlsx, shortlist.md, brand_map.md, calendar.md and method.md. method.md covers sources, spend (US$61.35 of US$100 on Apify), gaps and confidence.

- Phases 2 and 3 (enrichment, verification) used the full model; Phase 4 scoring used Haiku from the records alone, and shortlist.md and method.md were written by Sonnet, to save cost. Treat scores as a first sort.
- Archive rule: discontinued events, plus on-hiatus or unknown events with a last edition before 21 Oct 2023 and no upcoming edition (`DORMANT_BEFORE` in `research/tools/merge.py`). 536 active, 46 archived.
- The 258 events outside the Phase 2 scope were not enriched, verified or scored.

Rebuild everything after a record change (venv Python): `merge.py`, then `phase5_outputs.py`. Score files: `research/score/`; apply with `phase4_apply.py`.
