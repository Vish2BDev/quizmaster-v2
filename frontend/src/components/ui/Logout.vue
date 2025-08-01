<template>
  <div class="logout-component">
    <!-- Logout Button -->
    <button 
      v-if="!showConfirmation"
      class="logout-btn"
      :class="buttonClass"
      @click="handleLogoutClick"
      :disabled="isLoggingOut"
      :title="buttonTitle"
    >
      <i class="fas fa-sign-out-alt" v-if="!isLoggingOut"></i>
      <div class="spinner-border spinner-border-sm" role="status" v-else>
        <span class="visually-hidden">Logging out...</span>
      </div>
      <span v-if="showText && !isLoggingOut">{{ buttonText }}</span>
      <span v-if="showText && isLoggingOut">{{ loadingText }}</span>
    </button>
    
    <!-- Confirmation Modal -->
    <div 
      v-if="showConfirmation" 
      class="logout-modal-backdrop"
      @click="cancelLogout"
    >
      <div class="logout-modal" @click.stop>
        <div class="logout-modal-header">
          <div class="logout-icon">
            <i class="fas fa-sign-out-alt"></i>
          </div>
          <h5 class="logout-title">Confirm Logout</h5>
        </div>
        
        <div class="logout-modal-body">
          <p class="logout-message">
            {{ confirmationMessage }}
          </p>
          
          <!-- Session Info -->
          <div class="session-info" v-if="sessionInfo">
            <div class="session-item">
              <span class="session-label">Logged in as:</span>
              <span class="session-value">{{ sessionInfo.username }}</span>
            </div>
            <div class="session-item" v-if="sessionInfo.role">
              <span class="session-label">Role:</span>
              <span class="session-value role-badge" :class="`role-${sessionInfo.role}`">
                {{ formatRole(sessionInfo.role) }}
              </span>
            </div>
            <div class="session-item" v-if="sessionInfo.loginTime">
              <span class="session-label">Session started:</span>
              <span class="session-value">{{ formatTime(sessionInfo.loginTime) }}</span>
            </div>
          </div>
          
          <!-- Unsaved Changes Warning -->
          <div class="unsaved-warning" v-if="hasUnsavedChanges">
            <div class="warning-icon">
              <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="warning-content">
              <strong>Warning:</strong> You have unsaved changes that will be lost.
            </div>
          </div>
        </div>
        
        <div class="logout-modal-footer">
          <button 
            class="btn btn-secondary"
            @click="cancelLogout"
            :disabled="isLoggingOut"
          >
            Cancel
          </button>
          <button 
            class="btn btn-danger"
            @click="confirmLogout"
            :disabled="isLoggingOut"
          >
            <div class="spinner-border spinner-border-sm me-2" role="status" v-if="isLoggingOut">
              <span class="visually-hidden">Logging out...</span>
            </div>
            <i class="fas fa-sign-out-alt me-2" v-else></i>
            {{ isLoggingOut ? 'Logging out...' : 'Logout' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'

export default {
  name: 'Logout',
  props: {
    // Button appearance
    variant: {
      type: String,
      default: 'outline',
      validator: (value) => ['outline', 'solid', 'text', 'icon'].includes(value)
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md', 'lg'].includes(value)
    },
    showText: {
      type: Boolean,
      default: true
    },
    buttonText: {
      type: String,
      default: 'Logout'
    },
    loadingText: {
      type: String,
      default: 'Logging out...'
    },
    
    // Behavior
    requireConfirmation: {
      type: Boolean,
      default: true
    },
    confirmationMessage: {
      type: String,
      default: 'Are you sure you want to logout? This will end your current session.'
    },
    autoRedirect: {
      type: Boolean,
      default: true
    },
    redirectTo: {
      type: String,
      default: '/login'
    },
    
    // Session management
    clearLocalStorage: {
      type: Boolean,
      default: true
    },
    clearSessionStorage: {
      type: Boolean,
      default: true
    },
    
    // Custom handlers
    customLogoutHandler: {
      type: Function,
      default: null
    }
  },
  emits: ['logout-start', 'logout-success', 'logout-error', 'logout-cancel'],
  setup(props, { emit }) {
    const router = useRouter()
    const { showToast } = useToast()
    
    // Reactive state
    const isLoggingOut = ref(false)
    const showConfirmation = ref(false)
    const hasUnsavedChanges = ref(false)
    const sessionInfo = ref(null)
    
    // Computed properties
    const buttonClass = computed(() => {
      const classes = ['logout-btn']
      
      // Variant classes
      switch (props.variant) {
        case 'solid':
          classes.push('btn', 'btn-danger')
          break
        case 'outline':
          classes.push('btn', 'btn-outline-danger')
          break
        case 'text':
          classes.push('btn', 'btn-link', 'text-danger')
          break
        case 'icon':
          classes.push('btn', 'btn-outline-secondary', 'btn-icon')
          break
      }
      
      // Size classes
      if (props.size === 'sm') classes.push('btn-sm')
      if (props.size === 'lg') classes.push('btn-lg')
      
      return classes.join(' ')
    })
    
    const buttonTitle = computed(() => {
      if (props.variant === 'icon') {
        return props.buttonText
      }
      return ''
    })
    
    // Methods
    const loadSessionInfo = () => {
      try {
        const token = localStorage.getItem('token')
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        const loginTime = localStorage.getItem('loginTime')
        
        if (token && user.username) {
          sessionInfo.value = {
            username: user.username,
            role: user.role,
            loginTime: loginTime ? new Date(loginTime) : null
          }
        }
      } catch (error) {
        console.warn('Failed to load session info:', error)
      }
    }
    
    const checkUnsavedChanges = () => {
      // Check for unsaved changes in forms, editors, etc.
      const forms = document.querySelectorAll('form[data-unsaved="true"]')
      const editors = document.querySelectorAll('[data-editor-dirty="true"]')
      
      hasUnsavedChanges.value = forms.length > 0 || editors.length > 0
    }
    
    const handleLogoutClick = () => {
      if (props.requireConfirmation) {
        loadSessionInfo()
        checkUnsavedChanges()
        showConfirmation.value = true
      } else {
        performLogout()
      }
    }
    
    const cancelLogout = () => {
      showConfirmation.value = false
      emit('logout-cancel')
    }
    
    const confirmLogout = () => {
      showConfirmation.value = false
      performLogout()
    }
    
    const performLogout = async () => {
      if (isLoggingOut.value) return
      
      isLoggingOut.value = true
      emit('logout-start')
      
      try {
        // Custom logout handler
        if (props.customLogoutHandler) {
          await props.customLogoutHandler()
        } else {
          await defaultLogoutHandler()
        }
        
        // Clear storage
        if (props.clearLocalStorage) {
          clearLocalStorageData()
        }
        
        if (props.clearSessionStorage) {
          sessionStorage.clear()
        }
        
        // Show success message
        showToast({
          type: 'success',
          title: 'Logged Out',
          message: 'You have been successfully logged out.',
          duration: 3000
        })
        
        emit('logout-success')
        
        // Redirect
        if (props.autoRedirect) {
          await router.push(props.redirectTo)
        }
        
      } catch (error) {
        console.error('Logout error:', error)
        
        showToast({
          type: 'error',
          title: 'Logout Failed',
          message: error.message || 'An error occurred during logout. Please try again.',
          duration: 5000
        })
        
        emit('logout-error', error)
      } finally {
        isLoggingOut.value = false
      }
    }
    
    const defaultLogoutHandler = async () => {
      const token = localStorage.getItem('token')
      
      if (token) {
        // Call logout API endpoint
        try {
          const response = await fetch('http://localhost:5000/logout', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          })
          
          if (!response.ok) {
            throw new Error(`Logout failed: ${response.statusText}`)
          }
        } catch (error) {
          // If API call fails, still proceed with local logout
          console.warn('API logout failed, proceeding with local logout:', error)
        }
      }
    }
    
    const clearLocalStorageData = () => {
      const keysToRemove = [
        'token',
        'user',
        'loginTime',
        'refreshToken',
        'userPreferences',
        'dashboardState',
        'quizProgress'
      ]
      
      keysToRemove.forEach(key => {
        localStorage.removeItem(key)
      })
    }
    
    const formatRole = (role) => {
      return role.charAt(0).toUpperCase() + role.slice(1)
    }
    
    const formatTime = (time) => {
      if (!time) return 'Unknown'
      
      const now = new Date()
      const loginTime = new Date(time)
      const diffMs = now - loginTime
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
      
      if (diffHours > 0) {
        return `${diffHours}h ${diffMinutes}m ago`
      } else if (diffMinutes > 0) {
        return `${diffMinutes}m ago`
      } else {
        return 'Just now'
      }
    }
    
    // Handle escape key
    const handleEscapeKey = (event) => {
      if (event.key === 'Escape' && showConfirmation.value) {
        cancelLogout()
      }
    }
    
    // Lifecycle hooks
    onMounted(() => {
      document.addEventListener('keydown', handleEscapeKey)
    })
    
    onUnmounted(() => {
      document.removeEventListener('keydown', handleEscapeKey)
    })
    
    return {
      isLoggingOut,
      showConfirmation,
      hasUnsavedChanges,
      sessionInfo,
      buttonClass,
      buttonTitle,
      handleLogoutClick,
      cancelLogout,
      confirmLogout,
      formatRole,
      formatTime
    }
  }
}
</script>

<style scoped>
/* Logout Button */
.logout-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: var(--qm-transition);
  border: none;
  background: none;
  cursor: pointer;
}

