from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import os
import tempfile
import re

from agents.extractor_agent import extract_clauses
from agents.rule_matcher_agent import match_rules
from agents.risk_scorer_agent import score_risk
from agents.verifier_agent import verify_finding
from agents.report_writer_agent import write_report


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="ComplyCrew API",
    description="Multi-Agent Regulatory Compliance Checker",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# BASIC HOME ROUTE
# ============================================================

@app.get("/")
def home():

    return {
        "message": "ComplyCrew Backend is running",
        "status": "online",
        "ai_engine": "Gemma 2B + Ollama",
        "vector_database": "ChromaDB",
        "agents": 5
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "ComplyCrew Backend"
    }


# ============================================================
# TEXT EXTRACTION FROM UPLOAD
# ============================================================

def extract_document_text(
    file_path,
    filename
):

    extension = (
        filename
        .split(".")[-1]
        .lower()
    )


    # --------------------------------------------------------
    # TXT
    # --------------------------------------------------------

    if extension == "txt":

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            return file.read()


    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if extension == "pdf":

        from pypdf import PdfReader

        reader = PdfReader(
            file_path
        )

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

        return text


    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    if extension == "docx":

        from docx import Document

        document = Document(
            file_path
        )

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )


    return ""


# ============================================================
# CLAUSE PARSER
# ============================================================

def parse_clauses(text):

    clauses = []

    blocks = text.split(
        "CLAUSE "
    )

    for block in blocks[1:]:

        block = block.strip()

        if block:

            clauses.append(
                block
            )

    return clauses


# ============================================================
# EXTRACT RISK LEVEL
# ============================================================

def get_risk_level(
    risk_result
):

    match = re.search(
        r"RISK LEVEL\s*:\s*"
        r"(HIGH|MEDIUM|LOW)",
        risk_result,
        re.IGNORECASE
    )

    if match:

        return (
            match
            .group(1)
            .upper()
        )

    return "UNKNOWN"


# ============================================================
# EXTRACT VERIFICATION
# ============================================================

def get_verification_status(
    verification_result
):

    match = re.search(
        r"VERIFICATION\s*:\s*"
        r"(VERIFIED|NEEDS_REVIEW)",
        verification_result,
        re.IGNORECASE
    )

    if match:

        return (
            match
            .group(1)
            .upper()
        )

    return "UNKNOWN"


# ============================================================
# ANALYZE DOCUMENT
# ============================================================

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...)
):

    temp_path = None


    try:

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

            contents = await file.read()

            temp_file.write(
                contents
            )

            temp_path = temp_file.name


        # ====================================================
        # READ DOCUMENT
        # ====================================================

        document_text = extract_document_text(
            temp_path,
            file.filename
        )


        if not document_text.strip():

            return {
                "success": False,
                "error": "Could not extract text from document."
            }


        # ====================================================
        # AGENT 1 — EXTRACTOR
        # ====================================================

        extracted_clauses = extract_clauses(
            document_text
        )


        clauses = parse_clauses(
            extracted_clauses
        )


        if not clauses:

            return {
                "success": False,
                "error": "No clauses could be extracted."
            }


        # ====================================================
        # STORE RESULTS
        # ====================================================

        findings = []


        # ====================================================
        # PROCESS EACH CLAUSE
        # ====================================================

        for index, clause in enumerate(
            clauses,
            start=1
        ):

            # ------------------------------------------------
            # AGENT 2 — RULE MATCHER
            # ------------------------------------------------

            matched_rule = match_rules(
                clause
            )


            # ------------------------------------------------
            # DETERMINE POTENTIAL ISSUE
            # ------------------------------------------------

            if (
                "POTENTIAL ISSUE: NO"
                in matched_rule.upper()
            ):

                potential_issue = "NO"

            else:

                potential_issue = "YES"


            # ------------------------------------------------
            # AGENT 3 — RISK SCORER
            # ------------------------------------------------

            risk_result = score_risk(
                clause,
                matched_rule,
                potential_issue
            )


            risk_level = get_risk_level(
                risk_result
            )


            # ------------------------------------------------
            # AGENT 4 — VERIFIER
            # ------------------------------------------------

            verification_result = verify_finding(
                clause,
                matched_rule,
                risk_result
            )


            verification_status = (
                get_verification_status(
                    verification_result
                )
            )


            # ------------------------------------------------
            # AGENT 5 — REPORT WRITER
            # ------------------------------------------------

            report = write_report(
                clause,
                matched_rule,
                risk_result,
                verification_result
            )


            # ------------------------------------------------
            # SAVE FINDING
            # ------------------------------------------------

            findings.append(
                {
                    "finding_number": index,

                    "clause": clause,

                    "matched_rule": matched_rule,

                    "potential_issue":
                        potential_issue,

                    "risk_level":
                        risk_level,

                    "risk_result":
                        risk_result,

                    "verification":
                        verification_status,

                    "verification_result":
                        verification_result,

                    "report":
                        report
                }
            )


        # ====================================================
        # SUMMARY
        # ====================================================

        high_count = 0
        medium_count = 0
        low_count = 0
        review_count = 0


        for finding in findings:

            if finding["risk_level"] == "HIGH":

                high_count += 1

            elif finding["risk_level"] == "MEDIUM":

                medium_count += 1

            elif finding["risk_level"] == "LOW":

                low_count += 1


            if (
                finding["verification"]
                == "NEEDS_REVIEW"
            ):

                review_count += 1


        # ====================================================
        # RETURN RESULT TO FRONTEND
        # ====================================================

        return {

            "success": True,

            "document_name":
                file.filename,

            "summary": {

                "clauses_analyzed":
                    len(findings),

                "high_risk":
                    high_count,

                "medium_risk":
                    medium_count,

                "low_risk":
                    low_count,

                "needs_review":
                    review_count
            },

            "findings":
                findings
        }


    except Exception as error:

        return {

            "success": False,

            "error":
                str(error)
        }


    finally:

        # ====================================================
        # DELETE TEMPORARY FILE
        # ====================================================

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            os.remove(
                temp_path
            )