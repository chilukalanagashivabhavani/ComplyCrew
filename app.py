import streamlit as st
import os
import re
import tempfile

from agents.extractor_agent import extract_clauses
from agents.rule_matcher_agent import match_rules
from agents.risk_scorer_agent import score_risk
from agents.verifier_agent import verify_finding
from agents.report_writer_agent import write_report


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ComplyCrew",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HTML HELPER
# ============================================================

def render_html(html):
    """
    Render custom HTML safely.
    Removes leading/trailing spaces from every line
    so Streamlit does not treat the HTML as a code block.
    """

    lines = html.splitlines()

    cleaned_lines = []

    for line in lines:
        cleaned_lines.append(line.strip())

    cleaned_html = "\n".join(cleaned_lines)

    st.markdown(
        cleaned_html,
        unsafe_allow_html=True
    )


# ============================================================
# CUSTOM CSS
# WHITE BACKGROUND + DARK TEXT + COLORFUL UI
# ============================================================

render_html("""
<style>

/* ============================================================
   GLOBAL PAGE
   ============================================================ */

html,
body {
    background-color: #ffffff !important;
    color: #111827 !important;
}

.stApp {
    background-color: #ffffff !important;
    color: #111827 !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #111827 !important;
}

[data-testid="stMain"] {
    background-color: #ffffff !important;
    color: #111827 !important;
}

[data-testid="stAppViewContainer"] > .main {
    background-color: #ffffff !important;
    color: #111827 !important;
}

.main {
    background-color: #ffffff !important;
    color: #111827 !important;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
    background-color: #ffffff !important;
    color: #111827 !important;
}


/* ============================================================
   NORMAL STREAMLIT TEXT
   ============================================================ */

[data-testid="stMarkdownContainer"] {
    color: #111827 !important;
}

[data-testid="stMarkdownContainer"] p {
    color: #111827 !important;
}

[data-testid="stMarkdownContainer"] strong {
    color: #111827 !important;
}

[data-testid="stMarkdownContainer"] li {
    color: #111827 !important;
}

[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6 {
    color: #0f172a !important;
}


/* ============================================================
   HEADINGS
   ============================================================ */

h1,
h2,
h3,
h4,
h5,
h6 {
    color: #0f172a !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] h5,
section[data-testid="stSidebar"] h6 {
    color: #1e293b !important;
}

section[data-testid="stSidebar"] .stCaption {
    color: #64748b !important;
}


/* ============================================================
   SIDEBAR BRAND
   ============================================================ */

.sidebar-brand {
    font-size: 28px;
    font-weight: 900;
    color: #2563eb !important;
    margin-bottom: 5px;
}


/* ============================================================
   SIDEBAR STATUS CARDS
   ============================================================ */

.status-card {
    padding: 15px 17px;
    margin-bottom: 10px;

    border-radius: 13px;

    background: linear-gradient(
        135deg,
        #ecfdf5,
        #d1fae5
    );

    border: 1px solid #86efac;

    color: #166534 !important;

    font-weight: 750;
}

.status-card * {
    color: #166534 !important;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    padding: 42px 45px;

    border-radius: 26px;

    background:
        linear-gradient(
            135deg,
            #172554 0%,
            #312e81 45%,
            #581c87 100%
        );

    border: 1px solid #6366f1;

    box-shadow:
        0 25px 70px rgba(79, 70, 229, 0.30);

    margin-bottom: 32px;
}

.hero-title {
    font-size: 50px;
    font-weight: 900;

    color: #ffffff !important;

    line-height: 1.1;
}

.hero-subtitle {
    font-size: 22px;
    font-weight: 700;

    color: #dbeafe !important;

    margin-top: 8px;
}

.hero-description {
    max-width: 950px;

    margin-top: 18px;

    color: #c7d2fe !important;

    font-size: 16px;

    line-height: 1.75;
}

.hero-badge {
    display: inline-block;

    margin-top: 22px;

    padding: 10px 18px;

    border-radius: 30px;

    background: rgba(15, 23, 42, 0.65);

    border: 1px solid #38bdf8;

    color: #7dd3fc !important;

    font-size: 13px;

    font-weight: 800;
}

.hero,
.hero *,
.hero .hero-title,
.hero .hero-subtitle,
.hero .hero-description,
.hero .hero-badge {
    color: inherit;
}

.hero .hero-title {
    color: #ffffff !important;
}

.hero .hero-subtitle {
    color: #dbeafe !important;
}

.hero .hero-description {
    color: #c7d2fe !important;
}

.hero .hero-badge {
    color: #7dd3fc !important;
}


/* ============================================================
   WORKFLOW
   ============================================================ */

.workflow-container {
    display: flex;

    align-items: center;

    gap: 10px;

    width: 100%;

    margin-bottom: 35px;
}

.workflow-card {
    flex: 1;

    min-height: 125px;

    padding: 17px 8px;

    border-radius: 18px;

    text-align: center;

    background:
        linear-gradient(
            145deg,
            #f8fafc,
            #e2e8f0
        );

    border: 1px solid #cbd5e1;

    box-shadow:
        0 12px 30px rgba(15, 23, 42, 0.10);

    transition: 0.2s;
}

.workflow-card:hover {
    border-color: #818cf8;

    transform: translateY(-3px);
}

.workflow-number {
    color: #2563eb !important;

    font-size: 12px;

    font-weight: 900;
}

.workflow-icon {
    font-size: 30px;

    margin-top: 8px;
}

.workflow-name {
    color: #0f172a !important;

    font-size: 14px;

    font-weight: 800;

    margin-top: 7px;
}

.workflow-arrow {
    color: #6366f1 !important;

    font-size: 25px;

    font-weight: 900;
}


/* ============================================================
   INFORMATION BOX
   ============================================================ */

.info-box {
    padding: 19px;

    border-radius: 15px;

    background:
        linear-gradient(
            135deg,
            #eff6ff,
            #dbeafe
        );

    border: 1px solid #93c5fd;

    color: #1e3a8a !important;

    margin: 15px 0;
}

.info-box * {
    color: #1e3a8a !important;
}


/* ============================================================
   METRIC CARDS
   ============================================================ */

.metric-card {
    min-height: 130px;

    padding: 18px 8px;

    text-align: center;

    border-radius: 18px;

    background:
        linear-gradient(
            145deg,
            #f8fafc,
            #e2e8f0
        );

    border: 1px solid #cbd5e1;

    box-shadow:
        0 12px 30px rgba(15, 23, 42, 0.10);
}

.metric-icon {
    font-size: 27px;
}

.metric-value {
    font-size: 34px;

    font-weight: 900;

    color: #0f172a !important;

    margin-top: 3px;
}

.metric-label {
    color: #475569 !important;

    font-size: 11px;

    font-weight: 850;
}

.metric-blue {
    border-top: 4px solid #38bdf8;
}

.metric-red {
    border-top: 4px solid #ef4444;
}

.metric-orange {
    border-top: 4px solid #f59e0b;
}

.metric-green {
    border-top: 4px solid #22c55e;
}

.metric-purple {
    border-top: 4px solid #a855f7;
}


/* ============================================================
   HUMAN REVIEW
   ============================================================ */

.review-box {
    margin-top: 30px;

    padding: 22px;

    border-radius: 17px;

    background:
        linear-gradient(
            135deg,
            #fff7ed,
            #ffedd5
        );

    border: 1px solid #f59e0b;

    color: #92400e !important;
}

.review-box * {
    color: #92400e !important;
}


/* ============================================================
   EXPANDER
   ============================================================ */

[data-testid="stExpander"] {
    border: 1px solid #cbd5e1 !important;

    border-radius: 15px !important;

    background-color: #ffffff !important;

    color: #111827 !important;
}


/* ============================================================
   EXPANDER HEADER
   ============================================================ */

[data-testid="stExpander"] summary {
    background-color: #171a21 !important;

    color: #ffffff !important;

    border-radius: 14px 14px 0 0 !important;
}

[data-testid="stExpander"] summary span {
    color: #ffffff !important;
}

[data-testid="stExpander"] summary p {
    color: #ffffff !important;
}

[data-testid="stExpander"] summary * {
    color: #ffffff !important;
}


/* ============================================================
   EXPANDER CONTENT
   ============================================================ */

[data-testid="stExpander"] > div {
    background-color: #ffffff !important;
}

[data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
    color: #111827 !important;
}

[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
    color: #111827 !important;
}

[data-testid="stExpander"] [data-testid="stMarkdownContainer"] strong {
    color: #111827 !important;
}

[data-testid="stExpander"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] h3,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] h4,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] h5,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] h6 {
    color: #0f172a !important;
}


/* ============================================================
   REPORT TEXT
   ============================================================ */

[data-testid="stExpander"] .stMarkdown {
    color: #111827 !important;
}

[data-testid="stExpander"] .stMarkdown p {
    color: #111827 !important;
}


/* ============================================================
   ALERTS
   ============================================================ */

[data-testid="stAlert"] {
    color: #111827 !important;
}

[data-testid="stAlert"] p {
    color: #111827 !important;
}


/* ============================================================
   FILE UPLOADER
   ============================================================ */

[data-testid="stFileUploader"] {
    background: #f8fafc !important;

    border: 1px dashed #94a3b8;

    border-radius: 15px;

    padding: 10px;
}

[data-testid="stFileUploader"] label {
    color: #1e293b !important;
}

[data-testid="stFileUploader"] section {
    background: #f8fafc !important;
}

[data-testid="stFileUploader"] small {
    color: #64748b !important;
}


/* ============================================================
   BUTTON
   ============================================================ */

.stButton > button {
    min-height: 52px;

    border-radius: 13px;

    font-size: 16px;

    font-weight: 850;
}


/* ============================================================
   DOWNLOAD BUTTON
   ============================================================ */

.stDownloadButton > button {
    min-height: 52px;

    border-radius: 13px;

    font-size: 16px;

    font-weight: 850;
}


/* ============================================================
   CODE BLOCKS
   ============================================================ */

[data-testid="stCode"] {
    border-radius: 10px;
}


/* ============================================================
   DIVIDERS
   ============================================================ */

hr {
    border-color: #e2e8f0 !important;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {
    margin-top: 50px;

    padding: 28px;

    text-align: center;

    border-top: 1px solid #cbd5e1;

    color: #64748b !important;

    line-height: 1.8;
}

.footer * {
    color: #64748b !important;
}


/* ============================================================
   CAPTIONS
   ============================================================ */

.stCaption {
    color: #64748b !important;
}


/* ============================================================
   GENERAL TEXT
   ============================================================ */

[data-testid="stText"] {
    color: #111827 !important;
}


/* ============================================================
   FINAL WHITE BACKGROUND
   ============================================================ */

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.block-container {
    background-color: #ffffff !important;
}

</style>
""")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html("""
    <div class="sidebar-brand">
    🛡️ ComplyCrew
    </div>
    """)

    st.caption(
        "AI Compliance Intelligence"
    )

    st.divider()

    st.markdown(
        "### 🟢 System Status"
    )

    render_html("""
    <div class="status-card">
    🟢 Gemma 2B — Local AI
    </div>

    <div class="status-card">
    🟢 ChromaDB — Active
    </div>

    <div class="status-card">
    🟢 Multi-Agent Pipeline — Ready
    </div>
    """)

    st.divider()

    st.markdown(
        "### 🤖 Agent Pipeline"
    )

    st.write(
        "① 📄 Extractor Agent"
    )

    st.write(
        "② 🔎 Rule Matcher Agent"
    )

    st.write(
        "③ ⚠️ Risk Scorer Agent"
    )

    st.write(
        "④ 🔍 Verifier Agent"
    )

    st.write(
        "⑤ 📑 Report Writer Agent"
    )

    st.divider()

    st.markdown(
        "### 🔐 Privacy First"
    )

    st.caption(
        "The AI analysis uses the locally "
        "running Gemma 2B model through Ollama."
    )

    st.divider()

    st.caption(
        "Avinya 2.0 • AI Agents"
    )


