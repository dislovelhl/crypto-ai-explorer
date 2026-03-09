#!/usr/bin/env python3
"""
CryptoAI Copilot - Agent Wallet Generator
Generates an EVM-compatible wallet (for Base, Optimism, Arbitrum, Ethereum)
so the AI agent can autonomously receive x402/L402 payments.
Safely stores keys in the ignored data/ directory.
"""

import os
import json
import sys
from pathlib import Path

try:
    from eth_account import Account
except ImportError:
    import subprocess
    print("Installing eth-account...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "eth-account"])
    from eth_account import Account

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
WALLET_FILE = DATA_DIR / "agent_wallet.json"

def get_or_create_wallet():
    Account.enable_unaudited_hdwallet_features()
    
    if WALLET_FILE.exists():
        with open(WALLET_FILE, "r") as f:
            wallet_data = json.load(f)
        print(f"✅ Found existing Agent Wallet: {wallet_data['address']}")
        return wallet_data

    print("Generating new EVM Agent Wallet...")
    acct, mnemonic = Account.create_with_mnemonic()
    
    wallet_data = {
        "address": acct.address,
        "private_key": acct.key.hex(),
        "mnemonic": mnemonic,
        "network_focus": "Base (for x402 USDC payments)",
        "created_at": str(os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip())
    }
    
    # Save safely (data/*.json is in .gitignore)
    with open(WALLET_FILE, "w") as f:
        json.dump(wallet_data, f, indent=4)
        
    os.chmod(WALLET_FILE, 0o600)  # Restrict permissions
    
    print(f"🎉 New Agent Wallet Created!")
    print(f"   Address: {wallet_data['address']}")
    print(f"   Keys securely saved to {WALLET_FILE} (ignored by Git).")
    print(f"   Fund this address with Base USDC to test x402 functionality.")
    
    return wallet_data

def main():
    print("🤖 Agent Financial Rails Initialization")
    print("=" * 60)
    get_or_create_wallet()

if __name__ == "__main__":
    main()
