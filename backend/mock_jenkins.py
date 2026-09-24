from flask import Flask, jsonify, render_template_string, request, redirect, url_for
import os
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# ── 3 Pipeline definitions ────────────────────────────────────────────────────
PIPELINES = {
    "python-flaky-tests": {
        "description": "Python project with flaky unit tests and retry logic",
        "logs": ["log4.txt", "log10.txt", "log18.txt", "log2.txt", "log16.txt"]
    },
    "docker-image-build": {
        "description": "Docker container build and automated dependency resolution",
        "logs": ["log1.txt", "log9.txt", "log15.txt", "log5.txt", "log13.txt"]
    },
    "kubernetes-deploy": {
        "description": "Deployment pipeline to Kubernetes cluster with timeout mitigation",
        "logs": ["log3.txt", "log11.txt", "log17.txt", "log6.txt", "log14.txt"]
    }
}

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "..", "data")

def read_log(filename):
    path = os.path.join(DATA_FOLDER, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return "Log file not found"

def random_duration():
    return random.randint(45000, 180000)

def random_result():
    return random.choice(["FAILURE", "FAILURE", "SUCCESS"])

# ── Authentic Jenkins HTML Template ──────────────────────────────────────────
JENKINS_BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>{{ title }} - Jenkins</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Roboto', sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.5; }
    .topbar { background: #1f2937; color: #fff; padding: 0.75rem 1.5rem; display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid #3b82f6; }
    .logo-area { display: flex; align-items: center; gap: 10px; }
    .logo-img { font-size: 1.6rem; }
    .logo-title { font-weight: 700; font-size: 1.15rem; letter-spacing: -0.5px; }
    .logo-sub { font-size: 0.72rem; color: #94a3b8; }
    .nav-bar { background: #334155; color: #e2e8f0; padding: 0.5rem 1.5rem; font-size: 0.85rem; display: flex; align-items: center; gap: 8px; }
    .nav-bar a { color: #93c5fd; text-decoration: none; }
    .nav-bar a:hover { text-decoration: underline; }
    .main-layout { display: flex; max-width: 1300px; margin: 1.5rem auto; padding: 0 1rem; gap: 24px; }
    .sidebar { width: 240px; }
    .sidebar-menu { list-style: none; background: #fff; border-radius: 8px; border: 1px solid #e2e8f0; overflow: hidden; }
    .sidebar-menu li a { display: flex; align-items: center; gap: 8px; padding: 0.75rem 1rem; color: #334155; text-decoration: none; font-size: 0.88rem; font-weight: 500; border-bottom: 1px solid #f1f5f9; }
    .sidebar-menu li a:hover { background: #f8fafc; color: #2563eb; }
    .content { flex: 1; }
    .card { background: #fff; border-radius: 8px; border: 1px solid #e2e8f0; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .badge { display: inline-block; padding: 0.25rem 0.6rem; font-size: 0.75rem; font-weight: 700; border-radius: 4px; }
    .badge-FAILURE { background: #fee2e2; color: #b91c1c; }
    .badge-SUCCESS { background: #dcfce7; color: #15803d; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    th { text-align: left; padding: 0.75rem; background: #f8fafc; font-size: 0.75rem; text-transform: uppercase; color: #64748b; border-bottom: 1px solid #e2e8f0; }
    td { padding: 0.75rem; border-bottom: 1px solid #f1f5f9; font-size: 0.88rem; }
    tr:hover td { background: #f8fafc; }
    .btn { display: inline-flex; align-items: center; gap: 6px; padding: 0.5rem 1rem; background: #2563eb; color: #fff; text-decoration: none; border-radius: 6px; font-size: 0.85rem; font-weight: 600; border: none; cursor: pointer; }
    .btn:hover { background: #1d4ed8; }
    .btn-secondary { background: #e2e8f0; color: #1e293b; }
    .btn-secondary:hover { background: #cbd5e1; }
    .console-box { background: #0f172a; color: #f8fafc; padding: 1.2rem; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; line-height: 1.6; white-space: pre-wrap; max-height: 600px; overflow-y: auto; }
  </style>
</head>
<body>
  <div class="topbar">
    <div class="logo-area">
      <div class="logo-img">⚙️</div>
      <div>
        <div class="logo-title">Jenkins Automation Server</div>
        <div class="logo-sub">Enterprise DevOps CI/CD Engine (Mock/Demo Environment)</div>
      </div>
    </div>
    <div style="font-size: 0.85rem; color: #cbd5e1;">
      User: <strong>admin</strong> | <a href="http://localhost:8501" style="color: #60a5fa; text-decoration: none; font-weight: 600;">⚡ Back to AI Dashboard</a>
    </div>
  </div>

  <div class="nav-bar">
    <a href="/">Dashboard</a>
    {% if pipeline_name %}
      <span>&gt;</span> <a href="/job/{{ pipeline_name }}">{{ pipeline_name }}</a>
    {% endif %}
    {% if build_number %}
      <span>&gt;</span> <span>#{{ build_number }}</span>
    {% endif %}
  </div>

  <div class="main-layout">
    <div class="sidebar">
      <ul class="sidebar-menu">
        <li><a href="/">📋 All Pipelines</a></li>
        {% if pipeline_name %}
          <li><a href="/job/{{ pipeline_name }}/build" style="color: #16a34a;">▶ Build Now</a></li>
          <li><a href="/job/{{ pipeline_name }}/lastBuild/console">💻 Console Output</a></li>
          <li><a href="/job/{{ pipeline_name }}/lastBuild">🔍 Last Build Info</a></li>
        {% endif %}
        <li><a href="http://localhost:8501">🤖 AI Self-Healing Center</a></li>
      </ul>
    </div>

    <div class="content">
      {{ body_content | safe }}
    </div>
  </div>
</body>
</html>
"""

# ── HTML Views ────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "message": "Mock Jenkins Server Running",
            "version": "2.426.1",
            "pipelines": list(PIPELINES.keys()),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    jobs_html = ""
    for name, info in PIPELINES.items():
        jobs_html += f"""
        <tr>
          <td><span style="font-size: 1.2rem;">🔴</span></td>
          <td><a href="/job/{name}" style="color: #2563eb; font-weight: 600; text-decoration: none;">{name}</a></td>
          <td>{info['description']}</td>
          <td><span class="badge badge-FAILURE">Build #5 Failed</span></td>
          <td>
            <a href="/job/{name}/build" class="btn" style="padding: 0.3rem 0.7rem; font-size: 0.75rem;">Build Now</a>
            <a href="/job/{name}/lastBuild/console" class="btn btn-secondary" style="padding: 0.3rem 0.7rem; font-size: 0.75rem;">Console</a>
          </td>
        </tr>
        """

    content = f"""
    <div class="card">
      <h2 style="font-size: 1.3rem; margin-bottom: 0.5rem;">Pipeline Dashboard</h2>
      <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1.2rem;">Monitored Jenkins pipelines managed by the Autonomous AI Agent.</p>
      <table>
        <thead>
          <tr>
            <th>Status</th>
            <th>Pipeline Name</th>
            <th>Description</th>
            <th>Last Build</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {jobs_html}
        </tbody>
      </table>
    </div>
    """
    return render_template_string(JENKINS_BASE_HTML, title="Dashboard", body_content=content, pipeline_name=None, build_number=None)

@app.route("/job/<pipeline_name>", methods=["GET", "POST"])
@app.route("/job/<pipeline_name>/", methods=["GET", "POST"])
def job_view(pipeline_name):
    if pipeline_name not in PIPELINES:
        return f"Pipeline '{pipeline_name}' not found", 404

    info = PIPELINES[pipeline_name]
    builds_rows = ""
    for i in range(5, 0, -1):
        status = "FAILURE" if i >= 4 else ("SUCCESS" if i == 3 else "FAILURE")
        builds_rows += f"""
        <tr>
          <td><a href="/job/{pipeline_name}/{i}" style="color: #2563eb; font-weight: 600;">#{i}</a></td>
          <td><span class="badge badge-{status}">{status}</span></td>
          <td>{datetime.now().strftime("%Y-%m-%d %H:%M")}</td>
          <td>{(i*23)+12}s</td>
          <td><a href="/job/{pipeline_name}/{i}/console" style="color: #2563eb;">View Console</a></td>
        </tr>
        """

    content = f"""
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
          <h1 style="font-size: 1.4rem;">Pipeline: {pipeline_name}</h1>
          <p style="color: #64748b; font-size: 0.88rem;">{info['description']}</p>
        </div>
        <div style="display: flex; gap: 8px;">
          <a href="/job/{pipeline_name}/build" class="btn">▶ Trigger Build</a>
          <a href="/job/{pipeline_name}/lastBuild/console" class="btn btn-secondary">💻 Last Console</a>
        </div>
      </div>

      <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 0.9rem; margin-bottom: 1.5rem; font-size: 0.85rem; color: #1e40af;">
        ⚡ <strong>Autonomous AI Remediation:</strong> Monitored by AI-Powered Jenkins Analyzer with automatic root cause detection and healing.
      </div>

      <h3 style="font-size: 1.1rem; margin-bottom: 0.6rem;">Build History</h3>
      <table>
        <thead>
          <tr>
            <th>Build</th>
            <th>Result</th>
            <th>Timestamp</th>
            <th>Duration</th>
            <th>Console</th>
          </tr>
        </thead>
        <tbody>
          {builds_rows}
        </tbody>
      </table>
    </div>
    """
    return render_template_string(JENKINS_BASE_HTML, title=pipeline_name, body_content=content, pipeline_name=pipeline_name, build_number=None)

@app.route("/job/<pipeline_name>/<int:build_number>", methods=["GET"])
@app.route("/job/<pipeline_name>/<int:build_number>/", methods=["GET"])
@app.route("/job/<pipeline_name>/lastBuild", methods=["GET"])
@app.route("/job/<pipeline_name>/lastBuild/", methods=["GET"])
def build_view(pipeline_name, build_number=5):
    if pipeline_name not in PIPELINES:
        return f"Pipeline '{pipeline_name}' not found", 404

    content = f"""
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
          <h1 style="font-size: 1.4rem;">{pipeline_name} # {build_number}</h1>
          <div style="margin-top: 4px;">
            <span class="badge badge-FAILURE">FAILURE</span>
            <span style="font-size: 0.85rem; color: #64748b; margin-left: 8px;">Duration: 74s · Completed {datetime.now().strftime("%H:%M:%S")}</span>
          </div>
        </div>
        <a href="/job/{pipeline_name}/{build_number}/console" class="btn">💻 View Console Output</a>
      </div>

      <h3 style="font-size: 1.05rem; margin-bottom: 0.5rem;">Pipeline Stages</h3>
      <div style="display: flex; gap: 8px; margin-bottom: 1.5rem;">
        <div style="flex: 1; background: #f0fdf4; border: 1px solid #bbf7d0; padding: 0.8rem; border-radius: 6px; text-align: center;">
          <div style="font-size: 0.75rem; color: #166534; font-weight: 700;">CHECKOUT</div>
          <div style="font-weight: 700; color: #15803d;">SUCCESS</div>
        </div>
        <div style="flex: 1; background: #f0fdf4; border: 1px solid #bbf7d0; padding: 0.8rem; border-radius: 6px; text-align: center;">
          <div style="font-size: 0.75rem; color: #166534; font-weight: 700;">BUILD</div>
          <div style="font-weight: 700; color: #15803d;">SUCCESS</div>
        </div>
        <div style="flex: 1; background: #fef2f2; border: 1px solid #fecaca; padding: 0.8rem; border-radius: 6px; text-align: center;">
          <div style="font-size: 0.75rem; color: #991b1b; font-weight: 700;">TEST</div>
          <div style="font-weight: 700; color: #b91c1c;">FAILED</div>
        </div>
        <div style="flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; padding: 0.8rem; border-radius: 6px; text-align: center;">
          <div style="font-size: 0.75rem; color: #64748b; font-weight: 700;">DEPLOY</div>
          <div style="font-weight: 700; color: #64748b;">ABORTED</div>
        </div>
      </div>
    </div>
    """
    return render_template_string(JENKINS_BASE_HTML, title=f"{pipeline_name} #{build_number}", body_content=content, pipeline_name=pipeline_name, build_number=build_number)

@app.route("/job/<pipeline_name>/console", methods=["GET"])
@app.route("/job/<pipeline_name>/lastBuild/console", methods=["GET"])
@app.route("/job/<pipeline_name>/<int:build_number>/console", methods=["GET"])
def console_view(pipeline_name, build_number=5):
    if pipeline_name not in PIPELINES:
        return f"Pipeline '{pipeline_name}' not found", 404

    logs = PIPELINES[pipeline_name]["logs"]
    log_file = logs[build_number % len(logs)] if build_number else logs[0]
    log_content = read_log(log_file)
    header = f"Started by user admin\nRunning in Durability level: MAX_SURVIVABILITY\n[Pipeline] Start of Pipeline\nRunning on Jenkins node in /var/jenkins_home/workspace/{pipeline_name}\n[Pipeline] stage: Checkout\n[Pipeline] stage: Build\n[Pipeline] stage: Test\n\n"
    full_log = header + log_content + "\n\nFinished: FAILURE"

    content = f"""
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
          <h1 style="font-size: 1.3rem;">Console Output: {pipeline_name} #{build_number}</h1>
          <span class="badge badge-FAILURE">Finished: FAILURE</span>
        </div>
        <a href="/job/{pipeline_name}" class="btn btn-secondary">← Back to Pipeline</a>
      </div>
      <div class="console-box">{full_log}</div>
    </div>
    """
    return render_template_string(JENKINS_BASE_HTML, title=f"Console - {pipeline_name} #{build_number}", body_content=content, pipeline_name=pipeline_name, build_number=build_number)

@app.route("/job/<pipeline_name>/build", methods=["GET", "POST"])
@app.route("/job/<pipeline_name>/buildWithParameters", methods=["GET", "POST"])
def trigger_build_route(pipeline_name):
    if pipeline_name not in PIPELINES:
        return f"Pipeline '{pipeline_name}' not found", 404
    return redirect(f"/job/{pipeline_name}")

# ── JSON APIs for Automated Agents ─────────────────────────────────────────────

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
    header = f"Started by user admin\nRunning in Durability level: MAX_SURVIVABILITY\n[Pipeline] Start of Pipeline\nRunning on Jenkins node in /var/jenkins_home/workspace/{pipeline_name}\n[Pipeline] stage: Checkout\n[Pipeline] stage: Build\n[Pipeline] stage: Test\n\n"
    return header + log_content + "\nFinished: FAILURE"

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