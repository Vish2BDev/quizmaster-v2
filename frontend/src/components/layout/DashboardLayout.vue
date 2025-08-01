<template>
  <div class="dashboard-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- Sidebar -->
    <Sidebar 
      :role="userRole" 
      @toggle-sidebar="handleSidebarToggle"
    />
    
    <!-- Mobile Overlay -->
    <div 
      class="mobile-overlay" 
      :class="{ 'show': showMobileMenu }"
      @click="closeMobileMenu"
    ></div>
    
    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Top Navigation Bar -->
      <header class="top-navbar">
        <div class="navbar-content">
          <!-- Mobile Menu Toggle -->
          <button 
            class="mobile-menu-toggle d-md-none"
            @click="toggleMobileMenu"
          >
            <i class="fas fa-bars"></i>
          </button>
          
          <!-- Breadcrumb Navigation -->
          <nav class="breadcrumb-nav" aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item">
                <router-link :to="homeRoute" class="breadcrumb-link">
                  <i class="fas fa-home"></i>
                  <span class="d-none d-sm-inline">{{ homeLabel }}</span>
                </router-link>
              </li>
              <li 
                v-for="(crumb, index) in breadcrumbs" 
                :key="index" 
                class="breadcrumb-item"
                :class="{ 'active': index === breadcrumbs.length - 1 }"
              >
                <router-link 
                  v-if="crumb.to && index !== breadcrumbs.length - 1" 
                  :to="crumb.to" 
                  class="breadcrumb-link"
                >
                  <i :class="crumb.icon" v-if="crumb.icon"></i>
                  {{ crumb.text }}
                </router-link>
                <span v-else class="breadcrumb-current">
                  <i :class="crumb.icon" v-if="crumb.icon"></i>
                  {{ crumb.text }}
                </span>
              </li>
            </ol>
          </nav>
          
          <!-- Right Side Actions -->
          <div class="navbar-actions">
            <!-- Notifications (Optional) -->
            <div class="notification-bell" v-if="showNotifications">
              <button class="btn-icon" title="Notifications">
                <i class="fas fa-bell"></i>
                <span class="notification-badge" v-if="notificationCount > 0">
                  {{ notificationCount > 99 ? '99+' : notificationCount }}
                </span>
              </button>
            </div>
            
            <!-- Profile Badge -->
            <div class="profile-badge">
              <div class="profile-avatar">
                <i class="fas fa-user-circle"></i>
              </div>
              <div class="profile-info d-none d-sm-block">
                <div class="profile-name">{{ currentUser?.username || 'User' }}</div>
                <div class="profile-role">
                  <i :class="roleIcon"></i>
                  {{ roleDisplayName }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      <!-- Page Header (Optional) -->
      <div class="page-header" v-if="pageTitle || $slots['page-header']">
        <div class="page-header-content">
          <div class="page-title-section" v-if="pageTitle">
            <h1 class="page-title">
              <i :class="pageIcon" v-if="pageIcon"></i>
              {{ pageTitle }}
            </h1>
            <p class="page-description" v-if="pageDescription">
              {{ pageDescription }}
            </p>
          </div>
          
          <!-- Page Actions Slot -->
          <div class="page-actions" v-if="$slots['page-actions']">
            <slot name="page-actions"></slot>
          </div>
          
          <!-- Custom Page Header Slot -->
          <slot name="page-header"></slot>
        </div>
      </div>
      
      <!-- Main Content -->
      <main class="content-area">
        <div class="content-container">
          <slot></slot>
        </div>
      </main>
    </div>
    
    <!-- Toast Notifications -->
    <div class="toast-container">
      <div 
        v-for="toast in toasts" 
        :key="toast.id" 
        :class="['toast', 'show', `toast-${toast.type}`]" 
        role="alert"
      >
        <div class="toast-header">
          <i :class="getToastIcon(toast.type)"></i>
          <strong class="toast-title">{{ toast.title }}</strong>
          <button 
            type="button" 
            class="toast-close" 
            @click="removeToast(toast.id)"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="toast-body">
          {{ toast.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import Sidebar from './Sidebar.vue'

export default {
  name: 'DashboardLayout',
  components: {
    Sidebar
  },
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
    showNotifications: {
      type: Boolean,
      default: false
    },
    notificationCount: {
      type: Number,
      default: 0
    }
  },
  setup() {
    const route = useRoute()
    const store = useStore()
    
    // Reactive state
    const sidebarCollapsed = ref(false)
    const showMobileMenu = ref(false)
    const toasts = ref([])
    const toastIdCounter = ref(0)
    
    // Get current user from store
    const currentUser = computed(() => store.getters.currentUser)
    
    // Determine user role
    const userRole = computed(() => {
      return route.path.startsWith('/admin') ? 'admin' : 'user'
    })
    
    // Role-based computed properties
    const roleDisplayName = computed(() => {
      return userRole.value === 'admin' ? 'Administrator' : 'Student'
    })
    
    const roleIcon = computed(() => {
      return userRole.value === 'admin' ? 'fas fa-crown' : 'fas fa-user-graduate'
    })
    
    const homeRoute = computed(() => {
      return userRole.value === 'admin' ? '/admin' : '/dashboard'
    })
    
    const homeLabel = computed(() => {
      return userRole.value === 'admin' ? 'Admin' : 'Dashboard'
    })
    
    // Methods
    const handleSidebarToggle = (collapsed) => {
      sidebarCollapsed.value = collapsed
    }
    
    const toggleMobileMenu = () => {
      showMobileMenu.value = !showMobileMenu.value
    }
    
    const closeMobileMenu = () => {
      showMobileMenu.value = false
    }
    
    // Toast notification methods
    const showToast = (type, title, message, duration = 5000) => {
      const toast = {
        id: ++toastIdCounter.value,
        type,
        title,
        message,
        timestamp: Date.now()
      }
      
      toasts.value.push(toast)
      
      // Auto-remove toast after duration
      setTimeout(() => {
        removeToast(toast.id)
      }, duration)
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
        case 'error': return 'fas fa-exclamation-circle'
        case 'warning': return 'fas fa-exclamation-triangle'
        case 'info': return 'fas fa-info-circle'
        default: return 'fas fa-info-circle'
      }
    }
    
    // Handle window resize for mobile responsiveness
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        showMobileMenu.value = false
      }
    }
    
    // Lifecycle hooks
    onMounted(() => {
      window.addEventListener('resize', handleResize)
      
      // Load sidebar state from localStorage
      const savedState = localStorage.getItem('sidebar-collapsed')
      if (savedState !== null) {
        sidebarCollapsed.value = savedState === 'true'
      }
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })
    
    // Expose methods for child components
    const layoutMethods = {
      showToast,
      removeToast
    }
    
    // Provide methods to child components
    return {
      sidebarCollapsed,
      showMobileMenu,
      toasts,
      currentUser,
      userRole,
      roleDisplayName,
      roleIcon,
      homeRoute,
      homeLabel,
      handleSidebarToggle,
      toggleMobileMenu,
      closeMobileMenu,
      showToast,
      removeToast,
      getToastIcon,
      ...layoutMethods
    }
  }
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background: #f8f9fa;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: var(--qm-transition);
}

