#!/usr/bin/env python3
"""Aggregate sponsor and partner signals from each account's Instagram posts.

For every scraped account: which other accounts appear as collab co-authors,
photo tags, caption mentions, and mentions close to partner words
("presented by", "partner", "sponsor", "patrocinio", "協賛" ...), plus
paid-partnership posts. Each signal keeps up to three example post URLs.

Writes research/apify/derived/post_signals.json keyed by account.

Usage: python3 research/tools/phase2_post_signals.py
"""
import glob
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "research" / "apify"
PARTNER_WORDS = re.compile(
    r"present(ed|s)? by|partner|sponsor|supported by|support of|thanks? to|thank you to|in collaboration|collab|"
    r"powered by|brought to you|proudly|naming rights|official (drink|beer|water|partner)|"
    r"patrocin|colabora|apoio|apoyo|parceri|parceiro|con el apoyo|gracias a|obrigad|"
    r"協賛|スポンサー|協力|提供|特別協賛|didukung|dipersembahkan|bekerja sama|"
    r"in partnership|together with|x @|×", re.I)
MENTION = re.compile(r"@([A-Za-z0-9._]{2,30})")

# Collab posts sit on the event's grid but may be owned by the collaborator, so a post
# belongs to every scraped account that is its owner or one of its co-authors.
scraped = set(json.loads((A / "derived" / "post_accounts.json").read_text())["accounts"])
posts_by_owner = defaultdict(list)
for f in sorted(glob.glob(str(A / "raw" / "ig-posts" / "*.jsonl"))):
    if "pilot" in f:
        continue
    for l in Path(f).read_text().split("\n"):
        if l.strip():
            p = json.loads(l)
            people = {(p.get("ownerUsername") or "").lower()} | {(u.get("username") or "").lower() for u in p.get("coauthorProducers") or []}
            for acc in people & scraped:
                posts_by_owner[acc].append(p)

out = {}
for owner, posts in posts_by_owner.items():
    seen_ids, uniq = set(), []
    for p in posts:
        if p.get("id") not in seen_ids:
            seen_ids.add(p.get("id"))
            uniq.append(p)
    sig = defaultdict(lambda: {"coauthor": 0, "tagged": 0, "mention": 0, "partner_context": 0, "paid": 0,
                               "examples": [], "snippets": []})
    paid_posts = []
    for p in uniq:
        url, ts, cap = p.get("url"), (p.get("timestamp") or "")[:10], p.get("caption") or ""
        hits = defaultdict(set)
        for u in p.get("coauthorProducers") or []:
            hits[(u.get("username") or "").lower()].add("coauthor")
        tagged = list(p.get("taggedUsers") or []) + [u for c in (p.get("childPosts") or []) for u in (c.get("taggedUsers") or [])]
        for u in tagged:
            hits[(u.get("username") or "").lower()].add("tagged")
        for m in set(x.lower().rstrip(".") for x in (p.get("mentions") or []) + MENTION.findall(cap)):
            hits[m].add("mention")
        for line in re.split(r"[\n。]|(?<=[.!?])\s", cap):
            if PARTNER_WORDS.search(line):
                for m in MENTION.findall(line):
                    hits[m.lower().rstrip(".")].add("partner_context")
                    s = sig[m.lower().rstrip(".")]
                    if len(s["snippets"]) < 2:
                        s["snippets"].append(f"{ts}: {line.strip()[:220]}")
        if p.get("paidPartnership"):
            paid_posts.append({"url": url, "date": ts, "caption": cap[:200]})
            for h in hits:
                hits[h].add("paid")
        for h, kinds in hits.items():
            if not h or h == owner:
                continue
            s = sig[h]
            for k in kinds:
                s[k] += 1
            if len(s["examples"]) < 3:
                s["examples"].append(f"{url} ({ts})")
    def weight(s):
        return s["coauthor"] * 3 + s["paid"] * 3 + s["partner_context"] * 2 + s["tagged"] + s["mention"] * 0.5
    ranked = sorted(((h, s) for h, s in sig.items()), key=lambda x: -weight(x[1]))
    dates = sorted((p.get("timestamp") or "")[:10] for p in uniq if p.get("timestamp"))
    out[owner] = {"posts": len(uniq), "first": dates[0] if dates else None, "last": dates[-1] if dates else None,
                  "paid_partnership_posts": paid_posts[:10],
                  "accounts": [{"handle": h, "weight": round(weight(s), 1), **s} for h, s in ranked[:40] if weight(s) >= 1.5]}
(A / "derived" / "post_signals.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(f"{len(out)} accounts, {sum(v['posts'] for v in out.values())} posts")
