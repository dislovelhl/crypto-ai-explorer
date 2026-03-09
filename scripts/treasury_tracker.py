#!/usr/bin/env python3
"""
DAO Treasury & Smart Money Tracker
Pulls data on the largest DAO treasuries using DefiLlama API.
Helps delegates and analysts track where capital is concentrated.
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
REPORT_DIR = Path(__file__).parent.parent / "reports"
DATA_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

def main():
    now = datetime.now(timezone.utc)
    print(f"🏦 DAO Treasury & Smart Money Tracker — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    # DefiLlama protocols endpoint contains treasury data if filtered correctly
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        print("📋 Fetching protocol and treasury data from DefiLlama...")
        resp = client.get("https://api.llama.fi/protocols")
        resp.raise_for_status()
        protocols = resp.json()

    # Filter for entities that act as treasuries, reserves, or have massive TVL
    # Often, DAOs have category "Treasury" or we can just sort top protocols by TVL
    # to proxy where the highest concentrated capital sits.
    
    # We'll extract "Treasury" categories
    treasuries = [p for p in protocols if p.get("category", "") in ["Treasury", "Reserve", "CDP", "Yield Aggregator", "Services"]]
    
    # If not enough, let's just grab the top 20 protocols by TVL as proxy for "Smart Money" concentration
    top_protocols = sorted(protocols, key=lambda x: x.get("tvl", 0) or 0, reverse=True)[:50]

    print(f"   Found {len(treasuries)} DAO Treasuries/Reserves")
    
    # Sort treasuries by TVL
    treasuries.sort(key=lambda x: x.get("tvl", 0) or 0, reverse=True)

    print("\n💰 TOP DAO TREASURIES:")
    print(f"{'Name':<25} {'Chain':<15} {'TVL (USD)':>15}")
    print("-" * 60)
    
    treasury_data = []
    for t in treasuries[:15]:
        name = t.get("name", "")[:24]
        chain = t.get("chain", "")[:14]
        tvl = t.get("tvl", 0) or 0
        tvl_m = tvl / 1e6
        
        treasury_data.append({
            "name": name,
            "chain": chain,
            "tvl": tvl,
            "symbol": t.get("symbol", ""),
            "url": t.get("url", "")
        })
        print(f"{name:<25} {chain:<15} ${tvl_m:>11,.1f}M")

    # Save Data
    out_data = {
        "timestamp": now.isoformat(),
        "total_treasuries_tracked": len(treasuries),
        "total_treasury_tvl": sum(t.get("tvl", 0) or 0 for t in treasuries),
        "top_treasuries": treasury_data,
        "top_defi_protocols": [
            {"name": p.get("name"), "tvl": p.get("tvl"), "chain": p.get("chain")} 
            for p in top_protocols[:10]
        ]
    }

    data_file = DATA_DIR / "dao_treasuries.json"
    with open(data_file, "w") as f:
        json.dump(out_data, f, indent=2)
    print(f"\n💾 Treasury data saved to {data_file}")

    # Generate Report
    report_file = REPORT_DIR / f"treasury_report_{now.strftime('%Y%m%d')}.md"
    with open(report_file, "w") as f:
        f.write(f"# 🏦 DAO Treasury Concentration Report\n\n")
        f.write(f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        f.write(f"**Total Treasuries Tracked:** {len(treasuries)}\n")
        f.write(f"**Cumulative Treasury TVL:** ${out_data['total_treasury_tvl']/1e9:,.2f} Billion\n\n")
        f.write("## Top 15 DAO Treasuries\n\n")
        f.write("| DAO / Treasury | Chain | TVL (USD) | Symbol | URL |\n")
        f.write("|---|---|---|---|---|\n")
        for t in treasury_data:
            f.write(f"| {t['name']} | {t['chain']} | ${t['tvl']/1e6:,.1f}M | {t['symbol']} | {t['url']} |\n")
            
        f.write("\n## Strategic Intelligence\n")
        f.write("> **Copilot Action:** Target the DAOs listed above for the `x402 Treasury Yield Router` pitch. These entities possess massive idle capital and stand to gain the most from automated risk-adjusted yield discovery.\n")

    print(f"📄 Report saved to {report_file}")

if __name__ == "__main__":
    main()
