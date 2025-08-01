<template>
  <DashboardTemplate 
    page-title="Score History"
    page-description="Complete history of your quiz performances"
    page-icon="fas fa-history"
    :breadcrumbs="breadcrumbs"
  >
    <!-- Summary Cards -->
    <div class="row mb-4">
      <div class="col-lg-3 col-md-6 mb-3">
        <QmCard variant="primary" class="text-white">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h3 class="mb-1">{{ totalAttempts }}</h3>
              <p class="mb-0 opacity-75">Total Attempts</p>
            </div>
            <i class="fas fa-play fa-2x opacity-75"></i>
          </div>
        </QmCard>
      </div>
      
      <div class="col-lg-3 col-md-6 mb-3">
        <QmCard variant="success" class="text-white">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h3 class="mb-1">{{ averageScore }}%</h3>
              <p class="mb-0 opacity-75">Average Score</p>
            </div>
            <i class="fas fa-chart-line fa-2x opacity-75"></i>
          </div>
        </QmCard>
      </div>
      
      <div class="col-lg-3 col-md-6 mb-3">
        <QmCard variant="warning" class="text-white">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h3 class="mb-1">{{ bestScore }}%</h3>
              <p class="mb-0 opacity-75">Best Score</p>
            </div>
            <i class="fas fa-trophy fa-2x opacity-75"></i>
          </div>
        </QmCard>
      </div>
      
      <div class="col-lg-3 col-md-6 mb-3">
        <QmCard variant="info" class="text-white">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h3 class="mb-1">{{ improvementTrend }}</h3>
              <p class="mb-0 opacity-75">Trend</p>
            </div>
            <i :class="trendIcon" class="fa-2x opacity-75"></i>
          </div>
        </QmCard>
      </div>
    </div>

    <!-- Filters and Search -->
    <QmCard class="mb-4">
        <div class="row align-items-center">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text"><i class="fas fa-search"></i></span>
              <input 
                v-model="searchQuery" 
                type="text" 
                class="form-control" 
                placeholder="Search quizzes..."
              >
            </div>
          </div>
          <div class="col-md-3">
            <select v-model="selectedSubject" class="form-select">
              <option value="">All Subjects</option>
              <option v-for="subject in subjects" :key="subject" :value="subject">
                {{ subject }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <select v-model="sortBy" class="form-select">
              <option value="date_desc">Latest First</option>
              <option value="date_asc">Oldest First</option>
              <option value="score_desc">Highest Score</option>
              <option value="score_asc">Lowest Score</option>
            </select>
          </div>
          <div class="col-md-2">
            <button @click="clearFilters" class="btn btn-outline-secondary w-100">
              <i class="fas fa-times me-1"></i>Clear
            </button>
          </div>
        </div>
    </QmCard>

    <!-- Score History Table -->
    <QmCard>
      <template #header>
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="card-title text-primary mb-0">
            <i class="fas fa-list me-2"></i>Quiz Attempts ({{ filteredAttempts.length }})
          </h5>
          <div class="d-flex gap-2">
            <button @click="toggleView" class="btn btn-sm btn-outline-primary">
              <i :class="viewMode === 'table' ? 'fas fa-th' : 'fas fa-list'"></i>
              {{ viewMode === 'table' ? 'Card View' : 'Table View' }}
            </button>
          </div>
        </div>
      </template>
      <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="text-muted mt-2">Loading your quiz history...</p>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="filteredAttempts.length === 0" class="text-center py-5">
          <i class="fas fa-clipboard-list text-muted" style="font-size: 4rem;"></i>
          <h4 class="text-muted mt-3">No Quiz Attempts Found</h4>
          <p class="text-muted">{{ searchQuery || selectedSubject ? 'Try adjusting your filters' : 'Start taking quizzes to see your history here!' }}</p>
          <router-link to="/dashboard" class="btn btn-primary">
            <i class="fas fa-arrow-left me-2"></i>Back to Dashboard
          </router-link>
        </div>
        
        <!-- Table View -->
        <div v-else-if="viewMode === 'table'" class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Quiz Title</th>
                <th>Subject</th>
                <th>Score</th>
                <th>Performance</th>
                <th>Date</th>
                <th>Time Taken</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="attempt in paginatedAttempts" :key="attempt.id">
                <td>
                  <strong>{{ attempt.quiz_title }}</strong>
                </td>
                <td>
                  <span class="badge bg-primary">{{ attempt.subject_name }}</span>
                </td>
                <td>
                  <span class="fw-bold" :class="getScoreClass(attempt.percentage)">
                    {{ attempt.score }}/{{ attempt.total_questions }}
                  </span>
                </td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="progress me-2" style="width: 100px; height: 8px;">
                      <div 
                        class="progress-bar" 
                        :class="getProgressBarClass(attempt.percentage)"
                        :style="{ width: attempt.percentage + '%' }"
                      ></div>
                    </div>
                    <span class="small fw-bold" :class="getScoreClass(attempt.percentage)">
                      {{ attempt.percentage }}%
                    </span>
                  </div>
                </td>
                <td>
                  <small>{{ formatDate(attempt.completed_at) }}</small>
                </td>
                <td>
                  <small>{{ formatTime(attempt.time_taken) }}</small>
                </td>
                <td>
                  <button 
                    @click="viewDetails(attempt)" 
                    class="btn btn-sm btn-outline-primary"
                    title="View Details"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Card View -->
        <div v-else class="row">
          <div v-for="attempt in paginatedAttempts" :key="attempt.id" class="col-lg-6 col-xl-4 mb-3">
            <div class="card h-100 attempt-card">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="card-title mb-0">{{ attempt.quiz_title }}</h6>
                  <span class="badge bg-primary">{{ attempt.subject_name }}</span>
                </div>
                
                <div class="score-display text-center my-3">
                  <div class="score-circle" :class="getScoreClass(attempt.percentage)">
                    <span class="score-percentage">{{ attempt.percentage }}%</span>
                    <small class="score-fraction">{{ attempt.score }}/{{ attempt.total_questions }}</small>
                  </div>
                </div>
                
                <div class="attempt-meta">
                  <div class="d-flex justify-content-between text-muted small mb-1">
                    <span><i class="fas fa-calendar me-1"></i>{{ formatDate(attempt.completed_at) }}</span>
                    <span><i class="fas fa-clock me-1"></i>{{ formatTime(attempt.time_taken) }}</span>
                  </div>
                </div>
                
                <button 
                  @click="viewDetails(attempt)" 
                  class="btn btn-sm btn-outline-primary w-100 mt-2"
                >
                  <i class="fas fa-eye me-1"></i>View Details
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Pagination -->
        <div v-if="totalPages > 1" class="d-flex justify-content-center mt-4">
          <nav>
            <ul class="pagination">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link" @click="currentPage = 1" :disabled="currentPage === 1">
                  <i class="fas fa-angle-double-left"></i>
                </button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link" @click="currentPage--" :disabled="currentPage === 1">
                  <i class="fas fa-angle-left"></i>
                </button>
              </li>
              
              <li 
                v-for="page in visiblePages" 
                :key="page" 
                class="page-item" 
                :class="{ active: page === currentPage }"
              >
                <button class="page-link" @click="currentPage = page">
                  {{ page }}
                </button>
              </li>
              
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link" @click="currentPage++" :disabled="currentPage === totalPages">
                  <i class="fas fa-angle-right"></i>
                </button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link" @click="currentPage = totalPages" :disabled="currentPage === totalPages">
                  <i class="fas fa-angle-double-right"></i>
                </button>
              </li>
            </ul>
          </nav>
        </div>
    </QmCard>
  </DashboardTemplate>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import DashboardTemplate from '../components/templates/DashboardTemplate.vue'
import QmCard from '../components/atoms/QmCard.vue'

export default {
  name: 'PastScores',
  components: {
    DashboardTemplate,
    QmCard
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const loading = ref(true)
    const attempts = ref([])
    const searchQuery = ref('')
    const selectedSubject = ref('')
    const sortBy = ref('date_desc')
    const viewMode = ref('table')
    const currentPage = ref(1)
    const itemsPerPage = 10
    
    const breadcrumbs = [
      { text: 'Dashboard', to: '/dashboard', icon: 'fas fa-tachometer-alt' },
      { text: 'Score History', icon: 'fas fa-history' }
    ]
    
    // Computed properties
    const subjects = computed(() => {
      const subjectSet = new Set(attempts.value.map(a => a.subject_name).filter(Boolean))
      return Array.from(subjectSet).sort()
    })
    
    const filteredAttempts = computed(() => {
      let filtered = attempts.value
      
      // Search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(attempt => 
          attempt.quiz_title.toLowerCase().includes(query) ||
          attempt.subject_name.toLowerCase().includes(query)
        )
      }
      
      // Subject filter
      if (selectedSubject.value) {
        filtered = filtered.filter(attempt => attempt.subject_name === selectedSubject.value)
      }
      
      // Sort
      filtered.sort((a, b) => {
        switch (sortBy.value) {
          case 'date_asc':
            return new Date(a.completed_at) - new Date(b.completed_at)
          case 'score_desc':
            return b.percentage - a.percentage
          case 'score_asc':
            return a.percentage - b.percentage
          default: // date_desc
            return new Date(b.completed_at) - new Date(a.completed_at)
        }
      })
      
      return filtered
    })
    
    const totalPages = computed(() => Math.ceil(filteredAttempts.value.length / itemsPerPage))
    
    const paginatedAttempts = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return filteredAttempts.value.slice(start, end)
    })
    
    const visiblePages = computed(() => {
      const pages = []
      const total = totalPages.value
      const current = currentPage.value
      
      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i)
        }
      } else {
        if (current <= 4) {
          for (let i = 1; i <= 5; i++) pages.push(i)
          pages.push('...', total)
        } else if (current >= total - 3) {
          pages.push(1, '...')
          for (let i = total - 4; i <= total; i++) pages.push(i)
        } else {
          pages.push(1, '...', current - 1, current, current + 1, '...', total)
        }
      }
      
      return pages.filter(p => p !== '...')
    })
    
    // Statistics
    const totalAttempts = computed(() => attempts.value.length)
    
    const averageScore = computed(() => {
      if (attempts.value.length === 0) return 0
      const sum = attempts.value.reduce((acc, attempt) => acc + attempt.percentage, 0)
      return Math.round(sum / attempts.value.length)
    })
    
    const bestScore = computed(() => {
      if (attempts.value.length === 0) return 0
      return Math.max(...attempts.value.map(a => a.percentage))
    })
    
    const improvementTrend = computed(() => {
      if (attempts.value.length < 2) return 'N/A'
      
      const recent = attempts.value.slice(0, 5)
      const older = attempts.value.slice(5, 10)
      
      if (older.length === 0) return 'N/A'
      
      const recentAvg = recent.reduce((acc, a) => acc + a.percentage, 0) / recent.length
      const olderAvg = older.reduce((acc, a) => acc + a.percentage, 0) / older.length
      
      const diff = recentAvg - olderAvg
      if (diff > 5) return '+' + Math.round(diff) + '%'
      if (diff < -5) return Math.round(diff) + '%'
      return 'Stable'
    })
    
    const trendIcon = computed(() => {
      const trend = improvementTrend.value
      if (trend.startsWith('+')) return 'fas fa-arrow-up'
      if (trend.startsWith('-')) return 'fas fa-arrow-down'
      return 'fas fa-minus'
    })
    
    // Methods
    const fetchAttempts = async () => {
      try {
        loading.value = true
        const result = await store.dispatch('fetchUserScores', {
          page: 1,
          perPage: 100, // Get all attempts for client-side filtering
          sort: 'date_desc'
        })
        
        if (result.success) {
          attempts.value = result.data.attempts || []
        } else {
          console.error('Failed to fetch attempts:', result.message)
          // Fallback to existing method
          await store.dispatch('fetchUserQuizAttempts')
          attempts.value = store.getters.userQuizAttempts || []
        }
      } catch (error) {
        console.error('Error fetching quiz attempts:', error)
        // Fallback to existing method
        try {
          await store.dispatch('fetchUserQuizAttempts')
          attempts.value = store.getters.userQuizAttempts || []
        } catch (fallbackError) {
          console.error('Fallback also failed:', fallbackError)
        }
      } finally {
        loading.value = false
      }
    }
    
    const getScoreClass = (score) => {
      if (score >= 80) return 'text-success'
      if (score >= 60) return 'text-warning'
      return 'text-danger'
    }
    
    const getProgressBarClass = (score) => {
      if (score >= 80) return 'bg-success'
      if (score >= 60) return 'bg-warning'
      return 'bg-danger'
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    const formatTime = (seconds) => {
      if (!seconds) return 'N/A'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = Math.floor(seconds % 60)
      return `${minutes}m ${remainingSeconds}s`
    }
    
    const viewDetails = (attempt) => {
      // Store attempt data and navigate to quiz summary
      const resultData = {
        score: attempt.score,
        total_questions: attempt.total_questions,
        percentage: attempt.percentage,
        time_taken: attempt.time_taken,
        quiz_id: attempt.quiz_id
      }
      
      localStorage.setItem('lastQuizResult', JSON.stringify(resultData))
      router.push('/quiz-summary')
    }
    
    const toggleView = () => {
      viewMode.value = viewMode.value === 'table' ? 'card' : 'table'
    }
    
    const clearFilters = () => {
      searchQuery.value = ''
      selectedSubject.value = ''
      sortBy.value = 'date_desc'
      currentPage.value = 1
    }
    
    onMounted(() => {
      fetchAttempts()
    })
    
    return {
      loading,
      attempts,
      searchQuery,
      selectedSubject,
      sortBy,
      viewMode,
      currentPage,
      breadcrumbs,
      subjects,
      filteredAttempts,
      paginatedAttempts,
      totalPages,
      visiblePages,
      totalAttempts,
      averageScore,
      bestScore,
      improvementTrend,
      trendIcon,
      getScoreClass,
      getProgressBarClass,
      formatDate,
      formatTime,
      viewDetails,
      toggleView,
      clearFilters
    }
  }
}
</script>

<style scoped>
.stat-card {
  border-radius: 12px;
  border: none;
  transition: transform 0.2s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-card-body {
  padding: 1.5rem;
}

.attempt-card {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  border: 1px solid #e9ecef;
}

.attempt-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  border: 3px solid;
  background-color: rgba(255, 255, 255, 0.1);
}

.score-circle.text-success {
  border-color: #28a745;
  background-color: rgba(40, 167, 69, 0.1);
}

.score-circle.text-warning {
  border-color: #ffc107;
  background-color: rgba(255, 193, 7, 0.1);
}

.score-circle.text-danger {
  border-color: #dc3545;
  background-color: rgba(220, 53, 69, 0.1);
}

.score-percentage {
  font-size: 1.1rem;
  font-weight: bold;
  line-height: 1;
}

.score-fraction {
  font-size: 0.7rem;
  opacity: 0.8;
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
  background-color: #e9ecef;
}

.pagination .page-link {
  border: 1px solid #dee2e6;
  color: #6c757d;
}

.pagination .page-item.active .page-link {
  background-color: #007bff;
  border-color: #007bff;
}

.pagination .page-link:hover {
  background-color: #e9ecef;
  border-color: #dee2e6;
}
</style>