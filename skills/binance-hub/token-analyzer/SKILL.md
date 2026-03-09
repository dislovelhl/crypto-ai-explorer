---
title: Token Fundamental Analyzer
description: Analyze any crypto token's fundamentals using CoinGecko data. Returns price, market cap, volume, ATH comparison, turnover analysis, and actionable signals.
metadata:
  version: 1.0.0
  author: cryptoai-explorer
license: MIT
---

# Token Fundamental Analyzer

Analyze any crypto token's market fundamentals using CoinGecko's free API. Returns structured data with actionable trading and investment signals.

## When to Use

- Quick token research and due diligence
- Comparing tokens within a category (e.g., AI agents)
- Monitoring portfolio positions
- Identifying overbought/oversold conditions
- ATH comparison and trend analysis

## How to Use

```python
import httpx

async def analyze_token(token_id: str):
    """Analyze a token by its CoinGecko ID."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"https://api.coingecko.com/api/v3/coins/{token_id}")
        data = resp.json()

    m = data.get("market_data", {})
    price = m.get("current_price", {}).get("usd", 0)
    mcap = m.get("market_cap", {}).get("usd", 0)
    vol = m.get("total_volume", {}).get("usd", 0)
    ath = m.get("ath", {}).get("usd", 0)

    turnover = (vol / mcap * 100) if mcap > 0 else 0
    ath_drop = ((ath - price) / ath * 100) if ath > 0 else 0

    print(f"{data['name']} ({data['symbol'].upper()})")
    print(f"Price: ${price:.4f}")
    print(f"Market Cap: ${mcap/1e6:.1f}M")
    print(f"24h Volume: ${vol/1e6:.1f}M")
    print(f"Turnover: {turnover:.1f}%")
    print(f"ATH: ${ath:.2f} (-{ath_drop:.0f}%)")

    # Generate signals
    if turnover > 20: print("🔥 HIGH TURNOVER")
    if ath_drop > 80: print("📉 DEEP ATH DROP")
    if m.get("price_change_percentage_24h", 0) > 10: print("📈 STRONG PUMP")
    if m.get("price_change_percentage_24h", 0) < -10: print("📉 STRONG DUMP")

# Category scan
async def scan_category(category="ai-agents", limit=20):
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={"vs_currency": "usd", "category": category,
                    "order": "market_cap_desc", "per_page": limit}
        )
        return resp.json()
```

## Useful Categories

| Category ID | Description |
|-------------|-------------|
| `ai-agents` | AI agent tokens |
| `artificial-intelligence` | Broader AI crypto |
| `decentralized-finance-defi` | DeFi tokens |
| `layer-1` | L1 blockchains |
| `layer-2` | L2 scaling |
| `meme-token` | Memecoins |

## Signal Definitions

| Signal | Condition | Interpretation |
|--------|-----------|----------------|
| HIGH TURNOVER | Volume/MCap > 20% | Active trading, potential volatility |
| DEEP ATH DROP | >80% below ATH | Either deep value or dying project |
| STRONG PUMP | >10% 24h gain | Momentum or manipulation |
| STRONG DUMP | >-10% 24h loss | Selling pressure or liquidations |
| MONTHLY RALLY | >50% 30d gain | Sustained uptrend |
| MONTHLY BLEED | <-30% 30d loss | Sustained downtrend |

## Rate Limits

CoinGecko free API: ~10-30 requests/minute. Use `per_page` parameter to reduce calls.
