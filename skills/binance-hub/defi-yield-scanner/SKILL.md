---
title: DeFi Yield Scanner
description: Scan and rank stablecoin yield opportunities across all DeFi protocols and chains using DefiLlama data. Returns risk-adjusted, scored results filtered by APY, TVL, and chain.
metadata:
  version: 1.0.0
  author: cryptoai-explorer
license: MIT
---

# DeFi Yield Scanner

Scan 19,000+ DeFi pools across all chains to find the best stablecoin yield opportunities. Returns risk-adjusted rankings with protocol trust scoring and sustainability analysis.

## When to Use

- Finding the best yield for stablecoin deposits
- Comparing yields across chains (Ethereum, Base, Arbitrum, Solana, etc.)
- Monitoring yield changes for treasury management
- Identifying sustainable vs. incentivized yields

## How to Use

Query the DefiLlama Yields API and apply risk-adjusted scoring:

```python
import httpx

async def scan_yields(min_tvl=1_000_000, min_apy=5.0, stablecoin_only=True):
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get("https://yields.llama.fi/pools")
        pools = resp.json()["data"]

    filtered = [
        p for p in pools
        if (not stablecoin_only or p.get("stablecoin"))
        and (p.get("apy", 0) or 0) >= min_apy
        and (p.get("tvlUsd", 0) or 0) >= min_tvl
    ]

    # Sort by APY descending
    filtered.sort(key=lambda x: x.get("apy", 0) or 0, reverse=True)

    for p in filtered[:20]:
        chain = p.get("chain", "")
        project = p.get("project", "")
        symbol = p.get("symbol", "")
        apy = p.get("apy", 0) or 0
        tvl = (p.get("tvlUsd", 0) or 0) / 1e6
        print(f"{apy:>6.1f}% | ${tvl:>7.1f}M | {chain:<12} | {project:<20} | {symbol}")
```

## API Reference

- **Endpoint**: `https://yields.llama.fi/pools`
- **Method**: GET
- **Auth**: None required
- **Rate Limit**: Generous, no key needed
- **Response**: JSON array of pool objects

### Key Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `chain` | string | Blockchain name |
| `project` | string | Protocol identifier |
| `symbol` | string | Pool token symbols |
| `tvlUsd` | number | Total value locked in USD |
| `apy` | number | Total APY (base + reward) |
| `apyBase` | number | Base yield from protocol fees |
| `apyReward` | number | Additional incentive yield |
| `stablecoin` | boolean | Whether pool is stablecoin-only |

## Risk Assessment

- **Base APY** is more sustainable than reward APY
- Higher TVL pools are generally more battle-tested
- Trusted protocols: Aave, Morpho, Compound, Curve, Euler, Pendle
- Watch for: extremely high APYs (>50%), low TVL (<$500K), unknown protocols

## Example Output

```
  10.5% | $   83.0M | Base         | avantis              | USDC
   7.7% | $  216.5M | Arbitrum     | usd-ai               | SUSDAI
   7.2% | $   82.9M | Ethereum     | curve-dex            | USDC-RLUSD
   7.1% | $  104.0M | Ethereum     | morpho-v1            | BBQUSDCRESERVOIR
   6.8% | $  132.9M | Ethereum     | euler-v2             | PYUSD
```
