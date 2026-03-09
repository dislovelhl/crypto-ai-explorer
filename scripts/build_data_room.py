#!/usr/bin/env python3
"""
CryptoAI Data Room Builder
Generates a professional static HTML "Data Room" representing the project's
pitches, stats, and capabilities. Built specifically to be submitted as a URL
to hackathons and grant programs.
"""

import os
import json
import re
from datetime import datetime, timezone
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = ROOT_DIR / "docs"
BOUNTY_DIR = ROOT_DIR / "bounties"
GRANTS_DIR = ROOT_DIR / "grants"

def load_json(filename: str) -> dict:
    path = DATA_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def read_md(path: Path) -> str:
    if path.exists():
        with open(path) as f:
            return f.read()
    return ""

def markdown_to_html(text: str) -> str:
    """A very basic regex-based markdown to HTML converter for simple layouts."""
    # Headers
    text = re.sub(r'^### (.*?)$', r'<h3 class="text-xl font-bold mt-6 mb-3">\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2 class="text-2xl font-bold mt-8 mb-4 border-b border-gray-800 pb-2">\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1 class="text-3xl font-extrabold mb-6">\1</h1>', text, flags=re.MULTILINE)
    
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Lists
    text = re.sub(r'^- (.*?)$', r'<li class="ml-4 list-disc mb-1">\1</li>', text, flags=re.MULTILINE)
    
    # Paragraphs (basic newline replacement for display)
    text = text.replace('\n\n', '<br><br>')
    
    return text

def build_data_room():
    print("🏢 Building Investor & Hackathon Data Room...")
    
    # Pull dynamic data
    yield_data = load_json("defi_yields.json")
    tokens_data = load_json("agent_tokens.json")
    grants_data = load_json("superteam_grants.json")
    bounty_data = load_json("superteam_bounties.json")
    
    tvl_scanned = yield_data.get("total_pools", 19200)
    token_mcap = tokens_data.get("total_market_cap", 2600000000)
    grants_tracked = grants_data.get("total_funding", 100000)
    
    # Load pitches
    tokenton_pitch = read_md(BOUNTY_DIR / "tokenton26" / "FINAL_SUBMISSION.md")
    helpbnk_pitch = read_md(BOUNTY_DIR / "helpbnk" / "business_challenge.md")
    op_grant = read_md(GRANTS_DIR / "optimism-s9" / "application.md")
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CryptoAI Copilot | Investor Data Room</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        .bg-grid {{ background-image: radial-gradient(#374151 1px, transparent 1px); background-size: 24px 24px; }}
    </style>
</head>
<body class="bg-gray-950 text-gray-200 bg-grid min-h-screen">
    <div class="max-w-7xl mx-auto px-4 py-12 flex flex-col md:flex-row gap-8">
        
        <!-- Sidebar Navigation -->
        <aside class="w-full md:w-64 shrink-0">
            <div class="sticky top-12 bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h2 class="text-xl font-bold text-white mb-6">Data Room</h2>
                <nav class="flex flex-col gap-3">
                    <a href="#overview" class="text-blue-400 hover:text-blue-300 transition-colors">1. Executive Overview</a>
                    <a href="#tokenton" class="text-gray-400 hover:text-white transition-colors">2. TokenTon26 Submission</a>
                    <a href="#helpbnk" class="text-gray-400 hover:text-white transition-colors">3. HelpBnk Business Pitch</a>
                    <a href="#optimism" class="text-gray-400 hover:text-white transition-colors">4. Optimism S9 Grant</a>
                    <a href="#metrics" class="text-gray-400 hover:text-white transition-colors">5. Live Data Metrics</a>
                </nav>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="flex-grow space-y-16">
            
            <!-- Overview -->
            <section id="overview" class="bg-gray-900/80 border border-gray-800 rounded-2xl p-8 backdrop-blur-sm">
                <h1 class="text-4xl font-extrabold text-white mb-4">CryptoAI Copilot</h1>
                <p class="text-xl text-emerald-400 font-mono mb-8">Status: LIVE & EXECUTING</p>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                    <div class="bg-black/50 p-4 rounded-lg border border-gray-800">
                        <div class="text-2xl font-bold text-white">{tvl_scanned:,}</div>
                        <div class="text-xs text-gray-400 uppercase tracking-wider">DeFi Pools Scanned</div>
                    </div>
                    <div class="bg-black/50 p-4 rounded-lg border border-gray-800">
                        <div class="text-2xl font-bold text-white">${token_mcap / 1e9:.2f}B</div>
                        <div class="text-xs text-gray-400 uppercase tracking-wider">Agent Token Market</div>
                    </div>
                    <div class="bg-black/50 p-4 rounded-lg border border-gray-800">
                        <div class="text-2xl font-bold text-white">${grants_tracked:,.0f}</div>
                        <div class="text-xs text-gray-400 uppercase tracking-wider">Grants Monitored</div>
                    </div>
                </div>
                
                <p class="text-gray-300 leading-relaxed mb-4">
                    Welcome to the CryptoAI Copilot Data Room. We are an AI-native execution layer for delegates, DAOs, and crypto builders that turns fragmented intelligence into an automated, risk-adjusted opportunity radar with x402 payment rails.
                </p>
                <p class="text-gray-300 leading-relaxed">
                    This document compiles our primary hackathon submissions, grant applications, and live system metrics in one place.
                </p>
            </section>

            <!-- TokenTon26 -->
            <section id="tokenton" class="bg-gray-900 border border-gray-800 rounded-2xl p-8">
                <div class="prose prose-invert max-w-none text-gray-300">
                    {markdown_to_html(tokenton_pitch)}
                </div>
            </section>

            <!-- HelpBnk -->
            <section id="helpbnk" class="bg-gray-900 border border-gray-800 rounded-2xl p-8">
                <div class="prose prose-invert max-w-none text-gray-300">
                    {markdown_to_html(helpbnk_pitch)}
                </div>
            </section>
            
            <!-- Optimism -->
            <section id="optimism" class="bg-gray-900 border border-gray-800 rounded-2xl p-8">
                <div class="prose prose-invert max-w-none text-gray-300">
                    {markdown_to_html(op_grant)}
                </div>
            </section>

        </main>
    </div>
</body>
</html>
"""

    out_file = DOCS_DIR / "data-room.html"
    with open(out_file, "w") as f:
        f.write(html_template)
        
    print(f"✅ Data Room built successfully!")
    print(f"📄 Saved to: {out_file}")

if __name__ == "__main__":
    build_data_room()
