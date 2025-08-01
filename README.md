# 🎓 Quiz Master V2 - Complete Academic Quiz Platform

A full-stack quiz management system built with **Vue 3**, **Flask**, **SQLite**, and **Celery** featuring real-time interactions, performance analytics, and emotional design patterns.

## ✨ Key Features

### 🎯 **Emotional Design System**
- **Curiosity**: Progressive disclosure, hover reveals, surprise elements
- **Belonging**: Community stats, welcoming messages, social proof  
- **Redemption**: Encouraging retries, growth visualization, second chances

### 🎨 **10/10 Visual Identity**
- Orange (#ff9a56) → Teal (#4ecdc4) gradient branding
- Typography: Merriweather + Inter + Nunito
- Micro-animations and celebratory feedback
- WCAG AA accessibility compliance

### 🚀 **Technical Excellence**
- **Frontend**: Vue 3 + Bootstrap 5 + Chart.js
- **Backend**: Flask + SQLAlchemy + SQLite  
- **Background Jobs**: Celery + Redis
- **Real-time**: WebSocket support for live updates

## 🏃‍♂️ **Quick Start**

### Prerequisites
- Python 3.8+
- Node.js 16+  
- Redis Server

### Automated Setup (Recommended)
```bash
# macOS/Linux
chmod +x setup_local.sh
./setup_local.sh

# Windows  
setup_local.bat
```

### Manual Setup
```bash
# 1. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Frontend Setup  
cd ../frontend
npm install

# 3. Start Services (4 terminals needed)
# Terminal 1: Redis
redis-server

# Terminal 2: Flask API
cd backend && python app.py

# Terminal 3: Celery Worker
cd backend && python run_celery.py

# Terminal 4: Celery Beat  
cd backend && python run_celery_beat.py

# Terminal 5: Vue Frontend
cd frontend && npm run serve
```

## 🌐 **Access Points**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000  
- **Admin Login**: admin / admin123

## 📊 **Features Showcase**

### For Students:
- **Intuitive Dashboard** with progress tracking
- **Real-time Quizzes** with timer and instant feedback
- **Performance Analytics** with interactive charts
- **Achievement System** with badges and celebrations

### For Administrators:
- **Content Management** (Subjects → Chapters → Quizzes → Questions)
- **User Analytics** with real-time activity feeds
- **Automated Reports** via email with beautiful HTML templates
- **System Monitoring** with health indicators

### For Developers:
- **Modular Architecture** with reusable Vue components
- **Design System** with consistent styling tokens
- **API-First Design** with comprehensive REST endpoints
- **Background Jobs** for scalable task processing

## 🎯 **Technical Highlights**

### Backend Architecture
- **Flask + SQLAlchemy**: RESTful API with ORM
- **JWT Authentication**: Secure token-based auth
- **Celery + Redis**: Background job processing
- **Email Integration**: SMTP + HTML templates
- **Caching**: Redis-powered performance optimization

### Frontend Architecture  
- **Vue 3 Composition API**: Modern reactive framework
- **Bootstrap 5**: Mobile-first responsive design
- **Chart.js**: Interactive data visualizations  
- **Vuex**: Centralized state management
- **Axios**: HTTP client with interceptors

### Design System
- **CSS Custom Properties**: Theme consistency
- **Component Library**: Reusable UI elements
- **Animation System**: Micro-interactions and celebrations
- **Accessibility**: Keyboard navigation, screen readers
- **Responsive**: Mobile-first with touch optimization

## 🔧 **Development Guide**

### Project Structure
```
quiz-master-v2/
├── backend/           # Flask API + Celery
├── frontend/          # Vue 3 application  
├── docs/             # Documentation
└── setup/            # Setup scripts
```

### Key Commands
```bash
# Backend Development
cd backend && python app.py              # Start Flask dev server
cd backend && python run_celery.py       # Start background worker
cd backend && python run_celery_beat.py  # Start task scheduler

# Frontend Development  
cd frontend && npm run serve              # Start Vue dev server
cd frontend && npm run build             # Build for production
cd frontend && npm run lint              # Lint code

# Database
# SQLite DB auto-created on first run at backend/quiz_master.db
```

## 📧 **Email Configuration**

Update `backend/.env` with your SMTP settings:
```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password  
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## 🎨 **Design System Usage**

The application includes a complete design system with:
- **Color Variables**: Primary gradients, semantic colors
- **Component Classes**: `.btn-qm-primary`, `.card-qm`, `.qm-progress`
- **Typography**: Consistent font hierarchy
- **Animations**: Micro-interactions and celebrations

## 🔒 **Security Features**

- **JWT Authentication**: Secure token-based sessions
- **Password Hashing**: Werkzeug secure password storage  
- **CORS Protection**: Configured cross-origin policies
- **Input Validation**: Server-side and client-side validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection

## 📱 **Mobile Experience**

- **Touch Optimized**: 44px minimum touch targets
- **Responsive Design**: Breakpoints for all screen sizes
- **Progressive Web App**: Installable with offline capabilities
- **Gesture Support**: Swipe navigation and interactions

## 🎯 **Academic Focus**

Built specifically for Modern Application Development II (MAD 2):
- **No Jinja Templates**: Pure Vue.js frontend
- **Component Architecture**: Modular, reusable design
- **State Management**: Centralized with Vuex
- **Real-time Features**: WebSocket integration
- **Background Processing**: Celery job queues
- **Email Integration**: SMTP with HTML templates

## 🚀 **Production Deployment**

See individual README files in `backend/` and `frontend/` directories for production deployment guides including:
- Environment configuration
- Database migration
- Process management (PM2, Supervisor)
- Web server setup (Nginx, Apache)
- SSL/TLS configuration

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow the coding standards in `.eslintrc.js` and PEP 8
4. Test thoroughly on both desktop and mobile
5. Submit pull request with detailed description

## 📄 **License**

Educational use for MAD 2 course. All rights reserved.

---

**🎉 Ready to experience the future of quiz platforms? Start with the quick setup guide above!** 