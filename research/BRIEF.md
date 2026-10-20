# Discovery brief: Subculture Festival and Event Landscape Scan

Shared brief for every Phase 1 discovery agent. Read this, `data/schema.json` and `research/benchmark/surplus.md` before you search.

## Purpose

Research to inform High Ground's event partnership and activation strategy. High Ground is an Australian health brand. Output is research only. Legal and compliance review happens separately, so do not filter or caveat on regulatory grounds.

## Benchmark

SURPLUS Sydney. See `research/benchmark/surplus.md` for facts, the brand roster to snowball from, and the 1 to 5 vibe rubric.

## Scope

**A. Australia, events like SURPLUS.** Cities: Sydney, Melbourne, Brisbane, Gold Coast, Northern Rivers/Byron, Adelaide, Perth, Hobart, Canberra, Darwin. Types: streetwear and culture festivals, creative markets, design and art weeks, skate/surf/culture weekends, independent music festivals and club culture, makers' and vintage events, food and culture night markets.

**B. Global subculture festivals.** Regions: Australia, New Zealand, Portugal, Spain, Japan, California and the wider US West Coast, South America (Brazil, Chile, Argentina, Peru), Indonesia/Bali. Subcultures (expand if you find others): longboarding and downhill skate, skateboarding, surf (incl. log and single-fin), sneaker and streetwear, independent and electronic music, van life and overlanding, climbing and bouldering, gravel and fixed-gear cycling, tattoo, vintage motorcycle and custom builds (Deus-style), wellness and breathwork, art and street art, zines and independent publishing.

## Method

1. **Search tooling.** In this environment only `WebSearch` reaches the internet. `WebFetch` and `curl` are blocked by the network policy (DNS failure or proxy 403), so do not use them. Take facts and URLs from search results. Use `mode: "extended"` for roundup and list-building queries (about a third of your searches) and `mode: "standard"` for single-fact lookups. Budget: roughly 40 to 80 searches.
2. **Query patterns.** "<subculture> festival <city> 2026", "best <type> festivals <region> 2026 2027", publication guides (Broadsheet, Concrete Playground, Time Out, Hypebeast, Highsnobiety, Tone Deaf, Resident Advisor, plus strong local equivalents), "brands sponsored <event>", "<event> partners sponsors", "<event> attendance", "<event> instagram".
3. **Snowball.** Take the SURPLUS roster in `research/benchmark/surplus.md` and trace where the same brands, vendors and collectives appear in your region. Also trace adjacent culture-event sponsors you meet along the way (for example Red Bull, Vans, Converse, Deus Ex Machina, Patagonia, Salomon, New Balance, Heaps Normal, Young Henrys). Note any new events this surfaces.
4. **Target.** 15 to 40 candidates for your region. Quality over padding: a candidate should plausibly meet at least two of the four qualifying traits. Include notable mass-market events only if they have a genuine subculture strand, and score them honestly low.
5. **Timing.** Today is 20 Oct 2026. Prioritise events with a next edition between now and April 2028. Still record discontinued or dormant events you come across, with `status` set to `discontinued` or `on-hiatus`, so they can be archived.

## Data rules

- Australian English. Plain and direct. No em dashes or en dashes anywhere (write "16 to 18 Oct", not a dash range). The validator rejects them.
- Cite a source URL for every factual field in `sources[]` (one entry per claim, `field` names the schema path). Sponsors and attendance also carry their own `source`.
- Unknown means `null` plus a line in `gaps[]`. Never invent numbers, dates, handles or emails. Mark estimates with `is_estimate: true`. Organiser-reported figures are not estimates but say "organiser-reported" in the note.
- Instagram: record the handle and URL when a search result shows it. Record a follower count only when a search result shows one, with `followers_source: "search snippet"` and `followers_as_of` set to today. Phase 2 will collect counts properly.
- Vibe score: give one at discovery with `preliminary: true` and a one-line rationale against the rubric.
- Fit notes: one or two lines on why the event suits High Ground or not. Consider audience age (adult share), lifestyle and wellness adjacency, community depth, and whether non-endemic brands have partnered before.
- `scores` stays all null except `scale_band` and `accessibility` when the evidence is clear.
- `record_meta`: `{"phase": "discovery", "updated": "2026-10-20"}`.
- `scope`: "A" for Australian SURPLUS-like events, "B" for global subculture festivals, "A+B" for Australian events that are both.
- `id`: kebab-case slug, event name plus city where needed (e.g. `bowl-a-rama-bondi`). Check `research/benchmark/candidates.jsonl` for the format of a complete record.

## Outputs (write only inside your own region folder)

1. `research/<region>/candidates.jsonl`: one schema-valid record per line.
2. `research/<region>/candidates.md`: a short header (region, candidate count, date), a table (name, category, city, next edition, IG handle, preliminary vibe score, one-line why), then a "Leads not pursued" list (names you saw but could not confirm, with the URL that mentioned them) and a "Gaps" paragraph.
3. Validate before finishing: `python3 research/tools/validate.py research/<region>/candidates.jsonl`. Fix every error it reports.

Do not edit files outside your region folder. Do not run git commands. Duplicates across regions are fine; the orchestrator dedupes on merge.

## What to return

A reply of 15 lines or fewer: candidate count, the five strongest picks with vibe scores, the number with a confirmed next edition, and the main gaps. Do not paste the records back.
