import os
import sys

# Ensure backend directory is in sys.path for pytest discovery across all environments
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("GEMINI_API_KEY", "test-mock-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-ci")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
