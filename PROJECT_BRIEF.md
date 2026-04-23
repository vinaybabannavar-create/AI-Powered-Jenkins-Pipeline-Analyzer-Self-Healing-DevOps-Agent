# Project Brief — Hack2Hire 1.0

## Team
- Vinay Babannavar
- Preetam Anil Kage

## Problem Statement
Problem 08 — AI-Powered Jenkins Pipeline Analyzer & Self-Healing DevOps Agent

## One-Line Description
An AI agent that monitors Jenkins pipelines, classifies build failures into 6 categories using Regex + Gemini LLM, and triggers automated self-healing actions — reducing MTTR by 69.8%.

## Problem Being Solved
Jenkins pipeline failures require manual log analysis averaging 16 minutes per incident. At scale this creates significant DevOps bottlenecks. No existing lightweight tool combines automatic classification with self-healing actions and real-time visualization in a single agent.

## What We Built
A Python-based AI agent with four integrated components. The Mock Jenkins REST API (Flask) simulates a real Jenkins server with three distinct pipelines. The Jenkins Agent fetches live pipeline data including build info, console logs, test reports, and stage timings via HTTP. The dual-layer classifier first applies regex pattern matching for speed, then falls back to Gemini 1.5 Flash LLM for ambiguous cases, correctly classifying 90% of 20 labeled logs. The self-healing layer automatically triggers the correct remediation action per failure type. A Streamlit dashboard visualizes everything in real time with auto-refresh every 10 seconds.

## Key Results
- MTTR reduced from 15.05 minutes to 4.55 minutes (69.8% improvement)
- 90% classification accuracy on 20 labeled logs
- 6 failure categories detected and handled automatically
- 3 Jenkins pipelines monitored simultaneously via REST API

## Tech Stack
Python 3.10, Google Gemini 1.5 Flash, Flask, Streamlit, Plotly, Pandas, Regex

## GitHub Repository
https://github.com/vinaybabannavar-create/AI-Powered-Jenkins-Pipeline-Analyzer-Self-Healing-DevOps-Agent

## Theme
AI / DevOps — Problem Statement 08