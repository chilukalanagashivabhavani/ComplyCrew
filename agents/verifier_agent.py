import requests


def verify_finding(clause_text, matched_rule, risk_result):

    prompt = f"""
You are the Verifier Agent of ComplyCrew.

Verify the compliance finding using ONLY the information below.

Return exactly:

VERIFICATION:
VERIFIED or NEEDS_REVIEW

CONFIDENCE:
HIGH or MEDIUM or LOW

REASON:
One short sentence explaining why.

DOCUMENT CLAUSE:
{clause_text}

MATCHED RULE:
{matched_rule}

RISK RESULT:
{risk_result}
"""

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "gemma2:2b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0
            }
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["message"]["content"]