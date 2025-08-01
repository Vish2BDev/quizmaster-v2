<template>
  <div class="qm-dashboard-stats" :class="statsClasses">
    <div class="qm-dashboard-stats-header" v-if="showHeader">
      <div class="qm-dashboard-stats-title">
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="subtitle" class="qm-dashboard-stats-subtitle">{{ subtitle }}</p>
      </div>
      
      <div class="qm-dashboard-stats-actions" v-if="actions && actions.length">
        <QmBtn
          v-for="action in actions"
          :key="action.key"
          :variant="action.variant || 'ghost'"
          :size="action.size || 'sm'"
          :icon="action.icon"
          @click="handleAction(action)"
        >
          {{ action.label }}
        </QmBtn>
      </div>
    </div>
    
    <div class="qm-dashboard-stats-grid" :class="gridClasses">
      <StatCard
        v-for="stat in processedStats"
        :key="stat.key"
        :value="stat.value"
        :label="stat.label"
        :subtitle="stat.subtitle"
        :icon="stat.icon"
        :icon-variant="stat.iconVariant || 'primary'"
        :unit="stat.unit"
        :trend="stat.trend"
        :comparison="stat.comparison"
        :progress="stat.progress"
        :actions="stat.actions"
        :size="stat.size || size"
        :variant="stat.variant || 'elevated'"
        :clickable="stat.clickable"
        :loading="stat.loading || loading"
        :format="stat.format || 'number'"
        :precision="stat.precision || 0"
        @click="handleStatClick(stat)"
        @action="handleStatAction(stat, $event)"
      />
    </div>
    
    <div v-if="showFooter" class="qm-dashboard-stats-footer">
      <div class="qm-dashboard-stats-summary">
        <span class="qm-dashboard-stats-summary-text">{{ summaryText }}</span>
        <QmBadge
          v-if="summaryBadge"
          :variant="summaryBadge.variant || 'secondary'"
          :size="summaryBadge.size || 'sm'"
        >
          {{ summaryBadge.text }}
        </QmBadge>
      </div>
      
      <div class="qm-dashboard-stats-meta" v-if="lastUpdated">
        <i class="fas fa-clock"></i>
        <span>Last updated {{ formatLastUpdated(lastUpdated) }}</span>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="qm-dashboard-stats-loading">
      <div class="qm-dashboard-stats-skeleton" v-for="n in skeletonCount" :key="n">
        <div class="qm-dashboard-stats-skeleton-icon"></div>
        <div class="qm-dashboard-stats-skeleton-content">
          <div class="qm-dashboard-stats-skeleton-line qm-dashboard-stats-skeleton-line-short"></div>
          <div class="qm-dashboard-stats-skeleton-line qm-dashboard-stats-skeleton-line-long"></div>
          <div class="qm-dashboard-stats-skeleton-line qm-dashboard-stats-skeleton-line-medium"></div>
        </div>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="showEmptyState" class="qm-dashboard-stats-empty">
      <div class="qm-dashboard-stats-empty-icon">
        <i :class="emptyIcon"></i>
      </div>
      <h3 class="qm-dashboard-stats-empty-title">{{ emptyTitle }}</h3>
      <p class="qm-dashboard-stats-empty-message">{{ emptyMessage }}</p>
      <QmBtn
        v-if="emptyAction"
        :variant="emptyAction.variant || 'primary'"
        :icon="emptyAction.icon"
        @click="handleEmptyAction"
      >
        {{ emptyAction.label }}
      </QmBtn>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { StatCard } from '../molecules'
import QmBtn from '../atoms/QmBtn.vue'
import QmBadge from '../atoms/QmBadge.vue'

