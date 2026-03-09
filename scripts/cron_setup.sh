#!/bin/bash
# Set up daily cron job for CryptoAI Explorer scans
# Run this once to install the cron schedule

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

# Create the cron entry
CRON_CMD="0 9 * * * cd $PROJECT_DIR && /usr/bin/python3 $SCRIPT_DIR/superteam_monitor.py >> $LOG_DIR/superteam.log 2>&1
30 9 * * * cd $PROJECT_DIR && /usr/bin/python3 $SCRIPT_DIR/arbitrum_governance_scanner.py >> $LOG_DIR/arbitrum.log 2>&1
0 10 * * * cd $PROJECT_DIR && /usr/bin/python3 $SCRIPT_DIR/defi_yield_scanner.py >> $LOG_DIR/yields.log 2>&1
30 10 * * * cd $PROJECT_DIR && /usr/bin/python3 $SCRIPT_DIR/agent_token_tracker.py >> $LOG_DIR/tokens.log 2>&1"

echo "Adding cron jobs for CryptoAI Explorer..."
echo ""
echo "Schedule (UTC):"
echo "  09:00 — Superteam bounty monitor"
echo "  09:30 — Arbitrum governance scanner"
echo "  10:00 — DeFi yield scanner"
echo "  10:30 — Agent token tracker"
echo ""

# Add to crontab (preserving existing entries)
(crontab -l 2>/dev/null | grep -v "crypto-ai-explorer"; echo "$CRON_CMD") | crontab -

echo "✅ Cron jobs installed. Verify with: crontab -l"
echo "📁 Logs will be saved to: $LOG_DIR/"
