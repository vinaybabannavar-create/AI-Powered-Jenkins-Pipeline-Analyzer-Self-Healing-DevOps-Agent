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

def check_jenkins_running():
    try:
        response = requests.get(f"{JENKINS_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

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

def get_status_icon(result, issue_type):
    if result == "SUCCESS":
        return "🟢"
    elif issue_type == "Unknown":
        return "🟡"
    else:
        return "🔴"

def run_jenkins_agent():
    print("\n" + "="*55)
    print("  🤖 Jenkins AI Agent — Fetching from Mock Jenkins API")
    print("="*55)

    # ── Check Jenkins is running ──────────────────────────────
    if not check_jenkins_running():
        print("\n❌ Mock Jenkins server is not running!")
        print("   Please start it first:")
        print("   py -3.10 mock_jenkins.py")
        return []

    print("✅ Mock Jenkins server connected at", JENKINS_URL)
    print(f"📋 Analyzing {len(PIPELINES)} pipelines...\n")

    all_results = []

    for pipeline in PIPELINES:
        print(f"📡 Fetching pipeline: {pipeline}")
        print("-"*45)

        # Fetch from Jenkins REST API
        build_info  = fetch_build_info(pipeline)
        console_log = fetch_console_log(pipeline)
        test_report = fetch_test_report(pipeline)

        build_num    = build_info.get("number", "N/A")
        build_result = build_info.get("result", "N/A")
        duration_ms  = build_info.get("duration", 0)

        print(f"   Build #    : {build_num}")
        print(f"   Result     : {build_result}")
        print(f"   Duration   : {duration_ms/1000:.1f} seconds")

        if test_report:
            pass_count = test_report.get("passCount", 0)
            fail_count = test_report.get("failCount", 0)
            print(f"   Tests Pass : {pass_count}")
            print(f"   Tests Fail : {fail_count}")

        # Stage timings
        stages = build_info.get("stages", [])
        if stages:
            print("   Stages:")
            for stage in stages:
                status_icon = "✅" if stage["status"] == "SUCCESS" else "❌"
                print(f"     {status_icon} {stage['name']:<12} → {stage['status']}")

        # AI Analysis
        result = analyze_log(console_log)
        result = take_action(result)

        print(f"\n   🔍 AI Analysis:")
        print(f"   Type       : {result['type']}")
        print(f"   Category   : {result['category']}")
        print(f"   Confidence : {result['confidence']}")
        print(f"   Source     : {result.get('source','regex')}")
        print(f"   Reason     : {result['reason']}")
        print(f"   Fix        : {result['fix']}")

        action = result.get("action_taken", [])
        if action:
            print(f"   Action     : {action[0]}")

        all_results.append({
            "pipeline":    pipeline,
            "build":       build_num,
            "result":      build_result,
            "duration_sec": round(duration_ms/1000, 1),
            "tests_pass":  test_report.get("passCount", 0),
            "tests_fail":  test_report.get("failCount", 0),
            "type":        result["type"],
            "category":    result["category"],
            "confidence":  result["confidence"],
            "fix":         result["fix"],
            "source":      result.get("source", "regex"),
            "action":      action[0] if action else "None",
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        print()

    # ── Pipeline Health Summary ───────────────────────────────
    print("="*55)
    print("  📊 PIPELINE HEALTH SUMMARY")
    print("="*55)
    for r in all_results:
        icon = get_status_icon(r["result"], r["type"])
        print(f"  {icon} {r['pipeline']:<30} → {r['type']:<25} [{r['confidence']}]")

    # ── MTTR Calculation ──────────────────────────────────────
    failed = [r for r in all_results if r["result"] == "FAILURE"]
    if failed:
        print(f"\n  ❌ Failed Pipelines : {len(failed)}/{len(PIPELINES)}")
        print(f"  ⏱  Avg Duration    : {sum(r['duration_sec'] for r in failed)/len(failed):.1f} sec")

    # ── Save pipeline report ──────────────────────────────────
    report_path = os.path.join(os.path.dirname(__file__), "pipeline_report.json")
    with open(report_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_pipelines": len(PIPELINES),
            "failed_pipelines": len([r for r in all_results if r["result"] == "FAILURE"]),
            "pipelines": all_results
        }, f, indent=2)

    print(f"\n✅ Pipeline report saved to pipeline_report.json")
    print("✅ Run dashboard to see live results\n")
    return all_results

if __name__ == "__main__":
    run_jenkins_agent()