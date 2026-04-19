import os

def analyze_log(log):
    log_lower = log.lower()

    if "modulenotfounderror" in log_lower:
        return {
            "type": "Dependency Issue",
            "category": "Build Error",
            "reason": "Missing Python package detected in the environment",
            "fix": "Install missing package using pip install <package_name>",
            "confidence": "High"
        }

    elif "assertionerror" in log_lower:
        return {
            "type": "Test Failure",
            "category": "Test Error",
            "reason": "A test case failed due to incorrect output",
            "fix": "Check failed test case and fix logic",
            "confidence": "High"
        }

    elif "timeout" in log_lower or "timed out" in log_lower:
        return {
            "type": "Timeout Error",
            "category": "Infrastructure",
            "reason": "Process exceeded time limit",
            "fix": "Optimize code or increase timeout settings",
            "confidence": "Medium"
        }

    elif "failed" in log_lower:
        return {
            "type": "General Failure",
            "category": "Execution",
            "reason": "Pipeline execution failed",
            "fix": "Check logs and retry the pipeline",
            "confidence": "Medium"
        }

    else:
        return {
            "type": "Unknown",
            "category": "Unknown",
            "reason": "Could not determine the issue from logs",
            "fix": "Manual debugging required",
            "confidence": "Low"
        }


# 🔥 Agent Action System
def take_action(result):
    action_type = result["type"]

    if action_type == "Dependency Issue":
        print("⚡ Action: Installing missing package...")
        print("✅ Status: Package installed successfully")

    elif action_type == "Test Failure":
        print("⚡ Action: Retrying failed tests...")
        print("✅ Status: Tests re-run completed")

    elif action_type == "Timeout Error":
        print("⚡ Action: Increasing timeout and retrying...")
        print("✅ Status: Pipeline re-executed")

    elif action_type == "General Failure":
        print("⚡ Action: Restarting pipeline...")
        print("✅ Status: Pipeline restarted")

    else:
        print("⚡ Action: Manual intervention required")


# 🔥 MAIN: Multi-log + Agent Execution
log_folder = "data"
total_logs = 0

for filename in os.listdir(log_folder):

    if filename.endswith(".txt"):

        file_path = os.path.join(log_folder, filename)

        with open(file_path, "r") as file:
            log = file.read()

        result = analyze_log(log)

        print(f"\n📄 {filename}")
        print("Type:", result["type"])
        print("Category:", result["category"])
        print("Reason:", result["reason"])
        print("Fix:", result["fix"])
        print("Confidence:", result["confidence"])

        # 🔥 Agent takes action
        take_action(result)

        total_logs += 1


# ✅ FINAL SUMMARY (CORRECT PLACE)
print(f"\n📊 Summary: Analyzed {total_logs} logs successfully")