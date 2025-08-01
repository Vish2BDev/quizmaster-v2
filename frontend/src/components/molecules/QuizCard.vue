<template>
  <QmCard
    :variant="cardVariant"
    :hover="!disabled"
    :clickable="clickable"
    :disabled="disabled"
    :loading="loading"
    class="qm-quiz-card"
    @click="handleCardClick"
  >
    <template #header>
      <div class="qm-quiz-card-header">
        <div class="qm-quiz-card-meta">
          <QmBadge 
            :variant="difficultyVariant" 
            size="sm" 
            shape="pill"
            :icon="difficultyIcon"
          >
            {{ quiz.difficulty }}
          </QmBadge>
          <QmBadge 
            variant="default" 
            size="sm" 
            shape="pill"
            icon="fas fa-clock"
          >
            {{ formatDuration(quiz.duration) }}
          </QmBadge>
          <QmBadge 
            variant="info" 
            size="sm" 
            shape="pill"
            icon="fas fa-question-circle"
          >
            {{ quiz.questionCount }} questions
          </QmBadge>
        </div>
        <div v-if="showActions" class="qm-quiz-card-actions">
          <QmBtn
            variant="ghost"
            size="sm"
            icon="fas fa-heart"
            :class="{ 'qm-quiz-card-favorited': isFavorited }"
            @click.stop="toggleFavorite"
            :aria-label="isFavorited ? 'Remove from favorites' : 'Add to favorites'"
          />
          <QmBtn
            variant="ghost"
            size="sm"
            icon="fas fa-share"
            @click.stop="shareQuiz"
            aria-label="Share quiz"
          />
        </div>
      </div>
    </template>
    
    <div class="qm-quiz-card-content">
      <h3 class="qm-quiz-card-title">{{ quiz.title }}</h3>
      <p class="qm-quiz-card-description">{{ quiz.description }}</p>
      
      <div v-if="quiz.tags && quiz.tags.length" class="qm-quiz-card-tags">
        <QmBadge
          v-for="tag in quiz.tags.slice(0, 3)"
          :key="tag"
          variant="default"
          size="xs"
          outlined
        >
          {{ tag }}
        </QmBadge>
        <QmBadge
          v-if="quiz.tags.length > 3"
          variant="default"
          size="xs"
          outlined
        >
          +{{ quiz.tags.length - 3 }} more
        </QmBadge>
      </div>
      
      <div v-if="showStats" class="qm-quiz-card-stats">
        <div class="qm-quiz-card-stat">
          <i class="fas fa-users"></i>
          <span>{{ formatNumber(quiz.attempts || 0) }} attempts</span>
        </div>
        <div class="qm-quiz-card-stat">
          <i class="fas fa-star"></i>
          <span>{{ quiz.averageScore || 0 }}% avg</span>
        </div>
        <div v-if="quiz.lastAttempt" class="qm-quiz-card-stat">
          <i class="fas fa-clock"></i>
          <span>{{ formatRelativeTime(quiz.lastAttempt) }}</span>
        </div>
      </div>
      
      <div v-if="userProgress" class="qm-quiz-card-progress">
        <div class="qm-quiz-card-progress-header">
          <span class="qm-quiz-card-progress-label">Your Progress</span>
          <span class="qm-quiz-card-progress-value">{{ userProgress.percentage }}%</span>
        </div>
        <div class="qm-quiz-card-progress-bar">
          <div 
            class="qm-quiz-card-progress-fill"
            :style="{ width: `${userProgress.percentage}%` }"
          ></div>
        </div>
        <div class="qm-quiz-card-progress-details">
          <span>Best Score: {{ userProgress.bestScore }}%</span>
          <span>{{ userProgress.completedAttempts }}/{{ userProgress.totalAttempts }} attempts</span>
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="qm-quiz-card-footer">
        <div class="qm-quiz-card-author">
          <div class="qm-quiz-card-avatar">
            <img 
              v-if="quiz.author?.avatar" 
              :src="quiz.author.avatar" 
              :alt="quiz.author.name"
            />
            <i v-else class="fas fa-user"></i>
          </div>
          <div class="qm-quiz-card-author-info">
            <span class="qm-quiz-card-author-name">{{ quiz.author?.name || 'Anonymous' }}</span>
            <span class="qm-quiz-card-created">{{ formatDate(quiz.createdAt) }}</span>
          </div>
        </div>
        
        <div class="qm-quiz-card-cta">
          <QmBtn
            v-if="showStartButton"
            :variant="ctaVariant"
            size="sm"
            :disabled="disabled"
            @click.stop="startQuiz"
          >
            {{ ctaText }}
          </QmBtn>
          <QmBtn
            v-if="showViewButton"
            variant="ghost"
            size="sm"
            @click.stop="viewQuiz"
          >
            View Details
          </QmBtn>
        </div>
      </div>
    </template>
  </QmCard>
