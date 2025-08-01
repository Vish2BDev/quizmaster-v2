<template>
  <div class="qm-form-field" :class="fieldClasses">
    <label 
      v-if="label"
      :for="fieldId"
      class="qm-form-field-label"
      :class="labelClasses"
    >
      {{ label }}
      <span v-if="required" class="qm-form-field-required">*</span>
      <QmBadge
        v-if="badge"
        :variant="badge.variant || 'secondary'"
        :size="badge.size || 'xs'"
        class="qm-form-field-badge"
      >
        {{ badge.text }}
      </QmBadge>
    </label>
    
    <div class="qm-form-field-input-wrapper">
      <QmInput
        :id="fieldId"
        v-model="inputValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :size="size"
        :prepend-icon="prependIcon"
        :append-icon="appendIcon"
        :error="hasError"
        :autocomplete="autocomplete"
        :maxlength="maxlength"
        :minlength="minlength"
        :min="min"
        :max="max"
        :step="step"
        :pattern="pattern"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @keydown="handleKeydown"
        @keyup="handleKeyup"
      />
      
      <div v-if="showCharacterCount" class="qm-form-field-character-count">
        <span :class="characterCountClasses">
          {{ characterCount }}
          <span v-if="maxlength">{{ ` / ${maxlength}` }}</span>
        </span>
      </div>
    </div>
    
    <div v-if="hasError" class="qm-form-field-error">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ errorMessage }}</span>
    </div>
    
    <div v-else-if="hint" class="qm-form-field-hint">
      <i class="fas fa-info-circle"></i>
      <span>{{ hint }}</span>
    </div>
    
    <div v-if="validationRules && showValidation" class="qm-form-field-validation">
      <div 
        v-for="rule in validationDisplay"
        :key="rule.key"
        class="qm-form-field-validation-rule"
        :class="rule.classes"
      >
        <i :class="rule.icon"></i>
        <span>{{ rule.message }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, watch, nextTick } from 'vue'
import QmInput from '../atoms/QmInput.vue'
import QmBadge from '../atoms/QmBadge.vue'

