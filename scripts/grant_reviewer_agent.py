#!/usr/bin/env python3
"""
Grant Reviewer Agent
Evaluates grant proposals against ecosystem criteria using an LLM API.
Designed for the Optimism Season 9 Grants Council use case.
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    import httpx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx

# You can use OpenAI or Anthropic. We use Anthropic here as a default for long context.
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def evaluate_grant(proposal_text: str) -> dict:
    """Send the proposal to an LLM to evaluate against OP S9 criteria."""
    
    if not ANTHROPIC_API_KEY:
        print("⚠️ ANTHROPIC_API_KEY not found. Returning mocked evaluation.")
        return {
            "score": 85,
            "alignment": "Strong alignment with OP Season 9 Growth initiatives.",
            "feasibility": "High. The team has shipped similar products.",
            "budget_reasonableness": "Medium. The $50k ask is justified but milestone 2 is vague.",
            "recommendation": "APPROVE with conditions on Milestone 2."
        }
    
    prompt = f"""
You are an expert Grant Reviewer for the Optimism Season 9 Grants Council.
Your goal is to evaluate the following grant proposal objectively based on:
1. Alignment with Optimism's Growth/Public Goods mandate.
2. Technical Feasibility & Team Capability.
3. Budget Reasonableness & Milestones.

Provide a JSON output ONLY with the following schema:
{{
  "score": <0-100 integer>,
  "alignment": "<1-2 sentences>",
  "feasibility": "<1-2 sentences>",
  "budget_reasonableness": "<1-2 sentences>",
  "recommendation": "<APPROVE|REJECT|REVISE>"
}}

PROPOSAL TEXT:
---
{proposal_text}
---
"""

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            
            content = response.json()["content"][0]["text"]
            # Try to extract just the JSON
            if "{" in content and "}" in content:
                json_str = content[content.find("{"):content.rfind("}")+1]
                return json.loads(json_str)
            else:
                return {"error": "Failed to parse JSON", "raw": content}

    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Evaluate a grant proposal markdown file.")
    parser.add_argument("file", help="Path to the markdown file containing the grant proposal")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r") as f:
        text = f.read()
        
    print(f"🔍 Analyzing {file_path.name} ({len(text)} characters)...")
    
    result = evaluate_grant(text)
    
    print("\n✅ Evaluation Complete:\n")
    print(json.dumps(result, indent=2))
    
    if "score" in result:
        print(f"\nFINAL SCORE: {result['score']}/100")
        print(f"DECISION: {result['recommendation']}")

if __name__ == "__main__":
    main()
