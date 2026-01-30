#!/bin/bash

echo "🚀 Starting AI Job Agent System..."
echo ""

# Check if n8n is running
if ! docker ps | grep -q n8n; then
    echo "📦 Starting n8n..."
    docker start n8n
    sleep 3
fi

# Start Flask API in background
echo "🔧 Starting Flask API (port 5000)..."
cd ~/projects/job-agent
source venv/bin/activate
python3 app.py &
API_PID=$!

# Wait a bit
sleep 2

# Start Dashboard in background
echo "📊 Starting Dashboard (port 5001)..."
python3 dashboard.py &
DASH_PID=$!

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Access your system:"
echo "   - Dashboard: http://127.0.0.1:5001"
echo "   - Flask API: http://127.0.0.1:5000"
echo "   - n8n: http://localhost:5678"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to press Ctrl+C
trap "kill $API_PID $DASH_PID; echo 'Stopped all services'; exit" INT
wait
