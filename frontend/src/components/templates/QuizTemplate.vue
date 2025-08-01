<template>
  <div class="quiz-template" :class="templateClasses">
    <!-- Quiz Header -->
    <QuizHeader
      v-if="showHeader"
      :quiz="quiz"
      :current-question="currentQuestion"
      :total-questions="totalQuestions"
      :time-remaining="timeRemaining"
      :time-limit="timeLimit"
      :is-paused="isPaused"
      :show-timer="showTimer"
      :show-progress="showProgress"
      :show-actions="showHeaderActions"
      @pause="$emit('pause')"
      @resume="$emit('resume')"
      @help="$emit('help')"
      @settings="$emit('settings')"
      @exit="$emit('exit')"
    />

    <!-- Quiz Content -->
    <main class="quiz-main">
      <div class="container-fluid">
        <div class="row justify-content-center">
          <div class="col-12" :class="contentColumnClasses">
            <!-- Question Card -->
            <div class="question-section" v-if="!showResults">
              <QmCard 
                class="question-card"
                :class="questionCardClasses"
                variant="elevated"
              >
                <!-- Question Header -->
                <template #header v-if="showQuestionHeader">
                  <div class="question-header">
                    <div class="question-meta">
                      <QmBadge 
                        :variant="difficultyVariant"
                        :icon="difficultyIcon"
                      >
                        {{ quiz?.difficulty || 'Medium' }}
                      </QmBadge>
                      <QmBadge variant="outline-secondary" icon="fas fa-clock">
                        {{ questionTimeDisplay }}
                      </QmBadge>
                      <QmBadge 
                        v-if="question?.points"
                        variant="outline-primary" 
                        icon="fas fa-star"
                      >
                        {{ question.points }} pts
                      </QmBadge>
                    </div>
                    <div class="question-number">
                      Question {{ currentQuestion }} of {{ totalQuestions }}
                    </div>
                  </div>
                </template>

                <!-- Question Content -->
                <div class="question-content">
                  <h3 class="question-text">{{ question?.text }}</h3>
                  
                  <!-- Question Image -->
                  <div class="question-image" v-if="question?.image">
                    <img 
                      :src="question.image" 
                      :alt="`Question ${currentQuestion} image`"
                      class="img-fluid rounded"
                    />
                  </div>

                  <!-- Question Code Block -->
                  <div class="question-code" v-if="question?.code">
                    <pre><code>{{ question.code }}</code></pre>
                  </div>

                  <!-- Answer Options -->
                  <div class="answer-options" v-if="question?.options">
                    <div 
                      v-for="(option, index) in question.options"
                      :key="index"
                      class="answer-option"
                      :class="getOptionClasses(option, index)"
                      @click="selectOption(option, index)"
                    >
                      <div class="option-indicator">
                        <span class="option-letter">{{ getOptionLetter(index) }}</span>
                      </div>
                      <div class="option-content">
                        <span class="option-text">{{ option.text || option }}</span>
                        <i 
                          v-if="showAnswerFeedback && getOptionIcon(option, index)"
                          :class="getOptionIcon(option, index)"
                          class="option-icon"
                        ></i>
                      </div>
                    </div>
                  </div>

                  <!-- Text Answer Input -->
                  <div class="text-answer" v-if="question?.type === 'text'">
                    <QmInput
                      :value="textAnswer"
                      @input="$emit('text-answer-change', $event)"
                      type="textarea"
                      :placeholder="textAnswerPlaceholder"
                      :rows="textAnswerRows"
                      :disabled="isAnswered"
                    />
                  </div>
                </div>

                <!-- Question Footer -->
                <template #footer>
                  <div class="question-actions">
                    <div class="action-left">
                      <QmBtn
                        v-if="showPreviousButton && currentQuestion > 1"
                        variant="outline-secondary"
                        icon="fas fa-chevron-left"
                        @click="$emit('previous-question')"
                        :disabled="isLoading"
                      >
                        Previous
                      </QmBtn>
                    </div>
                    
                    <div class="action-center">
                      <QmBtn
                        v-if="showHintButton && question?.hint"
                        variant="outline-info"
                        icon="fas fa-lightbulb"
                        @click="$emit('show-hint')"
                        :disabled="hintUsed"
                      >
                        {{ hintUsed ? 'Hint Used' : 'Get Hint' }}
                      </QmBtn>
                    </div>

                    <div class="action-right">
                      <QmBtn
                        v-if="showSubmitButton"
                        :variant="submitButtonVariant"
                        :icon="submitButtonIcon"
                        @click="submitAnswer"
                        :disabled="!canSubmit || isLoading"
                        :loading="isLoading"
                      >
                        {{ submitButtonText }}
                      </QmBtn>
                    </div>
                  </div>
                </template>
              </QmCard>

              <!-- Hint Card -->
              <QmCard 
                v-if="showHint && question?.hint"
                class="hint-card mt-4"
                variant="info"
              >
                <template #header>
                  <div class="d-flex align-items-center">
                    <i class="fas fa-lightbulb me-2"></i>
                    <span>Hint</span>
                  </div>
                </template>
                <p class="mb-0">{{ question.hint }}</p>
              </QmCard>

              <!-- Explanation Card -->
              <QmCard 
                v-if="showExplanation && question?.explanation"
                class="explanation-card mt-4"
                :variant="explanationVariant"
              >
                <template #header>
                  <div class="d-flex align-items-center">
                    <i :class="explanationIcon" class="me-2"></i>
                    <span>{{ explanationTitle }}</span>
                  </div>
                </template>
                <p class="mb-0">{{ question.explanation }}</p>
              </QmCard>
            </div>

            <!-- Results Section -->
            <div class="results-section" v-else>
              <slot name="results">
                <QmCard class="results-card" variant="elevated">
                  <template #header>
                    <div class="text-center">
                      <i class="fas fa-flag-checkered fa-3x text-primary mb-3"></i>
                      <h2>Quiz Complete!</h2>
                    </div>
                  </template>
                  
                  <div class="results-content text-center">
                    <div class="score-display mb-4">
                      <div class="score-circle">
                        <span class="score-percentage">{{ scorePercentage }}%</span>
                        <span class="score-fraction">{{ correctAnswers }}/{{ totalQuestions }}</span>
                      </div>
                    </div>
                    
                    <div class="results-stats">
                      <div class="row">
                        <div class="col-md-3">
                          <StatCard
                            title="Score"
                            :value="scorePercentage"
                            format="percentage"
                            icon="fas fa-percentage"
                            variant="primary"
                          />
                        </div>
                        <div class="col-md-3">
                          <StatCard
                            title="Time Taken"
                            :value="timeTaken"
                            format="duration"
                            icon="fas fa-clock"
                            variant="info"
                          />
                        </div>
                        <div class="col-md-3">
                          <StatCard
                            title="Correct"
                            :value="correctAnswers"
                            icon="fas fa-check"
                            variant="success"
                          />
                        </div>
                        <div class="col-md-3">
                          <StatCard
                            title="Incorrect"
                            :value="incorrectAnswers"
                            icon="fas fa-times"
                            variant="danger"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <template #footer>
                    <div class="results-actions text-center">
                      <QmBtn
                        variant="primary"
                        icon="fas fa-redo"
                        class="me-3"
                        @click="$emit('retake-quiz')"
                      >
                        Retake Quiz
                      </QmBtn>
                      <QmBtn
                        variant="outline-primary"
                        icon="fas fa-list"
                        class="me-3"
                        @click="$emit('review-answers')"
                      >
                        Review Answers
                      </QmBtn>
                      <QmBtn
                        variant="outline-secondary"
                        icon="fas fa-home"
                        @click="$emit('go-home')"
                      >
                        Back to Dashboard
                      </QmBtn>
                    </div>
                  </template>
                </QmCard>
              </slot>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Quiz Footer -->
    <footer class="quiz-footer" v-if="showFooter">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-6">
            <div class="quiz-progress-info">
              <small class="text-muted">
                Progress: {{ currentQuestion }}/{{ totalQuestions }} questions
                <span v-if="timeRemaining"> • {{ formatTime(timeRemaining) }} remaining</span>
              </small>
            </div>
          </div>
          <div class="col-md-6 text-end">
            <div class="quiz-actions">
              <QmBtn
                v-if="showSaveButton"
                variant="outline-secondary"
                size="sm"
                icon="fas fa-save"
                @click="$emit('save-progress')"
                :disabled="isLoading"
              >
                Save Progress
              </QmBtn>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed } from 'vue'
