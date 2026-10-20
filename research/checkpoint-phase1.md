# Phase 1 checkpoint: discovery complete

Date: 20 Oct 2026. Source data: `data/events.jsonl` (569 active, on-hiatus or unknown) and `data/archived.jsonl` (13 discontinued). Regenerate this table with `python3 research/tools/merge.py && python3 research/tools/checkpoint.py`.

## Candidate count per region

| Region | Events | Next edition confirmed | Next edition in 18-month window | Vibe 4+ | Hiatus or unknown | Archived |
|---|---|---|---|---|---|---|
| a-sydney | 40 | 6 | 15 | 13 | 11 | 3 |
| a-melbourne | 43 | 14 | 33 | 16 | 6 | 0 |
| a-brisbane-gold-coast | 32 | 6 | 21 | 12 | 5 | 1 |
| a-northern-rivers-byron | 35 | 8 | 21 | 8 | 6 | 1 |
| a-adelaide-perth | 40 | 13 | 28 | 7 | 6 | 3 |
| a-hobart-canberra-darwin | 44 | 10 | 37 | 11 | 1 | 1 |
| b-australia | 44 | 15 | 27 | 18 | 4 | 1 |
| b-new-zealand | 43 | 18 | 30 | 13 | 4 | 1 |
| b-portugal | 38 | 6 | 20 | 14 | 12 | 0 |
| b-spain | 42 | 10 | 33 | 18 | 1 | 1 |
| b-japan | 33 | 8 | 31 | 15 | 1 | 0 |
| b-us-west-coast | 49 | 7 | 32 | 30 | 8 | 1 |
| b-south-america | 51 | 17 | 27 | 17 | 11 | 1 |
| b-indonesia-bali | 46 | 5 | 20 | 21 | 11 | 0 |
| benchmark (SURPLUS) | 1 | 0 | 1 | 1 | 0 | 0 |
| **Total (deduped)** | **569** | **139** | **367** | **206** | **86** | **13** |

An event found by two regions counts in both rows but once in the total (13 such merges, e.g. Byron Bay Surf Festival, Strawberry Fields, Rainbow Spirit). "18-month window" means a confirmed or expected next edition between 20 Oct 2026 and 20 Apr 2028. Every region is inside the brief's 15 to 40 target or just above it.

Vibe scores are preliminary (discovery evidence only). Seven events score 5: SURPLUS (benchmark), Dark Mofo (Hobart), Zushi Beach Film Festival (Japan), Festival Iminente (Lisbon), Tremor (Azores, 16 to 20 Mar 2027 confirmed), Goiânia Crew Attack (Brazil), FORM Arcosanti (Arizona).

## Coverage

- Categories: subculture festival 111, independent music 97, competition or contest 64, creative market 60, design or art week 45, skate/surf culture weekend 37, club culture 25, streetwear culture 24, makers and vintage 20, expo 19, food and culture night market 13, other 54.
- Subculture tags (top): independent music 161, art and street art 117, electronic 103, makers 82, surf 72, food culture 59, design 57, club culture 51, skateboarding 44, wellness and breathwork 42, zines 37, sneaker and streetwear 34, vintage moto and custom 25, gravel 20, log and single-fin 19, tattoo 18, yoga 16, climbing 15, van life 12.
- Thin strands everywhere: downhill and longboard racing, fixed-gear and alleycat events, van life gatherings, outdoor climbing festivals. Most searches found few or no current events, which may be a real signal (small, IG-only scenes) rather than a search gap.

## Field fill (569 active records)

| Field | Filled | Note |
|---|---|---|
| Website | 218 | Many small events are IG-only |
| Instagram handle | 11 | Phase 2 job; search results rarely show handles |
| Attendance | 71 | Mostly organiser-reported or press |
| Sponsors (at least one) | 158 | Rosters are partial |
| Partnership contact | 21 | Needs site crawls (blocked here) |
| Ticket price | 214 | |
| Demographics | 21 | Needs media kits and IG audience signals |

## Flags for High Ground

