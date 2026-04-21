from flask import Flask, jsonify
import os
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# ── 3 Pipeline definitions ────────────────────────────────────────────────────
PIPELINES = {
    "python-flaky-tests": {
        "description": "Python project with flaky unit tests",
        "logs": ["log4.txt", "log10.txt", "log18.txt", "log2.txt", "log16.txt"]
    },
    "docker-image-build": {
        "description": "Docker image build pipeline",
        "logs": ["log1.txt", "log9.txt", "log15.txt", "log5.txt", "log13.txt"]
    },
    "kubernetes-deploy": {
        "description": "Deployment pipeline to Kubernetes cluster",
        "logs": ["log3.txt", "log11.txt", "log17.txt", "log6.txt", "log14.txt"]
    }
}

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "..", "data")

def read_log(filename):
    path = os.path.join(DATA_FOLDER, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return "Log file not found"

def random_duration():
    return random.randint(45000, 180000)

def random_result():
    return random.choice(["FAILURE", "FAILURE", "SUCCESS"])

# ── Jenkins REST API endpoints ─────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Mock Jenkins Server Running",
        "version": "2.426.1",
        "pipelines": list(PIPELINES.keys()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/api/json", methods=["GET"])
def jenkins_root():
    jobs = []
    for name, info in PIPELINES.items():
        jobs.append({
            "name": name,
            "url": f"http://localhost:5000/job/{name}/",
            "color": "red",
            "description": info["description"]
        })
    return jsonify({"jobs": jobs, "numExecutors": 2})

@app.route("/job/<pipeline_name>/api/json", methods=["GET"])
def pipeline_info(pipeline_name):
    if pipeline_name not in PIPELINES:
        return jsonify({"error": "Pipeline not found"}), 404

    builds = []
    for i in range(1, 6):
        builds.append({
            "number": i,
            "url": f"http://localhost:5000/job/{pipeline_name}/{i}/",
            "result": random_result(),
            "duration": random_duration(),
            "timestamp": int((datetime.now() - timedelta(hours=i*2)).timestamp() * 1000)
        })

    return jsonify({
        "name": pipeline_name,
        "description": PIPELINES[pipeline_name]["description"],
        "builds": builds,
        "lastBuild": {"number": 5, "url": f"http://localhost:5000/job/{pipeline_name}/5/"},
        "lastFailedBuild": {"number": 4},
        "lastSuccessfulBuild": {"number": 3},
        "healthReport": [{"description": "Build stability: 2 out of 5 builds failed", "score": 60}]
    })

@app.route("/job/<pipeline_name>/lastBuild/api/json", methods=["GET"])
def last_build_info(pipeline_name):
    if pipeline_name not in PIPELINES:
        return jsonify({"error": "Pipeline not found"}), 404

    return jsonify({
        "number": 5,
        "result": "FAILURE",
        "duration": random_duration(),
        "timestamp": int(datetime.now().timestamp() * 1000),
        "url": f"http://localhost:5000/job/{pipeline_name}/5/",
        "stages": [
            {"name": "Checkout",   "status": "SUCCESS", "durationMillis": 12000},
            {"name": "Build",      "status": "SUCCESS", "durationMillis": 45000},
            {"name": "Test",       "status": "FAILED",  "durationMillis": 23000},
            {"name": "Deploy",     "status": "ABORTED", "durationMillis": 0}
        ]
    })

@app.route("/job/<pipeline_name>/lastBuild/consoleText", methods=["GET"])
def console_log(pipeline_name):
    if pipeline_name not in PIPELINES:
        return "Pipeline not found", 404

    logs = PIPELINES[pipeline_name]["logs"]
    log_file = random.choice(logs)
    log_content = read_log(log_file)

    header = f"""
Started by user admin
Running in Durability level: MAX_SURVIVABILITY
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in /var/jenkins_home/workspace/{pipeline_name}
[Pipeline] stage: Checkout
Cloning repository https://github.com/example/{pipeline_name}.git
[Pipeline] stage: Build
+ pip install -r requirements.txt
[Pipeline] stage: Test
+ python -m pytest tests/
"""
    return header + "\n" + log_content + "\nFinished: FAILURE"

@app.route("/job/<pipeline_name>/lastBuild/testReport/api/json", methods=["GET"])
def test_report(pipeline_name):
    return jsonify({
        "failCount": 2,
        "passCount": 8,
        "skipCount": 1,
        "duration": 12.4,
        "suites": [{
            "name": f"{pipeline_name}-tests",
            "cases": [
                {"name": "test_login",    "status": "PASSED",  "duration": 2.1},
                {"name": "test_payment",  "status": "FAILED",  "duration": 3.2,
                 "errorDetails": "AssertionError: expected 200 got 404"},
                {"name": "test_logout",   "status": "PASSED",  "duration": 1.8},
                {"name": "test_register", "status": "FAILED",  "duration": 2.9,
                 "errorDetails": "Timeout: exceeded 30s"},
                {"name": "test_profile",  "status": "PASSED",  "duration": 2.4}
            ]
        }]
    })

@app.route("/job/<pipeline_name>/<int:build_number>/consoleText", methods=["GET"])
def build_console_log(pipeline_name, build_number):
    if pipeline_name not in PIPELINES:
        return "Pipeline not found", 404
    logs = PIPELINES[pipeline_name]["logs"]
    log_file = logs[build_number % len(logs)]
    return read_log(log_file)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Mock Jenkins Server Starting...")
    print("  URL: http://localhost:5000")
    print("  Pipelines:")
    for name in PIPELINES:
        print(f"    - {name}")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)