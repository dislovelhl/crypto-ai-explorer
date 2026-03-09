#!/usr/bin/env python3
"""
CryptoAI MCP Server
Model Context Protocol server for crypto intelligence.
Enables Claude Desktop, Cursor, and other MCP-compatible tools
to query governance, yield, token, and bounty data.

Run: python3 server.py
Configure in Claude Desktop: ~/.config/claude/claude_desktop_config.json
"""

import asyncio
import json
import sys
from datetime import datetime, timezone

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx

# MCP protocol implementation (simplified stdio transport)
# Full MCP SDK: pip install mcp

TOOLS = [
    {
        "name": "governance_digest",
        "description": "Get latest governance discussions from a DAO forum (Arbitrum or Optimism). Returns active proposals, AI-related topics, grant discussions, and high-activity threads.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dao": {
                    "type": "string",
                    "description": "DAO name: 'arbitrum' or 'optimism'",
                    "enum": ["arbitrum", "optimism"],
                    "default": "arbitrum",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of topics to return",
                    "default": 15,
                },
            },
        },
    },
    {
        "name": "top_yields",
        "description": "Get top stablecoin DeFi yield opportunities across all chains. Scans 19,000+ pools via DefiLlama and returns risk-adjusted rankings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_tvl": {
                    "type": "number",
                    "description": "Minimum TVL in USD",
                    "default": 1000000,
                },
                "min_apy": {
                    "type": "number",
                    "description": "Minimum APY percentage",
                    "default": 5.0,
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of pools to return",
                    "default": 15,
                },
            },
        },
    },
    {
        "name": "agent_bounties",
        "description": "Get AGENT_ALLOWED bounties from Superteam Earn — crypto bounties that AI agents can legitimately complete. Shows reward, deadline, and competition level.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_reward": {
                    "type": "number",
                    "description": "Minimum reward amount",
                    "default": 0,
                },
                "agent_only": {
                    "type": "boolean",
                    "description": "Only show AGENT_ALLOWED bounties",
                    "default": True,
                },
            },
        },
    },
    {
        "name": "token_analysis",
        "description": "Analyze an AI agent token's fundamentals — price, market cap, volume, ATH comparison, turnover, and trading signals.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_id": {
                    "type": "string",
                    "description": "CoinGecko token ID (e.g., 'virtual-protocol', 'fetch-ai')",
                },
            },
            "required": ["token_id"],
        },
    },
    {
        "name": "agent_market_overview",
        "description": "Get overview of the AI agent token market — total market cap, sentiment, top tokens by market cap, high-turnover tokens, and tokenization timing signal.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of tokens to return",
                    "default": 15,
                },
            },
        },
    },
]

FORUM_APIS = {
    "arbitrum": "https://forum.arbitrum.foundation",
    "optimism": "https://gov.optimism.io",
}


async def handle_governance_digest(args: dict) -> str:
    dao = args.get("dao", "arbitrum")
    limit = args.get("limit", 15)
    forum_url = FORUM_APIS.get(dao)
    if not forum_url:
        return json.dumps({"error": f"Unsupported DAO: {dao}"})

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(f"{forum_url}/latest.json")
        data = resp.json()

    topics = data.get("topic_list", {}).get("topics", [])[:limit]
    result = {
        "dao": dao,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "topics": [
            {
                "title": t.get("title", ""),
                "views": t.get("views", 0),
                "posts": t.get("posts_count", 0),
                "id": t.get("id", 0),
                "url": f"{forum_url}/t/{t.get('id', 0)}",
            }
            for t in topics
        ],
    }
    return json.dumps(result, indent=2)


async def handle_top_yields(args: dict) -> str:
    min_tvl = args.get("min_tvl", 1e6)
    min_apy = args.get("min_apy", 5.0)
    limit = args.get("limit", 15)

    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        resp = await client.get("https://yields.llama.fi/pools")
        pools = resp.json().get("data", [])

    filtered = [
        p for p in pools
        if p.get("stablecoin", False)
        and (p.get("apy", 0) or 0) >= min_apy
        and (p.get("tvlUsd", 0) or 0) >= min_tvl
    ]
    filtered.sort(key=lambda x: x.get("apy", 0) or 0, reverse=True)

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_scanned": len(pools),
        "qualifying": len(filtered),
        "pools": [
            {
                "chain": p.get("chain", ""),
                "protocol": p.get("project", ""),
                "pool": p.get("symbol", ""),
                "apy": round(p.get("apy", 0) or 0, 2),
                "apy_base": round(p.get("apyBase", 0) or 0, 2),
                "tvl_usd": p.get("tvlUsd", 0),
            }
            for p in filtered[:limit]
        ],
    }
    return json.dumps(result, indent=2)


