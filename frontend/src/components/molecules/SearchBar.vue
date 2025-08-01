<template>
  <div class="qm-search-bar" :class="searchBarClasses">
    <div class="qm-search-bar-input-wrapper">
      <QmInput
        v-model="searchQuery"
        :placeholder="placeholder"
        :disabled="disabled"
        :size="size"
        prepend-icon="fas fa-search"
        class="qm-search-bar-input"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown.enter="handleSearch"
        @keydown.escape="handleEscape"
        @keydown.arrow-down="handleArrowDown"
        @keydown.arrow-up="handleArrowUp"
      />
      
      <QmBtn
        v-if="showClearButton && searchQuery"
        variant="ghost"
        :size="size"
        icon="fas fa-times"
        class="qm-search-bar-clear"
        @click="clearSearch"
        aria-label="Clear search"
      />
    </div>
    
    <QmBtn
      v-if="showSearchButton"
      :variant="searchButtonVariant"
      :size="size"
      :disabled="disabled || (!searchQuery && requireQuery)"
      :loading="loading"
      class="qm-search-bar-button"
      @click="handleSearch"
    >
      <i class="fas fa-search"></i>
      <span v-if="searchButtonText">{{ searchButtonText }}</span>
    </QmBtn>
    
    <!-- Suggestions Dropdown -->
    <Transition name="qm-search-suggestions">
      <div 
        v-if="showSuggestions && suggestions.length > 0"
        class="qm-search-suggestions"
        role="listbox"
        :aria-label="'Search suggestions'"
      >
        <div
          v-for="(suggestion, index) in suggestions"
          :key="suggestion.id || index"
          :class="[
            'qm-search-suggestion',
            { 'qm-search-suggestion-active': index === activeSuggestionIndex }
          ]"
          role="option"
          :aria-selected="index === activeSuggestionIndex"
          @click="selectSuggestion(suggestion)"
          @mouseenter="activeSuggestionIndex = index"
        >
          <div class="qm-search-suggestion-icon">
            <i :class="suggestion.icon || 'fas fa-search'"></i>
          </div>
          <div class="qm-search-suggestion-content">
            <div class="qm-search-suggestion-title">
              <span v-html="highlightMatch(suggestion.title || suggestion.text)"></span>
            </div>
            <div v-if="suggestion.subtitle" class="qm-search-suggestion-subtitle">
              {{ suggestion.subtitle }}
            </div>
          </div>
          <div v-if="suggestion.badge" class="qm-search-suggestion-badge">
            <QmBadge :variant="suggestion.badge.variant || 'default'" size="xs">
              {{ suggestion.badge.text }}
            </QmBadge>
          </div>
        </div>
        
        <div v-if="showViewAllOption && totalResults > suggestions.length" class="qm-search-view-all">
          <button 
            class="qm-search-view-all-button"
            @click="viewAllResults"
          >
            View all {{ totalResults }} results
          </button>
        </div>
      </div>
    </Transition>
    
    <!-- No Results -->
    <Transition name="qm-search-suggestions">
      <div 
        v-if="showNoResults"
        class="qm-search-no-results"
        role="status"
        aria-live="polite"
      >
        <div class="qm-search-no-results-icon">
          <i class="fas fa-search"></i>
        </div>
        <div class="qm-search-no-results-text">
          {{ noResultsText }}
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick } from 'vue'
import QmInput from '../atoms/QmInput.vue'
import QmBtn from '../atoms/QmBtn.vue'
import QmBadge from '../atoms/QmBadge.vue'

