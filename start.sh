#!/bin/bash

# Exit on error
set -e

echo "--- 🚀 Starting Deployment Script ---"

# Start the Mock Jenkins Flask server in the background
echo "--- 🟢 Starting Mock Jenkins Server (Port 5000) ---"
python3 backend/mock_jenkins.py > flask_logs.txt 2>&1 &

# Wait for the Flask server to initialize
echo "--- ⏳ Waiting for Flask to warm up... ---"
sleep 7

# Start the Jenkins Agent to fetch initial data
echo "--- 🤖 Running Jenkins Agent Analysis ---"
python3 backend/jenkins_agent.py || echo "⚠️ Agent run had issues, but continuing to Dashboard..."

# Start the Modern Dashboard Server
echo "--- 📊 Starting Modern DevOps Dashboard on Port $PORT ---"
PORT=${PORT:-8501}

python3 dashboard/app.py --port $PORT --host 0.0.0.0

