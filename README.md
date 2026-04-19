# 🤖 AI-Powered Jenkins Pipeline Analyzer & Self-Healing DevOps Agent

> **Hack2Hire 1.0 — Problem Statement 08**  
> T John Institute of Technology | Department of CSE | 2026

---

## 🚀 Overview

An AI agent that monitors Jenkins pipeline logs, automatically classifies 
build/test failures into 6 categories, and takes corrective self-healing 
actions — all without human intervention for routine failures.

---

## 🎯 Problem

Debugging Jenkins pipeline failures is time-consuming and requires manual 
log analysis. Engineers spend an average of 16 minutes per failure just 
identifying the root cause — before they even start fixing it.

## 💡 Solution

This agent reads pipeline logs, classifies failures using **Regex + Gemini LLM**, 
triggers automated healing actions, and visualizes everything on a live 
Streamlit dashboard — reducing MTTR by **68.8%**.

---

## ✅ Features

- **6 Failure Categories** — Flaky Test, Dependency Issue, Infrastructure Issue,
  Code Defect, Configuration Error, Timeout
- **Dual Classification** — Fast regex pattern matching + Gemini 1.5 Flash LLM fallback
- **Self-Healing Actions** — Auto-retry, pip install trigger, Jira issue generation,
  Jenkinsfile diff suggestion, ops alerts
- **MTTR Reduction** — From 16 min avg to 5 min avg (68.8% improvement)
- **Live Dashboard** — Streamlit dashboard with pie chart, bar chart, full log table
- **Accuracy Report** — 95% classification accuracy on 20 labeled logs
- **CSV + JSON Export** — Every analysis saved automatically

---

## 🏗️ Project Structure
AI-Powered-Jenkins-Pipeline/
├── backend/
│   ├── analyzer.py           # Core AI classifier (Regex + Gemini LLM)
│   ├── cli.py                # CLI agent with analytics + MTTR report
│   ├── analysis_log.csv      # Auto-generated analysis history
│   ├── summary_report.json   # Auto-generated summary for dashboard
│   ├── jira_issues.txt       # Auto-generated Jira-style issue summaries
│   └── config_suggestions.txt# Auto-generated Jenkinsfile diff suggestions
├── dashboard/
│   └── app.py                # Streamlit dashboard
├── data/
│   ├── log1.txt — log20.txt  # 20 labeled pipeline log files
│   └── labeled_logs.csv      # Ground truth labels for accuracy report
├── architecture.png          # System architecture diagram
└── README.md

---

## ⚙️ How It Works
Pipeline Log File
↓
Regex Pattern Matching (Layer 1)
↓ (if confidence is Low)
Gemini 1.5 Flash LLM (Layer 2)
↓
Self-Healing Action Layer
├── Flaky Test       → Auto-retry with 30s backoff
├── Dependency Issue → pip install -r requirements.txt
├── Infrastructure   → Alert sent to ops team
├── Code Defect      → Jira-style issue created
├── Config Error     → Jenkinsfile diff suggested
└── Timeout          → Pipeline restarted at 2x timeout
↓
CSV Logger + JSON Summary
↓
Streamlit Dashboard

---

## 📊 Results

| Metric | Value |
|---|---|
| Total logs analyzed | 20 |
| Regex classified | 19 (95%) |
| LLM classified | 1 (5%) |
| Classification accuracy | **95% (19/20)** |
| MTTR without AI | 16.0 min |
| MTTR with AI | 5.0 min |
| Improvement | **68.8% faster** |

### Failure Distribution
| Category | Logs | Action Taken |
|---|---|---|
| Dependency Issue | 3 | pip install triggered |
| Code Defect | 3 | Jira issue created |
| Flaky Test | 3 | Auto-retry with backoff |
| Timeout | 3 | Pipeline restarted |
| Configuration Error | 3 | Jenkinsfile diff saved |
| Infrastructure Issue | 3 | Ops team alerted |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| AI / LLM | Google Gemini 1.5 Flash |
| Classification | Regex + Embeddings |
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
pip install streamlit plotly pandas google-genai
```

**3. Set your Gemini API key**
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Mac/Linux
export GEMINI_API_KEY=your_api_key_here
```
Get a free API key at: `aistudio.google.com`

**4. Run the CLI agent**
```bash
cd backend
py -3.10 cli.py
```
Choose option 1 to analyze all logs.

**5. Run the dashboard** (in a separate terminal)
```bash
cd dashboard
py -3.10 -m streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 🧪 Example Output

**Input log:**
ModuleNotFoundError: No module named 'requests'
pip install failed with exit code 1

**Agent output:**
Type      : Dependency Issue
Category  : Build Error
Reason    : Required package or module is missing from the environment
Fix       : Run pip install -r requirements.txt and rebuild
Confidence: High
Source    : regex
Action    : Triggering pip install -r requirements.txt

---

## 📋 Deliverables

- [x] Working agent with 6 failure classifications
- [x] Dual classification — Regex + Gemini LLM
- [x] Self-healing actions per failure type
- [x] Streamlit dashboard with live charts
- [x] 20 labeled logs with 95% accuracy report
- [x] MTTR improvement — 68.8% faster resolution
- [x] CSV + JSON auto-export
- [x] Architecture diagram
- [ ] Jenkins REST API integration *(in progress)*

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
