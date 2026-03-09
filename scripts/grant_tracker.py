#!/usr/bin/env python3
"""
Grant Application Tracker
Tracks status of all grant applications and upcoming deadlines.
Maintains persistent state in data/grant_tracker.json.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
TRACKER_FILE = DATA_DIR / "grant_tracker.json"


def load_tracker() -> dict:
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {"applications": [], "last_updated": ""}


def save_tracker(data: dict):
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def init_applications() -> list[dict]:
    """Initialize with known applications."""
    return [
        {
            "id": "arb-trailblazer",
            "name": "Arbitrum Trailblazer AI Fund",
            "program": "Arbitrum Foundation",
            "amount_requested": 50000,
            "amount_currency": "ARB",
            "status": "DRAFT",
            "portal": "https://arbitrumfoundation.medium.com",
            "draft_file": "grants/arbitrum_trailblazer_application.md",
            "deadline": "2026-04-30",
            "submitted_date": None,
            "notes": "Need to validate portal URL and fill team details",
            "priority": 1,
        },
        {
            "id": "op-s9",
            "name": "Optimism Season 9 Grants Council",
            "program": "Optimism Collective",
            "amount_requested": 10000,
            "amount_currency": "USD",
            "status": "DRAFT",
            "portal": "https://app.opgrants.io",
            "draft_file": "grants/optimism-s9/application.md",
            "deadline": "2026-04-15",
            "submitted_date": None,
            "notes": "CONFIRMED LIVE — Topic #10599 on gov.optimism.io",
            "priority": 0,
        },
        {
            "id": "gitcoin-gg24",
            "name": "Gitcoin GG24 AI For Public Goods",
            "program": "Gitcoin",
            "amount_requested": 5000,
            "amount_currency": "USD",
            "status": "DRAFT",
            "portal": "https://grants.gitcoin.co",
            "draft_file": "grants/gitcoin-gg24/ai_public_goods_application.md",
            "deadline": "2026-04-30",
            "submitted_date": None,
            "notes": "Need public GitHub repo and live demo for QF matching",
            "priority": 1,
        },
        {
            "id": "solana-superteam",
            "name": "Solana Foundation via Superteam",
            "program": "Superteam",
            "amount_requested": 7500,
            "amount_currency": "USDG",
            "status": "DRAFT",
            "portal": "https://earn.superteam.fun/grants/",
            "draft_file": "grants/solana-foundation/application.md",
            "deadline": "2026-06-30",
            "submitted_date": None,
            "notes": "Choose regional chapter with least competition",
            "priority": 2,
        },
    ]


def display_tracker(data: dict):
    now = datetime.now(timezone.utc)
    apps = data["applications"]

    print(f"📋 Grant Application Tracker — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 80)

    # Sort by priority then deadline
    apps.sort(key=lambda x: (x.get("priority", 9), x.get("deadline", "9999")))

    status_emoji = {
        "DRAFT": "📝",
        "SUBMITTED": "📨",
        "UNDER_REVIEW": "🔍",
        "APPROVED": "✅",
        "REJECTED": "❌",
        "FOLLOW_UP": "📞",
    }

    total_requested = 0
    total_pending = 0

    for a in apps:
        emoji = status_emoji.get(a["status"], "❓")
        deadline = a.get("deadline", "")
        days_left = "?"
        if deadline:
            try:
                dl = datetime.fromisoformat(deadline + "T00:00:00+00:00")
                days_left = (dl - now).days
            except ValueError:
                pass

        amount = a.get("amount_requested", 0)
        total_requested += amount
        if a["status"] not in ("REJECTED", "APPROVED"):
            total_pending += amount

        print(f"\n{emoji} {a['name']}")
        print(f"   Program: {a['program']}")
        print(f"   Amount: ${amount:,} {a.get('amount_currency', '')}")
        print(f"   Status: {a['status']}")
        print(f"   Deadline: {deadline} ({days_left} days)")
        print(f"   Portal: {a.get('portal', '')}")
        print(f"   Draft: {a.get('draft_file', '')}")
        if a.get("notes"):
            print(f"   Notes: {a['notes']}")
        if a.get("submitted_date"):
            print(f"   Submitted: {a['submitted_date']}")

    print(f"\n{'=' * 80}")
    print(f"📊 Summary:")
    print(f"   Total applications: {len(apps)}")
    print(f"   Total requested: ${total_requested:,}")
    print(f"   Pending value: ${total_pending:,}")
    print(f"   Submitted: {sum(1 for a in apps if a['status'] == 'SUBMITTED')}")
    print(f"   Drafts: {sum(1 for a in apps if a['status'] == 'DRAFT')}")

    # Upcoming deadlines
    upcoming = [
        a for a in apps
        if a["status"] in ("DRAFT", "SUBMITTED")
        and a.get("deadline", "9999") < "2026-04-15"
    ]
    if upcoming:
        print(f"\n⏰ Upcoming deadlines (next 5 weeks):")
        for a in upcoming:
            print(f"   {a['deadline']} — {a['name']} ({a['status']})")


def main():
    if "--init" in sys.argv or not TRACKER_FILE.exists():
        data = {"applications": init_applications()}
        save_tracker(data)
        print("✅ Tracker initialized with 4 applications")
    else:
        data = load_tracker()

    if "--update" in sys.argv:
        # Update a specific application
        app_id = sys.argv[sys.argv.index("--update") + 1] if len(sys.argv) > sys.argv.index("--update") + 1 else None
        status = sys.argv[sys.argv.index("--status") + 1] if "--status" in sys.argv and len(sys.argv) > sys.argv.index("--status") + 1 else None
        if app_id and status:
            for a in data["applications"]:
                if a["id"] == app_id:
                    a["status"] = status
                    if status == "SUBMITTED":
                        a["submitted_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                    save_tracker(data)
                    print(f"✅ Updated {app_id} → {status}")
                    break
            else:
                print(f"❌ Application '{app_id}' not found")

    display_tracker(data)


if __name__ == "__main__":
    main()
