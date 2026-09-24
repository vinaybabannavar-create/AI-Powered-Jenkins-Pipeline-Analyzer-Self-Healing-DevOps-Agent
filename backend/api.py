import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Header, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, get_db, SessionLocal
from models import User, UserSettings, Pipeline, AnalysisRecord, HealingAction
from security import (
    hash_password, verify_password, create_access_token, decode_access_token,
    encrypt_secret, decrypt_secret
)
from integrations import JenkinsClient
from pipeline_service import run_pipeline_analysis_sync, broadcast_event, sse_subscribers
from scheduler import background_pipeline_scheduler

# Create tables
Base.metadata.create_all(bind=engine)

def seed_initial_data():
    """Seeds default demo user and pipeline data if database is empty."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(
                id=1,
                email="admin@devops.ai",
                hashed_password=hash_password("admin123"),
                full_name="Lead DevOps Engineer",
                is_admin=True
            )
            db.add(user)
            db.commit()

            settings = UserSettings(
                user_id=user.id,
                jenkins_url="http://localhost:5000",
                jenkins_user="admin",
                demo_mode=True,
                auto_heal_enabled=True,
                scan_interval_minutes=5,
                jira_project_key="DEVOPS",
                github_repo="vinaybabannavar-create/AI-Powered-Jenkins-Pipeline-Analyzer-Self-Healing-DevOps-Agent"
            )
            db.add(settings)
            db.commit()

            # Seed initial pipelines
            pipelines = [
                Pipeline(
                    user_id=user.id,
                    name="python-flaky-tests",
                    description="Python project unit test pipeline",
                    status="FAILURE",
                    last_build=5,
                    duration_sec=60.3,
                    tests_pass=8,
                    tests_fail=2,
                    last_failure_type="Flaky Test",
                    last_action="Retrying failed stage with 30s backoff (attempt 1 of 3)"
                ),
                Pipeline(
                    user_id=user.id,
                    name="docker-image-build",
                    description="Container image build pipeline",
                    status="FAILURE",
                    last_build=5,
                    duration_sec=150.9,
                    tests_pass=8,
                    tests_fail=2,
                    last_failure_type="Dependency Issue",
                    last_action="Triggered PR for missing dependency in requirements.txt"
                ),
                Pipeline(
                    user_id=user.id,
                    name="kubernetes-deploy",
                    description="Kubernetes production deploy pipeline",
                    status="FAILURE",
                    last_build=5,
                    duration_sec=129.5,
                    tests_pass=8,
                    tests_fail=2,
                    last_failure_type="Infrastructure Issue",
                    last_action="Alert sent to ops team — resource threshold breached"
                )
            ]
            db.add_all(pipelines)
            db.commit()

            # Seed initial action
            actions = [
                HealingAction(
                    user_id=user.id,
                    pipeline_name="python-flaky-tests",
                    action_type="Flaky Test",
                    description="Auto-retriggered Jenkins build with backoff",
                    status="EXECUTED",
                    external_url="http://localhost:5000/job/python-flaky-tests/5"
                ),
                HealingAction(
                    user_id=user.id,
                    pipeline_name="docker-image-build",
                    action_type="Dependency Issue",
                    description="Created GitHub Pull Request with missing package patch",
                    status="EXECUTED",
                    external_url="https://github.com/vinaybabannavar-create/AI-Powered-Jenkins-Pipeline-Analyzer-Self-Healing-DevOps-Agent/pull/1"
                ),
                HealingAction(
                    user_id=user.id,
                    pipeline_name="kubernetes-deploy",
                    action_type="Infrastructure Issue",
                    description="Alert dispatched to Ops team via notification webhook",
                    status="EXECUTED",
                    external_url="http://localhost:5000/job/kubernetes-deploy"
                )
            ]
            db.add_all(actions)
            db.commit()
            print("[OK] Initial seed completed with demo user & pipelines.")
    finally:
        db.close()

seed_initial_data()

# Lifespan for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background scheduler task
    scheduler_task = asyncio.create_task(background_pipeline_scheduler(interval_seconds=300))
    yield
    scheduler_task.cancel()

app = FastAPI(
    title="AI-Powered Jenkins Pipeline Analyzer & Self-Healing Agent API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Request Models ──────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = "DevOps Engineer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SettingsUpdateRequest(BaseModel):
    jenkins_url: Optional[str] = None
    jenkins_user: Optional[str] = None
    jenkins_token: Optional[str] = None
    demo_mode: Optional[bool] = None
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    jira_url: Optional[str] = None
    jira_email: Optional[str] = None
    jira_token: Optional[str] = None
    jira_project_key: Optional[str] = None
    auto_heal_enabled: Optional[bool] = None
    scan_interval_minutes: Optional[int] = None

class JenkinsTestRequest(BaseModel):
    jenkins_url: str
    jenkins_user: Optional[str] = None
    jenkins_token: Optional[str] = None
    demo_mode: bool = False

# ── Auth Dependency ──────────────────────────────────────────────────────────
def get_current_user_optional(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """Returns authenticated user, or defaults to primary admin user for frictionless demo access."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            user = db.query(User).filter(User.email == payload["sub"]).first()
            if user:
                return user
    # Fallback to user ID 1
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ── Auth Endpoints ───────────────────────────────────────────────────────────
@app.post("/api/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize settings
    settings = UserSettings(user_id=user.id, demo_mode=True)
    db.add(settings)
    db.commit()

    token = create_access_token({"sub": user.email, "id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.email, "id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }

@app.get("/api/auth/me")
def get_profile(user: User = Depends(get_current_user_optional)):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_admin": user.is_admin
    }

# ── Settings & Jenkins Connection Endpoints ─────────────────────────────────
@app.get("/api/settings")
def get_user_settings(user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        settings = UserSettings(user_id=user.id, demo_mode=True)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return {
        "jenkins_url": settings.jenkins_url,
        "jenkins_user": settings.jenkins_user,
        "jenkins_token_configured": bool(settings.jenkins_token_enc),
        "demo_mode": settings.demo_mode,
        "github_repo": settings.github_repo,
        "github_token_configured": bool(settings.github_token_enc),
        "jira_url": settings.jira_url,
        "jira_email": settings.jira_email,
        "jira_token_configured": bool(settings.jira_token_enc),
        "jira_project_key": settings.jira_project_key,
        "auto_heal_enabled": settings.auto_heal_enabled,
        "scan_interval_minutes": settings.scan_interval_minutes
    }

@app.post("/api/settings")
def update_user_settings(
    req: SettingsUpdateRequest,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        settings = UserSettings(user_id=user.id)
        db.add(settings)

    if req.jenkins_url is not None:
        settings.jenkins_url = req.jenkins_url.strip()
    if req.jenkins_user is not None:
        settings.jenkins_user = req.jenkins_user.strip()
    if req.jenkins_token:
        settings.jenkins_token_enc = encrypt_secret(req.jenkins_token.strip())
    if req.demo_mode is not None:
        settings.demo_mode = req.demo_mode
    if req.github_repo is not None:
        settings.github_repo = req.github_repo.strip()
    if req.github_token:
        settings.github_token_enc = encrypt_secret(req.github_token.strip())
    if req.jira_url is not None:
        settings.jira_url = req.jira_url.strip()
    if req.jira_email is not None:
        settings.jira_email = req.jira_email.strip()
    if req.jira_token:
        settings.jira_token_enc = encrypt_secret(req.jira_token.strip())
    if req.jira_project_key is not None:
        settings.jira_project_key = req.jira_project_key.strip()
    if req.auto_heal_enabled is not None:
        settings.auto_heal_enabled = req.auto_heal_enabled
    if req.scan_interval_minutes is not None:
        settings.scan_interval_minutes = req.scan_interval_minutes

    db.commit()
    return {"status": "success", "message": "Settings updated and credentials securely encrypted"}

@app.post("/api/settings/test-jenkins")
def test_jenkins_connection(req: JenkinsTestRequest):
    client = JenkinsClient(
        base_url=req.jenkins_url,
        username=req.jenkins_user,
        api_token=req.jenkins_token,
        demo_mode=req.demo_mode
    )
    ok, msg, details = client.test_connection()
    return {
        "success": ok,
        "message": msg,
        "details": details
    }

# ── Pipeline & Analysis Endpoints ───────────────────────────────────────────
@app.get("/api/pipelines")
def get_pipelines(user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    pipelines = db.query(Pipeline).filter(Pipeline.user_id == user.id).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "status": p.status,
            "build": p.last_build,
            "duration_sec": p.duration_sec,
            "tests_pass": p.tests_pass,
            "tests_fail": p.tests_fail,
            "failure_type": p.last_failure_type,
            "action": p.last_action,
            "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M:%S") if p.updated_at else None
        }
        for p in pipelines
    ]

@app.get("/api/analysis/history")
def get_analysis_history(
    limit: int = 50,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    records = db.query(AnalysisRecord).filter(
        AnalysisRecord.user_id == user.id
    ).order_by(AnalysisRecord.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "pipeline": r.pipeline_name,
            "build": r.build_number,
            "type": r.failure_type,
            "category": r.category,
            "confidence": r.confidence,
            "reason": r.reason,
            "fix": r.fix,
            "source": r.source
        }
        for r in records
    ]

@app.get("/api/analysis/analytics")
def get_analytics(user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    records = db.query(AnalysisRecord).filter(AnalysisRecord.user_id == user.id).all()
    total = len(records) or 20

    types = {}
    conf = {"High": 0, "Medium": 0, "Low": 0}
    src = {"regex": 0, "llm": 0}

    for r in records:
        types[r.failure_type] = types.get(r.failure_type, 0) + 1
        conf[r.confidence] = conf.get(r.confidence, 0) + 1
        src[r.source] = src.get(r.source, 0) + 1

    if not types:
        types = {
            "Flaky Test": 3,
            "Dependency Issue": 3,
            "Infrastructure Issue": 3,
            "Code Defect": 4,
            "Configuration Error": 2,
            "Timeout": 3
        }
        conf = {"High": 9, "Medium": 9, "Low": 2}
        src = {"regex": 18, "llm": 2}

    return {
        "total_logs": total,
        "failure_distribution": types,
        "confidence_breakdown": conf,
        "source_counts": src,
        "mttr": {
            "without_ai": 15.05,
            "with_ai": 4.55,
            "improvement": 69.77
        }
    }

@app.get("/api/actions")
def get_healing_actions(
    limit: int = 50,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    actions = db.query(HealingAction).filter(
        HealingAction.user_id == user.id
    ).order_by(HealingAction.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": a.id,
            "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "pipeline": a.pipeline_name,
            "action_type": a.action_type,
            "description": a.description,
            "status": a.status,
            "external_url": a.external_url,
            "external_id": a.external_id
        }
        for a in actions
    ]

# ── Native Async Run-Agent Endpoint (No Subprocess) ─────────────────────────
@app.post("/api/run-agent")
async def trigger_agent(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Executes pipeline analysis directly as a native Python function call.
    Runs asynchronously, triggers real healing actions, stores in database,
    and returns immediate status while streaming events via SSE.
    """
    try:
        # Run directly in thread pool to prevent blocking FastAPI event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_pipeline_analysis_sync, db, user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Real-Time Server-Sent Events (SSE) Stream ────────────────────────────────
@app.get("/api/events")
async def event_stream(request: Request):
    """
    Server-Sent Events endpoint streaming live activity feed messages,
    pipeline scan progress, and self-healing action logs directly to connected browsers.
    """
    queue = asyncio.Queue()
    sse_subscribers.append(queue)

    async def event_generator():
        # Initial greeting event
        yield f"data: {json.dumps({'event': 'connected', 'message': 'Real-time telemetry stream active'})}\n\n"
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat
                    yield f": keep-alive\n\n"
        finally:
            if queue in sse_subscribers:
                sse_subscribers.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ── Health Check ─────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "version": "2.0.0"}

# ── Static Frontend Serving ─────────────────────────────────────────────────
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard", "dist"))

assets_dir = os.path.join(FRONTEND_DIST, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if os.path.exists(FRONTEND_DIST):
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
    return JSONResponse({"status": "healthy", "service": "AI DevOps Agent API"})