import QmBtn from '@/components/atoms/QmBtn.vue'
import QmCard from '@/components/atoms/QmCard.vue'
import QmInput from '@/components/atoms/QmInput.vue'
import QmBadge from '@/components/atoms/QmBadge.vue'
import StatCard from '@/components/molecules/StatCard.vue'
import QuizHeader from '@/components/organisms/QuizHeader.vue'

export default {
  name: 'QuizTemplate',
  components: {
    QmBtn,
    QmCard,
    QmInput,
    QmBadge,
    StatCard,
    QuizHeader
  },
  props: {
    // Quiz data
    quiz: {
      type: Object,
      required: true
    },
    question: {
      type: Object,
      required: true
    },
    currentQuestion: {
      type: Number,
      required: true
    },
    totalQuestions: {
      type: Number,
      required: true
    },
    selectedAnswer: {
      type: [String, Number, Array],
      default: null
    },
    textAnswer: {
      type: String,
      default: ''
    },

    // Timer props
    timeRemaining: {
      type: Number,
      default: null
    },
    timeLimit: {
      type: Number,
      default: null
    },
    timeTaken: {
      type: Number,
      default: 0
    },
    showTimer: {
      type: Boolean,
      default: true
    },

    // State props
    isPaused: {
      type: Boolean,
      default: false
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    isAnswered: {
      type: Boolean,
      default: false
    },
    showAnswerFeedback: {
      type: Boolean,
      default: false
    },
    showResults: {
      type: Boolean,
      default: false
    },

    // UI props
    showHeader: {
      type: Boolean,
      default: true
    },
    showHeaderActions: {
      type: Boolean,
      default: true
    },
    showProgress: {
      type: Boolean,
      default: true
    },
    showQuestionHeader: {
      type: Boolean,
      default: true
    },
    showPreviousButton: {
      type: Boolean,
      default: true
    },
    showSubmitButton: {
      type: Boolean,
      default: true
    },
    showHintButton: {
      type: Boolean,
      default: true
    },
    showSaveButton: {
      type: Boolean,
      default: false
    },
    showFooter: {
      type: Boolean,
      default: true
    },
    fullscreen: {
      type: Boolean,
      default: false
    },

    // Hint and explanation
    showHint: {
      type: Boolean,
      default: false
    },
    hintUsed: {
      type: Boolean,
      default: false
    },
    showExplanation: {
      type: Boolean,
      default: false
    },

    // Results props
    scorePercentage: {
      type: Number,
      default: 0
    },
    correctAnswers: {
      type: Number,
      default: 0
    },
    incorrectAnswers: {
      type: Number,
      default: 0
    },

    // Text answer props
    textAnswerPlaceholder: {
      type: String,
      default: 'Enter your answer here...'
    },
    textAnswerRows: {
      type: Number,
      default: 4
    }
  },
  emits: [
    'pause',
    'resume',
    'help',
    'settings',
    'exit',
    'previous-question',
    'next-question',
    'submit-answer',
    'select-option',
    'text-answer-change',
    'show-hint',
    'save-progress',
    'retake-quiz',
    'review-answers',
    'go-home'
  ],
  setup(props, { emit }) {
    const templateClasses = computed(() => ({
      'quiz-fullscreen': props.fullscreen,
      'quiz-paused': props.isPaused,
      'quiz-completed': props.showResults
    }))

    const contentColumnClasses = computed(() => {
      if (props.fullscreen) {
        return 'col-lg-10 col-xl-8'
      }
      return 'col-lg-8 col-xl-6'
    })

    const questionCardClasses = computed(() => ({
      'question-answered': props.isAnswered,
      'question-loading': props.isLoading
    }))

    const difficultyVariant = computed(() => {
      const difficulty = props.quiz?.difficulty?.toLowerCase()
      switch (difficulty) {
        case 'easy': return 'success'
        case 'medium': return 'warning'
        case 'hard': return 'danger'
        default: return 'secondary'
      }
    })

    const difficultyIcon = computed(() => {
      const difficulty = props.quiz?.difficulty?.toLowerCase()
      switch (difficulty) {
        case 'easy': return 'fas fa-leaf'
        case 'medium': return 'fas fa-balance-scale'
        case 'hard': return 'fas fa-fire'
        default: return 'fas fa-question'
      }
    })

    const questionTimeDisplay = computed(() => {
      if (props.timeRemaining) {
        return formatTime(props.timeRemaining)
      }
      return 'No limit'
    })

    const canSubmit = computed(() => {
      if (props.question?.type === 'text') {
        return props.textAnswer?.trim().length > 0
      }
      return props.selectedAnswer !== null && props.selectedAnswer !== undefined
    })

    const submitButtonVariant = computed(() => {
      if (props.currentQuestion === props.totalQuestions) {
        return 'success'
      }
      return 'primary'
    })

    const submitButtonIcon = computed(() => {
      if (props.currentQuestion === props.totalQuestions) {
        return 'fas fa-flag-checkered'
      }
      return 'fas fa-chevron-right'
    })

    const submitButtonText = computed(() => {
      if (props.isLoading) {
        return 'Submitting...'
      }
      if (props.currentQuestion === props.totalQuestions) {
        return 'Finish Quiz'
      }
      return 'Next Question'
    })

    const explanationVariant = computed(() => {
      if (props.isAnswered) {
        return props.selectedAnswer === props.question?.correctAnswer ? 'success' : 'danger'
      }
      return 'info'
    })

    const explanationIcon = computed(() => {
      if (props.isAnswered) {
        return props.selectedAnswer === props.question?.correctAnswer ? 'fas fa-check-circle' : 'fas fa-times-circle'
      }
      return 'fas fa-info-circle'
    })

    const explanationTitle = computed(() => {
      if (props.isAnswered) {
        return props.selectedAnswer === props.question?.correctAnswer ? 'Correct!' : 'Incorrect'
      }
      return 'Explanation'
    })

    const getOptionLetter = (index) => {
      return String.fromCharCode(65 + index) // A, B, C, D...
    }

    const getOptionClasses = (option, index) => {
      const classes = ['answer-option']
      
      if (props.selectedAnswer === index || props.selectedAnswer === option) {
        classes.push('selected')
      }
      
      if (props.showAnswerFeedback) {
        if (option.correct || index === props.question?.correctAnswer) {
          classes.push('correct')
        } else if (props.selectedAnswer === index || props.selectedAnswer === option) {
          classes.push('incorrect')
        }
      }
      
      return classes
    }

    const getOptionIcon = (option, index) => {
      if (!props.showAnswerFeedback) return null
      
      if (option.correct || index === props.question?.correctAnswer) {
        return 'fas fa-check-circle text-success'
      } else if (props.selectedAnswer === index || props.selectedAnswer === option) {
        return 'fas fa-times-circle text-danger'
      }
      
      return null
    }

    const selectOption = (option, index) => {
      if (props.isAnswered || props.isLoading) return
      emit('select-option', { option, index })
    }

    const submitAnswer = () => {
      if (!props.canSubmit || props.isLoading) return
      emit('submit-answer')
    }

    const formatTime = (seconds) => {
      if (!seconds) return '0:00'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    return {
      templateClasses,
      contentColumnClasses,
      questionCardClasses,
      difficultyVariant,
      difficultyIcon,
      questionTimeDisplay,
      canSubmit,
      submitButtonVariant,
      submitButtonIcon,
      submitButtonText,
      explanationVariant,
      explanationIcon,
      explanationTitle,
      getOptionLetter,
      getOptionClasses,
      getOptionIcon,
      selectOption,
      submitAnswer,
      formatTime
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/qm-theme';

.quiz-template {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--qm-bg-primary);
  
  &.quiz-fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 9999;
  }
  
  &.quiz-paused {
    .quiz-main {
      opacity: 0.7;
      pointer-events: none;
    }
  }
}

// Main Content
.quiz-main {
  flex: 1;
  padding: var(--qm-spacing-lg) 0;
  transition: all var(--qm-transition-base);
}

// Question Card
.question-card {
  margin-bottom: var(--qm-spacing-lg);
  
  &.question-answered {
    border-color: var(--qm-color-success);
  }
  
  &.question-loading {
    opacity: 0.8;
    pointer-events: none;
  }
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--qm-spacing-md);
  
  .question-meta {
    display: flex;
    gap: var(--qm-spacing-sm);
    flex-wrap: wrap;
  }
  
  .question-number {
    font-weight: var(--qm-font-weight-semibold);
    color: var(--qm-text-secondary);
    font-size: var(--qm-font-size-sm);
  }
}

.question-content {
  .question-text {
    color: var(--qm-text-primary);
    font-size: var(--qm-font-size-xl);
    font-weight: var(--qm-font-weight-semibold);
    line-height: 1.4;
    margin-bottom: var(--qm-spacing-lg);
  }
  
  .question-image {
    margin: var(--qm-spacing-lg) 0;
    text-align: center;
    
    img {
      max-height: 300px;
      box-shadow: var(--qm-shadow-md);
    }
  }
  
  .question-code {
    margin: var(--qm-spacing-lg) 0;
    
    pre {
      background: var(--qm-bg-secondary);
      border: 1px solid var(--qm-border-light);
      border-radius: var(--qm-border-radius-md);
      padding: var(--qm-spacing-md);
      overflow-x: auto;
      
      code {
        color: var(--qm-text-primary);
        font-family: var(--qm-font-mono);
        font-size: var(--qm-font-size-sm);
      }
    }
  }
}

// Answer Options
.answer-options {
  margin-top: var(--qm-spacing-lg);
}

.answer-option {
  display: flex;
  align-items: center;
  padding: var(--qm-spacing-md);
  margin-bottom: var(--qm-spacing-sm);
  border: 2px solid var(--qm-border-light);
  border-radius: var(--qm-border-radius-lg);
  background: var(--qm-bg-surface);
  cursor: pointer;
  transition: all var(--qm-transition-base);
  
  &:hover {
    border-color: var(--qm-color-primary);
    background: var(--qm-bg-hover);
    transform: translateY(-1px);
    box-shadow: var(--qm-shadow-sm);
  }
  
  &.selected {
    border-color: var(--qm-color-primary);
    background: var(--qm-color-primary-light);
  }
  
  &.correct {
    border-color: var(--qm-color-success);
    background: var(--qm-color-success-light);
    
    .option-indicator {
      background: var(--qm-color-success);
      color: white;
    }
  }
  
  &.incorrect {
    border-color: var(--qm-color-danger);
    background: var(--qm-color-danger-light);
    
    .option-indicator {
      background: var(--qm-color-danger);
      color: white;
    }
  }
  
  .option-indicator {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--qm-color-secondary);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: var(--qm-font-weight-bold);
    font-size: var(--qm-font-size-sm);
    margin-right: var(--qm-spacing-md);
    flex-shrink: 0;
    transition: all var(--qm-transition-base);
  }
  
  .option-content {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .option-text {
      color: var(--qm-text-primary);
      font-size: var(--qm-font-size-base);
      line-height: 1.4;
    }
    
    .option-icon {
      font-size: var(--qm-font-size-lg);
      margin-left: var(--qm-spacing-sm);
    }
  }
}

// Text Answer
.text-answer {
  margin-top: var(--qm-spacing-lg);
}

// Question Actions
.question-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--qm-spacing-md);
  
  .action-left,
  .action-center,
  .action-right {
    flex: 1;
  }
  
  .action-center {
    text-align: center;
  }
  
  .action-right {
    text-align: right;
  }
}

