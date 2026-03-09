---
title: Crypto Bounty Scanner
description: Monitor and discover bounties across Superteam Earn, with special focus on AGENT_ALLOWED bounties that AI agents can complete. Filters by reward, deadline, competition level, and agent access.
metadata:
  version: 1.0.0
  author: cryptoai-explorer
license: MIT
---

# Crypto Bounty Scanner

Discover bounties on Superteam Earn. Identifies AGENT_ALLOWED bounties that AI agents can legitimately complete. Filters by reward amount, deadline proximity, and competition level.

## When to Use

- Finding paid work AI agents can do in crypto
- Monitoring new bounty opportunities
- Filtering for low-competition high-reward bounties
- Tracking AI/agent related bounties

## How to Use

```python
import httpx

async def scan_bounties(agent_only=False, min_reward=100):
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            "https://earn.superteam.fun/api/listings",
            params={"take": 100, "type": "bounty"}
        )
        bounties = resp.json()

    open_bounties = [b for b in bounties if b.get("status") == "OPEN"]

    if agent_only:
        open_bounties = [b for b in open_bounties if b.get("agentAccess") == "AGENT_ALLOWED"]

    open_bounties = [b for b in open_bounties if (b.get("rewardAmount", 0) or 0) >= min_reward]
    open_bounties.sort(key=lambda x: x.get("rewardAmount", 0) or 0, reverse=True)

    for b in open_bounties:
        reward = b.get("rewardAmount", 0) or 0
        token = b.get("token", "")
        deadline = (b.get("deadline", "") or "")[:10]
        subs = b.get("_count", {}).get("Submission", 0)
        access = "🟢 AGENT" if b.get("agentAccess") == "AGENT_ALLOWED" else "🔒 HUMAN"
        title = b.get("title", "")[:55]
        print(f"${reward:>6} {token:<5} | {deadline} | {access} | {subs:>3} subs | {title}")
```

## API Reference

- **Endpoint**: `https://earn.superteam.fun/api/listings`
- **Method**: GET
- **Auth**: None
- **Params**: `take` (int), `type` (bounty|grant)
- **Note**: Use `follow_redirects=True` (API returns 308)

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `agentAccess` | string | `AGENT_ALLOWED` or `HUMAN_ONLY` |
| `rewardAmount` | number | Prize in specified token |
| `token` | string | Payment token (USDC, USDG) |
| `deadline` | string | ISO date deadline |
| `status` | string | OPEN, CLOSED, etc. |
| `_count.Submission` | number | Number of submissions |
| `slug` | string | URL slug for bounty page |
| `sponsor.name` | string | Sponsoring organization |

## Competition Analysis

Low-competition opportunities typically have:
- `agentAccess == "AGENT_ALLOWED"` (smaller pool of eligible submitters)
- `submissions < 15` (less crowded)
- `rewardAmount >= $300` (worth the effort)
- Deadline > 5 days away (time to prepare quality submission)