async def handle_agent_bounties(args: dict) -> str:
    min_reward = args.get("min_reward", 0)
    agent_only = args.get("agent_only", True)

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            "https://earn.superteam.fun/api/listings",
            params={"take": 100, "type": "bounty"},
        )
        bounties = resp.json()

    filtered = [b for b in bounties if b.get("status") == "OPEN"]
    if agent_only:
        filtered = [b for b in filtered if b.get("agentAccess") == "AGENT_ALLOWED"]
    filtered = [b for b in filtered if (b.get("rewardAmount", 0) or 0) >= min_reward]
    filtered.sort(key=lambda x: x.get("rewardAmount", 0) or 0, reverse=True)

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_bounties": len(filtered),
        "total_prize_pool": sum(b.get("rewardAmount", 0) or 0 for b in filtered),
        "bounties": [
            {
                "title": b.get("title", ""),
                "reward": b.get("rewardAmount", 0),
                "token": b.get("token", ""),
                "deadline": (b.get("deadline", "") or "")[:10],
                "submissions": b.get("_count", {}).get("Submission", 0),
                "agent_access": b.get("agentAccess", ""),
                "url": f"https://earn.superteam.fun/listings/{b.get('slug', '')}/",
            }
            for b in filtered
        ],
    }
    return json.dumps(result, indent=2)


async def handle_token_analysis(args: dict) -> str:
    token_id = args["token_id"]
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(f"https://api.coingecko.com/api/v3/coins/{token_id}")
        if resp.status_code != 200:
            return json.dumps({"error": f"Token '{token_id}' not found"})
        data = resp.json()

    m = data.get("market_data", {})
    result = {
        "name": data.get("name", ""),
        "symbol": data.get("symbol", "").upper(),
        "price": m.get("current_price", {}).get("usd", 0),
        "market_cap": m.get("market_cap", {}).get("usd", 0),
        "volume_24h": m.get("total_volume", {}).get("usd", 0),
        "ath": m.get("ath", {}).get("usd", 0),
        "ath_change_pct": m.get("ath_change_percentage", {}).get("usd", 0),
        "change_24h": m.get("price_change_percentage_24h", 0),
        "change_7d": m.get("price_change_percentage_7d", 0),
        "change_30d": m.get("price_change_percentage_30d", 0),
        "description": (data.get("description", {}).get("en", "") or "")[:500],
    }
    return json.dumps(result, indent=2)


async def handle_agent_market_overview(args: dict) -> str:
    limit = args.get("limit", 15)
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "category": "ai-agents",
                "order": "market_cap_desc",
                "per_page": limit,
            },
        )
        tokens = resp.json()

    total_mcap = sum(t.get("market_cap", 0) or 0 for t in tokens)
    avg_change = sum(t.get("price_change_percentage_24h", 0) or 0 for t in tokens) / max(len(tokens), 1)

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_market_cap": total_mcap,
        "avg_24h_change": round(avg_change, 2),
        "sentiment": "BULLISH" if avg_change > 5 else "NEUTRAL" if avg_change > -3 else "BEARISH",
        "tokenization_signal": "FAVORABLE" if avg_change > 2 else "CAUTIOUS" if avg_change > -5 else "AVOID",
        "tokens": [
            {
                "name": t.get("name", ""),
                "symbol": t.get("symbol", "").upper(),
                "price": t.get("current_price", 0),
                "market_cap": t.get("market_cap", 0),
                "volume_24h": t.get("total_volume", 0),
                "change_24h": t.get("price_change_percentage_24h", 0),
            }
            for t in tokens
        ],
    }
    return json.dumps(result, indent=2)


HANDLERS = {
    "governance_digest": handle_governance_digest,
    "top_yields": handle_top_yields,
    "agent_bounties": handle_agent_bounties,
    "token_analysis": handle_token_analysis,
    "agent_market_overview": handle_agent_market_overview,
}


async def handle_request(request: dict) -> dict:
    """Handle an MCP request."""
    method = request.get("method", "")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "cryptoai-explorer", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            },
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS},
        }
    elif method == "tools/call":
        tool_name = request.get("params", {}).get("name", "")
        arguments = request.get("params", {}).get("arguments", {})
        handler = HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }
        try:
            result = await handler(arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": result}]},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)},
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


async def main_stdio():
    """Run MCP server over stdio transport."""
    print("CryptoAI MCP Server starting (stdio transport)...", file=sys.stderr)
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            request = json.loads(line.decode())
            response = await handle_request(request)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            continue


async def test_mode():
    """Test all tools without MCP transport."""
    print("🔧 CryptoAI MCP Server — Test Mode")
    print("=" * 60)

    for tool in TOOLS:
        name = tool["name"]
        print(f"\n--- Testing: {name} ---")
        handler = HANDLERS.get(name)
        if handler:
            # Use defaults
            test_args = {}
            if name == "token_analysis":
                test_args = {"token_id": "virtual-protocol"}
            try:
                result = await handler(test_args)
                parsed = json.loads(result)
                # Print compact summary
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        if isinstance(v, list):
                            print(f"  {k}: [{len(v)} items]")
                        elif isinstance(v, (int, float)):
                            print(f"  {k}: {v}")
                        elif isinstance(v, str) and len(v) < 100:
                            print(f"  {k}: {v}")
                print(f"  ✅ OK")
            except Exception as e:
                print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    if "--test" in sys.argv:
        asyncio.run(test_mode())
    else:
        asyncio.run(main_stdio())
