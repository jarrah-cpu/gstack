#!/usr/bin/env python3
"""Build one evidence pack per target event for the Phase 2 extraction agents:
research/apify/evidence/<region>/<id>.md

Each pack holds the event's current record (key fields and gaps), its resolved
Instagram accounts with stats, sponsor signals from its posts, keyword-filtered
lines from its crawled web pages, and its Google results. Every item carries
the URL it came from so agents can cite it.

Usage: python3 research/tools/phase2_evidence.py
"""
import glob
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "research" / "apify"
EV = A / "evidence"


def jl(path):
    return [json.loads(l) for l in Path(path).read_text().split("\n") if l.strip()]


def dom(u):
    return urlparse(u or "").netloc.lower().removeprefix("www.")


events = {e["id"]: e for e in jl(ROOT / "data" / "events.jsonl")}
targets = {t["id"]: t for t in jl(A / "targets.jsonl")}
resolved = {r["id"]: r for r in jl(A / "derived" / "handles_resolved.jsonl")}
new_sites = json.loads((A / "derived" / "new_websites.json").read_text())
signals = json.loads((A / "derived" / "post_signals.json").read_text())
tag_profiles = {}
for f in glob.glob(str(A / "raw" / "ig-profile" / "*.jsonl")) + glob.glob(str(A / "raw" / "ig-search" / "*.jsonl")):
    for p in jl(f):
        if p.get("username"):
            tag_profiles[p["username"].lower()] = (p, f)

# crawl pages: exact URL lists per event, then domain fallback for depth-1 pages
url_owner = defaultdict(set)
for f in ("crawl_urls.jsonl", "crawl_urls_new.jsonl"):
    if (A / "derived" / f).exists():
        for r in jl(A / "derived" / f):
            for u in r["urls"]:
                url_owner[u.rstrip("/")].add(r["id"])
dom_owner = defaultdict(set)
for tid, t in targets.items():
    for u in [t["website"], new_sites.get(tid, {}).get("url")]:
        if u:
            dom_owner[dom(u)].add(tid)
pages = defaultdict(list)
for f in sorted(glob.glob(str(A / "raw" / "crawl" / "*.jsonl"))):
    for it in jl(f):
        u = (it.get("url") or "").rstrip("/")
        owners = url_owner.get(u) or url_owner.get((it.get("loadedUrl") or "").rstrip("/")) or (
            dom_owner.get(dom(u)) if it.get("depth") else None) or set()
        for tid in owners:
            pages[tid].append(it)

KW = re.compile(r"partner|sponsor|present|support|thank|proud|collaborat|fund|naming|official|media kit|mediakit|"
                r"advertis|enquir|inquir|contact|e-?mail|@|attend|visitor|crowd|audience|demograph|\baged?\b|years old|"
                r"capacity|sold out|ticket|\$|€|£|¥|activation|pop-?up|lounge|stall|workshop|sampling|installation|"
                r"patrocin|colabora|apoio|apoyo|parceir|asistentes|visitantes|público|publico|personas|pessoas|"
                r"来場|協賛|スポンサー|協力|特別|pengunjung|didukung|mitra|\b\d{1,3}[,.]?\d{3}\b", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
IMG = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)")


def page_lines(it, budget):
    md = it.get("markdown") or ""
    url = it.get("loadedUrl") or it.get("url")
    partnerish = re.search(r"partner|sponsor|patrocin|parceir|colabora|kyosan|supporter", url or "", re.I)
    out, seen = [], set()
    for line in md.split("\n"):
        s = line.strip()
        if not s or s in seen:
            continue
        if partnerish and s.startswith(("![", "[![")):
            for alt, src in IMG.findall(s):
                label = alt.strip() or src.rsplit("/", 1)[-1][:60]
                if label not in seen:
                    seen.add(label)
                    out.append(f"logo: {label}")
            continue
        if KW.search(s) and len(s) < 600 and not s.startswith(("![", "[![", "*   [", "* [")):
            seen.add(s)
            out.append(s[:400])
    emails = sorted(set(e for e in EMAIL.findall(md) if not e.lower().endswith((".png", ".jpg", ".webp", ".svg"))))
    text = "\n".join(out)
    return url, it.get("title"), emails, text[:budget]


press = json.loads((A / "inputs" / "press.map.json").read_text())
serps = defaultdict(list)
for f in sorted(glob.glob(str(A / "raw" / "google" / "*press*.jsonl"))):
    for it in jl(f):
        m = press.get(it["searchQuery"]["term"])
        if m:
            serps[m["id"]].append((m["kind"], it))


