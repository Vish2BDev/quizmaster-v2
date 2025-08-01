<template>
  <div class="quiz-container">
    <!-- Quiz Not Started - Confidence Building -->
    <div v-if="!quizStarted && !quizCompleted" class="quiz-intro">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="card-qm shadow-lg">
              <div class="card-body p-5 text-center">
                <div class="quiz-intro-icon mb-4">
                  <i class="fas fa-rocket text-primary" style="font-size: 4rem;"></i>
                </div>
                <h2 class="mb-3" style="font-family: var(--qm-font-heading);">Ready to Challenge Yourself?</h2>
                <p class="lead text-muted mb-4">Take your time, trust your knowledge, and remember - every question is a learning opportunity!</p>
                
                <div class="quiz-info-grid mb-4">
                  <div class="row text-center">
                    <div class="col-md-4">
                      <div class="info-card">
                        <div class="info-icon">
                          <i class="fas fa-clock text-warning"></i>
                        </div>
                        <div class="info-content">
                          <h6>Duration</h6>
                          <p class="mb-0">{{ currentQuiz?.quiz?.duration_minutes || currentQuiz?.quiz?.duration || 0 }} minutes</p>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div class="info-card">
                        <div class="info-icon">
                          <i class="fas fa-list-ol text-info"></i>
                        </div>
                        <div class="info-content">
                          <h6>Questions</h6>
                          <p class="mb-0">{{ currentQuiz?.questions?.length || 0 }} questions</p>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div class="info-card">
                        <div class="info-icon">
                          <i class="fas fa-medal text-success"></i>
                        </div>
                        <div class="info-content">
                          <h6>Type</h6>
                          <p class="mb-0">Multiple Choice</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Motivational Preview -->
                <div class="motivation-box mb-4">
                  <div class="d-flex align-items-center justify-content-center">
                    <i class="fas fa-lightbulb text-warning me-2"></i>
                    <span class="small text-muted">{{ getMotivationalTip() }}</span>
                  </div>
                </div>
                
                <button @click="startQuiz" class="btn btn-qm-primary btn-lg px-5" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fas fa-play me-2"></i>
                  {{ loading ? 'Preparing Quiz...' : 'Start Quiz' }}
                </button>

                <div class="mt-3">
                  <router-link to="/dashboard" class="btn btn-outline-secondary">
                    <i class="fas fa-arrow-left me-2"></i>Back to Dashboard
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quiz In Progress - Focus Mode -->
    <div v-if="quizStarted && !quizCompleted" class="quiz-active">
      <!-- Header with Timer and Progress -->
      <div class="quiz-header qm-gradient-bg text-white sticky-top">
        <div class="container">
          <div class="row align-items-center py-3">
            <div class="col-md-6">
              <div class="quiz-progress-info">
                <h6 class="mb-1">{{ currentQuiz?.quiz?.title }}</h6>
                <div class="progress-text">
                  Question {{ currentQuestionIndex + 1 }} of {{ currentQuiz?.questions?.length || 0 }}
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="timer-section text-end">
                <div class="timer-display" :class="{ 'timer-warning': timeRemaining < 300, 'timer-danger': timeRemaining < 60 }">
                  <i class="fas fa-stopwatch me-2"></i>
                  <span class="timer-text">{{ formatTime(timeRemaining) }}</span>
                </div>
                <div class="timer-bar mt-2">
                  <div class="timer-fill" 
                       :class="{ 'warning': timeRemaining < 300, 'danger': timeRemaining < 60 }"
                       :style="{ width: (timeRemaining / ((currentQuiz?.quiz?.duration_minutes || currentQuiz?.quiz?.duration || 30) * 60) * 100) + '%' }">
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Visual Progress Bar -->
          <div class="overall-progress">
            <div class="qm-progress">
              <div class="qm-progress-fill" 
                   :style="{ width: progressPercentage + '%' }">
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Question Content -->
      <div class="quiz-content">
        <div class="container py-4">
          <div class="row justify-content-center">
            <div class="col-lg-10">
              <div class="question-card card-qm" v-if="currentQuestion">
                <!-- Question Text -->
                <div class="question-container">
                  <div class="question-number">
                    <span class="badge bg-primary">{{ currentQuestionIndex + 1 }}</span>
                  </div>
                  <div class="question-text">
                    {{ currentQuestion.text }}
                  </div>
                </div>

                <!-- Answer Options -->
                <div class="answers-section">
                  <div class="row">
                    <div class="col-md-6" v-for="option in ['a', 'b']" :key="option">
                      <div class="answer-option"
                           :class="{ 'selected': answers[currentQuestion.id] === option }"
                           @click="selectAnswer(option)">
                        <div class="option-marker">
                          <span class="option-letter">{{ option.toUpperCase() }}</span>
                          <div class="selection-indicator">
                            <i class="fas fa-check"></i>
                          </div>
                        </div>
                        <div class="option-text">
                          {{ currentQuestion[`option_${option}`] }}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="row mt-3">
                    <div class="col-md-6" v-for="option in ['c', 'd']" :key="option">
                      <div class="answer-option"
                           :class="{ 'selected': answers[currentQuestion.id] === option }"
                           @click="selectAnswer(option)">
                        <div class="option-marker">
                          <span class="option-letter">{{ option.toUpperCase() }}</span>
                          <div class="selection-indicator">
                            <i class="fas fa-check"></i>
                          </div>
                        </div>
                        <div class="option-text">
                          {{ currentQuestion[`option_${option}`] }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Navigation Controls -->
                <div class="quiz-navigation">
                  <div class="d-flex justify-content-between align-items-center">
                    <button 
                      @click="previousQuestion" 
                      class="btn btn-outline-secondary"
                      :disabled="currentQuestionIndex === 0"
                    >
                      <i class="fas fa-chevron-left me-2"></i>Previous
                    </button>
                    
                    <div class="question-dots">
                      <span v-for="(q, index) in currentQuiz?.questions" 
                            :key="index"
                            class="dot"
                            :class="{ 
                              'active': index === currentQuestionIndex,
                              'answered': answers[q.id],
                              'current': index === currentQuestionIndex
                            }"
                            @click="goToQuestion(index)">
                      </span>
                    </div>
                    
                    <button 
                      v-if="currentQuestionIndex < (currentQuiz?.questions?.length || 0) - 1"
                      @click="nextQuestion" 
                      class="btn btn-qm-primary"
                      :disabled="!answers[currentQuestion.id]"
                    >
                      Next<i class="fas fa-chevron-right ms-2"></i>
                    </button>
                    
                    <button 
                      v-else
                      @click="showSubmitModal" 
                      class="btn btn-success btn-lg"
                      :class="{ 'pulse': allQuestionsAnswered }"
                    >
                      <i class="fas fa-flag-checkered me-2"></i>Finish Quiz
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quiz Completed - Celebration & Redemption -->
    <div v-if="quizCompleted" class="quiz-results">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="results-card card-qm shadow-lg">
              <div class="card-body p-5 text-center">
                <!-- Celebration Header -->
                <div class="celebration-header mb-4">
                  <div class="result-icon mb-3">
                    <i :class="getResultIcon()" :style="{ color: getResultColor(), fontSize: '5rem' }"></i>
                  </div>
                  <h2 class="result-title" :style="{ color: getResultColor() }">
                    {{ getResultTitle() }}
                  </h2>
                  <p class="result-subtitle text-muted">
                    {{ getResultMessage() }}
                  </p>
                </div>

                <!-- Score Visualization -->
                <div class="score-display mb-4">
                  <div class="row">
                    <div class="col-md-3">
                      <div class="score-stat">
                        <div class="stat-number text-primary">{{ quizResult?.score || 0 }}</div>
                        <div class="stat-label">Correct</div>
                      </div>
                    </div>
                    <div class="col-md-3">
                      <div class="score-stat">
                        <div class="stat-number text-info">{{ quizResult?.total_questions || 0 }}</div>
                        <div class="stat-label">Total</div>
                      </div>
                    </div>
                    <div class="col-md-3">
                      <div class="score-stat">
                        <div class="stat-number" :style="{ color: getResultColor() }">
                          {{ quizResult?.percentage || 0 }}%
                        </div>
                        <div class="stat-label">Score</div>
                      </div>
                    </div>
                    <div class="col-md-3">
                      <div class="score-stat">
                        <div class="stat-number text-warning">{{ formatTime(quizResult?.time_taken) }}</div>
                        <div class="stat-label">Time</div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Performance Feedback -->
                <div class="performance-feedback mb-4">
                  <div class="feedback-card" :class="getResultAlertClass()">
                    <div class="feedback-content">
                      <h5 class="mb-2">{{ getDetailedFeedback().title }}</h5>
                      <p class="mb-0">{{ getDetailedFeedback().message }}</p>
                    </div>
                  </div>
                </div>

                <!-- Quick Feedback - Emoji Rating -->
                <div class="emoji-feedback mb-4">
                  <h6 class="text-muted mb-3">How was this quiz?</h6>
                  <div class="emoji-options">
                    <span v-for="(emoji, index) in ['😢', '😐', '🙂', '😊', '🤩']" 
                          :key="index"
                          class="emoji-option"
                          :class="{ 'selected': selectedEmoji === index }"
                          @click="selectEmoji(index)">
                      {{ emoji }}
                    </span>
                  </div>
                </div>

                <!-- Action Buttons -->
                <div class="result-actions">
                  <div class="row">
                    <div class="col-md-6 mb-2">
                      <router-link to="/dashboard" class="btn btn-qm-primary w-100">
                        <i class="fas fa-home me-2"></i>Back to Dashboard
                      </router-link>
                    </div>
                    <div class="col-md-6 mb-2">
                      <button @click="retakeQuiz" class="btn btn-outline-primary w-100">
                        <i class="fas fa-redo me-2"></i>{{ getRetryButtonText() }}
                      </button>
                    </div>
                  </div>
                  
                  <div class="mt-3">
                    <button @click="shareResult" class="btn btn-outline-success me-2">
                      <i class="fas fa-share me-2"></i>Share Result
                    </button>
                    <button @click="viewSimilarQuizzes" class="btn btn-outline-info">
                      <i class="fas fa-search me-2"></i>Similar Quizzes
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Submit Confirmation Modal -->
    <div class="modal fade" id="submitModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content border-0">
          <div class="modal-header qm-gradient-bg text-white">
            <h5 class="modal-title">Ready to Submit?</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="text-center mb-3">
              <i class="fas fa-flag-checkered text-primary fa-3x mb-3"></i>
              <p class="lead">You're about to submit your quiz!</p>
            </div>
            
            <div class="submission-summary">
              <div class="row text-center">
                <div class="col-6">
                  <div class="summary-stat">
                    <div class="stat-number text-success">{{ answeredQuestions }}</div>
                    <div class="stat-label">Answered</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="summary-stat">
                    <div class="stat-number" :class="unansweredQuestions > 0 ? 'text-warning' : 'text-muted'">
                      {{ unansweredQuestions }}
                    </div>
                    <div class="stat-label">Remaining</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="unansweredQuestions > 0" class="alert alert-warning mt-3">
              <i class="fas fa-exclamation-triangle me-2"></i>
              <strong>Note:</strong> {{ unansweredQuestions }} questions are still unanswered. You can still submit, but consider reviewing them first.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
              <i class="fas fa-edit me-2"></i>Review Answers
            </button>
            <button type="button" class="btn btn-success" @click="submitQuiz" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="fas fa-paper-plane me-2"></i>
              Submit Quiz
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { Modal } from 'bootstrap'

