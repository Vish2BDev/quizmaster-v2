<template>
  <QmCard
    :variant="cardVariant"
    :size="size"
    :clickable="clickable"
    :loading="loading"
    :hover="clickable"
    class="qm-stat-card"
    @click="handleClick"
  >
    <div class="qm-stat-card-content">
      <div class="qm-stat-card-header">
        <div class="qm-stat-card-icon" :class="iconClasses">
          <i :class="icon"></i>
        </div>
        <div v-if="trend" class="qm-stat-card-trend" :class="trendClasses">
          <i :class="trendIcon"></i>
          <span>{{ formatTrend(trend) }}</span>
        </div>
      </div>
      
      <div class="qm-stat-card-body">
        <div class="qm-stat-card-value">
          <span class="qm-stat-card-number">{{ formattedValue }}</span>
          <span v-if="unit" class="qm-stat-card-unit">{{ unit }}</span>
        </div>
        <div class="qm-stat-card-label">{{ label }}</div>
        <div v-if="subtitle" class="qm-stat-card-subtitle">{{ subtitle }}</div>
      </div>
      
      <div v-if="showProgress" class="qm-stat-card-progress">
        <div class="qm-stat-card-progress-header">
          <span class="qm-stat-card-progress-label">{{ progressLabel }}</span>
          <span class="qm-stat-card-progress-value">{{ progressPercentage }}%</span>
        </div>
        <div class="qm-stat-card-progress-bar">
          <div 
            class="qm-stat-card-progress-fill"
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
      </div>
      
      <div v-if="comparison" class="qm-stat-card-comparison">
        <div class="qm-stat-card-comparison-item">
          <span class="qm-stat-card-comparison-label">{{ comparison.previousLabel || 'Previous' }}</span>
          <span class="qm-stat-card-comparison-value">{{ formatValue(comparison.previousValue) }}</span>
        </div>
        <div class="qm-stat-card-comparison-change" :class="comparisonClasses">
          <i :class="comparisonIcon"></i>
          <span>{{ formatComparison(comparison) }}</span>
        </div>
      </div>
      
      <div v-if="actions && actions.length" class="qm-stat-card-actions">
        <QmBtn
          v-for="action in actions"
          :key="action.key"
          :variant="action.variant || 'ghost'"
          :size="action.size || 'sm'"
          :icon="action.icon"
          @click.stop="handleAction(action)"
        >
          {{ action.label }}
        </QmBtn>
      </div>
    </div>
  </QmCard>
</template>

<script>
import { computed } from 'vue'
import QmCard from '../atoms/QmCard.vue'
import QmBtn from '../atoms/QmBtn.vue'

