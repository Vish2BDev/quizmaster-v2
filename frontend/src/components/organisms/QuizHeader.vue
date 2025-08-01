<template>
  <div class="qm-quiz-header" :class="headerClasses">
    <div class="qm-quiz-header-container">
      <!-- Quiz Info Section -->
      <div class="qm-quiz-header-info">
        <div class="qm-quiz-header-title">
          <h1>{{ quiz.title }}</h1>
          <QmBadge 
            v-if="quiz.difficulty"
            :variant="difficultyVariant"
            size="sm"
            class="qm-quiz-header-difficulty"
          >
            {{ quiz.difficulty }}
          </QmBadge>
        </div>
        
        <div class="qm-quiz-header-meta">
          <div class="qm-quiz-header-progress">
            <span class="qm-quiz-header-progress-text">
              Question {{ currentQuestion }} of {{ totalQuestions }}
            </span>
            <div class="qm-quiz-header-progress-bar">
              <div 
                class="qm-quiz-header-progress-fill"
                :style="{ width: `${progressPercentage}%` }"
              ></div>
            </div>
          </div>
          
          <div v-if="showTimer" class="qm-quiz-header-timer" :class="timerClasses">
            <i class="fas fa-clock"></i>
            <span class="qm-quiz-header-timer-text">{{ formattedTime }}</span>
            <div v-if="showTimerBar" class="qm-quiz-header-timer-bar">
              <div 
                class="qm-quiz-header-timer-fill"
                :style="{ width: `${timerPercentage}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Actions Section -->
      <div class="qm-quiz-header-actions">
        <QmBtn
          v-if="showPauseButton"
          variant="ghost"
          size="sm"
          icon="fas fa-pause"
          :disabled="disabled"
          @click="handlePause"
        >
          {{ isPaused ? 'Resume' : 'Pause' }}
        </QmBtn>
        
        <QmBtn
          v-if="showHelpButton"
          variant="ghost"
          size="sm"
          icon="fas fa-question-circle"
          :disabled="disabled"
          @click="handleHelp"
        >
          Help
        </QmBtn>
        
        <QmBtn
          v-if="showSettingsButton"
          variant="ghost"
          size="sm"
          icon="fas fa-cog"
          :disabled="disabled"
          @click="handleSettings"
        >
          Settings
        </QmBtn>
        
        <QmBtn
          v-if="showExitButton"
          variant="danger"
          size="sm"
          icon="fas fa-times"
          :disabled="disabled"
          @click="handleExit"
        >
          Exit Quiz
        </QmBtn>
      </div>
    </div>
    
    <!-- Warning Banner -->
    <div v-if="showWarning" class="qm-quiz-header-warning" :class="warningClasses">
      <i :class="warningIcon"></i>
      <span>{{ warningMessage }}</span>
      <QmBtn
        v-if="warningAction"
        variant="ghost"
        size="xs"
        @click="handleWarningAction"
      >
        {{ warningAction.label }}
      </QmBtn>
    </div>
  </div>
</template>

<script>
import { computed, watch, ref } from 'vue'
import QmBtn from '../atoms/QmBtn.vue'
import QmBadge from '../atoms/QmBadge.vue'