export default {
  name: 'FormField',
  components: {
    QmInput,
    QmBadge
  },
  emits: ['update:modelValue', 'input', 'blur', 'focus', 'keydown', 'keyup', 'validate'],
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    label: {
      type: String,
      default: null
    },
    type: {
      type: String,
      default: 'text'
    },
    placeholder: {
      type: String,
      default: null
    },
    hint: {
      type: String,
      default: null
    },
    error: {
      type: String,
      default: null
    },
    required: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    readonly: {
      type: Boolean,
      default: false
    },
    size: {
      type: String,
      default: 'md'
    },
    prependIcon: {
      type: String,
      default: null
    },
    appendIcon: {
      type: String,
      default: null
    },
    autocomplete: {
      type: String,
      default: null
    },
    maxlength: {
      type: Number,
      default: null
    },
    minlength: {
      type: Number,
      default: null
    },
    min: {
      type: [Number, String],
      default: null
    },
    max: {
      type: [Number, String],
      default: null
    },
    step: {
      type: [Number, String],
      default: null
    },
    pattern: {
      type: String,
      default: null
    },
    badge: {
      type: Object,
      default: null
      // Expected: { text: string, variant?: string, size?: string }
    },
    validationRules: {
      type: Array,
      default: () => []
      // Expected: [{ key: string, message: string, validator: function }]
    },
    showValidation: {
      type: Boolean,
      default: false
    },
    showCharacterCount: {
      type: Boolean,
      default: false
    },
    validateOnBlur: {
      type: Boolean,
      default: true
    },
    validateOnInput: {
      type: Boolean,
      default: false
    },
    id: {
      type: String,
      default: null
    }
  },
  setup(props, { emit }) {
    const inputValue = ref(props.modelValue)
    const isFocused = ref(false)
    const isTouched = ref(false)
    const validationResults = ref({})
    
    // Generate unique field ID
    const fieldId = computed(() => {
      return props.id || `qm-form-field-${Math.random().toString(36).substr(2, 9)}`
    })
    
    // Watch for external model value changes
    watch(() => props.modelValue, (newValue) => {
      inputValue.value = newValue
    })
    
    // Watch for input value changes
    watch(inputValue, (newValue) => {
      emit('update:modelValue', newValue)
      if (props.validateOnInput) {
        nextTick(() => validateField())
      }
    })
    
    const fieldClasses = computed(() => {
      return [
        'qm-form-field',
        {
          'qm-form-field-focused': isFocused.value,
          'qm-form-field-touched': isTouched.value,
          'qm-form-field-error': hasError.value,
          'qm-form-field-disabled': props.disabled,
          'qm-form-field-readonly': props.readonly,
          'qm-form-field-required': props.required
        }
      ]
    })
    
    const labelClasses = computed(() => {
      return [
        'qm-form-field-label',
        {
          'qm-form-field-label-required': props.required,
          'qm-form-field-label-error': hasError.value
        }
      ]
    })
    
    const hasError = computed(() => {
      return Boolean(props.error || Object.values(validationResults.value).some(result => !result.valid))
    })
    
    const errorMessage = computed(() => {
      if (props.error) return props.error
      
      const failedValidation = Object.values(validationResults.value).find(result => !result.valid)
      return failedValidation?.message || ''
    })
    
    const characterCount = computed(() => {
      return String(inputValue.value || '').length
    })
    
    const characterCountClasses = computed(() => {
      const isNearLimit = props.maxlength && characterCount.value > props.maxlength * 0.8
      const isOverLimit = props.maxlength && characterCount.value > props.maxlength
      
      return [
        'qm-form-field-character-count-text',
        {
          'qm-form-field-character-count-warning': isNearLimit && !isOverLimit,
          'qm-form-field-character-count-error': isOverLimit
        }
      ]
    })
    
    const validationDisplay = computed(() => {
      if (!props.validationRules.length) return []
      
      return props.validationRules.map(rule => {
        const result = validationResults.value[rule.key]
        const isValid = result?.valid ?? null
        
        return {
          key: rule.key,
          message: rule.message,
          classes: [
            'qm-form-field-validation-rule',
            {
              'qm-form-field-validation-rule-valid': isValid === true,
              'qm-form-field-validation-rule-invalid': isValid === false,
              'qm-form-field-validation-rule-pending': isValid === null
            }
          ],
          icon: isValid === true ? 'fas fa-check' : 
                isValid === false ? 'fas fa-times' : 
                'fas fa-circle'
        }
      })
    })
    
    const validateField = () => {
      if (!props.validationRules.length) return true
      
      const results = {}
      let isValid = true
      
      props.validationRules.forEach(rule => {
        try {
          const result = rule.validator(inputValue.value)
          results[rule.key] = {
            valid: result,
            message: rule.message
          }
          if (!result) isValid = false
        } catch (error) {
          results[rule.key] = {
            valid: false,
            message: rule.message
          }
          isValid = false
        }
      })
      
      validationResults.value = results
      emit('validate', { isValid, results })
      
      return isValid
    }
    
    const handleInput = (value) => {
      inputValue.value = value
      emit('input', value)
    }
    
    const handleBlur = (event) => {
      isFocused.value = false
      isTouched.value = true
      
      if (props.validateOnBlur) {
        nextTick(() => validateField())
      }
      
      emit('blur', event)
    }
    
    const handleFocus = (event) => {
      isFocused.value = true
      emit('focus', event)
    }
    
    const handleKeydown = (event) => {
      emit('keydown', event)
    }
    
    const handleKeyup = (event) => {
      emit('keyup', event)
    }
    
    // Public method for external validation
    const validate = () => {
      return validateField()
    }
    
    // Public method to reset validation
    const resetValidation = () => {
      validationResults.value = {}
      isTouched.value = false
    }
    
    return {
      inputValue,
      fieldId,
      fieldClasses,
      labelClasses,
      hasError,
      errorMessage,
      characterCount,
      characterCountClasses,
      validationDisplay,
      handleInput,
      handleBlur,
      handleFocus,
      handleKeydown,
      handleKeyup,
      validate,
      resetValidation
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.qm-form-field-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--qm-font-body);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--qm-dark-gray);
  line-height: 1.4;
  
  &.qm-form-field-label-error {
    color: var(--qm-error-red);
  }
}

