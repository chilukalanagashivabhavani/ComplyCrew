from agents.extractor_agent import extract_clauses
from agents.rule_matcher_agent import match_rules
from agents.risk_scorer_agent import score_risk
from agents.verifier_agent import verify_finding
from agents.report_writer_agent import write_report


# ============================================================
# READ DOCUMENT
# ============================================================

with open(
    "sample/sample_privacy_policy.txt",
    "r",
    encoding="utf-8"
) as file:
    document_text = file.read()


# ============================================================
# START PIPELINE
# ============================================================

print("\n========================================")
print("       COMPLyCREW PIPELINE STARTED")
print("========================================")


# ============================================================
# STEP 1 — EXTRACT CLAUSES
# ============================================================

print("\n[1/5] Running Extractor Agent...")

extracted_clauses = extract_clauses(
    document_text
)

print("Extractor Agent completed.")


# ============================================================
# PARSE EXTRACTED CLAUSES
# ============================================================

def parse_clauses(text):
    """
    Convert the Extractor Agent output into
    individual clause blocks.
    """

    clauses = []

    blocks = text.split("CLAUSE ")

    for block in blocks[1:]:

        block = block.strip()

        if block:
            clauses.append(block)

    return clauses


clauses = parse_clauses(
    extracted_clauses
)

print(
    f"\nExtracted {len(clauses)} clauses."
)


# ============================================================
# PROCESS EACH CLAUSE
# ============================================================

all_reports = []


for index, clause in enumerate(
    clauses,
    start=1
):

    print("\n----------------------------------------")
    print(
        f"ANALYZING CLAUSE {index}/{len(clauses)}"
    )
    print("----------------------------------------")


    # ========================================================
    # STEP 2 — RULE MATCHER
    # ========================================================

    print("\n[2/5] Running Rule Matcher Agent...")

    matched_rule = match_rules(
        clause
    )

    print("Rule Matcher Agent completed.")


    # ========================================================
    # STEP 3 — RISK SCORER
    # ========================================================

    print("\n[3/5] Running Risk Scorer Agent...")

    risk_result = score_risk(
        clause,
        matched_rule,
        "YES"
    )

    print("Risk Scorer Agent completed.")


    # ========================================================
    # STEP 4 — VERIFIER
    # ========================================================

    print("\n[4/5] Running Verifier Agent...")

    verification_result = verify_finding(
        clause,
        matched_rule,
        risk_result
    )

    print("Verifier Agent completed.")


    # ========================================================
    # STEP 5 — REPORT WRITER
    # ========================================================

    print("\n[5/5] Running Report Writer Agent...")

    report = write_report(
        clause,
        matched_rule,
        risk_result,
        verification_result
    )

    print("Report Writer Agent completed.")


    # Store report
    all_reports.append(
        report
    )


# ============================================================
# FINAL COMPLIANCE AUDIT REPORT
# ============================================================

print("\n\n========================================")
print("       FINAL COMPLIANCE AUDIT REPORT")
print("========================================")


for index, report in enumerate(
    all_reports,
    start=1
):

    print("\n\n========================================")
    print(
        f"              FINDING {index}"
    )
    print("========================================")

    print(report)


# ============================================================
# PIPELINE COMPLETED
# ============================================================

print("\n========================================")
print("       COMPLYCREW PIPELINE COMPLETED")
print("========================================")