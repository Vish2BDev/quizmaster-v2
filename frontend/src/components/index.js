// ============================================================================
// QUIZ MASTER V2 - COMPONENT EXPORTS
// ============================================================================
// Central export file for all components following atomic design principles
// This file provides a single entry point for importing components

// ============================================================================
// ATOMS - Basic building blocks
// ============================================================================
export {
  QmBtn,
  QmInput,
  QmCard,
  QmToast,
  QmBadge,
  QmThemeToggle
} from './atoms'

// ============================================================================
// MOLECULES - Simple combinations of atoms
// ============================================================================
export {
  QuizCard,
  SearchBar,
  StatCard,
  FormField
} from './molecules'

// ============================================================================
// ORGANISMS - Complex UI components
// ============================================================================
export {
  QuizHeader,
  DashboardStats,
  AdminSidebar,
  QmToastContainer
} from './organisms'

// ============================================================================
// TEMPLATES - Page-level layout components
// ============================================================================
export {
  DashboardTemplate,
  QuizTemplate
} from './templates'

// ============================================================================
// LEGACY COMPONENTS (to be gradually migrated)
// ============================================================================
// These components exist in the current structure and will be
// gradually refactored into the atomic design system

// Layout Components (Legacy - Use DashboardTemplate instead)
export { default as AdminLayout } from './AdminLayout.vue' // @deprecated - Use DashboardTemplate
export { default as UserLayout } from './UserLayout.vue' // @deprecated - Use DashboardTemplate
export { default as DashboardLayout } from './layout/DashboardLayout.vue'
export { default as Sidebar } from './layout/Sidebar.vue'

// Feature Components
export { default as ExportButton } from './ExportButton.vue'
export { default as RealTimeEvents } from './RealTimeEvents.vue'
export { default as UserExport } from './UserExport.vue'
export { default as UserSearch } from './UserSearch.vue'

// UI Components
export { default as ChartCards } from './ui/ChartCards.vue'
export { default as Logout } from './ui/Logout.vue'

// ============================================================================
// COMPONENT GROUPS FOR CONVENIENCE
// ============================================================================

// All atomic components
export const Atoms = {
  QmBtn,
  QmInput,
  QmCard,
  QmToast,
  QmBadge,
  QmThemeToggle
}

// All molecule components
export const Molecules = {
  QuizCard,
  SearchBar,
  StatCard,
  FormField
}

// All organism components
export const Organisms = {
  QuizHeader,
  DashboardStats,
  AdminSidebar,
  QmToastContainer
}

// All template components
export const Templates = {
  DashboardTemplate,
  QuizTemplate
}

// ============================================================================
// USAGE EXAMPLES
// ============================================================================
/*
// Import individual components
// These circular imports have been removed to prevent dependency issues
// Components should be imported directly from their specific paths
*/