// Hint and Explanation Cards
.hint-card,
.explanation-card {
  animation: slideDown var(--qm-transition-base) ease-out;
}

// Results Section
.results-section {
  .results-card {
    text-align: center;
  }
  
  .score-display {
    .score-circle {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--qm-color-primary), var(--qm-color-secondary));
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      margin: 0 auto;
      color: white;
      
      .score-percentage {
        font-size: var(--qm-font-size-2xl);
        font-weight: var(--qm-font-weight-bold);
        line-height: 1;
      }
      
      .score-fraction {
        font-size: var(--qm-font-size-sm);
        opacity: 0.9;
      }
    }
  }
  
  .results-stats {
    margin-top: var(--qm-spacing-xl);
  }
  
  .results-actions {
    margin-top: var(--qm-spacing-lg);
  }
}

// Footer
.quiz-footer {
  background: var(--qm-bg-surface);
  border-top: 1px solid var(--qm-border-light);
  padding: var(--qm-spacing-md) 0;
  
  .quiz-progress-info {
    color: var(--qm-text-secondary);
  }
  
  .quiz-actions {
    display: flex;
    gap: var(--qm-spacing-sm);
    justify-content: flex-end;
  }
}

// Animations
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Responsive Design
@media (max-width: 991.98px) {
  .question-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--qm-spacing-sm);
  }
  
  .question-actions {
    flex-direction: column;
    
    .action-left,
    .action-center,
    .action-right {
      text-align: center;
      width: 100%;
    }
  }
  
  .quiz-footer {
    .row {
      flex-direction: column;
      gap: var(--qm-spacing-sm);
      text-align: center;
    }
  }
}