export default {
  name: 'DashboardStats',
  components: {
    StatCard,
    QmBtn,
    QmBadge
  },
  emits: ['action', 'stat-click', 'stat-action', 'empty-action'],
  props: {
    stats: {
      type: Array,
      default: () => []
      // Expected: [{ key: string, value: number|string, label: string, icon: string, ... }]
    },
    title: {
      type: String,
      default: null
    },
    subtitle: {
      type: String,
      default: null
    },
    actions: {
      type: Array,
      default: () => []
      // Expected: [{ key: string, label: string, icon?: string, variant?: string }]
    },
    columns: {
      type: [Number, String],
      default: 'auto'
      // 'auto', 1, 2, 3, 4, 5, 6
    },
    size: {
      type: String,
      default: 'md'
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    },
    lastUpdated: {
      type: [Date, String, Number],
      default: null
    },
    summaryText: {
      type: String,
      default: null
    },
    summaryBadge: {
      type: Object,
      default: null
      // Expected: { text: string, variant?: string, size?: string }
    },
    emptyTitle: {
      type: String,
      default: 'No Statistics Available'
    },
    emptyMessage: {
      type: String,
      default: 'There are no statistics to display at this time.'
    },
    emptyIcon: {
      type: String,
      default: 'fas fa-chart-bar'
    },
    emptyAction: {
      type: Object,
      default: null
      // Expected: { label: string, icon?: string, variant?: string }
    },
    responsive: {
      type: Boolean,
      default: true
    },
    animated: {
      type: Boolean,
      default: true
    }
  },
  setup(props, { emit }) {
    const statsClasses = computed(() => {
      return [
        'qm-dashboard-stats',
        {
          'qm-dashboard-stats-loading': props.loading,
          'qm-dashboard-stats-error': props.error,
          'qm-dashboard-stats-responsive': props.responsive,
          'qm-dashboard-stats-animated': props.animated
        }
      ]
    })
    
    const gridClasses = computed(() => {
      const classes = ['qm-dashboard-stats-grid']
      
      if (props.columns === 'auto') {
        classes.push('qm-dashboard-stats-grid-auto')
      } else if (typeof props.columns === 'number') {
        classes.push(`qm-dashboard-stats-grid-${props.columns}`)
      }
      
      return classes
    })
    
    const showHeader = computed(() => {
      return props.title || props.subtitle || (props.actions && props.actions.length)
    })
    
    const showFooter = computed(() => {
      return props.summaryText || props.summaryBadge || props.lastUpdated
    })
    
    const showEmptyState = computed(() => {
      return !props.loading && !props.error && (!props.stats || props.stats.length === 0)
    })
    
    const skeletonCount = computed(() => {
      if (props.columns === 'auto') return 4
      if (typeof props.columns === 'number') return props.columns
      return 4
    })
    
    const processedStats = computed(() => {
      return props.stats.map((stat, index) => {
        return {
          ...stat,
          key: stat.key || `stat-${index}`,
          // Add default values if not provided
          iconVariant: stat.iconVariant || getDefaultIconVariant(stat.label, index),
          // Add animation delay for staggered loading
          animationDelay: props.animated ? `${index * 100}ms` : '0ms'
        }
      })
    })
    
    const getDefaultIconVariant = (label, index) => {
      const variants = ['primary', 'secondary', 'success', 'warning', 'info']
      
      // Try to determine variant based on label content
      const labelLower = label?.toLowerCase() || ''
      
      if (labelLower.includes('success') || labelLower.includes('complete') || labelLower.includes('pass')) {
        return 'success'
      }
      if (labelLower.includes('error') || labelLower.includes('fail') || labelLower.includes('issue')) {
        return 'error'
      }
      if (labelLower.includes('warning') || labelLower.includes('pending') || labelLower.includes('review')) {
        return 'warning'
      }
      if (labelLower.includes('info') || labelLower.includes('total') || labelLower.includes('count')) {
        return 'info'
      }
      
      // Fallback to cycling through variants
      return variants[index % variants.length]
    }
    
    const formatLastUpdated = (timestamp) => {
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)
      
      if (diffMins < 1) return 'just now'
      if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
      if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
      
      return date.toLocaleDateString()
    }
    
    const handleAction = (action) => {
      emit('action', action)
    }
    
    const handleStatClick = (stat) => {
      if (stat.clickable) {
        emit('stat-click', stat)
      }
    }
    
    const handleStatAction = (stat, action) => {
      emit('stat-action', { stat, action })
    }
    
    const handleEmptyAction = () => {
      emit('empty-action', props.emptyAction)
    }
    
    return {
      statsClasses,
      gridClasses,
      showHeader,
      showFooter,
      showEmptyState,
      skeletonCount,
      processedStats,
      formatLastUpdated,
      handleAction,
      handleStatClick,
      handleStatAction,
      handleEmptyAction
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-dashboard-stats {
  width: 100%;
}

.qm-dashboard-stats-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.qm-dashboard-stats-title {
  flex: 1;
  
  h2 {
    font-family: var(--qm-font-heading);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--qm-dark-gray);
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
  }
}

.qm-dashboard-stats-subtitle {
  font-size: 0.875rem;
  color: var(--qm-medium-gray);
  margin: 0;
  line-height: 1.4;
}

.qm-dashboard-stats-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.qm-dashboard-stats-grid {
  display: grid;
  gap: 1.5rem;
  
  &.qm-dashboard-stats-grid-auto {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
  
  &.qm-dashboard-stats-grid-1 {
    grid-template-columns: 1fr;
  }
  
  &.qm-dashboard-stats-grid-2 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  &.qm-dashboard-stats-grid-3 {
    grid-template-columns: repeat(3, 1fr);
  }
  
  &.qm-dashboard-stats-grid-4 {
    grid-template-columns: repeat(4, 1fr);
  }
  
  &.qm-dashboard-stats-grid-5 {
    grid-template-columns: repeat(5, 1fr);
  }
  
  &.qm-dashboard-stats-grid-6 {
    grid-template-columns: repeat(6, 1fr);
  }
}

.qm-dashboard-stats-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--qm-light-gray);
  gap: 1rem;
}

.qm-dashboard-stats-summary {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.qm-dashboard-stats-summary-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--qm-dark-gray);
}

.qm-dashboard-stats-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--qm-medium-gray);
  
  i {
    font-size: 0.875rem;
  }
}

