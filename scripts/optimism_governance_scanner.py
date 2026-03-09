#!/usr/bin/env python3
"""
Optimism Governance Scanner
Monitors gov.optimism.io for AI opportunities, grants, and governance activity.
Generates daily digest with categorized topics.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx

FORUM_BASE = "https://gov.optimism.io"
DATA_DIR = Path(__file__).parent.parent / "data"
REPORT_DIR = Path(__file__).parent.parent / "reports"
DATA_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

AI_KEYWORDS = ["ai", "agent", "llm", "automat", "bot", "intellig", "agentic", "cognitive", "model"]
GRANT_KEYWORDS = ["grant", "fund", "budget", "treasury", "retropgf", "rpgf", "season", "round"]
GOVERNANCE_KEYWORDS = ["proposal", "vote", "delegate", "council", "election", "constitution"]


def categorize_topic(title: str) -> list[str]:
    """Categorize a topic by keywords."""
    t = title.lower()
    cats = []
    if any(k in t for k in AI_KEYWORDS):
        cats.append("ai_related")
    if any(k in t for k in GRANT_KEYWORDS):
        cats.append("grant_related")
    if any(k in t for k in GOVERNANCE_KEYWORDS):
        cats.append("governance")
    return cats or ["general"]


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def main():
    now = datetime.now(timezone.utc)
    print(f"🔴 Optimism Governance Scanner — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    with httpx.Client(timeout=30, follow_redirects=True) as client:
        # Fetch latest topics
        print("\n📋 Fetching latest topics...")
        resp = client.get(f"{FORUM_BASE}/latest.json")
        resp.raise_for_status()
        data = resp.json()

    topics = data.get("topic_list", {}).get("topics", [])
    print(f"   Found {len(topics)} topics")

    # Categorize all topics
    categorized = {"ai_related": [], "grant_related": [], "governance": [], "general": [], "hot": []}

    for t in topics:
        title = t.get("title", "")
        views = t.get("views", 0)
        posts = t.get("posts_count", 0)
        tid = t.get("id", 0)
        created = t.get("created_at", "")[:10]

        entry = {
            "title": title,
            "id": tid,
            "views": views,
            "posts_count": posts,
            "created_at": created,
            "url": f"{FORUM_BASE}/t/{tid}",
        }

        cats = categorize_topic(title)
        for cat in cats:
            categorized[cat].append(entry)

        if views >= 500 or posts >= 15:
            categorized["hot"].append(entry)

    # Search for specific topics (limited to avoid rate limiting)
    search_queries = ["retropgf", "AI agent", "grants council"]
    search_results = {}

    with httpx.Client(timeout=30, follow_redirects=True) as client:
        for query in search_queries:
            print(f"   🔍 Searching: '{query}'...")
            try:
                resp = client.get(f"{FORUM_BASE}/search.json", params={"q": query})
                if resp.status_code == 200:
                    sdata = resp.json()
                    search_results[query] = {
                        "topics": len(sdata.get("topics", [])),
                        "posts": len(sdata.get("posts", [])),
                        "top_results": [
                            {
                                "title": t.get("title", ""),
                                "id": t.get("id", 0),
                                "url": f"{FORUM_BASE}/t/{t.get('id', 0)}",
                            }
                            for t in sdata.get("topics", [])[:5]
                        ],
                    }
                elif resp.status_code == 429:
                    print(f"   ⚠️ Rate limited on '{query}'")
                    search_results[query] = {"error": "rate_limited"}
            except Exception as e:
                print(f"   ❌ Error: {e}")
                search_results[query] = {"error": str(e)}

    # Save data
    scan_data = {
        "timestamp": now.isoformat(),
        "dao": "optimism",
        "total_topics": len(topics),
        "categorized": {
            k: sorted(v, key=lambda x: x["views"], reverse=True) for k, v in categorized.items()
        },
        "search_results": search_results,
    }

    data_file = DATA_DIR / "optimism_governance_scan.json"
    with open(data_file, "w") as f:
        json.dump(scan_data, f, indent=2)
    print(f"\n💾 Data saved to {data_file}")

    # Generate report
    lines = [
        f"# Optimism Governance Digest — {now.strftime('%Y-%m-%d')}",
        "",
        f"**Scanned**: {len(topics)} topics from gov.optimism.io",
        f"**Generated**: {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "---",
        "",
    ]

    if categorized["ai_related"]:
        lines.append("## 🤖 AI-Related Topics")
        lines.append("")
        for t in categorized["ai_related"][:8]:
            lines.append(f"- [{t['views']} views | {t['posts_count']} posts] **{t['title']}**")
            lines.append(f"  → {t['url']}")
        lines.append("")

    if categorized["grant_related"]:
        lines.append("## 💰 Grants & Funding")
        lines.append("")
        for t in categorized["grant_related"][:8]:
            lines.append(f"- [{t['views']} views | {t['posts_count']} posts] **{t['title']}**")
            lines.append(f"  → {t['url']}")
        lines.append("")

    if categorized["governance"]:
        lines.append("## 🏛️ Governance Activity")
        lines.append("")
        for t in categorized["governance"][:8]:
            lines.append(f"- [{t['views']} views | {t['posts_count']} posts] **{t['title']}**")
            lines.append(f"  → {t['url']}")
        lines.append("")

    if categorized["hot"]:
        lines.append("## 🔥 Hot Topics")
        lines.append("")
        for t in categorized["hot"][:10]:
            lines.append(f"- [{t['views']} views | {t['posts_count']} posts] **{t['title']}**")
        lines.append("")

    if search_results:
        lines.append("## 🔍 Search Results")
        lines.append("")
        for query, result in search_results.items():
            if "error" in result:
                lines.append(f"- **{query}**: ⚠️ {result['error']}")
            else:
                lines.append(f"- **{query}**: {result['topics']} topics, {result['posts']} posts")
                for sr in result.get("top_results", [])[:3]:
                    lines.append(f"  - {sr['title']}")
        lines.append("")

    report = "\n".join(lines)
    report_file = REPORT_DIR / f"optimism_digest_{now.strftime('%Y%m%d')}.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"📄 Report saved to {report_file}")

    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"  AI-related topics: {len(categorized['ai_related'])}")
    print(f"  Grant-related topics: {len(categorized['grant_related'])}")
    print(f"  Governance topics: {len(categorized['governance'])}")
    print(f"  Hot topics (>500 views or >15 posts): {len(categorized['hot'])}")


if __name__ == "__main__":
    main()