export default {
  name: 'QuizHeader',
  components: {
    QmBtn,
    QmBadge
  },
  emits: ['pause', 'help', 'settings', 'exit', 'warning-action'],
  props: {
    quiz: {
      type: Object,
      required: true
      // Expected: { title: string, difficulty?: string, duration?: number }
    },
    currentQuestion: {
      type: Number,
      required: true
    },
    totalQuestions: {
      type: Number,
      required: true
    },
    timeRemaining: {
      type: Number,
      default: null
      // Time in seconds
    },
    totalTime: {
      type: Number,
      default: null
      // Total time in seconds
    },
    isPaused: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    sticky: {
      type: Boolean,
      default: true
    },
    showTimer: {
      type: Boolean,
      default: true
    },
    showTimerBar: {
      type: Boolean,
      default: true
    },
    showPauseButton: {
      type: Boolean,
      default: true
    },
    showHelpButton: {
      type: Boolean,
      default: true
    },
    showSettingsButton: {
      type: Boolean,
      default: false
    },
    showExitButton: {
      type: Boolean,
      default: true
    },
    warningThreshold: {
      type: Number,
      default: 300
      // Show warning when time remaining is less than this (in seconds)
    },
    dangerThreshold: {
      type: Number,
      default: 60
      // Show danger state when time remaining is less than this (in seconds)
    },
    warning: {
      type: Object,
      default: null
      // Expected: { message: string, type: 'warning'|'danger'|'info', action?: { label: string, handler: function } }
    }
  },
  setup(props, { emit }) {
    const pulseAnimation = ref(false)
    
    const headerClasses = computed(() => {
      return [
        'qm-quiz-header',
        {
          'qm-quiz-header-sticky': props.sticky,
          'qm-quiz-header-paused': props.isPaused,
          'qm-quiz-header-disabled': props.disabled,
          'qm-quiz-header-warning': isWarningState.value,
          'qm-quiz-header-danger': isDangerState.value
        }
      ]
    })
    
    const difficultyVariant = computed(() => {
      if (!props.quiz.difficulty) return 'secondary'
      
      const difficulty = props.quiz.difficulty.toLowerCase()
      switch (difficulty) {
        case 'easy': return 'success'
        case 'medium': return 'warning'
        case 'hard': return 'error'
        default: return 'secondary'
      }
    })
    
    const progressPercentage = computed(() => {
      if (props.totalQuestions === 0) return 0
      return Math.min(100, (props.currentQuestion / props.totalQuestions) * 100)
    })
    
    const timerPercentage = computed(() => {
      if (!props.totalTime || props.timeRemaining === null) return 100
      return Math.max(0, (props.timeRemaining / props.totalTime) * 100)
    })
    
    const isWarningState = computed(() => {
      return props.timeRemaining !== null && 
             props.timeRemaining <= props.warningThreshold && 
             props.timeRemaining > props.dangerThreshold
    })
    
    const isDangerState = computed(() => {
      return props.timeRemaining !== null && 
             props.timeRemaining <= props.dangerThreshold
    })
    
    const timerClasses = computed(() => {
      return [
        'qm-quiz-header-timer',
        {
          'qm-quiz-header-timer-warning': isWarningState.value,
          'qm-quiz-header-timer-danger': isDangerState.value,
          'qm-quiz-header-timer-pulse': pulseAnimation.value
        }
      ]
    })
    
    const formattedTime = computed(() => {
      if (props.timeRemaining === null) return '--:--'
      
      const minutes = Math.floor(props.timeRemaining / 60)
      const seconds = props.timeRemaining % 60
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    })
    
    const showWarning = computed(() => {
      return Boolean(props.warning || isWarningState.value || isDangerState.value)
    })
    
    const warningClasses = computed(() => {
      const type = props.warning?.type || (isDangerState.value ? 'danger' : 'warning')
      return [
        'qm-quiz-header-warning',
        `qm-quiz-header-warning-${type}`
      ]
    })
    
    const warningIcon = computed(() => {
      const type = props.warning?.type || (isDangerState.value ? 'danger' : 'warning')
      switch (type) {
        case 'danger': return 'fas fa-exclamation-triangle'
        case 'warning': return 'fas fa-clock'
        case 'info': return 'fas fa-info-circle'
        default: return 'fas fa-exclamation-circle'
      }
    })
    
    const warningMessage = computed(() => {
      if (props.warning?.message) return props.warning.message
      
      if (isDangerState.value) {
        return `Only ${formattedTime.value} remaining!`
      }
      
      if (isWarningState.value) {
        return `${formattedTime.value} remaining`
      }
      
      return ''
    })
    
    const warningAction = computed(() => {
      return props.warning?.action || null
    })
    
    // Watch for danger state to trigger pulse animation
    watch(isDangerState, (newValue) => {
      if (newValue) {
        pulseAnimation.value = true
        // Reset animation after a short delay to allow re-triggering
        setTimeout(() => {
          pulseAnimation.value = false
        }, 1000)
      }
    })
    
    const handlePause = () => {
      emit('pause')
    }
    
    const handleHelp = () => {
      emit('help')
    }
    
    const handleSettings = () => {
      emit('settings')
    }
    
    const handleExit = () => {
      emit('exit')
    }
    
    const handleWarningAction = () => {
      if (props.warning?.action?.handler) {
        props.warning.action.handler()
      }
      emit('warning-action', props.warning?.action)
    }
    
    return {
      headerClasses,
      difficultyVariant,
      progressPercentage,
      timerPercentage,
      timerClasses,
      formattedTime,
      showWarning,
      warningClasses,
      warningIcon,
      warningMessage,
      warningAction,
      handlePause,
      handleHelp,
      handleSettings,
      handleExit,
      handleWarningAction
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-quiz-header {
  background: var(--qm-white);
  border-bottom: 1px solid var(--qm-light-gray);
  transition: all 0.3s ease;
  
  &.qm-quiz-header-sticky {
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  &.qm-quiz-header-paused {
    background: rgba(245, 158, 11, 0.05);
    border-bottom-color: var(--qm-warning-yellow);
  }
  
  &.qm-quiz-header-warning {
    background: rgba(245, 158, 11, 0.05);
  }
  
  &.qm-quiz-header-danger {
    background: rgba(239, 68, 68, 0.05);
    animation: qm-quiz-header-pulse 2s infinite;
  }
  
  &.qm-quiz-header-disabled {
    opacity: 0.7;
    pointer-events: none;
  }
}

.qm-quiz-header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  gap: 2rem;
}

.qm-quiz-header-info {
  flex: 1;
  min-width: 0;
}

.qm-quiz-header-title {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
  
  h1 {
    font-family: var(--qm-font-heading);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--qm-dark-gray);
    margin: 0;
    line-height: 1.2;
    
    // Truncate long titles
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.qm-quiz-header-difficulty {
  flex-shrink: 0;
}

.qm-quiz-header-meta {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.qm-quiz-header-progress {
  flex: 1;
  min-width: 200px;
}

.qm-quiz-header-progress-text {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--qm-dark-gray);
  margin-bottom: 0.5rem;
}

.qm-quiz-header-progress-bar {
  height: 6px;
  background: var(--qm-light-gray);
  border-radius: 3px;
  overflow: hidden;
}

.qm-quiz-header-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--qm-electric-blue), var(--qm-royal-purple));
  transition: width 0.3s ease;
}

.qm-quiz-header-timer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--qm-light-gray);
  border-radius: var(--qm-border-radius-lg);
  font-weight: 600;
  color: var(--qm-dark-gray);
  transition: all 0.3s ease;
  
  &.qm-quiz-header-timer-warning {
    background: rgba(245, 158, 11, 0.1);
    color: var(--qm-warning-yellow);
    border: 1px solid rgba(245, 158, 11, 0.3);
  }
  
  &.qm-quiz-header-timer-danger {
    background: rgba(239, 68, 68, 0.1);
    color: var(--qm-error-red);
    border: 1px solid rgba(239, 68, 68, 0.3);
  }
  
  &.qm-quiz-header-timer-pulse {
    animation: qm-quiz-timer-pulse 1s ease-in-out;
  }
  
  i {
    font-size: 1rem;
  }
}