export default {
  name: 'SearchBar',
  components: {
    QmInput,
    QmBtn,
    QmBadge
  },
  emits: [
    'search', 'input', 'focus', 'blur', 'clear', 
    'suggestion-select', 'view-all'
  ],
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Search...'
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md', 'lg'].includes(value)
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    showSearchButton: {
      type: Boolean,
      default: true
    },
    showClearButton: {
      type: Boolean,
      default: true
    },
    searchButtonText: {
      type: String,
      default: null
    },
    searchButtonVariant: {
      type: String,
      default: 'primary'
    },
    requireQuery: {
      type: Boolean,
      default: false
    },
    suggestions: {
      type: Array,
      default: () => []
    },
    showSuggestions: {
      type: Boolean,
      default: true
    },
    totalResults: {
      type: Number,
      default: 0
    },
    showViewAllOption: {
      type: Boolean,
      default: true
    },
    noResultsText: {
      type: String,
      default: 'No results found'
    },
    debounceMs: {
      type: Number,
      default: 300
    },
    variant: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'compact', 'prominent'].includes(value)
    }
  },
  setup(props, { emit }) {
    const searchQuery = ref(props.modelValue)
    const isFocused = ref(false)
    const activeSuggestionIndex = ref(-1)
    let debounceTimer = null
    
    const searchBarClasses = computed(() => {
      return [
        `qm-search-bar-${props.variant}`,
        {
          'qm-search-bar-focused': isFocused.value,
          'qm-search-bar-has-suggestions': props.showSuggestions && props.suggestions.length > 0
        }
      ]
    })
    
    const showNoResults = computed(() => {
      return isFocused.value && 
             searchQuery.value.length > 0 && 
             props.suggestions.length === 0 && 
             !props.loading
    })
    
    // Watch for external model value changes
    watch(() => props.modelValue, (newValue) => {
      searchQuery.value = newValue
    })
    
    // Watch for search query changes
    watch(searchQuery, (newValue) => {
      emit('input', newValue)
      
      // Debounced search
      if (debounceTimer) {
        clearTimeout(debounceTimer)
      }
      
      debounceTimer = setTimeout(() => {
        if (newValue.trim()) {
          emit('search', newValue.trim())
        }
      }, props.debounceMs)
    })
    
    const handleInput = (event) => {
      searchQuery.value = event.target.value
      activeSuggestionIndex.value = -1
    }
    
    const handleFocus = (event) => {
      isFocused.value = true
      emit('focus', event)
    }
    
    const handleBlur = (event) => {
      // Delay blur to allow suggestion clicks
      setTimeout(() => {
        isFocused.value = false
        activeSuggestionIndex.value = -1
        emit('blur', event)
      }, 150)
    }
    
    const handleSearch = () => {
      if (activeSuggestionIndex.value >= 0 && props.suggestions[activeSuggestionIndex.value]) {
        selectSuggestion(props.suggestions[activeSuggestionIndex.value])
      } else if (searchQuery.value.trim()) {
        emit('search', searchQuery.value.trim())
        isFocused.value = false
      }
    }
    
    const handleEscape = () => {
      if (activeSuggestionIndex.value >= 0) {
        activeSuggestionIndex.value = -1
      } else {
        isFocused.value = false
      }
    }
    
    const handleArrowDown = (event) => {
      event.preventDefault()
      if (props.suggestions.length > 0) {
        activeSuggestionIndex.value = Math.min(
          activeSuggestionIndex.value + 1,
          props.suggestions.length - 1
        )
      }
    }
    
    const handleArrowUp = (event) => {
      event.preventDefault()
      if (props.suggestions.length > 0) {
        activeSuggestionIndex.value = Math.max(
          activeSuggestionIndex.value - 1,
          -1
        )
      }
    }
    
    const clearSearch = () => {
      searchQuery.value = ''
      activeSuggestionIndex.value = -1
      emit('clear')
      nextTick(() => {
        // Focus back to input after clearing
        const input = document.querySelector('.qm-search-bar-input input')
        if (input) input.focus()
      })
    }
    
    const selectSuggestion = (suggestion) => {
      searchQuery.value = suggestion.title || suggestion.text || ''
      isFocused.value = false
      activeSuggestionIndex.value = -1
      emit('suggestion-select', suggestion)
    }
    
    const viewAllResults = () => {
      emit('view-all', searchQuery.value.trim())
      isFocused.value = false
    }
    
    const highlightMatch = (text) => {
      if (!searchQuery.value || !text) return text
      
      const query = searchQuery.value.trim()
      const regex = new RegExp(`(${query})`, 'gi')
      return text.replace(regex, '<mark>$1</mark>')
    }
    
    return {
      searchQuery,
      isFocused,
      activeSuggestionIndex,
      searchBarClasses,
      showNoResults,
      handleInput,
      handleFocus,
      handleBlur,
      handleSearch,
      handleEscape,
      handleArrowDown,
      handleArrowUp,
      clearSearch,
      selectSuggestion,
      viewAllResults,
      highlightMatch
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-search-bar {
  position: relative;
  display: flex;
  gap: 0.5rem;
  
  &.qm-search-bar-compact {
    .qm-search-bar-input-wrapper {
      flex: 1;
    }
  }
  
  &.qm-search-bar-prominent {
    flex-direction: column;
    gap: 1rem;
    
    .qm-search-bar-input-wrapper {
      width: 100%;
    }
    
    .qm-search-bar-button {
      align-self: center;
      min-width: 120px;
    }
  }
}

.qm-search-bar-input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.qm-search-bar-input {
  flex: 1;
}

.qm-search-bar-clear {
  position: absolute;
  right: 0.5rem;
  z-index: 2;
}

.qm-search-bar-button {
  flex-shrink: 0;
  
  span {
    margin-left: 0.5rem;
  }
}

.qm-search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  background: var(--qm-white);
  border: 1px solid var(--qm-light-border);
  border-radius: var(--qm-border-radius-lg);
  box-shadow: var(--qm-shadow-xl);
  max-height: 300px;
  overflow-y: auto;
  margin-top: 0.25rem;
}

.qm-search-suggestion {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: var(--qm-transition);
  border-bottom: 1px solid var(--qm-light-border);
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover,
  &.qm-search-suggestion-active {
    background: var(--qm-light-gray);
  }
}

.qm-search-suggestion-icon {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--qm-medium-gray);
  
  i {
    font-size: 0.875rem;
  }
}

