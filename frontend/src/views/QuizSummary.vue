<template>
  <DashboardTemplate 
    page-title="Quiz Results"
    page-description="Your quiz performance summary"
    page-icon="fas fa-chart-pie"
    :breadcrumbs="breadcrumbs"
  >
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <!-- Result Header Card -->
        <QmCard class="mb-4">
            <div class="text-center py-5">
            <div class="result-icon mb-3">
              <i :class="resultIcon" :style="{ color: resultColor, fontSize: '4rem' }"></i>
            </div>
            <h2 class="display-4 fw-bold mb-2" :style="{ color: resultColor }">
              {{ quizResult.percentage }}%
            </h2>
            <h4 class="text-muted mb-3">{{ resultMessage }}</h4>
            <p class="lead text-muted">
              You scored {{ quizResult.score }} out of {{ quizResult.total_questions }} questions correctly
            </p>
            <div class="row mt-4">
              <div class="col-md-4">
                <div class="stat-item">
                  <h5 class="text-primary mb-1">{{ quizResult.score }}</h5>
                  <small class="text-muted">Correct Answers</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="stat-item">
                  <h5 class="text-warning mb-1">{{ quizResult.total_questions - quizResult.score }}</h5>
                  <small class="text-muted">Incorrect Answers</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="stat-item">
                  <h5 class="text-info mb-1">{{ formatTime(quizResult.time_taken) }}</h5>
                  <small class="text-muted">Time Taken</small>
                </div>
              </div>
            </div>
            </div>
        </QmCard>

        <!-- Performance Chart -->
        <QmCard class="mb-4">
          <template #header>
            <h5 class="card-title text-primary mb-0">
              <i class="fas fa-chart-pie me-2"></i>Performance Breakdown
            </h5>
          </template>
            <div class="row">
              <div class="col-md-6">
                <canvas ref="performanceChart" width="300" height="300"></canvas>
              </div>
              <div class="col-md-6 d-flex align-items-center">
                <div class="w-100">
                  <div class="performance-legend">
                    <div class="legend-item mb-3">
                      <span class="legend-color bg-success me-2"></span>
                      <span class="fw-medium">Correct: {{ quizResult.score }} questions</span>
                    </div>
                    <div class="legend-item mb-3">
                      <span class="legend-color bg-danger me-2"></span>
                      <span class="fw-medium">Incorrect: {{ quizResult.total_questions - quizResult.score }} questions</span>
                    </div>
                  </div>
                  <div class="mt-4">
                    <div class="progress mb-2" style="height: 20px;">
                      <div 
                        class="progress-bar" 
                        :class="progressBarClass"
                        :style="{ width: quizResult.percentage + '%' }"
                      >
                        {{ quizResult.percentage }}%
                      </div>
                    </div>
                    <small class="text-muted">Overall Performance</small>
                  </div>
                </div>
              </div>
            </div>
        </QmCard>

        <!-- Action Buttons -->
        <QmCard>
            <div class="text-center">
            <div class="d-flex flex-wrap justify-content-center gap-3">
              <router-link to="/my-quizzes" class="btn btn-outline-primary">
                <i class="fas fa-list me-2"></i>View All Attempts
              </router-link>
              <router-link to="/dashboard" class="btn btn-primary">
                <i class="fas fa-tachometer-alt me-2"></i>Back to Dashboard
              </router-link>
              <button @click="retakeQuiz" class="btn btn-outline-success">
                <i class="fas fa-redo me-2"></i>Retake Quiz
              </button>
            </div>
            </div>
        </QmCard>
      </div>
    </div>
  </DashboardTemplate>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Chart, registerables } from 'chart.js'
import DashboardTemplate from '../components/templates/DashboardTemplate.vue'
import QmCard from '../components/atoms/QmCard.vue'

Chart.register(...registerables)

