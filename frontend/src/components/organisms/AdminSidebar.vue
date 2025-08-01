<template>
  <aside class="qm-admin-sidebar" :class="sidebarClasses">
    <!-- Sidebar Header -->
    <div class="qm-admin-sidebar-header">
      <div class="qm-admin-sidebar-logo">
        <div class="qm-admin-sidebar-logo-icon">
          <i class="fas fa-brain"></i>
        </div>
        <div v-if="!collapsed" class="qm-admin-sidebar-logo-text">
          <h1>QuizMaster</h1>
          <span>Admin Panel</span>
        </div>
      </div>
      
      <QmBtn
        variant="ghost"
        size="sm"
        :icon="collapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"
        class="qm-admin-sidebar-toggle"
        @click="toggleSidebar"
      />
    </div>
    
    <!-- User Profile Section -->
    <div class="qm-admin-sidebar-profile">
      <div class="qm-admin-sidebar-avatar">
        <img 
          v-if="user.avatar" 
          :src="user.avatar" 
          :alt="user.name"
          class="qm-admin-sidebar-avatar-img"
        />
        <div v-else class="qm-admin-sidebar-avatar-placeholder">
          <i class="fas fa-user"></i>
        </div>
        <div class="qm-admin-sidebar-status" :class="statusClasses">
          <div class="qm-admin-sidebar-status-dot"></div>
        </div>
      </div>
      
      <div v-if="!collapsed" class="qm-admin-sidebar-user-info">
        <div class="qm-admin-sidebar-user-name">{{ user.name }}</div>
        <div class="qm-admin-sidebar-user-role">{{ user.role }}</div>
        <QmBadge
          v-if="user.badge"
          :variant="user.badge.variant || 'primary'"
          size="xs"
          class="qm-admin-sidebar-user-badge"
        >
          {{ user.badge.text }}
        </QmBadge>
      </div>
    </div>
    
    <!-- Navigation Menu -->
    <nav class="qm-admin-sidebar-nav">
      <div class="qm-admin-sidebar-nav-section" v-for="section in processedNavigation" :key="section.key">
        <div v-if="section.title && !collapsed" class="qm-admin-sidebar-nav-title">
          {{ section.title }}
        </div>
        
        <ul class="qm-admin-sidebar-nav-list">
          <li 
            v-for="item in section.items" 
            :key="item.key"
            class="qm-admin-sidebar-nav-item"
          >
            <a 
              :href="item.href || '#'"
              :class="getNavItemClasses(item)"
              @click="handleNavClick(item, $event)"
            >
              <div class="qm-admin-sidebar-nav-icon">
                <i :class="item.icon"></i>
                <QmBadge
                  v-if="item.badge && !collapsed"
                  :variant="item.badge.variant || 'error'"
                  size="xs"
                  class="qm-admin-sidebar-nav-badge"
                >
                  {{ item.badge.text }}
                </QmBadge>
              </div>
              
              <span v-if="!collapsed" class="qm-admin-sidebar-nav-text">
                {{ item.label }}
              </span>
              
              <div v-if="item.children && !collapsed" class="qm-admin-sidebar-nav-arrow">
                <i :class="item.expanded ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </div>
            </a>
            
            <!-- Submenu -->
            <ul 
              v-if="item.children && item.expanded && !collapsed"
              class="qm-admin-sidebar-nav-submenu"
            >
              <li 
                v-for="child in item.children"
                :key="child.key"
                class="qm-admin-sidebar-nav-subitem"
              >
                <a 
                  :href="child.href || '#'"
                  :class="getNavItemClasses(child, true)"
                  @click="handleNavClick(child, $event)"
                >
                  <div class="qm-admin-sidebar-nav-subicon">
                    <i :class="child.icon || 'fas fa-circle'"></i>
                  </div>
                  <span class="qm-admin-sidebar-nav-subtext">{{ child.label }}</span>
                  <QmBadge
                    v-if="child.badge"
                    :variant="child.badge.variant || 'error'"
                    size="xs"
                    class="qm-admin-sidebar-nav-subbadge"
                  >
                    {{ child.badge.text }}
                  </QmBadge>
                </a>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </nav>
    
    <!-- Sidebar Footer -->
    <div class="qm-admin-sidebar-footer">
      <div v-if="stats && !collapsed" class="qm-admin-sidebar-stats">
        <div class="qm-admin-sidebar-stat" v-for="stat in stats" :key="stat.key">
          <div class="qm-admin-sidebar-stat-icon">
            <i :class="stat.icon"></i>
          </div>
          <div class="qm-admin-sidebar-stat-content">
            <div class="qm-admin-sidebar-stat-value">{{ stat.value }}</div>
            <div class="qm-admin-sidebar-stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
      
      <div class="qm-admin-sidebar-actions">
        <QmBtn
          variant="ghost"
          :size="collapsed ? 'sm' : 'md'"
          icon="fas fa-cog"
          :block="!collapsed"
          @click="handleSettings"
        >
          <span v-if="!collapsed">Settings</span>
        </QmBtn>
        
        <QmBtn
          variant="ghost"
          :size="collapsed ? 'sm' : 'md'"
          icon="fas fa-sign-out-alt"
          :block="!collapsed"
          @click="handleLogout"
        >
          <span v-if="!collapsed">Logout</span>
        </QmBtn>
      </div>
    </div>
    
    <!-- Tooltip for collapsed state -->
    <div v-if="collapsed && hoveredItem" class="qm-admin-sidebar-tooltip">
      {{ hoveredItem.label }}
    </div>
  </aside>
