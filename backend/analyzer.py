import os

def analyze_log(log):
    log_lower = log.lower()

    if "modulenotfounderror" in log_lower:
        return {
            "type": "Dependency Issue",
            "reason": "Missing Python package detected in the environment",
            "fix": "Install missing package using pip install <package_name>",
            "confidence": "High"
        }

    elif "assertionerror" in log_lower:
        return {
            "type": "Test Failure",
            "reason": "A test case failed due to incorrect output",
            "fix": "Check failed test case and fix logic",
            "confidence": "High"
        }

    elif "timeout" in log_lower or "timed out" in log_lower:
        return {
            "type": "Timeout Error",
            "reason": "Process exceeded time limit",
            "fix": "Optimize code or increase timeout settings",
            "confidence": "Medium"
        }

    elif "failed" in log_lower:
        return {
            "type": "General Failure",
            "reason": "Pipeline execution failed",
            "fix": "Check logs and retry the pipeline",
            "confidence": "Medium"
        }

    else:
        return {
            "type": "Unknown",
            "reason": "Could not determine the issue from logs",
            "fix": "Manual debugging required",
            "confidence": "Low"
        }


# 🔥 Day 4: Multi-log analyzer (improved)
log_folder = "data"

for filename in os.listdir(log_folder):

    # ✅ Only read .txt files (important improvement)
    if filename.endswith(".txt"):

        file_path = os.path.join(log_folder, filename)

        with open(file_path, "r") as file:
            log = file.read()

        result = analyze_log(log)

        print(f"\n📄 {filename}")
        print("Type:", result["type"])
        print("Reason:", result["reason"])
        print("Fix:", result["fix"])
        print("Confidence:", result["confidence"]) 