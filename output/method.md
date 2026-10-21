# Method: subculture festival and event scan

Date: 21 Oct 2026. This is research to inform High Ground's event partnership and activation strategy. Legal and compliance review happens separately, so no event was filtered or caveated on regulatory grounds. The benchmark is SURPLUS Sydney, and every event is compared with it on four traits: an authentic community core, a vibey and welcoming feel, curation rather than mass-market, and brands that fit without feeling corporate.

## Scope and phases

The scan covers two sets. Set A is Australian events like SURPLUS, across ten cities from Sydney to Darwin. Set B is global subculture festivals in Australia, New Zealand, Portugal, Spain, Japan, the US West Coast, South America and Indonesia and Bali.

1. **Phase 1, discovery (20 Oct 2026).** Fourteen regional agents searched the web. The network policy blocked direct page fetches, so every fact came from search results: about 730 searches in all, across a first pass (which hit the session's cap of about 200 searches per turn) and a top-up pass. Result: 569 events that were active, on hiatus or of unknown status, plus 13 found already discontinued. Records were merged on id with an alias file (13 cross-region merges) and suspected duplicates were checked by hand. Each carries a preliminary vibe score from 1 to 5.
2. **Phase 2, Apify enrichment (20 to 21 Oct).** Limited to the 311 events with a preliminary vibe score of 3 or more and a next edition by 20 Apr 2028, under an approved hard cap of US$100. Result: Instagram accounts on 279 events (follower counts on 240), websites on 269, attendance figures on 143, sponsors on 273 events (3,365 entries) and a partnership contact on 214.
3. **Phase 3, verification (21 Oct).** Seven verifier agents, separate from the agents that gathered the data, checked the 310 active targets and the one discontinued event. They checked status and next-edition dates, attendance and (for vibe 4 and 5 events) major sponsors against a second source, and facts that rested on search summaries. They patched 121 records and left flags where a check failed or could not be settled (`record_meta.verifier_flags`, on 100 active records).
4. **Phase 4, scoring.** Agents scored the 308 targets still active on vibe fit (1 to 5 against the SURPLUS rubric), audience fit (1 to 5, how well the audience suits a health brand), scale band, accessibility (open, selective or locked) and cost signal. A script computes the weighted total: vibe fit 35 per cent, audience fit 35, scale 10, accessibility 10, cost 10. Mid-size events score best on scale, and an unknown scale takes a neutral mid value.
5. **Phase 5, outputs.** One script builds the master CSV and workbook, the calendar, the brand map and the shortlist data. `shortlist.md` is written from those records.

## Sources and tools

Phase 2 used five Apify actors on the Scale plan: 29 runs and US$61.35 in total, against the US$100 cap.

| Actor | Used for | Runs | Spend (US$) |
|---|---|---|---|
| apify/google-search-scraper | Handle lookups (site:instagram.com searches) and regional press queries on attendance, sponsors and audience | 11 | 2.52 |
| apify/instagram-search-scraper | Finding Instagram handles by event name | 2 | 0.32 |
| apify/instagram-profile-scraper | Followers, bio, link and counts for event, organiser and tagged accounts | 5 | 3.86 |
| apify/instagram-post-scraper | Sponsor and collaboration signals from posts since 1 Oct 2025 | 7 | 52.34 |
| apify/website-content-crawler | Sponsor, partner, about, press, media kit and contact pages | 4 | 2.32 (estimated) |

The crawler's cost is estimated from compute units at US$0.16 each, because its run record does not show platform usage. The other figures are charged amounts. Every run, with its run ID, dataset ID, input file, raw file and cost, is in `research/apify/runs.md`.

Other tools:

- **Local homepage scans.** Free scripts fetched each target's event and organiser homepage, listed the Instagram accounts it links to, and picked the partner, sponsor, about, press and contact pages worth crawling. Page content was parsed for links only.
- **WebFetch checks.** Phase 2 agents (up to 12 calls each) and Phase 3 verifiers (up to 25 calls and 15 searches each) opened cited pages to confirm or complete facts. Phase 1 had no fetch access, and some pages refused later fetches.
- **Evidence packs.** Each target has a Markdown pack (`research/apify/evidence/<region>/<id>.md`) holding its current record, Instagram stats, sponsor signals from posts, keyword-filtered crawl lines and Google results on attendance, sponsors and audience.
- **Patch workflow.** Agents did not edit records. Each wrote one JSON patch per event (311 in Phase 2, 121 in Phase 3), and a validator checked it. The orchestrator applied valid patches to the regional candidate files, which stay the source of truth, and `merge.py` rebuilt `data/events.jsonl`. Every change needs a matching source entry.

## Data rules

- Every factual claim has a source URL in `sources[]`, with the field it supports and a note. Sponsors and attendance also carry their own source.
- Unknown means `null` plus a line in `gaps[]`. Dates, numbers, handles and emails are never invented, and emails are copied exactly as published.
- Estimates are marked `is_estimate: true`. Organiser-reported figures say so in the note. Attendance is never derived from follower counts or capacity guesses.
- Audience details (age, gender, psychographics) come only from a published source, or are marked "inferred from IG audience signals".
- Artists, performers and individual makers are not sponsors. A brand that only runs a stall is recorded as `vendor-or-stall`.

## Archive rule

`research/tools/merge.py` moves a record to `data/archived.jsonl` when its status is discontinued, or when it is on-hiatus or unknown, its last edition began before `DORMANT_BEFORE` (21 Oct 2023, three years before the scan date, compared at the precision the record holds) and it has no confirmed or expected next edition. Verifiers had marked long-dormant events on-hiatus or unknown instead of discontinued, which is why the second test exists.

Result: 536 records stay in `data/events.jsonl` (473 active, 52 unknown, 11 on-hiatus) and 46 are archived (14 discontinued, 13 on-hiatus, 19 unknown). Three of the 311 Phase 2 targets are among the archived, which leaves 308 active and scored. Archived events are kept for reference, not deleted.

## Confidence and known gaps

- **Instagram depth.** Posts were scraped from 1 Oct 2025 only, which is the latest edition for annual events. Seven post runs cost US$52.34. Going back two editions would have cost about US$98 for posts alone, so sponsor rosters are mostly one edition deep.
- **Google snippets.** Facts that rest on a search snippet are marked in the source notes. Verifier budgets ran out before every snippet note on vibe 3 events was opened, and some pages blocked fetches, so not all were re-opened.
- **Demographics.** Published demographics are rare: 26 of the 536 active records have an age range and 11 a gender skew. Audience fit therefore rests mostly on descriptions of the crowd, not measured age or gender.
- **Attendance.** Figures vary in kind: tickets, entries, riders, registration caps, listed capacity, organiser projections and press estimates. Festival Iminente counts entries, The Traka counts participants and Waking Life's 8,000 is a listed capacity. Some are old (Zushi's 15,000 dates from 2019). 161 of the 536 active records have a figure, and 167 of the 308 scored events have no usable scale band.
- **Sponsor names.** Some come from logo file names or link domains, some roles were inferred from list order, and rosters are partial.
- **Out-of-scope events.** The 258 events outside Phase 2 were not enriched, verified or scored. 228 of them remain in `data/events.jsonl` with Phase 1 data and a preliminary vibe score only.
- **Scoring.** A lighter model scored events from the records alone, with no new research. Scores are a first sort, not a final ranking, and the accessibility and cost signals are judgement calls.

## Privacy and safety of the public repo

- Instagram data keeps no comment text and no commenters' usernames. Tagged accounts keep only username, display name and verified flag. Related-profile lists and images are dropped, and latest posts keep only dates, counts, mentions, tagged usernames and a 300-character caption.
- Crawled pages keep only URL, status, title, description, language and markdown. Token-shaped strings that third-party sites embed, such as map tokens and API keys, are redacted.
- Contacts in the records are those published for partnership, sponsorship, media or general enquiries.
- The full Apify datasets stay on Apify under the dataset IDs in `runs.md`, for the account's retention period.

## Files

- `output/events_master.csv` and `output/events_master.xlsx`: one row per event, with category and region tabs in the workbook.
- `output/calendar.md`: next editions from 21 Oct 2026 to 20 Apr 2028, in date order.
- `output/brand_map.md`: brands and the events they sponsor, with role, years and source.
- `output/shortlist.md`: the top 15 overall, the top 5 per category and watch-outs.
- `data/events.jsonl`: the 536 records still in play.
- `data/archived.jsonl`: the 46 archived records.
- `research/apify/runs.md`: the Apify run ledger and spend.
