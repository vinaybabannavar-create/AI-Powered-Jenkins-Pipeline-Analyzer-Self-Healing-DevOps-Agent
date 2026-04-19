import os

def analyze_log(log):
    if "ModuleNotFoundError" in log:
        return {
            "type": "Dependency Issue",
            "reason": "Missing Python package detected in the environment",
            "fix": "Install missing package using pip install <package_name>"
        }

    elif "AssertionError" in log:
        return {
            "type": "Test Failure",
            "reason": "A test case failed due to incorrect output",
            "fix": "Check failed test case and fix logic"
        }

    elif "timeout" in log.lower() or "timed out" in log.lower():
        return {
            "type": "Timeout Error",
            "reason": "Process exceeded time limit",
            "fix": "Optimize code or increase timeout settings"
        }

    elif "failed" in log.lower():
        return {
            "type": "General Failure",
            "reason": "Pipeline execution failed",
            "fix": "Check logs and retry the pipeline"
        }

    else:
        return {
            "type": "Unknown",
            "reason": "Could not determine the issue from logs",
            "fix": "Manual debugging required"
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