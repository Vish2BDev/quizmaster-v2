<template>
  <button 
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="type"
    @click="handleClick"
    v-bind="$attrs"
  >
    <span v-if="loading" class="qm-btn-spinner">
      <div class="spinner-border spinner-border-sm" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </span>
    <i v-else-if="icon && !iconRight" :class="icon" class="qm-btn-icon qm-btn-icon-left"></i>
    
    <span class="qm-btn-content">
      <slot></slot>
    </span>
    
    <i v-if="icon && iconRight" :class="icon" class="qm-btn-icon qm-btn-icon-right"></i>
  </button>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'QmBtn',
  inheritAttrs: false,
  emits: ['click'],
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'secondary', 'ghost', 'danger', 'success', 'warning'].includes(value)
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    icon: {
      type: String,
      default: null
    },
    iconRight: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'button',
      validator: (value) => ['button', 'submit', 'reset'].includes(value)
    },
    block: {
      type: Boolean,
      default: false
    },
    rounded: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { emit, slots }) {
    const buttonClasses = computed(() => {
      return [
        'qm-btn',
        `qm-btn-${props.variant}`,
        `qm-btn-${props.size}`,
        {
          'qm-btn-loading': props.loading,
          'qm-btn-disabled': props.disabled,
          'qm-btn-block': props.block,
          'qm-btn-rounded': props.rounded,
          'qm-btn-icon-only': props.icon && !slots.default
        }
      ]
    })

    const handleClick = (event) => {
      if (!props.disabled && !props.loading) {
        emit('click', event)
      }
    }

    return {
      buttonClasses,
      handleClick
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: var(--qm-font-ui);
  font-weight: 600;
  border: none;
  border-radius: var(--qm-border-radius);
  cursor: pointer;
  transition: var(--qm-transition);
  text-decoration: none;
  position: relative;
  overflow: hidden;
  white-space: nowrap;
  user-select: none;
  
  &:focus {
    outline: 3px solid var(--qm-electric-blue);
    outline-offset: 2px;
  }
  
  &:active {
    transform: scale(0.97);
    transition: transform var(--qm-animation-fast) ease-out;
  }
  
  // Variants
  &-primary {
    background: var(--qm-primary-gradient);
    color: var(--qm-white);
    box-shadow: var(--qm-shadow);
    
    &:hover:not(.qm-btn-disabled):not(.qm-btn-loading) {
      transform: translateY(-2px);
      box-shadow: var(--qm-shadow-hover);
    }
  }
  
  &-secondary {
    background: var(--qm-secondary-gradient);
    color: var(--qm-white);
    box-shadow: var(--qm-shadow);
    
    &:hover:not(.qm-btn-disabled):not(.qm-btn-loading) {
      transform: translateY(-2px);
      box-shadow: var(--qm-shadow-hover);
    }
  }
  
  &-ghost {
    background: transparent;
    color: var(--qm-electric-blue);
    border: 2px solid var(--qm-electric-blue);
    
    &:hover:not(.qm-btn-disabled):not(.qm-btn-loading) {
      background: var(--qm-electric-blue);
      color: var(--qm-white);
    }
  }
  
  &-danger {
    background: linear-gradient(135deg, var(--qm-error-red), #dc2626);
    color: var(--qm-white);
    box-shadow: var(--qm-shadow);
    
    &:hover:not(.qm-btn-disabled):not(.qm-btn-loading) {
      transform: translateY(-2px);
      box-shadow: var(--qm-shadow-hover);
    }
  }
  
  &-success {
    background: linear-gradient(135deg, var(--qm-success-green), #16a34a);
    color: var(--qm-white);
    box-shadow: var(--qm-shadow);
    
    &:hover:not(.qm-btn-disabled):not(.qm-btn-loading) {
      transform: translateY(-2px);
      box-shadow: var(--qm-shadow-hover);
    }
  }
  
  &-warning {
    background: linear-gradient(135deg, var(--qm-warning-orange), #ea580c);
    color: var(--qm-white);
    box-shadow: var(--qm-shadow);
    
    &:hover:not(.qm-btn-disabled):not(.qm-btn-loading) {
      transform: translateY(-2px);
      box-shadow: var(--qm-shadow-hover);
    }
  }
  
  // Sizes
  &-sm {
    padding: 8px 16px;
    font-size: 0.875rem;
    min-height: 32px;
  }
  
  &-md {
    padding: 12px 24px;
    font-size: 1rem;
    min-height: 40px;
  }
  
  &-lg {
    padding: 16px 32px;
    font-size: 1.125rem;
    min-height: 48px;
  }
  
  &-xl {
    padding: 20px 40px;
    font-size: 1.25rem;
    min-height: 56px;
  }
  
  // States
  &-disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
  }
  
  &-loading {
    cursor: wait;
    
    .qm-btn-content {
      opacity: 0.7;
    }
  }
  
  &-block {
    width: 100%;
  }
  
  &-rounded {
    border-radius: 50px;
  }
  
  &-icon-only {
    padding: 12px;
    
    &.qm-btn-sm {
      padding: 8px;
    }
    
    &.qm-btn-lg {
      padding: 16px;
    }
    
    &.qm-btn-xl {
      padding: 20px;
    }
  }
}

.qm-btn-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.qm-btn-icon {
  &-left {
    margin-right: 0.25rem;
  }
  
  &-right {
    margin-left: 0.25rem;
  }
}

// Dark mode support
[data-theme="dark"] {
  .qm-btn {
    &-ghost {
      color: var(--qm-electric-blue);
      border-color: var(--qm-electric-blue);
      
      &:hover:not(.qm-btn-disabled):not(.qm-btn-loading) {
        background: var(--qm-electric-blue);
        color: var(--qm-white);
      }
    }
  }
}

// Reduced motion support
@media (prefers-reduced-motion: reduce) {
  .qm-btn {
    &:hover {
      transform: none;
    }
    
    &:active {
      transform: none;
    }
  }
}
</style>