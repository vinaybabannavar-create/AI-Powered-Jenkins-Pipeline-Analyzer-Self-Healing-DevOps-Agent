# 🤖 AI-Powered Jenkins Pipeline Analyzer & Self-Healing DevOps Agent

> **Hack2Hire 1.0 — Problem Statement 08**
> T John Institute of Technology | Department of CSE | 2026

---

## 🚀 Overview

An AI agent that monitors Jenkins pipelines via REST API, automatically
classifies build/test failures into 6 categories, and takes corrective
self-healing actions — all without human intervention for routine failures.

---

## 🎯 Problem

Debugging Jenkins pipeline failures is time-consuming and requires manual
log analysis. Engineers spend an average of 16 minutes per failure just
identifying the root cause — before they even start fixing it.

---

## 💡 Solution

This agent connects to Jenkins REST API, fetches pipeline logs, classifies
failures using **Regex + Gemini 1.5 Flash LLM**, triggers automated healing
actions, and visualizes everything on a live Streamlit dashboard —
reducing MTTR by **69.8%**.

---

## ✅ Features

- **3 Jenkins Pipelines** — python-flaky-tests, docker-image-build, kubernetes-deploy
- **Jenkins REST API** — Fetches build info, console logs, test reports, stage timings
- **6 Failure Categories** — Flaky Test, Dependency Issue, Infrastructure Issue, Code Defect, Configuration Error, Timeout
- **Dual Classification** — Fast regex pattern matching + Gemini 1.5 Flash LLM fallback
- **Self-Healing Actions** — Auto-retry, pip install trigger, Jira issue generation, Jenkinsfile diff suggestion, ops alerts
- **MTTR Reduction** — From 16 min avg to 5 min avg (69.8% improvement)
- **Live Dashboard** — Streamlit dashboard with pie chart, bar chart, full log table, auto-refresh every 10 seconds
- **Accuracy Report** — 90% classification accuracy on 20 labeled logs
- **CSV + JSON Export** — Every analysis saved automatically

---

## 🏗️ System Architecture

![System Architecture](architecture.png)

---

## 📁 Project Structure
AI-Powered-Jenkins-Pipeline/
├── backend/
│   ├── analyzer.py              # Core AI classifier (Regex + Gemini LLM)
│   ├── cli.py                   # CLI agent with analytics + MTTR report
│   ├── mock_jenkins.py          # Mock Jenkins REST API server (Flask)
│   ├── jenkins_agent.py         # Agent fetching from Jenkins REST API
│   ├── analysis_log.csv         # Auto-generated analysis history
│   ├── summary_report.json      # Auto-generated summary for dashboard
│   ├── pipeline_report.json     # Auto-generated pipeline health report
│   ├── labeled_logs.csv         # Ground truth labels — 90% accuracy
│   ├── jira_issues.txt          # Auto-generated Jira-style issue summaries
│   └── config_suggestions.txt  # Auto-generated Jenkinsfile diff suggestions
├── dashboard/
│   └── app.py                   # Streamlit dashboard (auto-refresh 10s)
├── data/
│   ├── log1.txt — log20.txt     # 20 labeled pipeline log files
│   ├── labeled_logs.csv         # Accuracy report ground truth
│   └── test_report.xml          # JUnit XML test report sample
├── architecture.png             # System architecture diagram
└── README.md

---

## ⚙️ How It Works
Jenkins REST API (mock_jenkins.py)
↓
Jenkins Agent (jenkins_agent.py)
Fetches: build info, console logs,
test reports, stage timings
↓
Regex Classifier (Layer 1 — Fast)
6 pattern categories
↓ (if Low confidence)
Gemini 1.5 Flash LLM (Layer 2)
Few-shot prompted
↓
Self-Healing Action Layer
├── Flaky Test       → Auto-retry 30s backoff
├── Dependency Issue → pip install triggered
├── Infrastructure   → Ops team alerted
├── Code Defect      → Jira issue created
├── Config Error     → Jenkinsfile diff saved
└── Timeout          → Pipeline restarted 2x
↓
CSV Logger + JSON Summary
↓
Streamlit Dashboard (auto-refresh 10s)

---

## 📊 Results

