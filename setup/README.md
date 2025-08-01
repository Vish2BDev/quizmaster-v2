# Quiz Master V2 - Setup Scripts

This directory contains setup and deployment scripts for the Quiz Master V2 project.

## Available Scripts

### Windows Scripts
- `setup_windows.bat` - Complete setup for Windows environment
- `install_dependencies.bat` - Install all dependencies
- `start_services.bat` - Start all required services

### Linux/Mac Scripts
- `setup_linux.sh` - Complete setup for Linux/Mac environment
- `install_dependencies.sh` - Install all dependencies
- `start_services.sh` - Start all required services

### Docker Scripts
- `docker-compose.yml` - Docker Compose configuration
- `build_docker.sh` - Build Docker images
- `deploy_docker.sh` - Deploy with Docker

## Quick Setup

### Windows
```bash
cd setup
setup_windows.bat
```

### Linux/Mac
```bash
cd setup
chmod +x setup_linux.sh
./setup_linux.sh
```

### Docker
```bash
cd setup
docker-compose up -d
```

## Manual Setup

If you prefer to set up manually:

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

3. **Database Setup**
   ```bash
   # Install Redis
   # Start Redis server
   redis-server
   ```

4. **Start Services**
   ```bash
   # Terminal 1: Backend
   cd backend
   python app.py
   
   # Terminal 2: Celery Worker
   cd backend
   python run_celery.py
   
   # Terminal 3: Frontend
   cd frontend
   npm run serve
   ``` 