/* Top Navigation */
.top-navbar {
  background: white;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
  position: sticky;
  top: 0;
  z-index: 1020;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  gap: 1rem;
}

.mobile-menu-toggle {
  background: none;
  border: none;
  color: var(--qm-dark-gray);
  font-size: 1.25rem;
  padding: 0.5rem;
  border-radius: var(--qm-border-radius);
  transition: var(--qm-transition);
}

.mobile-menu-toggle:hover {
  background: var(--qm-light-gray);
  color: var(--qm-electric-blue);
}

/* Breadcrumb Navigation */
.breadcrumb-nav {
  flex: 1;
  min-width: 0;
}

.breadcrumb {
  background: transparent;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: "/";
  color: var(--qm-medium-gray);
  margin: 0 0.5rem;
}

.breadcrumb-link {
  color: var(--qm-electric-blue);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: var(--qm-transition);
  padding: 0.25rem 0.5rem;
  border-radius: var(--qm-border-radius);
}

.breadcrumb-link:hover {
  background: rgba(52, 152, 219, 0.1);
  color: var(--qm-electric-blue);
}

.breadcrumb-current {
  color: var(--qm-dark-gray);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Navbar Actions */
.navbar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.notification-bell {
  position: relative;
}

.btn-icon {
  background: none;
  border: none;
  color: var(--qm-medium-gray);
  font-size: 1.25rem;
  padding: 0.5rem;
  border-radius: var(--qm-border-radius);
  transition: var(--qm-transition);
  position: relative;
}

.btn-icon:hover {
  background: var(--qm-light-gray);
  color: var(--qm-electric-blue);
}

.notification-badge {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  background: var(--qm-error-red);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.125rem 0.375rem;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  line-height: 1;
}

.profile-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: var(--qm-border-radius);
  transition: var(--qm-transition);
}

