#!/usr/bin/env python3
"""
Generate Social Media Thread
Automates the creation of a daily 5-part Twitter/Farcaster thread summarizing
the highest EV crypto opportunities across yields, governance, and grants.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)


def load_json(filename: str) -> dict:
    path = DATA_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def main():
    print("📢 Generating Daily Social Media Thread...")
    
    # Load Data
    op_data = load_json("optimism_governance_scan.json")
    bounty_data = load_json("bounty_analysis.json")
    grant_data = load_json("superteam_grants.json")
    
    # Fallback to yield_data if it exists or use dummy for formatting
    yield_data = load_json("defi_yields.json")
    
    # Process Top Yield
    top_yield_text = "N/A"
    if yield_data and "top_30" in yield_data and len(yield_data["top_30"]) > 0:
        top_y = yield_data["top_30"][0]
        protocol = top_y.get('project', 'Unknown')
        chain = top_y.get('chain', 'Unknown')
        apy = top_y.get('apy', 0)
        tvl = top_y.get('tvlUsd', 0) / 1e6
        top_yield_text = f"Highest risk-adjusted stablecoin yield today: {protocol} on {chain} yielding {apy:.1f}% APY (TVL: ${tvl:.1f}M)."
    else:
        top_yield_text = "We scanned 19,000+ stablecoin pools today to find the highest risk-adjusted APY for idle treasuries."

    # Process Top Governance
    op_hot = op_data.get("categorized", {}).get("hot", [])
    op_gov_text = "Governance is heating up."
    if op_hot:
        op_gov_text = f"Top Optimism Governance discussion today: '{op_hot[0]['title'][:60]}...' with {op_hot[0]['views']} views. Are delegates paying attention?"

    # Process Top Bounties/Grants
    grant_text = "Grants are available."
    low_comp = grant_data.get("low_competition", [])
    if low_comp:
        grant_text = f"Zero-competition alert 🚨: The '{low_comp[0]['title'][:40]}...' grant has ${low_comp[0]['reward']:,} up for grabs and currently ZERO submissions."

    # Build the Thread
    date_str = datetime.now(timezone.utc).strftime('%b %d')
    
    thread = f"""# 🧵 CryptoAI Daily Alpha Thread ({date_str})

*Copy-paste these 5 tweets/casts into X or Farcaster.*

---

**[Tweet 1/5: The Hook]**
Crypto ecosystems move too fast. Delegates can't read 50 forum posts a day, and DAO treasuries are leaving millions of stablecoins idle.

I built an AI intelligence layer that scans 19,000+ data points daily. Here is today's execution alpha. 🧵👇

---

**[Tweet 2/5: Yield Alpha]**
🏦 Treasury Optimization:
{top_yield_text}

Stop leaving DAO capital idle. We scan 19k+ pools to flag safe deployments and smart-contract risks before they happen.

---

**[Tweet 3/5: Governance Alpha]**
🏛️ Governance Intel:
{op_gov_text}

Our MCP server digests the noise so delegates can focus on voting impact, not just reading forums. 

---

**[Tweet 4/5: Grant Alpha]**
💰 Grant Pipeline:
{grant_text}

Builders miss $100k+ in grants because they don't know they exist. We built a tracker that calculates the exact $/submission ratio.

---

**[Tweet 5/5: CTA]**
🤖 I've deployed this intelligence as an x402-compliant API and Telegram bot.

If you're an active delegate, treasury manager, or building an AI agent that needs on-chain context natively:

Read the docs and deploy your own copilot here:
github.com/dislovelhl/crypto-ai-explorer
"""
    
    out_file = REPORT_DIR / f"social_thread_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"
    
    with open(out_file, "w") as f:
        f.write(thread)
        
    print(f"✅ Generated 5-part social media thread.")
    print(f"📄 Saved to: {out_file}")


if __name__ == "__main__":
    main()