</template>

<script>
import { computed } from 'vue'
import QmCard from '../atoms/QmCard.vue'
import QmBtn from '../atoms/QmBtn.vue'
import QmBadge from '../atoms/QmBadge.vue'

export default {
  name: 'QuizCard',
  components: {
    QmCard,
    QmBtn,
    QmBadge
  },
  emits: ['start', 'view', 'favorite', 'share', 'click'],
  props: {
    quiz: {
      type: Object,
      required: true
    },
    userProgress: {
      type: Object,
      default: null
    },
    clickable: {
      type: Boolean,
      default: true
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    showActions: {
      type: Boolean,
      default: true
    },
    showStats: {
      type: Boolean,
      default: true
    },
    showStartButton: {
      type: Boolean,
      default: true
    },
    showViewButton: {
      type: Boolean,
      default: false
    },
    variant: {
      type: String,
      default: 'default'
    }
  },
  setup(props, { emit }) {
    const isFavorited = computed(() => {
      return props.quiz.isFavorited || false
    })
    
    const difficultyVariant = computed(() => {
      const variants = {
        easy: 'success',
        medium: 'warning',
        hard: 'error',
        expert: 'secondary'
      }
      return variants[props.quiz.difficulty?.toLowerCase()] || 'default'
    })
    
    const difficultyIcon = computed(() => {
      const icons = {
        easy: 'fas fa-leaf',
        medium: 'fas fa-fire',
        hard: 'fas fa-bolt',
        expert: 'fas fa-crown'
      }
      return icons[props.quiz.difficulty?.toLowerCase()] || 'fas fa-question'
    })
    
    const cardVariant = computed(() => {
      if (props.variant !== 'default') return props.variant
      if (props.userProgress?.percentage === 100) return 'outlined'
      return 'default'
    })
    
    const ctaVariant = computed(() => {
      if (props.userProgress?.percentage > 0) return 'secondary'
      return 'primary'
    })
    
    const ctaText = computed(() => {
      if (props.userProgress?.percentage === 100) return 'Retake'
      if (props.userProgress?.percentage > 0) return 'Continue'
      return 'Start Quiz'
    })
    
    const formatDuration = (minutes) => {
      if (minutes < 60) return `${minutes}m`
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
    }
    
    const formatNumber = (num) => {
      if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
      if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
      return num.toString()
    }
    
    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    }
    
    const formatRelativeTime = (date) => {
      if (!date) return ''
      const now = new Date()
      const past = new Date(date)
      const diffMs = now - past
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) return 'Today'
      if (diffDays === 1) return 'Yesterday'
      if (diffDays < 7) return `${diffDays} days ago`
      if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
      return formatDate(date)
    }
    
    const handleCardClick = () => {
      emit('click', props.quiz)
    }
    
    const startQuiz = () => {
      emit('start', props.quiz)
    }
    
    const viewQuiz = () => {
      emit('view', props.quiz)
    }
    
    const toggleFavorite = () => {
      emit('favorite', props.quiz)
    }
    
    const shareQuiz = () => {
      emit('share', props.quiz)
    }
    
    return {
      isFavorited,
      difficultyVariant,
      difficultyIcon,
      cardVariant,
      ctaVariant,
      ctaText,
      formatDuration,
      formatNumber,
      formatDate,
      formatRelativeTime,
      handleCardClick,
      startQuiz,
      viewQuiz,
      toggleFavorite,
      shareQuiz
    }
  }
}
</script>

