import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from integrations import JenkinsClient, GitHubClient, JiraClient

def test_jenkins_demo_mode():
    client = JenkinsClient(base_url="http://localhost:5000", demo_mode=True)
    ok, msg, details = client.test_connection()
    assert ok is True
    assert "Demo Mode" in msg

    jobs = client.get_jobs()
    assert len(jobs) >= 3

    success, tr_msg, url = client.trigger_build("python-flaky-tests")
    assert success is True
    assert url is not None

def test_github_client_fallback():
    client = GitHubClient(token=None, repo=None)
    ok, msg, url = client.open_pull_request_with_fix(
        file_path="requirements.txt",
        fix_content="requests>=2.31.0",
        branch_prefix="fix-dep-test",
        pr_title="fix: dependency update",
        pr_body="Auto fix"
    )
    assert ok is True
    assert "pull" in url

def test_jira_client_fallback():
    client = JiraClient()
    ok, msg, url, key = client.create_issue(
        summary="Test defect",
        description="Stack trace info"
    )
    assert ok is True
    assert key is not None
    assert "browse" in url