export default {
  name: 'StatCard',
  components: {
    QmCard,
    QmBtn
  },
  emits: ['click', 'action'],
  props: {
    value: {
      type: [Number, String],
      required: true
    },
    label: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      default: null
    },
    icon: {
      type: String,
      required: true
    },
    iconVariant: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'secondary', 'success', 'error', 'warning', 'info'].includes(value)
    },
    unit: {
      type: String,
      default: null
    },
    trend: {
      type: Object,
      default: null
      // Expected: { value: number, period: string }
    },
    comparison: {
      type: Object,
      default: null
      // Expected: { previousValue: number, previousLabel?: string }
    },
    progress: {
      type: Object,
      default: null
      // Expected: { current: number, total: number, label?: string }
    },
    actions: {
      type: Array,
      default: () => []
      // Expected: [{ key: string, label: string, icon?: string, variant?: string }]
    },
    size: {
      type: String,
      default: 'md'
    },
    variant: {
      type: String,
      default: 'default'
    },
    clickable: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    format: {
      type: String,
      default: 'number',
      validator: (value) => ['number', 'currency', 'percentage', 'duration', 'custom'].includes(value)
    },
    precision: {
      type: Number,
      default: 0
    }
  },
  setup(props, { emit }) {
    const cardVariant = computed(() => {
      if (props.variant !== 'default') return props.variant
      return 'elevated'
    })
    
    const iconClasses = computed(() => {
      return [
        'qm-stat-card-icon',
        `qm-stat-card-icon-${props.iconVariant}`
      ]
    })
    
    const showProgress = computed(() => {
      return props.progress && 
             typeof props.progress.current === 'number' && 
             typeof props.progress.total === 'number'
    })
    
    const progressPercentage = computed(() => {
      if (!showProgress.value) return 0
      return Math.min(100, Math.max(0, (props.progress.current / props.progress.total) * 100))
    })
    
    const progressLabel = computed(() => {
      return props.progress?.label || 'Progress'
    })
    
    const trendClasses = computed(() => {
      if (!props.trend) return []
      const isPositive = props.trend.value > 0
      const isNegative = props.trend.value < 0
      
      return [
        'qm-stat-card-trend',
        {
          'qm-stat-card-trend-positive': isPositive,
          'qm-stat-card-trend-negative': isNegative,
          'qm-stat-card-trend-neutral': !isPositive && !isNegative
        }
      ]
    })
    
    const trendIcon = computed(() => {
      if (!props.trend) return ''
      if (props.trend.value > 0) return 'fas fa-arrow-up'
      if (props.trend.value < 0) return 'fas fa-arrow-down'
      return 'fas fa-minus'
    })
    
    const comparisonClasses = computed(() => {
      if (!props.comparison) return []
      const current = typeof props.value === 'number' ? props.value : parseFloat(props.value)
      const previous = props.comparison.previousValue
      const change = current - previous
      
      return [
        'qm-stat-card-comparison-change',
        {
          'qm-stat-card-comparison-positive': change > 0,
          'qm-stat-card-comparison-negative': change < 0,
          'qm-stat-card-comparison-neutral': change === 0
        }
      ]
    })
    
    const comparisonIcon = computed(() => {
      if (!props.comparison) return ''
      const current = typeof props.value === 'number' ? props.value : parseFloat(props.value)
      const previous = props.comparison.previousValue
      const change = current - previous
      
      if (change > 0) return 'fas fa-arrow-up'
      if (change < 0) return 'fas fa-arrow-down'
      return 'fas fa-equals'
    })
    
    const formattedValue = computed(() => {
      return formatValue(props.value)
    })
    
    const formatValue = (value) => {
      if (value === null || value === undefined) return '—'
      
      const numValue = typeof value === 'number' ? value : parseFloat(value)
      if (isNaN(numValue)) return value.toString()
      
      switch (props.format) {
        case 'currency':
          return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: props.precision,
            maximumFractionDigits: props.precision
          }).format(numValue)
          
        case 'percentage':
          return `${numValue.toFixed(props.precision)}%`
          
        case 'duration':
          return formatDuration(numValue)
          
        case 'number':
        default:
          if (numValue >= 1000000) {
            return `${(numValue / 1000000).toFixed(1)}M`
          }
          if (numValue >= 1000) {
            return `${(numValue / 1000).toFixed(1)}K`
          }
          return numValue.toFixed(props.precision)
      }
    }
    
    const formatDuration = (minutes) => {
      if (minutes < 60) return `${minutes}m`
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
    }
    
    const formatTrend = (trend) => {
      if (!trend) return ''
      const absValue = Math.abs(trend.value)
      const formatted = absValue.toFixed(1)
      const period = trend.period ? ` ${trend.period}` : ''
      return `${formatted}%${period}`
    }
    
    const formatComparison = (comparison) => {
      if (!comparison) return ''
      const current = typeof props.value === 'number' ? props.value : parseFloat(props.value)
      const previous = comparison.previousValue
      const change = current - previous
      const percentage = previous !== 0 ? Math.abs((change / previous) * 100) : 0
      
      return `${percentage.toFixed(1)}%`
    }
    
    const handleClick = () => {
      if (props.clickable) {
        emit('click')
      }
    }
    
    const handleAction = (action) => {
      emit('action', action)
    }
    
    return {
      cardVariant,
      iconClasses,
      showProgress,
      progressPercentage,
      progressLabel,
      trendClasses,
      trendIcon,
      comparisonClasses,
      comparisonIcon,
      formattedValue,
      formatValue,
      formatTrend,
      formatComparison,
      handleClick,
      handleAction
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-stat-card {
  height: 100%;
}

.qm-stat-card-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

.qm-stat-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.qm-stat-card-icon {
  width: 3rem;
  height: 3rem;
  border-radius: var(--qm-border-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  
  &.qm-stat-card-icon-primary {
    background: linear-gradient(135deg, var(--qm-electric-blue), rgba(14, 165, 233, 0.8));
    color: var(--qm-white);
  }
  
  &.qm-stat-card-icon-secondary {
    background: linear-gradient(135deg, var(--qm-royal-purple), rgba(147, 51, 234, 0.8));
    color: var(--qm-white);
  }
  
  &.qm-stat-card-icon-success {
    background: linear-gradient(135deg, var(--qm-success-green), rgba(34, 197, 94, 0.8));
    color: var(--qm-white);
  }
  
  &.qm-stat-card-icon-error {
    background: linear-gradient(135deg, var(--qm-error-red), rgba(239, 68, 68, 0.8));
    color: var(--qm-white);
  }
  
  &.qm-stat-card-icon-warning {
    background: linear-gradient(135deg, var(--qm-warning-yellow), rgba(245, 158, 11, 0.8));
    color: var(--qm-dark-gray);
  }
  
  &.qm-stat-card-icon-info {
    background: linear-gradient(135deg, var(--qm-electric-blue), rgba(59, 130, 246, 0.8));
    color: var(--qm-white);
  }
}

.qm-stat-card-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: var(--qm-border-radius);
  
  &.qm-stat-card-trend-positive {
    background: rgba(34, 197, 94, 0.1);
    color: var(--qm-success-green);
  }
  
  &.qm-stat-card-trend-negative {
    background: rgba(239, 68, 68, 0.1);
    color: var(--qm-error-red);
  }
  
  &.qm-stat-card-trend-neutral {
    background: rgba(107, 114, 128, 0.1);
    color: var(--qm-medium-gray);
  }
}

.qm-stat-card-body {
  flex: 1;
}

.qm-stat-card-value {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.qm-stat-card-number {
  font-family: var(--qm-font-heading);
  font-size: 2rem;
  font-weight: 700;
  color: var(--qm-dark-gray);
  line-height: 1;
}

.qm-stat-card-unit {
  font-size: 1rem;
  font-weight: 500;
  color: var(--qm-medium-gray);
}

.qm-stat-card-label {
  font-family: var(--qm-font-body);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--qm-dark-gray);
  margin-bottom: 0.25rem;
}

.qm-stat-card-subtitle {
  font-size: 0.75rem;
  color: var(--qm-medium-gray);
  line-height: 1.4;
}

.qm-stat-card-progress {
  padding: 0.75rem;
  background: var(--qm-light-gray);
  border-radius: var(--qm-border-radius);
}

.qm-stat-card-progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.qm-stat-card-progress-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--qm-dark-gray);
}

