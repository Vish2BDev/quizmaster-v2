<template>
  <div class="dashboard-template">
    <!-- Header Section -->
    <header class="dashboard-header" v-if="showHeader">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <div class="page-title-section">
              <h1 class="page-title">{{ title }}</h1>
              <p class="page-subtitle" v-if="subtitle">{{ subtitle }}</p>
              <nav aria-label="breadcrumb" v-if="breadcrumbs?.length">
                <ol class="breadcrumb">
                  <li 
                    v-for="(crumb, index) in breadcrumbs" 
                    :key="index"
                    class="breadcrumb-item"
                    :class="{ active: index === breadcrumbs.length - 1 }"
                  >
                    <router-link v-if="crumb.to && index !== breadcrumbs.length - 1" :to="crumb.to">
                      <i v-if="crumb.icon" :class="crumb.icon" class="me-1"></i>
                      {{ crumb.text }}
                    </router-link>
                    <span v-else>
                      <i v-if="crumb.icon" :class="crumb.icon" class="me-1"></i>
                      {{ crumb.text }}
                    </span>
                  </li>
                </ol>
              </nav>
            </div>
          </div>
          <div class="col-md-4 text-end">
            <div class="header-actions">
              <slot name="header-actions">
                <QmThemeToggle v-if="showThemeToggle" size="sm" />
              </slot>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Stats Section -->
    <section class="dashboard-stats" v-if="showStats">
      <div class="container-fluid">
        <DashboardStats
          :title="statsTitle"
          :subtitle="statsSubtitle"
          :stats="stats"
          :loading="statsLoading"
          :columns="statsColumns"
          @refresh="$emit('refresh-stats')"
        >
          <template #actions>
            <slot name="stats-actions"></slot>
          </template>
        </DashboardStats>
      </div>
    </section>

    <!-- Main Content -->
    <main class="dashboard-main">
      <div class="container-fluid">
        <div class="row">
          <!-- Sidebar -->
          <aside 
            v-if="showSidebar" 
            class="col-lg-3 col-xl-2 dashboard-sidebar"
            :class="sidebarClasses"
          >
            <slot name="sidebar">
              <div class="sidebar-content">
                <div class="sidebar-section" v-if="quickActions?.length">
                  <h6 class="sidebar-title">Quick Actions</h6>
                  <div class="quick-actions">
                    <QmBtn
                      v-for="action in quickActions"
                      :key="action.id"
                      :variant="action.variant || 'outline-primary'"
                      :size="action.size || 'sm'"
                      :icon="action.icon"
                      class="w-100 mb-2"
                      @click="$emit('quick-action', action)"
                    >
                      {{ action.label }}
                    </QmBtn>
                  </div>
                </div>

                <div class="sidebar-section" v-if="filters?.length">
                  <h6 class="sidebar-title">Filters</h6>
                  <div class="filters">
                    <FormField
                      v-for="filter in filters"
                      :key="filter.id"
                      :label="filter.label"
                      :type="filter.type"
                      :options="filter.options"
                      :model-value="filter.value"
                      :placeholder="filter.placeholder"
                      class="mb-3"
                      @update:model-value="$emit('filter-change', filter.id, $event)"
                    />
                  </div>
                </div>
              </div>
            </slot>
          </aside>

          <!-- Content Area -->
          <div 
            class="dashboard-content"
            :class="contentClasses"
          >
            <!-- Search Bar -->
            <div class="content-header" v-if="showSearch || $slots['content-header']">
              <div class="row align-items-center mb-4">
                <div class="col-md-8" v-if="showSearch">
                  <SearchBar
                    :model-value="searchQuery"
                    :placeholder="searchPlaceholder"
                    :suggestions="searchSuggestions"
                    :loading="searchLoading"
                    @update:model-value="$emit('search', $event)"
                    @search="$emit('search-submit', $event)"
                    @suggestion-select="$emit('search-suggestion', $event)"
                  />
                </div>
                <div class="col-md-4 text-end">
                  <slot name="content-header"></slot>
                </div>
              </div>
            </div>

            <!-- Main Content Slot -->
            <div class="content-body">
              <slot name="content">
                <div class="empty-state text-center py-5" v-if="showEmptyState">
                  <div class="empty-icon mb-3">
                    <i :class="emptyStateIcon" class="fa-3x text-muted"></i>
                  </div>
                  <h4 class="empty-title">{{ emptyStateTitle }}</h4>
                  <p class="empty-description text-muted">{{ emptyStateDescription }}</p>
                  <QmBtn
                    v-if="emptyStateAction"
                    :variant="emptyStateAction.variant || 'primary'"
                    :icon="emptyStateAction.icon"
                    @click="$emit('empty-action', emptyStateAction)"
                  >
                    {{ emptyStateAction.label }}
                  </QmBtn>
                </div>
              </slot>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="dashboard-footer" v-if="showFooter || $slots.footer">
      <div class="container-fluid">
        <slot name="footer">
          <div class="row align-items-center">
            <div class="col-md-6">
              <p class="footer-text mb-0">{{ footerText }}</p>
            </div>
            <div class="col-md-6 text-end">
              <small class="text-muted" v-if="lastUpdated">
                Last updated: {{ formatDate(lastUpdated) }}
              </small>
            </div>
          </div>
        </slot>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed } from 'vue'