| Metric | Value |
|---|---|
| Total logs analyzed | 20 |
| Regex classified | 18 (90%) |
| LLM classified | 2 (10%) |
| Classification accuracy | **90% (18/20)** |
| MTTR without AI | 15.05 min |
| MTTR with AI | 4.55 min |
| Improvement | **69.8% faster** |
| Pipelines monitored | 3 |
| Failure scenarios demo | 6 |

### Pipeline Health
| Pipeline | Status | Issue Detected | Action Taken |
|---|---|---|---|
| python-flaky-tests | 🔴 FAILURE | Flaky Test | Auto-retry 30s backoff |
| docker-image-build | 🔴 FAILURE | Dependency Issue | pip install triggered |
| kubernetes-deploy | 🔴 FAILURE | Infrastructure Issue | Ops team alerted |

### Failure Distribution
| Category | Logs | Action Taken |
|---|---|---|
| Code Defect | 4 | Jira issue created |
| Dependency Issue | 3 | pip install triggered |
| Flaky Test | 3 | Auto-retry with backoff |
| Timeout | 3 | Pipeline restarted |
| Infrastructure Issue | 3 | Ops team alerted |
| Configuration Error | 2 | Jenkinsfile diff saved |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| AI / LLM | Google Gemini 1.5 Flash |
| Classification | Regex + Pattern Matching |
| Mock Jenkins API | Flask |
| Dashboard | Streamlit + Plotly |
| Data Storage | CSV + JSON |
| Version Control | GitHub |

---

## 🚀 Setup & Run

**1. Clone the repository**
```bash
git clone https://github.com/vinaybabannavar-create/AI-Powered-Jenkins-Pipeline-Analyzer-Self-Healing-DevOps-Agent.git
cd AI-Powered-Jenkins-Pipeline-Analyzer-Self-Healing-DevOps-Agent
```

**2. Install dependencies**
```bash
pip install streamlit plotly pandas google-genai flask requests
```

**3. Set your Gemini API key**
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Mac/Linux
export GEMINI_API_KEY=your_api_key_here
```
Get a free API key at: `aistudio.google.com`

**4. Start Mock Jenkins Server — Terminal 1**
```bash
cd backend
py -3.10 mock_jenkins.py
```
Server runs at `http://localhost:5000`

**5. Run Jenkins Agent — Terminal 2**
```bash
cd backend
py -3.10 jenkins_agent.py
```
Fetches from all 3 pipelines via REST API.

**6. Run CLI Agent — Terminal 3**
```bash
cd backend
py -3.10 cli.py
```
Choose option 1 to analyze all 20 logs.

**7. Run Dashboard — Terminal 4**
```bash
cd dashboard
py -3.10 -m streamlit run app.py
```
Open `http://localhost:8501` — auto-refreshes every 10 seconds.

---

## 🧪 Example Output

**Jenkins Agent fetching pipeline:**
📡 Fetching pipeline: python-flaky-tests
Build #    : 5
Result     : FAILURE
Duration   : 78.2 seconds
Tests Pass : 8
Tests Fail : 2
Stages:
✅ Checkout  → SUCCESS
✅ Build     → SUCCESS
❌ Test      → FAILED
❌ Deploy    → ABORTED
🔍 AI Analysis:
Type       : Flaky Test
Confidence : High
Source     : regex
Fix        : Auto-retry the flaky stage with exponential backoff
Action     : Retrying failed stage with 30s backoff (attempt 1 of 3)

---

## 📋 Deliverables

- [x] Working agent with 6 failure classifications
- [x] Dual classification — Regex + Gemini LLM
- [x] Self-healing actions per failure type
- [x] Streamlit dashboard with live charts + auto-refresh
- [x] 20 labeled logs with 90% accuracy report
- [x] MTTR improvement — 69.8% faster resolution
- [x] CSV + JSON auto-export
- [x] Architecture diagram
- [x] Mock Jenkins REST API with 3 pipelines
- [x] Stage timings per pipeline
- [x] JUnit XML test report
- [x] Pipeline health summary
- [x] 5+ failure scenarios demonstrated

---

## 👨‍💻 Team

- **Vinay Babannavar**
- **Preetam Anil Kage**

---

## 📌 Hackathon

**Hack2Hire 1.0 — Problem Statement 08**
Department of Computer Science & Engineering
T John Institute of Technology | 2026
`#BuildToGetHired` `#H2H2026CSE` `#Hack2Hire`
