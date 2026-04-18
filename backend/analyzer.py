import os

def analyze_log(log):
    if "ModuleNotFoundError" in log:
        return {
            "type": "Dependency Issue",
            "fix": "Install missing package using pip install numpy"
        }

    elif "AssertionError" in log:
        return {
            "type": "Test Failure",
            "fix": "Check failed test case and fix logic"
        }

    elif "failed" in log:
        return {
            "type": "General Failure",
            "fix": "Check logs and retry the pipeline"
        }

    else:
        return {
            "type": "Unknown",
            "fix": "Manual debugging required"
        }


# 🔥 Day 3: Multi-log analyzer
log_folder = "data"

for filename in os.listdir(log_folder):
    file_path = os.path.join(log_folder, filename)

    with open(file_path, "r") as file:
        log = file.read()

    result = analyze_log(log)

    print(f"\n📄 {filename}")
    print("Failure Type:", result["type"])
    print("Suggested Fix:", result["fix"])