# ============================================================
# HERO SECTION
# ============================================================

render_html("""
<div class="hero">

<div class="hero-title">
🛡️ ComplyCrew
</div>

<div class="hero-subtitle">
AI-Powered Compliance Analysis & Risk Detection
</div>

<div class="hero-description">
Analyze policies, contracts and SOPs against a
structured compliance rulebook. ComplyCrew uses
specialized AI agents to identify potential risks,
verify findings and generate evidence-backed
remediation recommendations.
</div>

<span class="hero-badge">
● LOCAL AI
&nbsp; • &nbsp;
MULTI-AGENT
&nbsp; • &nbsp;
HUMAN-IN-THE-LOOP
</span>

</div>
""")


# ============================================================
# WORKFLOW SECTION
# ============================================================

st.markdown(
    "### 🤖 AI Agent Workflow"
)

st.markdown(
    "Each agent performs a specialized step "
    "in the compliance analysis."
)


render_html("""
<div class="workflow-container">

<div class="workflow-card">

<div class="workflow-number">
01
</div>

<div class="workflow-icon">
📄
</div>

<div class="workflow-name">
Extract
</div>

</div>

<div class="workflow-arrow">
→
</div>

<div class="workflow-card">

<div class="workflow-number">
02
</div>

<div class="workflow-icon">
🔎
</div>

<div class="workflow-name">
Match Rules
</div>

</div>

<div class="workflow-arrow">
→
</div>

<div class="workflow-card">

<div class="workflow-number">
03
</div>

<div class="workflow-icon">
⚠️
</div>

<div class="workflow-name">
Assess Risk
</div>

</div>

<div class="workflow-arrow">
→
</div>

<div class="workflow-card">

<div class="workflow-number">
04
</div>

<div class="workflow-icon">
🔍
</div>

<div class="workflow-name">
Verify
</div>

</div>

<div class="workflow-arrow">
→
</div>

<div class="workflow-card">

<div class="workflow-number">
05
</div>

<div class="workflow-icon">
📑
</div>

<div class="workflow-name">
Generate Report
</div>

</div>

</div>
""")


