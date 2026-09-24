# Frontend — AI DevOps Self-Healing Platform

This directory contains the production-grade **React 18 Single-Page Application (SPA)** with an OLED pitch-black theme, ambient aurora animations, a floating bottom navigation dock, real-time Server-Sent Events (SSE) telemetry, and Chart.js analytics.

## Structure
- `dist/index.html`: Optimized React 18 production bundle with Babel transpilation and Tailwind-style utility classes.
- `package.json`: Project metadata and dependencies.

## Key Features
- **OLED Black Cyberpunk Theme:** Pure black background (`#000000`) with ambient floating neon auroras (Indigo, Cyan, Violet) and cursor spotlight.
- **Floating Bottom Navigation Dock:** Pinned at the bottom with distinct colored glows for each tab (Overview, Architecture Flow, Web CLI, Pipelines, Remediation Center, Analytics, Settings) with zero horizontal scrollbars.
- **Interactive Web CLI & Terminal:** Browser-based shell supporting `analyze all`, `analyze log<n>.txt`, `run agent`, and `status`.
- **Architecture Flow Visualizer:** 5-step autonomous flow diagram with zoom controls (`+`, `−`, `Reset`).
- **Remediation Proof Inspector:** In-app visual proof viewer for GitHub Pull Requests (with unified Git diffs), Jira Bug Tickets, and Jenkins build retry traces.