export default {
  name: 'QuizSummary',
  components: {
    DashboardTemplate,
    QmCard
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const performanceChart = ref(null)
    const quizResult = ref({
      score: 0,
      total_questions: 0,
      percentage: 0,
      time_taken: 0,
      quiz_id: null
    })
    
    const breadcrumbs = [
      { text: 'Dashboard', to: '/dashboard', icon: 'fas fa-tachometer-alt' },
      { text: 'Quiz Results', icon: 'fas fa-chart-pie' }
    ]
    
    // Computed properties for result styling
    const resultIcon = computed(() => {
      const percentage = quizResult.value.percentage
      if (percentage >= 80) return 'fas fa-trophy'
      if (percentage >= 60) return 'fas fa-thumbs-up'
      return 'fas fa-chart-line'
    })
    
    const resultColor = computed(() => {
      const percentage = quizResult.value.percentage
      if (percentage >= 80) return '#28a745'
      if (percentage >= 60) return '#ffc107'
      return '#dc3545'
    })
    
    const resultMessage = computed(() => {
      const percentage = quizResult.value.percentage
      if (percentage >= 80) return 'Excellent Performance!'
      if (percentage >= 60) return 'Good Job!'
      return 'Keep Practicing!'
    })
    
    const progressBarClass = computed(() => {
      const percentage = quizResult.value.percentage
      if (percentage >= 80) return 'bg-success'
      if (percentage >= 60) return 'bg-warning'
      return 'bg-danger'
    })
    
    const formatTime = (seconds) => {
      if (!seconds) return '0m 0s'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = Math.floor(seconds % 60)
      return `${minutes}m ${remainingSeconds}s`
    }
    
    const createPerformanceChart = () => {
      if (!performanceChart.value) return
      
      const ctx = performanceChart.value.getContext('2d')
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Correct', 'Incorrect'],
          datasets: [{
            data: [quizResult.value.score, quizResult.value.total_questions - quizResult.value.score],
            backgroundColor: ['#28a745', '#dc3545'],
            borderWidth: 0,
            cutout: '60%'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || ''
                  const value = context.parsed
                  const total = quizResult.value.total_questions
                  const percentage = ((value / total) * 100).toFixed(1)
                  return `${label}: ${value} (${percentage}%)`
                }
              }
            }
          }
        }
      })
    }
    
    const retakeQuiz = () => {
      if (quizResult.value.quiz_id) {
        router.push(`/quiz/${quizResult.value.quiz_id}`)
      }
    }
    
    const loadQuizResult = () => {
      // Get result from route params or localStorage
      const resultData = route.params.result || localStorage.getItem('lastQuizResult')
      
      if (resultData) {
        try {
          const parsed = typeof resultData === 'string' ? JSON.parse(resultData) : resultData
          quizResult.value = {
            score: parsed.score || 0,
            total_questions: parsed.total_questions || 0,
            percentage: parsed.percentage || 0,
            time_taken: parsed.time_taken || 0,
            quiz_id: parsed.quiz_id || null
          }
          
          // Clear localStorage after loading
          localStorage.removeItem('lastQuizResult')
        } catch (error) {
          console.error('Error parsing quiz result:', error)
          router.push('/dashboard')
        }
      } else {
        // No result data, redirect to dashboard
        router.push('/dashboard')
      }
    }
    
    onMounted(() => {
      loadQuizResult()
      setTimeout(() => {
        createPerformanceChart()
      }, 100)
    })
    
    return {
      quizResult,
      breadcrumbs,
      performanceChart,
      resultIcon,
      resultColor,
      resultMessage,
      progressBarClass,
      formatTime,
      retakeQuiz
    }
  }
}
</script>

<style scoped>
.result-icon {
  animation: bounceIn 0.6s ease-out;
}

@keyframes bounceIn {
  0% {
    transform: scale(0.3);
    opacity: 0;
  }
  50% {
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.stat-item {
  padding: 1rem;
  border-radius: 8px;
  background-color: #f8f9fa;
  margin-bottom: 1rem;
}

.legend-color {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.performance-legend .legend-item {
  display: flex;
  align-items: center;
}

.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}

.btn {
  min-width: 150px;
}
</style>