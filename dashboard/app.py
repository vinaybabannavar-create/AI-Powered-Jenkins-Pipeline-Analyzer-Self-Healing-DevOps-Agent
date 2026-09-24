import os
import sys
import argparse
import uvicorn

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from api import app

def main():
    parser = argparse.ArgumentParser(description="AI DevOps Agent Production Server")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8501)), help="Port to listen on")
    parser.add_argument("--server.port", dest="server_port", type=int, default=None, help="Streamlit backwards compat port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface")
    parser.add_argument("--server.address", dest="server_address", type=str, default=None, help="Streamlit backwards compat address")
    parser.add_argument("--server.headless", dest="server_headless", type=str, default=None, help="Streamlit backwards compat")

    args, _ = parser.parse_known_args()
    port = args.server_port or args.port
    host = args.server_address or args.host

    print(f"\n=======================================================")
    print(f"  [AI] DevOps Production Agent Running on FastAPI & React")
    print(f"  URL: http://localhost:{port}")
    print(f"=======================================================\n")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()