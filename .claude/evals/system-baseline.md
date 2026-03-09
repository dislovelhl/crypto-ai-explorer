## EVAL DEFINITION: system-baseline

### Capability Evals
1. **API Payment Gateway**: `/api/*` endpoints must return HTTP 402 (Payment Required) when no auth is provided.
2. **API Subscription Bypass**: `/api/*` endpoints must return HTTP 200 when a valid `X-API-Key` is provided.
3. **Data Room Compilation**: `build_data_room.py` must successfully compile markdown pitches into a single `docs/data-room.html` file.
4. **Agent Wallet Generation**: `agent_wallet.py` must generate a valid EVM address and save it to the ignored `data/agent_wallet.json` file.
5. **MCP Server Health**: `services/mcp-server/server.py --test` must exit cleanly with code 0.

### Regression Evals
1. **Directory Structure**: Essential directories (`scripts/`, `services/`, `data/`, `reports/`) must exist.
2. **Scanner Syntax**: All python files in `scripts/` must pass a basic syntax/compilation check.

### Success Metrics
- pass@1: 100% for regression evals (must not break).
- pass@1: > 80% for capability evals.