<style lang="scss" scoped>
.qm-quiz-card {
  height: 100%;
  
  &:hover {
    .qm-quiz-card-title {
      color: var(--qm-electric-blue);
    }
  }
}

.qm-quiz-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.qm-quiz-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.qm-quiz-card-actions {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.qm-quiz-card-favorited {
  color: var(--qm-error-red) !important;
}

.qm-quiz-card-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.qm-quiz-card-title {
  margin: 0;
  font-family: var(--qm-font-heading);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--qm-dark-gray);
  line-height: 1.3;
  transition: var(--qm-transition);
}

.qm-quiz-card-description {
  margin: 0;
  color: var(--qm-medium-gray);
  font-size: 0.875rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.qm-quiz-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.qm-quiz-card-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.qm-quiz-card-stat {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--qm-medium-gray);
  
  i {
    font-size: 0.625rem;
    opacity: 0.7;
  }
}

.qm-quiz-card-progress {
  padding: 0.75rem;
  background: var(--qm-light-gray);
  border-radius: var(--qm-border-radius);
}

.qm-quiz-card-progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.qm-quiz-card-progress-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--qm-dark-gray);
}

.qm-quiz-card-progress-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--qm-electric-blue);
}

.qm-quiz-card-progress-bar {
  height: 4px;
  background: var(--qm-white);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.qm-quiz-card-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--qm-electric-blue), var(--qm-royal-purple));
  transition: width 0.3s ease;
}

.qm-quiz-card-progress-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.625rem;
  color: var(--qm-medium-gray);
}

.qm-quiz-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.qm-quiz-card-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.qm-quiz-card-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: var(--qm-light-gray);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  i {
    color: var(--qm-medium-gray);
    font-size: 0.875rem;
  }
}

.qm-quiz-card-author-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.qm-quiz-card-author-name {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--qm-dark-gray);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.qm-quiz-card-created {
  font-size: 0.625rem;
  color: var(--qm-medium-gray);
}

.qm-quiz-card-cta {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

// Dark mode support
[data-theme="dark"] {
  .qm-quiz-card-title {
    color: var(--qm-text-50, #f8fafc);
  }
  
  .qm-quiz-card-description {
    color: var(--qm-text-300, #d1d5db);
  }
  
  .qm-quiz-card-stat {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-quiz-card-progress {
    background: var(--qm-bg-surface-800, #2d2d2d);
  }
  
  .qm-quiz-card-progress-label {
    color: var(--qm-text-200, #e5e7eb);
  }
  
  .qm-quiz-card-progress-bar {
    background: var(--qm-bg-surface-700, #404040);
  }
  
  .qm-quiz-card-progress-details {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-quiz-card-author-name {
    color: var(--qm-text-200, #e5e7eb);
  }
  
  .qm-quiz-card-created {
    color: var(--qm-text-400, #9ca3af);
  }
  
  .qm-quiz-card-avatar {
    background: var(--qm-bg-surface-700, #404040);
    
    i {
      color: var(--qm-text-400, #9ca3af);
    }
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .qm-quiz-card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .qm-quiz-card-actions {
    align-self: flex-end;
  }
  
  .qm-quiz-card-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .qm-quiz-card-cta {
    justify-content: stretch;
    
    .qm-btn {
      flex: 1;
    }
  }
}
</style>