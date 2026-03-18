<p align="center">
  <strong>NIRVAAH AI</strong><br/>
  <em>Intelligent Multi-Agent Healthcare Pipeline for India's ASHA Workers</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-Multi_Agent-FF6F00?style=flat" />
  <img src="https://img.shields.io/badge/React-Dashboard-61DAFB?style=flat&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Supabase-Realtime-3FCF8E?style=flat&logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" />
</p>

---

## 📌 Overview

**Nirvaah AI** is an end-to-end, AI-powered healthcare data pipeline purpose-built for India's **ASHA (Accredited Social Health Activist) workers** — the 1 million+ frontline health workers who deliver maternal and child health services across rural India.

The system transforms a simple **WhatsApp message** (voice note, text, or photograph of a printed document) into **validated, government-ready health records** — automatically extracted, cross-checked against clinical protocols, mapped to official registries (HMIS, MCTS, Kerala HIMS), synced to the cloud, screened for fraud, and enriched with predictive dropout-risk insights — all within **seconds**, with zero additional hardware and no training required.

> _"Bridging the last mile of India's public health infrastructure — one WhatsApp message at a time."_

---

## 🌟 Key Features & Novelties

### 🤖 Multi-Agent LangGraph Pipeline
The core of Nirvaah AI is a **7-agent directed acyclic graph** orchestrated with [LangGraph](https://github.com/langchain-ai/langgraph). Each agent is a specialised autonomous node with clear input/output contracts and graceful error isolation — if one agent fails, the pipeline continues safely.

| Agent | Role | Technology |
|---|---|---|
| **1. Extraction Agent** | Structured clinical field extraction from raw voice/text/OCR transcripts | Groq LLM (LLaMA 3.3 70B) |
| **2. Validation Agent** | Range-checks vitals against Kerala NHM protocols, flags clinical alerts (anemia, pre-eclampsia, hypertension) | Pure Python rules + Groq for bilingual clarification messages |
| **3. Clarification Agent** | Sends WhatsApp follow-ups to the worker when data confidence is too low | Twilio WhatsApp API |
| **4. Form Mapping Agent** | Maps validated fields to three government database schemas (HMIS, MCTS, Kerala eHealth HIMS) via a 179 KB JSON schema registry | Registry-driven mapping + Groq fallback for unmapped fields |
| **5. Sync Agent** | Writes records to Supabase and Google Sheets, manages Redis-backed clarification state | Supabase, gspread, Upstash Redis |
| **6. Anomaly Detection Agent** | Detects fraudulent submission patterns using a trained IsolationForest model and hard rule checks | scikit-learn IsolationForest + rule engine |
| **7. Insights Agent** | Predicts patient dropout risk and checks eligibility for 5 government welfare schemes | XGBoost classifier + scheme eligibility rules + Groq risk summaries |

### 🗣️ Multi-Modal Input Processing
ASHA workers can submit data in **any format** they are comfortable with — no app downloads, no forms, no training:

- **Voice Notes** — Transcribed via **ElevenLabs STT** with native support for Malayalam, English, and code-mixed conversational speech.
- **Text Messages** — Normalised and processed directly.
- **Photographs of Printed Documents** — Aadhaar cards, BPL cards, government health forms, and ASHA registers are processed via a custom **Tesseract OCR pipeline** with:
  - Bilingual support (English + Malayalam) using three-pass extraction
  - Adaptive image preprocessing (upscaling, contrast enhancement, unsharp masking) tuned for phone-camera photographs of printed documents
  - Intelligent deduplication across OCR passes

### 🏥 Clinical Validation Engine
Every record is automatically validated against **Kerala state NHM protocol rules** before it enters any database:

- **Hard range checks** — physiologically impossible values (e.g. BP > 180 mmHg) are flagged and nullified
- **Clinical alert generation** — anemia flags, hypertension alerts, severe anemia critical alerts, pre-eclampsia risk detection, and low birth weight alerts
- **Confidence thresholds** — field-level and overall confidence gating with automatic bilingual (English + Malayalam) clarification messages sent back to the worker via WhatsApp

### 📋 Government Survey Mode
A dedicated **survey subsystem** lets ASHA workers conduct four types of standardised surveys directly via WhatsApp:

| Survey | Use Case |
|---|---|
| **Leprosy Survey** | Household screening with pin-prick test tracking and PHC referrals |
| **Pulse Polio Survey** | Under-5 vaccination coverage, guest children, and fever/diarrhoea tracking |
| **Above 30 Screening** | NCD screening — BP, blood sugar (fasting/random), and complaint recording |
| **Pregnant Ladies Survey** | Full ANC data collection — BP, Hb, weight, IFA, next visit scheduling |

Each survey runs a complete **transcribe → extract → validate → store → audit → notify** cycle with automatic referral alert generation to both the worker and their supervisor.

### 🛡️ Security & Compliance Layer

Nirvaah AI implements a comprehensive security framework compliant with India's **Digital Personal Data Protection (DPDP) Act 2023**:

| Feature | Implementation |
|---|---|
| **PII Redaction** | Aadhaar numbers and phone numbers are pattern-matched and redacted before any data enters the pipeline |
| **Identifier Hashing** | All phone numbers and worker IDs are hashed with SHA-256 (with a `sha256:` prefix) — originals are never stored |
| **AES-256-GCM Encryption** | Health records are encrypted with authenticated encryption before at-rest storage |
| **Blockchain-Style Audit Chain** | Every record receives a SHA-256 hash chain entry (`LOG-03`) linking to the previous record — ensuring tamper-evidence and immutable audit trails |
| **Access Event Logging** | All data access events (`LOG-05`) are recorded with hashed user IDs, roles (ASHA / Supervisor / District Officer), and actions (Read / Write / Export) |
| **Consent Management** | Workers can text `STOP` to withdraw consent (opt-out) or `RECORD` to request their health data (data portability) — fully implementing DPDP Act sections |
| **Webhook Sanitisation** | Raw webhook payloads are PII-stripped at the entry point before any processing (`LOG-01`) |

### 🚨 SOS Emergency Alert System
ASHA workers in rural India sometimes face dangerous situations during home visits. Nirvaah AI includes a **silent SOS system**:
- A configurable **secret keyword** (default: `"jalebi"`) triggers emergency alerts
- Alerts are sent via **WhatsApp messages + phone calls** to supervisor, nearby ASHA worker, and local authority
- **Silent response** — no confirmation is sent back to the worker's phone to protect them
- All SOS events are logged to Supabase for audit trails

### 📊 Anomaly Detection & Anti-Fraud Engine
Submission integrity is monitored through a **dual-layer detection system**:

1. **ML Layer** — A trained **IsolationForest** model scores each submission based on:
   - Records per day, submission velocity, standard deviation of clinical readings, and unique beneficiary ratio
2. **Rule Engine** — Hard-coded checks for:
   - **GPS Impossibility** — 30+ km travel between submissions in under 15 minutes
   - **Submission Velocity** — More than 1 record in 90 seconds
   - **Field Duplication** — Identical BP readings for different beneficiaries on the same day
   - **Off-Hours Submissions** — Records filed between 11 PM and 5 AM IST
   - **Incentive Gaming** — Threshold-based detection for JSY/PNC/immunisation incentive triggers

### 💡 Predictive Insights & Scheme Eligibility
The Insights Agent provides **proactive, actionable intelligence**:

- **Dropout Risk Prediction** — An XGBoost classifier trained on NFHS-5 (National Family Health Survey) features predicts the probability of a patient dropping out of care programs. Features include maternal age, parity, gestational age at first ANC, hemoglobin levels, distance to PHC, IFA tablet compliance, BPL status, and scheme enrollment.
- **Government Scheme Eligibility** — Automatically checks eligibility for 5 major welfare schemes:
  - **PMMVY** — Pradhan Mantri Matru Vandana Yojana (₹5,000 cash transfer for first live birth)
  - **JSY** — Janani Suraksha Yojana (institutional delivery incentive for BPL families)
  - **Sneha Sparsham** — Kerala state scheme (free transport + nutrition for all pregnant women)
  - **JSSK** — Janani Shishu Suraksha Karyakram (free delivery, drugs, and referral transport)
  - **PMSMA** — Pradhan Mantri Surakshit Matritva Abhiyan (free ANC on the 9th of every month)
- **Groq-Generated Risk Summaries** — When dropout risk exceeds 70%, a human-readable 2-sentence risk explanation is generated and pushed to the dashboard.

### 📈 Real-Time Supervisor Dashboard
A **React + Vite** frontend provides block-level supervisors with real-time visibility:

| Tab | Functionality |
|---|---|
| **Live Feed** | Real-time stream of incoming health submissions via Supabase Realtime subscriptions |
| **Records Table** | Searchable, sortable table of all validated records with extracted data, mapped forms, and sync status |
| **Audit Chain** | Visual blockchain-style integrity chain showing hash links between records |
| **Risk Map** | Geographic risk visualisation with dropout risk overlays |

Additional dashboard features:
- **Offline support** — IndexedDB-backed queue for areas with intermittent connectivity
- **Login-protected** supervisor portal with session audit logging
- **Client-side encryption** utilities for data-in-transit security

---

## 🏗️ Architecture

```
WhatsApp (Twilio)
     │
     ▼
┌──────────────────────────────────────────────────────┐
│  FastAPI Webhook                                     │
│  ┌─ PII Redaction ─ Consent Check ─ SOS Detect ─┐   │
│  │  Survey Mode Routing                          │   │
│  └───────────────────────────────────────────────┘   │
│                        │                             │
│  ┌─────────── LangGraph Pipeline ────────────────┐   │
│  │                                               │   │
│  │  ┌──────────┐    ┌──────────┐                 │   │
│  │  │ Extract  │───▶│ Validate │                 │   │
│  │  │ Agent 1  │    │ Agent 2  │                 │   │
│  │  └──────────┘    └────┬─────┘                 │   │
│  │                       │                       │   │
│  │            ┌──────────┴──────────┐            │   │
│  │            ▼                     ▼            │   │
│  │   ┌──────────────┐     ┌──────────────┐       │   │
│  │   │ Clarify &    │     │ Form Mapping │       │   │
│  │   │ Ask via WA   │     │   Agent 3    │       │   │
│  │   │  (stops)     │     └──────┬───────┘       │   │
│  │   └──────────────┘            │               │   │
│  │                               ▼               │   │
│  │                      ┌──────────────┐         │   │
│  │                      │  Sync Agent  │         │   │
│  │                      │   Agent 4    │         │   │
│  │                      └──────┬───────┘         │   │
│  │                             ▼                 │   │
│  │                      ┌──────────────┐         │   │
│  │                      │  Anomaly     │         │   │
│  │                      │  Agent 5     │         │   │
│  │                      └──────┬───────┘         │   │
│  │                             ▼                 │   │
│  │                      ┌──────────────┐         │   │
│  │                      │  Insights    │         │   │
│  │                      │  Agent 6     │         │   │
│  │                      └──────────────┘         │   │
│  │                                               │   │
│  └───────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
     │                    │                    │
     ▼                    ▼                    ▼
  Supabase          Google Sheets       React Dashboard
  (Primary DB)     (HMIS Mirror)     (Supervisor Portal)
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | FastAPI, Uvicorn |
| **AI Orchestration** | LangGraph (multi-agent state machine), LangChain |
| **LLM Provider** | Groq (LLaMA 3.3 70B Versatile) — for extraction, validation messages, derived fields, unmapped field suggestions, and risk summaries |
| **Speech-to-Text** | ElevenLabs |
| **OCR** | Tesseract (via pytesseract) with Pillow image preprocessing — English + Malayalam bilingual support |
| **ML Models** | scikit-learn IsolationForest (anomaly detection), XGBoost (dropout risk prediction) |
| **Database** | Supabase (PostgreSQL + Realtime + Row Level Security) |
| **Caching / State** | Upstash Redis (HTTP-based) for clarification state and survey sessions |
| **Messaging** | Twilio WhatsApp API (incoming webhooks + outgoing notifications) |
| **Encryption** | `cryptography` library — AES-256-GCM authenticated encryption, SHA-256 hashing |
| **Frontend** | React 18, Vite, Recharts, Supabase JS (Realtime subscriptions) |
| **Spreadsheet Sync** | gspread + Google Sheets API (supplementary HMIS mirror) |
| **Deployment** | Render (Procfile-based), with support for background threads |

---

## 📂 Repository Structure

```
Nirvaah-AI/
├── Procfile                       # Render deployment entry point
├── requirements.txt               # Python dependencies
├── app/                           # FastAPI backend
│   ├── main.py                    # FastAPI application entry point
│   ├── webhook.py                 # Twilio WhatsApp webhook handler
│   ├── pipeline.py                # LangGraph state machine builder
│   ├── state.py                   # Shared TypedDict pipeline state contract
│   ├── agents/                    # LangGraph agent nodes
│   │   ├── extraction.py          # Agent 1 — LLM-based medical field extraction
│   │   ├── validation.py          # Agent 2 — Clinical range validation + alert generation
│   │   ├── form_agent.py          # Agent 3 — Government schema mapping (HMIS/MCTS/Kerala HIMS)
│   │   ├── sync_agent.py          # Agent 4 — Supabase + Google Sheets sync
│   │   ├── anomaly.py             # Agent 5 — IsolationForest ML + rule-based fraud detection
│   │   └── insights.py            # Agent 6 — XGBoost dropout risk + scheme eligibility
│   ├── security/                  # Security rule modules
│   │   └── anomaly_rules.py       # Incentive gaming detection rules
│   ├── ocr.py                     # Tesseract OCR with bilingual image preprocessing
│   ├── transcription.py           # ElevenLabs speech-to-text integration
│   ├── audit_chain.py             # SHA-256 blockchain-style audit chain (LOG-03)
│   ├── encryption.py              # AES-256-GCM record encryption (LOG-04)
│   ├── pii_utils.py               # Aadhaar/phone PII redaction and identifier hashing
│   ├── middleware.py               # DPDP Act 2023 compliance middleware (LOG-01, LOG-05)
│   ├── constants.py               # Global security constants and log type definitions
│   ├── sos.py                     # Silent SOS emergency alert system
│   ├── survey_handler.py          # WhatsApp-based survey session management
│   ├── survey_extraction.py       # Survey-specific LLM data extraction
│   ├── survey_validation.py       # Survey clinical validation + referral rules
│   ├── survey_notifications.py    # Survey confirmation + referral alert messages
│   ├── notifications.py           # WhatsApp outbound messaging via Twilio
│   ├── database.py                # Supabase client initialisation
│   └── verify_integrity.py        # Audit chain integrity verification
├── dashboard/                     # React + Vite supervisor dashboard
│   └── src/
│       ├── App.jsx                # Login + tabbed layout (Live Feed, Records, Audit, Risk Map)
│       ├── components/
│       │   ├── LiveFeed.jsx       # Real-time submission stream
│       │   ├── RecordsTable.jsx   # Searchable records table
│       │   ├── AuditChain.jsx     # Blockchain audit chain visualiser
│       │   ├── RiskMap.jsx        # Geographic risk map
│       │   └── AlertSidebar.jsx   # Anomaly alert sidebar
│       └── crypto.js              # Client-side encryption utilities
├── data/                          # Validation rules, schemas, and prompts
│   ├── validation_rules.py        # Kerala NHM clinical range rules
│   ├── scheme_eligibility.py      # Government scheme eligibility checks
│   ├── schema_registry.json       # 179 KB schema registry (HMIS/MCTS/Kerala HIMS field definitions)
│   ├── extraction_prompt.txt      # Dynamic extraction prompt template
│   └── survey_prompt_*.txt        # Survey-specific extraction prompts
├── models/                        # Pre-trained ML model artifacts
│   ├── anomaly_model.pkl          # IsolationForest anomaly detection model
│   ├── anomaly_scaler.pkl         # StandardScaler for anomaly features
│   ├── dropout_model.pkl          # XGBoost dropout risk classifier
│   ├── dropout_scaler.pkl         # StandardScaler for dropout features
│   ├── feature_columns.json       # Feature column definitions
│   └── threshold.json             # Tuned anomaly detection threshold
├── scripts/                       # Training and utility scripts
│   ├── train_anomaly_model.py     # IsolationForest training script
│   ├── train_dropout_model.py     # XGBoost training script
│   └── validation_script.py       # Manual validation utility
├── docs/                          # Agent and pipeline documentation
│   ├── agent1-extraction.md
│   ├── agent2-validation.md
│   ├── agent3-form-agent.md
│   ├── ocr-module.md
│   ├── pipeline.md
│   └── results.md
└── security_reference/            # Security architecture reference docs
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | Required for `TypedDict` advanced features |
| Node.js | 18+ | For the React dashboard |
| Tesseract OCR | 4.x+ | Required with `eng` and `mal` language packs for bilingual OCR |

### API Keys Required

| Service | Purpose |
|---|---|
| **Twilio** | WhatsApp webhook (incoming) and message delivery (outgoing) |
| **Supabase** | Primary database (PostgreSQL) with Realtime subscriptions |
| **Groq** | LLM inference for extraction, validation, mapping, and risk summaries |
| **ElevenLabs** | Voice note transcription (speech-to-text) |

### Environment Variables

Create a `.env` file at the project root (see `.env.example`):

```ini
# FastAPI
PORT=8000
ENVIRONMENT=development

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_SANDBOX_NUMBER=whatsapp:+14155238886

# Supabase
SUPABASE_URL=your_project_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# AI Providers
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Redis (for survey sessions and clarification state)
UPSTASH_REDIS_REST_URL=your_upstash_url
UPSTASH_REDIS_REST_TOKEN=your_upstash_token

# Anomaly Detection
ANOMALY_THRESHOLD=0.6

# SOS Emergency (optional)
SOS_KEYWORD=jalebi
SOS_SUPERVISOR_PHONE=+91...
SOS_NEARBY_ASHA_PHONE=+91...
SOS_AUTHORITY_PHONE=+91...
```

### Running the Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Running the Dashboard

```bash
cd dashboard
npm install
npm run dev
```

---

## ⚙️ Deployment

This project is configured for **Render** out-of-the-box:

- The `Procfile` uses: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Ensure Tesseract with English and Malayalam language packs is installed in the deployment environment:
  ```bash
  apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-mal
  ```
- Attach a persistent disk or deploy the `models/` directory alongside the application for ML model availability.

---

## 🌍 Societal Impact

### The Problem
India has **over 1 million ASHA workers** serving as the primary link between communities and the healthcare system. These workers currently maintain records using **paper registers and manual forms** — a process that is slow, error-prone, and vulnerable to data loss. Critical health data often never reaches government databases, leading to:
- Missed high-risk patients (anemia, pre-eclampsia, hypertension)
- Delayed welfare scheme enrollment (PMMVY, JSY, JSSK)
- No early warning for patient dropout from care programs
- Impossibility of real-time supervision at scale

### How Nirvaah AI Helps

| Problem | Nirvaah AI Solution |
|---|---|
| **Paper-based recording** | Voice/text/photo → structured digital records via WhatsApp |
| **Data never reaches databases** | Automatic sync to Supabase + HMIS/MCTS/Kerala HIMS mappings |
| **Missed clinical emergencies** | Real-time clinical alerts (anemia, hypertension, pre-eclampsia) sent to both worker and supervisor |
| **Delayed scheme enrollment** | Proactive eligibility checks for 5 government welfare schemes on every visit |
| **Patient dropout** | XGBoost-powered predictive risk scoring with actionable summaries for follow-up prioritisation |
| **Data fraud / gaming** | IsolationForest + rule engine for submission integrity monitoring |
| **Worker safety** | Silent SOS emergency system via a secret WhatsApp keyword |
| **Language barriers** | Full support for Malayalam, English, and code-mixed speech — no app needed, just WhatsApp |
| **Offline areas** | Dashboard IndexedDB offline queue + background sync for intermittent connectivity |
| **Privacy concerns** | DPDP Act 2023 compliance — PII redaction, identifier hashing, AES-256-GCM encryption, consent management |

### Key Social Benefits
- **Zero Training Overhead** — ASHA workers use WhatsApp, which they already know. No new app to install, no forms to learn.
- **Inclusive Design** — Voice note support eliminates literacy barriers. Malayalam support ensures accessibility for Kerala's 35 million Malayalam speakers.
- **Proactive Care** — Dropout risk prediction enables supervisors to prioritise follow-ups before patients are lost from the system.
- **Transparency & Accountability** — Blockchain-style audit chains and anomaly detection ensure data integrity from field to database.
- **Scalable Architecture** — The LangGraph multi-agent design allows new agents (e.g., nutrition tracking, mental health screening) to be added without modifying existing agents.

---

## 👥 Acknowledgements

Built as part of the National Health Mission Kerala initiative to digitise frontline healthcare delivery through AI-powered automation.

---

<p align="center">
  <em>Nirvaah (निर्वाह) — sustenance, livelihood, the act of carrying forward.</em>
</p>
