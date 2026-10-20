# Phase 1 top-up pass: rules

The first discovery pass ran 14 agents at once and hit the session's shared web-search cap (about 200 searches per turn across all agents) after 11 to 26 searches each. Most regions only covered music festivals and their starting leads. This top-up pass runs in waves of five agents so each one gets a real budget.

Read `research/BRIEF.md` first. Everything there still applies (WebSearch only, sourcing, nulls, no em or en dashes, Australian English). These extra rules override it where they differ:

1. **Hard search cap: 36 WebSearch calls.** Count them. Stop at 36 even if leads remain. If a search returns a budget or limit error, stop searching immediately and write up what you have. Use `mode: "extended"` for at most 12 of them.
2. **Start from the existing files.** Read `research/<region>/candidates.md` (especially "Leads not pursued" and "Gaps") and `research/<region>/candidates.jsonl` before searching. Do not re-search events that are already recorded unless the region prompt asks you to fix one.
3. **Spend searches on coverage, not polish.** Priority order: (a) subculture strands and lead lists named in your region prompt, (b) the SURPLUS snowball (`research/benchmark/surplus.md`), (c) fixing statuses or dates the prompt flags. Do not spend searches hunting Instagram handles or follower counts: Phase 2 collects those. Record a handle only when a result shows it.
4. **Keep existing records.** Append new records. When you learn something new about an existing record, update that record in place (fill nulls, add sources, correct status) and set `record_meta.updated` to 2026-10-20. Never delete a record; mark it `discontinued` or `on-hiatus` with a source instead.
5. **Scratch files.** Write any helper script or notes only under `/tmp/claude-0/-home-user-gstack/23ce11a6-ca04-500d-9ade-f27d7c15c739/scratchpad/<region>/`, with your region in the filename (e.g. `build_a_sydney.py`). Never run a script you did not write in this pass. Other agents share the scratchpad.
6. **Update `candidates.md`.** Refresh the header count and date, add new rows to the table, rewrite "Leads not pursued" and "Gaps" to reflect what is still open after this pass, and add a one-line "Top-up pass" note saying how many searches you used and what you covered.
7. **Validate:** `python3 research/tools/validate.py research/<region>/candidates.jsonl` must print OK.
8. **Return** 12 lines or fewer: new record count and total, strands now covered, the three best new finds with preliminary vibe scores, and what is still open.
