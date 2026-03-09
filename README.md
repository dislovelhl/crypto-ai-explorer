# 🔍 CryptoAI Explorer

**Open-source AI agent intelligence toolkit for crypto opportunities**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)

> Revenue-first approach: Bounties → Grants → x402 Services → Platform

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CryptoAI Explorer                        │
│                                                             │
│  ┌─── Data Layer ──────────────────────────────────────┐    │
│  │  Superteam API  │  Forum APIs  │  DefiLlama  │ CG   │    │
│  └──────┬──────────┴──────┬───────┴──────┬──────┴──┬───┘    │
│         │                 │              │         │         │
│  ┌─── Scanners ────────────────────────────────────────┐    │
│  │  bounty_monitor  │  arb_gov  │  op_gov  │  yields  │    │
│  │  token_tracker   │  grants   │  analyzer │          │    │
│  └──────┬──────────────────┬────────────────┬──────────┘    │
│         │                  │                │               │
│  ┌─── Services ────────────────────────────────────────┐    │
│  │  x402 API (FastAPI)  │  Telegram Bot  │  MCP Server │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─── Intelligence ───────────────────────────────────┐    │
│  │  Opportunity Dashboard  │  Competitive Analyzer     │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## ⚡ Quick Start

```bash
# Clone and install
git clone https://github.com/YOUR_USER/crypto-ai-explorer.git
cd crypto-ai-explorer
pip install -r requirements.txt

# Run full scan (all 8 scanners)
bash scripts/run_full_scan.sh

# Or run individual scanners
python3 scripts/superteam_monitor.py          # Bounty tracking
python3 scripts/arbitrum_governance_scanner.py # Arbitrum DAO intel
python3 scripts/optimism_governance_scanner.py # Optimism DAO intel
python3 scripts/defi_yield_scanner.py          # DeFi yields
python3 scripts/agent_token_tracker.py         # AI token market
python3 scripts/superteam_grants_scanner.py    # Grant programs
python3 scripts/bounty_competitive_analyzer.py # Competition analysis
python3 scripts/opportunity_dashboard.py       # Consolidated dashboard

# Set up daily cron (09:00-10:30 UTC)
bash scripts/cron_setup.sh

# Start x402 API server
uvicorn services.x402-api.server:app --port 8402

# Test Telegram bot (CLI mode)
python3 services/governance-bot/bot.py --test

# Test MCP server
python3 services/mcp-server/server.py --test
```

## 📊 Live Data Snapshot

| Metric | Value |
|--------|-------|
| DeFi pools scanned | 19,200+ |
| Bounties tracked | 39 (12 AGENT_ALLOWED) |
| AGENT_ALLOWED prize pool | $30,508 |
| Grant programs found | 39 active ($97,938 total) |
| AI-relevant grants | 8 |
| DAO forums monitored | 2 (Arbitrum + Optimism) |
| AI agent token market | $2.65B |
| Best yield (stablecoin) | Avantis/Base USDC 10.5% ($83M TVL) |
| Best bounty opportunity | TokenTon26 DeFi $8,500 (11 subs, $708/sub) |

## 🔧 Scanners

### 1. Superteam Bounty Monitor (`superteam_monitor.py`)
Tracks all bounties on Superteam Earn with focus on `AGENT_ALLOWED` bounties that AI agents can legitimately complete. Detects new opportunities and sends alerts.

### 2. Arbitrum Governance Scanner (`arbitrum_governance_scanner.py`)
Monitors `forum.arbitrum.foundation` for AI-related proposals, grant discussions, and governance activity. Generates structured digests.

### 3. Optimism Governance Scanner (`optimism_governance_scanner.py`)
Monitors `gov.optimism.io` — confirmed Season 9 Grants Council applications are LIVE.

### 4. DeFi Yield Scanner (`defi_yield_scanner.py`)
Scans 19,200+ DeFi pools via DefiLlama. Filters for stablecoin pools, risk-scores by protocol reputation and TVL.

### 5. Agent Token Tracker (`agent_token_tracker.py`)
Tracks AI agent token market via CoinGecko. Provides sentiment analysis and tokenization timing signals.

