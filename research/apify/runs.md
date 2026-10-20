# Apify run ledger

Phase 2 enrichment. Approved 20 Oct 2026: the 311 filtered events in `research/apify/targets.jsonl` only, hard cap US$100 total. Account: Scale plan (Silver store tier).

Every run is listed here with its run ID, dataset ID, input file, raw output file and charged cost. Raw outputs are downloaded from the run's dataset with `curl "https://api.apify.com/v2/datasets/<dataset>/items?format=jsonl&clean=true"` and kept unedited under `research/apify/raw/`. The run's own INPUT record is saved next to each prepared input as `*.actual-input.json`.

Cost is the run's charged `usageTotalUsd` for pay-per-event actors. The Website Content Crawler bills platform usage, which the tokenless run record does not show, so its cost is estimated from compute units at the Scale plan's US$0.16 per CU and marked (est.). Datacenter proxy use is included in the plan.

| # | Date | Step | Actor | Input | Items | Cost (USD) | Running total | Run ID | Dataset ID | Raw file |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-20 | google | apify/google-search-scraper | `research/apify/inputs/01-google-pilot.json` | 3 | 0.0059 | 0.0059 | xv5NE0fik3COY72nR | QzjRTqgcZxMsVynvr | `research/apify/raw/google/01-pilot-xv5NE0fik3COY72nR.jsonl` |
| 2 | 2026-10-20 | google | apify/google-search-scraper | `research/apify/inputs/02-google-handles.json` | 312 | 0.6084 | 0.6143 | CPhSEwbS8iPIpIYm3 | BVjk620lqGQq8Aeti | `research/apify/raw/google/02-handles-CPhSEwbS8iPIpIYm3.jsonl` |
| 3 | 2026-10-20 | google | apify/google-search-scraper | `research/apify/inputs/press-nz.json` | 75 | 0.1463 | 0.7606 | EgQy2XcfBQjL8fAtd | oFCqQZ9FBUFad7w6J | `research/apify/raw/google/03-press-nz-EgQy2XcfBQjL8fAtd.jsonl` |
| 4 | 2026-10-20 | google | apify/google-search-scraper | `research/apify/inputs/press-es.json` | 93 | 0.1814 | 0.9420 | mbYaZXSuTP6n9uJSh | UWyj51EC4BWq4VzeL | `research/apify/raw/google/04-press-es-mbYaZXSuTP6n9uJSh.jsonl` |
| 5 | 2026-10-20 | google | apify/google-search-scraper | `research/apify/inputs/press-pt-br.json` | 66 | 0.1287 | 1.0707 | aamGFbKu0fvwmodH3 | gVafa1g2zckts4qyR | `research/apify/raw/google/05-press-pt-br-aamGFbKu0fvwmodH3.jsonl` |
| 6 | 2026-10-20 | google | apify/google-search-scraper | `research/apify/inputs/press-jp.json` | 84 | 0.1638 | 1.2345 | n9q7sRBWJslzoM28e | F77UyIbeX2WffanmL | `research/apify/raw/google/06-press-jp-n9q7sRBWJslzoM28e.jsonl` |
| 7 | 2026-10-20 | google | apify/google-search-scraper | `research/apify/inputs/press-id.json` | 54 | 0.1053 | 1.3398 | TTZBvnUMx9qnQNm7w | gEGlpAxuAV3MfRVt6 | `research/apify/raw/google/07-press-id-TTZBvnUMx9qnQNm7w.jsonl` |
| 8 | 2026-10-20 | google | apify/google-search-scraper | `research/apify/inputs/press-ar-cl-pe.json` | 48 | 0.0936 | 1.4334 | zhq0xVKi5poWWGYyT | jhunYXghE20PUicpk | `research/apify/raw/google/08-press-ar-cl-pe-zhq0xVKi5poWWGYyT.jsonl` |
| 9 | 2026-10-20 | ig-search | apify/instagram-search-scraper | `research/apify/inputs/03-ig-search-pilot.json` | 1 | 0.0019 | 1.4353 | 1CgNdk938Kic0LvZU | mPqN4iLaIugoBJWQF | `research/apify/raw/ig-search/09-pilot-1CgNdk938Kic0LvZU.jsonl` |
| 10 | 2026-10-20 | google | apify/google-search-scraper | `research/apify/inputs/press-us.json` | 85 | 0.1697 | 1.6050 | g6mAUqgnm4GhMh0Cd | gD0R7EgiHVhfpUmuG | `research/apify/raw/google/10-press-us-g6mAUqgnm4GhMh0Cd.jsonl` |
| 11 | 2026-10-20 | crawl | apify/website-content-crawler | `research/apify/inputs/05-crawl-pilot.json` | 15 | 0.0219 (est.) | 1.6269 | JfCFjgXYiDxCkPVKG | NKZe6jRMI9AYk3keT | `research/apify/raw/crawl/11-pilot-JfCFjgXYiDxCkPVKG.jsonl` |
