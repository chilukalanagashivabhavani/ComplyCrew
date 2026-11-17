from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import os
import re
import tempfile

from agents.extractor_agent import extract_clauses
from agents.rule_matcher_agent import match_rules
from agents.risk_scorer_agent import score_risk
from agents.verifier_agent import verify_finding


app = FastAPI(
    title="ComplyCrew API",
    description="Multi-Agent Compliance Analysis System",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "ComplyCrew API is running",
        "status": "online"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "ai_engine": "Gemma 2B via Ollama",
        "architecture": "Multi-Agent"
    }


# ============================================================
# DOCUMENT READER
# ============================================================

def read_document(file_path, filename):

    extension = os.path.splitext(filename)[1].lower()

    # --------------------------------------------------------
    # TXT
    # --------------------------------------------------------

    if extension == ".txt":

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()


    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    elif extension == ".pdf":

        from pypdf import PdfReader

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text


    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    elif extension == ".docx":

        from docx import Document

        document = Document(file_path)

        text = ""

        for paragraph in document.paragraphs:

            text += paragraph.text + "\n"

        return text


    else:

        raise ValueError(
            "Unsupported file type. "
            "Please upload TXT, PDF or DOCX."
        )


# ============================================================
# CLAUSE PARSER
# ============================================================

def parse_clauses(extracted_text):

    pattern = (
        r"CLAUSE\s+\d+\s*:\s*"
        r"Title:\s*(.*?)\s*"
        r"Text:\s*(.*?)(?="
        r"\n\s*CLAUSE\s+\d+\s*:|$)"
    )

    matches = re.findall(
        pattern,
        extracted_text,
        re.IGNORECASE | re.DOTALL
    )

    clauses = []

    for title, text in matches:

        clauses.append({
            "title": title.strip(),
            "text": text.strip()
        })

    return clauses


# ============================================================
# EXTRACT RULE ID
# ============================================================

def extract_rule_id(rule_text):

    match = re.search(
        r"Rule ID:\s*(R\d+)",
        rule_text,
        re.IGNORECASE
    )

    if match:

        return match.group(1).upper()

    return "UNKNOWN"


# ============================================================
# EXTRACT POTENTIAL ISSUE
# ============================================================

def extract_potential_issue(rule_text):

    match = re.search(
        r"POTENTIAL ISSUE:\s*(YES|NO)",
        rule_text,
        re.IGNORECASE
    )

    if match:

        return match.group(1).upper()

    return "YES"


# ============================================================
# EXTRACT RISK LEVEL
# ============================================================

def extract_risk_level(risk_text):

    match = re.search(
        r"RISK LEVEL:\s*(HIGH|MEDIUM|LOW)",
        risk_text,
        re.IGNORECASE
    )

    if match:

        return match.group(1).upper()

    return "UNKNOWN"


# ============================================================
# EXTRACT VERIFICATION
# ============================================================

def extract_verification(verification_text):

    match = re.search(
        r"VERIFICATION:\s*"
        r"(VERIFIED|NEEDS_REVIEW|NOT_REQUIRED)",
        verification_text,
        re.IGNORECASE
    )

    if match:

        return match.group(1).upper()

    return "NOT_REQUIRED"


# ============================================================
# EXTRACT CONFIDENCE
# ============================================================

def extract_confidence(text):

    match = re.search(
        r"CONFIDENCE:\s*(HIGH|MEDIUM|LOW)",
        text,
        re.IGNORECASE
    )

    if match:

        return match.group(1).upper()

    return "MEDIUM"


