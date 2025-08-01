<template>
  <div class="qm-sidebar" :class="{ 'collapsed': isCollapsed }">
    <div class="sidebar-content">
      <!-- Brand Header -->
      <div class="sidebar-header">
        <div class="brand-section">
          <div class="brand-icon">
            <i class="fas fa-graduation-cap"></i>
          </div>
          <div class="brand-text" v-show="!isCollapsed">
            <h4 class="brand-title">Quiz Master</h4>
            <p class="brand-subtitle">{{ roleDisplayName }}</p>
          </div>
        </div>
        <button 
          class="sidebar-toggle" 
          @click="toggleSidebar"
          :title="isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'"
        >
          <i :class="isCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
        </button>
      </div>

      <!-- Navigation Menu -->
      <nav class="sidebar-nav">
        <template v-for="section in navigationSections" :key="section.title">
          <div class="nav-section" v-if="!isCollapsed || section.items.length > 0">
            <div class="nav-section-title" v-show="!isCollapsed">
              <small>{{ section.title }}</small>
            </div>
            <ul class="nav-items">
              <li v-for="item in section.items" :key="item.path" class="nav-item">
                <router-link 
                  :to="item.path" 
                  class="nav-link"
                  :class="{ 'active': isActiveRoute(item.path) }"
                  :title="isCollapsed ? item.label : ''"
                >
                  <div class="nav-icon">
                    <i :class="item.icon"></i>
                  </div>
                  <span class="nav-label" v-show="!isCollapsed">{{ item.label }}</span>
                  <div class="nav-indicator"></div>
                </router-link>
              </li>
            </ul>
          </div>
        </template>
      </nav>

      <!-- User Profile Section -->
      <div class="sidebar-footer">
        <div class="user-profile">
          <div class="user-avatar">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="user-info" v-show="!isCollapsed">
            <div class="user-name">{{ currentUser?.username || 'User' }}</div>
            <div class="user-role">
              <i :class="roleIcon"></i>
              {{ roleDisplayName }}
            </div>
          </div>
        </div>
        
        <!-- Logout Button -->
        <button 
          class="logout-btn"
          @click="handleLogout"
          :title="isCollapsed ? 'Logout' : ''"
        >
          <i class="fas fa-sign-out-alt"></i>
          <span v-show="!isCollapsed">Logout</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'

export default {
  name: 'Sidebar',
  props: {
    role: {
      type: String,
      required: true,
      validator: (value) => ['admin', 'user'].includes(value)
    }
  },
  emits: ['toggle-sidebar'],
  setup(props, { emit }) {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()
    
    const isCollapsed = ref(false)
    
    // Get current user from store
    const currentUser = computed(() => store.getters.currentUser)
    
    // Role-based computed properties
    const roleDisplayName = computed(() => {
      return props.role === 'admin' ? 'Admin Dashboard' : 'Student Portal'
    })
    
    const roleIcon = computed(() => {
      return props.role === 'admin' ? 'fas fa-crown' : 'fas fa-user-graduate'
    })
    
    // Navigation configuration based on role
    const navigationSections = computed(() => {
      if (props.role === 'admin') {
        return [
          {
            title: 'MAIN',
            items: [
              { path: '/admin', label: 'Dashboard', icon: 'fas fa-tachometer-alt' },
              { path: '/admin/analytics', label: 'Analytics', icon: 'fas fa-chart-line' },
              { path: '/admin/real-time', label: 'Real-Time Events', icon: 'fas fa-satellite-dish' }
            ]
          },
          {
            title: 'CONTENT MANAGEMENT',
            items: [
              { path: '/admin/subjects', label: 'Subjects & Chapters', icon: 'fas fa-book' },
              { path: '/admin/quizzes', label: 'Quizzes', icon: 'fas fa-question-circle' }
            ]
          },
          {
            title: 'USERS',
            items: [
              { path: '/admin/users', label: 'Users', icon: 'fas fa-users' }
            ]
          },
          {
            title: 'AUTOMATION',
            items: [
              { path: '/admin/tasks', label: 'Celery Reports / Tasks', icon: 'fas fa-cogs' }
            ]
          }
        ]
      } else {
        return [
          {
            title: 'MAIN',
            items: [
              { path: '/dashboard', label: 'My Dashboard', icon: 'fas fa-home' },
              { path: '/dashboard?tab=quizzes', label: 'My Subjects', icon: 'fas fa-book' },
              { path: '/dashboard?tab=quizzes', label: 'Attempt Quiz', icon: 'fas fa-play-circle' }
            ]
          },
          {
            title: 'PERFORMANCE',
            items: [
              { path: '/dashboard?tab=performance', label: 'Quiz History', icon: 'fas fa-history' },
              { path: '/dashboard?tab=leaderboard', label: 'Leaderboard', icon: 'fas fa-trophy' },
              { path: '/dashboard?tab=performance', label: 'My Statistics', icon: 'fas fa-chart-bar' }
            ]
          },
          {
            title: 'REPORTS',
            items: [
              { path: '/dashboard?tab=export', label: 'Export Report', icon: 'fas fa-download' }
            ]
          }
        ]
      }
    })
    
    // Methods
    const toggleSidebar = () => {
      isCollapsed.value = !isCollapsed.value
      emit('toggle-sidebar', isCollapsed.value)
      
      // Store preference in localStorage
      localStorage.setItem('sidebar-collapsed', isCollapsed.value.toString())
    }
    
    const isActiveRoute = (path) => {
      if (path.includes('?')) {
        const [basePath, query] = path.split('?')
        return route.path === basePath && route.query.tab === new URLSearchParams(query).get('tab')
      }
      return route.path === path || route.path.startsWith(path + '/')
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
    
    // Load sidebar state from localStorage
    onMounted(() => {
      const savedState = localStorage.getItem('sidebar-collapsed')
      if (savedState !== null) {
        isCollapsed.value = savedState === 'true'
      }
    })
    
    return {
      isCollapsed,
      currentUser,
      roleDisplayName,
      roleIcon,
      navigationSections,
      toggleSidebar,
      isActiveRoute,
      handleLogout
    }
  }
}
</script>

<style scoped>
.qm-sidebar {
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  min-height: 100vh;
  width: 280px;
  transition: var(--qm-transition);
  box-shadow: 2px 0 15px rgba(0,0,0,0.1);
  position: relative;
  z-index: 1000;
}

.qm-sidebar.collapsed {
  width: 70px;
}

.sidebar-content {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
}

/* Brand Header */
.sidebar-header {
  padding: 1.5rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  position: relative;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand-icon {
  width: 50px;
  height: 50px;
  background: var(--qm-primary-gradient);
  border-radius: var(--qm-border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  animation: float 3s ease-in-out infinite;
  flex-shrink: 0;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-3px); }
}

.brand-text {
  color: white;
  min-width: 0;
}

.brand-title {
  font-family: var(--qm-font-heading);
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 0.875rem;
  opacity: 0.8;
  margin: 0;
  line-height: 1.2;
}

.sidebar-toggle {
  position: absolute;
  top: 50%;
  right: -15px;
  transform: translateY(-50%);
  width: 30px;
  height: 30px;
  background: var(--qm-primary-gradient);
  border: none;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--qm-transition);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  z-index: 1001;
}