def record_summary(e):
    keys = ["website", "dates", "organiser", "attendance", "audience", "sponsors", "activation_formats",
            "partnership_contact", "ticket_price", "status"]
    return json.dumps({k: e.get(k) for k in keys}, ensure_ascii=False)


EV.mkdir(exist_ok=True)
for tid, t in targets.items():
    e = events[tid]
    r = resolved[tid]
    L = [f"# {e['name']} ({tid})", f"City: {e['location']['city']}, {e['location']['country']}. Region: {e['region']}. "
         f"Category: {e['category']}. Preliminary vibe: {e['vibe']['score']}.", "",
         "## Current record (key fields)", record_summary(e), "", "Gaps: " + " | ".join(e.get("gaps") or []), ""]
    if tid in new_sites:
        L += [f"Proposed website (not yet on record): {new_sites[tid]['url']} (source: {new_sites[tid]['source']})", ""]
    L.append("## Instagram (Apify profile data; already written to the record by script, do not edit)")
    for label, h in (("event", r["handle"]), ("organiser", r["organiser_handle"])):
        if h and h in tag_profiles:
            p, f = tag_profiles[h]
            L.append(f"- {label}: @{h} https://www.instagram.com/{h}/ | {p.get('fullName')} | followers {p.get('followersCount')} | "
                     f"posts {p.get('postsCount')} | link {p.get('externalUrl')} | bio: {(p.get('biography') or '')[:200]!r}")
    if r.get("override_note"):
        L.append(f"- note: {r['override_note']}")
    L.append("")
    acc = r["handle"] or r["organiser_handle"]
    sg = signals.get(acc or "")
    L.append("## Sponsor signals from Instagram posts since 1 Oct 2025 (account " + (f"@{acc}" if acc else "none") + ")")
    if sg:
        L.append(f"{sg['posts']} posts from {sg['first']} to {sg['last']}. Paid-partnership posts: {len(sg['paid_partnership_posts'])}.")
        for pp in sg["paid_partnership_posts"][:5]:
            L.append(f"- paid partnership post {pp['url']} ({pp['date']}): {pp['caption'][:150]!r}")
        L.append("Accounts (co = collab co-author, tag = tagged in photo, men = caption mention, ctx = mentioned next to partner words, paid = in paid-partnership post). Category and followers from Apify profile data where scraped:")
        n = 0
        for a in sg["accounts"]:
            if n >= 25:
                break
            p = tag_profiles.get(a["handle"], (None, None))[0]
            cat = f" | {p.get('businessCategoryName') or 'no category'} | {p.get('fullName')} | {p.get('followersCount')} followers" if p else ""
            L.append(f"- @{a['handle']}: co {a['coauthor']}, tag {a['tagged']}, men {a['mention']}, ctx {a['partner_context']}, paid {a['paid']}{cat}"
                     f" | e.g. {a['examples'][0] if a['examples'] else ''}")
            for s in a["snippets"][:1]:
                L.append(f"    context: {s!r}")
            n += 1
    else:
        L.append("No posts scraped for this event.")
    L.append("")
    L.append("## Website pages (Apify Website Content Crawler, keyword-filtered lines)")
    budget = 6000
    for it in pages.get(tid, [])[:14]:
        if budget <= 0:
            break
        url, title, emails, text = page_lines(it, min(1500, budget))
        if not text and not emails:
            continue
        L.append(f"### {url} ({title})")
        if emails:
            L.append("emails on page: " + ", ".join(emails[:6]))
        L.append(text)
        budget -= len(text) + 100
    if not pages.get(tid):
        L.append("No pages crawled.")
    L.append("")
    L.append("## Google results (Apify Google Search Results Scraper)")
    for kind, it in serps.get(tid, []):
        L.append(f"### {kind}: {it['searchQuery']['term']}")
        for o in (it.get("organicResults") or [])[:8]:
            L.append(f"- {o.get('title','')[:100]} | {o.get('url')} | {(o.get('description') or '')[:260]}")
    region = e["region"].split("+")[0]
    (EV / region).mkdir(parents=True, exist_ok=True)
    (EV / region / f"{tid}.md").write_text("\n".join(L) + "\n")
print(f"{len(targets)} packs written to {EV.relative_to(ROOT)}")
