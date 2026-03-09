#!/usr/bin/env python3
"""
DeFi Yield Scanner
Monitors stablecoin yield opportunities across all chains via DefiLlama.
Identifies agent-manageable strategies with risk-adjusted scoring.
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
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)

YIELDS_API = "https://yields.llama.fi/pools"
PROTOCOLS_API = "https://api.llama.fi/protocols"

# Risk scoring by protocol reputation
TRUSTED_PROTOCOLS = {
    "aave-v3": 1.0, "morpho-v1": 0.95, "morpho": 0.95, "euler-v2": 0.9,
    "compound-v3": 1.0, "curve-dex": 0.9, "pendle": 0.85,
    "sky-lending": 0.85, "wildcat-protocol": 0.8, "aerodrome-slipstream": 0.85,
    "uniswap-v3": 0.95, "lido": 1.0, "spark": 0.9,
}

CHAIN_RISK = {
    "Ethereum": 1.0, "Arbitrum": 0.95, "Base": 0.9, "Optimism": 0.9,
    "Polygon": 0.85, "Solana": 0.85, "Avalanche": 0.85,
    "Binance": 0.8, "Hyperliquid L1": 0.7, "Aptos": 0.75,
}


def fetch_yields() -> list[dict]:
    """Fetch all yield pools from DefiLlama."""
    with httpx.Client(timeout=60) as client:
        resp = client.get(YIELDS_API)
        resp.raise_for_status()
        return resp.json().get("data", [])


def score_pool(pool: dict) -> float:
    """Risk-adjusted score for a yield pool."""
    apy = pool.get("apy", 0) or 0
    tvl = pool.get("tvlUsd", 0) or 0
    project = pool.get("project", "")
    chain = pool.get("chain", "")
    apy_base = pool.get("apyBase", 0) or 0
    apy_reward = pool.get("apyReward", 0) or 0

    # Base yield is more sustainable than reward yield
    sustainability = apy_base / max(apy, 0.01)

    # Protocol trust
    protocol_trust = TRUSTED_PROTOCOLS.get(project, 0.5)

    # Chain trust
    chain_trust = CHAIN_RISK.get(chain, 0.5)

    # TVL factor (higher TVL = more tested)
    tvl_factor = min(tvl / 1e8, 1.0)  # caps at $100M

    # Penalize extremely high APY (likely unsustainable)
    apy_penalty = 1.0 if apy < 20 else (0.8 if apy < 50 else 0.5)

    score = (
        apy * 0.3
        * sustainability * 0.2
        * protocol_trust
        * chain_trust
        * (0.5 + tvl_factor * 0.5)
        * apy_penalty
    )
    return round(score, 4)


def analyze_yields(pools: list[dict]) -> dict:
    """Analyze and rank yield opportunities."""
    # Filter stablecoins with meaningful TVL and APY
    stable_pools = [
        p for p in pools
        if p.get("stablecoin", False)
        and (p.get("apy", 0) or 0) > 3
        and (p.get("tvlUsd", 0) or 0) > 500_000
    ]

    # Score and sort
    for p in stable_pools:
        p["risk_score"] = score_pool(p)

    stable_pools.sort(key=lambda x: x["risk_score"], reverse=True)

    # Categorize
    conservative = [p for p in stable_pools if (p.get("apy", 0) or 0) <= 10 and (p.get("tvlUsd", 0) or 0) > 10_000_000]
    moderate = [p for p in stable_pools if 10 < (p.get("apy", 0) or 0) <= 25]
    aggressive = [p for p in stable_pools if (p.get("apy", 0) or 0) > 25]

    # Chain distribution
    chain_dist: dict[str, int] = {}
    for p in stable_pools:
        chain = p.get("chain", "Unknown")
        chain_dist[chain] = chain_dist.get(chain, 0) + 1

    # Top opportunities per chain
    by_chain: dict[str, list] = {}
    for p in stable_pools[:100]:
        chain = p.get("chain", "Unknown")
        if chain not in by_chain:
            by_chain[chain] = []
        if len(by_chain[chain]) < 3:
            by_chain[chain].append(p)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_pools": len(pools),
        "stable_pools": len(stable_pools),
        "top_risk_adjusted": stable_pools[:30],
        "conservative": conservative[:15],
        "moderate": moderate[:15],
        "aggressive": aggressive[:15],
        "chain_distribution": dict(sorted(chain_dist.items(), key=lambda x: x[1], reverse=True)),
        "by_chain": {k: v for k, v in sorted(by_chain.items(), key=lambda x: len(x[1]), reverse=True)},
    }


def format_pool(p: dict) -> str:
    """Format a pool entry for display."""
    chain = p.get("chain", "?")[:12]
    project = p.get("project", "?")[:20]
    symbol = p.get("symbol", "?")[:20]
    apy = p.get("apy", 0) or 0
    apy_base = p.get("apyBase", 0) or 0
    tvl = (p.get("tvlUsd", 0) or 0) / 1e6
    score = p.get("risk_score", 0)
    return f"  {apy:>6.1f}% (base:{apy_base:>5.1f}%) | ${tvl:>7.1f}M | {chain:<12} | {project:<20} | {symbol:<20} | score:{score:.2f}"


def generate_report(analysis: dict) -> str:
    """Generate markdown yield report."""
    now = analysis["timestamp"][:19]
    lines = [
        f"# DeFi Stablecoin Yield Intelligence Report",
        f"**Generated**: {now} UTC",
        f"**Total pools scanned**: {analysis['total_pools']:,}",
        f"**Qualifying stablecoin pools**: {analysis['stable_pools']}",
        "",
        "---",
        "",
        "## 🏆 Top Risk-Adjusted Opportunities",
        "",
        "| Rank | APY | Base APY | TVL | Chain | Protocol | Pool | Score |",
        "|------|-----|----------|-----|-------|----------|------|-------|",
    ]

    for i, p in enumerate(analysis["top_risk_adjusted"][:20], 1):
        chain = p.get("chain", "")
        project = p.get("project", "")
        symbol = p.get("symbol", "")
        apy = p.get("apy", 0) or 0
        apy_base = p.get("apyBase", 0) or 0
        tvl = (p.get("tvlUsd", 0) or 0) / 1e6
        score = p.get("risk_score", 0)
        lines.append(f"| {i} | {apy:.1f}% | {apy_base:.1f}% | ${tvl:.1f}M | {chain} | {project} | {symbol} | {score:.2f} |")

    lines.extend([
        "",
        "## 🟢 Conservative (≤10% APY, >$10M TVL)",
        "",
        "Best for DAO treasury management and low-risk allocation.",
        "",
    ])
    for p in analysis["conservative"][:10]:
        lines.append(format_pool(p))

    lines.extend([
        "",
        "## 🟡 Moderate (10-25% APY)",
        "",
    ])
    for p in analysis["moderate"][:10]:
        lines.append(format_pool(p))

    lines.extend([
        "",
        "## 🔴 Aggressive (>25% APY)",
        "",
        "Higher risk. Verify sustainability of yield source.",
        "",
    ])
    for p in analysis["aggressive"][:10]:
        lines.append(format_pool(p))

    lines.extend([
        "",
        "## 📊 Chain Distribution",
        "",
    ])
    for chain, count in list(analysis["chain_distribution"].items())[:15]:
        bar = "█" * min(count, 40)
        lines.append(f"  {chain:<15} {count:>4} pools {bar}")

    return "\n".join(lines)


def main():
    print("📊 Scanning DeFi yields across all chains...")

    print("  Fetching yield data from DefiLlama...")
    pools = fetch_yields()
    print(f"  Fetched {len(pools):,} pools")

    print("  Analyzing and scoring...")
    analysis = analyze_yields(pools)
    print(f"  Found {analysis['stable_pools']} qualifying stablecoin pools")

    # Save raw data
    raw_file = DATA_DIR / "defi_yields.json"
    # Only save top pools to avoid huge files
    save_data = {
        "timestamp": analysis["timestamp"],
        "total_pools": analysis["total_pools"],
        "stable_pools": analysis["stable_pools"],
        "top_30": [
            {
                "chain": p.get("chain"),
                "project": p.get("project"),
                "symbol": p.get("symbol"),
                "apy": p.get("apy"),
                "apyBase": p.get("apyBase"),
                "tvlUsd": p.get("tvlUsd"),
                "risk_score": p.get("risk_score"),
            }
            for p in analysis["top_risk_adjusted"][:30]
        ],
    }
    with open(raw_file, "w") as f:
        json.dump(save_data, f, indent=2)

    # Generate report
    report = generate_report(analysis)
    report_file = REPORT_DIR / f"yield_report_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"\n✅ Report saved to {report_file}")

    # Print summary
    print("\n" + "=" * 80)
    print("🏆 TOP 10 RISK-ADJUSTED STABLECOIN YIELDS")
    print("=" * 80)
    print(f"  {'APY':>6} {'(base)':>8} | {'TVL':>9} | {'Chain':<12} | {'Protocol':<20} | {'Pool':<20} | Score")
    print(f"  {'-' * 90}")
    for p in analysis["top_risk_adjusted"][:10]:
        print(format_pool(p))


if __name__ == "__main__":
    main()
