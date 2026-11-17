import { useState } from "react";
import axios from "axios";

import {
  LayoutDashboard,
  FileSearch,
  ShieldCheck,
  Settings,
  Upload,
  FileText,
  CheckCircle,
  AlertTriangle,
  AlertCircle,
  Clock,
  Activity,
  ArrowRight,
  Lock,
  Users,
  Database,
  RefreshCw,
  BookOpen,
  Server,
  ChevronRight,
  Eye,
} from "lucide-react";

import "./App.css";


function App() {

  // =========================================================
  // STATE
  // =========================================================

  const [selectedFile, setSelectedFile] =
    useState(null);

  const [activeNav, setActiveNav] =
    useState("Dashboard");

  const [message, setMessage] =
    useState("");

  const [analyzing, setAnalyzing] =
    useState(false);

  const [analysisResult, setAnalysisResult] =
    useState(null);

  const [savedDocuments, setSavedDocuments] =
    useState([]);


  // =========================================================
  // NAVIGATION
  // =========================================================

  const navigationItems = [
    {
      name: "Dashboard",
      icon: LayoutDashboard,
    },
    {
      name: "Documents",
      icon: FileText,
    },
    {
      name: "Compliance",
      icon: ShieldCheck,
    },
    {
      name: "Settings",
      icon: Settings,
    },
  ];


  // =========================================================
  // RULEBOOK
  // =========================================================

  const rules = [
    {
      id: "R001",
      topic: "Notice and transparency",
      requirement:
        "An organization should provide individuals with clear information about what personal data is being collected and the purpose for which it is being processed.",
      risk: "High",
    },

    {
      id: "R002",
      topic: "Consent",
      requirement:
        "Where consent is the applicable basis for processing personal data, consent should be informed, specific, clear and capable of being withdrawn.",
      risk: "High",
    },

    {
      id: "R003",
      topic: "Purpose limitation",
      requirement:
        "Personal data should be processed for a lawful and specified purpose and should not be used for unrelated purposes without an appropriate legal basis.",
      risk: "High",
    },

    {
      id: "R004",
      topic: "Data minimization",
      requirement:
        "An organization should avoid collecting personal data that is unnecessary for the stated purpose.",
      risk: "Medium",
    },

    {
      id: "R005",
      topic: "Data security",
      requirement:
        "Organizations should implement reasonable security safeguards to protect personal data against unauthorized access, use, alteration, disclosure or loss.",
      risk: "High",
    },

    {
      id: "R006",
      topic: "Data retention",
      requirement:
        "Personal data should not be retained when it is no longer necessary for the purpose for which it was processed, subject to applicable legal requirements.",
      risk: "Medium",
    },

    {
      id: "R007",
      topic: "Data sharing",
      requirement:
        "An organization should clearly address applicable conditions and purposes for sharing personal data with other organizations or third parties.",
      risk: "High",
    },

    {
      id: "R008",
      topic: "Individual rights",
      requirement:
        "The organization should provide appropriate mechanisms for individuals to exercise applicable rights relating to their personal data.",
      risk: "Medium",
    },

    {
      id: "R009",
      topic: "Grievance handling",
      requirement:
        "The organization should provide a mechanism through which individuals can raise complaints or grievances relating to personal data processing.",
      risk: "Medium",
    },

    {
      id: "R010",
      topic: "Children's data",
      requirement:
        "Where personal data relates to children, the organization should apply the additional requirements and safeguards applicable to children's personal data.",
      risk: "High",
    },
  ];


  // =========================================================
  // FILE SELECTION
  // =========================================================

  const handleFileChange = (event) => {

    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    setSelectedFile(file);

    setAnalysisResult(null);

    setMessage(
      `Selected: ${file.name}`
    );

    setActiveNav("Dashboard");
  };


  // =========================================================
  // ANALYZE DOCUMENT
  // =========================================================

  const handleAnalyze = async () => {

    if (!selectedFile) {

      setMessage(
        "Please select a document first."
      );

      return;
    }

    setAnalyzing(true);

    setMessage(
      "Analyzing document with ComplyCrew AI agents..."
    );

    setAnalysisResult(null);

    const formData =
      new FormData();

    formData.append(
      "file",
      selectedFile
    );

    try {

      console.log(
        "Sending document to backend..."
      );

      const response =
        await axios.post(
          "http://127.0.0.1:8000/analyze",
          formData,
          {
            headers: {
              "Content-Type":
                "multipart/form-data",
            },

            timeout: 600000,
          }
        );

      console.log(
        "Backend response:",
        response.data
      );


      if (!response.data) {

        throw new Error(
          "The backend returned an empty response."
        );

      }


      if (
        response.data.success === false
      ) {

        throw new Error(
          response.data.error ||
          "Document analysis failed."
        );

      }


      // ---------------------------------------------
      // SAVE ANALYSIS RESULT
      // ---------------------------------------------

      setAnalysisResult(
        response.data
      );


      // ---------------------------------------------
      // SAVE DOCUMENT HISTORY
      // ---------------------------------------------

      setSavedDocuments(
        (previous) => [

          ...previous,

          {
            name:
              selectedFile.name,

            size:
              selectedFile.size,

            clauses:
              response.data
                .clauses_analyzed || 0,

            findings:
              response.data
                .findings || [],

            analyzedAt:
              new Date()
                .toLocaleString(),
          },

        ]
      );


      setMessage(
        `Analysis completed successfully. ${
          response.data
            .clauses_analyzed || 0
        } clauses analyzed.`
      );


    } catch (error) {

      console.error(
        "Analysis error:",
        error
      );


      let errorMessage =
        "Unable to analyze the document.";


      if (
        error.response &&
        error.response.data
      ) {

        errorMessage =
          error.response.data.error ||
          error.response.data.message ||
          errorMessage;

      } else if (
        error.message
      ) {

        errorMessage =
          error.message;

      }


      setMessage(
        `Error: ${errorMessage}`
      );

      setAnalysisResult(null);


    } finally {

      setAnalyzing(false);

    }

  };


  // =========================================================
  // FINDINGS
  // =========================================================

  const findings =
    analysisResult?.findings || [];


  const highRiskCount =
    findings.filter(
      (finding) =>
        String(
          finding.risk || ""
        )
          .toUpperCase()
          .includes("HIGH")
    ).length;


  const lowRiskCount =
    findings.filter(
      (finding) =>
        String(
          finding.risk || ""
        )
          .toUpperCase()
          .includes("LOW")
    ).length;


  const reviewCount =
    findings.filter(
      (finding) =>
        finding.human_review === true
    ).length;


  // =========================================================
  // NAVIGATION PAGE — DOCUMENTS
  // =========================================================

  const renderDocumentsPage = () => {

    return (

      <section
        style={{
          paddingTop: "30px",
        }}
      >

        {/* HEADER */}

        <div
          style={{
            display: "flex",
            justifyContent:
              "space-between",
            alignItems: "flex-start",
            marginBottom: "30px",
          }}
        >

          <div>

            <span className="eyebrow">
              DOCUMENT MANAGEMENT
            </span>

            <h2
              style={{
                fontSize: "34px",
                margin:
                  "8px 0 10px",
              }}
            >
              Documents
            </h2>

            <p
              style={{
                color: "#64748b",
                maxWidth: "650px",
                lineHeight: "1.7",
              }}
            >
              View documents analyzed by
              ComplyCrew and review their
              analysis information.
            </p>

          </div>


          <div
            style={{
              width: "60px",
              height: "60px",
              borderRadius: "16px",
              background:
                "#eef2ff",
              display: "flex",
              alignItems: "center",
              justifyContent:
                "center",
              color: "#4f46e5",
            }}
          >
            <FileText size={30} />
          </div>

        </div>


        {/* CURRENT FILE */}

        {selectedFile && (

          <div
            style={{
              background: "#f8fafc",
              border:
                "1px solid #e2e8f0",
              borderRadius: "16px",
              padding: "20px",
              marginBottom: "24px",
              display: "flex",
              alignItems: "center",
              gap: "16px",
            }}
          >

            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                background:
                  "#eef2ff",
                display: "flex",
                alignItems: "center",
                justifyContent:
                  "center",
                color: "#4f46e5",
              }}
            >
              <FileText size={23} />
            </div>


            <div
              style={{
                flex: 1,
              }}
            >

              <strong>
                Current document
              </strong>

              <div
                style={{
                  marginTop: "4px",
                  color: "#475569",
                }}
              >
                {selectedFile.name}
              </div>

            </div>


            {analysisResult && (

              <button
                className="page-action-button"
                onClick={() =>
                  setActiveNav(
                    "Dashboard"
                  )
                }
              >
                View Analysis
                <ArrowRight
                  size={17}
                />
              </button>

            )}

          </div>

        )}


        {/* HISTORY */}

        {savedDocuments.length === 0 ? (

          <div
            style={{
              background: "#ffffff",
              border:
                "1px solid #e2e8f0",
              borderRadius: "18px",
              padding: "60px 30px",
              textAlign: "center",
            }}
          >

            <FileSearch
              size={45}
              color="#94a3b8"
            />

            <h3
              style={{
                marginTop: "18px",
              }}
            >
              No documents analyzed yet
            </h3>

            <p
              style={{
                color: "#64748b",
                margin:
                  "8px auto 22px",
                maxWidth: "450px",
              }}
            >
              Upload a TXT, PDF or DOCX
              document from the Dashboard
              to start your first analysis.
            </p>

            <button
              className="page-action-button"
              onClick={() =>
                setActiveNav(
                  "Dashboard"
                )
              }
            >
              Go to Dashboard
              <ArrowRight size={17} />
            </button>

          </div>

        ) : (

          <div>

            <h3
              style={{
                marginBottom: "16px",
              }}
            >
              Analysis History
            </h3>


            <div
              style={{
                display: "flex",
                flexDirection:
                  "column",
                gap: "14px",
              }}
            >

              {savedDocuments
                .slice()
                .reverse()
                .map(
                  (
                    document,
                    index
                  ) => (

                    <div
                      key={
                        `${document.name}-${index}`
                      }
                      style={{
                        background:
                          "#ffffff",
                        border:
                          "1px solid #e2e8f0",
                        borderRadius:
                          "16px",
                        padding: "20px",
                        display:
                          "flex",
                        alignItems:
                          "center",
                        gap: "16px",
                      }}
                    >

                      <div
                        style={{
                          width: "48px",
                          height: "48px",
                          borderRadius:
                            "12px",
                          background:
                            "#f1f5f9",
                          display:
                            "flex",
                          alignItems:
                            "center",
                          justifyContent:
                            "center",
                          color:
                            "#475569",
                        }}
                      >
                        <FileText
                          size={23}
                        />
                      </div>


                      <div
                        style={{
                          flex: 1,
                        }}
                      >

                        <h4
                          style={{
                            margin:
                              "0 0 5px",
                          }}
                        >
                          {
                            document.name
                          }
                        </h4>

                        <p
                          style={{
                            margin:
                              "0 0 5px",
                            color:
                              "#64748b",
                          }}
                        >
                          {(
                            document.size /
                            1024
                          ).toFixed(
                            1
                          )} KB
                          {" • "}
                          {
                            document.clauses
                          }{" "}
                          clauses
                        </p>

                        <span
                          style={{
                            fontSize:
                              "12px",
                            color:
                              "#94a3b8",
                          }}
                        >
                          Analyzed{" "}
                          {
                            document.analyzedAt
                          }
                        </span>

                      </div>


                      <div
                        style={{
                          textAlign:
                            "center",
                          minWidth:
                            "80px",
                        }}
                      >

                        <strong
                          style={{
                            display:
                              "block",
                            fontSize:
                              "22px",
                          }}
                        >
                          {
                            document.findings
                              .length
                          }
                        </strong>

                        <span
                          style={{
                            color:
                              "#64748b",
                            fontSize:
                              "12px",
                          }}
                        >
                          Findings
                        </span>

                      </div>


                      <button
                        className="page-action-button"
                        onClick={() =>
                          setActiveNav(
                            "Dashboard"
                          )
                        }
                      >
                        <Eye
                          size={16}
                        />
                        View
                      </button>

                    </div>

                  )
                )}

            </div>

          </div>

        )}

      </section>

    );

  };


  // =========================================================
  // NAVIGATION PAGE — COMPLIANCE
  // =========================================================

  const renderCompliancePage = () => {

    return (

      <section
        style={{
          paddingTop: "30px",
        }}
      >

        <div
          style={{
            display: "flex",
            justifyContent:
              "space-between",
            alignItems:
              "flex-start",
            marginBottom:
              "30px",
          }}
        >

          <div>

            <span className="eyebrow">
              COMPLIANCE RULEBOOK
            </span>

            <h2
              style={{
                fontSize:
                  "34px",
                margin:
                  "8px 0 10px",
              }}
            >
              Compliance Rules
            </h2>

            <p
              style={{
                color:
                  "#64748b",
                maxWidth:
                  "680px",
                lineHeight:
                  "1.7",
              }}
            >
              These prototype rules are
              used by the Rule Matcher
              Agent to identify relevant
              compliance requirements.
            </p>

          </div>


          <div
            style={{
              width: "60px",
              height: "60px",
              borderRadius:
                "16px",
              background:
                "#eef2ff",
              display:
                "flex",
              alignItems:
                "center",
              justifyContent:
                "center",
              color:
                "#4f46e5",
            }}
          >
            <BookOpen
              size={30}
            />
          </div>

        </div>


        <div
          style={{
            display:
              "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(300px, 1fr))",
            gap: "18px",
          }}
        >

          {rules.map(
            (rule) => (

              <div
                key={rule.id}
                style={{
                  background:
                    "#ffffff",
                  border:
                    "1px solid #e2e8f0",
                  borderRadius:
                    "18px",
                  padding:
                    "22px",
                  transition:
                    "transform 0.2s",
                }}
              >

                <div
                  style={{
                    display:
                      "flex",
                    justifyContent:
                      "space-between",
                    alignItems:
                      "center",
                    marginBottom:
                      "15px",
                  }}
                >

                  <span
                    style={{
                      fontWeight:
                        "700",
                      color:
                        "#4f46e5",
                      background:
                        "#eef2ff",
                      padding:
                        "6px 10px",
                      borderRadius:
                        "8px",
                      fontSize:
                        "13px",
                    }}
                  >
                    {rule.id}
                  </span>


                  <span
                    className={`risk-badge ${rule.risk.toLowerCase()}`}
                  >
                    {rule.risk}
                  </span>

                </div>


                <h3
                  style={{
                    margin:
                      "0 0 10px",
                    fontSize:
                      "18px",
                  }}
                >
                  {rule.topic}
                </h3>


                <p
                  style={{
                    color:
                      "#64748b",
                    lineHeight:
                      "1.6",
                    fontSize:
                      "14px",
                    margin:
                      "0",
                  }}
                >
                  {rule.requirement}
                </p>

              </div>

            )
          )}

        </div>

      </section>

    );

  };


  // =========================================================
  // NAVIGATION PAGE — SETTINGS
  // =========================================================

  const renderSettingsPage = () => {

    return (

      <section
        style={{
          paddingTop: "30px",
        }}
      >

        <div
          style={{
            display:
              "flex",
            justifyContent:
              "space-between",
            alignItems:
              "flex-start",
            marginBottom:
              "30px",
          }}
        >

          <div>

            <span className="eyebrow">
              SYSTEM CONFIGURATION
            </span>

            <h2
              style={{
                fontSize:
                  "34px",
                margin:
                  "8px 0 10px",
              }}
            >
              Settings
            </h2>

            <p
              style={{
                color:
                  "#64748b",
                maxWidth:
                  "650px",
                lineHeight:
                  "1.7",
              }}
            >
              View the current AI engine,
              processing mode, rulebook
              and risk-based review
              configuration.
            </p>

          </div>


          <div
            style={{
              width: "60px",
              height: "60px",
              borderRadius:
                "16px",
              background:
                "#eef2ff",
              display:
                "flex",
              alignItems:
                "center",
              justifyContent:
                "center",
              color:
                "#4f46e5",
            }}
          >
            <Settings
              size={30}
            />
          </div>

        </div>


        <div
          style={{
            display:
              "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(330px, 1fr))",
            gap: "18px",
          }}
        >

          {/* AI ENGINE */}

          <div
            style={{
              background:
                "#ffffff",
              border:
                "1px solid #e2e8f0",
              borderRadius:
                "18px",
              padding:
                "24px",
              display:
                "flex",
              gap:
                "16px",
              alignItems:
                "flex-start",
            }}
          >

            <div
              style={{
                width:
                  "48px",
                height:
                  "48px",
                borderRadius:
                  "12px",
                background:
                  "#eef2ff",
                display:
                  "flex",
                alignItems:
                  "center",
                justifyContent:
                  "center",
                color:
                  "#4f46e5",
              }}
            >
              <Server
                size={23}
              />
            </div>


            <div
              style={{
                flex: 1,
              }}
            >

              <h3
                style={{
                  margin:
                    "0 0 6px",
                }}
              >
                AI Engine
              </h3>

              <strong>
                Gemma 2B
              </strong>

              <p
                style={{
                  color:
                    "#64748b",
                  margin:
                    "6px 0 0",
                  lineHeight:
                    "1.5",
                }}
              >
                Running locally through
                Ollama.
              </p>

            </div>


            <span
              style={{
                background:
                  "#dcfce7",
                color:
                  "#15803d",
                padding:
                  "5px 9px",
                borderRadius:
                  "20px",
                fontSize:
                  "12px",
                fontWeight:
                  "700",
              }}
            >
              Connected
            </span>

          </div>


          {/* PRIVACY */}

          <div
            style={{
              background:
                "#ffffff",
              border:
                "1px solid #e2e8f0",
              borderRadius:
                "18px",
              padding:
                "24px",
              display:
                "flex",
              gap:
                "16px",
              alignItems:
                "flex-start",
            }}
          >

            <div
              style={{
                width:
                  "48px",
                height:
                  "48px",
                borderRadius:
                  "12px",
                background:
                  "#ecfdf5",
                display:
                  "flex",
                alignItems:
                  "center",
                justifyContent:
                  "center",
                color:
                  "#16a34a",
              }}
            >
              <Lock
                size={23}
              />
            </div>


            <div
              style={{
                flex: 1,
              }}
            >

              <h3
                style={{
                  margin:
                    "0 0 6px",
                }}
              >
                Processing Mode
              </h3>

              <strong>
                Local Processing
              </strong>

              <p
                style={{
                  color:
                    "#64748b",
                  margin:
                    "6px 0 0",
                  lineHeight:
                    "1.5",
                }}
              >
                Documents are processed
                through the local AI engine.
              </p>

            </div>


            <span
              style={{
                background:
                  "#dcfce7",
                color:
                  "#15803d",
                padding:
                  "5px 9px",
                borderRadius:
                  "20px",
                fontSize:
                  "12px",
                fontWeight:
                  "700",
              }}
            >
              Active
            </span>

          </div>


          {/* RULEBOOK */}

          <div
            style={{
              background:
                "#ffffff",
              border:
                "1px solid #e2e8f0",
              borderRadius:
                "18px",
              padding:
                "24px",
              display:
                "flex",
              gap:
                "16px",
              alignItems:
                "flex-start",
            }}
          >

            <div
              style={{
                width:
                  "48px",
                height:
                  "48px",
                borderRadius:
                  "12px",
                background:
                  "#fff7ed",
                display:
                  "flex",
                alignItems:
                  "center",
                justifyContent:
                  "center",
                color:
                  "#ea580c",
              }}
            >
              <BookOpen
                size={23}
              />
            </div>


            <div
              style={{
                flex: 1,
              }}
            >

              <h3
                style={{
                  margin:
                    "0 0 6px",
                }}
              >
                Rulebook
              </h3>

              <strong>
                ComplyCrew Prototype Rules
              </strong>

              <p
                style={{
                  color:
                    "#64748b",
                  margin:
                    "6px 0 0",
                }}
              >
                10 compliance rules
                are currently loaded.
              </p>

            </div>


            <button
              className="page-action-button"
              onClick={() =>
                setActiveNav(
                  "Compliance"
                )
              }
            >
              View
              <ChevronRight
                size={16}
              />
            </button>

          </div>


          {/* HUMAN REVIEW */}

          <div
            style={{
              background:
                "#ffffff",
              border:
                "1px solid #e2e8f0",
              borderRadius:
                "18px",
              padding:
                "24px",
              display:
                "flex",
              gap:
                "16px",
              alignItems:
                "flex-start",
            }}
          >

            <div
              style={{
                width:
                  "48px",
                height:
                  "48px",
                borderRadius:
                  "12px",
                background:
                  "#fef3c7",
                display:
                  "flex",
                alignItems:
                  "center",
                justifyContent:
                  "center",
                color:
                  "#d97706",
              }}
            >
              <Users
                size={23}
              />
            </div>


            <div
              style={{
                flex: 1,
              }}
            >

              <h3
                style={{
                  margin:
                    "0 0 6px",
                }}
              >
                Risk-Based Review
              </h3>

              <strong>
                Review only potential risks
              </strong>

              <p
                style={{
                  color:
                    "#64748b",
                  margin:
                    "6px 0 0",
                  lineHeight:
                    "1.5",
                }}
              >
                Findings without a potential
                issue do not require human
                review.
              </p>

            </div>


            <span
              style={{
                background:
                  "#dcfce7",
                color:
                  "#15803d",
                padding:
                  "5px 9px",
                borderRadius:
                  "20px",
                fontSize:
                  "12px",
                fontWeight:
                  "700",
              }}
            >
              Enabled
            </span>

          </div>

        </div>


        {/* ARCHITECTURE */}

        <div
          style={{
            marginTop:
              "24px",
            background:
              "#f8fafc",
            border:
              "1px solid #e2e8f0",
            borderRadius:
              "18px",
            padding:
              "24px",
          }}
        >

          <h3>
            Current AI Architecture
          </h3>

          <div
            style={{
              display:
                "flex",
              alignItems:
                "center",
              gap:
                "10px",
              flexWrap:
                "wrap",
              marginTop:
                "18px",
            }}
          >

            {[
              "Document",
              "Extractor",
              "Rule Matcher",
              "Risk Scorer",
              "Verifier",
            ].map(
              (step, index) => (

                <div
                  key={step}
                  style={{
                    display:
                      "flex",
                    alignItems:
                      "center",
                    gap:
                      "10px",
                  }}
                >

                  <span
                    style={{
                      padding:
                        "10px 15px",
                      background:
                        "#ffffff",
                      border:
                        "1px solid #e2e8f0",
                      borderRadius:
                        "10px",
                      fontWeight:
                        "600",
                      fontSize:
                        "14px",
                    }}
                  >
                    {step}
                  </span>

                  {index <
                    4 && (
                    <ArrowRight
                      size={17}
                      color="#94a3b8"
                    />
                  )}

                </div>

              )
            )}

          </div>

        </div>

      </section>

    );

  };


  // =========================================================
  // DASHBOARD
  // =========================================================

  const renderDashboard = () => {

    return (

      <>

        {/* ===================================================
            HERO
        =================================================== */}

        <section className="hero">

          <div className="hero-text">

            <span className="eyebrow">
              MULTI-AGENT COMPLIANCE ANALYSIS
            </span>

            <h2>
              Find compliance risks
              <br />
              before they become problems.
            </h2>

            <p>
              Upload a policy, contract or SOP.
              ComplyCrew uses specialized AI
              agents to extract clauses, match
              regulatory rules, assess risk and
              independently verify findings.
            </p>

          </div>


          <div className="hero-visual">

            <div className="hero-circle">

              <ShieldCheck
                size={72}
              />

            </div>

          </div>

        </section>


        {/* ===================================================
            STATS
        =================================================== */}

        <section className="stats-grid">

          {/* CLAUSES */}

          <div className="stat-card">

            <div className="stat-icon blue">
              <FileSearch
                size={21}
              />
            </div>

            <div>

              <span>
                Clauses Analyzed
              </span>

              <strong>
                {analysisResult
                  ? analysisResult
                      .clauses_analyzed ||
                    0
                  : "—"}
              </strong>

            </div>

          </div>


          {/* HIGH */}

          <div className="stat-card">

            <div className="stat-icon red">

              <AlertTriangle
                size={21}
              />

            </div>

            <div>

              <span>
                High Risk
              </span>

              <strong>
                {analysisResult
                  ? highRiskCount
                  : "—"}
              </strong>

            </div>

          </div>


          {/* REVIEW */}

          <div className="stat-card">

            <div className="stat-icon orange">

              <Clock
                size={21}
              />

            </div>

            <div>

              <span>
                Needs Review
              </span>

              <strong>
                {analysisResult
                  ? reviewCount
                  : "—"}
              </strong>

            </div>

          </div>


          {/* LOW */}

          <div className="stat-card">

            <div className="stat-icon green">

              <CheckCircle
                size={21}
              />

            </div>

            <div>

              <span>
                Low Risk
              </span>

              <strong>
                {analysisResult
                  ? lowRiskCount
                  : "—"}
              </strong>

            </div>

          </div>

        </section>


        {/* ===================================================
            UPLOAD + WORKFLOW
        =================================================== */}

        <section className="analysis-grid">

          {/* UPLOAD */}

          <div className="upload-panel">

            <div className="panel-header">

              <div>

                <h3>
                  Analyze a document
                </h3>

                <p>
                  Upload your compliance
                  document to start the
                  AI workflow.
                </p>

              </div>

              <FileText
                size={24}
              />

            </div>


            {!selectedFile ? (

              <label
                className="upload-box"
              >

                <input
                  type="file"
                  accept=".txt,.pdf,.docx"
                  onChange={
                    handleFileChange
                  }
                  hidden
                />

                <div className="upload-icon">

                  <Upload
                    size={25}
                  />

                </div>

                <strong>
                  Drop your document here
                </strong>

                <span>
                  or click to browse
                </span>

                <small>
                  TXT, PDF or DOCX
                </small>

              </label>

            ) : (

              <div className="selected-file">

                <div className="selected-file-icon">

                  <FileText
                    size={22}
                  />

                </div>


                <div className="selected-file-info">

                  <strong>
                    {
                      selectedFile.name
                    }
                  </strong>

                  <span>
                    {(
                      selectedFile.size /
                      1024
                    ).toFixed(
                      1
                    )} KB
                  </span>

                </div>


                <CheckCircle
                  size={21}
                />

              </div>

            )}


            {/* ANALYZE BUTTON */}

            <button
              className="analyze-button"
              onClick={
                handleAnalyze
              }
              disabled={
                !selectedFile ||
                analyzing
              }
            >

              {analyzing ? (

                <>

                  <RefreshCw
                    size={19}
                    className="spin"
                  />

                  Analyzing...

                </>

              ) : (

                <>

                  Analyze Document

                  <ArrowRight
                    size={19}
                  />

                </>

              )}

            </button>


            {/* MESSAGE */}

            {message && (

              <div
                className={`message ${
                  message
                    .toLowerCase()
                    .startsWith(
                      "error"
                    )
                    ? "error-message"
                    : "success-message"
                }`}
              >

                {message
                  .toLowerCase()
                  .startsWith(
                    "error"
                  ) ? (

                  <AlertCircle
                    size={17}
                  />

                ) : (

                  <CheckCircle
                    size={17}
                  />

                )}

                <span>
                  {message}
                </span>

              </div>

            )}

          </div>


          {/* WORKFLOW */}

          <div className="pipeline-panel">

            <div className="panel-header">

              <div>

                <h3>
                  AI Agent Workflow
                </h3>

                <p>
                  Your document passes
                  through specialized agents.
                </p>

              </div>

            </div>


            <div className="mini-pipeline">

              <div className="pipeline-step">

                <div className="pipeline-number">
                  01
                </div>

                <div>

                  <strong>
                    Extractor
                  </strong>

                  <span>
                    Identifies document
                    clauses
                  </span>

                </div>

              </div>


              <div className="pipeline-line"></div>


              <div className="pipeline-step">

                <div className="pipeline-number">
                  02
                </div>

                <div>

                  <strong>
                    Rule Matcher
                  </strong>

                  <span>
                    Finds relevant
                    compliance rules
                  </span>

                </div>

              </div>


              <div className="pipeline-line"></div>


              <div className="pipeline-step">

                <div className="pipeline-number">
                  03
                </div>

                <div>

                  <strong>
                    Risk Scorer
                  </strong>

                  <span>
                    Assesses potential
                    risk
                  </span>

                </div>

              </div>


              <div className="pipeline-line"></div>


              <div className="pipeline-step">

                <div className="pipeline-number">
                  04
                </div>

                <div>

                  <strong>
                    Verifier
                  </strong>

                  <span>
                    Independently checks
                    findings
                  </span>

                </div>

              </div>

            </div>

          </div>

        </section>


        {/* ===================================================
            RESULTS
        =================================================== */}

        {analysisResult && (

          <section className="workflow-section">

            <div className="section-heading">

              <div>

                <span className="eyebrow">
                  ANALYSIS RESULTS
                </span>

                <h3>
                  Compliance Findings
                </h3>

              </div>


              <div className="result-summary">

                <span>
                  {findings.length}
                  {" "}
                  findings
                </span>

              </div>

            </div>


            {findings.length === 0 ? (

              <div className="empty-results">

                <CheckCircle
                  size={28}
                />

                <h4>
                  No findings returned
                </h4>

                <p>
                  The backend completed
                  the analysis but returned
                  no findings.
                </p>

              </div>

            ) : (

              <div className="findings-list">

                {findings.map(
                  (
                    finding,
                    index
                  ) => {

                    const risk =
                      String(
                        finding.risk ||
                        "UNKNOWN"
                      ).toUpperCase();


                    const verification =
                      String(
                        finding.verification ||
                        "UNKNOWN"
                      ).toUpperCase();


                    const isVerified =
                      verification ===
                        "VERIFIED" ||
                      verification ===
                        "NOT_REQUIRED";


                    return (

                      <div
                        className="finding-card"
                        key={
                          `${
                            finding.clause_number ||
                            index
                          }-${index}`
                        }
                      >

                        {/* FINDING HEADER */}

                        <div className="finding-header">

                          <div className="finding-title">

                            <span className="finding-number">

                              {String(
                                index + 1
                              ).padStart(
                                2,
                                "0"
                              )}

                            </span>


                            <div>

                              <h4>

                                {
                                  finding.clause ||
                                  `Clause ${
                                    index + 1
                                  }`
                                }

                              </h4>


                              <span>

                                Rule:{" "}

                                {
                                  finding.matched_rule ||
                                  "NO MATCH"
                                }

                              </span>

                            </div>

                          </div>


                          <div className="finding-badges">

                            <span
                              className={`risk-badge ${risk.toLowerCase()}`}
                            >
                              {risk}
                            </span>


                            <span
                              className={`verification-badge ${
                                isVerified
                                  ? "verified"
                                  : "review"
                              }`}
                            >

                              {isVerified ? (

                                <CheckCircle
                                  size={14}
                                />

                              ) : (

                                <Clock
                                  size={14}
                                />

                              )}

                              {verification}

                            </span>

                          </div>

                        </div>


                        {/* FINDING BODY */}

                        <div className="finding-body">

                          <div className="finding-column">

                            <span className="column-label">
                              DOCUMENT CLAUSE
                            </span>

                            <p>
                              {
                                finding.clause_text ||
                                "No clause text available."
                              }
                            </p>

                          </div>


                          <div className="finding-column">

                            <span className="column-label">
                              COMPLIANCE RULE
                            </span>

                            <p>
                              {
                                finding.matched_rule ||
                                "No matching rule."
                              }
                            </p>

                          </div>


                          <div className="finding-column">

                            <span className="column-label">
                              CONFIDENCE
                            </span>

                            <p>
                              {
                                finding.confidence ||
                                "MEDIUM"
                              }
                            </p>

                          </div>

                        </div>


                        {/* FINDING FOOTER */}

                        <div className="finding-footer">

                          {finding.human_review ===
                            true && (

                            <span>

                              <Users
                                size={15}
                              />

                              Human review required

                            </span>

                          )}


                          <span>

                            <Database
                              size={15}
                            />

                            Evidence preserved

                          </span>

                        </div>

                      </div>

                    );

                  }
                )}

              </div>

            )}

          </section>

        )}


        {/* ===================================================
            INFORMATION CARDS
        =================================================== */}

        <section className="bottom-grid">

          {/* PRIVACY */}

          <div className="info-card">

            <div className="info-icon">

              <Lock
                size={20}
              />

            </div>

            <div>

              <h4>
                Privacy-first architecture
              </h4>

              <p>
                Prototype documents are
                processed locally through
                Ollama and Gemma 2B.
              </p>

            </div>

          </div>


          {/* HUMAN */}

          <div className="info-card">

            <div className="info-icon">

              <ShieldCheck
                size={20}
              />

            </div>

            <div>

              <h4>
                Human-in-the-loop
              </h4>

              <p>
                Only potential compliance
                risks are sent for human
                verification.
              </p>

            </div>

          </div>


          {/* MULTI AGENT */}

          <div className="info-card">

            <div className="info-icon">

              <Activity
                size={20}
              />

            </div>

            <div>

              <h4>
                Multi-agent workflow
              </h4>

              <p>
                Specialized agents provide
                an auditable analysis process.
              </p>

            </div>

          </div>

        </section>

      </>

    );

  };


  // =========================================================
  // MAIN RETURN
  // =========================================================

  return (

    <div className="app">


      {/* =====================================================
          SIDEBAR
      ===================================================== */}

      <aside className="sidebar">


        {/* BRAND */}

        <button
          onClick={() =>
            setActiveNav(
              "Dashboard"
            )
          }
          style={{
            background:
              "transparent",
            border:
              "none",
            padding:
              "0",
            cursor:
              "pointer",
            textAlign:
              "left",
            width:
              "100%",
          }}
        >

          <div className="brand">

            <div className="brand-icon">

              <ShieldCheck
                size={24}
              />

            </div>


            <div>

              <h1>
                ComplyCrew
              </h1>

              <span>
                AI Compliance
              </span>

            </div>

          </div>

        </button>


        {/* NAVIGATION */}

        <nav className="navigation">

          {navigationItems.map(
            (item) => {

              const Icon =
                item.icon;


              return (

                <button
                  key={item.name}
                  className={`nav-item ${
                    activeNav ===
                    item.name
                      ? "active"
                      : ""
                  }`}
                  onClick={() =>
                    setActiveNav(
                      item.name
                    )
                  }
                >

                  <Icon
                    size={19}
                  />

                  <span>
                    {item.name}
                  </span>

                </button>

              );

            }
          )}

        </nav>


        {/* PRIVACY CARD */}

        <button
          onClick={() =>
            setActiveNav(
              "Settings"
            )
          }
          style={{
            background:
              "transparent",
            border:
              "none",
            padding:
              "0",
            cursor:
              "pointer",
            textAlign:
              "left",
            width:
              "100%",
          }}
        >

          <div className="privacy-card">

            <div className="privacy-icon">

              <Lock
                size={18}
              />

            </div>


            <div>

              <strong>
                Privacy First
              </strong>

              <p>
                Documents remain local
                during prototype processing.
              </p>

            </div>

          </div>

        </button>


        {/* SYSTEM STATUS */}

        <button
          onClick={() =>
            setActiveNav(
              "Settings"
            )
          }
          style={{
            background:
              "transparent",
            border:
              "none",
            padding:
              "0",
            cursor:
              "pointer",
            textAlign:
              "left",
            width:
              "100%",
          }}
        >

          <div className="system-status">

            <div className="status-dot"></div>

            <div>

              <strong>
                AI Engine
              </strong>

              <span>
                Gemma 2B via Ollama
              </span>

            </div>

          </div>

        </button>

      </aside>


      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <main className="main-content">


        {/* TOP BAR */}

        <header className="topbar">

          <div>

            <span className="breadcrumb">
              ComplyCrew
            </span>

            <span className="breadcrumb-separator">
              /
            </span>

            <span className="breadcrumb-current">
              {activeNav}
            </span>

          </div>


          <div className="topbar-status">

            <Activity
              size={16}
            />

            <span>
              System Online
            </span>

          </div>

        </header>


        {/* =====================================================
            PAGE CONTENT
        ===================================================== */}

        {activeNav ===
          "Dashboard" &&
          renderDashboard()}


        {activeNav ===
          "Documents" &&
          renderDocumentsPage()}


        {activeNav ===
          "Compliance" &&
          renderCompliancePage()}


        {activeNav ===
          "Settings" &&
          renderSettingsPage()}


        {/* =====================================================
            FOOTER
        ===================================================== */}

        <footer>

          <span>
            ComplyCrew © 2026
          </span>

          <span>
            AI-assisted compliance analysis
          </span>

        </footer>


      </main>

    </div>

  );

}


export default App;
