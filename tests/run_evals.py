#!/usr/bin/env python3
"""
Eval Harness Runner for CryptoAI Explorer
Runs deterministic code-based graders for the system-baseline eval.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
import urllib.request
import urllib.error

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

EVAL_NAME = "system-baseline"
LOG_FILE = ROOT_DIR / ".claude" / "evals" / f"{EVAL_NAME}.log"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def run_eval(name: str, check_fn) -> bool:
    try:
        result = check_fn()
        if result:
            log(f"  [PASS] {name}")
            return True
        else:
            log(f"  [FAIL] {name} - Check function returned False")
            return False
    except Exception as e:
        log(f"  [FAIL] {name} - Exception: {e}")
        return False

# --- Regression Graders ---

def eval_dir_structure():
    dirs = ["scripts", "services", "data", "reports", "docs"]
    return all((ROOT_DIR / d).is_dir() for d in dirs)

def eval_scanner_syntax():
    scripts = list((ROOT_DIR / "scripts").glob("*.py"))
    for script in scripts:
        result = subprocess.run(["python3", "-m", "py_compile", str(script)], capture_output=True)
        if result.returncode != 0:
            print(f"Syntax error in {script.name}: {result.stderr.decode()}")
            return False
    return True

# --- Capability Graders ---

def eval_api_402():
    # Start the server in the background
    server_process = subprocess.Popen(
        ["uvicorn", "services.x402-api.server:app", "--port", "8499"],
        cwd=str(ROOT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2) # Give it time to start
    
    passed = False
    try:
        req = urllib.request.Request("http://127.0.0.1:8499/api/yields/top?limit=1")
        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            if e.code == 402:
                # Check if it returned proper L402 challenge header
                auth_header = e.headers.get("WWW-Authenticate", "")
                if "L402" in auth_header:
                    passed = True
    finally:
        server_process.terminate()
        server_process.wait()
        
    return passed

def eval_api_200_bypass():
    server_process = subprocess.Popen(
        ["uvicorn", "services.x402-api.server:app", "--port", "8499"],
        cwd=str(ROOT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    
    passed = False
    try:
        req = urllib.request.Request("http://127.0.0.1:8499/api/yields/top?limit=1")
        req.add_header("X-API-Key", "test-key-123")
        try:
            resp = urllib.request.urlopen(req)
            if resp.getcode() == 200:
                data = json.loads(resp.read())
                if "pools" in data:
                    passed = True
        except urllib.error.HTTPError:
            pass
    finally:
        server_process.terminate()
        server_process.wait()
        
    return passed

def eval_data_room():
    result = subprocess.run(["python3", "scripts/build_data_room.py"], cwd=str(ROOT_DIR), capture_output=True)
    if result.returncode != 0:
        return False
    return (ROOT_DIR / "docs" / "data-room.html").exists()

def eval_agent_wallet():
    # Make sure we don't accidentally nuke a real wallet, script handles get_or_create safely.
    result = subprocess.run(["python3", "scripts/agent_wallet.py"], cwd=str(ROOT_DIR), capture_output=True)
    if result.returncode != 0:
        return False
    
    wallet_file = ROOT_DIR / "data" / "agent_wallet.json"
    if not wallet_file.exists():
        return False
        
    with open(wallet_file) as f:
        data = json.load(f)
        return "address" in data and "private_key" in data

def eval_mcp_server():
    result = subprocess.run(["python3", "services/mcp-server/server.py", "--test"], cwd=str(ROOT_DIR), capture_output=True)
    return result.returncode == 0

def main():
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        
    log(f"EVAL REPORT: {EVAL_NAME}")
    log("=" * (13 + len(EVAL_NAME)))
    log(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
    
    log("Regression Evals:")
    r1 = run_eval("dir-structure", eval_dir_structure)
    r2 = run_eval("scanner-syntax", eval_scanner_syntax)
    
    log("\nCapability Evals:")
    c1 = run_eval("api-402-payment-gate", eval_api_402)
    c2 = run_eval("api-200-auth-bypass", eval_api_200_bypass)
    c3 = run_eval("data-room-compilation", eval_data_room)
    c4 = run_eval("agent-wallet-generation", eval_agent_wallet)
    c5 = run_eval("mcp-server-test-mode", eval_mcp_server)
    
    r_passed = sum([r1, r2])
    c_passed = sum([c1, c2, c3, c4, c5])
    
    log("\nMetrics:")
    log(f"  Regression pass rate: {r_passed}/2 ({(r_passed/2)*100:.0f}%)")
    log(f"  Capability pass rate: {c_passed}/5 ({(c_passed/5)*100:.0f}%)")
    
    if r_passed == 2 and c_passed >= 4:
        log("\nStatus: READY FOR RELEASE ✅")
    else:
        log("\nStatus: FAILING REVIEWS ❌")

if __name__ == "__main__":
    main()