</template>

<script>
import { computed, ref, watch } from 'vue'
import QmBtn from '../atoms/QmBtn.vue'
import QmBadge from '../atoms/QmBadge.vue'

export default {
  name: 'AdminSidebar',
  components: {
    QmBtn,
    QmBadge
  },
  emits: ['toggle', 'navigate', 'settings', 'logout'],
  props: {
    user: {
      type: Object,
      required: true
      // Expected: { name: string, role: string, avatar?: string, status?: string, badge?: object }
    },
    navigation: {
      type: Array,
      required: true
      // Expected: [{ key: string, title?: string, items: [{ key: string, label: string, icon: string, href?: string, active?: boolean, children?: array }] }]
    },
    collapsed: {
      type: Boolean,
      default: false
    },
    activeRoute: {
      type: String,
      default: null
    },
    stats: {
      type: Array,
      default: () => []
      // Expected: [{ key: string, value: string|number, label: string, icon: string }]
    },
    theme: {
      type: String,
      default: 'light',
      validator: (value) => ['light', 'dark'].includes(value)
    }
  },
  setup(props, { emit }) {
    const hoveredItem = ref(null)
    const expandedItems = ref(new Set())
    
    const sidebarClasses = computed(() => {
      return [
        'qm-admin-sidebar',
        {
          'qm-admin-sidebar-collapsed': props.collapsed,
          'qm-admin-sidebar-dark': props.theme === 'dark'
        }
      ]
    })
    
    const statusClasses = computed(() => {
      const status = props.user.status || 'online'
      return [
        'qm-admin-sidebar-status',
        `qm-admin-sidebar-status-${status}`
      ]
    })
    
    const processedNavigation = computed(() => {
      return props.navigation.map(section => {
        return {
          ...section,
          items: section.items.map(item => {
            return {
              ...item,
              expanded: expandedItems.value.has(item.key),
              active: isItemActive(item)
            }
          })
        }
      })
    })
    
    const isItemActive = (item) => {
      if (item.active) return true
      if (props.activeRoute && item.href) {
        return props.activeRoute === item.href || props.activeRoute.startsWith(item.href)
      }
      
      // Check if any child is active
      if (item.children) {
        return item.children.some(child => isItemActive(child))
      }
      
      return false
    }
    
    const getNavItemClasses = (item, isChild = false) => {
      const baseClass = isChild ? 'qm-admin-sidebar-nav-sublink' : 'qm-admin-sidebar-nav-link'
      
      return [
        baseClass,
        {
          [`${baseClass}-active`]: isItemActive(item),
          [`${baseClass}-disabled`]: item.disabled,
          [`${baseClass}-has-children`]: item.children && !isChild
        }
      ]
    }
    
    const toggleSidebar = () => {
      emit('toggle', !props.collapsed)
    }
    
    const handleNavClick = (item, event) => {
      if (item.disabled) {
        event.preventDefault()
        return
      }
      
      // Handle submenu toggle
      if (item.children && !props.collapsed) {
        event.preventDefault()
        toggleSubmenu(item.key)
        return
      }
      
      // Handle navigation
      if (item.href && item.href !== '#') {
        emit('navigate', item)
      } else {
        event.preventDefault()
      }
      
      // Handle custom click handler
      if (item.onClick) {
        item.onClick(item, event)
      }
    }
    
    const toggleSubmenu = (itemKey) => {
      const newExpanded = new Set(expandedItems.value)
      if (newExpanded.has(itemKey)) {
        newExpanded.delete(itemKey)
      } else {
        newExpanded.add(itemKey)
      }
      expandedItems.value = newExpanded
    }
    
    const handleSettings = () => {
      emit('settings')
    }
    
    const handleLogout = () => {
      emit('logout')
    }
    
    const handleMouseEnter = (item) => {
      if (props.collapsed) {
        hoveredItem.value = item
      }
    }
    
    const handleMouseLeave = () => {
      hoveredItem.value = null
    }
    
    // Auto-expand active parent items
    watch(() => props.activeRoute, () => {
      const newExpanded = new Set(expandedItems.value)
      
      props.navigation.forEach(section => {
        section.items.forEach(item => {
          if (item.children) {
            const hasActiveChild = item.children.some(child => isItemActive(child))
            if (hasActiveChild) {
              newExpanded.add(item.key)
            }
          }
        })
      })
      
      expandedItems.value = newExpanded
    }, { immediate: true })
    
    return {
      sidebarClasses,
      statusClasses,
      processedNavigation,
      hoveredItem,
      getNavItemClasses,
      toggleSidebar,
      handleNavClick,
      handleSettings,
      handleLogout,
      handleMouseEnter,
      handleMouseLeave
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-admin-sidebar {
  width: 280px;
  height: 100vh;
  background: var(--qm-white);
  border-right: 1px solid var(--qm-light-gray);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: relative;
  
  &.qm-admin-sidebar-collapsed {
    width: 80px;
  }
}

.qm-admin-sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 1rem;
  border-bottom: 1px solid var(--qm-light-gray);
}

.qm-admin-sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.qm-admin-sidebar-logo-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, var(--qm-electric-blue), var(--qm-royal-purple));
  border-radius: var(--qm-border-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--qm-white);
  font-size: 1.25rem;
  flex-shrink: 0;
}

