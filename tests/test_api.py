import pytest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from api import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"

def test_pipelines_endpoint():
    response = client.get("/api/pipelines")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

def test_analytics_endpoint():
    response = client.get("/api/analysis/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "mttr" in data
    assert "failure_distribution" in data

def test_settings_endpoint():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "jenkins_url" in data
    assert "demo_mode" in data

def test_actions_endpoint():
    response = client.get("/api/actions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
