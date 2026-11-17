import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# LOAD LOCAL EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# ============================================================
# CREATE CHROMADB DATABASE
# ============================================================

client = chromadb.PersistentClient(
    path="data/chroma_db"
)


# ============================================================
# CREATE / GET RULE COLLECTION
# ============================================================

collection = client.get_or_create_collection(
    name="complycrew_rules"
)


# ============================================================
# READ RULEBOOK
# ============================================================

with open(
    "data/rulebook.txt",
    "r",
    encoding="utf-8"
) as file:

    rulebook = file.read()


# ============================================================
# SPLIT RULEBOOK INTO INDIVIDUAL RULES
# ============================================================

rule_blocks = rulebook.split("RULE R")

rules = []

for block in rule_blocks[1:]:

    rule_text = "RULE R" + block.strip()

    rules.append(rule_text)


# ============================================================
# ADD RULES TO CHROMADB
# ============================================================

for index, rule in enumerate(rules):

    rule_id = "R" + rule.split("RULE R")[1].split()[0]

    embedding = embedding_model.encode(
        rule
    ).tolist()

    collection.upsert(
        ids=[rule_id],
        documents=[rule],
        embeddings=[embedding]
    )


print(f"Loaded {len(rules)} rules into ChromaDB.")


# ============================================================
# TEST RETRIEVAL
# ============================================================

test_query = """
We may share personal information with partners,
advertisers and other organizations.
"""

query_embedding = embedding_model.encode(
    test_query
).tolist()


results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)


print("\n===== RETRIEVED RULES =====\n")

for rule in results["documents"][0]:

    print(rule)
    print("----------------------------------------")