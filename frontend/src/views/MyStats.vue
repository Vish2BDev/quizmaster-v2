<template>
  <DashboardTemplate 
    page-title="My Statistics"
    page-description="Detailed analysis of your quiz performance"
    page-icon="fas fa-chart-line"
    :breadcrumbs="breadcrumbs"
  >
    <div class="row">
      <!-- Performance Overview Cards -->
      <div class="col-lg-3 col-md-6 mb-4">
        <QmCard variant="primary" class="stat-card">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h3 class="stat-number text-primary mb-1">{{ stats.totalAttempts }}</h3>
              <p class="stat-label text-muted mb-0">Total Attempts</p>
            </div>
            <div class="stat-icon bg-primary">
              <i class="fas fa-play text-white"></i>
            </div>
          </div>
        </QmCard>
      </div>
      
      <div class="col-lg-3 col-md-6 mb-4">
        <QmCard variant="success" class="stat-card">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h3 class="stat-number text-success mb-1">{{ stats.averageScore }}%</h3>
              <p class="stat-label text-muted mb-0">Average Score</p>
            </div>
            <div class="stat-icon bg-success">
              <i class="fas fa-chart-line text-white"></i>
            </div>
          </div>
        </QmCard>
      </div>
      
      <div class="col-lg-3 col-md-6 mb-4">
        <QmCard variant="warning" class="stat-card">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h3 class="stat-number text-warning mb-1">{{ stats.bestScore }}%</h3>
              <p class="stat-label text-muted mb-0">Best Score</p>
            </div>
            <div class="stat-icon bg-warning">
              <i class="fas fa-trophy text-white"></i>
            </div>
          </div>
        </QmCard>
      </div>
      
      <div class="col-lg-3 col-md-6 mb-4">
        <QmCard variant="info" class="stat-card">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h3 class="stat-number text-info mb-1">{{ stats.streak }}</h3>
              <p class="stat-label text-muted mb-0">Current Streak</p>
            </div>
            <div class="stat-icon bg-info">
              <i class="fas fa-fire text-white"></i>
            </div>
          </div>
        </QmCard>
      </div>
    </div>
    
    <div class="row">
      <!-- Performance Chart -->
      <div class="col-lg-8 mb-4">
        <QmCard>
          <template #header>
            <h5 class="card-title text-primary mb-0">
              <i class="fas fa-chart-area me-2"></i>Performance Trend
            </h5>
          </template>
          <template #content>
            <canvas ref="performanceChart" height="300"></canvas>
          </template>
        </QmCard>
      </div>
      
      <!-- Subject Performance -->
      <div class="col-lg-4 mb-4">
        <QmCard>
          <template #header>
            <h5 class="card-title text-primary mb-0">
              <i class="fas fa-book me-2"></i>Subject Performance
            </h5>
          </template>
          <div v-if="subjectStats.length === 0" class="text-center py-4">
            <i class="fas fa-chart-pie text-muted" style="font-size: 3rem;"></i>
            <p class="text-muted mt-2">No subject data available</p>
          </div>
          <div v-else>
            <div v-for="subject in subjectStats" :key="subject.name" class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-medium">{{ subject.name }}</span>
                <span class="text-primary fw-bold">{{ subject.average }}%</span>
              </div>
              <div class="progress" style="height: 8px;">
                <div 
                  class="progress-bar" 
                  :class="getProgressBarClass(subject.average)"
                  :style="{ width: subject.average + '%' }"
                ></div>
              </div>
              <small class="text-muted">{{ subject.attempts }} attempts</small>
            </div>
          </div>
        </QmCard>
      </div>
    </div>
    
    <div class="row">
      <!-- Recent Activity -->
      <div class="col-12">
        <QmCard>
          <template #header>
            <h5 class="card-title text-primary mb-0">
              <i class="fas fa-history me-2"></i>Recent Quiz Attempts
            </h5>
          </template>
          <div v-if="recentAttempts.length === 0" class="text-center py-4">
            <i class="fas fa-clipboard-list text-muted" style="font-size: 3rem;"></i>
            <p class="text-muted mt-2">No recent attempts</p>
          </div>
          <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Quiz</th>
                    <th>Subject</th>
                    <th>Score</th>
                    <th>Date</th>
                    <th>Time Taken</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="attempt in recentAttempts" :key="attempt.id">
                    <td><strong>{{ attempt.quiz_title }}</strong></td>
                    <td><QmBadge variant="primary">{{ attempt.subject }}</QmBadge></td>
                    <td>
                      <span class="fw-bold" :class="getScoreClass(attempt.score)">
                        {{ attempt.score }}%
                      </span>
                    </td>
                    <td>{{ formatDate(attempt.date) }}</td>
                    <td>{{ attempt.time_taken }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
        </QmCard>
      </div>
    </div>
  </DashboardTemplate>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { useStore } from 'vuex'
import DashboardTemplate from '@/components/templates/DashboardTemplate.vue'
import QmCard from '@/components/atoms/QmCard.vue'
import QmBadge from '@/components/atoms/QmBadge.vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'MyStats',
  components: {
    DashboardTemplate,
    QmCard,
    QmBadge
  },
  setup() {
    const store = useStore()
    const performanceChart = ref(null)
    const chartInstance = ref(null)
    
    const breadcrumbs = [
      { text: 'Dashboard', to: '/dashboard', icon: 'fas fa-tachometer-alt' },
      { text: 'My Stats', icon: 'fas fa-chart-line' }
    ]
    
    const stats = ref({
      totalAttempts: 12,
      averageScore: 75,
      bestScore: 95,
      streak: 3
    })
    
    const subjectStats = ref([
      { name: 'Mathematics', average: 85, attempts: 8 },
      { name: 'Science', average: 72, attempts: 4 },
      { name: 'History', average: 68, attempts: 2 }
    ])
    
    const recentAttempts = ref([
      {
        id: 1,
        quiz_title: 'Linear Equations',
        subject: 'Mathematics',
        score: 85,
        date: new Date().toISOString(),
        time_taken: '5m 30s'
      },
      {
        id: 2,
        quiz_title: 'Basic Chemistry',
        subject: 'Science',
        score: 72,
        date: new Date(Date.now() - 86400000).toISOString(),
        time_taken: '8m 15s'
      }
    ])
    
    const createPerformanceChart = () => {
      if (!performanceChart.value) return
      
      const ctx = performanceChart.value.getContext('2d')
      
      if (chartInstance.value) {
        chartInstance.value.destroy()
      }
      
      chartInstance.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
          datasets: [{
            label: 'Average Score',
            data: [65, 70, 75, 72, 78, 85],
            borderColor: '#007bff',
            backgroundColor: 'rgba(0, 123, 255, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function(value) {
                  return value + '%'
                }
              }
            }
          }
        }
      })
    }
    
    const getProgressBarClass = (score) => {
      if (score >= 80) return 'bg-success'
      if (score >= 60) return 'bg-warning'
      return 'bg-danger'
    }
    
    const getScoreClass = (score) => {
      if (score >= 80) return 'text-success'
      if (score >= 60) return 'text-warning'
      return 'text-danger'
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    }
    
    onMounted(async () => {
      await nextTick()
      createPerformanceChart()
    })
    
    return {
      performanceChart,
      breadcrumbs,
      stats,
      subjectStats,
      recentAttempts,
      getProgressBarClass,
      getScoreClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.stat-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-card-body {
  padding: 1.5rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 500;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.table th {
  background-color: #f8f9fa;
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.table-hover tbody tr:hover {
  background-color: rgba(0, 123, 255, 0.05);
}

.progress {
  border-radius: 10px;
}

.progress-bar {
  border-radius: 10px;
}
</style>