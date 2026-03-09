#!/usr/bin/env python3
"""
Arbitrum Governance Scanner
Fetches latest proposals, discussions, and AI-related opportunities from
the Arbitrum governance forum. Generates daily intelligence digests.
"""

import json
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

FORUM_BASE = "https://forum.arbitrum.foundation"
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)

AI_KEYWORDS = [
    "ai", "agent", "llm", "automat", "bot", "intellig", "machine learn",
    "neural", "model", "copilot", "gpt", "cognitive", "agentic",
]
GRANT_KEYWORDS = [
    "grant", "fund", "budget", "treasury", "allocat", "incentive",
    "trailblazer", "ltipp", "stip", "retro",
]
GOVERNANCE_KEYWORDS = [
    "proposal", "vote", "delegate", "constitutional", "election",
    "council", "governance", "snapshot",
]


def strip_html(text: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_latest_topics(page: int = 0) -> list[dict]:
    """Fetch latest topics from Arbitrum forum."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{FORUM_BASE}/latest.json?page={page}")
        resp.raise_for_status()
        data = resp.json()
        return data.get("topic_list", {}).get("topics", [])


def search_forum(query: str) -> dict:
    """Search Arbitrum forum."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{FORUM_BASE}/search.json", params={"q": query})
        resp.raise_for_status()
        return resp.json()


def fetch_topic_detail(topic_id: int) -> dict:
    """Fetch full topic with posts."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{FORUM_BASE}/t/{topic_id}.json")
        resp.raise_for_status()
        return resp.json()


def categorize_topic(topic: dict) -> list[str]:
    """Categorize a topic by keywords."""
    title = topic.get("title", "").lower()
    tags = []
    if any(k in title for k in AI_KEYWORDS):
        tags.append("AI")
    if any(k in title for k in GRANT_KEYWORDS):
        tags.append("GRANT")
    if any(k in title for k in GOVERNANCE_KEYWORDS):
        tags.append("GOVERNANCE")
    return tags


def analyze_topics(topics: list[dict]) -> dict:
    """Analyze and categorize all topics."""
    categorized = {
        "ai_related": [],
        "grant_related": [],
        "governance": [],
        "high_activity": [],
        "recent": [],
    }

    for t in topics:
        title = t.get("title", "")
        views = t.get("views", 0)
        posts = t.get("posts_count", 0)
        topic_id = t.get("id", 0)
        created = t.get("created_at", "")
        tags = categorize_topic(t)

        entry = {
            "id": topic_id,
            "title": title,
            "views": views,
            "posts_count": posts,
            "created_at": created[:10] if created else "",
            "tags": tags,
            "url": f"{FORUM_BASE}/t/{topic_id}",
            "activity_score": views * 0.3 + posts * 10,
        }

        if "AI" in tags:
            categorized["ai_related"].append(entry)
        if "GRANT" in tags:
            categorized["grant_related"].append(entry)
        if "GOVERNANCE" in tags:
            categorized["governance"].append(entry)
        if posts >= 10 or views >= 500:
            categorized["high_activity"].append(entry)

    # Sort by activity score
    for key in categorized:
        categorized[key].sort(key=lambda x: x["activity_score"], reverse=True)

    return categorized


def generate_ai_opportunity_search() -> list[dict]:
    """Search for AI-specific opportunities."""
    queries = [
        "AI agent grant",
        "Trailblazer AI",
        "agentic governance",
        "AI tooling bounty",
        "treasury automation",
    ]
    results = []
    for q in queries:
        try:
            data = search_forum(q)
            for topic in data.get("topics", []):
                results.append({
                    "query": q,
                    "title": topic.get("title", ""),
                    "id": topic.get("id", 0),
                    "url": f"{FORUM_BASE}/t/{topic.get('id', 0)}",
                })
            for post in data.get("posts", []):
                blurb = post.get("blurb", "")[:300]
                results.append({
                    "query": q,
                    "topic_id": post.get("topic_id", 0),
                    "blurb": blurb,
                })
        except Exception as e:
            print(f"  Warning: search for '{q}' failed: {e}", file=sys.stderr)
    return results


def generate_digest(categorized: dict, ai_search: list[dict]) -> str:
    """Generate a markdown intelligence digest."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Arbitrum Governance Intelligence Digest",
        f"**Generated**: {now}",
        "",
        "---",
        "",
        "## 🤖 AI-Related Discussions",
        "",
    ]

    if categorized["ai_related"]:
        lines.append("| Topic | Views | Posts | Tags | Link |")
        lines.append("|-------|-------|-------|------|------|")
        for t in categorized["ai_related"]:
            tags = ", ".join(t["tags"])
            lines.append(f"| {t['title'][:60]} | {t['views']} | {t['posts_count']} | {tags} | [→]({t['url']}) |")
    else:
        lines.append("No AI-related topics found in latest page.")

    lines.extend([
        "",
        "## 💰 Grant & Funding Discussions",
        "",
    ])

    if categorized["grant_related"]:
        lines.append("| Topic | Views | Posts | Link |")
        lines.append("|-------|-------|-------|------|")
        for t in categorized["grant_related"]:
            lines.append(f"| {t['title'][:60]} | {t['views']} | {t['posts_count']} | [→]({t['url']}) |")

    lines.extend([
        "",
        "## 🔥 High-Activity Topics",
        "",
        "| Topic | Views | Posts | Tags | Link |",
        "|-------|-------|-------|------|------|",
    ])
    for t in categorized["high_activity"][:15]:
        tags = ", ".join(t["tags"]) if t["tags"] else "—"
        lines.append(f"| {t['title'][:60]} | {t['views']} | {t['posts_count']} | {tags} | [→]({t['url']}) |")

    lines.extend([
        "",
        "## 🔍 AI Opportunity Search Results",
        "",
    ])
    seen_titles = set()
    for r in ai_search:
        if "title" in r and r["title"] not in seen_titles:
            seen_titles.add(r["title"])
            lines.append(f"- **{r['title']}** ([link]({r['url']})) — query: `{r['query']}`")
        elif "blurb" in r:
            lines.append(f"- _Topic {r['topic_id']}_: {r['blurb'][:150]}...")

    lines.extend([
        "",
        "---",
        "",
        "## Action Items",
        "",
        "1. [ ] Review AI-related topics for contribution opportunities",
        "2. [ ] Check grant discussions for application deadlines",
        "3. [ ] Monitor high-activity proposals for voting intelligence",
        "4. [ ] Search for Trailblazer AI Grant application portal",
        "",
    ])

    return "\n".join(lines)


