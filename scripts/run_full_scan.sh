#!/bin/bash
# Full CryptoAI Explorer Scan
# Runs all scanners and generates consolidated report

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🔍 CryptoAI Explorer — Full Scan                          ║"
echo "║  $(date '+%Y-%m-%d %H:%M:%S %Z')                                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Superteam Bounty Monitor
echo "━━━ [1/4] Superteam Bounty Monitor ━━━"
python3 "$SCRIPT_DIR/superteam_monitor.py" || true
echo ""

# 2. Arbitrum Governance Scanner
echo "━━━ [2/4] Arbitrum Governance Scanner ━━━"
python3 "$SCRIPT_DIR/arbitrum_governance_scanner.py" || true
echo ""

# 3. DeFi Yield Scanner
echo "━━━ [3/4] DeFi Yield Scanner ━━━"
python3 "$SCRIPT_DIR/defi_yield_scanner.py" || true
echo ""

# 4. Agent Token Tracker
echo "━━━ [4/4] Agent Token Market Tracker ━━━"
python3 "$SCRIPT_DIR/agent_token_tracker.py" || true
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Full Scan Complete                                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Data files:"
ls -la "$PROJECT_DIR/data/" 2>/dev/null
echo ""
echo "📄 Reports:"
ls -la "$PROJECT_DIR/reports/" 2>/dev/null
