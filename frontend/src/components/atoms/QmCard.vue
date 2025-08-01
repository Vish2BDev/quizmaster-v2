<template>
  <div 
    :class="cardClasses"
    @click="handleClick"
    :role="clickable ? 'button' : undefined"
    :tabindex="clickable ? '0' : undefined"
    @keydown="handleKeydown"
  >
    <div v-if="$slots.header || title" class="qm-card-header">
      <slot name="header">
        <h3 v-if="title" class="qm-card-title">{{ title }}</h3>
      </slot>
    </div>
    
    <div v-if="$slots.media" class="qm-card-media">
      <slot name="media"></slot>
    </div>
    
    <div class="qm-card-body">
      <slot></slot>
    </div>
    
    <div v-if="$slots.footer" class="qm-card-footer">
      <slot name="footer"></slot>
    </div>
    
    <div v-if="loading" class="qm-card-loading">
      <div class="qm-card-spinner"></div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'QmCard',
  emits: ['click'],
  props: {
    title: {
      type: String,
      default: null
    },
    variant: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'elevated', 'outlined', 'filled', 'gradient'].includes(value)
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
    },
    clickable: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    hover: {
      type: Boolean,
      default: true
    },
    rounded: {
      type: Boolean,
      default: true
    }
  },
  setup(props, { emit }) {
    const cardClasses = computed(() => {
      return [
        'qm-card',
        `qm-card-${props.variant}`,
        `qm-card-${props.size}`,
        {
          'qm-card-clickable': props.clickable && !props.disabled,
          'qm-card-disabled': props.disabled,
          'qm-card-loading': props.loading,
          'qm-card-hover': props.hover && !props.disabled,
          'qm-card-rounded': props.rounded
        }
      ]
    })
    
    const handleClick = (event) => {
      if (!props.disabled && !props.loading && props.clickable) {
        emit('click', event)
      }
    }
    
    const handleKeydown = (event) => {
      if (props.clickable && !props.disabled && !props.loading) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          emit('click', event)
        }
      }
    }
    
    return {
      cardClasses,
      handleClick,
      handleKeydown
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--qm-white);
  border-radius: var(--qm-border-radius);
  transition: var(--qm-transition);
  overflow: hidden;
  
  // Size variants
  &.qm-card-sm {
    .qm-card-header,
    .qm-card-body,
    .qm-card-footer {
      padding: 0.75rem;
    }
  }
  
  &.qm-card-md {
    .qm-card-header,
    .qm-card-body,
    .qm-card-footer {
      padding: 1rem;
    }
  }
  
  &.qm-card-lg {
    .qm-card-header,
    .qm-card-body,
    .qm-card-footer {
      padding: 1.5rem;
    }
  }
  
  &.qm-card-xl {
    .qm-card-header,
    .qm-card-body,
    .qm-card-footer {
      padding: 2rem;
    }
  }
  
  // Style variants
  &.qm-card-default {
    border: 1px solid var(--qm-light-border);
    box-shadow: var(--qm-shadow-sm);
  }
  
  &.qm-card-elevated {
    border: none;
    box-shadow: var(--qm-shadow-lg);
  }
  
  &.qm-card-outlined {
    border: 2px solid var(--qm-electric-blue);
    box-shadow: none;
  }
  
  &.qm-card-filled {
    background: var(--qm-light-gray);
    border: none;
    box-shadow: none;
  }
  
  &.qm-card-gradient {
    background: linear-gradient(135deg, var(--qm-electric-blue), var(--qm-royal-purple));
    border: none;
    box-shadow: var(--qm-shadow-lg);
    color: var(--qm-white);
  }
  
  // Interactive states
  &.qm-card-clickable {
    cursor: pointer;
    
    &:focus {
      outline: 2px solid var(--qm-electric-blue);
      outline-offset: 2px;
    }
  }
  
  &.qm-card-hover:hover:not(.qm-card-disabled):not(.qm-card-loading) {
    transform: translateY(-2px);
    box-shadow: var(--qm-shadow-xl);
  }
  
  &.qm-card-disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }
  
  &.qm-card-loading {
    pointer-events: none;
  }
  
  &.qm-card-rounded {
    border-radius: var(--qm-border-radius-lg);
  }
}

.qm-card-header {
  border-bottom: 1px solid var(--qm-light-border);
  
  .qm-card-gradient & {
    border-bottom-color: rgba(255, 255, 255, 0.2);
  }
}

.qm-card-title {
  margin: 0;
  font-family: var(--qm-font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--qm-dark-gray);
  
  .qm-card-gradient & {
    color: var(--qm-white);
  }
}

.qm-card-media {
  padding: 0;
  
  img {
    width: 100%;
    height: auto;
    display: block;
  }
}

.qm-card-body {
  flex: 1;
  
  &:first-child {
    border-top-left-radius: inherit;
    border-top-right-radius: inherit;
  }
  
  &:last-child {
    border-bottom-left-radius: inherit;
    border-bottom-right-radius: inherit;
  }
}

.qm-card-footer {
  border-top: 1px solid var(--qm-light-border);
  
  .qm-card-gradient & {
    border-top-color: rgba(255, 255, 255, 0.2);
  }
}

.qm-card-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.qm-card-spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--qm-light-gray);
  border-top: 3px solid var(--qm-electric-blue);
  border-radius: 50%;
  animation: qm-spin 1s linear infinite;
}

@keyframes qm-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// Dark mode support
[data-theme="dark"] {
  .qm-card {
    background: var(--qm-bg-surface-900, #1e1e1e);
    
    &.qm-card-default {
      border-color: var(--qm-border-dark, #374151);
    }
    
    &.qm-card-filled {
      background: var(--qm-bg-surface-800, #2d2d2d);
    }
  }
  
  .qm-card-header,
  .qm-card-footer {
    border-color: var(--qm-border-dark, #374151);
  }
  
  .qm-card-title {
    color: var(--qm-text-50, #f8fafc);
  }
  
  .qm-card-loading {
    background: rgba(30, 30, 30, 0.8);
  }
  
  .qm-card-spinner {
    border-color: var(--qm-bg-surface-700, #404040);
    border-top-color: var(--qm-electric-blue);
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .qm-card {
    &.qm-card-lg {
      .qm-card-header,
      .qm-card-body,
      .qm-card-footer {
        padding: 1rem;
      }
    }
    
    &.qm-card-xl {
      .qm-card-header,
      .qm-card-body,
      .qm-card-footer {
        padding: 1.25rem;
      }
    }
  }
}
</style>