#!/usr/bin/env python3
"""
CryptoAI Opportunity Dashboard
Consolidated view of all opportunities across bounties, grants, yields, and tokens.
Cross-references data from all scanners to produce ranked action list.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)


def load_data(filename: str) -> dict:
    """Load scanner data file."""
    path = DATA_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def generate_dashboard() -> str:
    """Generate consolidated opportunity dashboard."""
    bounties = load_data("superteam_bounties.json")
    governance = load_data("arbitrum_governance_scan.json")
    yields = load_data("defi_yields.json")
    tokens = load_data("agent_tokens.json")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# 🎯 CryptoAI Opportunity Dashboard",
        f"**Generated**: {now}",
        "",
        "---",
        "",
    ]

    # === IMMEDIATE ACTIONS (next 48 hours) ===
    lines.extend([
        "## 🚨 IMMEDIATE ACTIONS (Next 48 Hours)",
        "",
    ])

    agent_bounties = bounties.get("agent_allowed", [])
    urgent_bounties = [b for b in agent_bounties if b.get("deadline", "9999") < "2026-03-15"]
    if urgent_bounties:
        lines.append("### Expiring Bounties")
        lines.append("| Bounty | Reward | Deadline | Subs | Action |")
        lines.append("|--------|--------|----------|------|--------|")
        for b in urgent_bounties:
            lines.append(
                f"| {b['title'][:45]} | ${b['reward']} {b['token']} | {b['deadline']} | {b['submissions']} | **SUBMIT NOW** |"
            )
        lines.append("")

    # === BOUNTY OPPORTUNITIES ===
    lines.extend([
        "## 💰 Bounty Opportunities",
        "",
        f"**Total AGENT_ALLOWED**: {len(agent_bounties)} bounties",
        f"**Total Prize Pool**: ${sum(b.get('reward', 0) for b in agent_bounties):,.0f}",
        "",
    ])

    # Priority ranking
    for b in agent_bounties:
        # Score: high reward + low competition = best
        reward = b.get("reward", 0)
        subs = b.get("submissions", 0)
        b["priority_score"] = reward / max(subs, 1)

    agent_bounties.sort(key=lambda x: x["priority_score"], reverse=True)

    lines.append("### Ranked by Reward-to-Competition Ratio")
    lines.append("| Priority | Bounty | Reward | Subs | Score | Deadline |")
    lines.append("|----------|--------|--------|------|-------|----------|")
    for i, b in enumerate(agent_bounties[:10], 1):
        emoji = "🔴" if i <= 3 else "🟡" if i <= 6 else "⚪"
        lines.append(
            f"| {emoji} #{i} | {b['title'][:40]} | ${b['reward']} | {b['submissions']} | {b['priority_score']:.0f} | {b['deadline']} |"
        )
    lines.append("")

    # === GOVERNANCE INTEL ===
    lines.extend([
        "## 🏛️ Governance Intelligence",
        "",
    ])

    categorized = governance.get("categorized", {})
    ai_topics = categorized.get("ai_related", [])
    grant_topics = categorized.get("grant_related", [])

    if ai_topics:
        lines.append("### AI-Related Governance Topics")
        for t in ai_topics[:5]:
            lines.append(f"- **{t['title'][:60]}** — {t['views']} views, {t['posts_count']} posts — [link]({t['url']})")
        lines.append("")

    if grant_topics:
        lines.append("### Grant & Funding Topics")
        for t in grant_topics[:5]:
            lines.append(f"- **{t['title'][:60]}** — {t['views']} views — [link]({t['url']})")
        lines.append("")

    # === YIELD OPPORTUNITIES ===
    lines.extend([
        "## 📊 Top Yield Opportunities",
        "",
    ])

    top_yields = yields.get("top_30", [])
    if top_yields:
        lines.append(f"**Pools scanned**: {yields.get('total_pools', 0):,}")
        lines.append(f"**Qualifying stablecoin pools**: {yields.get('stable_pools', 0)}")
        lines.append("")
        lines.append("| APY | Base APY | TVL | Chain | Protocol | Pool |")
        lines.append("|-----|----------|-----|-------|----------|------|")
        for p in top_yields[:10]:
            apy = p.get("apy", 0) or 0
            apy_base = p.get("apyBase", 0) or 0
            tvl = (p.get("tvlUsd", 0) or 0) / 1e6
            lines.append(
                f"| {apy:.1f}% | {apy_base:.1f}% | ${tvl:.1f}M | {p.get('chain', '')} | {p.get('project', '')} | {p.get('symbol', '')} |"
            )
        lines.append("")

    # === TOKEN MARKET ===
    lines.extend([
        "## 🪙 AI Agent Token Market",
        "",
    ])

    if tokens:
        total_mcap = tokens.get("total_market_cap", 0)
        avg_change = tokens.get("avg_change_24h", 0)
        sentiment = tokens.get("sentiment", "?")
        signal = tokens.get("tokenization_signal", "?")

        lines.append(f"- **Total Market Cap**: ${total_mcap/1e9:.2f}B")
        lines.append(f"- **24h Change**: {avg_change:+.2f}%")
        lines.append(f"- **Sentiment**: {sentiment}")
        lines.append(f"- **Tokenization Signal**: {signal}")
        lines.append("")

        top_tokens = tokens.get("top_tokens", [])
        if top_tokens:
            lines.append("| Token | Price | MCap | 24h | Trending |")
            lines.append("|-------|-------|------|-----|----------|")
            for t in top_tokens[:8]:
                mcap = (t.get("market_cap", 0) or 0) / 1e6
                change = t.get("change_24h", 0) or 0
                trend = "🔥" if t.get("is_trending") else ""
                lines.append(
                    f"| {t['name'][:20]} ({t['symbol']}) | ${t.get('price', 0):.4f} | ${mcap:.0f}M | {change:+.1f}% | {trend} |"
                )
        lines.append("")

    # === STRATEGIC RECOMMENDATIONS ===
    lines.extend([
        "## 🎯 Strategic Recommendations",
        "",
        "### This Week",
        "",
    ])

    # Generate dynamic recommendations
    recs = []
    if urgent_bounties:
        recs.append(f"1. **URGENT**: Submit to {len(urgent_bounties)} expiring bounties before deadlines")
    if agent_bounties:
        best = agent_bounties[0]
        recs.append(f"2. **HIGH EV**: Submit to '{best['title'][:40]}' (${best['reward']}, only {best['submissions']} subs)")
    if ai_topics:
        recs.append(f"3. **ENGAGE**: Participate in '{ai_topics[0]['title'][:50]}' on Arbitrum forum")
    if tokens and tokens.get("tokenization_signal", "").startswith("⚠"):
        recs.append("4. **AVOID**: Do NOT launch tokens — market conditions unfavorable")
    recs.append("5. **APPLY**: Submit Arbitrum Trailblazer AI Grant application")
    recs.append("6. **BUILD**: Deploy x402 governance analysis endpoint on Base")

    for r in recs:
        lines.append(r)

    lines.extend([
        "",
        "---",
        f"*Dashboard generated from {sum(1 for f in DATA_DIR.glob('*.json'))} data sources*",
    ])

    return "\n".join(lines)


def main():
    print("🎯 Generating Opportunity Dashboard...")
    dashboard = generate_dashboard()

    # Save report
    report_file = REPORT_DIR / f"dashboard_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, "w") as f:
        f.write(dashboard)
    print(f"✅ Dashboard saved to {report_file}")

    # Also print to stdout
    print()
    print(dashboard)


if __name__ == "__main__":
    main()
