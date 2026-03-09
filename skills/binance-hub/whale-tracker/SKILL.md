---
title: Whale Wallet Tracker
description: Track large wallet movements and whale activity on Ethereum, Base, Arbitrum, and Solana using public APIs. Detect significant token transfers, accumulation patterns, and smart money flows.
metadata:
  version: 1.0.0
  author: cryptoai-explorer
license: MIT
---

# Whale Wallet Tracker

Monitor large wallet movements using free public APIs. Track whale accumulation, distribution, and smart money flows across major chains.

## When to Use

- Monitoring large holder movements for specific tokens
- Detecting whale accumulation or distribution patterns
- Tracking smart money wallets (VCs, funds, known traders)
- Setting up alerts for significant transfers

## Data Sources

| Source | Chains | Auth | Rate Limit |
|--------|--------|------|------------|
| Etherscan API | Ethereum | API key (free) | 5/sec |
| Arbiscan API | Arbitrum | API key (free) | 5/sec |
| Basescan API | Base | API key (free) | 5/sec |
| Solscan API | Solana | API key (free) | Varies |
| DeBank OpenAPI | Multi-chain | API key | Varies |

## How to Use

```python
import httpx

async def get_large_transfers(token_address: str, chain="ethereum", min_usd=100000):
    """Get recent large token transfers."""
    # Using Etherscan-compatible API
    explorers = {
        "ethereum": "https://api.etherscan.io/api",
        "arbitrum": "https://api.arbiscan.io/api",
        "base": "https://api.basescan.org/api",
    }

    base = explorers.get(chain)
    if not base:
        return []

    api_key = "YourFreeAPIKey"  # Get from etherscan.io
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(base, params={
            "module": "account",
            "action": "tokentx",
            "contractaddress": token_address,
            "page": 1,
            "offset": 100,
            "sort": "desc",
            "apikey": api_key,
        })
        data = resp.json()

    transfers = data.get("result", [])
    # Filter for large transfers (requires price data to convert to USD)
    return transfers[:20]


async def track_wallet(address: str, chain="ethereum"):
    """Get recent transactions for a specific wallet."""
    explorers = {
        "ethereum": "https://api.etherscan.io/api",
        "arbitrum": "https://api.arbiscan.io/api",
        "base": "https://api.basescan.org/api",
    }

    base = explorers.get(chain)
    api_key = "YourFreeAPIKey"

    async with httpx.AsyncClient(timeout=30) as client:
        # Normal transactions
        resp = await client.get(base, params={
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": 20,
            "sort": "desc",
            "apikey": api_key,
        })
        return resp.json().get("result", [])
```

## Known Whale Addresses

Research and track these categories:
- Exchange hot wallets (Binance, Coinbase deposits indicate selling)
- VC fund wallets (a16z, Paradigm, Polychain)
- Protocol treasuries (Arbitrum, Optimism, Uniswap)
- Notable traders (follow Arkham Intel, Nansen labels)

## Alert Patterns

| Pattern | Signal | Action |
|---------|--------|--------|
| Large exchange deposit | Potential sell pressure | Monitor for price drop |
| Large exchange withdrawal | Potential accumulation | Monitor for position building |
| New wallet accumulation | Smart money entry | Research what they know |
| Treasury diversification | Protocol de-risking | Check governance forums |
| Multiple whales buying | Coordinated accumulation | Strong bullish signal |
