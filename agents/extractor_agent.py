import requests


def extract_clauses(document_text):

    prompt = f"""
You are the Extractor Agent of ComplyCrew.

Your job is ONLY to identify and organize the important clauses
in the document.

Do not judge whether the document is compliant.
Do not give legal advice.
Do not invent information.
Do not rewrite the meaning of the document.

Return every important clause in EXACTLY this format:

CLAUSE 1:
Title: ...
Text: ...

CLAUSE 2:
Title: ...
Text: ...

CLAUSE 3:
Title: ...
Text: ...

Continue until all important clauses are extracted.

IMPORTANT:
- Every clause must have a number.
- Every clause must have a Title.
- Every clause must have Text.
- Keep the original meaning.
- Do not combine unrelated clauses.
- Do not create clauses that are not present in the document.

DOCUMENT:
{document_text}
"""

    print("\n======================================")
    print("EXTRACTOR AGENT")
    print("Sending document to Gemma 2B...")
    print("======================================")

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
        timeout=300
    )

    response.raise_for_status()

    result = response.json()["message"]["content"]

    print("\n========== EXTRACTOR OUTPUT ==========")
    print(result)
    print("======================================\n")

    return result