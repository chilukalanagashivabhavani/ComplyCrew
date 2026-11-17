import requests


def write_report(
    clause_text,
    matched_rule,
    risk_result,
    verification_result
):
    """
    Generate a professional compliance finding report
    using local Gemma 2B.
    """

    prompt = f"""
You are the Report Writer Agent of ComplyCrew.

Create a clear and professional compliance audit finding
from the information provided by the previous agents.

IMPORTANT:
- Do not invent regulations.
- Do not add facts that are not provided.
- Keep the Rule ID exactly as provided.
- Clearly separate evidence from recommendation.
- If verification is NEEDS_REVIEW, clearly mention that
  human review is required.
- This is an AI-generated compliance recommendation,
  NOT a legal verdict.

Use exactly this structure:

COMPLYCREW COMPLIANCE FINDING

CLAUSE:
...

MATCHED RULE:
...

POTENTIAL ISSUE:
YES / NO

RISK LEVEL:
...

PRIORITY:
...

VERIFICATION:
...

CONFIDENCE:
...

EXPLANATION:
...

RECOMMENDED FIX:
...

HUMAN REVIEW:
YES / NO

DOCUMENT CLAUSE:
{clause_text}

MATCHED RULE:
{matched_rule}

RISK ASSESSMENT:
{risk_result}

VERIFICATION RESULT:
{verification_result}
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
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


if __name__ == "__main__":

    clause = """
    We may share your personal information with our partners,
    advertisers and other organizations whenever we consider it necessary.
    """

    matched_rule = """
    Rule ID: R007
    Topic: Data sharing

    Requirement:
    An organization should clearly address applicable conditions
    and purposes for sharing personal data with other organizations
    or third parties.
    """

    risk_result = """
    RISK LEVEL:
    HIGH

    RECOMMENDED PRIORITY:
    IMMEDIATE

    POTENTIAL ISSUE:
    YES
    """

    verification_result = """
    VERIFICATION:
    NEEDS_REVIEW

    CONFIDENCE:
    MEDIUM

    REASON:
    The clause indicates data sharing but does not clearly
    specify the conditions and purposes for sharing.
    """

    result = write_report(
        clause,
        matched_rule,
        risk_result,
        verification_result
    )

    print("\n===== REPORT WRITER AGENT RESULT =====\n")
    print(result)