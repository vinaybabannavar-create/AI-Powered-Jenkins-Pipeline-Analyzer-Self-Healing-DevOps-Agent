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

# ── Modern Pitch-Black Jenkins HTML Template ─────────────────────────────────
JENKINS_BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>{{ title }} - Jenkins Automation Server</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: #000000 !important;
      color: #f8fafc;
      line-height: 1.5;
      min-height: 100vh;
      overflow-x: hidden;
      position: relative;
    }

    /* Ambient Background Auroras & Grid */
    .aurora-container { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; background: #000000; }
    .aurora-orb { position: absolute; border-radius: 50%; filter: blur(140px); opacity: 0.16; animation: floatAurora 20s infinite alternate ease-in-out; }
    .aurora-1 { width: 650px; height: 650px; background: #4f46e5; top: -100px; left: -100px; }
    .aurora-2 { width: 700px; height: 700px; background: #06b6d4; bottom: -150px; right: -100px; animation-duration: 25s; }
    @keyframes floatAurora { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(-40px, 80px) scale(0.95); } }

    .bg-grid {
      position: fixed; inset: 0; pointer-events: none; z-index: 1;
      background-image: linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
      background-size: 48px 48px;
    }

    #mouse-spotlight {
      position: fixed; inset: 0; pointer-events: none; z-index: 2;
      background: radial-gradient(800px circle at var(--mouse-x, 50vw) var(--mouse-y, 50vh), rgba(6, 182, 212, 0.18), rgba(99, 102, 241, 0.12) 35%, transparent 80%);
    }

    .app-wrapper { position: relative; z-index: 10; min-height: 100vh; display: flex; flex-direction: column; background: #000000; }

    /* Top Bar */
    .topbar {
      background: #000000 !important; color: #fff; padding: 0.9rem 2rem;
      display: flex; align-items: center; justify-content: space-between;
      border-bottom: 1px solid rgba(255, 255, 255, 0.12); position: sticky; top: 0; z-index: 100;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.95);
    }
    .logo-area { display: flex; align-items: center; gap: 12px; }
    .logo-img {
      width: 40px; height: 40px; border-radius: 10px; background: linear-gradient(135deg, #6366f1, #06b6d4);
      display: flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
    }
    .logo-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.15rem; color: #fff; letter-spacing: -0.5px; }
    .logo-sub { font-size: 0.72rem; color: #06b6d4; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }

    .nav-bar {
      background: #000000 !important; color: #94a3b8; padding: 0.6rem 2rem; font-size: 0.82rem;
      display: flex; align-items: center; gap: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .nav-bar a { color: #38bdf8; text-decoration: none; font-weight: 600; }
    .nav-bar a:hover { text-decoration: underline; color: #67e8f9; }

    .main-layout { display: flex; max-width: 1440px; width: 100%; margin: 1.5rem auto; padding: 0 2rem; gap: 24px; flex: 1; }
    .sidebar { width: 250px; flex-shrink: 0; }
    .sidebar-menu { list-style: none; background: #000000; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.12); overflow: hidden; }
    .sidebar-menu li a { display: flex; align-items: center; gap: 10px; padding: 0.85rem 1.1rem; color: #cbd5e1; text-decoration: none; font-size: 0.86rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: all 0.2s; }
    .sidebar-menu li a:hover { background: rgba(99, 102, 241, 0.14); color: #fff; transform: translateX(3px); }

    .content { flex: 1; width: 100%; min-width: 0; }
    .card {
      background: #000000; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 1.8rem; margin-bottom: 1.5rem; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.9); position: relative;
    }
    
    .badge { display: inline-block; padding: 0.25rem 0.65rem; font-size: 0.74rem; font-weight: 700; border-radius: 8px; }
    .badge-FAILURE { background: rgba(239, 68, 68, 0.18); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-SUCCESS { background: rgba(16, 185, 129, 0.18); color: #86efac; border: 1px solid rgba(16, 185, 129, 0.4); }

    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    th { text-align: left; padding: 0.9rem 1.1rem; background: #050505; font-size: 0.72rem; text-transform: uppercase; color: #94a3b8; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-weight: 700; letter-spacing: 0.08em; }
    td { padding: 0.9rem 1.1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.04); font-size: 0.86rem; color: #cbd5e1; vertical-align: middle; }
    tr:hover td { background: rgba(99, 102, 241, 0.08); }

    .btn {
      display: inline-flex; align-items: center; gap: 6px; padding: 0.55rem 1.1rem;
      background: linear-gradient(135deg, #4f46e5, #6366f1); color: #fff; text-decoration: none;
      border-radius: 10px; font-size: 0.82rem; font-weight: 700; border: none; cursor: pointer;
      box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); transition: all 0.2s ease;
    }
    .btn:hover { background: linear-gradient(135deg, #4338ca, #4f46e5); box-shadow: 0 0 30px rgba(99, 102, 241, 0.7); transform: translateY(-1px); }
    
    .btn-secondary {
      background: rgba(255, 255, 255, 0.08); color: #e2e8f0; border: 1px solid rgba(255, 255, 255, 0.15); box-shadow: none;
    }
    .btn-secondary:hover { background: rgba(255, 255, 255, 0.14); border-color: rgba(255, 255, 255, 0.3); transform: translateY(-1px); }

    .console-box {
      background: #03060d; color: #e2e8f0; padding: 1.4rem; border-radius: 14px;
      font-family: 'JetBrains Mono', monospace; font-size: 0.84rem; line-height: 1.65;
      white-space: pre-wrap; max-height: 600px; overflow-y: auto; border: 1px solid rgba(99, 102, 241, 0.35);
      box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.9);
    }
  </style>
</head>
<body>
  <div class="aurora-container">
    <div class="aurora-orb aurora-1"></div>
    <div class="aurora-orb aurora-2"></div>
  </div>
  <div class="bg-grid"></div>
  <div id="mouse-spotlight"></div>

  <div class="app-wrapper">
    <div class="topbar">
      <div class="logo-area">
        <div class="logo-img">⚙️</div>
        <div>
          <div class="logo-title">Jenkins Automation Server</div>
          <div class="logo-sub">Enterprise DevOps CI/CD Engine</div>
        </div>
      </div>
      <div style="font-size: 0.85rem; color: #cbd5e1;">
        User: <strong style="color: #fff;">admin</strong> | <a href="http://localhost:8501" style="color: #38bdf8; text-decoration: none; font-weight: 700; background: rgba(6,182,212,0.12); padding: 5px 12px; border-radius: 8px; border: 1px solid rgba(6,182,212,0.3);">⚡ Back to AI Dashboard</a>
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
            <li><a href="/job/{{ pipeline_name }}/build" style="color: #4ade80;">▶ Build Now</a></li>
            <li><a href="/job/{{ pipeline_name }}/lastBuild/console">💻 Console Output</a></li>
            <li><a href="/job/{{ pipeline_name }}/lastBuild">🔍 Last Build Info</a></li>
          {% endif %}
          <li><a href="http://localhost:8501" style="color: #38bdf8;">🤖 AI Self-Healing Center</a></li>
        </ul>
      </div>

      <div class="content">
        {{ body_content | safe }}
      </div>
    </div>
  </div>

  <script>
    document.addEventListener('mousemove', (e) => {
      document.documentElement.style.setProperty('--mouse-x', `${e.clientX}px`);
      document.documentElement.style.setProperty('--mouse-y', `${e.clientY}px`);
    });
  </script>
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
          <td><span style="font-size: 1.1rem;">🔴</span></td>
          <td><a href="/job/{name}" style="color: #38bdf8; font-weight: 700; font-family: 'JetBrains Mono'; text-decoration: none;">{name}</a></td>
          <td>{info['description']}</td>
          <td><span class="badge badge-FAILURE">Build #5 Failed</span></td>
          <td>
            <div style="display: flex; gap: 8px;">
              <a href="/job/{name}/build" class="btn" style="padding: 0.35rem 0.75rem; font-size: 0.76rem;">▶ Build Now</a>
              <a href="/job/{name}/lastBuild/console" class="btn btn-secondary" style="padding: 0.35rem 0.75rem; font-size: 0.76rem;">💻 Console</a>
            </div>
          </td>
        </tr>
        """

    content = f"""
    <div class="card">
      <h2 style="font-size: 1.3rem; font-weight: 700; margin-bottom: 0.5rem; color: #fff;">Pipeline Dashboard</h2>
      <p style="color: #94a3b8; font-size: 0.88rem; margin-bottom: 1.2rem;">Monitored Jenkins pipelines managed by the Autonomous AI Agent.</p>
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
          <td><a href="/job/{pipeline_name}/{i}" style="color: #38bdf8; font-weight: 700; font-family: 'JetBrains Mono';">#{i}</a></td>
          <td><span class="badge badge-{status}">{status}</span></td>
          <td>{datetime.now().strftime("%Y-%m-%d %H:%M")}</td>
          <td>{(i*23)+12}s</td>
          <td><a href="/job/{pipeline_name}/{i}/console" style="color: #38bdf8; font-weight: 600;">View Console</a></td>
        </tr>
        """

    content = f"""
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem;">
        <div>
          <h1 style="font-size: 1.4rem; font-weight: 700; color: #fff;">Pipeline: {pipeline_name}</h1>
          <p style="color: #94a3b8; font-size: 0.88rem; margin-top: 4px;">{info['description']}</p>
        </div>
        <div style="display: flex; gap: 8px;">
          <a href="/job/{pipeline_name}/build" class="btn">▶ Trigger Build</a>
          <a href="/job/{pipeline_name}/lastBuild/console" class="btn btn-secondary">💻 Last Console</a>
        </div>
      </div>

      <div style="background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem; font-size: 0.85rem; color: #a5b4fc;">
        ⚡ <strong>Autonomous AI Remediation Active:</strong> Monitored by AI-Powered Jenkins Analyzer with automatic root cause detection and self-healing.
      </div>

      <h3 style="font-size: 1.05rem; font-weight: 700; color: #fff; margin-bottom: 0.8rem;">Build History</h3>
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
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem;">
        <div>
          <h1 style="font-size: 1.4rem; font-weight: 700; color: #fff;">{pipeline_name} #{build_number}</h1>
          <div style="margin-top: 6px;">
            <span class="badge badge-FAILURE">FAILURE</span>
            <span style="font-size: 0.85rem; color: #94a3b8; margin-left: 8px;">Duration: 74s · Completed {datetime.now().strftime("%H:%M:%S")}</span>
          </div>
        </div>
        <a href="/job/{pipeline_name}/{build_number}/console" class="btn">💻 View Console Output</a>
      </div>

      <h3 style="font-size: 1.05rem; font-weight: 700; color: #fff; margin-bottom: 0.8rem;">Pipeline Stages</h3>
      <div style="display: flex; gap: 10px; margin-bottom: 1.5rem;">
        <div style="flex: 1; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); padding: 0.9rem; border-radius: 12px; text-align: center;">
          <div style="font-size: 0.75rem; color: #86efac; font-weight: 700;">CHECKOUT</div>
          <div style="font-weight: 700; color: #4ade80; margin-top: 2px;">SUCCESS</div>
        </div>
        <div style="flex: 1; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); padding: 0.9rem; border-radius: 12px; text-align: center;">
          <div style="font-size: 0.75rem; color: #86efac; font-weight: 700;">BUILD</div>
          <div style="font-weight: 700; color: #4ade80; margin-top: 2px;">SUCCESS</div>
        </div>
        <div style="flex: 1; background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); padding: 0.9rem; border-radius: 12px; text-align: center;">
          <div style="font-size: 0.75rem; color: #fca5a5; font-weight: 700;">TEST</div>
          <div style="font-weight: 700; color: #f87171; margin-top: 2px;">FAILED</div>
        </div>
        <div style="flex: 1; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); padding: 0.9rem; border-radius: 12px; text-align: center;">
          <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700;">DEPLOY</div>
          <div style="font-weight: 700; color: #64748b; margin-top: 2px;">ABORTED</div>
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
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem;">
        <div>
          <h1 style="font-size: 1.3rem; font-weight: 700; color: #fff;">Console Output: {pipeline_name} #{build_number}</h1>
          <span class="badge badge-FAILURE" style="margin-top: 4px;">Finished: FAILURE</span>
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
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)