<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark qm-gradient-bg" v-if="!isAdminRoute && !isUserDashboardRoute">
      <div class="container">
        <router-link class="navbar-brand fw-bold" to="/">
          <i class="fas fa-graduation-cap me-2"></i>
          Quiz Master V2
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item" v-if="isAuthenticated">
              <router-link class="nav-link" to="/dashboard">
                <i class="fas fa-tachometer-alt me-1"></i>Dashboard
              </router-link>
            </li>
            <li class="nav-item" v-if="isAdmin">
              <router-link class="nav-link" to="/admin">
                <i class="fas fa-cog me-1"></i>Admin Panel
              </router-link>
            </li>
          </ul>
          
          <ul class="navbar-nav">
            <li class="nav-item" v-if="!isAuthenticated">
              <router-link class="nav-link" to="/login">
                <i class="fas fa-sign-in-alt me-1"></i>Login
              </router-link>
            </li>
            <li class="nav-item" v-if="!isAuthenticated">
              <router-link class="nav-link" to="/register">
                <i class="fas fa-user-plus me-1"></i>Register
              </router-link>
            </li>
            <li class="nav-item dropdown" v-if="isAuthenticated">
              <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button" data-bs-toggle="dropdown">
                <div class="welcome-text me-2">
                  <small class="d-block opacity-75">Welcome back,</small>
                  <strong>{{ user?.username || 'User' }}</strong>
                </div>
                <div class="user-avatar">
                  <i class="fas fa-user-circle fa-2x"></i>
                </div>
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><router-link class="dropdown-item" to="/profile"><i class="fas fa-user me-2"></i>Profile</router-link></li>
                <li><router-link class="dropdown-item" to="/achievements"><i class="fas fa-trophy me-2"></i>Achievements</router-link></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click="logout"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>

    <!-- Achievement Celebration Modal -->
    <div class="modal fade" id="achievementModal" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0">
          <div class="modal-body text-center p-5">
            <div class="achievement-celebration">
              <div class="confetti-container" ref="confettiContainer"></div>
              <div class="achievement-icon mb-3">
                <i class="fas fa-trophy text-warning" style="font-size: 4rem;"></i>
              </div>
              <h3 class="achievement-title text-primary mb-2">🎉 Achievement Unlocked!</h3>
              <p class="achievement-description">{{ achievementMessage }}</p>
              <div class="badge-qm d-inline-block mt-2">
                {{ achievementBadge }}
              </div>
            </div>
            <button type="button" class="btn btn-qm-primary mt-4" data-bs-dismiss="modal">
              <i class="fas fa-check me-2"></i>Awesome!
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Container -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div class="toast toast-qm-success" id="successToast" role="alert">
        <div class="toast-header bg-transparent border-0 text-white">
          <i class="fas fa-check-circle me-2"></i>
          <strong class="me-auto">Success</strong>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body" id="successMessage"></div>
      </div>
      
      <div class="toast toast-qm-error" id="errorToast" role="alert">
        <div class="toast-header bg-transparent border-0 text-white">
          <i class="fas fa-exclamation-triangle me-2"></i>
          <strong class="me-auto">Notice</strong>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body" id="errorMessage"></div>
      </div>
    </div>

    <!-- Global Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted">{{ loadingMessage || 'Loading...' }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Toast, Modal } from 'bootstrap'

export default {
  name: 'App',
  setup() {
    const store = useStore()
    const router = useRouter()
    const confettiContainer = ref(null)
    const achievementMessage = ref('')
    const achievementBadge = ref('')
    const loadingMessage = ref('')

    const isAuthenticated = computed(() => store.getters.isAuthenticated)
    const isAdmin = computed(() => store.getters.isAdmin)
    const user = computed(() => store.state.user)
    const isLoading = computed(() => store.getters.isLoading)
    const isAdminRoute = computed(() => router.currentRoute.value.path.startsWith('/admin'))
    const isUserDashboardRoute = computed(() => {
      const path = router.currentRoute.value.path
      return path.startsWith('/dashboard') || path.startsWith('/my-') || path.startsWith('/leaderboard') || path.startsWith('/achievements') || path.startsWith('/quiz/')
    })

    const logout = async () => {
      await store.dispatch('logout')
      router.push('/login')
      showSuccessToast('Logged out successfully!')
    }

    const showSuccessToast = (message) => {
      const toastElement = document.getElementById('successToast')
      const messageElement = document.getElementById('successMessage')
      messageElement.textContent = message
      
      const toast = new Toast(toastElement)
      toast.show()
    }

    const showErrorToast = (message) => {
      const toastElement = document.getElementById('errorToast')
      const messageElement = document.getElementById('errorMessage')
      messageElement.textContent = message
      
      const toast = new Toast(toastElement)
      toast.show()
    }

    const triggerAchievement = (message, badge) => {
      achievementMessage.value = message
      achievementBadge.value = badge
      
      // Trigger confetti animation
      if (confettiContainer.value) {
        createConfetti()
      }
      
      const modal = new Modal(document.getElementById('achievementModal'))
      modal.show()
    }

    const createConfetti = () => {
      // Simple confetti effect using CSS animations
      const colors = ['#ff9a56', '#4ecdc4', '#3498db', '#2ecc71', '#f39c12']
      
      for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div')
        confetti.style.cssText = `
          position: absolute;
          width: 10px;
          height: 10px;
          background: ${colors[Math.floor(Math.random() * colors.length)]};
          left: ${Math.random() * 100}%;
          top: -10px;
          opacity: 1;
          animation: confettiFall 3s linear forwards;
          animation-delay: ${Math.random() * 2}s;
        `
        
        confettiContainer.value.appendChild(confetti)
        
        setTimeout(() => {
          confetti.remove()
        }, 5000)
      }
    }

    // Add confetti animation CSS
    onMounted(() => {
      const style = document.createElement('style')
      style.textContent = `
        @keyframes confettiFall {
          0% {
            transform: translateY(-10px) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(360deg);
            opacity: 0;
          }
        }
      `
      document.head.appendChild(style)
    })

    // Global event listeners for toasts and achievements
    onMounted(() => {
      window.addEventListener('show-success-toast', (e) => {
        showSuccessToast(e.detail.message)
      })
      
      window.addEventListener('show-error-toast', (e) => {
        showErrorToast(e.detail.message)
      })
      
      window.addEventListener('trigger-achievement', (e) => {
        triggerAchievement(e.detail.message, e.detail.badge)
      })
    })

    return {
      isAuthenticated,
      isAdmin,
      user,
      isLoading,
      loadingMessage,
      achievementMessage,
      achievementBadge,
      confettiContainer,
      isAdminRoute,
      isUserDashboardRoute,
      logout
    }
  }
}
</script>

