#!/usr/bin/env python3
"""
Bounty Competitive Analyzer
Analyzes competition levels for AGENT_ALLOWED bounties and recommends actions.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def main():
    now = datetime.now(timezone.utc)
    print(f"🏆 Bounty Competitive Analyzer — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    bounty_file = DATA_DIR / "superteam_bounties.json"
    if not bounty_file.exists():
        print("❌ No bounty data found. Run superteam_monitor.py first.")
        sys.exit(1)

    with open(bounty_file) as f:
        data = json.load(f)

    agent_bounties = data.get("agent_allowed", [])
    if not agent_bounties:
        print("❌ No AGENT_ALLOWED bounties found in data.")
        sys.exit(1)

    print(f"📋 Analyzing {len(agent_bounties)} AGENT_ALLOWED bounties\n")

    analysis = []

    for b in agent_bounties:
        reward = b.get("reward", 0) or 0
        subs = b.get("submissions", 0) or 0
        deadline = b.get("deadline", "")
        title = b.get("title", "")

        # Calculate days until deadline
        days_left = 999
        if deadline:
            try:
                dl = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                days_left = (dl - now).days
            except (ValueError, TypeError):
                pass

        # Reward per submission (higher = less competition per dollar)
        reward_per_sub = reward / max(subs + 1, 1)  # +1 for yourself

        # Competition score (lower = better opportunity)
        # Factors: more subs = worse, less reward = worse, less time = worse
        competition_score = (subs * 10) - (reward / 100) - (min(days_left, 30) * 2)

        # Recommendation
        if days_left <= 0:
            action = "EXPIRED"
        elif days_left <= 2 and subs < 5:
            action = "🔴 SUBMIT NOW — expiring, low competition"
        elif days_left <= 2:
            action = "🟡 RUSH — expiring soon"
        elif reward_per_sub >= 200 and subs < 20:
            action = "🟢 STRONG — high reward/competition ratio"
        elif reward_per_sub >= 50:
            action = "🟡 CONSIDER — moderate opportunity"
        elif subs > 50:
            action = "⚪ SKIP — too competitive"
        else:
            action = "🟡 EVALUATE — needs more analysis"

        entry = {
            "title": title,
            "reward": reward,
            "token": b.get("token", ""),
            "submissions": subs,
            "deadline": deadline[:10] if deadline else "",
            "days_left": days_left,
            "reward_per_sub": round(reward_per_sub, 1),
            "competition_score": round(competition_score, 1),
            "action": action,
        }
        analysis.append(entry)

    # Sort by reward_per_sub (best opportunities first)
    analysis.sort(key=lambda x: x["reward_per_sub"], reverse=True)

    # Print ranked table
    print(f"{'#':>2} {'Action':<45} {'Reward':>8} {'Subs':>5} {'$/Sub':>8} {'Days':>5} {'Title':<40}")
    print("-" * 120)

    for i, a in enumerate(analysis, 1):
        print(
            f"{i:>2} {a['action']:<45} ${a['reward']:>7,.0f} {a['submissions']:>5} "
            f"${a['reward_per_sub']:>7,.0f} {a['days_left']:>5} {a['title'][:40]}"
        )

    # Summary stats
    submit_now = [a for a in analysis if "SUBMIT NOW" in a["action"]]
    strong = [a for a in analysis if "STRONG" in a["action"]]
    consider = [a for a in analysis if "CONSIDER" in a["action"]]

    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"  🔴 Submit NOW: {len(submit_now)} bounties")
    print(f"  🟢 Strong opportunities: {len(strong)} bounties")
    print(f"  🟡 Worth considering: {len(consider)} bounties")
    print(f"  Total addressable prize: ${sum(a['reward'] for a in analysis if 'SKIP' not in a['action']):,.0f}")

    if submit_now:
        print(f"\n🚨 URGENT — Submit these before they expire:")
        for a in submit_now:
            print(f"  ${a['reward']:>6} | {a['days_left']}d left | {a['submissions']} subs | {a['title'][:55]}")

    if strong:
        print(f"\n💎 BEST OPPORTUNITIES:")
        for a in strong:
            print(f"  ${a['reward']:>6} | {a['days_left']}d left | {a['submissions']} subs | ${a['reward_per_sub']:.0f}/sub | {a['title'][:45]}")

    # Save
    output = {
        "timestamp": now.isoformat(),
        "total_analyzed": len(analysis),
        "submit_now": len(submit_now),
        "strong": len(strong),
        "analysis": analysis,
    }

    out_file = DATA_DIR / "bounty_analysis.json"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n💾 Analysis saved to {out_file}")


if __name__ == "__main__":
    main()
