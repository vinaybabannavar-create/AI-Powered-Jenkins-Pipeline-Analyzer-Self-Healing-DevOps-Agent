import requests
import json
import os
import csv
from datetime import datetime
from analyzer import analyze_log, take_action

JENKINS_URL = "http://localhost:5000"

PIPELINES = [
    "python-flaky-tests",
    "docker-image-build",
    "kubernetes-deploy"
]

def fetch_console_log(pipeline):
    try:
        url = f"{JENKINS_URL}/job/{pipeline}/lastBuild/consoleText"
        response = requests.get(url, timeout=10)
        return response.text
    except Exception as e:
        return f"Error fetching log: {str(e)}"

def fetch_build_info(pipeline):
    try:
        url = f"{JENKINS_URL}/job/{pipeline}/lastBuild/api/json"
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {}

def fetch_test_report(pipeline):
    try:
        url = f"{JENKINS_URL}/job/{pipeline}/lastBuild/testReport/api/json"
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {}

def run_jenkins_agent():
    print("\n" + "="*55)
    print("  🤖 Jenkins AI Agent — Fetching from Mock Jenkins API")
    print("="*55)

    all_results = []

    for pipeline in PIPELINES:
        print(f"\n📡 Fetching pipeline: {pipeline}")
        print("-"*45)

        # Fetch from Jenkins REST API
        build_info  = fetch_build_info(pipeline)
        console_log = fetch_console_log(pipeline)
        test_report = fetch_test_report(pipeline)

        print(f"   Build #    : {build_info.get('number', 'N/A')}")
        print(f"   Result     : {build_info.get('result', 'N/A')}")
        duration_ms = build_info.get('duration', 0)
        print(f"   Duration   : {duration_ms/1000:.1f} seconds")

        if test_report:
            print(f"   Tests Pass : {test_report.get('passCount', 0)}")
            print(f"   Tests Fail : {test_report.get('failCount', 0)}")

        # Analyze with AI
        result = analyze_log(console_log)
        result = take_action(result)

        print(f"\n   🔍 AI Analysis:")
        print(f"   Type       : {result['type']}")
        print(f"   Confidence : {result['confidence']}")
        print(f"   Source     : {result.get('source','regex')}")
        print(f"   Fix        : {result['fix']}")

        all_results.append({
            "pipeline":   pipeline,
            "build":      build_info.get("number", "N/A"),
            "result":     build_info.get("result", "N/A"),
            "type":       result["type"],
            "confidence": result["confidence"],
            "fix":        result["fix"],
            "source":     result.get("source", "regex"),
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    # Save pipeline report
    report_path = os.path.join(os.path.dirname(__file__), "pipeline_report.json")
    with open(report_path, "w") as f:
        json.dump(all_results, f, indent=2)

    # Summary
    print("\n" + "="*55)
    print("  📊 PIPELINE HEALTH SUMMARY")
    print("="*55)
    for r in all_results:
        status = "🔴" if r["result"] == "FAILURE" else "🟢"
        print(f"  {status} {r['pipeline']:<30} → {r['type']}")

    print(f"\n✅ Pipeline report saved to pipeline_report.json")
    return all_results

if __name__ == "__main__":
    run_jenkins_agent()