- **Name clash:** Leaps and Bounds (Melbourne, July) ran a 2026 program strand called "HIGH GROUND". Check before any approach. Record: `research/a-melbourne/candidates.jsonl`.
- **Health and wellness precedents** (non-endemic brands already partnering): Heaps Normal co-hosting Marrickville Block Weekender (Sydney), Bioglan naming the Bells Beach Longboard Classic, Bepanthen presenting the NZ Tattoo & Art Festival (2024), NRMA Insurance naming Seas The Day to 2028, Aesop backing Adelaide Design Week's prize, Spotify running a program stage at FORM.
- **Category-native events:** The Big Sweat (Leura, sauna, new not-for-profit), Sauna Fest Rotorua (14 to 16 May 2027), JAPAN SAUNA FESTIVAL (openly recruiting sponsors), Seattle Sauna Festival, Othership Runners' Night (Adelaide), AM Social sober morning raves (Brisbane, Gold Coast), Udara Sunday Festival (Bali), Wellness Rave Barcelona (sells a Recovery Stage with naming rights), Byron Wellness Festival, Byron Fest 2027 (Health and Wellbeing pillar, founding partner role open), KUUMA Dark Dip and Nude Solstice Swim (Dark Mofo).
- **Sponsor-closed:** Boom Festival (no logos), Dragon Dreaming (no commercial advertising), Blazing Swan and Kiwiburn (burn principles), Deus-owned events (locked).
- **Unverified sponsor note:** older sources tie Soundrenaline (Indonesia) to a tobacco brand's sponsorship. No 2026 source confirms the current presenter. Verifier to check.

## Method notes (carry into method.md)

- Search only. This environment's network policy blocks direct page fetches (WebFetch and curl), so every fact comes from WebSearch results. Some facts come from search-engine summaries where the exact page had to be inferred; agents flagged these in `sources[].note` and `gaps[]`.
- The first pass ran 14 agents at once and hit the session's shared cap of about 200 searches per turn after 11 to 26 searches each. A top-up pass then ran in three waves of four or five agents, 36 searches each. Total: roughly 730 searches.
- Dedupe: `research/tools/merge.py` merges on id, applies `research/tools/aliases.json`, and prints suspected duplicates. All current suspects were checked by hand and are distinct events (e.g. XChange Markets runs separately in Adelaide and Sydney).

## Phase 2 plan (needs Apify; not connected in this session)

Apify is not connected here: no connector, no `APIFY_TOKEN`, and `api.apify.com` is not on the network allowlist. No Apify credits have been spent. To run Phase 2, start a new session after either connecting Apify at claude.ai/customize/connectors, or adding `APIFY_TOKEN` as an environment secret and allowing `api.apify.com` (and ideally general web access, so the crawler step can also be checked by hand).

Proposed order and rough volume (prices are indicative store figures from search results, not checked against your plan):

| Step | Actor | Volume | Indicative cost |
|---|---|---|---|
| 1. Find handles | Instagram search scraper by event name | ~570 events, plus organiser accounts | low single-digit USD |
| 2. Profiles | apify/instagram-profile-scraper | ~600 to 800 profiles | ~US$1.60 to 2.30 per 1,000 |
| 3. Sponsors from posts | Instagram post or hashtag scraper, last 2 editions | ~100 posts x ~311 filtered events | ~US$1.50 to 2.30 per 1,000 posts |
| 4. Sponsor, about, media kit pages | Website Content Crawler | ~220 sites, ~10 pages each | compute-unit billed |
| 5. Press and attendance | Google Search Results Scraper | ~3 queries x ~311 events | price not confirmed |

To keep spend down, run steps 1 and 2 on all events, and steps 3 to 5 only on events with a preliminary vibe of 3+ and a next edition inside the 18-month window (311 events today). A budget cap of about US$100 should cover this comfortably on the indicative prices, but confirm against your Apify plan first.

## Decisions needed

1. Approve Phase 2 Apify spend, and set a budget cap.
2. Enrichment scope: all 569 events, or the filtered set of 311 (recommended).
