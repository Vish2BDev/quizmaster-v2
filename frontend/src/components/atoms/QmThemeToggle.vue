<template>
  <button
    :class="[
      'qm-theme-toggle',
      `qm-theme-toggle--${size}`,
      {
        'qm-theme-toggle--disabled': disabled,
        'qm-theme-toggle--loading': loading
      }
    ]"
    :disabled="disabled || loading"
    :aria-label="ariaLabel"
    :title="title"
    @click="toggleTheme"
    type="button"
  >
    <!-- Loading State -->
    <div v-if="loading" class="qm-theme-toggle__loading">
      <div class="qm-theme-toggle__spinner"></div>
    </div>
    
    <!-- Theme Icons -->
    <div v-else class="qm-theme-toggle__icons">
      <!-- Sun Icon (Light Mode) -->
      <svg
        v-show="currentTheme === 'light'"
        class="qm-theme-toggle__icon qm-theme-toggle__icon--sun"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
        ></path>
      </svg>
      
      <!-- Moon Icon (Dark Mode) -->
      <svg
        v-show="currentTheme === 'dark'"
        class="qm-theme-toggle__icon qm-theme-toggle__icon--moon"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
        ></path>
      </svg>
      
      <!-- Auto Icon (System Preference) -->
      <svg
        v-show="currentTheme === 'auto'"
        class="qm-theme-toggle__icon qm-theme-toggle__icon--auto"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
        ></path>
      </svg>
    </div>
    
    <!-- Label (optional) -->
    <span v-if="showLabel" class="qm-theme-toggle__label">
      {{ labelText }}
    </span>
  </button>
</template>

