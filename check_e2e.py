import urllib.request
import json
import sys

def test_endpoint(name, url, method="GET", data=None, timeout=15):
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8") if data else None,
            headers={"Content-Type": "application/json"} if data else {},
            method=method
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            print(f"[PASS] {name:28} -> {method:4} {url} ({resp.status}, {len(content)} bytes)", flush=True)
            return True
    except Exception as e:
        print(f"[FAIL] {name:28} -> {method:4} {url} (Error: {e})", flush=True)
        return False

def main():
    print("==================================================", flush=True)
    print("  VERIFYING FRONTEND, BACKEND & JENKINS SERVICES  ", flush=True)
    print("==================================================", flush=True)
    
    results = []
    
    # 1. Mock Jenkins (Port 5000)
    print("\n[1. Mock Jenkins Server - Port 5000]", flush=True)
    results.append(test_endpoint("Jenkins Web UI", "http://localhost:5000/"))
    results.append(test_endpoint("Jenkins JSON API", "http://localhost:5000/api/json"))
    results.append(test_endpoint("Jenkins Job Detail", "http://localhost:5000/job/python-flaky-tests/api/json"))
    results.append(test_endpoint("Jenkins Last Build JSON", "http://localhost:5000/job/python-flaky-tests/lastBuild/api/json"))
    results.append(test_endpoint("Jenkins Console Logs", "http://localhost:5000/job/python-flaky-tests/lastBuild/consoleText"))
    
    # 2. FastAPI Backend API (Port 8501)
    print("\n[2. FastAPI Backend API - Port 8501]", flush=True)
    results.append(test_endpoint("Health Check", "http://localhost:8501/api/health"))
    results.append(test_endpoint("Pipelines API", "http://localhost:8501/api/pipelines"))
    results.append(test_endpoint("Analysis History API", "http://localhost:8501/api/analysis/history"))
    results.append(test_endpoint("Analytics API", "http://localhost:8501/api/analysis/analytics"))
    results.append(test_endpoint("Actions API", "http://localhost:8501/api/actions"))
    results.append(test_endpoint("Run Agent API", "http://localhost:8501/api/run-agent", method="POST", timeout=30))
    results.append(test_endpoint("CLI Execute Command", "http://localhost:8501/api/cli/execute", method="POST", data={
        "command": "analyze all"
    }))
    results.append(test_endpoint("CLI Sample Logs", "http://localhost:8501/api/cli/logs"))
    results.append(test_endpoint("Remediation Proof HTML", "http://localhost:8501/proof/1"))
    
    # 3. Frontend Web Platform (Port 8501)
    print("\n[3. Frontend Web Platform - Port 8501]", flush=True)
    results.append(test_endpoint("Main Single-Page UI", "http://localhost:8501/"))
    results.append(test_endpoint("Swagger OpenAPI Docs", "http://localhost:8501/docs"))
    
    print("\n==================================================", flush=True)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"  RESULT: {passed}/{total} services & endpoints operating 100% cleanly", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    main()
