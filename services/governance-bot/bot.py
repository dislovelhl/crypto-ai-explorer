#!/usr/bin/env python3
"""
Governance Intelligence Telegram Bot
Multi-DAO governance monitoring with AI-powered analysis.

Supported DAOs: Arbitrum, Optimism
Commands:
  /start    — Welcome + help
  /digest   — Latest governance digest
  /search   — Search governance topics
  /yields   — Top stablecoin yields
  /tokens   — AI agent token market overview
  /alerts   — Configure alerts
  /help     — Command reference

Environment Variables:
  TELEGRAM_BOT_TOKEN  — Bot token from @BotFather
  LLM_API_KEY         — Optional: Claude/OpenAI API key for enhanced analysis
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx

# Optional telegram dependency
try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        ContextTypes,
        MessageHandler,
        filters,
    )
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    print("python-telegram-bot not installed. Run: pip install python-telegram-bot")
    print("Running in CLI-only mode for testing.")


FORUM_APIS = {
    "arbitrum": "https://forum.arbitrum.foundation",
    "optimism": "https://gov.optimism.io",
}

YIELDS_API = "https://yields.llama.fi/pools"
COINGECKO_API = "https://api.coingecko.com/api/v3"

AI_KEYWORDS = [
    "ai", "agent", "llm", "automat", "bot", "intellig", "agentic",
    "cognitive", "neural", "model", "copilot",
]


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


async def fetch_governance_digest(dao: str = "arbitrum", limit: int = 15) -> str:
    """Generate a governance digest for a DAO."""
    forum_url = FORUM_APIS.get(dao.lower())
    if not forum_url:
        return f"❌ Unsupported DAO: {dao}. Supported: {', '.join(FORUM_APIS.keys())}"

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(f"{forum_url}/latest.json")
        resp.raise_for_status()
        data = resp.json()

    topics = data.get("topic_list", {}).get("topics", [])[:limit]

    lines = [
        f"📋 **{dao.upper()} Governance Digest**",
        f"🕐 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]

    # Categorize
    ai_topics = []
    grant_topics = []
    hot_topics = []

    for t in topics:
        title = t.get("title", "")
        views = t.get("views", 0)
        posts = t.get("posts_count", 0)
        tid = t.get("id", 0)

        is_ai = any(k in title.lower() for k in AI_KEYWORDS)
        is_grant = any(k in title.lower() for k in ["grant", "fund", "budget", "treasury"])

        entry = f"  • [{views} 👁 | {posts} 💬] {title[:65]}"

        if is_ai:
            ai_topics.append(entry)
        if is_grant:
            grant_topics.append(entry)
        if views >= 200 or posts >= 10:
            hot_topics.append(entry)

    if ai_topics:
        lines.append("🤖 **AI-Related:**")
        lines.extend(ai_topics[:5])
        lines.append("")

    if grant_topics:
        lines.append("💰 **Grants & Funding:**")
        lines.extend(grant_topics[:5])
        lines.append("")

    lines.append("🔥 **Hot Topics:**")
    lines.extend(hot_topics[:8])

    return "\n".join(lines)


async def fetch_top_yields(limit: int = 10) -> str:
    """Get top stablecoin yields."""
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        resp = await client.get(YIELDS_API)
        resp.raise_for_status()
        pools = resp.json().get("data", [])

    stable = [
        p for p in pools
        if p.get("stablecoin", False)
        and (p.get("apy", 0) or 0) > 5
        and (p.get("tvlUsd", 0) or 0) > 1_000_000
    ]
    stable.sort(key=lambda x: x.get("apy", 0) or 0, reverse=True)

    lines = [
        "📊 **Top Stablecoin Yields**",
        f"🕐 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Scanned {len(pools):,} pools | {len(stable)} qualifying",
        "",
    ]

    for p in stable[:limit]:
        chain = p.get("chain", "")[:10]
        project = p.get("project", "")[:15]
        symbol = p.get("symbol", "")[:15]
        apy = p.get("apy", 0) or 0
        tvl = (p.get("tvlUsd", 0) or 0) / 1e6
        lines.append(f"  {apy:>6.1f}% | ${tvl:>6.1f}M | {chain} | {project} | {symbol}")

    return "\n".join(lines)


async def fetch_agent_tokens(limit: int = 10) -> str:
    """Get AI agent token market overview."""
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            f"{COINGECKO_API}/coins/markets",
            params={
                "vs_currency": "usd",
                "category": "ai-agents",
                "order": "market_cap_desc",
                "per_page": limit,
            },
        )
        resp.raise_for_status()
        tokens = resp.json()

    total_mcap = sum(t.get("market_cap", 0) or 0 for t in tokens)
    avg_change = sum(t.get("price_change_percentage_24h", 0) or 0 for t in tokens) / max(len(tokens), 1)

    sentiment = "🟢 BULLISH" if avg_change > 5 else "🟡 NEUTRAL" if avg_change > -3 else "🔴 BEARISH"

    lines = [
        "🪙 **AI Agent Token Market**",
        f"🕐 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Total MCap: ${total_mcap/1e9:.2f}B | Sentiment: {sentiment} ({avg_change:+.1f}%)",
        "",
    ]

    for t in tokens[:limit]:
        name = t.get("name", "")[:18]
        sym = t.get("symbol", "").upper()
        price = t.get("current_price", 0) or 0
        mcap = (t.get("market_cap", 0) or 0) / 1e6
        change = t.get("price_change_percentage_24h", 0) or 0
        lines.append(f"  {name:<18} ${price:>8.4f} | ${mcap:>6.0f}M | {change:>+5.1f}%")

    return "\n".join(lines)


async def fetch_bounties() -> str:
    """Get AGENT_ALLOWED bounties from Superteam."""
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(
            "https://earn.superteam.fun/api/listings",
            params={"take": 50, "type": "bounty"},
        )
        resp.raise_for_status()
        bounties = resp.json()

    agent_bounties = [
        b for b in bounties
        if b.get("agentAccess") == "AGENT_ALLOWED" and b.get("status") == "OPEN"
    ]
    agent_bounties.sort(key=lambda x: x.get("rewardAmount", 0) or 0, reverse=True)

    lines = [
        "🎯 **AGENT_ALLOWED Bounties**",
        f"🕐 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Found {len(agent_bounties)} agent-completable bounties",
        "",
    ]

    total = 0
    for b in agent_bounties:
        reward = b.get("rewardAmount", 0) or 0
        token = b.get("token", "")
        deadline = (b.get("deadline", "") or "")[:10]
        subs = b.get("_count", {}).get("Submission", 0)
        title = b.get("title", "")[:50]
        total += reward
        lines.append(f"  ${reward:>6} {token:<5} | {deadline} | {subs:>3} subs | {title}")

    lines.append(f"\n💰 Total prize pool: ${total:,}")
    return "\n".join(lines)


# === Telegram Bot Handlers ===

if HAS_TELEGRAM:
    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "🔍 **CryptoAI Explorer Bot**\n\n"
            "Your AI-powered crypto intelligence agent.\n\n"
            "**Commands:**\n"
            "/digest [dao] — Governance digest (arbitrum/optimism)\n"
            "/yields — Top stablecoin yields\n"
            "/tokens — AI agent token market\n"
            "/bounties — AGENT_ALLOWED bounties\n"
            "/help — This message\n\n"
            "Data sources: Arbitrum Forum, Optimism Forum, DefiLlama, CoinGecko, Superteam",
            parse_mode="Markdown",
        )

    async def cmd_digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        dao = context.args[0] if context.args else "arbitrum"
        await update.message.reply_text("⏳ Fetching governance data...")
        try:
            digest = await fetch_governance_digest(dao)
            await update.message.reply_text(digest, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def cmd_yields(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("⏳ Scanning yields...")
        try:
            yields = await fetch_top_yields()
            await update.message.reply_text(f"```\n{yields}\n```", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def cmd_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("⏳ Fetching market data...")
        try:
            tokens = await fetch_agent_tokens()
            await update.message.reply_text(f"```\n{tokens}\n```", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def cmd_bounties(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("⏳ Checking bounties...")
        try:
            bounties = await fetch_bounties()
            await update.message.reply_text(f"```\n{bounties}\n```", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    def run_telegram_bot():
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            print("❌ Set TELEGRAM_BOT_TOKEN environment variable")
            print("   Get one from @BotFather on Telegram")
            sys.exit(1)

        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("start", cmd_start))
        app.add_handler(CommandHandler("help", cmd_start))
        app.add_handler(CommandHandler("digest", cmd_digest))
        app.add_handler(CommandHandler("yields", cmd_yields))
        app.add_handler(CommandHandler("tokens", cmd_tokens))
        app.add_handler(CommandHandler("bounties", cmd_bounties))

        print("🤖 Bot starting...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


async def cli_test():
    """Test all data fetching in CLI mode."""
    print("=" * 60)
    print("🔍 CryptoAI Explorer — CLI Test Mode")
    print("=" * 60)

    print("\n--- Governance Digest (Arbitrum) ---")
    print(await fetch_governance_digest("arbitrum", 8))

    print("\n--- Top Yields ---")
    print(await fetch_top_yields(8))

    print("\n--- Agent Tokens ---")
    print(await fetch_agent_tokens(8))

    print("\n--- Agent Bounties ---")
    print(await fetch_bounties())


if __name__ == "__main__":
    if "--test" in sys.argv or not HAS_TELEGRAM or not os.environ.get("TELEGRAM_BOT_TOKEN"):
        print("Running CLI test (set TELEGRAM_BOT_TOKEN to run as Telegram bot)")
        asyncio.run(cli_test())
    else:
        run_telegram_bot()