.sidebar-toggle:hover {
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-section {
  margin-bottom: 2rem;
}

.nav-section-title {
  padding: 0 1.5rem 0.5rem;
  color: rgba(255,255,255,0.6);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin-bottom: 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.875rem 1.5rem;
  color: rgba(255,255,255,0.8);
  text-decoration: none;
  transition: var(--qm-transition);
  position: relative;
  border-radius: 0;
  margin: 0 0.5rem;
  border-radius: var(--qm-border-radius);
}

.nav-link:hover {
  color: white;
  background: rgba(255,255,255,0.1);
  transform: translateX(5px);
}

.nav-link.active {
  color: white;
  background: var(--qm-primary-gradient);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.nav-icon {
  width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
}

.nav-label {
  font-weight: 500;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--qm-primary-gradient);
  transform: scaleY(0);
  transition: transform 0.3s ease;
  border-radius: 0 3px 3px 0;
}

.nav-link.active .nav-indicator {
  transform: scaleY(1);
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255,255,255,0.1);
  margin-top: auto;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(255,255,255,0.05);
  border-radius: var(--qm-border-radius);
}

.user-avatar {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.8);
  font-size: 1.5rem;
  flex-shrink: 0;
}

.user-info {
  min-width: 0;
  color: white;
}

.user-name {
  font-weight: 600;
  font-size: 0.9rem;
  line-height: 1.2;
  margin-bottom: 0.25rem;
}

.user-role {
  font-size: 0.75rem;
  opacity: 0.8;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.logout-btn {
  width: 100%;
  padding: 0.75rem;
  background: rgba(231, 76, 60, 0.1);
  border: 1px solid rgba(231, 76, 60, 0.3);
  border-radius: var(--qm-border-radius);
  color: #e74c3c;
  font-weight: 500;
  cursor: pointer;
  transition: var(--qm-transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.logout-btn:hover {
  background: rgba(231, 76, 60, 0.2);
  border-color: rgba(231, 76, 60, 0.5);
  transform: translateY(-1px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .qm-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1050;
    transform: translateX(-100%);
  }
  
  .qm-sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .sidebar-toggle {
    display: none;
  }
}

/* Collapsed state adjustments */
.qm-sidebar.collapsed .nav-link {
  justify-content: center;
  padding: 0.875rem 0;
}

.qm-sidebar.collapsed .nav-icon {
  margin-right: 0;
}

.qm-sidebar.collapsed .user-profile {
  justify-content: center;
}

.qm-sidebar.collapsed .logout-btn {
  padding: 0.75rem 0;
}
</style>