export default {
  name: 'TakeQuiz',
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    const quizId = route.params.id
    const quizStarted = ref(false)
    const quizCompleted = ref(false)
    const loading = ref(false)
    const submitting = ref(false)
    const currentQuestionIndex = ref(0)
    const answers = ref({})
    const timeRemaining = ref(0)
    const quizResult = ref(null)
    const timer = ref(null)
    const selectedEmoji = ref(null)
    
    const currentQuiz = computed(() => store.state.currentQuiz)
    const currentQuestion = computed(() => 
      currentQuiz.value?.questions?.[currentQuestionIndex.value]
    )
    
    const progressPercentage = computed(() => {
      if (!currentQuiz.value?.questions?.length) return 0
      return ((currentQuestionIndex.value + 1) / currentQuiz.value.questions.length) * 100
    })
    
    const answeredQuestions = computed(() => Object.keys(answers.value).length)
    const unansweredQuestions = computed(() => 
      (currentQuiz.value?.questions?.length || 0) - answeredQuestions.value
    )

    const allQuestionsAnswered = computed(() => unansweredQuestions.value === 0)

    const getMotivationalTip = () => {
      const tips = [
        "Read each question carefully - you've got this! 💪",
        "Trust your first instinct, it's often correct! ✨",
        "Take your time, there's no rush to greatness! 🌟",
        "Every question is a chance to learn something new! 🧠"
      ]
      return tips[Math.floor(Math.random() * tips.length)]
    }
    
    const startQuiz = async () => {
      loading.value = true
      const result = await store.dispatch('startQuiz', quizId)
      
      if (result.success) {
        quizStarted.value = true
        
        // Use remaining time from backend if available, otherwise calculate from duration
        const remainingMinutes = currentQuiz.value?.quiz?.remaining_time
        const durationMinutes = currentQuiz.value?.quiz?.duration_minutes || currentQuiz.value?.quiz?.duration || 30
        
        if (remainingMinutes !== undefined && remainingMinutes !== null) {
          timeRemaining.value = Math.max(0, Math.floor(remainingMinutes * 60))
        } else {
          timeRemaining.value = durationMinutes * 60
        }
        
        startTimer()
        
        // Trigger focus mode
        document.body.classList.add('quiz-focus-mode')
      } else {
        window.dispatchEvent(new CustomEvent('show-error-toast', {
          detail: { message: 'Failed to start quiz: ' + result.message }
        }))
      }
      loading.value = false
    }
    
    const startTimer = () => {
      timer.value = setInterval(() => {
        timeRemaining.value--
        if (timeRemaining.value <= 0) {
          submitQuiz(true) // Auto-submit when time runs out
        }
      }, 1000)
    }

    const selectAnswer = (option) => {
      answers.value[currentQuestion.value.id] = option
      
      // Haptic feedback simulation
      const answerElement = event.target.closest('.answer-option')
      answerElement.classList.add('answer-selected')
      setTimeout(() => {
        answerElement.classList.remove('answer-selected')
      }, 200)
    }

    const goToQuestion = (index) => {
      currentQuestionIndex.value = index
    }
    
    const nextQuestion = () => {
      if (currentQuestionIndex.value < (currentQuiz.value?.questions?.length || 0) - 1) {
        currentQuestionIndex.value++
      }
    }
    
    const previousQuestion = () => {
      if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--
      }
    }
    
    const showSubmitModal = () => {
      const modal = new Modal(document.getElementById('submitModal'))
      modal.show()
    }
    
    const submitQuiz = async (autoSubmit = false) => {
      if (!autoSubmit) {
        const modal = Modal.getInstance(document.getElementById('submitModal'))
        modal?.hide()
      }
      
      submitting.value = true
      clearInterval(timer.value)
      document.body.classList.remove('quiz-focus-mode')
      
      const result = await store.dispatch('submitQuiz', {
        attemptId: currentQuiz.value?.attempt_id,
        answers: answers.value
      })
      
      if (result.success) {
        quizResult.value = result.data
        
        // Store result data for QuizSummary page
        const resultData = {
          score: result.data.score,
          total_questions: result.data.total_questions,
          percentage: result.data.percentage,
          time_taken: result.data.time_taken,
          quiz_id: currentQuiz.value?.id
        }
        
        localStorage.setItem('lastQuizResult', JSON.stringify(resultData))
        
        // Trigger celebration based on performance
        triggerCelebration(result.data.percentage)
        
        // Navigate to quiz summary page after a short delay
        setTimeout(() => {
          router.push('/quiz-summary')
        }, 1500)
      } else {
        window.dispatchEvent(new CustomEvent('show-error-toast', {
          detail: { message: 'Failed to submit quiz: ' + result.message }
        }))
      }
      
      submitting.value = false
    }

    const triggerCelebration = (percentage) => {
      if (percentage >= 90) {
        // Trigger confetti for excellent performance
        window.dispatchEvent(new CustomEvent('trigger-achievement', {
          detail: { 
            message: 'Outstanding performance! You\'re a quiz master!', 
            badge: 'Perfect Score' 
          }
        }))
      } else if (percentage >= 70) {
        window.dispatchEvent(new CustomEvent('show-success-toast', {
          detail: { message: 'Great job! Well done on this quiz! 🎉' }
        }))
      }
    }
    
    const retakeQuiz = () => {
      // Reset quiz state for redemption opportunity
      quizCompleted.value = false
      quizStarted.value = false
      currentQuestionIndex.value = 0
      answers.value = {}
      quizResult.value = null
      selectedEmoji.value = null
    }

    const selectEmoji = (index) => {
      selectedEmoji.value = index
      // Send feedback to backend
      // ... feedback API call
    }

    const shareResult = () => {
      // Social sharing functionality
      window.dispatchEvent(new CustomEvent('show-success-toast', {
        detail: { message: 'Result shared successfully! 🎉' }
      }))
    }

    const viewSimilarQuizzes = () => {
      router.push('/dashboard?tab=quizzes')
    }
    
    const formatTime = (seconds) => {
      if (!seconds) return '0:00'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    const getResultIcon = () => {
      const percentage = quizResult.value?.percentage || 0
      if (percentage >= 90) return 'fas fa-trophy'
      if (percentage >= 80) return 'fas fa-medal'
      if (percentage >= 70) return 'fas fa-star'
      if (percentage >= 60) return 'fas fa-thumbs-up'
      return 'fas fa-heart'
    }

    const getResultColor = () => {
      const percentage = quizResult.value?.percentage || 0
      if (percentage >= 80) return '#2ecc71'
      if (percentage >= 60) return '#f39c12'
      return '#e74c3c'
    }

    const getResultTitle = () => {
      const percentage = quizResult.value?.percentage || 0
      if (percentage >= 90) return 'Outstanding! 🏆'
      if (percentage >= 80) return 'Excellent Work! ⭐'
      if (percentage >= 70) return 'Great Job! 👏'
      if (percentage >= 60) return 'Good Effort! 👍'
      return 'Keep Learning! 💪'
    }

    const getResultMessage = () => {
      const percentage = quizResult.value?.percentage || 0
      if (percentage >= 90) return 'You\'ve mastered this topic! Your dedication shows.'
      if (percentage >= 80) return 'Impressive performance! You really know your stuff.'
      if (percentage >= 70) return 'Solid understanding! You\'re on the right track.'
      if (percentage >= 60) return 'Good foundation! A bit more practice will help.'
      return 'Every expert was once a beginner. Keep practicing!'
    }

    const getDetailedFeedback = () => {
      const percentage = quizResult.value?.percentage || 0
      if (percentage >= 80) {
        return {
          title: 'Excellent Performance!',
          message: 'You demonstrated strong understanding of the material. Consider exploring advanced topics in this area.'
        }
      } else if (percentage >= 60) {
        return {
          title: 'Good Foundation',
          message: 'You have a solid grasp of the basics. Focus on areas where you missed questions to improve further.'
        }
      } else {
        return {
          title: 'Learning Opportunity',
          message: 'This quiz highlighted areas for improvement. Review the material and try again - you\'ve got this!'
        }
      }
    }

    const getResultAlertClass = () => {
      const percentage = quizResult.value?.percentage || 0
      if (percentage >= 80) return 'alert-success'
      if (percentage >= 60) return 'alert-warning'
      return 'alert-info' // Changed from alert-danger to be more encouraging
    }

    const getRetryButtonText = () => {
      const percentage = quizResult.value?.percentage || 0
      if (percentage >= 80) return 'Challenge Yourself Again'
      return 'Try Again for Better Score'
    }
    
    onMounted(() => {
      // If quiz data not loaded, redirect to dashboard
      if (!currentQuiz.value) {
        router.push('/dashboard')
      }
    })
    
    onUnmounted(() => {
      if (timer.value) {
        clearInterval(timer.value)
      }
      document.body.classList.remove('quiz-focus-mode')
    })
    
    return {
      quizStarted,
      quizCompleted,
      loading,
      submitting,
      currentQuestionIndex,
      answers,
      timeRemaining,
      quizResult,
      selectedEmoji,
      currentQuiz,
      currentQuestion,
      progressPercentage,
      answeredQuestions,
      unansweredQuestions,
      allQuestionsAnswered,
      getMotivationalTip,
      startQuiz,
      selectAnswer,
      goToQuestion,
      nextQuestion,
      previousQuestion,
      showSubmitModal,
      submitQuiz,
      retakeQuiz,
      selectEmoji,
      shareResult,
      viewSimilarQuizzes,
      formatTime,
      getResultIcon,
      getResultColor,
      getResultTitle,
      getResultMessage,
      getDetailedFeedback,
      getResultAlertClass,
      getRetryButtonText
    }
  }
}
</script>

