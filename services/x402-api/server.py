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
  uvicorn server:app --host 0.0.0.0 --port 8402
"""

import json
import re
import sys
import os
from datetime import datetime, timezone
from typing import Any, Callable

try:
    from fastapi import FastAPI, HTTPException, Query, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "httpx"])
    from fastapi import FastAPI, HTTPException, Query, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import httpx

app = FastAPI(
    title="CryptoAI Intelligence API",
    description="AI-powered crypto intelligence endpoints. Pay-per-call via x402/L402 (USDC on Base).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# x402 / L402 Payment Middleware Implementation
# -----------------------------------------------------------------------------
# This middleware enforces a 402 Payment Required response for monetized endpoints.
# Clients must supply an `Authorization: L402 <macaroon>:<preimage>` or a 
# valid `X-API-Key` (for subscription users).
# In a full production environment, this integrates with Coinbase Commerce, 
# Solana Pay, or a Lightning Node (Alby/LND).

VALID_API_KEYS = {"test-key-123", "pro-delegate-456"}
# Simulated endpoint pricing
ENDPOINT_PRICES = {
    "/api/governance/summary": 10, # cents
    "/api/yields/top": 5,
    "/api/token/analysis": 10,
    "/api/treasury/health": 15,
}

# Load actual wallet address
AGENT_WALLET_FILE = Path(__file__).parent.parent.parent / "data" / "agent_wallet.json"
AGENT_WALLET_ADDRESS = "0xCRYPTOAI_TREASURY_WALLET_ADDRESS"
if AGENT_WALLET_FILE.exists():
    try:
        with open(AGENT_WALLET_FILE, "r") as f:
            wallet_data = json.load(f)
            AGENT_WALLET_ADDRESS = wallet_data.get("address", AGENT_WALLET_ADDRESS)
    except Exception:
        pass

@app.middleware("http")
async def x402_payment_middleware(request: Request, call_next: Callable) -> Response:
    # Allow health and root endpoints for free
    if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
        return await call_next(request)

    price_cents = ENDPOINT_PRICES.get(request.url.path, 10)
    
    # 1. Check for subscription API Key
    api_key = request.headers.get("X-API-Key")
    if api_key in VALID_API_KEYS:
        # Proceed if subscription is valid
        return await call_next(request)

    # 2. Check for L402/x402 Payment Proof
    auth_header = request.headers.get("Authorization")
    
    # If no valid payment proof, return 402
    if not auth_header or not auth_header.startswith("L402 "):
        headers = {
            "WWW-Authenticate": f'L402 macaroon="mock_macaroon_string_here", invoice="mock_payment_invoice_string_here"'
        }
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment Required",
                "message": f"This endpoint requires a payment of ${price_cents/100:.2f} USDC on Base.",
                "payment_address": AGENT_WALLET_ADDRESS,
                "payment_network": "base",
                "payment_token": "usdc",
                "amount": price_cents / 100
            },
            headers=headers
        )
    
    # Validate the macaroon/preimage here (Mock validation)
    token = auth_header.split(" ")[1]
    if ":" not in token:
        return JSONResponse(status_code=401, content={"error": "Invalid L402 token format"})

    # If valid, proceed to the endpoint
    return await call_next(request)
# -----------------------------------------------------------------------------


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
        "payment": "x402/L402 enabled. Supply valid X-API-Key or Authorization header.",
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