@media (max-width: 575.98px) {
  .quiz-main {
    padding: var(--qm-spacing-md) 0;
  }
  
  .question-content {
    .question-text {
      font-size: var(--qm-font-size-lg);
    }
  }
  
  .answer-option {
    padding: var(--qm-spacing-sm);
    
    .option-indicator {
      width: 28px;
      height: 28px;
      font-size: var(--qm-font-size-xs);
    }
  }
  
  .results-section {
    .score-display .score-circle {
      width: 100px;
      height: 100px;
      
      .score-percentage {
        font-size: var(--qm-font-size-xl);
      }
    }
  }
}

// Dark mode support
@media (prefers-color-scheme: dark) {
  .quiz-template {
    background: var(--qm-bg-primary-dark);
  }
  
  .answer-option {
    background: var(--qm-bg-surface-dark);
    border-color: var(--qm-border-light-dark);
    
    &:hover {
      background: var(--qm-bg-hover-dark);
    }
  }
  
  .quiz-footer {
    background: var(--qm-bg-surface-dark);
    border-color: var(--qm-border-light-dark);
  }
}

// High contrast mode
@media (prefers-contrast: high) {
  .answer-option {
    border-width: 3px;
    
    &.selected,
    &.correct,
    &.incorrect {
      border-width: 4px;
    }
  }
}

// Reduced motion
@media (prefers-reduced-motion: reduce) {
  .answer-option,
  .quiz-main {
    transition: none;
  }
  
  .hint-card,
  .explanation-card {
    animation: none;
  }
}
</style>