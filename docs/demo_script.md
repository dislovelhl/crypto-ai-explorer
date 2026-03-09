# CryptoAI Treasury & Governance Copilot — Demo Script

**Target Length**: 3 minutes
**Format**: Screen recording (Loom)
**Visuals**: Terminal outputs, API JSON responses, Markdown dashboards
**Goal**: Prove immediate utility for TokenTon26 AI Track and Optimism S9 Grant reviewers.

---

### [0:00 - 0:30] The Hook (The Problem)

*(Screen: Empty Terminal)*

**Speaker:**
"Hi, I'm building CryptoAI Copilot. 
Right now, delegates are drowning in governance forum posts. DAO treasuries are leaving millions of dollars in stablecoins earning zero yield. And builders are missing out on active grant funding because the information is too fragmented to track. 

This isn't just an analytics problem. It's an execution problem. 
I built an AI-native intelligence layer to fix this. Let me show you what it does."

### [0:30 - 1:15] Demo 1: The Operator Dashboard (Human Interface)

*(Screen: Split screen, running `./scripts/run_full_scan.sh` on the left, opening `reports/dashboard_YYYYMMDD.md` on the right)*

**Speaker:**
"Every day, my Python orchestrator scans forum APIs across Arbitrum and Optimism, 19,000 liquidity pools on DefiLlama, and active bounty networks. 

It synthesizes this raw data into an Opportunity Dashboard. 
Here, we see immediate actions ranked by Expected Value. It flags expiring bounties, highlights the highest stablecoin yields adjusting for protocol risk, and pulls the top AI-related governance proposals currently being debated. 

This gives a delegate or treasury manager a complete snapshot of where they need to act today, without reading 50 forum posts."

### [1:15 - 2:00] Demo 2: The Agent-to-Agent API (x402 / Machine Interface)

*(Screen: Running `curl -H "X-API-Key: test-key-123" http://localhost:8402/api/governance/summary?dao=optimism | jq`)*

**Speaker:**
"But humans shouldn't be the only ones reading this. 
I've deployed this intelligence as a monetized, x402-compliant FastAPI server. 

If you're building an autonomous agent—say, a treasury management bot on Base or TON—your agent can call our `/api/governance/summary` or `/api/yields/top` endpoints. 

Notice the middleware: if you hit this API without a valid API key or an L402 payment macaroon, it returns a 402 Payment Required with an invoice for 10 cents in USDC. We are building the data infrastructure for the agent economy."

*(Screen: Run a curl command without headers to show the `402 Payment Required` response)*

### [2:00 - 2:40] Demo 3: MCP & Telegram Bot (Integration)

*(Screen: Claude Desktop pulling the MCP tools list, or simply typing `/digest` in a Telegram bot window)*

**Speaker:**
"To make this instantly useful, the entire stack connects to Claude and Cursor via the Model Context Protocol (MCP). Your local LLM can natively query our intelligence network. 

And for non-technical users, it’s wrapped in a Telegram bot. A delegate can type `/yields` while on the go and instantly see where their DAO should be parking its idle capital."

### [2:40 - 3:00] The Ask / Conclusion

*(Screen: Open the `OPPORTUNITY_BRIEF.md` or Grant tracker)*

**Speaker:**
"The code is live, the data is flowing, and the APIs are working. 
We are using this infrastructure today to apply for the Optimism Season 9 Grants Council and to compete in TokenTon26. 

Thank you for watching. The repo is public, and the API is ready for integration."