### 6. Superteam Grants Scanner (`superteam_grants_scanner.py`)
Discovers active grant programs across 20+ Superteam regional chapters. Identifies low-competition opportunities.

### 7. Bounty Competitive Analyzer (`bounty_competitive_analyzer.py`)
Cross-references reward amounts, submission counts, and deadlines to rank bounties by reward-per-submission ratio.

### 8. Opportunity Dashboard (`opportunity_dashboard.py`)
Consolidates all scanner data into a single ranked action list with strategic recommendations.

## 🌐 Services

### x402 Pay-Per-Call API
FastAPI server with 4 monetizable endpoints:

```bash
# Governance summary
curl http://localhost:8402/api/governance/summary?dao=arbitrum

# Top yields
curl http://localhost:8402/api/yields/top?min_tvl=10000000

# Token analysis
curl http://localhost:8402/api/token/analysis?token_id=virtual-protocol

# Treasury health
curl http://localhost:8402/api/treasury/health?dao=arbitrum
```

### Telegram Bot
5 commands: `/digest`, `/yields`, `/tokens`, `/bounties`, `/help`

```bash
export TELEGRAM_BOT_TOKEN="your-token-from-botfather"
python3 services/governance-bot/bot.py
```

### MCP Server (Claude/Cursor Integration)
5 tools: `governance_digest`, `top_yields`, `agent_bounties`, `token_analysis`, `agent_market_overview`

Add to `~/.config/claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "cryptoai-explorer": {
      "command": "python3",
      "args": ["/path/to/services/mcp-server/server.py"]
    }
  }
}
```

## 💰 Grant Applications

| Grant | Amount | Status | Application |
|-------|--------|--------|-------------|
| Arbitrum Trailblazer | Up to $1M fund | Draft ready | `grants/arbitrum_trailblazer_application.md` |
| Optimism Season 9 | $10,000 | ✅ CONFIRMED LIVE | `grants/optimism-s9/application.md` |
| Gitcoin GG24 AI | QF matching | Draft ready | `grants/gitcoin-gg24/ai_public_goods_application.md` |
| Solana Foundation | $0-10,000 | Active via Superteam | `grants/solana-foundation/application.md` |

## 🎯 Active Bounty Submissions

| Bounty | Reward | Competition | Submission |
|--------|--------|-------------|------------|
| Bungee Incognito Deep Dive | $300 | 2 submissions | `bounties/bungee/` |
| TokenTon26 AI Track | $8,500 | 14 submissions | `bounties/tokenton26/` |

## 📚 Binance Skills Hub Skills

5 skills in `skills/binance-hub/`:
- **DeFi Yield Scanner** — Stablecoin yield discovery
- **Governance Analyzer** — Multi-DAO governance monitoring
- **Token Analyzer** — Token fundamental analysis
- **Bounty Scanner** — AGENT_ALLOWED bounty discovery
- **Whale Tracker** — Large wallet movement monitoring

## 🐳 Docker Deployment

```bash
# Start x402 API + Telegram bot
docker-compose up -d

# Or just the API
docker build -t cryptoai-explorer .
docker run -p 8402:8402 cryptoai-explorer
```

## 📈 Revenue Strategy

```
Phase 1 (Now)     → Bounty submissions ($300-$8,500 per win)
Phase 2 (Week 2)  → Grant applications ($1K-$100K)
Phase 3 (Week 3)  → x402 API on Base (recurring revenue)
Phase 4 (Month 2) → Platform + subscriptions
```

**Why revenue-first?** AI agent token market is down 87% from ATH (VIRTUAL $5.07→$0.63). Service revenue is safer than token speculation.

## 🛠️ Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run all scanners
bash scripts/run_full_scan.sh

# Test services
python3 services/governance-bot/bot.py --test
python3 services/mcp-server/server.py --test
uvicorn services.x402-api.server:app --port 8402

# Set up daily automation
bash scripts/cron_setup.sh
```

## 📄 License

MIT — Use freely, attribution appreciated.
