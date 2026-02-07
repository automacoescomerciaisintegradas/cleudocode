#!/bin/bash
export STREAMLIT_SERVER_HEADLESS=true
export PATH=$PATH:/root/.local/bin

echo "Killing old processes..."
pkill -f web_server.py
pkill -f streamlit

echo "Starting Web Server..."
nohup python3 web_server.py > web_server.log 2>&1 &
disown

echo "Starting Dashboard..."
nohup /root/.local/bin/streamlit run web/dashboard.py --server.address 0.0.0.0 --server.port 8501 --server.headless true > dashboard.log 2>&1 &
disown

echo "Services started! Check logs: web_server.log, dashboard.log"
sleep 2
