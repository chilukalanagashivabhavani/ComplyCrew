import requests
from sentence_transformers import SentenceTransformer
import chromadb


# ---------------------------------------------------------
# LOAD EMBEDDING MODEL
# ---------------------------------------------------------

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------------------------------------
# CHROMADB
# ---------------------------------------------------------

client = chromadb.PersistentClient(
    path="data/chroma_db"
)

collection = client.get_or_create_collection(
    name="complycrew_rules"
)


# ---------------------------------------------------------
# RULE MATCHER
# ---------------------------------------------------------

def match_rules(clause_text):

    print("    Creating clause embedding...")

    clause_embedding = embedding_model.encode(
        clause_text
    ).tolist()

    print("    Searching compliance rules...")

    results = collection.query(
        query_embeddings=[clause_embedding],
        n_results=1
    )

    retrieved_rules = results["documents"][0]

    if not retrieved_rules:
        return """
MATCHED RULE:
Rule ID: NO MATCH
Topic: NONE

REASON:
No relevant rule was retrieved.

POTENTIAL ISSUE:
NO

EVIDENCE:
No matching rule was found.
"""

    rules_text = retrieved_rules[0]

    print("    Retrieved rule successfully.")

    prompt = f"""
You are the Rule Matcher Agent of ComplyCrew.

Your job is to match ONE document clause with the
MOST RELEVANT compliance rule.

IMPORTANT:

1. Use ONLY the retrieved rule below.
2. Do NOT invent a Rule ID.
3. Copy the Rule ID exactly.
4. Select only the most relevant rule.
5. Do not create new requirements.
6. Do not give legal advice.
7. Base your answer only on the document clause
   and retrieved rule.

Return exactly:

MATCHED RULE:
Rule ID: R001 / R002 / R003 / etc.

Topic:
...

REASON:
...

POTENTIAL ISSUE:
YES or NO

EVIDENCE:
...

RETRIEVED RULE:
{rules_text}

DOCUMENT CLAUSE:
{clause_text}
"""

    print("    Sending rule-matching request to Gemma...")

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

    result = response.json()["message"]["content"]

    print("    Rule Matcher completed.")

    return result