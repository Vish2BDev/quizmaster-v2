<template>
  <teleport to="body">
    <!-- Toast containers for each position -->
    <div
      v-for="position in Object.keys(POSITIONS)"
      :key="position"
      :class="[
        'qm-toast-container',
        `qm-toast-container--${position}`
      ]"
      v-show="getToastsByPosition(position).length > 0"
    >
      <transition-group
        name="qm-toast"
        tag="div"
        class="qm-toast-container__list"
      >
        <qm-toast
          v-for="toast in getToastsByPosition(position)"
          :key="toast.id"
          :type="toast.type"
          :title="toast.title"
          :message="toast.message"
          :closable="toast.closable"
          :clickable="toast.clickable"
          :show-progress="toast.showProgress"
          :progress="toast.progress"
          :icon="toast.icon"
          @close="removeToast(toast.id)"
          @click="handleToastClick(toast)"
          @mouseenter="toast.pauseOnHover && pauseToast(toast.id)"
          @mouseleave="toast.pauseOnHover && resumeToast(toast.id)"
          class="qm-toast-container__item"
        />
      </transition-group>
    </div>
  </teleport>
</template>

<script>
import { useToast } from '@/composables/useToast'
import QmToast from '../atoms/QmToast.vue'

export default {
  name: 'QmToastContainer',
  components: {
    QmToast
  },
  
  setup() {
    const {
      toasts,
      removeToast,
      pauseToast,
      resumeToast,
      handleToastClick,
      getToastsByPosition,
      POSITIONS
    } = useToast()
    
    return {
      toasts,
      removeToast,
      pauseToast,
      resumeToast,
      handleToastClick,
      getToastsByPosition,
      POSITIONS
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-toast-container {
  position: fixed;
  z-index: var(--qm-z-toast);
  pointer-events: none;
  
  // Position variants
  &--top-left {
    top: var(--qm-space-4);
    left: var(--qm-space-4);
  }
  
  &--top-center {
    top: var(--qm-space-4);
    left: 50%;
    transform: translateX(-50%);
  }
  
  &--top-right {
    top: var(--qm-space-4);
    right: var(--qm-space-4);
  }
  
  &--bottom-left {
    bottom: var(--qm-space-4);
    left: var(--qm-space-4);
  }
  
  &--bottom-center {
    bottom: var(--qm-space-4);
    left: 50%;
    transform: translateX(-50%);
  }
  
  &--bottom-right {
    bottom: var(--qm-space-4);
    right: var(--qm-space-4);
  }
  
  // Responsive adjustments
  @media (max-width: 640px) {
    &--top-left,
    &--top-right {
      top: var(--qm-space-2);
      left: var(--qm-space-2);
      right: var(--qm-space-2);
    }
    
    &--bottom-left,
    &--bottom-right {
      bottom: var(--qm-space-2);
      left: var(--qm-space-2);
      right: var(--qm-space-2);
    }
    
    &--top-center {
      top: var(--qm-space-2);
      left: var(--qm-space-2);
      right: var(--qm-space-2);
      transform: none;
    }
    
    &--bottom-center {
      bottom: var(--qm-space-2);
      left: var(--qm-space-2);
      right: var(--qm-space-2);
      transform: none;
    }
  }
}

.qm-toast-container__list {
  display: flex;
  flex-direction: column;
  gap: var(--qm-space-2);
  min-width: 320px;
  max-width: 480px;
  
  @media (max-width: 640px) {
    min-width: auto;
    max-width: none;
    width: 100%;
  }
}

.qm-toast-container__item {
  pointer-events: auto;
}

// Toast animations
.qm-toast-enter-active {
  transition: all var(--qm-duration-300) var(--qm-ease-out);
}

.qm-toast-leave-active {
  transition: all var(--qm-duration-200) var(--qm-ease-in);
}

.qm-toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.qm-toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

// Position-specific animations
.qm-toast-container--top-left,
.qm-toast-container--bottom-left {
  .qm-toast-enter-from,
  .qm-toast-leave-to {
    transform: translateX(-100%);
  }
}

.qm-toast-container--top-center,
.qm-toast-container--bottom-center {
  .qm-toast-enter-from {
    transform: translateY(-20px) scale(0.95);
  }
  
  .qm-toast-leave-to {
    transform: translateY(-20px) scale(0.95);
  }
}

.qm-toast-container--bottom-left,
.qm-toast-container--bottom-right,
.qm-toast-container--bottom-center {
  .qm-toast-container__list {
    flex-direction: column-reverse;
  }
}

// Move animation for list reordering
.qm-toast-move {
  transition: transform var(--qm-duration-200) var(--qm-ease-in-out);
}

// Reduced motion support
@media (prefers-reduced-motion: reduce) {
  .qm-toast-enter-active,
  .qm-toast-leave-active,
  .qm-toast-move {
    transition: none;
  }
  
  .qm-toast-enter-from,
  .qm-toast-leave-to {
    transform: none;
    opacity: 0;
  }
}

// High contrast mode
@media (prefers-contrast: high) {
  .qm-toast-container__item {
    border: 2px solid currentColor;
  }
}
</style>