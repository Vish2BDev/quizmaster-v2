// ============================================================================
// QUIZ MASTER V2 - TOAST NOTIFICATION SYSTEM
// ============================================================================
// Global toast notification composable using Vue 3 Composition API
// Provides a centralized way to show toast notifications throughout the app

import { ref, reactive, nextTick } from 'vue'

// Global toast state
const toasts = ref([])
const toastId = ref(0)

// Default configuration
const defaultConfig = {
  duration: 5000,
  position: 'top-right',
  closable: true,
  clickable: false,
  persistent: false,
  showProgress: true,
  maxToasts: 5,
  pauseOnHover: true
}

// Toast positions
const POSITIONS = {
  'top-left': 'top-left',
  'top-center': 'top-center', 
  'top-right': 'top-right',
  'bottom-left': 'bottom-left',
  'bottom-center': 'bottom-center',
  'bottom-right': 'bottom-right'
}

// Toast types
const TYPES = {
  success: 'success',
  error: 'error',
  warning: 'warning',
  info: 'info'
}

export function useToast() {
  
  /**
   * Add a new toast notification
   * @param {Object} options - Toast configuration
   * @param {string} options.type - Toast type (success, error, warning, info)
   * @param {string} options.title - Toast title
   * @param {string} options.message - Toast message
   * @param {number} options.duration - Duration in milliseconds (0 for persistent)
   * @param {string} options.position - Toast position
   * @param {boolean} options.closable - Whether toast can be closed manually
   * @param {boolean} options.clickable - Whether toast is clickable
   * @param {boolean} options.persistent - Whether toast persists until manually closed
   * @param {boolean} options.showProgress - Whether to show progress bar
   * @param {string} options.icon - Custom icon (optional)
   * @param {Function} options.onClick - Click handler
   * @param {Function} options.onClose - Close handler
   * @returns {number} Toast ID
   */
  const addToast = (options = {}) => {
    const id = ++toastId.value
    
    // Merge with defaults
    const toast = {
      id,
      type: options.type || 'info',
      title: options.title || '',
      message: options.message || '',
      duration: options.persistent ? 0 : (options.duration ?? defaultConfig.duration),
      position: options.position || defaultConfig.position,
      closable: options.closable ?? defaultConfig.closable,
      clickable: options.clickable ?? defaultConfig.clickable,
      persistent: options.persistent ?? defaultConfig.persistent,
      showProgress: options.showProgress ?? defaultConfig.showProgress,
      pauseOnHover: options.pauseOnHover ?? defaultConfig.pauseOnHover,
      icon: options.icon,
      onClick: options.onClick,
      onClose: options.onClose,
      createdAt: Date.now(),
      timeoutId: null,
      progress: 100,
      paused: false
    }
    
    // Add to toasts array
    toasts.value.push(toast)
    
    // Limit number of toasts
    if (toasts.value.length > defaultConfig.maxToasts) {
      const oldestToast = toasts.value.shift()
      if (oldestToast?.timeoutId) {
        clearTimeout(oldestToast.timeoutId)
      }
    }
    
    // Auto-remove after duration (if not persistent)
    if (toast.duration > 0) {
      startToastTimer(toast)
    }
    
    return id
  }
  
  /**
   * Start the auto-remove timer for a toast
   * @param {Object} toast - Toast object
   */
  const startToastTimer = (toast) => {
    if (toast.duration <= 0) return
    
    const startTime = Date.now()
    const updateInterval = 50 // Update progress every 50ms
    
    const updateProgress = () => {
      if (toast.paused) {
        // If paused, restart the timer
        setTimeout(updateProgress, updateInterval)
        return
      }
      
      const elapsed = Date.now() - startTime
      const remaining = Math.max(0, toast.duration - elapsed)
      toast.progress = (remaining / toast.duration) * 100
      
      if (remaining <= 0) {
        removeToast(toast.id)
      } else {
        setTimeout(updateProgress, updateInterval)
      }
    }
    
    updateProgress()
  }
  
  /**
   * Remove a toast by ID
   * @param {number} id - Toast ID
   */
  const removeToast = (id) => {
    const index = toasts.value.findIndex(toast => toast.id === id)
    if (index > -1) {
      const toast = toasts.value[index]
      
      // Call onClose callback
      if (toast.onClose) {
        toast.onClose(toast)
      }
      
      // Clear timeout
      if (toast.timeoutId) {
        clearTimeout(toast.timeoutId)
      }
      
      // Remove from array
      toasts.value.splice(index, 1)
    }
  }
  
  /**
   * Clear all toasts
   */
  const clearAllToasts = () => {
    toasts.value.forEach(toast => {
      if (toast.timeoutId) {
        clearTimeout(toast.timeoutId)
      }
      if (toast.onClose) {
        toast.onClose(toast)
      }
    })
    toasts.value = []
  }
  
  /**
   * Pause a toast (stops auto-removal timer)
   * @param {number} id - Toast ID
   */
  const pauseToast = (id) => {
    const toast = toasts.value.find(t => t.id === id)
    if (toast) {
      toast.paused = true
    }
  }
  
  /**
   * Resume a toast (restarts auto-removal timer)
   * @param {number} id - Toast ID
   */
  const resumeToast = (id) => {
    const toast = toasts.value.find(t => t.id === id)
    if (toast) {
      toast.paused = false
    }
  }
  
  /**
   * Handle toast click
   * @param {Object} toast - Toast object
   */
  const handleToastClick = (toast) => {
    if (toast.clickable && toast.onClick) {
      toast.onClick(toast)
    }
  }
  
  /**
   * Get toasts by position
   * @param {string} position - Toast position
   * @returns {Array} Filtered toasts
   */
  const getToastsByPosition = (position) => {
    return toasts.value.filter(toast => toast.position === position)
  }
  
  // Convenience methods for different toast types
  const success = (message, options = {}) => {
    return addToast({
      type: 'success',
      message,
      title: options.title || 'Success',
      ...options
    })
  }
  
  const error = (message, options = {}) => {
    return addToast({
      type: 'error',
      message,
      title: options.title || 'Error',
      duration: options.duration ?? 8000, // Longer duration for errors
      ...options
    })
  }
  
  const warning = (message, options = {}) => {
    return addToast({
      type: 'warning',
      message,
      title: options.title || 'Warning',
      ...options
    })
  }
  
  const info = (message, options = {}) => {
    return addToast({
      type: 'info',
      message,
      title: options.title || 'Info',
      ...options
    })
  }
  
  // Quiz-specific convenience methods
  const quizStarted = (quizTitle) => {
    return success(`Quiz "${quizTitle}" started!`, {
      title: 'Quiz Started',
      icon: '🎯'
    })
  }
  
  const quizCompleted = (score, total) => {
    const percentage = Math.round((score / total) * 100)
    return success(`Quiz completed! Score: ${score}/${total} (${percentage}%)`, {
      title: 'Quiz Completed',
      icon: '🎉',
      duration: 8000
    })
  }
  
  const quizSaved = () => {
    return success('Quiz saved successfully!', {
      title: 'Saved',
      icon: '💾'
    })
  }
  
  const exportReady = (filename) => {
    return info(`Export ready: ${filename}`, {
      title: 'Export Complete',
      icon: '📊',
      clickable: true,
      onClick: () => {
        // Could trigger download here
        console.log('Download triggered for:', filename)
      }
    })
  }
  
  const networkError = () => {
    return error('Network connection lost. Please check your internet connection.', {
      title: 'Connection Error',
      icon: '🌐',
      persistent: true
    })
  }
  
  return {
    // State
    toasts: toasts.value,
    
    // Core methods
    addToast,
    removeToast,
    clearAllToasts,
    pauseToast,
    resumeToast,
    handleToastClick,
    getToastsByPosition,
    
    // Type-specific methods
    success,
    error,
    warning,
    info,
    
    // Quiz-specific methods
    quizStarted,
    quizCompleted,
    quizSaved,
    exportReady,
    networkError,
    
    // Constants
    POSITIONS,
    TYPES
  }
}

// Global toast instance for use outside of components
export const toast = {
  success: (message, options) => {
    const { success } = useToast()
    return success(message, options)
  },
  error: (message, options) => {
    const { error } = useToast()
    return error(message, options)
  },
  warning: (message, options) => {
    const { warning } = useToast()
    return warning(message, options)
  },
  info: (message, options) => {
    const { info } = useToast()
    return info(message, options)
  },
  clear: () => {
    const { clearAllToasts } = useToast()
    return clearAllToasts()
  }
}