import requests


def score_risk(clause_text, matched_rule, potential_issue):

    # =========================================================
    # IF RULE MATCHER ALREADY FOUND NO ISSUE
    # =========================================================

    if potential_issue.strip().upper() == "NO":

        return """
RISK LEVEL:
LOW

REASON:
The document clause does not show a potential compliance problem
based on the matched rule.

RECOMMENDED PRIORITY:
MONITOR

POTENTIAL ISSUE:
NO

HUMAN REVIEW:
NO
"""

    # =========================================================
    # ASK GEMMA TO ASSESS A POTENTIAL ISSUE
    # =========================================================

    prompt = f"""
You are the Risk Scorer Agent of ComplyCrew.

Your job is to determine whether the document clause contains
a potential compliance risk based ONLY on the matched rule.

IMPORTANT:

1. Compare the DOCUMENT CLAUSE with the MATCHED RULE.

2. If the document clause ALREADY satisfies the requirement,
   the result must be:

POTENTIAL ISSUE:
NO

RISK LEVEL:
LOW

3. If the document clause clearly fails to satisfy the
   requirement, the result must be:

POTENTIAL ISSUE:
YES

4. Do NOT treat the existence of a topic as a violation.

5. For example:

Rule:
The organization should provide a mechanism through which
individuals can raise complaints.

Clause:
Users can contact our support team if they have questions
or complaints.

This clause provides a complaint mechanism.

Therefore:
POTENTIAL ISSUE: NO
RISK LEVEL: LOW

6. Only identify a risk when the actual wording of the clause
shows a missing, weak, unclear or contradictory requirement.

7. Do not invent legal requirements.

8. Do not give a legal verdict.

9. If the evidence is uncertain, mark the potential issue as YES
   and allow the Verifier Agent to check it.

Return EXACTLY:

RISK LEVEL:
HIGH / MEDIUM / LOW

REASON:
...

RECOMMENDED PRIORITY:
IMMEDIATE / SOON / MONITOR

POTENTIAL ISSUE:
YES / NO

HUMAN REVIEW:
YES / NO

DOCUMENT CLAUSE:
{clause_text}

MATCHED RULE:
{matched_rule}

"""

    # =========================================================
    # GEMMA REQUEST
    # =========================================================

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
        },
        timeout=180
    )

    response.raise_for_status()

    return response.json()["message"]["content"]