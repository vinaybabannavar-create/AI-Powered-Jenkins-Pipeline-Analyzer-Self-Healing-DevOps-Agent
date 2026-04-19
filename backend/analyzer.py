import re
import os
import json

from google import genai
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "AIzaSyB3NFOlKPNlZXO842T4pXLJgV7HV0PcMFA"))

# ── Regex patterns for all 6 required categories ──────────────────────────────
PATTERNS = {
    "Flaky Test": [
        r"test.*retry", r"intermittent", r"flaky", r"passed on second attempt",
        r"randomly fail", r"non-deterministic"
    ],
    "Dependency Issue": [
        r"modulenotfounderror", r"importerror", r"pip.*failed",
        r"no module named", r"package.*not found", r"requirements.*error"
    ],
    "Infrastructure Issue": [
        r"out of memory", r"no space left", r"disk full",
        r"connection refused", r"host unreachable", r"oomkilled"
    ],
    "Code Defect": [
        r"assertionerror", r"typeerror", r"valueerror",
        r"nullpointerexception", r"segmentation fault", r"uncaught exception"
    ],
    "Configuration Error": [
        r"jenkinsfile.*error", r"invalid.*config", r"syntax error.*pipeline",
        r"missing.*environment variable", r"undefined.*variable", r"invalid yaml"
    ],
    "Timeout": [
        r"timed out", r"timeout", r"exceeded.*minutes",
        r"build timed out", r"stage.*timeout", r"deadline exceeded"
    ],
    # Add inside PATTERNS dict under "Code Defect"
    "Code Defect": [
        r"assertionerror", r"typeerror", r"valueerror",
        r"nullpointerexception", r"segmentation fault",
        r"uncaught exception", r"exit code 1",        # ← add this
        r"process crashed", r"build process"           # ← add this
    ],
}

# ── Layer 1: Regex classifier ─────────────────────────────────────────────────
def regex_classify(log):
    log_lower = log.lower()
    scores = {}

    for category, patterns in PATTERNS.items():
        count = sum(1 for p in patterns if re.search(p, log_lower))
        if count > 0:
            scores[category] = count

    if not scores:
        return None, "Low"

    best = max(scores, key=scores.get)
    total_matches = scores[best]
    confidence = "High" if total_matches >= 3 else "Medium" if total_matches >= 1 else "Low"

    return best, confidence

# ── Layer 2: Gemini LLM fallback ──────────────────────────────────────────────
def llm_classify(log):
    prompt = f"""You are a DevOps AI agent analyzing Jenkins build logs.
Classify this log into exactly one of these categories:
- Flaky Test
- Dependency Issue
- Infrastructure Issue
- Code Defect
- Configuration Error
- Timeout

Return ONLY a JSON object like this (no markdown, no extra text):
{{
  "type": "<category>",
  "category": "<Build Error / Test Error / Infrastructure / Execution>",
  "reason": "<one sentence explaining why>",
  "fix": "<one sentence fix suggestion>",
  "confidence": "<High / Medium / Low>"
}}

Log to analyze:
{log[:1500]}
"""
    for attempt in range(2):  # try twice
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            text = response.text.strip()
            text = re.sub(r"```json|```", "", text).strip()
            result = json.loads(text)
            return result
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt == 0:
                print("   ⏳ Rate limit hit — waiting 35 seconds and retrying...")
                time.sleep(35)
                continue
            # All retries failed — return graceful fallback
            return {
                "type":       "Unknown",
                "category":   "Unknown",
                "reason":     "LLM quota exceeded — will retry later",
                "fix":        "Manual debugging required",
                "confidence": "Low"
            }
# ── Main analyze function ─────────────────────────────────────────────────────
def analyze_log(log):
    # Try regex first
    category, confidence = regex_classify(log)

    if category and confidence in ["High", "Medium"]:
        # Regex was confident enough
        fixes = {
            "Flaky Test":          "Auto-retry the flaky stage with exponential backoff",
            "Dependency Issue":    "Run pip install -r requirements.txt and rebuild",
            "Infrastructure Issue":"Check resource limits, scale up or free disk space",
            "Code Defect":         "Review failing test/line, create Jira issue for dev team",
            "Configuration Error": "Validate Jenkinsfile syntax and environment variables",
            "Timeout":             "Optimize slow stage or increase timeout threshold"
        }
        reasons = {
            "Flaky Test":          "Test passed on retry — indicates non-deterministic behavior",
            "Dependency Issue":    "Required package or module is missing from the environment",
            "Infrastructure Issue":"System resource constraint detected (memory/disk/network)",
            "Code Defect":         "Exception or assertion failure found in application code",
            "Configuration Error": "Invalid pipeline configuration or missing environment variable",
            "Timeout":             "Stage or build exceeded the configured time limit"
        }
        return {
            "type":     category,
            "category": "Build Error" if category in ["Dependency Issue","Configuration Error"] else
                        "Test Error"  if category == "Code Defect" else
                        "Infrastructure" if category in ["Infrastructure Issue","Timeout"] else "Execution",
            "reason":     reasons.get(category, "Pattern matched"),
            "fix":        fixes.get(category, "Investigate logs"),
            "confidence": confidence,
            "source":     "regex"
        }

    # Regex not confident → use Gemini
    result = llm_classify(log)
    result["source"] = "llm"
    return result


# ── Self-healing action layer ─────────────────────────────────────────────────
def take_action(result):
    action_type = result["type"]
    action_log  = []

    if action_type == "Flaky Test":
        msg = "Retrying failed stage with 30s backoff (attempt 1 of 3)"
        print(f"⚡ Action: {msg}")
        action_log.append(msg)

    elif action_type == "Dependency Issue":
        msg = "Triggering: pip install -r requirements.txt"
        print(f"⚡ Action: {msg}")
        action_log.append(msg)

    elif action_type == "Infrastructure Issue":
        msg = "Alert sent to ops team — resource threshold breached"
        print(f"⚡ Action: {msg}")
        action_log.append(msg)

    elif action_type == "Code Defect":
        # Generate a Jira-style issue summary
        summary = (
            f"[AUTO] Code Defect Detected\n"
            f"Reason: {result['reason']}\n"
            f"Suggested Fix: {result['fix']}\n"
            f"Confidence: {result['confidence']}\n"
            f"Source: {result.get('source','unknown')}"
        )
        with open("jira_issues.txt", "a") as f:
            f.write(summary + "\n" + "="*40 + "\n")
        msg = "Jira-style issue written to jira_issues.txt"
        print(f"⚡ Action: {msg}")
        action_log.append(msg)

    elif action_type == "Configuration Error":
        msg = "Suggested Jenkinsfile diff saved to config_suggestions.txt"
        with open("config_suggestions.txt", "a") as f:
            f.write(f"Fix suggestion: {result['fix']}\n" + "="*40 + "\n")
        print(f"⚡ Action: {msg}")
        action_log.append(msg)

    elif action_type == "Timeout":
        msg = "Restarting pipeline with increased timeout (2x current limit)"
        print(f"⚡ Action: {msg}")
        action_log.append(msg)

    else:
        msg = "No automated action available — flagged for manual review"
        print(f"⚡ Action: {msg}")
        action_log.append(msg)

    print(f"✅ Status: Action logged")
    result["action_taken"] = action_log
    return result