<template>
  <div class="admin-container">
    <div class="row g-0">
      <!-- Enhanced Sidebar -->
      <div class="col-md-3 admin-sidebar">
        <div class="sidebar-content">
          <div class="admin-header p-4">
            <div class="admin-brand text-center">
              <div class="brand-icon mb-3">
                <i class="fas fa-graduation-cap text-white" style="font-size: 2.5rem;"></i>
              </div>
              <h4 class="text-white mb-1" style="font-family: var(--qm-font-heading);">Quiz Master</h4>
              <p class="text-white-50 small mb-0">Admin Dashboard</p>
            </div>
          </div>
            
          <nav class="admin-nav p-3">
            <ul class="nav flex-column">
              <!-- Main Navigation -->
              <li class="nav-section-title mb-2">
                <small class="text-white-50 text-uppercase fw-bold">Main</small>
              </li>
              <li class="nav-item mb-2">
                <router-link class="nav-link admin-nav-link" to="/admin" exact-active-class="active">
                  <i class="fas fa-tachometer-alt me-3"></i>
                  <span>Dashboard</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              <li class="nav-item mb-2">
                <router-link class="nav-link admin-nav-link" to="/admin/analytics" active-class="active">
                  <i class="fas fa-chart-line me-3"></i>
                  <span>Analytics</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              <li class="nav-item mb-2">
                <router-link class="nav-link admin-nav-link" to="/admin/real-time" active-class="active">
                  <i class="fas fa-satellite-dish me-3"></i>
                  <span>Real-Time Events</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              
              <!-- Content Management -->
              <li class="nav-section-title mt-4 mb-2">
                <small class="text-white-50 text-uppercase fw-bold">Content Management</small>
              </li>
              <li class="nav-item mb-1">
                <router-link class="nav-link admin-nav-link" to="/admin/subjects" active-class="active">
                  <i class="fas fa-book me-3"></i>
                  <span>Subjects</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              <li class="nav-item mb-1">
                <router-link class="nav-link admin-nav-link" to="/admin/chapters" active-class="active">
                  <i class="fas fa-bookmark me-3"></i>
                  <span>Chapters</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              <li class="nav-item mb-1">
                <router-link class="nav-link admin-nav-link" to="/admin/quizzes" active-class="active">
                  <i class="fas fa-question-circle me-3"></i>
                  <span>Quizzes</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              
              <!-- User Management -->
              <li class="nav-section-title mt-4 mb-2">
                <small class="text-white-50 text-uppercase fw-bold">Users</small>
              </li>
              <li class="nav-item mb-1">
                <router-link class="nav-link admin-nav-link" to="/admin/users" active-class="active">
                  <i class="fas fa-users me-3"></i>
                  <span>Manage Users</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              
              <!-- Background Tasks -->
              <li class="nav-section-title mt-4 mb-2">
                <small class="text-white-50 text-uppercase fw-bold">Automation</small>
              </li>
              <li class="nav-item mb-1">
                <router-link class="nav-link admin-nav-link" to="/admin/tasks" active-class="active">
                  <i class="fas fa-cogs me-3"></i>
                  <span>Background Tasks</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              <li class="nav-item mb-1">
                <router-link class="nav-link admin-nav-link" to="/admin/exports" active-class="active">
                  <i class="fas fa-download me-3"></i>
                  <span>Data Exports</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
              
              <!-- Quick Actions -->
              <li class="nav-section-title mt-4 mb-2">
                <small class="text-white-50 text-uppercase fw-bold">Quick Actions</small>
              </li>
              <li class="nav-item mb-1">
                <button class="nav-link admin-nav-link btn btn-link text-start w-100" @click="showCreateSubjectModal">
                  <i class="fas fa-plus me-3"></i>
                  <span>Add Subject</span>
                </button>
              </li>
              <li class="nav-item mb-1">
                <button class="nav-link admin-nav-link btn btn-link text-start w-100" @click="showCreateQuizModal">
                  <i class="fas fa-plus me-3"></i>
                  <span>Add Quiz</span>
                </button>
              </li>
            </ul>
          </nav>
          
          <!-- User Profile Section -->
          <div class="user-profile-section mt-auto p-3 border-top border-white-25">
            <div class="user-info mb-3">
              <div class="d-flex align-items-center mb-2">
                <div class="user-avatar me-3">
                  <i class="fas fa-user-shield text-white" style="font-size: 1.5rem;"></i>
                </div>
                <div class="user-details">
                  <div class="text-white fw-bold">{{ currentUser?.username || 'Admin' }}</div>
                  <div class="text-white-50 small">
                    <i class="fas fa-crown me-1"></i>Administrator
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
          
          <!-- Task History Panel -->
          <div class="task-history-panel p-3" v-if="taskHistory.length > 0">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h6 class="text-white mb-0">Recent Tasks</h6>
              <button class="btn btn-sm btn-outline-light" @click="toggleTaskHistory">
                <i :class="showTaskHistory ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>
            <div v-show="showTaskHistory" class="task-list">
              <div v-for="task in taskHistory.slice(0, 5)" :key="task.id" class="task-item mb-2 p-2 rounded">
                <div class="d-flex justify-content-between align-items-center">
                  <span class="text-white-75 small">{{ task.name }}</span>
                  <span :class="getTaskStatusClass(task.status)">
                    <i :class="getTaskStatusIcon(task.status)"></i>
                  </span>
                </div>
                <div class="text-white-50 small">{{ formatTaskTime(task.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Main Content Area -->
      <div class="col-md-9 admin-main">
        <div class="admin-content">
          <!-- Breadcrumb Navigation -->
          <div class="breadcrumb-section p-3 bg-white border-bottom">
            <nav aria-label="breadcrumb">
              <ol class="breadcrumb mb-0">
                <li class="breadcrumb-item">
                  <router-link to="/admin" class="text-decoration-none">
                    <i class="fas fa-home me-1"></i>Dashboard
                  </router-link>
                </li>
                <li v-for="(crumb, index) in breadcrumbs" :key="index" 
                    class="breadcrumb-item" 
                    :class="{ active: index === breadcrumbs.length - 1 }">
                  <router-link v-if="crumb.to && index !== breadcrumbs.length - 1" 
                               :to="crumb.to" 
                               class="text-decoration-none">
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
    
    <!-- Toast Container -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1055;">
      <div v-for="toast in toasts" :key="toast.id" 
           :class="['toast', 'show', `bg-${toast.type}`]" role="alert">
        <div class="toast-header">
          <i :class="getToastIcon(toast.type)" class="me-2"></i>
          <strong class="me-auto">{{ toast.title }}</strong>
          <button type="button" class="btn-close" @click="removeToast(toast.id)"></button>
        </div>
        <div class="toast-body text-white">
          {{ toast.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'

export default {
  name: 'AdminLayout',
  props: {
    pageTitle: {
      type: String,
      default: ''
    },
    pageDescription: {
      type: String,
      default: ''
    },
    pageIcon: {
      type: String,
      default: ''
    },
    breadcrumbs: {
      type: Array,
      default: () => []
    },
    currentSubject: {
      type: Object,
      default: null
    },
    currentChapter: {
      type: Object,
      default: null
    },
    currentQuiz: {
      type: Object,
      default: null
    }
  },
  emits: ['quick-add-subject'],
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()
    
    // Reactive data
    const taskHistory = ref([])
    const showTaskHistory = ref(true)
    const toasts = ref([])
    const toastIdCounter = ref(0)
    
    // Get current user from store
    const currentUser = computed(() => store.getters.currentUser)
    
    // Breadcrumb computation
    const breadcrumbs = computed(() => {
      const crumbs = []
      const path = route.path
      
      if (path.includes('/admin/subjects')) {
        crumbs.push({ text: 'Subjects', to: '/admin/subjects' })
        if (route.params.subjectId) {
          crumbs.push({ text: 'Subject Details', to: null })
        }
      } else if (path.includes('/admin/chapters')) {
        crumbs.push({ text: 'Chapters', to: '/admin/chapters' })
      } else if (path.includes('/admin/quizzes')) {
        crumbs.push({ text: 'Quizzes', to: '/admin/quizzes' })
      } else if (path.includes('/admin/users')) {
        crumbs.push({ text: 'Users', to: '/admin/users' })
      } else if (path.includes('/admin/analytics')) {
        crumbs.push({ text: 'Analytics', to: '/admin/analytics' })
      } else if (path.includes('/admin/real-time')) {
        crumbs.push({ text: 'Real-Time Events', to: '/admin/real-time' })
      } else if (path.includes('/admin/tasks')) {
        crumbs.push({ text: 'Background Tasks', to: '/admin/tasks' })
      } else if (path.includes('/admin/exports')) {
        crumbs.push({ text: 'Data Exports', to: '/admin/exports' })
      }
      
      return crumbs
    })
    
    // Methods
    const toggleTaskHistory = () => {
      showTaskHistory.value = !showTaskHistory.value
    }
    
    const addTask = (name, status = 'running') => {
      const task = {
        id: Date.now(),
        name,
        status,
        timestamp: new Date()
      }
      taskHistory.value.unshift(task)
      if (taskHistory.value.length > 10) {
        taskHistory.value = taskHistory.value.slice(0, 10)
      }
    }
    
    const updateTaskStatus = (taskId, status) => {
      const task = taskHistory.value.find(t => t.id === taskId)
      if (task) {
        task.status = status
      }
    }
    
    const getTaskStatusClass = (status) => {
      switch (status) {
        case 'success': return 'text-success'
        case 'error': return 'text-danger'
        case 'running': return 'text-warning'
        default: return 'text-secondary'
      }
    }
    
    const getTaskStatusIcon = (status) => {
      switch (status) {
        case 'success': return 'fas fa-check-circle'
        case 'error': return 'fas fa-times-circle'
        case 'running': return 'fas fa-spinner fa-spin'
        default: return 'fas fa-clock'
      }
    }
    
    const formatTaskTime = (timestamp) => {
      const now = new Date()
      const diff = now - timestamp
      const minutes = Math.floor(diff / 60000)
      
      if (minutes < 1) return 'Just now'
      if (minutes < 60) return `${minutes}m ago`
      const hours = Math.floor(minutes / 60)
      if (hours < 24) return `${hours}h ago`
      return timestamp.toLocaleDateString()
    }
    
    const showToast = (title, message, type = 'info') => {
      const toast = {
        id: ++toastIdCounter.value,
        title,
        message,
        type
      }
      toasts.value.push(toast)
      
      // Auto remove after 5 seconds
      setTimeout(() => {
        removeToast(toast.id)
      }, 5000)
    }
    
    const removeToast = (id) => {
      const index = toasts.value.findIndex(t => t.id === id)
      if (index > -1) {
        toasts.value.splice(index, 1)
      }
    }
    
    const getToastIcon = (type) => {
      switch (type) {
        case 'success': return 'fas fa-check-circle'
        case 'danger': return 'fas fa-exclamation-circle'
        case 'warning': return 'fas fa-exclamation-triangle'
        default: return 'fas fa-info-circle'
      }
    }
    
    const showCreateSubjectModal = () => {
      // Navigate to subjects page where user can add a new subject
      router.push('/admin/subjects')
    }
    
    const showCreateQuizModal = () => {
      // Navigate to quizzes page where user can add a new quiz
      router.push('/admin/quizzes')
    }
    
    const handleLogout = async () => {
      try {
        await store.dispatch('logout')
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
        // Force logout even if API call fails
        router.push('/login')
      }
    }
    
    return {
      route,
      breadcrumbs,
      taskHistory,
      showTaskHistory,
      toasts,
      currentUser,
      toggleTaskHistory,
      addTask,
      updateTaskStatus,
      getTaskStatusClass,
      getTaskStatusIcon,
      formatTaskTime,
      showToast,
      removeToast,
      getToastIcon,
      showCreateSubjectModal,
      showCreateQuizModal,
      handleLogout
    }
  }
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: var(--bg-soft);
}

/* Sidebar Styles */
.admin-sidebar {
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

.admin-header {
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.brand-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
}

.admin-nav-link {
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

.admin-nav-link:hover {
  color: white;
  background: rgba(255,255,255,0.1);
  transform: translateX(5px);
}

.admin-nav-link.active {
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

.admin-nav-link.active .nav-indicator {
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

/* Quick Actions */
.quick-actions {
  margin-top: auto;
  border-top: 1px solid rgba(255,255,255,0.1);
}

/* Main Content */
.admin-main {
  background: var(--bg-soft);
}

.breadcrumb-section {
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
  color: var(--qm-medium-gray);
}

.breadcrumb-item + .breadcrumb-item::before {
  content: ">";
  color: var(--qm-medium-gray);
}

.content-header {
  border-bottom: 1px solid #dee2e6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.main-content {
  background: var(--bg-soft);
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-sidebar {
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
}
</style>