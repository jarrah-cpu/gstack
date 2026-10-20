# Phase 4 scoring: rules for scoring agents

Read `research/BRIEF.md`, `research/benchmark/surplus.md` (the vibe rubric) and this file first. Score each event in your batch from its full record in `data/events.jsonl` (grep by id) and, where useful, its evidence pack `research/apify/evidence/<region>/<id>.md`. Do not research further: no WebSearch or WebFetch. Score on the evidence in the record; where evidence is thin, say so in the rationale and score cautiously.

High Ground is an Australian health brand. This is research to inform its event partnership and activation strategy. Legal and compliance review happens separately, so do not mark events down on regulatory grounds.

## Scores (all required)

**vibe_fit (1 to 5)**: the SURPLUS rubric in `research/benchmark/surplus.md`. Use the four qualifying traits: authentic community core; vibey, welcoming, slightly alternative; curated not mass-market; brand-friendly without feeling corporate.

**audience_fit (1 to 5)**: how well the audience suits a health brand, judged on the audience itself (not on where the event is):

| Score | Meaning |
|---|---|
| 5 | Adult audience (mostly 18 to 45), clear wellness, active-lifestyle or self-care adjacency, deep community, and a precedent of non-endemic or health brands partnering. |
| 4 | Adult, lifestyle-led audience with a plausible health or wellness angle and a strong community; precedent optional. |
| 3 | Adult audience but weak wellness adjacency or a generic crowd; or a good audience that is hard for brands to reach (strict no-sponsor culture). |
| 2 | Skews young, family or all-ages, or a niche hobby crowd with little health relevance. |
| 1 | Misaligned: children, trade-only, or an audience that rejects brands outright. |

**scale_band**: from `attendance` (use figure_high if given). `<1k`, `1k-5k`, `5k-20k`, `20k-50k`, `50k-100k`, `100k+`, or `unknown` when there is no figure. Do not guess.

**accessibility**: `open` (several partners and visibly seeking more: partner pages, sponsorship calls, media kits), `selective` (has partners but curated or invitation-led), `locked` (single dominant or naming sponsor, brand-owned, or a no-sponsor policy), `unknown`.

**cost_signal**: likely cost of a meaningful partnership. `low` (small community event, stall or in-kind level), `medium` (mid-size, packaged partnerships), `high` (major festival or brand-owned property), `unknown`.

The orchestrator computes `weighted_total` from these (vibe 35 per cent, audience 35, scale 10, accessibility 10, cost 10); do not compute it.

## Text fields

- `vibe_rationale`: one line, why that vibe score against SURPLUS.
- `fit_notes`: one or two lines on why the event suits High Ground or not (audience age, wellness adjacency, community depth, non-endemic brand precedent, activation formats on offer, and whether High Ground could activate there directly as an Australian brand).

## Output

Write `research/score/<id>.json` for every event in your batch:

```json
{"id": "event-id", "vibe_fit": 4, "vibe_rationale": "...", "audience_fit": 4, "scale_band": "5k-20k",
 "accessibility": "open", "cost_signal": "medium", "fit_notes": "..."}
```

Validate: `"/Users/jarrahkammoora/Documents/Claude/Personal/HG Event Planning/.venv/bin/python" research/tools/phase4_check_score.py research/score/<id>.json` and fix every error. Australian English, no em dashes or en dashes. Do not run git or edit other files.

## Return

Eight lines or fewer: events scored, score distribution, and the five strongest fits for High Ground in your batch with one line each.
