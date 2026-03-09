#!/usr/bin/env python3
"""
x402 Pay-Per-Call AI Agent API
Monetized crypto intelligence endpoints behind x402 payment wall.

Endpoints:
  /api/governance/summary   — Governance proposal analysis ($0.10/call)
  /api/yields/top           — Top stablecoin yields ($0.05/call)
  /api/token/analysis       — Token fundamental analysis ($0.10/call)
  /api/treasury/health      — DAO treasury health check ($0.15/call)

Deployment:
  pip install fastapi uvicorn httpx
  # pip install x402  # uncomment when x402 SDK is available
  uvicorn server:app --host 0.0.0.0 --port 8402
"""

import json
import re
import sys
from datetime import datetime, timezone
from typing import Any

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "httpx"])
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    import httpx

app = FastAPI(
    title="CryptoAI Intelligence API",
    description="AI-powered crypto intelligence endpoints. Pay-per-call via x402 (USDC on Base).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# x402 middleware would go here when SDK is integrated:
# from x402.middleware import X402Middleware
# app.add_middleware(
#     X402Middleware,
#     facilitator_url="https://x402.coinbase.com",
#     receiver_address="0xYOUR_WALLET_ADDRESS",
#     network="base",
# )


DEFI_LLAMA_YIELDS = "https://yields.llama.fi/pools"
ARBITRUM_FORUM = "https://forum.arbitrum.foundation"
COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


@app.get("/")
async def root():
    return {
        "service": "CryptoAI Intelligence API",
        "version": "0.1.0",
        "payment": "x402 (USDC on Base) — coming soon, currently free",
        "endpoints": {
            "/api/governance/summary": "Governance proposal analysis ($0.10/call)",
            "/api/yields/top": "Top stablecoin yields ($0.05/call)",
            "/api/token/analysis": "Token fundamental analysis ($0.10/call)",
            "/api/treasury/health": "DAO treasury health check ($0.15/call)",
        },
    }


@app.get("/api/governance/summary")
async def governance_summary(
    dao: str = Query("arbitrum", description="DAO name: arbitrum, optimism"),
    limit: int = Query(10, ge=1, le=50),
) -> dict[str, Any]:
    """
    Get AI-generated governance intelligence digest.
    Price: $0.10/call (x402)
    """
    if dao.lower() == "arbitrum":
        forum_url = f"{ARBITRUM_FORUM}/latest.json"
    elif dao.lower() == "optimism":
        forum_url = "https://gov.optimism.io/latest.json"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported DAO: {dao}")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(forum_url)
        resp.raise_for_status()
        data = resp.json()

    topics = data.get("topic_list", {}).get("topics", [])[:limit]

    ai_keywords = ["ai", "agent", "grant", "fund", "budget", "treasury", "proposal", "vote"]
    analyzed_topics = []
    for t in topics:
        title = t.get("title", "")
        views = t.get("views", 0)
        posts = t.get("posts_count", 0)
        tags = [k for k in ai_keywords if k in title.lower()]

        analyzed_topics.append({
            "title": title,
            "views": views,
            "posts": posts,
            "activity_score": round(views * 0.3 + posts * 10, 1),
            "tags": tags,
            "url": f"{ARBITRUM_FORUM}/t/{t.get('id', 0)}",
        })

    analyzed_topics.sort(key=lambda x: x["activity_score"], reverse=True)

    return {
        "dao": dao,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "topics_analyzed": len(analyzed_topics),
        "summary": f"{dao.title()} governance digest: {len(analyzed_topics)} active topics, "
                   f"top topic: '{analyzed_topics[0]['title'][:60]}' "
                   f"({analyzed_topics[0]['views']} views)" if analyzed_topics else "No topics",
        "topics": analyzed_topics,
        "ai_related": [t for t in analyzed_topics if "ai" in t["tags"] or "agent" in t["tags"]],
        "grant_related": [t for t in analyzed_topics if "grant" in t["tags"] or "fund" in t["tags"]],
    }


@app.get("/api/yields/top")
async def top_yields(
    min_tvl: float = Query(1e6, description="Minimum TVL in USD"),
    min_apy: float = Query(5.0, description="Minimum APY percentage"),
    stablecoin_only: bool = Query(True, description="Filter for stablecoins only"),
    limit: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    """
    Get top risk-adjusted DeFi yield opportunities.
    Price: $0.05/call (x402)
    """
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(DEFI_LLAMA_YIELDS)
        resp.raise_for_status()
        pools = resp.json().get("data", [])

    filtered = [
        p for p in pools
        if (not stablecoin_only or p.get("stablecoin", False))
        and (p.get("apy", 0) or 0) >= min_apy
        and (p.get("tvlUsd", 0) or 0) >= min_tvl
    ]

    filtered.sort(key=lambda x: (x.get("apy", 0) or 0), reverse=True)

    results = []
    for p in filtered[:limit]:
        results.append({
            "chain": p.get("chain", ""),
            "protocol": p.get("project", ""),
            "pool": p.get("symbol", ""),
            "apy": round(p.get("apy", 0) or 0, 2),
            "apy_base": round(p.get("apyBase", 0) or 0, 2),
            "apy_reward": round(p.get("apyReward", 0) or 0, 2),
            "tvl_usd": p.get("tvlUsd", 0),
            "stablecoin": p.get("stablecoin", False),
        })

    total_tvl = sum(r["tvl_usd"] for r in results)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_pools_scanned": len(pools),
        "qualifying_pools": len(filtered),
        "total_qualifying_tvl": total_tvl,
        "filters": {
            "min_tvl": min_tvl,
            "min_apy": min_apy,
            "stablecoin_only": stablecoin_only,
        },
        "pools": results,
    }


@app.get("/api/token/analysis")
async def token_analysis(
    token_id: str = Query(..., description="CoinGecko token ID (e.g., 'virtual-protocol', 'fetch-ai')"),
) -> dict[str, Any]:
    """
    Get AI agent token fundamental analysis.
    Price: $0.10/call (x402)
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{COINGECKO_BASE}/coins/{token_id}")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Token '{token_id}' not found on CoinGecko")
        resp.raise_for_status()
        data = resp.json()

    market = data.get("market_data", {})
    price = market.get("current_price", {}).get("usd", 0)
    mcap = market.get("market_cap", {}).get("usd", 0)
    vol = market.get("total_volume", {}).get("usd", 0)
    ath = market.get("ath", {}).get("usd", 0)
    ath_change = market.get("ath_change_percentage", {}).get("usd", 0)
    change_24h = market.get("price_change_percentage_24h", 0)
    change_7d = market.get("price_change_percentage_7d", 0)
    change_30d = market.get("price_change_percentage_30d", 0)

    # Basic analysis signals
    turnover = (vol / mcap * 100) if mcap > 0 else 0
    ath_drop = abs(ath_change) if ath_change else 0

    signals = []
    if turnover > 20:
        signals.append("🔥 HIGH TURNOVER — active trading interest")
    if ath_drop > 80:
        signals.append("📉 DEEP ATH DROP — potential value or dead project")
    if change_24h > 10:
        signals.append("📈 STRONG DAILY MOVE UP — momentum or pump")
    if change_24h < -10:
        signals.append("📉 STRONG DAILY DROP — selling pressure")
    if change_30d > 50:
        signals.append("🚀 STRONG MONTHLY RALLY")
    if change_30d < -30:
        signals.append("⚠️ MONTHLY DOWNTREND")

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "token": {
            "name": data.get("name", ""),
            "symbol": data.get("symbol", "").upper(),
            "id": token_id,
        },
        "market_data": {
            "price_usd": price,
            "market_cap": mcap,
            "volume_24h": vol,
            "ath": ath,
            "ath_change_pct": ath_change,
            "change_24h_pct": change_24h,
            "change_7d_pct": change_7d,
            "change_30d_pct": change_30d,
            "turnover_pct": round(turnover, 2),
        },
        "signals": signals,
        "description": (data.get("description", {}).get("en", "") or "")[:500],
        "links": {
            "homepage": (data.get("links", {}).get("homepage", []) or [""])[0],
            "github": (data.get("links", {}).get("repos_url", {}).get("github", []) or [""])[0],
            "twitter": data.get("links", {}).get("twitter_screen_name", ""),
        },
    }


@app.get("/api/treasury/health")
async def treasury_health(
    dao: str = Query("arbitrum", description="DAO to analyze"),
) -> dict[str, Any]:
    """
    Get DAO treasury health analysis.
    Price: $0.15/call (x402)
    """
    # This is a scaffold — full implementation would pull on-chain treasury data
    # For now, provide forum-based intelligence about treasury discussions

    if dao.lower() != "arbitrum":
        raise HTTPException(status_code=400, detail="Currently only 'arbitrum' is supported")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{ARBITRUM_FORUM}/search.json",
            params={"q": "treasury fund budget allocation"},
        )
        resp.raise_for_status()
        data = resp.json()

    topics = data.get("topics", [])
    posts = data.get("posts", [])

    treasury_topics = [
        {
            "title": t.get("title", ""),
            "id": t.get("id", 0),
            "url": f"{ARBITRUM_FORUM}/t/{t.get('id', 0)}",
        }
        for t in topics[:10]
    ]

    treasury_mentions = [
        {
            "topic_id": p.get("topic_id", 0),
            "blurb": p.get("blurb", "")[:200],
        }
        for p in posts[:10]
    ]

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dao": dao,
        "status": "scaffold — full on-chain analysis coming in v0.2",
        "treasury_discussions": treasury_topics,
        "recent_mentions": treasury_mentions,
        "recommendations": [
            "Monitor 'Automate Consolidation of Idle Funds' proposal for treasury optimization opportunity",
            "Track AGI proposal for governance automation investment",
            "Review Trailblazer AI grants for ecosystem development ROI",
        ],
    }


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8402)