<script>
export default {
  name: 'QmThemeToggle',
  props: {
    // Size variants
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md', 'lg'].includes(value)
    },
    
    // States
    disabled: {
      type: Boolean,
      default: false
    },
    
    loading: {
      type: Boolean,
      default: false
    },
    
    // Theme options
    enableAuto: {
      type: Boolean,
      default: true
    },
    
    // Label options
    showLabel: {
      type: Boolean,
      default: false
    },
    
    // Accessibility
    ariaLabel: {
      type: String,
      default: 'Toggle theme'
    },
    
    // Storage key for persistence
    storageKey: {
      type: String,
      default: 'qm-theme'
    }
  },
  
  data() {
    return {
      currentTheme: 'auto',
      systemPrefersDark: false
    }
  },
  
  computed: {
    title() {
      const themes = {
        light: 'Switch to dark mode',
        dark: this.enableAuto ? 'Switch to auto mode' : 'Switch to light mode',
        auto: 'Switch to light mode'
      }
      return themes[this.currentTheme] || 'Toggle theme'
    },
    
    labelText() {
      const labels = {
        light: 'Light',
        dark: 'Dark',
        auto: 'Auto'
      }
      return labels[this.currentTheme] || 'Theme'
    },
    
    effectiveTheme() {
      if (this.currentTheme === 'auto') {
        return this.systemPrefersDark ? 'dark' : 'light'
      }
      return this.currentTheme
    }
  },
  
  mounted() {
    this.initializeTheme()
    this.setupSystemPreferenceListener()
  },
  
  beforeUnmount() {
    this.cleanupSystemPreferenceListener()
  },
  
  methods: {
    initializeTheme() {
      // Load saved theme from localStorage
      const savedTheme = localStorage.getItem(this.storageKey)
      
      if (savedTheme && ['light', 'dark', 'auto'].includes(savedTheme)) {
        this.currentTheme = savedTheme
      } else {
        // Default to auto if no saved preference
        this.currentTheme = 'auto'
      }
      
      // Check system preference
      this.updateSystemPreference()
      
      // Apply theme
      this.applyTheme()
    },
    
    setupSystemPreferenceListener() {
      if (window.matchMedia) {
        this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
        this.mediaQuery.addEventListener('change', this.handleSystemPreferenceChange)
        this.updateSystemPreference()
      }
    },
    
    cleanupSystemPreferenceListener() {
      if (this.mediaQuery) {
        this.mediaQuery.removeEventListener('change', this.handleSystemPreferenceChange)
      }
    },
    
    handleSystemPreferenceChange(e) {
      this.systemPrefersDark = e.matches
      if (this.currentTheme === 'auto') {
        this.applyTheme()
      }
    },
    
    updateSystemPreference() {
      if (window.matchMedia) {
        this.systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      }
    },
    
    toggleTheme() {
      if (this.disabled || this.loading) return
      
      // Cycle through themes
      if (this.enableAuto) {
        const themes = ['light', 'dark', 'auto']
        const currentIndex = themes.indexOf(this.currentTheme)
        this.currentTheme = themes[(currentIndex + 1) % themes.length]
      } else {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light'
      }
      
      // Save to localStorage
      localStorage.setItem(this.storageKey, this.currentTheme)
      
      // Apply theme
      this.applyTheme()
      
      // Emit event
      this.$emit('theme-changed', {
        theme: this.currentTheme,
        effectiveTheme: this.effectiveTheme
      })
    },
    
    applyTheme() {
      const htmlElement = document.documentElement
      
      // Remove existing theme attributes
      htmlElement.removeAttribute('data-theme')
      
      // Apply new theme
      if (this.effectiveTheme === 'dark') {
        htmlElement.setAttribute('data-theme', 'dark')
      }
      
      // Add transition class for smooth theme switching
      htmlElement.classList.add('qm-theme-transitioning')
      
      // Remove transition class after animation
      setTimeout(() => {
        htmlElement.classList.remove('qm-theme-transitioning')
      }, 300)
    },
    
    // Public method to set theme programmatically
    setTheme(theme) {
      if (['light', 'dark', 'auto'].includes(theme)) {
        this.currentTheme = theme
        localStorage.setItem(this.storageKey, theme)
        this.applyTheme()
        this.$emit('theme-changed', {
          theme: this.currentTheme,
          effectiveTheme: this.effectiveTheme
        })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-theme-toggle {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--qm-space-2);
  border: 1px solid var(--qm-border-primary);
  border-radius: var(--qm-radius-md);
  background: var(--qm-bg-surface-100);
  color: var(--qm-text-primary);
  font-family: var(--qm-font-sans);
  font-weight: var(--qm-font-medium);
  cursor: pointer;
  transition: var(--qm-transition-all);
  
  &:hover:not(:disabled) {
    background: var(--qm-bg-surface-200);
    border-color: var(--qm-border-secondary);
    transform: translateY(-1px);
    box-shadow: var(--qm-shadow-sm);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
    box-shadow: var(--qm-shadow-xs);
  }
  
  &:focus-visible {
    outline: 2px solid var(--qm-electric-blue);
    outline-offset: 2px;
  }
  
  // Size variants
  &--sm {
    padding: var(--qm-space-1-5) var(--qm-space-2-5);
    font-size: var(--qm-text-sm);
    
    .qm-theme-toggle__icon {
      width: 16px;
      height: 16px;
    }
  }
  
  &--md {
    padding: var(--qm-space-2) var(--qm-space-3);
    font-size: var(--qm-text-base);
    
    .qm-theme-toggle__icon {
      width: 20px;
      height: 20px;
    }
  }
  
  &--lg {
    padding: var(--qm-space-3) var(--qm-space-4);
    font-size: var(--qm-text-lg);
    
    .qm-theme-toggle__icon {
      width: 24px;
      height: 24px;
    }
  }
  
  // States
  &--disabled {
    opacity: 0.5;
    cursor: not-allowed;
    
    &:hover {
      transform: none;
      box-shadow: none;
    }
  }
  
  &--loading {
    cursor: wait;
  }
}

.qm-theme-toggle__icons {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qm-theme-toggle__icon {
  transition: var(--qm-transition-all);
  
  &--sun {
    color: var(--qm-warning-yellow);
  }
  
  &--moon {
    color: var(--qm-info-blue);
  }
  
  &--auto {
    color: var(--qm-text-secondary);
  }
}

.qm-theme-toggle__loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.qm-theme-toggle__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--qm-border-primary);
  border-top: 2px solid var(--qm-electric-blue);
  border-radius: 50%;
  animation: qm-spin var(--qm-duration-1000) linear infinite;
}

.qm-theme-toggle__label {
  font-size: inherit;
  font-weight: inherit;
  color: inherit;
}

// Dark mode styles
[data-theme="dark"] .qm-theme-toggle {
  background: var(--qm-bg-surface-800);
  border-color: var(--qm-border-primary);
  
  &:hover:not(:disabled) {
    background: var(--qm-bg-surface-700);
    border-color: var(--qm-border-secondary);
  }
}

// Theme transition
.qm-theme-transitioning * {
  transition: background-color var(--qm-duration-300) var(--qm-ease-in-out),
              border-color var(--qm-duration-300) var(--qm-ease-in-out),
              color var(--qm-duration-300) var(--qm-ease-in-out) !important;
}

// Spin animation
@keyframes qm-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

// Reduced motion
@media (prefers-reduced-motion: reduce) {
  .qm-theme-toggle {
    transition: none;
  }
  
  .qm-theme-toggle__icon {
    transition: none;
  }
  
  .qm-theme-toggle__spinner {
    animation: none;
  }
}
</style>