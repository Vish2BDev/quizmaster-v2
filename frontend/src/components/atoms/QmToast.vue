<template>
  <Transition
    name="qm-toast"
    @enter="onEnter"
    @leave="onLeave"
  >
    <div
      v-if="visible"
      :class="toastClasses"
      role="alert"
      :aria-live="type === 'error' ? 'assertive' : 'polite'"
      @click="handleClick"
    >
      <div class="qm-toast-icon">
        <i :class="iconClass"></i>
      </div>
      
      <div class="qm-toast-content">
        <div v-if="title" class="qm-toast-title">{{ title }}</div>
        <div class="qm-toast-message">{{ message }}</div>
      </div>
      
      <button
        v-if="closable"
        class="qm-toast-close"
        @click.stop="close"
        :aria-label="'Close notification'"
      >
        <i class="fas fa-times"></i>
      </button>
      
      <div v-if="showProgress" class="qm-toast-progress">
        <div 
          class="qm-toast-progress-bar"
          :style="{ width: `${progressWidth}%` }"
        ></div>
      </div>
    </div>
  </Transition>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'QmToast',
  emits: ['close', 'click'],
  props: {
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
    },
    title: {
      type: String,
      default: null
    },
    message: {
      type: String,
      required: true
    },
    duration: {
      type: Number,
      default: 5000
    },
    closable: {
      type: Boolean,
      default: true
    },
    clickable: {
      type: Boolean,
      default: false
    },
    showProgress: {
      type: Boolean,
      default: true
    },
    persistent: {
      type: Boolean,
      default: false
    },
    position: {
      type: String,
      default: 'top-right',
      validator: (value) => [
        'top-left', 'top-center', 'top-right',
        'bottom-left', 'bottom-center', 'bottom-right'
      ].includes(value)
    }
  },
  setup(props, { emit }) {
    const visible = ref(true)
    const progressWidth = ref(100)
    let timer = null
    let progressTimer = null
    
    const toastClasses = computed(() => {
      return [
        'qm-toast',
        `qm-toast-${props.type}`,
        `qm-toast-${props.position}`,
        {
          'qm-toast-clickable': props.clickable,
          'qm-toast-with-title': props.title
        }
      ]
    })
    
    const iconClass = computed(() => {
      const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
      }
      return icons[props.type]
    })
    
    const startTimer = () => {
      if (!props.persistent && props.duration > 0) {
        timer = setTimeout(() => {
          close()
        }, props.duration)
        
        if (props.showProgress) {
          startProgressTimer()
        }
      }
    }
    
    const startProgressTimer = () => {
      const interval = 50
      const steps = props.duration / interval
      const decrement = 100 / steps
      
      progressTimer = setInterval(() => {
        progressWidth.value -= decrement
        if (progressWidth.value <= 0) {
          clearInterval(progressTimer)
        }
      }, interval)
    }
    
    const pauseTimer = () => {
      if (timer) {
        clearTimeout(timer)
        timer = null
      }
      if (progressTimer) {
        clearInterval(progressTimer)
        progressTimer = null
      }
    }
    
    const resumeTimer = () => {
      if (!props.persistent && props.duration > 0) {
        const remainingTime = (progressWidth.value / 100) * props.duration
        timer = setTimeout(() => {
          close()
        }, remainingTime)
        
        if (props.showProgress) {
          const interval = 50
          const steps = remainingTime / interval
          const decrement = progressWidth.value / steps
          
          progressTimer = setInterval(() => {
            progressWidth.value -= decrement
            if (progressWidth.value <= 0) {
              clearInterval(progressTimer)
            }
          }, interval)
        }
      }
    }
    
    const close = () => {
      visible.value = false
      pauseTimer()
      emit('close')
    }
    
    const handleClick = () => {
      if (props.clickable) {
        emit('click')
      }
    }
    
    const onEnter = (el) => {
      startTimer()
    }
    
    const onLeave = (el) => {
      pauseTimer()
    }
    
    onMounted(() => {
      startTimer()
    })
    
    onUnmounted(() => {
      pauseTimer()
    })
    
    return {
      visible,
      progressWidth,
      toastClasses,
      iconClass,
      close,
      handleClick,
      onEnter,
      onLeave,
      pauseTimer,
      resumeTimer
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-toast {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  min-width: 300px;
  max-width: 500px;
  padding: 1rem;
  background: var(--qm-white);
  border-radius: var(--qm-border-radius-lg);
  box-shadow: var(--qm-shadow-xl);
  border-left: 4px solid;
  font-family: var(--qm-font-body);
  cursor: default;
  overflow: hidden;
  
  // Type variants
  &.qm-toast-success {
    border-left-color: var(--qm-success-green);
    
    .qm-toast-icon {
      color: var(--qm-success-green);
    }
    
    .qm-toast-progress-bar {
      background: var(--qm-success-green);
    }
  }
  
  &.qm-toast-error {
    border-left-color: var(--qm-error-red);
    
    .qm-toast-icon {
      color: var(--qm-error-red);
    }
    
    .qm-toast-progress-bar {
      background: var(--qm-error-red);
    }
  }
  
  &.qm-toast-warning {
    border-left-color: var(--qm-warning-yellow);
    
    .qm-toast-icon {
      color: var(--qm-warning-yellow);
    }
    
    .qm-toast-progress-bar {
      background: var(--qm-warning-yellow);
    }
  }
  
  &.qm-toast-info {
    border-left-color: var(--qm-electric-blue);
    
    .qm-toast-icon {
      color: var(--qm-electric-blue);
    }
    
    .qm-toast-progress-bar {
      background: var(--qm-electric-blue);
    }
  }
  
  &.qm-toast-clickable {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: var(--qm-shadow-2xl);
    }
  }
}

