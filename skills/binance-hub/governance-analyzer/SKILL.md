---
title: DAO Governance Analyzer
description: Monitor, search, and summarize governance activity across major DAOs (Arbitrum, Optimism, Uniswap, Aave). Provides proposal summaries, sentiment analysis, and vote tracking.
metadata:
  version: 1.0.0
  author: cryptoai-explorer
license: MIT
---

# DAO Governance Analyzer

Monitor governance activity across major DAOs. Fetch latest proposals, search for specific topics, and generate structured summaries.

## When to Use

- Monitoring DAO governance activity before voting
- Researching proposals across multiple DAOs
- Finding AI/agent-related governance discussions
- Tracking grant programs and funding opportunities
- Building governance intelligence dashboards

## How to Use

### Fetch Latest Topics

```python
import httpx

FORUMS = {
    "arbitrum": "https://forum.arbitrum.foundation",
    "optimism": "https://gov.optimism.io",
}

async def get_latest_topics(dao="arbitrum", limit=20):
    base = FORUMS[dao]
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{base}/latest.json")
        topics = resp.json()["topic_list"]["topics"][:limit]

    for t in topics:
        views = t.get("views", 0)
        posts = t.get("posts_count", 0)
        title = t.get("title", "")
        print(f"[{views:>5} views | {posts:>3} posts] {title[:70]}")
```

### Search Governance Forums

```python
async def search_governance(dao="arbitrum", query="AI agent grant"):
    base = FORUMS[dao]
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{base}/search.json", params={"q": query})
        data = resp.json()

    for topic in data.get("topics", []):
        print(f"Topic: {topic['title']}")
    for post in data.get("posts", []):
        print(f"Blurb: {post['blurb'][:150]}")
```

### Get Full Proposal Content

```python
async def get_proposal(dao="arbitrum", topic_id=29244):
    base = FORUMS[dao]
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{base}/t/{topic_id}.json")
        data = resp.json()

    posts = data.get("post_stream", {}).get("posts", [])
    if posts:
        import re
        content = re.sub(r"<[^>]+>", " ", posts[0].get("cooked", ""))
        content = re.sub(r"\s+", " ", content).strip()
        print(f"Title: {data['title']}")
        print(f"Views: {data['views']} | Posts: {data['posts_count']}")
        print(f"Content: {content[:1000]}")
```

## Supported DAOs

| DAO | Forum URL | API Format |
|-----|-----------|------------|
| Arbitrum | forum.arbitrum.foundation | Discourse JSON |
| Optimism | gov.optimism.io | Discourse JSON |

## API Patterns

All use Discourse JSON API (no auth required):

- Latest: `{base}/latest.json`
- Search: `{base}/search.json?q={query}`
- Topic detail: `{base}/t/{topic_id}.json`
- Category: `{base}/c/{category_slug}.json`

## Key Governance Keywords

- AI/Agent: `ai`, `agent`, `agentic`, `llm`, `automation`
- Grants: `grant`, `fund`, `budget`, `trailblazer`, `ltipp`, `retro`
- Governance: `proposal`, `vote`, `delegate`, `constitutional`, `election`