.qm-admin-sidebar-logo-text {
  min-width: 0;
  
  h1 {
    font-family: var(--qm-font-heading);
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--qm-dark-gray);
    margin: 0;
    line-height: 1.2;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  span {
    font-size: 0.75rem;
    color: var(--qm-medium-gray);
    font-weight: 500;
  }
}

.qm-admin-sidebar-toggle {
  flex-shrink: 0;
}

.qm-admin-sidebar-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid var(--qm-light-gray);
  position: relative;
}

.qm-admin-sidebar-avatar {
  position: relative;
  flex-shrink: 0;
}

.qm-admin-sidebar-avatar-img,
.qm-admin-sidebar-avatar-placeholder {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qm-admin-sidebar-avatar-img {
  object-fit: cover;
}

.qm-admin-sidebar-avatar-placeholder {
  background: var(--qm-light-gray);
  color: var(--qm-medium-gray);
  font-size: 1rem;
}

.qm-admin-sidebar-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 0.75rem;
  height: 0.75rem;
  border: 2px solid var(--qm-white);
  border-radius: 50%;
}

.qm-admin-sidebar-status-dot {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  
  .qm-admin-sidebar-status-online & {
    background: var(--qm-success-green);
  }
  
  .qm-admin-sidebar-status-away & {
    background: var(--qm-warning-yellow);
  }
  
  .qm-admin-sidebar-status-busy & {
    background: var(--qm-error-red);
  }
  
  .qm-admin-sidebar-status-offline & {
    background: var(--qm-medium-gray);
  }
}

.qm-admin-sidebar-user-info {
  min-width: 0;
  flex: 1;
}

.qm-admin-sidebar-user-name {
  font-weight: 600;
  color: var(--qm-dark-gray);
  font-size: 0.875rem;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.qm-admin-sidebar-user-role {
  font-size: 0.75rem;
  color: var(--qm-medium-gray);
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.qm-admin-sidebar-user-badge {
  display: inline-block;
}

.qm-admin-sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

.qm-admin-sidebar-nav-section {
  margin-bottom: 1.5rem;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.qm-admin-sidebar-nav-title {
  padding: 0 1rem 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--qm-medium-gray);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.qm-admin-sidebar-nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.qm-admin-sidebar-nav-item {
  margin-bottom: 0.25rem;
}

.qm-admin-sidebar-nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: var(--qm-dark-gray);
  text-decoration: none;
  transition: all 0.2s ease;
  position: relative;
  
  &:hover {
    background: var(--qm-light-gray);
    color: var(--qm-electric-blue);
  }
  
  &.qm-admin-sidebar-nav-link-active {
    background: rgba(14, 165, 233, 0.1);
    color: var(--qm-electric-blue);
    
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background: var(--qm-electric-blue);
    }
  }
  
  &.qm-admin-sidebar-nav-link-disabled {
    opacity: 0.5;
    pointer-events: none;
  }
}

.qm-admin-sidebar-nav-icon {
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
  
  i {
    font-size: 1rem;
  }
}

.qm-admin-sidebar-nav-badge {
  position: absolute;
  top: -0.25rem;
  right: -0.25rem;
}

.qm-admin-sidebar-nav-text {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.qm-admin-sidebar-nav-arrow {
  width: 1rem;
  height: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  i {
    font-size: 0.75rem;
    transition: transform 0.2s ease;
  }
}

.qm-admin-sidebar-nav-submenu {
  list-style: none;
  margin: 0;
  padding: 0;
  background: rgba(0, 0, 0, 0.02);
}

.qm-admin-sidebar-nav-subitem {
  margin-bottom: 0.125rem;
}

.qm-admin-sidebar-nav-sublink {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem 0.5rem 3rem;
  color: var(--qm-medium-gray);
  text-decoration: none;
  font-size: 0.8125rem;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--qm-light-gray);
    color: var(--qm-electric-blue);
  }
  
  &.qm-admin-sidebar-nav-sublink-active {
    background: rgba(14, 165, 233, 0.05);
    color: var(--qm-electric-blue);
  }
}