.qm-stat-card-progress-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--qm-electric-blue);
}

.qm-stat-card-progress-bar {
  height: 4px;
  background: var(--qm-white);
  border-radius: 2px;
  overflow: hidden;
}

.qm-stat-card-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--qm-electric-blue), var(--qm-royal-purple));
  transition: width 0.3s ease;
}

.qm-stat-card-comparison {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: var(--qm-light-gray);
  border-radius: var(--qm-border-radius);
  font-size: 0.75rem;
}

.qm-stat-card-comparison-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.qm-stat-card-comparison-label {
  color: var(--qm-medium-gray);
  font-weight: 500;
}

.qm-stat-card-comparison-value {
  color: var(--qm-dark-gray);
  font-weight: 600;
}

.qm-stat-card-comparison-change {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 600;
  
  &.qm-stat-card-comparison-positive {
    color: var(--qm-success-green);
  }
  
  &.qm-stat-card-comparison-negative {
    color: var(--qm-error-red);
  }
  
  &.qm-stat-card-comparison-neutral {
    color: var(--qm-medium-gray);
  }
}

.qm-stat-card-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

// Dark mode support
[data-theme="dark"] {
  .qm-stat-card-number {
    color: var(--qm-text-50, #f8fafc);
  }
  
  .qm-stat-card-label {
    color: var(--qm-text-200, #e5e7eb);
  }
  
  .qm-stat-card-subtitle {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-stat-card-unit {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-stat-card-progress {
    background: var(--qm-bg-surface-800, #2d2d2d);
  }
  
  .qm-stat-card-progress-label {
    color: var(--qm-text-200, #e5e7eb);
  }
  
  .qm-stat-card-progress-bar {
    background: var(--qm-bg-surface-700, #404040);
  }
  
  .qm-stat-card-comparison {
    background: var(--qm-bg-surface-800, #2d2d2d);
  }
  
  .qm-stat-card-comparison-label {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-stat-card-comparison-value {
    color: var(--qm-text-200, #e5e7eb);
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .qm-stat-card-number {
    font-size: 1.75rem;
  }
  
  .qm-stat-card-icon {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1.25rem;
  }
  
  .qm-stat-card-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
  }
  
  .qm-stat-card-trend {
    align-self: flex-end;
  }
}
</style>