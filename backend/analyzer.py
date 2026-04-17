def analyze_log(log):
    if "ModuleNotFoundError" in log:
        return {
            "type": "Dependency Issue",
            "fix": "Install missing package using pip install numpy"
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


# Test run
with open("data/log1.txt", "r") as file:
    log = file.read()

result = analyze_log(log)

print("Failure Type:", result["type"])
print("Suggested Fix:", result["fix"])