// Loading State
.qm-dashboard-stats-loading {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.qm-dashboard-stats-skeleton {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--qm-white);
  border-radius: var(--qm-border-radius-lg);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.qm-dashboard-stats-skeleton-icon {
  width: 3rem;
  height: 3rem;
  background: var(--qm-light-gray);
  border-radius: var(--qm-border-radius-lg);
  animation: qm-skeleton-pulse 1.5s ease-in-out infinite;
}

.qm-dashboard-stats-skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.qm-dashboard-stats-skeleton-line {
  height: 1rem;
  background: var(--qm-light-gray);
  border-radius: var(--qm-border-radius);
  animation: qm-skeleton-pulse 1.5s ease-in-out infinite;
  
  &.qm-dashboard-stats-skeleton-line-short {
    width: 60%;
  }
  
  &.qm-dashboard-stats-skeleton-line-medium {
    width: 80%;
  }
  
  &.qm-dashboard-stats-skeleton-line-long {
    width: 100%;
  }
}

// Empty State
.qm-dashboard-stats-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  text-align: center;
  background: var(--qm-white);
  border-radius: var(--qm-border-radius-lg);
  border: 2px dashed var(--qm-light-gray);
}

.qm-dashboard-stats-empty-icon {
  width: 4rem;
  height: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--qm-light-gray);
  border-radius: 50%;
  margin-bottom: 1rem;
  
  i {
    font-size: 2rem;
    color: var(--qm-medium-gray);
  }
}

.qm-dashboard-stats-empty-title {
  font-family: var(--qm-font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--qm-dark-gray);
  margin: 0 0 0.5rem 0;
}

.qm-dashboard-stats-empty-message {
  font-size: 0.875rem;
  color: var(--qm-medium-gray);
  margin: 0 0 1.5rem 0;
  line-height: 1.4;
  max-width: 400px;
}

// Animations
@keyframes qm-skeleton-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.qm-dashboard-stats-animated {
  .qm-dashboard-stats-grid > * {
    animation: qm-stats-fade-in 0.6s ease-out forwards;
    opacity: 0;
    transform: translateY(20px);
  }
}

@keyframes qm-stats-fade-in {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Dark mode support
[data-theme="dark"] {
  .qm-dashboard-stats-title h2 {
    color: var(--qm-text-50, #f8fafc);
  }
  
  .qm-dashboard-stats-subtitle {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-dashboard-stats-footer {
    border-top-color: var(--qm-bg-surface-700, #404040);
  }
  
  .qm-dashboard-stats-summary-text {
    color: var(--qm-text-200, #e5e7eb);
  }
  
  .qm-dashboard-stats-meta {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-dashboard-stats-skeleton {
    background: var(--qm-bg-surface-800, #2d2d2d);
  }
  
  .qm-dashboard-stats-skeleton-icon,
  .qm-dashboard-stats-skeleton-line {
    background: var(--qm-bg-surface-700, #404040);
  }
  
  .qm-dashboard-stats-empty {
    background: var(--qm-bg-surface-800, #2d2d2d);
    border-color: var(--qm-bg-surface-600, #525252);
  }
  
  .qm-dashboard-stats-empty-icon {
    background: var(--qm-bg-surface-700, #404040);
    
    i {
      color: var(--qm-text-400, #9ca3af);
    }
  }
  
  .qm-dashboard-stats-empty-title {
    color: var(--qm-text-200, #e5e7eb);
  }
  
  .qm-dashboard-stats-empty-message {
    color: var(--qm-text-400, #9ca3af);
  }
}

// Responsive design
@media (max-width: 1024px) {
  .qm-dashboard-stats-grid {
    &.qm-dashboard-stats-grid-auto {
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    }
    
    &.qm-dashboard-stats-grid-4,
    &.qm-dashboard-stats-grid-5,
    &.qm-dashboard-stats-grid-6 {
      grid-template-columns: repeat(3, 1fr);
    }
  }
}

@media (max-width: 768px) {
  .qm-dashboard-stats-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .qm-dashboard-stats-actions {
    justify-content: flex-start;
  }
  
  .qm-dashboard-stats-grid {
    gap: 1rem;
    
    &.qm-dashboard-stats-grid-auto {
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    }
    
    &.qm-dashboard-stats-grid-2,
    &.qm-dashboard-stats-grid-3,
    &.qm-dashboard-stats-grid-4,
    &.qm-dashboard-stats-grid-5,
    &.qm-dashboard-stats-grid-6 {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  .qm-dashboard-stats-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .qm-dashboard-stats-summary {
    justify-content: center;
  }
  
  .qm-dashboard-stats-meta {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .qm-dashboard-stats-grid {
    &.qm-dashboard-stats-grid-auto,
    &.qm-dashboard-stats-grid-2,
    &.qm-dashboard-stats-grid-3,
    &.qm-dashboard-stats-grid-4,
    &.qm-dashboard-stats-grid-5,
    &.qm-dashboard-stats-grid-6 {
      grid-template-columns: 1fr;
    }
  }
  
  .qm-dashboard-stats-title h2 {
    font-size: 1.25rem;
  }
  
  .qm-dashboard-stats-empty {
    padding: 2rem 1rem;
  }
  
  .qm-dashboard-stats-empty-icon {
    width: 3rem;
    height: 3rem;
    
    i {
      font-size: 1.5rem;
    }
  }
}
</style>