def main():
    print("🔍 Scanning Arbitrum governance forum...")

    print("  Fetching latest topics...")
    topics = fetch_latest_topics(0)
    # Get page 2 for more coverage
    topics.extend(fetch_latest_topics(1))
    print(f"  Found {len(topics)} topics")

    print("  Categorizing topics...")
    categorized = analyze_topics(topics)
    print(f"  AI-related: {len(categorized['ai_related'])}")
    print(f"  Grant-related: {len(categorized['grant_related'])}")
    print(f"  High-activity: {len(categorized['high_activity'])}")

    print("  Searching for AI opportunities...")
    ai_search = generate_ai_opportunity_search()
    print(f"  Found {len(ai_search)} search results")

    # Generate digest
    digest = generate_digest(categorized, ai_search)
    digest_file = REPORT_DIR / f"arbitrum_digest_{datetime.now().strftime('%Y%m%d')}.md"
    with open(digest_file, "w") as f:
        f.write(digest)
    print(f"\n✅ Digest saved to {digest_file}")

    # Save raw data
    raw_file = DATA_DIR / "arbitrum_governance_scan.json"
    with open(raw_file, "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "topics_scanned": len(topics),
            "categorized": {k: v[:20] for k, v in categorized.items()},
            "ai_search_results": ai_search[:30],
        }, f, indent=2)
    print(f"✅ Raw data saved to {raw_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("📊 SCAN SUMMARY")
    print("=" * 60)
    for t in categorized["ai_related"][:5]:
        print(f"  🤖 [{t['views']} views] {t['title'][:65]}")
    for t in categorized["grant_related"][:5]:
        print(f"  💰 [{t['views']} views] {t['title'][:65]}")


if __name__ == "__main__":
    main()
