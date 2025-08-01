<template>
  <span 
    :class="badgeClasses"
    :role="clickable ? 'button' : undefined"
    :tabindex="clickable ? '0' : undefined"
    @click="handleClick"
    @keydown="handleKeydown"
  >
    <i v-if="icon" :class="icon" class="qm-badge-icon"></i>
    <slot></slot>
    <button 
      v-if="closable" 
      class="qm-badge-close"
      @click.stop="handleClose"
      :aria-label="'Remove badge'"
    >
      <i class="fas fa-times"></i>
    </button>
  </span>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'QmBadge',
  emits: ['click', 'close'],
  props: {
    variant: {
      type: String,
      default: 'default',
      validator: (value) => [
        'default', 'primary', 'secondary', 'success', 'error', 'warning', 'info'
      ].includes(value)
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['xs', 'sm', 'md', 'lg'].includes(value)
    },
    shape: {
      type: String,
      default: 'rounded',
      validator: (value) => ['rounded', 'pill', 'square'].includes(value)
    },
    icon: {
      type: String,
      default: null
    },
    clickable: {
      type: Boolean,
      default: false
    },
    closable: {
      type: Boolean,
      default: false
    },
    outlined: {
      type: Boolean,
      default: false
    },
    dot: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { emit }) {
    const badgeClasses = computed(() => {
      return [
        'qm-badge',
        `qm-badge-${props.variant}`,
        `qm-badge-${props.size}`,
        `qm-badge-${props.shape}`,
        {
          'qm-badge-clickable': props.clickable,
          'qm-badge-outlined': props.outlined,
          'qm-badge-dot': props.dot,
          'qm-badge-with-icon': props.icon,
          'qm-badge-closable': props.closable
        }
      ]
    })
    
    const handleClick = (event) => {
      if (props.clickable) {
        emit('click', event)
      }
    }
    
    const handleKeydown = (event) => {
      if (props.clickable && (event.key === 'Enter' || event.key === ' ')) {
        event.preventDefault()
        emit('click', event)
      }
    }
    
    const handleClose = (event) => {
      emit('close', event)
    }
    
    return {
      badgeClasses,
      handleClick,
      handleKeydown,
      handleClose
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-family: var(--qm-font-body);
  font-weight: 500;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
  vertical-align: baseline;
  transition: var(--qm-transition);
  
  // Size variants
  &.qm-badge-xs {
    padding: 0.125rem 0.375rem;
    font-size: 0.625rem;
    
    &.qm-badge-dot {
      width: 0.5rem;
      height: 0.5rem;
      padding: 0;
    }
  }
  
  &.qm-badge-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    
    &.qm-badge-dot {
      width: 0.625rem;
      height: 0.625rem;
      padding: 0;
    }
  }
  
  &.qm-badge-md {
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
    
    &.qm-badge-dot {
      width: 0.75rem;
      height: 0.75rem;
      padding: 0;
    }
  }
  
  &.qm-badge-lg {
    padding: 0.5rem 1rem;
    font-size: 1rem;
    
    &.qm-badge-dot {
      width: 1rem;
      height: 1rem;
      padding: 0;
    }
  }
  
  // Shape variants
  &.qm-badge-rounded {
    border-radius: var(--qm-border-radius);
  }
  
  &.qm-badge-pill {
    border-radius: 50px;
  }
  
  &.qm-badge-square {
    border-radius: 0;
  }
  
  // Dot variant
  &.qm-badge-dot {
    border-radius: 50%;
    
    .qm-badge-icon,
    .qm-badge-close {
      display: none;
    }
  }
  
  // Color variants
  &.qm-badge-default {
    background: var(--qm-light-gray);
    color: var(--qm-dark-gray);
    
    &.qm-badge-outlined {
      background: transparent;
      border: 1px solid var(--qm-light-border);
    }
  }
  
  &.qm-badge-primary {
    background: var(--qm-electric-blue);
    color: var(--qm-white);
    
    &.qm-badge-outlined {
      background: transparent;
      border: 1px solid var(--qm-electric-blue);
      color: var(--qm-electric-blue);
    }
  }
  
  &.qm-badge-secondary {
    background: var(--qm-royal-purple);
    color: var(--qm-white);
    
    &.qm-badge-outlined {
      background: transparent;
      border: 1px solid var(--qm-royal-purple);
      color: var(--qm-royal-purple);
    }
  }
  
  &.qm-badge-success {
    background: var(--qm-success-green);
    color: var(--qm-white);
    
    &.qm-badge-outlined {
      background: transparent;
      border: 1px solid var(--qm-success-green);
      color: var(--qm-success-green);
    }
  }
  
  &.qm-badge-error {
    background: var(--qm-error-red);
    color: var(--qm-white);
    
    &.qm-badge-outlined {
      background: transparent;
      border: 1px solid var(--qm-error-red);
      color: var(--qm-error-red);
    }
  }
  
  &.qm-badge-warning {
    background: var(--qm-warning-yellow);
    color: var(--qm-dark-gray);
    
    &.qm-badge-outlined {
      background: transparent;
      border: 1px solid var(--qm-warning-yellow);
      color: var(--qm-warning-yellow);
    }
  }
  
  &.qm-badge-info {
    background: var(--qm-electric-blue);
    color: var(--qm-white);
    
    &.qm-badge-outlined {
      background: transparent;
      border: 1px solid var(--qm-electric-blue);
      color: var(--qm-electric-blue);
    }
  }
  
  // Interactive states
  &.qm-badge-clickable {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: var(--qm-shadow-sm);
    }
    
    &:focus {
      outline: 2px solid var(--qm-electric-blue);
      outline-offset: 2px;
    }
    
    &:active {
      transform: translateY(0);
    }
  }
}

.qm-badge-icon {
  font-size: 0.875em;
}

.qm-badge-close {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  margin-left: 0.125rem;
  font-size: 0.75em;
  opacity: 0.7;
  transition: var(--qm-transition);
  
  &:hover {
    opacity: 1;
  }
  
  &:focus {
    outline: 1px solid currentColor;
    outline-offset: 1px;
    border-radius: 2px;
  }
}

// Dark mode support
[data-theme="dark"] {
  .qm-badge {
    &.qm-badge-default {
      background: var(--qm-bg-surface-700, #404040);
      color: var(--qm-text-200, #e5e7eb);
      
      &.qm-badge-outlined {
        border-color: var(--qm-border-dark, #374151);
        color: var(--qm-text-300, #d1d5db);
      }
    }
    
    &.qm-badge-warning {
      color: var(--qm-dark-gray);
      
      &.qm-badge-outlined {
        color: var(--qm-warning-yellow);
      }
    }
  }
}

// Animation for dynamic badges
.qm-badge-enter-active,
.qm-badge-leave-active {
  transition: all 0.2s ease;
}

.qm-badge-enter-from,
.qm-badge-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

// Responsive adjustments
@media (max-width: 768px) {
  .qm-badge {
    &.qm-badge-lg {
      padding: 0.375rem 0.75rem;
      font-size: 0.875rem;
    }
  }
}
</style>