<style scoped>
/* Enhanced Navigation Styling */
.navbar {
  background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #0EA5E9 100%) !important;
  box-shadow: 0 4px 20px rgba(30, 58, 138, 0.3);
  border-bottom: 3px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1000;
}

.navbar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, 
    rgba(255, 255, 255, 0.1) 0%, 
    rgba(255, 255, 255, 0.05) 50%, 
    rgba(255, 255, 255, 0.1) 100%);
  pointer-events: none;
}

.navbar-brand {
  font-family: var(--qm-font-heading);
  font-size: 1.6rem;
  text-decoration: none;
  color: #FFFFFF !important;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  font-weight: 700;
  transition: all 0.3s ease;
}

.navbar-brand:hover {
  color: #F0F9FF !important;
  transform: translateY(-1px);
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
}

.nav-link {
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 500;
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 0 4px;
  padding: 8px 16px !important;
}

.nav-link:hover {
  color: #FFFFFF !important;
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.dropdown-menu {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 8px 32px rgba(30, 58, 138, 0.2);
  border-radius: 12px;
}

.dropdown-item {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 2px 8px;
}

.dropdown-item:hover {
  background: linear-gradient(135deg, #3B82F6, #0EA5E9);
  color: white;
  transform: translateX(4px);
}

/* Enhanced Main Content Styling */
.main-content {
  min-height: calc(100vh - 76px);
  background: linear-gradient(135deg, 
    #F8FAFC 0%, 
    #F1F5F9 25%, 
    #E2E8F0 50%, 
    #F8FAFC 75%, 
    #FFFFFF 100%);
  position: relative;
  overflow-x: hidden;
}

.main-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(180deg, 
    rgba(59, 130, 246, 0.05) 0%, 
    rgba(59, 130, 246, 0.02) 50%, 
    transparent 100%);
  pointer-events: none;
}

/* Content sections visual enhancement */
.main-content .container {
  position: relative;
  z-index: 2;
}

/* Hero section enhancement */
.hero-section {
  background: linear-gradient(135deg, 
    #1E3A8A 0%, 
    #3B82F6 25%, 
    #0EA5E9 50%, 
    #06B6D4 75%, 
    #0891B2 100%) !important;
  position: relative;
  overflow: hidden;
}

.hero-section::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

/* Features section enhancement */
.features-section {
  background: linear-gradient(135deg, 
    #FFFFFF 0%, 
    #F8FAFC 25%, 
    #F1F5F9 50%, 
    #F8FAFC 75%, 
    #FFFFFF 100%) !important;
  border-top: 1px solid rgba(59, 130, 246, 0.1);
  position: relative;
}

.features-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    #3B82F6 25%, 
    #0EA5E9 50%, 
    #3B82F6 75%, 
    transparent 100%);
}

/* Card enhancements for better visual hierarchy */
.card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(59, 130, 246, 0.1);
  box-shadow: 0 4px 20px rgba(30, 58, 138, 0.08);
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(30, 58, 138, 0.15);
  border-color: rgba(59, 130, 246, 0.2);
}

.welcome-text {
  text-align: right;
  line-height: 1.2;
}

.user-avatar {
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.dropdown:hover .user-avatar {
  opacity: 1;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: var(--qm-border-radius);
  box-shadow: var(--qm-shadow);
}

.achievement-celebration {
  animation: achievementReveal 0.6s ease-out;
}

@keyframes achievementReveal {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.achievement-icon {
  animation: iconBounce 0.8s ease-out 0.2s both;
}

@keyframes iconBounce {
  0%, 20%, 53%, 80%, 100% {
    transform: translateY(0);
  }
  40%, 43% {
    transform: translateY(-15px);
  }
  70% {
    transform: translateY(-7px);
  }
  90% {
    transform: translateY(-3px);
  }
}

@media (max-width: 768px) {
  .welcome-text {
    display: none;
  }
  
  .navbar-brand {
    font-size: 1.25rem;
  }
}
</style>