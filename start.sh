#!/bin/bash

# Start the Mock Jenkins Flask server in the background
echo "Starting Mock Jenkins Server..."
python backend/mock_jenkins.py &

# Wait for the Flask server to initialize
sleep 5

# Start the Jenkins Agent to fetch initial data and run analysis
echo "Running Jenkins Agent..."
python backend/jenkins_agent.py &

# Start the Streamlit Dashboard
echo "Starting Streamlit Dashboard..."
# Render dynamically assigns the PORT environment variable
# If PORT is not set (e.g. running locally), default to 8501
PORT=${PORT:-8501}

python -m streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0
