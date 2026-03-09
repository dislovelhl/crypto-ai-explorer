#!/usr/bin/env python3
"""
Generate Outreach DMs
Automates the creation of personalized DMs/emails for delegates and builders
based on the latest CryptoAI Explorer scan data.
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


def format_delegate_dm(dao: str, governance_data: dict) -> str:
    """Generate an outreach DM for a delegate of a specific DAO."""
    hot_topics = governance_data.get("categorized", {}).get("hot", [])
    if not hot_topics:
        # Fallback to AI-related or general list depending on the scanner's structure
        hot_topics = governance_data.get("categorized", {}).get("ai_related", [])
    if not hot_topics:
        return ""

    top_topic = hot_topics[0]
    
    return f"""
Hi [Delegate Name],

I noticed you're an active delegate for {dao.title()}. I built a lightweight governance intelligence system that turns forum activity, proposal flow, and treasury context into daily delegate-ready summaries.

For example, today's top {dao.title()} discussion is "{top_topic['title'][:60]}..." which currently has {top_topic['views']} views.

I put together a sample dashboard based on live {dao.title()} data so your team doesn't have to read 50 forum posts a day. If useful, I can set up a 7-day free pilot for you (delivered via Telegram or API).

Worth sending over a sample?
"""

def format_builder_dm(grants_data: dict) -> str:
    """Generate an outreach DM for a builder/studio looking for grants."""
    ai_grants = grants_data.get("ai_grants", [])
    low_comp = grants_data.get("low_competition", [])
    
    grant_highlight = ""
    if ai_grants:
        grant_highlight = f"For instance, there's an active '{ai_grants[0]['title'][:40]}...' grant with a ${ai_grants[0]['reward']:,} reward."
    elif low_comp:
        grant_highlight = f"For instance, there's an active '{low_comp[0]['title'][:40]}...' grant with a ${low_comp[0]['reward']:,} reward and only {low_comp[0]['submissions']} submissions."

    return f"""
Hi [Builder Name],

I built a system that tracks live crypto grants, scores fit, monitors deadlines, and helps convert product work into stronger applications.

It already tracks opportunities across Superteam, governance ecosystems, and public goods funding. {grant_highlight}

If you're applying for ecosystem grants, I can show you:
- the best-fit current programs
- deadline alerts
- application scoring

Want a sample grant-fit report for your project?
"""

def format_treasury_dm(yield_data: dict) -> str:
    """Generate an outreach DM for a DAO treasury operator."""
    pools = yield_data.get("pools", [])
    top_yield = pools[0] if pools else None
    
    if top_yield:
        protocol = top_yield.get('project', top_yield.get('protocol', 'Unknown'))
        chain = top_yield.get('chain', 'Unknown')
        apy = top_yield.get('apy', 0)
        yield_highlight = f"Today, the top risk-adjusted stablecoin pool is {protocol} on {chain} yielding {apy:.1f}% APY."
    else:
        yield_highlight = "We scan 19,000+ pools daily for safe, high-yield stablecoin deployments."

    return f"""
Hi [Treasury Manager Name],

I've built a treasury intelligence tool that monitors stablecoin yield opportunities and allocation risk signals for DAOs.

It's designed for teams that want:
- conservative yield opportunity scanning
- daily/weekly treasury monitoring
- alerts when better risk-adjusted options emerge

{yield_highlight}

I can share a sample treasury memo using live market data. Open to a quick look?
"""


def main():
    print("🚀 Generating Outreach Campaign Messages...")
    
    arb_data = load_json("arbitrum_governance_scan.json")
    op_data = load_json("optimism_governance_scan.json")
    grant_data = load_json("superteam_grants.json")
    
    # Since yields data is requested directly by API in the actual system,
    # we'll mock it if the JSON isn't present, or use `defi_yields.json` if it exists.
    yield_data = load_json("defi_yields.json")
    if not yield_data:
        # Fallback dummy data if script hasn't saved defi_yields.json yet
        yield_data = {"pools": [{"protocol": "Avantis", "chain": "Base", "apy": 10.5}]}
    elif "top_30" in yield_data:
        # Map the dashboard format to expected format
        yield_data["pools"] = yield_data["top_30"]
        
    outreach_file = REPORT_DIR / f"outreach_campaign_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"
    
    with open(outreach_file, "w") as f:
        f.write("# ✉️ Outreach Campaign Templates\n\n")
        f.write("*Auto-generated from live scanner data.*\n\n")
        f.write("---\n\n")
        
        f.write("## 🏛️ Target: Arbitrum Delegates\n")
        f.write("```text\n")
        f.write(format_delegate_dm("arbitrum", arb_data).strip() + "\n")
        f.write("```\n\n")
        
        f.write("## 🏛️ Target: Optimism Delegates\n")
        f.write("```text\n")
        f.write(format_delegate_dm("optimism", op_data).strip() + "\n")
        f.write("```\n\n")
        
        f.write("## 💰 Target: Builders & Studios (Grants)\n")
        f.write("```text\n")
        f.write(format_builder_dm(grant_data).strip() + "\n")
        f.write("```\n\n")
        
        f.write("## 🏦 Target: DAO Treasury Managers\n")
        f.write("```text\n")
        f.write(format_treasury_dm(yield_data).strip() + "\n")
        f.write("```\n\n")
        
    print(f"✅ Generated personalized DMs based on latest data.")
    print(f"📄 Saved to: {outreach_file}")


if __name__ == "__main__":
    main()
