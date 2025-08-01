<template>
  <div class="user-container">
    <div class="row g-0">
      <!-- Enhanced Sidebar -->
      <div class="col-md-3 user-sidebar">
        <div class="sidebar-content">
          <div class="user-header p-4">
            <div class="user-brand text-center">
              <div class="brand-icon mb-3">
                <i class="fas fa-graduation-cap text-white" style="font-size: 2.5rem;"></i>
              </div>
              <h4 class="text-white mb-1" style="font-family: var(--qm-font-heading);">Quiz Master</h4>
              <p class="text-white-50 small mb-0">Student Dashboard</p>
            </div>
          </div>
            
          <nav class="user-nav p-3">
            <ul class="nav flex-column">
              <!-- Main Navigation -->
              <li class="nav-section-title mb-2">
                <small class="text-white-50 text-uppercase fw-bold">Main</small>
              </li>
              <li class="nav-item mb-2">
                <router-link class="nav-link user-nav-link" to="/dashboard" exact-active-class="active">
                  <i class="fas fa-tachometer-alt me-3"></i>
                  <span>Dashboard Overview</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              <li class="nav-item mb-2">
                <router-link class="nav-link user-nav-link" to="/my-quizzes" active-class="active">
                  <i class="fas fa-play me-3"></i>
                  <span>My Quizzes</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              <li class="nav-item mb-2">
                <router-link class="nav-link user-nav-link" to="/leaderboard" active-class="active">
                  <i class="fas fa-trophy me-3"></i>
                  <span>Leaderboard</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              
              <!-- Performance -->
              <li class="nav-section-title mt-4 mb-2">
                <small class="text-white-50 text-uppercase fw-bold">Performance</small>
              </li>
              <li class="nav-item mb-1">
                <router-link class="nav-link user-nav-link" to="/my-stats" active-class="active">
                  <i class="fas fa-chart-line me-3"></i>
                  <span>My Stats</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              <li class="nav-item mb-1">
                <router-link class="nav-link user-nav-link" to="/achievements" active-class="active">
                  <i class="fas fa-medal me-3"></i>
                  <span>Achievements</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              
              <!-- Quick Actions -->
              <li class="nav-section-title mt-4 mb-2">
                <small class="text-white-50 text-uppercase fw-bold">Quick Actions</small>
              </li>
              <li class="nav-item mb-1">
                <button class="nav-link user-nav-link btn btn-link text-start w-100" @click="exportData">
                  <i class="fas fa-download me-3"></i>
                  <span>Export My Data</span>
                </button>
              </li>
            </ul>
          </nav>
          
          <!-- User Profile Section -->
          <div class="user-profile-section mt-auto p-3 border-top border-white-25">
            <div class="user-info mb-3">
              <div class="d-flex align-items-center mb-2">
                <div class="user-avatar me-3">
                  <i class="fas fa-user text-white" style="font-size: 1.5rem;"></i>
                </div>
                <div class="user-details">
                  <div class="text-white fw-bold">{{ currentUser?.username || 'Student' }}</div>
                  <div class="text-white-50 small">
                    <i class="fas fa-graduation-cap me-1"></i>Student
                  </div>
                </div>
              </div>
            </div>
            
            <div class="user-actions">
              <button class="btn btn-outline-light btn-sm w-100 mb-2" @click="handleLogout">
                <i class="fas fa-sign-out-alt me-2"></i>
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Main Content Area -->
      <div class="col-md-9 user-main">
        <!-- Top Navigation Bar -->
        <div class="top-navbar bg-white border-bottom p-3">
          <div class="d-flex justify-content-between align-items-center">
            <!-- Breadcrumb Navigation -->
            <nav aria-label="breadcrumb">
              <ol class="breadcrumb mb-0">
                <li class="breadcrumb-item">
                  <router-link to="/" class="text-decoration-none">
                    <i class="fas fa-home me-1"></i>Home
                  </router-link>
                </li>
                <li v-for="crumb in breadcrumbs" :key="crumb.text" class="breadcrumb-item">
                  <router-link v-if="crumb.to" :to="crumb.to" class="text-decoration-none">
                    <i :class="crumb.icon + ' me-1'" v-if="crumb.icon"></i>
                    {{ crumb.text }}
                  </router-link>
                  <span v-else>
                    <i :class="crumb.icon + ' me-1'" v-if="crumb.icon"></i>
                    {{ crumb.text }}
                  </span>
                </li>
              </ol>
            </nav>
            
            <!-- Profile Dropdown -->
            <div class="profile-dropdown">
              <div class="d-flex align-items-center">
                <div class="welcome-message me-3">
                  <span class="text-muted small">Welcome back,</span>
                  <span class="fw-bold text-primary">{{ currentUser?.username }}!</span>
                </div>
                <div class="user-avatar-small">
                  <i class="fas fa-user-circle text-primary" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Content Header -->
        <div class="content-header p-4 bg-white border-bottom" v-if="pageTitle">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="text-primary mb-1" style="font-family: var(--qm-font-heading);">
                <i :class="pageIcon + ' me-2'" v-if="pageIcon"></i>{{ pageTitle }}
              </h2>
              <p class="text-muted mb-0" v-if="pageDescription">{{ pageDescription }}</p>
            </div>
            <div class="header-actions">
              <slot name="header-actions"></slot>
            </div>
          </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content p-4">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'UserLayout',
  emits: ['export-data'],
  props: {
    pageTitle: {
      type: String,
      default: 'Dashboard'
    },
    pageDescription: {
      type: String,
      default: ''
    },
    pageIcon: {
      type: String,
      default: 'fas fa-tachometer-alt'
    },
    breadcrumbs: {
      type: Array,
      default: () => []
    }
  },
  setup(props, { emit }) {
    const store = useStore()
    const router = useRouter()
    
    const currentUser = computed(() => store.getters.currentUser)
    
    const handleLogout = async () => {
      await store.dispatch('logout')
      router.push('/login')
    }
    
    const exportData = () => {
      // Emit event to parent component to show export tab
      emit('export-data')
    }
    
    return {
      currentUser,
      handleLogout,
      exportData
    }
  }
}
</script>

