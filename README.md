# AI-Powered-Jenkins-Pipeline-Analyzer-Self-Healing-DevOps-Agent

## 🚀 Problem

Debugging Jenkins pipeline failures is time-consuming and requires manual log analysis.

---

## 💡 Solution

This project analyzes pipeline logs and automatically detects failure types and suggests fixes.

---

## ⚙️ Features (Current)

- Supports multi-log analysis (automatic detection from multiple files)
- Detects dependency errors  
- Detects test failures  
- Suggests fixes automatically  
- Works with multiple log files
- Provides detailed reasoning for each detected failure
- Detects timeout errors and improves classification accuracy  
---

## 🏗️ Project Structure

backend/ → Analyzer logic
data/ → Log files
README.md → Documentation

---

## 🧪 Example

### Input:

AssertionError: test_login failed

### Output:

Failure Type: Test Failure
Suggested Fix: Check failed test case and fix logic

---

## 🛠️ Tech Stack

* Python

---

## 🚀 How to Run

```bash
python backend/analyzer.py
```

---

## 🎯 Future Improvements

* Jenkins integration
* Auto retry pipelines
* Dashboard

---

## 👨‍💻 Team

* Vinay Babannavar
* Preetam Anil Kage

---

## 📌 Hackathon

Hack2Hire 1.0 — Problem 08