<style scoped>
.quiz-container {
  min-height: 100vh;
}

/* Quiz Introduction Styles */
.quiz-intro {
  padding: 4rem 0;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.quiz-intro-icon {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.info-card {
  padding: 1.5rem;
  text-align: center;
}

.info-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.motivation-box {
  background: rgba(59, 130, 246, 0.1);
  padding: 1rem;
  border-radius: var(--qm-border-radius);
  border-left: 4px solid var(--primary);
}

/* Quiz Active Styles */
.quiz-header {
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 1000;
}

.quiz-progress-info h6 {
  font-family: var(--qm-font-heading);
  margin-bottom: 0;
}

.timer-display {
  font-size: 1.2rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.timer-display.timer-warning {
  color: #F59E0B;
  animation: pulse 1s infinite;
}

.timer-display.timer-danger {
  color: var(--danger);
  animation: pulse 0.5s infinite;
}

.overall-progress {
  margin-top: 10px;
}

/* Question Card Styles */
.question-card {
  margin: 2rem 0;
  border: none;
  overflow: visible;
}

.question-container {
  position: relative;
  padding: 2rem;
  margin-bottom: 2rem;
}

.question-number {
  position: absolute;
  top: -15px;
  left: 30px;
}

.question-number .badge {
  font-size: 1rem;
  padding: 8px 12px;
}

.question-text {
  font-size: 1.3rem;
  line-height: 1.6;
  color: var(--text-main);
  font-weight: 500;
  margin-left: 20px;
}

/* Answer Options */
.answers-section {
  padding: 0 2rem 2rem;
}

.answer-option {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  border: 2px solid transparent;
  border-radius: var(--qm-border-radius);
  background: var(--qm-white);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.answer-option:hover {
  background: rgba(52, 152, 219, 0.05);
  border-color: rgba(52, 152, 219, 0.3);
  transform: translateX(5px);
}

.answer-option.selected {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(76, 205, 196, 0.05));
  border-color: var(--qm-electric-blue);
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.2);
}

.answer-option.answer-selected {
  transform: scale(0.98);
  background: rgba(46, 204, 113, 0.1);
}

.option-marker {
  position: relative;
  margin-right: 1rem;
  flex-shrink: 0;
}

.option-letter {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--qm-light-gray);
  color: var(--qm-medium-gray);
  font-weight: 600;
  transition: all 0.3s ease;
}

.answer-option.selected .option-letter {
  background: var(--qm-electric-blue);
  color: white;
}

.selection-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  color: white;
  transition: transform 0.2s ease;
}