.logout-btn:hover {
  transform: translateY(-1px);
}

.logout-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

/* Modal Backdrop */
.logout-modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  animation: fadeIn 0.2s ease-out;
}

/* Modal */
.logout-modal {
  background: white;
  border-radius: var(--qm-border-radius-lg);
  box-shadow: var(--qm-shadow-lg);
  max-width: 480px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease-out;
}

/* Modal Header */
.logout-modal-header {
  padding: 2rem 2rem 1rem;
  text-align: center;
  border-bottom: 1px solid #f1f5f9;
}

.logout-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  font-size: 2rem;
  color: var(--qm-error-red);
}

.logout-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--qm-dark-gray);
  margin: 0;
}

/* Modal Body */
.logout-modal-body {
  padding: 1.5rem 2rem;
}

.logout-message {
  font-size: 1rem;
  color: var(--qm-medium-gray);
  text-align: center;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

/* Session Info */
.session-info {
  background: #f8fafc;
  border-radius: var(--qm-border-radius);
  padding: 1rem;
  margin-bottom: 1rem;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.session-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.session-label {
  font-size: 0.875rem;
  color: var(--qm-medium-gray);
  font-weight: 500;
}

.session-value {
  font-size: 0.875rem;
  color: var(--qm-dark-gray);
  font-weight: 600;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--qm-border-radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.role-admin {
  background: var(--qm-electric-blue);
  color: white;
}

.role-user {
  background: var(--qm-success-green);
  color: white;
}

/* Unsaved Warning */
.unsaved-warning {
  background: #fef3cd;
  border: 1px solid #ffeaa7;
  border-radius: var(--qm-border-radius);
  padding: 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.warning-icon {
  color: var(--qm-warning-orange);
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.warning-content {
  font-size: 0.875rem;
  color: #856404;
  line-height: 1.4;
}

/* Modal Footer */
.logout-modal-footer {
  padding: 1rem 2rem 2rem;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.logout-modal-footer .btn {
  min-width: 100px;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 576px) {
  .logout-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .logout-modal-header,
  .logout-modal-body {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
  
  .logout-modal-footer {
    padding: 1rem 1.5rem 1.5rem;
    flex-direction: column;
  }
  
  .logout-modal-footer .btn {
    width: 100%;
  }
  
  .logout-icon {
    width: 60px;
    height: 60px;
    font-size: 1.5rem;
  }
  
  .logout-title {
    font-size: 1.25rem;
  }
  
  .session-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}

/* Dark Theme */
@media (prefers-color-scheme: dark) {
  .logout-modal {
    background: #1f2937;
    color: white;
  }
  
  .logout-modal-header {
    border-bottom-color: #374151;
  }
  
  .logout-title {
    color: white;
  }
  
  .logout-message {
    color: #d1d5db;
  }
  
  .session-info {
    background: #111827;
  }
  
  .session-item {
    border-bottom-color: #374151;
  }
  
  .session-label {
    color: #9ca3af;
  }
  
  .session-value {
    color: white;
  }
}
</style>