<template>
  <div class="qm-input-wrapper" :class="wrapperClasses">
    <label v-if="label" :for="inputId" class="qm-input-label">
      {{ label }}
      <span v-if="required" class="qm-input-required">*</span>
    </label>
    
    <div class="qm-input-container">
      <div v-if="$slots.prepend || prependIcon" class="qm-input-prepend">
        <slot name="prepend">
          <i v-if="prependIcon" :class="prependIcon"></i>
        </slot>
      </div>
      
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        v-bind="$attrs"
      />
      
      <div v-if="$slots.append || appendIcon || showPasswordToggle" class="qm-input-append">
        <slot name="append">
          <button 
            v-if="showPasswordToggle" 
            type="button" 
            class="qm-input-password-toggle"
            @click="togglePasswordVisibility"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
          >
            <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </button>
          <i v-else-if="appendIcon" :class="appendIcon"></i>
        </slot>
      </div>
    </div>
    
    <div v-if="error || hint" class="qm-input-feedback">
      <div v-if="error" class="qm-input-error">
        <i class="fas fa-exclamation-circle"></i>
        {{ error }}
      </div>
      <div v-else-if="hint" class="qm-input-hint">
        {{ hint }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick } from 'vue'

export default {
  name: 'QmInput',
  inheritAttrs: false,
  emits: ['update:modelValue', 'focus', 'blur', 'input'],
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    type: {
      type: String,
      default: 'text'
    },
    label: {
      type: String,
      default: null
    },
    placeholder: {
      type: String,
      default: null
    },
    error: {
      type: String,
      default: null
    },
    hint: {
      type: String,
      default: null
    },
    disabled: {
      type: Boolean,
      default: false
    },
    readonly: {
      type: Boolean,
      default: false
    },
    required: {
      type: Boolean,
      default: false
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md', 'lg'].includes(value)
    },
    prependIcon: {
      type: String,
      default: null
    },
    appendIcon: {
      type: String,
      default: null
    },
    id: {
      type: String,
      default: null
    }
  },
  setup(props, { emit }) {
    const isFocused = ref(false)
    const showPassword = ref(false)
    
    const inputId = computed(() => {
      return props.id || `qm-input-${Math.random().toString(36).substr(2, 9)}`
    })
    
    const showPasswordToggle = computed(() => {
      return props.type === 'password'
    })
    
    const actualType = computed(() => {
      if (props.type === 'password' && showPassword.value) {
        return 'text'
      }
      return props.type
    })
    
    const wrapperClasses = computed(() => {
      return [
        'qm-input-wrapper',
        `qm-input-${props.size}`,
        {
          'qm-input-focused': isFocused.value,
          'qm-input-error': props.error,
          'qm-input-disabled': props.disabled,
          'qm-input-readonly': props.readonly
        }
      ]
    })
    
    const inputClasses = computed(() => {
      return [
        'qm-input',
        {
          'qm-input-has-prepend': props.prependIcon || props.$slots?.prepend,
          'qm-input-has-append': props.appendIcon || props.$slots?.append || showPasswordToggle.value
        }
      ]
    })
    
    const handleInput = (event) => {
      emit('update:modelValue', event.target.value)
      emit('input', event)
    }
    
    const handleFocus = (event) => {
      isFocused.value = true
      emit('focus', event)
    }
    
    const handleBlur = (event) => {
      isFocused.value = false
      emit('blur', event)
    }
    
    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value
    }
    
    return {
      isFocused,
      showPassword,
      inputId,
      showPasswordToggle,
      actualType,
      wrapperClasses,
      inputClasses,
      handleInput,
      handleFocus,
      handleBlur,
      togglePasswordVisibility
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  
  &.qm-input-sm {
    .qm-input {
      padding: 8px 12px;
      font-size: 0.875rem;
      min-height: 32px;
    }
  }
  
  &.qm-input-md {
    .qm-input {
      padding: 12px 16px;
      font-size: 1rem;
      min-height: 40px;
    }
  }
  
  &.qm-input-lg {
    .qm-input {
      padding: 16px 20px;
      font-size: 1.125rem;
      min-height: 48px;
    }
  }
}

.qm-input-label {
  font-family: var(--qm-font-body);
  font-weight: 500;
  color: var(--qm-dark-gray);
  font-size: 0.875rem;
  margin-bottom: 0;
}

.qm-input-required {
  color: var(--qm-error-red);
  margin-left: 2px;
}

.qm-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.qm-input {
  width: 100%;
  font-family: var(--qm-font-body);
  border: 2px solid var(--qm-light-border);
  border-radius: var(--qm-border-radius);
  background: var(--qm-white);
  color: var(--qm-dark-gray);
  transition: var(--qm-transition);
  
  &:focus {
    outline: none;
    border-color: var(--qm-electric-blue);
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
  }
  
  &::placeholder {
    color: var(--qm-medium-gray);
  }
  
  &:disabled {
    background-color: var(--qm-light-gray);
    color: var(--qm-medium-gray);
    cursor: not-allowed;
  }
  
  &:readonly {
    background-color: var(--qm-light-gray);
  }
  
  &.qm-input-has-prepend {
    padding-left: 3rem;
  }
  
  &.qm-input-has-append {
    padding-right: 3rem;
  }
}

.qm-input-prepend,
.qm-input-append {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  color: var(--qm-medium-gray);
  z-index: 1;
}

.qm-input-prepend {
  left: 0;
}

.qm-input-append {
  right: 0;
}

.qm-input-password-toggle {
  background: none;
  border: none;
  color: var(--qm-medium-gray);
  cursor: pointer;
  padding: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--qm-transition);
  
  &:hover {
    color: var(--qm-electric-blue);
  }
  
  &:focus {
    outline: 2px solid var(--qm-electric-blue);
    outline-offset: 2px;
    border-radius: 4px;
  }
}

.qm-input-feedback {
  min-height: 1.25rem;
}

.qm-input-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--qm-error-red);
  font-size: 0.875rem;
  font-family: var(--qm-font-body);
  
  i {
    font-size: 0.75rem;
  }
}

.qm-input-hint {
  color: var(--qm-medium-gray);
  font-size: 0.875rem;
  font-family: var(--qm-font-body);
}

// Error state styling
.qm-input-wrapper.qm-input-error {
  .qm-input {
    border-color: var(--qm-error-red);
    
    &:focus {
      border-color: var(--qm-error-red);
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }
  }
}

// Dark mode support
[data-theme="dark"] {
  .qm-input-label {
    color: var(--qm-text-50, #f8fafc);
  }
  
  .qm-input {
    background: var(--qm-bg-surface-900, #1e1e1e);
    border-color: var(--qm-border-dark, #374151);
    color: var(--qm-text-50, #f8fafc);
    
    &::placeholder {
      color: var(--qm-text-400, #9ca3af);
    }
    
    &:disabled,
    &:readonly {
      background-color: var(--qm-bg-surface-800, #2d2d2d);
      color: var(--qm-text-400, #9ca3af);
    }
  }
  
  .qm-input-prepend,
  .qm-input-append {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-input-password-toggle {
    color: var(--qm-text-400, #9ca3af);
    
    &:hover {
      color: var(--qm-electric-blue);
    }
  }
  
  .qm-input-hint {
    color: var(--qm-text-400, #9ca3af);
  }
}
</style>