# ============================================================
# ANALYZE DOCUMENT
# ============================================================

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...)
):

    temp_path = None

    try:

        print("\n======================================")
        print("COMPLYCREW ANALYSIS STARTED")
        print("======================================")

        print(
            f"Uploaded file: {file.filename}"
        )


        # ====================================================
        # SAVE UPLOADED FILE
        # ====================================================

        suffix = os.path.splitext(
            file.filename
        )[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_file.write(
                await file.read()
            )

            temp_path = temp_file.name


        # ====================================================
        # STEP 1 — READ DOCUMENT
        # ====================================================

        print("\n[1/5] Reading document...")

        document_text = read_document(
            temp_path,
            file.filename
        )

        print(
            f"Document loaded successfully "
            f"({len(document_text)} characters)"
        )


        # ====================================================
        # STEP 2 — EXTRACTOR
        # ====================================================

        print("\n[2/5] Extractor Agent running...")

        extracted_text = extract_clauses(
            document_text
        )

        clauses = parse_clauses(
            extracted_text
        )

        print(
            f"Extractor found {len(clauses)} clauses"
        )


        # ====================================================
        # RESULTS
        # ====================================================

        findings = []


        # ====================================================
        # PROCESS EACH CLAUSE
        # ====================================================

        for index, clause_data in enumerate(
            clauses,
            start=1
        ):

            title = clause_data["title"]
            clause_text = clause_data["text"]


            print("\n--------------------------------------")
            print(
                f"Processing Clause "
                f"{index}/{len(clauses)}: {title}"
            )
            print("--------------------------------------")


            # =================================================
            # STEP 3 — RULE MATCHER
            # =================================================

            print("  → Rule Matcher Agent")

            matched_rule = match_rules(
                clause_text
            )

            rule_id = extract_rule_id(
                matched_rule
            )

            potential_issue = extract_potential_issue(
                matched_rule
            )

            print(
                f"    Matched Rule: {rule_id}"
            )

            print(
                f"    Potential Issue: "
                f"{potential_issue}"
            )


            # =================================================
            # STEP 4 — RISK SCORER
            # =================================================

            print("  → Risk Scorer Agent")

            risk_result = score_risk(
                clause_text,
                matched_rule,
                potential_issue
            )

            risk_level = extract_risk_level(
                risk_result
            )

            print(
                f"    Risk Level: {risk_level}"
            )


            # =================================================
            # STEP 5 — VERIFICATION
            # =================================================

            # -----------------------------------------------
            # NO POTENTIAL ISSUE
            # -----------------------------------------------

            if potential_issue == "NO":

                print(
                    "  → No potential risk detected"
                )

                verification_result = """
VERIFICATION:
NOT_REQUIRED

CONFIDENCE:
HIGH

REASON:
No potential compliance issue was identified.
Human review is not required.
"""

                verification_status = "NOT_REQUIRED"

                confidence = "HIGH"


            # -----------------------------------------------
            # POTENTIAL ISSUE FOUND
            # -----------------------------------------------

            else:

                print(
                    "  → Verifier Agent"
                )

                verification_result = verify_finding(
                    clause_text,
                    matched_rule,
                    risk_result
                )

                verification_status = extract_verification(
                    verification_result
                )

                confidence = extract_confidence(
                    verification_result
                )

                print(
                    f"    Verification: "
                    f"{verification_status}"
                )

                print(
                    f"    Confidence: "
                    f"{confidence}"
                )


            # =================================================
            # HUMAN REVIEW LOGIC
            # =================================================

            if (
                potential_issue == "YES"
                and
                (
                    risk_level in [
                        "HIGH",
                        "MEDIUM"
                    ]
                    or
                    verification_status == "NEEDS_REVIEW"
                )
            ):

                human_review = True

            else:

                human_review = False


            # =================================================
            # FINAL FINDING
            # =================================================

            finding = {

                "clause_number": index,

                "title": title,

                "clause": clause_text,

                "rule": rule_id,

                "matched_rule": matched_rule,

                "potential_issue": potential_issue,

                "risk": risk_level,

                "verification": verification_status,

                "confidence": confidence,

                "human_review": human_review,

                "risk_result": risk_result,

                "verification_result":
                    verification_result
            }


            findings.append(
                finding
            )


        # ====================================================
        # COMPLETED
        # ====================================================

        print("\n======================================")
        print("ANALYSIS COMPLETED")
        print("======================================")

        print(
            f"Total clauses: {len(findings)}"
        )

        print(
            "======================================\n"
        )


        return {

            "success": True,

            "filename": file.filename,

            "clauses_analyzed": len(findings),

            "findings": findings
        }


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        print("\n======================================")
        print("ANALYSIS ERROR")
        print("======================================")

        print(str(e))

        print("======================================\n")

        return {

            "success": False,

            "error": str(e)
        }


    # ========================================================
    # CLEANUP
    # ========================================================

    finally:

        if temp_path:

            try:

                os.remove(
                    temp_path
                )

            except Exception:

                pass