.profile-badge:hover {
  background: var(--qm-light-gray);
}

.profile-avatar {
  color: var(--qm-medium-gray);
  font-size: 1.75rem;
}

.profile-info {
  text-align: right;
}

.profile-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--qm-dark-gray);
  line-height: 1.2;
}

.profile-role {
  font-size: 0.75rem;
  color: var(--qm-medium-gray);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.25rem;
}

/* Page Header */
.page-header {
  background: white;
  border-bottom: 1px solid #e9ecef;
  padding: 1.5rem;
}

.page-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.page-title {
  font-family: var(--qm-font-heading);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--qm-dark-gray);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-title i {
  color: var(--qm-electric-blue);
}

.page-description {
  color: var(--qm-medium-gray);
  margin: 0.5rem 0 0;
  font-size: 1rem;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Content Area */
.content-area {
  flex: 1;
  overflow-y: auto;
}

.content-container {
  padding: 1.5rem;
  max-width: 100%;
}

/* Mobile Overlay */
.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 1040;
  opacity: 0;
  visibility: hidden;
  transition: var(--qm-transition);
}

.mobile-overlay.show {
  opacity: 1;
  visibility: visible;
}

/* Toast Notifications */
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1060;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 400px;
}

.toast {
  background: white;
  border-radius: var(--qm-border-radius);
  box-shadow: var(--qm-shadow);
  overflow: hidden;
  transform: translateX(100%);
  transition: var(--qm-transition);
}

.toast.show {
  transform: translateX(0);
}

.toast-success {
  border-left: 4px solid var(--qm-success-green);
}

.toast-error {
  border-left: 4px solid var(--qm-error-red);
}

.toast-warning {
  border-left: 4px solid var(--qm-warning-orange);
}

.toast-info {
  border-left: 4px solid var(--qm-electric-blue);
}

.toast-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--qm-light-gray);
  border-bottom: 1px solid #e9ecef;
}

.toast-title {
  flex: 1;
  font-weight: 600;
  font-size: 0.9rem;
}

.toast-close {
  background: none;
  border: none;
  color: var(--qm-medium-gray);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: var(--qm-border-radius);
  transition: var(--qm-transition);
}

.toast-close:hover {
  background: rgba(0,0,0,0.1);
  color: var(--qm-dark-gray);
}

.toast-body {
  padding: 1rem;
  color: var(--qm-dark-gray);
  font-size: 0.9rem;
  line-height: 1.4;
}

/* Responsive Design */
@media (max-width: 768px) {
  .navbar-content {
    padding: 1rem;
  }
  
  .page-header {
    padding: 1rem;
  }
  
  .page-header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .content-container {
    padding: 1rem;
  }
  
  .toast-container {
    top: 0.5rem;
    right: 0.5rem;
    left: 0.5rem;
    max-width: none;
  }
}

@media (max-width: 576px) {
  .breadcrumb-item span {
    display: none;
  }
  
  .breadcrumb-item:first-child span {
    display: inline;
  }
}

/* Sidebar collapsed adjustments */
.dashboard-layout.sidebar-collapsed .main-content {
  margin-left: 0;
}
</style>