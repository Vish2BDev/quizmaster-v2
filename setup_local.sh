#!/bin/bash

echo "🚀 Setting up Quiz Master V2 locally..."

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.8+ is required but not installed"
    exit 1
fi

# Check if Node.js 16+ is installed  
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 16+ is required but not installed"
    exit 1
fi

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is required but not installed"
    echo "Install with: brew install redis (macOS) or sudo apt install redis (Ubuntu)"
    exit 1
fi

echo "✅ All prerequisites found"

# Setup Backend
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Backend dependencies installed"

# Setup Frontend  
echo "🎨 Setting up frontend..."
cd ../frontend
npm install
echo "✅ Frontend dependencies installed"

# Start services
echo "🚀 Starting services..."

# Start Redis in background
redis-server --daemonize yes

# Start Flask backend
cd ../backend
source venv/bin/activate
python app.py &
FLASK_PID=$!

# Start Celery worker
python run_celery.py &
CELERY_PID=$!

# Start Celery beat
python run_celery_beat.py &
BEAT_PID=$!

# Start Vue frontend
cd ../frontend
npm run serve &
VUE_PID=$!

echo "🎉 Quiz Master V2 is starting up!"
echo "📍 Frontend: http://localhost:3000"  
echo "📍 Backend API: http://localhost:5000"
echo "👤 Default admin: admin/admin123"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $FLASK_PID $CELERY_PID $BEAT_PID $VUE_PID 2>/dev/null; exit" INT
wait 