.answer-option.selected .selection-indicator {
  transform: translate(-50%, -50%) scale(1);
}

.option-text {
  flex: 1;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--text-main);
}

/* Navigation */
.quiz-navigation {
  padding: 2rem;
  border-top: 1px solid var(--qm-light-gray);
  background: rgba(248, 249, 250, 0.5);
}

.question-dots {
  display: flex;
  gap: 8px;
  align-items: center;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--qm-light-gray);
  cursor: pointer;
  transition: all 0.3s ease;
}

.dot.answered {
  background: var(--success);
}

.dot.current {
  background: var(--primary);
  transform: scale(1.3);
}

.dot:hover {
  transform: scale(1.2);
}

.btn.pulse {
  animation: pulseGlow 1.5s infinite;
}

@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(46, 204, 113, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(46, 204, 113, 0.8);
  }
}

/* Results Styles */
.quiz-results {
  padding: 4rem 0;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.results-card {
  border: none;
  position: relative;
  overflow: hidden;
}

.celebration-header {
  animation: celebrationEnter 0.8s ease-out;
}

@keyframes celebrationEnter {
  0% {
    opacity: 0;
    transform: translateY(30px) scale(0.9);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.result-icon {
  animation: iconCelebration 1s ease-out 0.3s both;
}

@keyframes iconCelebration {
  0%, 50%, 100% {
    transform: rotate(0deg) scale(1);
  }
  25% {
    transform: rotate(-10deg) scale(1.1);
  }
  75% {
    transform: rotate(10deg) scale(1.1);
  }
}

.score-display {
  background: rgba(52, 152, 219, 0.05);
  padding: 2rem;
  border-radius: var(--qm-border-radius);
  margin: 2rem 0;
}

.score-stat {
  text-align: center;
  padding: 1rem;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  font-family: var(--qm-font-ui);
  margin-bottom: 0.5rem;
}

.stat-label {
  color: var(--qm-medium-gray);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.feedback-card {
  padding: 1.5rem;
  border-radius: var(--qm-border-radius);
  border: none;
}

.feedback-content h5 {
  font-family: var(--qm-font-heading);
}

/* Emoji Feedback */
.emoji-feedback {
  background: rgba(255, 255, 255, 0.7);
  padding: 1.5rem;
  border-radius: var(--qm-border-radius);
}

.emoji-options {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.emoji-option {
  font-size: 2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
}

.emoji-option:hover {
  transform: scale(1.2);
  background: rgba(52, 152, 219, 0.1);
}

.emoji-option.selected {
  transform: scale(1.3);
  background: var(--qm-electric-blue);
  color: white;
}

/* Submit Modal */
.submission-summary {
  background: rgba(59, 130, 246, 0.05);
  padding: 1.5rem;
  border-radius: var(--qm-border-radius);
  margin: 1rem 0;
}

.summary-stat {
  text-align: center;
}

.summary-stat .stat-number {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.summary-stat .stat-label {
  color: var(--text-subtle);
  font-size: 0.9rem;
}

/* Focus Mode */
:global(.quiz-focus-mode) {
  .navbar {
    transform: translateY(-100%);
    transition: transform 0.3s ease;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .quiz-header .row {
    text-align: center;
  }
  
  .timer-section {
    text-align: center !important;
    margin-top: 1rem;
  }
  
  .question-text {
    font-size: 1.1rem;
    margin-left: 0;
  }
  
  .answer-option {
    padding: 1rem;
    margin-bottom: 0.8rem;
  }
  
  .option-text {
    font-size: 0.95rem;
  }
  
  .score-display .row {
    text-align: center;
  }
  
  .stat-number {
    font-size: 2rem;
  }
  
  .question-dots {
    justify-content: center;
    margin: 1rem 0;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .quiz-intro-icon,
  .timer-display.timer-warning,
  .timer-display.timer-danger,
  .btn.pulse,
  .celebration-header,
  .result-icon {
    animation: none;
  }
  
  .answer-option:hover {
    transform: none;
  }
  
  .answer-option.selected {
    transform: none;
  }
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
  .answer-option {
    border: 2px solid #000;
  }
  
  .answer-option.selected {
    background: #000;
    color: #fff;
  }
}
</style>