.qm-toast-icon {
  flex-shrink: 0;
  font-size: 1.25rem;
  margin-top: 0.125rem;
}

.qm-toast-content {
  flex: 1;
  min-width: 0;
}

.qm-toast-title {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--qm-dark-gray);
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.qm-toast-message {
  font-size: 0.875rem;
  color: var(--qm-medium-gray);
  line-height: 1.4;
  word-wrap: break-word;
}

.qm-toast-close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: var(--qm-medium-gray);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: var(--qm-border-radius);
  transition: var(--qm-transition);
  
  &:hover {
    background: var(--qm-light-gray);
    color: var(--qm-dark-gray);
  }
  
  &:focus {
    outline: 2px solid var(--qm-electric-blue);
    outline-offset: 2px;
  }
}

.qm-toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(0, 0, 0, 0.1);
}

.qm-toast-progress-bar {
  height: 100%;
  transition: width 50ms linear;
  border-radius: 0 0 var(--qm-border-radius-lg) var(--qm-border-radius-lg);
}

// Transition animations
.qm-toast-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.qm-toast-leave-active {
  transition: all 0.2s ease-in;
}

.qm-toast-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.qm-toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

// Position variants for container
.qm-toast-top-right {
  .qm-toast-enter-from,
  .qm-toast-leave-to {
    transform: translateX(100%) scale(0.8);
  }
}

.qm-toast-top-left {
  .qm-toast-enter-from,
  .qm-toast-leave-to {
    transform: translateX(-100%) scale(0.8);
  }
}

.qm-toast-top-center,
.qm-toast-bottom-center {
  .qm-toast-enter-from,
  .qm-toast-leave-to {
    transform: translateY(-100%) scale(0.8);
  }
}

.qm-toast-bottom-left {
  .qm-toast-enter-from,
  .qm-toast-leave-to {
    transform: translateX(-100%) scale(0.8);
  }
}

.qm-toast-bottom-right {
  .qm-toast-enter-from,
  .qm-toast-leave-to {
    transform: translateX(100%) scale(0.8);
  }
}

// Dark mode support
[data-theme="dark"] {
  .qm-toast {
    background: var(--qm-bg-surface-900, #1e1e1e);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
  }
  
  .qm-toast-title {
    color: var(--qm-text-50, #f8fafc);
  }
  
  .qm-toast-message {
    color: var(--qm-text-300, #d1d5db);
  }
  
  .qm-toast-close {
    color: var(--qm-text-400, #9ca3af);
    
    &:hover {
      background: var(--qm-bg-surface-800, #2d2d2d);
      color: var(--qm-text-200, #e5e7eb);
    }
  }
  
  .qm-toast-progress {
    background: rgba(255, 255, 255, 0.1);
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .qm-toast {
    min-width: 280px;
    max-width: calc(100vw - 2rem);
    margin: 0 1rem;
  }
}
</style>