import QmBtn from '@/components/atoms/QmBtn.vue'
import QmThemeToggle from '@/components/atoms/QmThemeToggle.vue'
import FormField from '@/components/molecules/FormField.vue'
import SearchBar from '@/components/molecules/SearchBar.vue'
import DashboardStats from '@/components/organisms/DashboardStats.vue'

export default {
  name: 'DashboardTemplate',
  components: {
    QmBtn,
    QmThemeToggle,
    FormField,
    SearchBar,
    DashboardStats
  },
  props: {
    // Header props
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    },
    breadcrumbs: {
      type: Array,
      default: () => []
    },
    showHeader: {
      type: Boolean,
      default: true
    },
    showThemeToggle: {
      type: Boolean,
      default: true
    },

    // Stats props
    showStats: {
      type: Boolean,
      default: false
    },
    statsTitle: {
      type: String,
      default: 'Overview'
    },
    statsSubtitle: {
      type: String,
      default: ''
    },
    stats: {
      type: Array,
      default: () => []
    },
    statsLoading: {
      type: Boolean,
      default: false
    },
    statsColumns: {
      type: Object,
      default: () => ({ sm: 1, md: 2, lg: 4 })
    },

    // Layout props
    showSidebar: {
      type: Boolean,
      default: false
    },
    sidebarCollapsed: {
      type: Boolean,
      default: false
    },
    quickActions: {
      type: Array,
      default: () => []
    },
    filters: {
      type: Array,
      default: () => []
    },

    // Search props
    showSearch: {
      type: Boolean,
      default: false
    },
    searchQuery: {
      type: String,
      default: ''
    },
    searchPlaceholder: {
      type: String,
      default: 'Search...'
    },
    searchSuggestions: {
      type: Array,
      default: () => []
    },
    searchLoading: {
      type: Boolean,
      default: false
    },

    // Empty state props
    showEmptyState: {
      type: Boolean,
      default: false
    },
    emptyStateIcon: {
      type: String,
      default: 'fas fa-inbox'
    },
    emptyStateTitle: {
      type: String,
      default: 'No data available'
    },
    emptyStateDescription: {
      type: String,
      default: 'There is no data to display at the moment.'
    },
    emptyStateAction: {
      type: Object,
      default: null
    },

    // Footer props
    showFooter: {
      type: Boolean,
      default: false
    },
    footerText: {
      type: String,
      default: '© 2024 Quiz Master V2. All rights reserved.'
    },
    lastUpdated: {
      type: [String, Date],
      default: null
    }
  },
  emits: [
    'refresh-stats',
    'quick-action',
    'filter-change',
    'search',
    'search-submit',
    'search-suggestion',
    'empty-action'
  ],
  setup(props) {
    const sidebarClasses = computed(() => ({
      'sidebar-collapsed': props.sidebarCollapsed
    }))

    const contentClasses = computed(() => {
      if (!props.showSidebar) {
        return 'col-12'
      }
      return props.sidebarCollapsed ? 'col-lg-11 col-xl-11' : 'col-lg-9 col-xl-10'
    })

    const formatDate = (date) => {
      if (!date) return ''
      const d = new Date(date)
      return d.toLocaleString()
    }

    return {
      sidebarClasses,
      contentClasses,
      formatDate
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/qm-theme';

.dashboard-template {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--qm-bg-primary);
}

// Header Styles
.dashboard-header {
  background: var(--qm-bg-surface);
  border-bottom: 1px solid var(--qm-border-light);
  padding: var(--qm-spacing-lg) 0;
  box-shadow: var(--qm-shadow-sm);

  .page-title {
    color: var(--qm-text-primary);
    font-size: var(--qm-font-size-2xl);
    font-weight: var(--qm-font-weight-bold);
    margin-bottom: var(--qm-spacing-xs);
  }

  .page-subtitle {
    color: var(--qm-text-secondary);
    font-size: var(--qm-font-size-lg);
    margin-bottom: var(--qm-spacing-sm);
  }

  .breadcrumb {
    background: transparent;
    padding: 0;
    margin-bottom: 0;
    font-size: var(--qm-font-size-sm);

    .breadcrumb-item {
      color: var(--qm-text-tertiary);

      &.active {
        color: var(--qm-text-secondary);
      }

      a {
        color: var(--qm-color-primary);
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: var(--qm-spacing-sm);
  }
}

// Stats Section
.dashboard-stats {
  background: var(--qm-bg-primary);
  padding: var(--qm-spacing-lg) 0;
}

// Main Content
.dashboard-main {
  flex: 1;
  padding: var(--qm-spacing-lg) 0;
}

// Sidebar Styles
.dashboard-sidebar {
  background: var(--qm-bg-surface);
  border-right: 1px solid var(--qm-border-light);
  padding: var(--qm-spacing-lg);
  transition: all var(--qm-transition-base);

  &.sidebar-collapsed {
    transform: translateX(-100%);
    
    @media (min-width: 992px) {
      transform: none;
      width: 60px;
      overflow: hidden;
    }
  }

  .sidebar-content {
    position: sticky;
    top: var(--qm-spacing-lg);
  }

  .sidebar-section {
    margin-bottom: var(--qm-spacing-xl);

    &:last-child {
      margin-bottom: 0;
    }
  }

  .sidebar-title {
    color: var(--qm-text-primary);
    font-size: var(--qm-font-size-sm);
    font-weight: var(--qm-font-weight-semibold);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: var(--qm-spacing-md);
    padding-bottom: var(--qm-spacing-xs);
    border-bottom: 1px solid var(--qm-border-light);
  }

  .quick-actions {
    display: flex;
    flex-direction: column;
    gap: var(--qm-spacing-xs);
  }
}

// Content Area
.dashboard-content {
  padding: 0 var(--qm-spacing-lg);

  .content-header {
    margin-bottom: var(--qm-spacing-lg);
  }

  .content-body {
    background: var(--qm-bg-surface);
    border-radius: var(--qm-border-radius-lg);
    padding: var(--qm-spacing-lg);
    box-shadow: var(--qm-shadow-sm);
    min-height: 400px;
  }
}

// Empty State
.empty-state {
  .empty-icon {
    opacity: 0.5;
  }

  .empty-title {
    color: var(--qm-text-primary);
    font-size: var(--qm-font-size-xl);
    font-weight: var(--qm-font-weight-semibold);
    margin-bottom: var(--qm-spacing-sm);
  }

  .empty-description {
    font-size: var(--qm-font-size-base);
    margin-bottom: var(--qm-spacing-lg);
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
  }
}

// Footer
.dashboard-footer {
  background: var(--qm-bg-surface);
  border-top: 1px solid var(--qm-border-light);
  padding: var(--qm-spacing-md) 0;
  margin-top: auto;

  .footer-text {
    color: var(--qm-text-secondary);
    font-size: var(--qm-font-size-sm);
  }
}

// Responsive Design
@media (max-width: 991.98px) {
  .dashboard-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1050;
    transform: translateX(-100%);
    
    &:not(.sidebar-collapsed) {
      transform: translateX(0);
    }
  }

  .dashboard-content {
    padding: 0 var(--qm-spacing-md);
  }

  .dashboard-header {
    padding: var(--qm-spacing-md) 0;

    .page-title {
      font-size: var(--qm-font-size-xl);
    }
  }
}

@media (max-width: 575.98px) {
  .dashboard-header {
    .header-actions {
      margin-top: var(--qm-spacing-sm);
    }
  }

  .content-header {
    .row {
      flex-direction: column;
      gap: var(--qm-spacing-sm);
    }
  }
}

// Dark mode support
@media (prefers-color-scheme: dark) {
  .dashboard-template {
    background: var(--qm-bg-primary-dark);
  }

  .dashboard-header,
  .dashboard-sidebar {
    background: var(--qm-bg-surface-dark);
    border-color: var(--qm-border-light-dark);
  }

  .content-body {
    background: var(--qm-bg-surface-dark);
  }

  .dashboard-footer {
    background: var(--qm-bg-surface-dark);
    border-color: var(--qm-border-light-dark);
  }
}

// High contrast mode
@media (prefers-contrast: high) {
  .dashboard-header,
  .dashboard-sidebar,
  .dashboard-footer {
    border-width: 2px;
  }

  .content-body {
    border: 2px solid var(--qm-border-light);
  }
}

// Reduced motion
@media (prefers-reduced-motion: reduce) {
  .dashboard-sidebar {
    transition: none;
  }
}
</style>