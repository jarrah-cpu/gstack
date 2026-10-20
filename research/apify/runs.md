# Apify run ledger

Phase 2 enrichment. Approved 20 Oct 2026: the 311 filtered events in `research/apify/targets.jsonl` only, hard cap US$100 total. Account: Scale plan (Silver store tier).

Every run is listed here with its run ID, dataset ID, input file, raw output file and charged cost. Raw outputs are downloaded from the run's dataset with `curl "https://api.apify.com/v2/datasets/<dataset>/items?format=jsonl&clean=true"` and kept unedited under `research/apify/raw/`. The run's own INPUT record is saved next to each prepared input as `*.actual-input.json`.

Cost is the run's charged `usageTotalUsd` for pay-per-event actors. The Website Content Crawler bills platform usage, which the tokenless run record does not show, so its cost is estimated from compute units at the Scale plan's US$0.16 per CU and marked (est.). Datacenter proxy use is included in the plan.

Privacy and size: post files keep only the fields used for sponsor and engagement analysis (`fields_kept` in `runs.jsonl`); comment text and commenters' usernames are dropped, and tagged accounts keep only username, display name and verified flag. Profile and search files drop related-profile lists and first-comment text. Crawled pages keep url, status, title, description, language and markdown only, with token-shaped strings (map tokens, API keys) that third-party sites embed redacted. The full datasets stay on Apify under the listed dataset IDs for the account's retention period.

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
| 12 | 2026-10-20 | ig-search | apify/instagram-search-scraper | `research/apify/inputs/04-ig-search.json` | 165 | 0.3135 | 1.9404 | h76E34mX1C7KjBA1N | CAl0J2ePzOoUMUsRj | `research/apify/raw/ig-search/12-weak-58-h76E34mX1C7KjBA1N.jsonl` |
| 13 | 2026-10-20 | google | apify/google-search-scraper | `research/apify/inputs/press-au.json` | 426 | 0.8288 | 2.7692 | II34ZdzZYT0na7aeY | xJ0ckGzg23C6hM6oY | `research/apify/raw/google/13-press-au-II34ZdzZYT0na7aeY.jsonl` |
| 14 | 2026-10-20 | ig-profile | apify/instagram-profile-scraper | `research/apify/inputs/06-ig-profiles.json` | 366 | 0.7320 | 3.5012 | MusXfYtVEUdwmfDjB | wJW1jPS0rli4sX8VP | `research/apify/raw/ig-profile/14-candidates-366-MusXfYtVEUdwmfDjB.jsonl` |
| 15 | 2026-10-21 | ig-posts | apify/instagram-post-scraper | `research/apify/inputs/08-ig-posts-pilot-basic.json` | 5 | 0.0065 | 3.5077 | aYXJoEgMzf6If7Psp | bhmjpmsiGlUx6txQW | `research/apify/raw/ig-posts/15-pilot-basic-aYXJoEgMzf6If7Psp.jsonl` |
| 16 | 2026-10-21 | ig-posts | apify/instagram-post-scraper | `research/apify/inputs/09-ig-posts-pilot-detailed.json` | 5 | 0.0100 | 3.5177 | S4tlHXXgcGcskIhBh | j6Bu0OdBsY57KxaxQ | `research/apify/raw/ig-posts/16-pilot-detailed-S4tlHXXgcGcskIhBh.jsonl` |
| 17 | 2026-10-21 | crawl | apify/website-content-crawler | `research/apify/derived/crawl_urls.txt` | 721 | 1.2799 (est.) | 4.7976 | Gp1z9LCzYmd8zrA5r | 8aVQ1KyFj1wonojnO | `research/apify/raw/crawl/17-sites-151-Gp1z9LCzYmd8zrA5r.jsonl` |
| 18 | 2026-10-21 | google | apify/google-search-scraper | `research/apify/inputs/07-google-ig-site.json` | 43 | 0.0839 | 4.8815 | Y1GzjPwwGguDgw4qA | 4SbKbBvjWaFH8VTIK | `research/apify/raw/google/18-ig-site-Y1GzjPwwGguDgw4qA.jsonl` |
| 19 | 2026-10-21 | ig-profile | apify/instagram-profile-scraper | `research/apify/inputs/10-ig-profiles-followup.json` | 13 | 0.0260 | 4.9075 | VZnMfg5kASKX7NEJY | vH8GZ2bXozJhWWhyM | `research/apify/raw/ig-profile/19-followup-13-VZnMfg5kASKX7NEJY.jsonl` |
