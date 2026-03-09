#!/usr/bin/env python3
"""
Superteam Earn AGENT_ALLOWED Bounty Monitor
Continuously monitors for new agent-completable bounties.
Saves results to data/ and prints actionable alerts.
"""

import json
import sys
import os
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

SUPERTEAM_API = "https://earn.superteam.fun/api/listings/"
BOUNTY_HISTORY_FILE = DATA_DIR / "superteam_bounties.json"
ALERT_FILE = DATA_DIR / "superteam_alerts.json"


def fetch_bounties(take: int = 100) -> list[dict]:
    """Fetch all open bounties from Superteam Earn API."""
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        resp = client.get(f"{SUPERTEAM_API}?take={take}&type=bounty")
        resp.raise_for_status()
        return resp.json()


def analyze_bounties(bounties: list[dict]) -> dict:
    """Analyze bounties and categorize by agent access and opportunity quality."""
    agent_allowed = []
    ai_related = []
    high_value = []
    low_competition = []

    ai_keywords = ["ai", "agent", "llm", "gpt", "automat", "bot", "intellig", "machine learn"]

    for b in bounties:
        if b.get("status") != "OPEN":
            continue

        title = b.get("title", "")
        reward = b.get("rewardAmount", 0) or 0
        deadline = b.get("deadline", "")
        token = b.get("token", "")
        access = b.get("agentAccess", "HUMAN_ONLY")
        subs = b.get("_count", {}).get("Submission", 0)
        sponsor = b.get("sponsor", {}).get("name", "")
        slug = b.get("slug", "")
        is_ai = any(k in title.lower() for k in ai_keywords)

        entry = {
            "title": title,
            "reward": reward,
            "token": token,
            "deadline": deadline[:10] if deadline else "",
            "agent_access": access,
            "submissions": subs,
            "sponsor": sponsor,
            "slug": slug,
            "url": f"https://earn.superteam.fun/listings/{slug}/",
            "is_ai_related": is_ai,
            "competition_ratio": round(subs / max(reward, 1) * 1000, 2),
        }

        if access == "AGENT_ALLOWED":
            agent_allowed.append(entry)
        if is_ai:
            ai_related.append(entry)
        if reward >= 5000:
            high_value.append(entry)
        if subs <= 15 and reward >= 100:
            low_competition.append(entry)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_open": len([b for b in bounties if b.get("status") == "OPEN"]),
        "agent_allowed": sorted(agent_allowed, key=lambda x: x["reward"], reverse=True),
        "ai_related": sorted(ai_related, key=lambda x: x["reward"], reverse=True),
        "high_value": sorted(high_value, key=lambda x: x["reward"], reverse=True),
        "low_competition": sorted(low_competition, key=lambda x: x["submissions"]),
    }


def detect_new_opportunities(current: dict) -> list[dict]:
    """Compare with previous scan to detect new opportunities."""
    alerts = []
    if BOUNTY_HISTORY_FILE.exists():
        with open(BOUNTY_HISTORY_FILE) as f:
            previous = json.load(f)
        prev_slugs = {b["slug"] for b in previous.get("agent_allowed", [])}
        for b in current["agent_allowed"]:
            if b["slug"] not in prev_slugs:
                alerts.append({
                    "type": "NEW_AGENT_BOUNTY",
                    "bounty": b,
                    "message": f"🆕 New AGENT_ALLOWED bounty: ${b['reward']} {b['token']} — {b['title']}",
                })
    return alerts


def print_report(analysis: dict, alerts: list[dict]) -> None:
    """Print formatted report to stdout."""
    print("=" * 80)
    print(f"🔍 SUPERTEAM BOUNTY MONITOR — {analysis['timestamp']}")
    print(f"   Total open bounties: {analysis['total_open']}")
    print("=" * 80)

    if alerts:
        print("\n🚨 NEW ALERTS:")
        for a in alerts:
            print(f"  {a['message']}")

    print(f"\n🟢 AGENT_ALLOWED BOUNTIES ({len(analysis['agent_allowed'])} found):")
    print(f"  {'Reward':>8} {'Token':<5} | {'Deadline':<10} | {'Subs':>4} | {'Title'}")
    print(f"  {'-' * 75}")
    for b in analysis["agent_allowed"]:
        print(f"  ${b['reward']:>6} {b['token']:<5} | {b['deadline']:<10} | {b['submissions']:>4} | {b['title'][:55]}")

    print(f"\n🤖 AI-RELATED BOUNTIES ({len(analysis['ai_related'])} found):")
    for b in analysis["ai_related"]:
        access = "🟢 AGENT" if b["agent_access"] == "AGENT_ALLOWED" else "🔒 HUMAN"
        print(f"  ${b['reward']:>6} {b['token']:<5} | {access} | {b['submissions']:>4} subs | {b['title'][:55]}")

    print(f"\n🎯 LOW COMPETITION OPPORTUNITIES (≤15 subs, ≥$100):")
    for b in analysis["low_competition"][:10]:
        access = "🟢" if b["agent_access"] == "AGENT_ALLOWED" else "🔒"
        print(f"  ${b['reward']:>6} {b['token']:<5} | {access} | {b['submissions']:>4} subs | {b['title'][:55]}")

    # Summary stats
    total_agent_pool = sum(b["reward"] for b in analysis["agent_allowed"])
    avg_competition = (
        sum(b["submissions"] for b in analysis["agent_allowed"]) / max(len(analysis["agent_allowed"]), 1)
    )
    print(f"\n📊 SUMMARY:")
    print(f"  Total AGENT_ALLOWED prize pool: ${total_agent_pool:,.0f}")
    print(f"  Average competition (agent bounties): {avg_competition:.0f} submissions")
    print(f"  Best opportunity: {analysis['agent_allowed'][0]['title'][:60] if analysis['agent_allowed'] else 'None'}")


def main():
    print("Fetching Superteam bounties...")
    bounties = fetch_bounties(100)
    analysis = analyze_bounties(bounties)
    alerts = detect_new_opportunities(analysis)

    # Save current state
    with open(BOUNTY_HISTORY_FILE, "w") as f:
        json.dump(analysis, f, indent=2)

    if alerts:
        with open(ALERT_FILE, "w") as f:
            json.dump(alerts, f, indent=2)

    print_report(analysis, alerts)

    # Return exit code based on whether there are actionable alerts
    return 0 if not alerts else 1


if __name__ == "__main__":
    sys.exit(main())