.qm-form-field-required {
  color: var(--qm-error-red);
  font-weight: 700;
}

.qm-form-field-badge {
  margin-left: auto;
}

.qm-form-field-input-wrapper {
  position: relative;
}

.qm-form-field-character-count {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.25rem;
  font-size: 0.75rem;
}

.qm-form-field-character-count-text {
  color: var(--qm-medium-gray);
  
  &.qm-form-field-character-count-warning {
    color: var(--qm-warning-yellow);
  }
  
  &.qm-form-field-character-count-error {
    color: var(--qm-error-red);
    font-weight: 600;
  }
}

.qm-form-field-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--qm-error-red);
  line-height: 1.4;
  
  i {
    font-size: 0.875rem;
    flex-shrink: 0;
  }
}

.qm-form-field-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--qm-medium-gray);
  line-height: 1.4;
  
  i {
    font-size: 0.875rem;
    flex-shrink: 0;
    color: var(--qm-electric-blue);
  }
}

.qm-form-field-validation {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  background: var(--qm-light-gray);
  border-radius: var(--qm-border-radius);
  border-left: 3px solid var(--qm-electric-blue);
}

.qm-form-field-validation-rule {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  line-height: 1.4;
  
  i {
    font-size: 0.625rem;
    flex-shrink: 0;
  }
  
  &.qm-form-field-validation-rule-valid {
    color: var(--qm-success-green);
  }
  
  &.qm-form-field-validation-rule-invalid {
    color: var(--qm-error-red);
  }
  
  &.qm-form-field-validation-rule-pending {
    color: var(--qm-medium-gray);
  }
}

// Field state styles
.qm-form-field-focused {
  .qm-form-field-label {
    color: var(--qm-electric-blue);
  }
}

.qm-form-field-disabled {
  opacity: 0.6;
  pointer-events: none;
  
  .qm-form-field-label {
    color: var(--qm-medium-gray);
  }
}

.qm-form-field-readonly {
  .qm-form-field-label {
    color: var(--qm-medium-gray);
  }
}

// Dark mode support
[data-theme="dark"] {
  .qm-form-field-label {
    color: var(--qm-text-200, #e5e7eb);
    
    &.qm-form-field-label-error {
      color: var(--qm-error-red);
    }
  }
  
  .qm-form-field-character-count-text {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-form-field-hint {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-form-field-validation {
    background: var(--qm-bg-surface-800, #2d2d2d);
  }
  
  .qm-form-field-validation-rule-pending {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-form-field-focused {
    .qm-form-field-label {
      color: var(--qm-electric-blue);
    }
  }
  
  .qm-form-field-disabled {
    .qm-form-field-label {
      color: var(--qm-text-500, #6b7280);
    }
  }
  
  .qm-form-field-readonly {
    .qm-form-field-label {
      color: var(--qm-text-400, #9ca3af);
    }
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .qm-form-field-label {
    font-size: 0.8125rem;
  }
  
  .qm-form-field-error,
  .qm-form-field-hint {
    font-size: 0.6875rem;
  }
  
  .qm-form-field-validation-rule {
    font-size: 0.6875rem;
  }
  
  .qm-form-field-character-count {
    font-size: 0.6875rem;
  }
}
</style>