#!/usr/bin/env python3
"""
AI Agent Token Market Tracker
Monitors AI agent token prices, volumes, and trends via CoinGecko.
Identifies market signals and tokenization timing indicators.
"""

import json
import sys
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

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def fetch_agent_tokens(per_page: int = 30) -> list[dict]:
    """Fetch AI agent category tokens from CoinGecko."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{COINGECKO_BASE}/coins/markets",
            params={
                "vs_currency": "usd",
                "category": "ai-agents",
                "order": "market_cap_desc",
                "per_page": per_page,
            },
        )
        resp.raise_for_status()
        return resp.json()


def fetch_trending() -> dict:
    """Fetch trending coins from CoinGecko."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{COINGECKO_BASE}/search/trending")
        resp.raise_for_status()
        return resp.json()


def analyze_market(tokens: list[dict], trending: dict) -> dict:
    """Analyze AI agent token market conditions."""
    trending_ids = {
        c["item"]["id"] for c in trending.get("coins", [])
    }

    total_mcap = sum(t.get("market_cap", 0) or 0 for t in tokens)
    total_vol = sum(t.get("total_volume", 0) or 0 for t in tokens)

    # Market health indicators
    positive = sum(1 for t in tokens if (t.get("price_change_percentage_24h", 0) or 0) > 0)
    negative = len(tokens) - positive
    avg_change = sum(t.get("price_change_percentage_24h", 0) or 0 for t in tokens) / max(len(tokens), 1)

    # High turnover tokens (volume/mcap ratio)
    high_turnover = []
    for t in tokens:
        mcap = t.get("market_cap", 0) or 1
        vol = t.get("total_volume", 0) or 0
        turnover = vol / mcap
        if turnover > 0.1:  # >10% daily turnover
            high_turnover.append({
                "name": t["name"],
                "symbol": t["symbol"].upper(),
                "turnover": round(turnover * 100, 1),
                "price": t.get("current_price", 0),
                "mcap": mcap,
                "volume": vol,
            })
    high_turnover.sort(key=lambda x: x["turnover"], reverse=True)

    # ATH analysis
    ath_drops = []
    for t in tokens:
        ath = t.get("ath", 0) or 0
        price = t.get("current_price", 0) or 0
        if ath > 0:
            drop_pct = ((ath - price) / ath) * 100
            ath_drops.append({
                "name": t["name"],
                "symbol": t["symbol"].upper(),
                "price": price,
                "ath": ath,
                "drop_pct": round(drop_pct, 1),
            })
    ath_drops.sort(key=lambda x: x["drop_pct"], reverse=True)

    # Market sentiment signal
    if avg_change > 5:
        sentiment = "🟢 BULLISH"
    elif avg_change > 0:
        sentiment = "🟡 SLIGHTLY BULLISH"
    elif avg_change > -5:
        sentiment = "🟡 SLIGHTLY BEARISH"
    else:
        sentiment = "🔴 BEARISH"

    tokenization_signal = "⛔ DO NOT TOKENIZE" if avg_change < -3 else (
        "⚠️ CAUTIOUS" if avg_change < 2 else "✅ FAVORABLE CONDITIONS"
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_market_cap": total_mcap,
        "total_volume_24h": total_vol,
        "tokens_tracked": len(tokens),
        "positive_24h": positive,
        "negative_24h": negative,
        "avg_change_24h": round(avg_change, 2),
        "sentiment": sentiment,
        "tokenization_signal": tokenization_signal,
        "top_tokens": [
            {
                "name": t["name"],
                "symbol": t["symbol"].upper(),
                "price": t.get("current_price", 0),
                "market_cap": t.get("market_cap", 0),
                "volume_24h": t.get("total_volume", 0),
                "change_24h": t.get("price_change_percentage_24h", 0),
                "is_trending": t["id"] in trending_ids,
            }
            for t in tokens[:20]
        ],
        "high_turnover": high_turnover[:10],
        "ath_drops": ath_drops[:10],
    }


def print_report(analysis: dict) -> None:
    """Print market analysis report."""
    print("=" * 80)
    print(f"🪙 AI AGENT TOKEN MARKET TRACKER — {analysis['timestamp'][:19]} UTC")
    print("=" * 80)
    print(f"  Total Market Cap: ${analysis['total_market_cap']/1e9:.2f}B")
    print(f"  24h Volume: ${analysis['total_volume_24h']/1e9:.2f}B")
    print(f"  Tokens Tracked: {analysis['tokens_tracked']}")
    print(f"  24h Positive/Negative: {analysis['positive_24h']}/{analysis['negative_24h']}")
    print(f"  Avg 24h Change: {analysis['avg_change_24h']:+.2f}%")
    print(f"  Sentiment: {analysis['sentiment']}")
    print(f"  Tokenization Signal: {analysis['tokenization_signal']}")

    print(f"\n📊 TOP 20 AI AGENT TOKENS BY MARKET CAP:")
    print(f"  {'Name':<22} {'Symbol':<8} {'Price':>10} {'MCap':>10} {'Vol':>10} {'24h':>7} {'Trend':>5}")
    print(f"  {'-' * 78}")
    for t in analysis["top_tokens"]:
        mcap = f"${t['market_cap']/1e6:.0f}M" if t["market_cap"] else "—"
        vol = f"${t['volume_24h']/1e6:.0f}M" if t["volume_24h"] else "—"
        change = t.get("change_24h", 0) or 0
        trend = "🔥" if t["is_trending"] else ""
        print(f"  {t['name']:<22} {t['symbol']:<8} ${t['price']:>8.4f} {mcap:>10} {vol:>10} {change:>+6.1f}% {trend}")

    print(f"\n🔄 HIGH TURNOVER (>10% daily volume/mcap):")
    for t in analysis["high_turnover"]:
        print(f"  {t['name']:<22} {t['symbol']:<8} turnover: {t['turnover']}%")

    print(f"\n📉 BIGGEST ATH DROPS:")
    for t in analysis["ath_drops"][:5]:
        print(f"  {t['name']:<22} {t['symbol']:<8} ${t['price']:.4f} (ATH: ${t['ath']:.2f}, -{t['drop_pct']:.0f}%)")


def main():
    print("🪙 Tracking AI agent token market...")

    print("  Fetching token data...")
    tokens = fetch_agent_tokens(30)
    print(f"  Got {len(tokens)} tokens")

    print("  Fetching trending data...")
    trending = fetch_trending()

    print("  Analyzing market conditions...")
    analysis = analyze_market(tokens, trending)

    # Save data
    data_file = DATA_DIR / "agent_tokens.json"
    with open(data_file, "w") as f:
        json.dump(analysis, f, indent=2)

    print_report(analysis)

    # Key decision output
    print(f"\n{'=' * 80}")
    print(f"🎯 STRATEGIC DECISION: {analysis['tokenization_signal']}")
    print(f"   Avg market change: {analysis['avg_change_24h']:+.2f}%")
    print(f"   Recommendation: Focus on SERVICE REVENUE, not token launches")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