# ============================================================
# FILE READER
# ============================================================

def read_uploaded_file(uploaded_file):

    extension = (
        uploaded_file.name
        .split(".")[-1]
        .lower()
    )

    # --------------------------------------------------------
    # TXT
    # --------------------------------------------------------

    if extension == "txt":

        return uploaded_file.read().decode(
            "utf-8",
            errors="ignore"
        )


    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if extension == "pdf":

        from pypdf import PdfReader

        temp_path = None

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getvalue()
                )

                temp_path = temp_file.name


            reader = PdfReader(
                temp_path
            )

            text = ""

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:

                    text += (
                        page_text
                        + "\n"
                    )

            return text

        finally:

            if (
                temp_path
                and os.path.exists(temp_path)
            ):

                os.remove(
                    temp_path
                )


    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    if extension == "docx":

        from docx import Document

        temp_path = None

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".docx"
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getvalue()
                )

                temp_path = temp_file.name


            document = Document(
                temp_path
            )

            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            )

            return text

        finally:

            if (
                temp_path
                and os.path.exists(temp_path)
            ):

                os.remove(
                    temp_path
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
# UPLOAD SECTION
# ============================================================

st.markdown(
    "### 📄 Upload Compliance Document"
)

st.markdown(
    "Upload a privacy policy, contract, SOP "
    "or other compliance document."
)


uploaded_file = st.file_uploader(
    "Choose a compliance document",
    type=[
        "pdf",
        "docx",
        "txt"
    ],
    label_visibility="collapsed"
)


# ============================================================
# DOCUMENT UPLOADED
# ============================================================

if uploaded_file:

    st.success(
        f"📎 {uploaded_file.name} "
        "loaded successfully"
    )


    render_html("""
    <div class="info-box">

    <strong>🚀 Ready for AI Analysis</strong>

    <br><br>

    Your document will pass through five
    specialized agents:

    <br><br>

    📄 Extraction
    →
    🔎 Rule Matching
    →
    ⚠️ Risk Assessment
    →
    🔍 Verification
    →
    📑 Report Generation

    </div>
    """)


    analyze = st.button(
        "🚀 ANALYZE DOCUMENT",
        type="primary",
        use_container_width=True
    )


    # ========================================================
    # RUN ANALYSIS
    # ========================================================

    if analyze:

        document_text = read_uploaded_file(
            uploaded_file
        )


        if not document_text.strip():

            st.error(
                "❌ Could not extract text "
                "from the document."
            )

            st.stop()


        st.divider()

        st.markdown(
            "### ⚙️ Multi-Agent Analysis"
        )


        progress = st.progress(
            0
        )

        status = st.empty()


        # ====================================================
        # AGENT 1 — EXTRACTOR
        # ====================================================

        status.info(
            "📄 Extractor Agent → "
            "extracting document clauses..."
        )

        progress.progress(
            10
        )


        extracted_clauses = extract_clauses(
            document_text
        )


        clauses = parse_clauses(
            extracted_clauses
        )


        if not clauses:

            st.error(
                "❌ No clauses could be extracted."
            )

            st.stop()


        progress.progress(
            25
        )


        status.success(
            f"✅ Extractor completed — "
            f"{len(clauses)} clauses identified."
        )


        # ====================================================
        # PROCESS EACH CLAUSE
        # ====================================================

        all_results = []


        for index, clause in enumerate(
            clauses,
            start=1
        ):

            # ------------------------------------------------
            # AGENT 2 — RULE MATCHER
            # ------------------------------------------------

            status.info(
                f"🔎 Rule Matcher Agent → "
                f"analyzing clause "
                f"{index}/{len(clauses)}"
            )


            matched_rule = match_rules(
                clause
            )


            # ------------------------------------------------
            # POTENTIAL ISSUE
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

            status.warning(
                f"⚠️ Risk Scorer Agent → "
                f"assessing clause "
                f"{index}/{len(clauses)}"
            )


            risk_result = score_risk(
                clause,
                matched_rule,
                potential_issue
            )


            # ------------------------------------------------
            # AGENT 4 — VERIFIER
            # ------------------------------------------------

            status.info(
                f"🔍 Verifier Agent → "
                f"verifying clause "
                f"{index}/{len(clauses)}"
            )


            verification_result = verify_finding(
                clause,
                matched_rule,
                risk_result
            )


            # ------------------------------------------------
            # AGENT 5 — REPORT WRITER
            # ------------------------------------------------

            status.info(
                f"📑 Report Writer Agent → "
                f"generating finding "
                f"{index}/{len(clauses)}"
            )


            report = write_report(
                clause,
                matched_rule,
                risk_result,
                verification_result
            )


            # ------------------------------------------------
            # STORE RESULT
            # ------------------------------------------------

            all_results.append(
                {
                    "clause": clause,
                    "matched_rule": matched_rule,
                    "risk_result": risk_result,
                    "verification": verification_result,
                    "report": report
                }
            )


            progress.progress(
                25
                + int(
                    index
                    / len(clauses)
                    * 75
                )
            )


        progress.progress(
            100
        )


        status.success(
            "🎉 All five AI agents "
            "completed successfully!"
        )


        st.session_state[
            "results"
        ] = all_results


        st.session_state[
            "document_name"
        ] = uploaded_file.name


# ============================================================
# RESULTS
# ============================================================

if "results" in st.session_state:

    results = st.session_state[
        "results"
    ]


    document_name = st.session_state.get(
        "document_name",
        "Document"
    )


    st.divider()


    st.markdown(
        "### 📊 Compliance Overview"
    )


    render_html(
        f"""
        <div class="info-box">
        📄 <strong>Analyzed Document:</strong>
        {document_name}
        </div>
        """
    )


    # ========================================================
    # COUNT RISKS
    # ========================================================

    high_count = 0
    medium_count = 0
    low_count = 0
    review_count = 0


    for result in results:

        risk_text = result[
            "risk_result"
        ].upper()


        verification_text = result[
            "verification"
        ].upper()


        if re.search(
            r"RISK LEVEL\s*:\s*HIGH",
            risk_text
        ):

            high_count += 1


        elif re.search(
            r"RISK LEVEL\s*:\s*MEDIUM",
            risk_text
        ):

            medium_count += 1


        elif re.search(
            r"RISK LEVEL\s*:\s*LOW",
            risk_text
        ):

            low_count += 1


        if (
            "NEEDS_REVIEW"
            in verification_text
        ):

            review_count += 1


    # ========================================================
    # METRIC CARDS
    # ========================================================

    m1, m2, m3, m4, m5 = st.columns(
        5
    )


    with m1:

        render_html(
            f"""
            <div class="metric-card metric-blue">

            <div class="metric-icon">
            📄
            </div>

            <div class="metric-value">
            {len(results)}
            </div>

            <div class="metric-label">
            CLAUSES ANALYZED
            </div>

            </div>
            """
        )


    with m2:

        render_html(
            f"""
            <div class="metric-card metric-red">

            <div class="metric-icon">
            🔴
            </div>

            <div class="metric-value">
            {high_count}
            </div>

            <div class="metric-label">
            HIGH RISK
            </div>

            </div>
            """
        )


    with m3:

        render_html(
            f"""
            <div class="metric-card metric-orange">

            <div class="metric-icon">
            🟠
            </div>

            <div class="metric-value">
            {medium_count}
            </div>

            <div class="metric-label">
            MEDIUM RISK
            </div>

            </div>
            """
        )


    with m4:

        render_html(
            f"""
            <div class="metric-card metric-green">

            <div class="metric-icon">
            🟢
            </div>

            <div class="metric-value">
            {low_count}
            </div>

            <div class="metric-label">
            LOW RISK
            </div>

            </div>
            """
        )


    with m5:

        render_html(
            f"""
            <div class="metric-card metric-purple">

            <div class="metric-icon">
            🔍
            </div>

            <div class="metric-value">
            {review_count}
            </div>

            <div class="metric-label">
            NEEDS REVIEW
            </div>

            </div>
            """
        )


    # ========================================================
    # FINDINGS
    # ========================================================

    st.markdown(
        "### 🔍 Compliance Findings"
    )


    st.markdown(
        "Evidence-backed findings generated "
        "by the multi-agent system."
    )


    for index, result in enumerate(
        results,
        start=1
    ):

        clause = result[
            "clause"
        ]

        matched_rule = result[
            "matched_rule"
        ]

        risk_result = result[
            "risk_result"
        ]

        verification = result[
            "verification"
        ]

        report = result[
            "report"
        ]


        # ====================================================
        # RISK LEVEL
        # ====================================================

        risk_match = re.search(
            r"RISK LEVEL\s*:\s*"
            r"(HIGH|MEDIUM|LOW)",
            risk_result,
            re.IGNORECASE
        )


        if risk_match:

            risk_level = (
                risk_match
                .group(1)
                .upper()
            )

        else:

            risk_level = "UNKNOWN"


        # ====================================================
        # VERIFICATION
        # ====================================================

        verification_match = re.search(
            r"VERIFICATION\s*:\s*"
            r"(VERIFIED|NEEDS_REVIEW)",
            verification,
            re.IGNORECASE
        )


        if verification_match:

            verification_status = (
                verification_match
                .group(1)
                .upper()
            )

        else:

            verification_status = "UNKNOWN"


        # ====================================================
        # ICON
        # ====================================================

        if risk_level == "HIGH":

            icon = "🔴"

        elif risk_level == "MEDIUM":

            icon = "🟠"

        elif risk_level == "LOW":

            icon = "🟢"

        else:

            icon = "⚪"


        # ====================================================
        # FINDING EXPANDER
        # ====================================================

        with st.expander(
            f"{icon} Finding {index} | "
            f"{risk_level} RISK | "
            f"{verification_status}",
            expanded=(index == 1)
        ):

            left, right = st.columns(
                [2.2, 1]
            )


            with left:

                st.markdown(
                    "#### 📋 AI-Generated Finding"
                )

                st.write(
                    report
                )


            with right:

                st.markdown(
                    "#### 🎯 Assessment"
                )


                if risk_level == "HIGH":

                    st.error(
                        "🔴 HIGH RISK"
                    )

                elif risk_level == "MEDIUM":

                    st.warning(
                        "🟠 MEDIUM RISK"
                    )

                elif risk_level == "LOW":

                    st.success(
                        "🟢 LOW RISK"
                    )

                else:

                    st.info(
                        "⚪ UNKNOWN"
                    )


                if (
                    verification_status
                    == "VERIFIED"
                ):

                    st.success(
                        "✅ VERIFIED"
                    )

                elif (
                    verification_status
                    == "NEEDS_REVIEW"
                ):

                    st.warning(
                        "🔍 NEEDS HUMAN REVIEW"
                    )


            st.divider()


            # =================================================
            # EVIDENCE CHAIN
            # =================================================

            st.markdown(
                "#### 🔗 Evidence Chain"
            )


            e1, e2, e3, e4, e5 = st.columns(
                5
            )


            with e1:

                st.info(
                    "📄\n\n**DOCUMENT**"
                )


            with e2:

                st.info(
                    "📚\n\n**RULE**"
                )


            with e3:

                if risk_level == "HIGH":

                    st.error(
                        "🔴\n\n**RISK**"
                    )

                elif risk_level == "MEDIUM":

                    st.warning(
                        "🟠\n\n**RISK**"
                    )

                else:

                    st.success(
                        "🟢\n\n**RISK**"
                    )


            with e4:

                if (
                    verification_status
                    == "VERIFIED"
                ):

                    st.success(
                        "✅\n\n**VERIFIED**"
                    )

                else:

                    st.warning(
                        "🔍\n\n**REVIEW**"
                    )


            with e5:

                st.info(
                    "🛠️\n\n**REMEDIATION**"
                )


            # =================================================
            # DOCUMENT EVIDENCE
            # =================================================

            st.markdown(
                "#### 📄 Document Evidence"
            )


            st.code(
                clause,
                language="text"
            )


            # =================================================
            # RETRIEVED RULE
            # =================================================

            st.markdown(
                "#### 📚 Retrieved Compliance Rule"
            )


            st.code(
                matched_rule,
                language="text"
            )


            # =================================================
            # DETAILED AGENT OUTPUT
            # =================================================

            with st.expander(
                "🧠 View Detailed Agent Outputs"
            ):

                st.markdown(
                    "##### ⚠️ Risk Scorer Agent"
                )


                st.code(
                    risk_result,
                    language="text"
                )


                st.markdown(
                    "##### 🔍 Verifier Agent"
                )


                st.code(
                    verification,
                    language="text"
                )


# ============================================================
# FINAL REPORT
# ============================================================

if "results" in st.session_state:

    st.divider()


    st.markdown(
        "### 📑 Final Compliance Report"
    )


    st.markdown(
        "Consolidated report generated "
        "by the Report Writer Agent."
    )


    final_report = ""


    for index, result in enumerate(
        st.session_state["results"],
        start=1
    ):

        final_report += (
            "\n\n"
            "========================================\n"
            f"COMPLIANCE FINDING {index}\n"
            "========================================\n\n"
        )

        final_report += (
            result["report"]
        )


    st.download_button(
        label="⬇️ DOWNLOAD COMPLIANCE REPORT",
        data=final_report,
        file_name="ComplyCrew_Compliance_Report.txt",
        mime="text/plain",
        use_container_width=True
    )


    # ========================================================
    # HUMAN REVIEW
    # ========================================================

    render_html("""
    <div class="review-box">

    👤 <strong>Human-in-the-Loop</strong>

    <br><br>

    Findings marked
    <strong>NEEDS_REVIEW</strong>
    require human verification before any
    final compliance decision is made.

    </div>
    """)


# ============================================================
# FOOTER
# ============================================================

render_html("""
<div class="footer">

🛡️ <strong>ComplyCrew</strong>

<br>

Multi-Agent Regulatory Compliance Checker

<br><br>

<strong>Avinya 2.0 • AI Agents</strong>

<br>

Local Gemma 2B + ChromaDB +
Multi-Agent Architecture

<br><br>

AI-generated findings are recommendations
and are not legal verdicts.

</div>
""")