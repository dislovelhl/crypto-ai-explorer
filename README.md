# 🔍 CryptoAI Explorer

Autonomous crypto opportunity discovery and execution toolkit for AI agents.

## Quick Start

```bash
# Full scan — runs all 4 scanners
./scripts/run_full_scan.sh

# Individual scanners
python3 scripts/superteam_monitor.py       # Bounty monitoring
python3 scripts/arbitrum_governance_scanner.py  # Governance intel
python3 scripts/defi_yield_scanner.py       # DeFi yield opportunities
python3 scripts/agent_token_tracker.py      # AI token market data

# API server (x402 endpoints)
cd services/x402-api && python3 server.py   # http://localhost:8402
```

## Structure

```
crypto-ai-explorer/
├── scripts/                    # Scanner scripts
│   ├── superteam_monitor.py    # Superteam AGENT_ALLOWED bounty tracker
│   ├── arbitrum_governance_scanner.py  # Arbitrum forum intelligence
│   ├── defi_yield_scanner.py   # Stablecoin yield opportunities
│   ├── agent_token_tracker.py  # AI agent token market tracker
│   └── run_full_scan.sh        # Run all scanners
├── services/
│   └── x402-api/server.py      # FastAPI x402 pay-per-call endpoints
├── grants/
│   └── arbitrum_trailblazer_application.md  # Draft grant application
├── data/                       # Scanner output (JSON)
├── reports/                    # Generated intelligence reports (MD)
└── bounties/                   # Bounty submission workspace
```

## API Endpoints

| Endpoint | Price | Description |
|----------|-------|-------------|
| `GET /api/governance/summary` | $0.10 | DAO governance intelligence |
| `GET /api/yields/top` | $0.05 | Top stablecoin yields |
| `GET /api/token/analysis` | $0.10 | Token fundamental analysis |
| `GET /api/treasury/health` | $0.15 | DAO treasury health check |

## Live Data Sources

| Source | API | Auth | Status |
|--------|-----|------|--------|
| Superteam Earn | REST | None | ✅ Working |
| Arbitrum Forum | JSON | None | ✅ Working |
| Optimism Forum | JSON | None | ✅ Working |
| DefiLlama | REST | None | ✅ Working (19,200 pools) |
| CoinGecko | REST | None | ✅ Working (rate limited) |
| GitHub | REST | Optional | ✅ Working |

## Reports

- [Chinese Full Report](../acgs-main/crypto-ai-explorer-report-zh.md) — 1,191 lines, comprehensive analysis
- `reports/arbitrum_digest_YYYYMMDD.md` — Daily governance intel
- `reports/yield_report_YYYYMMDD.md` — Daily yield opportunities
