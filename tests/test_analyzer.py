import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from analyzer import regex_classify, analyze_log

def test_regex_flaky_test():
    log = "Build failed on first run. Flaky test detected: test_user_checkout randomly fail. Passed on second attempt retry."
    cat, conf = regex_classify(log)
    assert cat == "Flaky Test"
    assert conf in ["High", "Medium"]

def test_regex_dependency_issue():
    log = "Traceback: ModuleNotFoundError: No module named 'requests'. pip install failed with requirements error."
    cat, conf = regex_classify(log)
    assert cat == "Dependency Issue"
    assert conf in ["High", "Medium"]

def test_regex_infrastructure_issue():
    log = "Fatal error: Out of memory. OOMKilled by Linux kernel. No space left on device."
    cat, conf = regex_classify(log)
    assert cat == "Infrastructure Issue"
    assert conf in ["High", "Medium"]

def test_regex_code_defect():
    log = "Traceback (most recent call last):\n  File 'app.py', line 45, in test_calc\n    assert a == b\nAssertionError: Values do not match. Exit code 1."
    cat, conf = regex_classify(log)
    assert cat == "Code Defect"
    assert conf in ["High", "Medium"]

def test_regex_config_error():
    log = "Jenkinsfile syntax error: Invalid pipeline config. Missing environment variable DATABASE_URL."
    cat, conf = regex_classify(log)
    assert cat == "Configuration Error"
    assert conf in ["High", "Medium"]

def test_regex_timeout():
    log = "Execution aborted: Build timed out after 15 minutes. Stage test deadline exceeded."
    cat, conf = regex_classify(log)
    assert cat == "Timeout"
    assert conf in ["High", "Medium"]

def test_analyze_log_structure():
    log = "ModuleNotFoundError: No module named 'flask'"
    result = analyze_log(log, pipeline_name="docker-image-build")
    assert result["type"] == "Dependency Issue"
    assert "reason" in result
    assert "fix" in result
    assert result["pipeline"] == "docker-image-build"
