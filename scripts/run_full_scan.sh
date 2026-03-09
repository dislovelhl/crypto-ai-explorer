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
echo "━━━ [1/6] Superteam Bounty Monitor ━━━"
python3 "$SCRIPT_DIR/superteam_monitor.py" || true
echo ""

# 2. Arbitrum Governance Scanner
echo "━━━ [2/6] Arbitrum Governance Scanner ━━━"
python3 "$SCRIPT_DIR/arbitrum_governance_scanner.py" || true
echo ""

# 3. Optimism Governance Scanner
echo "━━━ [3/6] Optimism Governance Scanner ━━━"
python3 "$SCRIPT_DIR/optimism_governance_scanner.py" || true
echo ""

# 4. DeFi Yield Scanner
echo "━━━ [4/6] DeFi Yield Scanner ━━━"
python3 "$SCRIPT_DIR/defi_yield_scanner.py" || true
echo ""

# 5. Agent Token Tracker
echo "━━━ [5/6] Agent Token Market Tracker ━━━"
python3 "$SCRIPT_DIR/agent_token_tracker.py" || true
echo ""

# 6. Opportunity Dashboard
echo "━━━ [6/6] Opportunity Dashboard ━━━"
python3 "$SCRIPT_DIR/opportunity_dashboard.py" || true
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