.qm-admin-sidebar-nav-subicon {
  width: 0.75rem;
  height: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  i {
    font-size: 0.5rem;
  }
}

.qm-admin-sidebar-nav-subtext {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.qm-admin-sidebar-nav-subbadge {
  flex-shrink: 0;
}

.qm-admin-sidebar-footer {
  border-top: 1px solid var(--qm-light-gray);
  padding: 1rem;
}

.qm-admin-sidebar-stats {
  margin-bottom: 1rem;
}

.qm-admin-sidebar-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  
  &:not(:last-child) {
    border-bottom: 1px solid var(--qm-light-gray);
  }
}

.qm-admin-sidebar-stat-icon {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--qm-light-gray);
  border-radius: var(--qm-border-radius);
  color: var(--qm-medium-gray);
  font-size: 0.75rem;
  flex-shrink: 0;
}

.qm-admin-sidebar-stat-content {
  flex: 1;
  min-width: 0;
}

.qm-admin-sidebar-stat-value {
  font-weight: 600;
  color: var(--qm-dark-gray);
  font-size: 0.875rem;
  line-height: 1.2;
}

.qm-admin-sidebar-stat-label {
  font-size: 0.75rem;
  color: var(--qm-medium-gray);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.qm-admin-sidebar-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.qm-admin-sidebar-tooltip {
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  background: var(--qm-dark-gray);
  color: var(--qm-white);
  padding: 0.5rem 0.75rem;
  border-radius: var(--qm-border-radius);
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 1000;
  margin-left: 0.5rem;
  
  &::before {
    content: '';
    position: absolute;
    right: 100%;
    top: 50%;
    transform: translateY(-50%);
    border: 4px solid transparent;
    border-right-color: var(--qm-dark-gray);
  }
}

// Dark mode support
[data-theme="dark"] {
  .qm-admin-sidebar {
    background: var(--qm-bg-surface-900, #1a1a1a);
    border-right-color: var(--qm-bg-surface-700, #404040);
  }
  
  .qm-admin-sidebar-header {
    border-bottom-color: var(--qm-bg-surface-700, #404040);
  }
  
  .qm-admin-sidebar-logo-text h1 {
    color: var(--qm-text-50, #f8fafc);
  }
  
  .qm-admin-sidebar-logo-text span {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-admin-sidebar-profile {
    border-bottom-color: var(--qm-bg-surface-700, #404040);
  }
  
  .qm-admin-sidebar-avatar-placeholder {
    background: var(--qm-bg-surface-700, #404040);
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-admin-sidebar-status {
    border-color: var(--qm-bg-surface-900, #1a1a1a);
  }
  
  .qm-admin-sidebar-user-name {
    color: var(--qm-text-200, #e5e7eb);
  }
  
  .qm-admin-sidebar-user-role {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-admin-sidebar-nav-title {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-admin-sidebar-nav-link {
    color: var(--qm-text-300, #d1d5db);
    
    &:hover {
      background: var(--qm-bg-surface-800, #2d2d2d);
    }
  }
  
  .qm-admin-sidebar-nav-submenu {
    background: rgba(255, 255, 255, 0.02);
  }
  
  .qm-admin-sidebar-nav-sublink {
    color: var(--qm-text-400, #9ca3af);
    
    &:hover {
      background: var(--qm-bg-surface-800, #2d2d2d);
    }
  }
  
  .qm-admin-sidebar-footer {
    border-top-color: var(--qm-bg-surface-700, #404040);
  }
  
  .qm-admin-sidebar-stat {
    &:not(:last-child) {
      border-bottom-color: var(--qm-bg-surface-700, #404040);
    }
  }
  
  .qm-admin-sidebar-stat-icon {
    background: var(--qm-bg-surface-700, #404040);
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-admin-sidebar-stat-value {
    color: var(--qm-text-200, #e5e7eb);
  }
  
  .qm-admin-sidebar-stat-label {
    color: var(--qm-text-400, #9ca3af);
  }
}

// Responsive design
@media (max-width: 768px) {
  .qm-admin-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    
    &.qm-admin-sidebar-open {
      transform: translateX(0);
    }
  }
}
</style>