<style scoped>
.user-container {
  min-height: 100vh;
  background: var(--bg-soft);
}

/* Sidebar Styles */
.user-sidebar {
  background: linear-gradient(180deg, var(--primary) 0%, #1E40AF 100%);
  min-height: 100vh;
  box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

.sidebar-content {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.user-header {
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.brand-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
}

.user-nav-link {
  color: rgba(255,255,255,0.8);
  border-radius: var(--qm-border-radius);
  padding: 12px 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  border: none;
  background: none;
  text-decoration: none;
  display: flex;
  align-items: center;
}

.user-nav-link:hover {
  color: white;
  background: rgba(255,255,255,0.1);
  transform: translateX(5px);
}

.user-nav-link.active {
  color: white;
  background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.nav-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.user-nav-link.active .nav-indicator {
  transform: scaleY(1);
}

.nav-section-title {
  padding: 0 16px;
}

/* User Profile Section */
.user-profile-section {
  border-top: 1px solid rgba(255,255,255,0.1) !important;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: rgba(255,255,255,0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-actions .btn {
  transition: all 0.3s ease;
}

.user-actions .btn:hover {
  background: rgba(255,255,255,0.2);
  border-color: rgba(255,255,255,0.3);
  transform: translateY(-1px);
}

/* Main Content */
.user-main {
  background: var(--bg-soft);
}

.top-navbar {
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.breadcrumb {
  background: none;
  padding: 0;
}

.breadcrumb-item {
  font-size: 0.9rem;
}

.breadcrumb-item.active {
  color: var(--text-subtle);
}

.breadcrumb-item + .breadcrumb-item::before {
  content: ">";
  color: var(--text-subtle);
}

.content-header {
  border-bottom: 1px solid #dee2e6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.main-content {
  background: var(--bg-soft);
}

.welcome-message {
  text-align: right;
}

.user-avatar-small {
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-avatar-small:hover {
  transform: scale(1.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .user-sidebar {
    min-height: auto;
    position: relative;
  }
  
  .sidebar-content {
    position: relative;
    height: auto;
  }
  
  .content-header {
    padding: 1rem !important;
  }
  
  .main-content {
    padding: 1rem !important;
  }
  
  .welcome-message {
    display: none;
  }
}
</style>