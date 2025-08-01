@echo off
echo 🚀 Setting up Quiz Master V2 locally...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.8+ is required but not installed
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 16+ is required but not installed
    exit /b 1
)

echo ✅ Prerequisites found

REM Setup Backend
echo 📦 Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo ✅ Backend dependencies installed

REM Setup Frontend
echo 🎨 Setting up frontend...  
cd ..\frontend
npm install
echo ✅ Frontend dependencies installed

echo 🎉 Setup complete!
echo 📖 See README.md for starting instructions
pause 