.qm-quiz-header-timer-text {
  font-family: var(--qm-font-mono, 'Courier New', monospace);
  font-size: 1rem;
  min-width: 3.5rem;
  text-align: center;
}

.qm-quiz-header-timer-bar {
  width: 60px;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: hidden;
  margin-left: 0.5rem;
}

.qm-quiz-header-timer-fill {
  height: 100%;
  background: currentColor;
  transition: width 1s linear;
}

.qm-quiz-header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.qm-quiz-header-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  
  &.qm-quiz-header-warning-warning {
    background: var(--qm-warning-yellow);
    color: var(--qm-dark-gray);
  }
  
  &.qm-quiz-header-warning-danger {
    background: var(--qm-error-red);
    color: var(--qm-white);
  }
  
  &.qm-quiz-header-warning-info {
    background: var(--qm-electric-blue);
    color: var(--qm-white);
  }
  
  i {
    font-size: 1rem;
  }
}

// Animations
@keyframes qm-quiz-header-pulse {
  0%, 100% {
    background: rgba(239, 68, 68, 0.05);
  }
  50% {
    background: rgba(239, 68, 68, 0.1);
  }
}

@keyframes qm-quiz-timer-pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

// Dark mode support
[data-theme="dark"] {
  .qm-quiz-header {
    background: var(--qm-bg-surface-900, #1a1a1a);
    border-bottom-color: var(--qm-bg-surface-700, #404040);
  }
  
  .qm-quiz-header-title h1 {
    color: var(--qm-text-50, #f8fafc);
  }
  
  .qm-quiz-header-progress-text {
    color: var(--qm-text-200, #e5e7eb);
  }
  
  .qm-quiz-header-progress-bar {
    background: var(--qm-bg-surface-700, #404040);
  }
  
  .qm-quiz-header-timer {
    background: var(--qm-bg-surface-800, #2d2d2d);
    color: var(--qm-text-200, #e5e7eb);
  }
  
  .qm-quiz-header-timer-bar {
    background: rgba(255, 255, 255, 0.1);
  }
}

// Responsive design
@media (max-width: 768px) {
  .qm-quiz-header-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .qm-quiz-header-info {
    width: 100%;
  }
  
  .qm-quiz-header-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    
    h1 {
      font-size: 1.25rem;
    }
  }
  
  .qm-quiz-header-meta {
    flex-direction: column;
    gap: 1rem;
    width: 100%;
  }
  
  .qm-quiz-header-progress {
    min-width: auto;
    width: 100%;
  }
  
  .qm-quiz-header-timer {
    align-self: center;
  }
  
  .qm-quiz-header-actions {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .qm-quiz-header-warning {
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .qm-quiz-header-timer {
    padding: 0.375rem 0.75rem;
    
    .qm-quiz-header-timer-text {
      font-size: 0.875rem;
      min-width: 3rem;
    }
  }
  
  .qm-quiz-header-timer-bar {
    width: 40px;
  }
  
  .qm-quiz-header-actions {
    gap: 0.25rem;
  }
}
</style>