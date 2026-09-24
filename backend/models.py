from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), default="DevOps Engineer")
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    pipelines = relationship("Pipeline", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("AnalysisRecord", back_populates="user", cascade="all, delete-orphan")
    actions = relationship("HealingAction", back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Jenkins config
    jenkins_url = Column(String(500), default="http://localhost:5000")
    jenkins_user = Column(String(255), default="admin")
    jenkins_token_enc = Column(Text, nullable=True)  # Fernet encrypted
    demo_mode = Column(Boolean, default=True)

    # GitHub config
    github_token_enc = Column(Text, nullable=True)  # Fernet encrypted
    github_repo = Column(String(255), nullable=True)  # "owner/repo"

    # Jira config
    jira_url = Column(String(500), nullable=True)     # "https://company.atlassian.net"
    jira_email = Column(String(255), nullable=True)
    jira_token_enc = Column(Text, nullable=True)   # Fernet encrypted
    jira_project_key = Column(String(50), default="DEVOPS")

    # Automation config
    auto_heal_enabled = Column(Boolean, default=True)
    scan_interval_minutes = Column(Integer, default=5)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="settings")


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(50), default="UNKNOWN")  # SUCCESS, FAILURE, UNSTABLE
    last_build = Column(Integer, default=1)
    duration_sec = Column(Float, default=0.0)
    tests_pass = Column(Integer, default=0)
    tests_fail = Column(Integer, default=0)
    last_failure_type = Column(String(100), nullable=True)
    last_action = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="pipelines")


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pipeline_name = Column(String(255), index=True, nullable=False)
    build_number = Column(Integer, default=1)
    failure_type = Column(String(100), nullable=False)
    category = Column(String(100), default="Execution")
    confidence = Column(String(50), default="Medium")
    reason = Column(Text, nullable=True)
    fix = Column(Text, nullable=True)
    source = Column(String(50), default="regex")  # regex or llm
    raw_log = Column(Text, nullable=True)
    mttr_before = Column(Float, default=15.0)
    mttr_after = Column(Float, default=4.5)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="analyses")
    actions = relationship("HealingAction", back_populates="analysis", cascade="all, delete-orphan")


class HealingAction(Base):
    __tablename__ = "healing_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("analysis_records.id"), nullable=True)
    pipeline_name = Column(String(255), nullable=False)
    action_type = Column(String(100), nullable=False)  # Retry, PullRequest, JiraTicket, Alert, Restart
    description = Column(Text, nullable=False)
    target = Column(String(255), nullable=True)
    status = Column(String(50), default="EXECUTED")  # EXECUTED, FAILED, PENDING, SIMULATED
    external_url = Column(String(1000), nullable=True)  # Link to real Jira, GitHub PR, or Jenkins build
    external_id = Column(String(255), nullable=True)   # Jira Key, PR #, or Jenkins Queue ID
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="actions")
    analysis = relationship("AnalysisRecord", back_populates="actions")