.qm-search-suggestion-content {
  flex: 1;
  min-width: 0;
}

.qm-search-suggestion-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--qm-dark-gray);
  line-height: 1.4;
  
  :deep(mark) {
    background: var(--qm-electric-blue);
    color: var(--qm-white);
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
    font-weight: 600;
  }
}

.qm-search-suggestion-subtitle {
  font-size: 0.75rem;
  color: var(--qm-medium-gray);
  margin-top: 0.125rem;
  line-height: 1.3;
}

.qm-search-suggestion-badge {
  flex-shrink: 0;
}

.qm-search-view-all {
  padding: 0.5rem 1rem;
  border-top: 1px solid var(--qm-light-border);
}

.qm-search-view-all-button {
  width: 100%;
  background: none;
  border: none;
  color: var(--qm-electric-blue);
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.5rem;
  border-radius: var(--qm-border-radius);
  cursor: pointer;
  transition: var(--qm-transition);
  
  &:hover {
    background: var(--qm-light-gray);
  }
  
  &:focus {
    outline: 2px solid var(--qm-electric-blue);
    outline-offset: 2px;
  }
}

.qm-search-no-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  background: var(--qm-white);
  border: 1px solid var(--qm-light-border);
  border-radius: var(--qm-border-radius-lg);
  box-shadow: var(--qm-shadow-xl);
  padding: 2rem 1rem;
  margin-top: 0.25rem;
  text-align: center;
}

.qm-search-no-results-icon {
  color: var(--qm-medium-gray);
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.qm-search-no-results-text {
  color: var(--qm-medium-gray);
  font-size: 0.875rem;
}

// Transition animations
.qm-search-suggestions-enter-active,
.qm-search-suggestions-leave-active {
  transition: all 0.2s ease;
}

.qm-search-suggestions-enter-from,
.qm-search-suggestions-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

// Dark mode support
[data-theme="dark"] {
  .qm-search-suggestions,
  .qm-search-no-results {
    background: var(--qm-bg-surface-900, #1e1e1e);
    border-color: var(--qm-border-dark, #374151);
  }
  
  .qm-search-suggestion {
    border-bottom-color: var(--qm-border-dark, #374151);
    
    &:hover,
    &.qm-search-suggestion-active {
      background: var(--qm-bg-surface-800, #2d2d2d);
    }
  }
  
  .qm-search-suggestion-title {
    color: var(--qm-text-50, #f8fafc);
  }
  
  .qm-search-suggestion-subtitle {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-search-suggestion-icon {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-search-view-all {
    border-top-color: var(--qm-border-dark, #374151);
  }
  
  .qm-search-view-all-button {
    &:hover {
      background: var(--qm-bg-surface-800, #2d2d2d);
    }
  }
  
  .qm-search-no-results-icon,
  .qm-search-no-results-text {
    color: var(--qm-text-400, #9ca3af);
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .qm-search-bar {
    &.qm-search-bar-prominent {
      .qm-search-bar-button {
        align-self: stretch;
      }
    }
  }
  
  .qm-search-suggestions {
    max-height: 250px;
  }
  
  .qm-search-suggestion {
    padding: 0.625rem 0.75rem;
  }
}
</style>