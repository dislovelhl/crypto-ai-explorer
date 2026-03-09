#!/usr/bin/env python3
"""
Superteam Grants Scanner
Discovers active grant programs across Superteam's regional chapters.
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


def main():
    now = datetime.now(timezone.utc)
    print(f"🎓 Superteam Grants Scanner — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    with httpx.Client(timeout=30, follow_redirects=True) as client:
        resp = client.get(
            "https://earn.superteam.fun/api/listings",
            params={"take": 100, "type": "grant"},
        )
        resp.raise_for_status()
        grants = resp.json()

    print(f"📋 Total grants found: {len(grants)}")

    # Filter for active/open
    active = [g for g in grants if g.get("status") in ("OPEN", "ACTIVE", None)]
    print(f"✅ Active grants: {len(active)}")

    # Sort by reward
    active.sort(key=lambda x: x.get("rewardAmount", 0) or 0, reverse=True)

    print(f"\n{'Reward':>10} {'Token':<6} {'Subs':>5} {'Sponsor':<25} {'Title':<45}")
    print("-" * 95)

    total_pool = 0
    grant_data = []

    for g in active:
        reward = g.get("rewardAmount", 0) or 0
        token = g.get("token", "") or ""
        subs = g.get("_count", {}).get("Submission", 0)
        sponsor = g.get("sponsor", {}).get("name", "") if g.get("sponsor") else ""
        title = g.get("title", "")
        slug = g.get("slug", "")
        deadline = (g.get("deadline", "") or "")[:10]
        region = g.get("region", "")

        total_pool += reward

        entry = {
            "title": title,
            "reward": reward,
            "token": token,
            "submissions": subs,
            "sponsor": sponsor,
            "deadline": deadline,
            "region": region,
            "slug": slug,
            "url": f"https://earn.superteam.fun/listings/{slug}/" if slug else "",
            "agent_access": g.get("agentAccess", ""),
        }
        grant_data.append(entry)

        print(f"${reward:>9,.0f} {token:<6} {subs:>5} {sponsor:<25} {title[:45]}")

    # Identify AI-relevant grants
    ai_grants = [
        g for g in grant_data
        if any(k in g["title"].lower() for k in ["ai", "agent", "llm", "automat", "intellig", "bot"])
    ]

    # Low-competition opportunities
    low_comp = [g for g in grant_data if g["submissions"] < 10 and g["reward"] >= 100]

    print(f"\n📊 SUMMARY:")
    print(f"  Total active grants: {len(active)}")
    print(f"  Total funding pool: ${total_pool:,.0f}")
    print(f"  AI-relevant grants: {len(ai_grants)}")
    print(f"  Low-competition opportunities (<10 subs): {len(low_comp)}")

    if ai_grants:
        print(f"\n🤖 AI-RELEVANT GRANTS:")
        for g in ai_grants:
            print(f"  ${g['reward']:>8,.0f} | {g['submissions']:>3} subs | {g['title'][:60]}")

    if low_comp:
        print(f"\n🎯 LOW-COMPETITION OPPORTUNITIES:")
        for g in low_comp[:10]:
            print(f"  ${g['reward']:>8,.0f} | {g['submissions']:>3} subs | {g['title'][:60]}")

    # Save data
    scan = {
        "timestamp": now.isoformat(),
        "total_grants": len(active),
        "total_funding": total_pool,
        "ai_relevant": len(ai_grants),
        "grants": grant_data,
        "ai_grants": ai_grants,
        "low_competition": low_comp,
    }

    data_file = DATA_DIR / "superteam_grants.json"
    with open(data_file, "w") as f:
        json.dump(scan, f, indent=2)
    print(f"\n💾 Data saved to {data_file}")


if __name__ == "__main__":
    main()
