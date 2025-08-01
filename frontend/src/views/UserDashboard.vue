<template>
  <DashboardTemplate
    title="Dashboard Overview"
    subtitle="Track your progress and performance"
    :breadcrumbs="breadcrumbs"
    :stats="dashboardStats"
    :loading="loading"
    show-search
    show-theme-toggle
  >
    <template #header-actions>
      <QmBtn
        variant="outline-primary"
        size="sm"
        @click="setActiveTab('export')"
      >
        <i class="fas fa-download me-2"></i>
        Export Data
      </QmBtn>
    </template>
    
    <template #content>
      <!-- Quick Export Section -->
      <div class="row mb-4">
        <div class="col-12 d-flex justify-content-end">
          <ExportButton 
            export-type="user-history"
            button-text="Export My Quiz History"
            button-class="btn btn-outline-success btn-sm"
          />
        </div>
      </div>

    <!-- User Search Section -->
    <div class="mb-4">
      <UserSearch
        @quiz-selected="handleQuizSelected"
        @start-quiz="handleStartQuiz"
        @subject-selected="handleSubjectSelected"
        @explore-subject="handleExploreSubject"
      />
    </div>

    <div class="container-fluid">

      <div class="row">
        <!-- Main Content Area -->
        <div class="col-12">
          <!-- Search Bar -->
          <div class="search-section mb-4" v-if="activeTab === 'quizzes'">
            <div class="search-container">
              <div class="input-group">
                <span class="input-group-text">
                  <i class="fas fa-search"></i>
                </span>
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Search quizzes by title, subject, or chapter..."
                  v-model="searchQuery"
                  @input="debouncedSearch"
                >
                <button 
                  v-if="searchQuery" 
                  class="btn btn-outline-secondary" 
                  @click="clearSearch"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <div v-if="searchSuggestions.length > 0" class="search-suggestions">
                <div 
                  v-for="suggestion in searchSuggestions" 
                  :key="suggestion.id"
                  class="suggestion-item"
                  @click="selectSuggestion(suggestion)"
                >
                  <i class="fas fa-search me-2"></i>
                  {{ suggestion.title }}
                  <small class="text-muted ms-2">{{ suggestion.subject }}</small>
                </div>
              </div>
            </div>
          </div>

          <!-- Overview Tab -->
          <div v-if="activeTab === 'overview'" class="tab-content">

            <!-- Recent Activity & Quick Actions -->
            <div class="row">
              <div class="col-md-8">
                <div class="card shadow-sm border-0 mb-4">
                  <div class="card-header bg-white border-bottom">
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <h5 class="card-title text-primary mb-1">
                          <i class="fas fa-history me-2"></i>Recent Quiz Attempts
                        </h5>
                        <p class="text-muted small mb-0">Your latest quiz performance</p>
                      </div>
                      <router-link to="/past-scores" class="btn btn-outline-primary btn-sm">
                        <i class="fas fa-history me-1"></i>View All Scores
                      </router-link>
                    </div>
                  </div>
                  <div class="card-body">
                    <div v-if="userPerformance?.recent_attempts?.length > 0">
                      <div class="timeline">
                        <div v-for="attempt in userPerformance.recent_attempts.slice(0, 5)" :key="attempt.quiz_title" 
                             class="timeline-item">
                          <div class="timeline-marker" :class="getScoreBadgeClass(attempt.percentage)"></div>
                          <div class="timeline-content">
                            <div class="timeline-header">
                              <h6 class="timeline-title mb-1">{{ attempt.quiz_title }}</h6>
                              <span class="timeline-time text-muted small">{{ formatDate(attempt.completed_at) }}</span>
                            </div>
                            <div class="timeline-body">
                              <div class="d-flex justify-content-between align-items-center">
                                <div class="score-info">
                                  <span class="badge" :class="getScoreBadgeClass(attempt.percentage)">
                                    {{ attempt.score }}/{{ attempt.total_questions }} ({{ attempt.percentage }}%)
                                  </span>
                                </div>
                                <div class="attempt-actions">
                                  <button class="btn btn-sm btn-outline-primary" @click="reviewQuiz(attempt.quiz_id)">
                                    <i class="fas fa-eye me-1"></i>Review
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-else class="text-center text-muted py-4">
                      <i class="fas fa-clipboard-list fa-3x mb-3 opacity-50"></i>
                      <p>No quiz attempts yet. Start your learning journey!</p>
                      <button @click="activeTab = 'quizzes'" class="btn btn-primary">
                        <i class="fas fa-play me-2"></i>Take Your First Quiz
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-4">
                <!-- Study Motivation Widget -->
                <div class="card shadow-sm border-0 mb-3">
                  <div class="card-header bg-white border-bottom">
                    <h6 class="text-primary mb-0">
                      <i class="fas fa-target me-2"></i>Today's Goal
                    </h6>
                  </div>
                  <div class="card-body">
                    <div class="goal-progress">
                      <div class="d-flex justify-content-between mb-2">
                        <span>Quiz Progress</span>
                        <span>{{ todayQuizzes }}/3</span>
                      </div>
                      <div class="qm-progress">
                        <div class="qm-progress-fill" :style="{ width: (todayQuizzes / 3 * 100) + '%' }"></div>
                      </div>
                      <p class="small text-muted mt-2">{{ getMotivationalMessage() }}</p>
                    </div>
                  </div>
                </div>

                <!-- Achievement Progress Widget -->
                <div class="card shadow-sm border-0">
                  <div class="card-header bg-white border-bottom">
                    <h6 class="text-primary mb-0">
                      <i class="fas fa-trophy me-2"></i>Achievement Progress
                    </h6>
                  </div>
                  <div class="card-body">
                    <div class="achievement-progress">
                      <div class="d-flex justify-content-between align-items-center mb-2">
                        <span>Unlocked</span>
                        <strong>{{ userAchievements.length }}/{{ userAchievements.length + lockedAchievements.length }}</strong>
                      </div>
                      <div class="qm-progress">
                        <div class="qm-progress-fill" :style="{ width: (userAchievements.length / (userAchievements.length + lockedAchievements.length) * 100) + '%' }"></div>
                      </div>
                      <p class="small text-muted mt-2">Keep taking quizzes to unlock more achievements!</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Export Tab -->
          <div v-if="activeTab === 'export'" class="tab-content">
            <UserExport />
          </div>
          
          <!-- Available Quizzes Tab - Curiosity Trigger -->
          <div v-if="activeTab === 'quizzes'" class="tab-content">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h2 class="text-primary">Available Quizzes</h2>
              <div class="quiz-filters">
                <select v-model="selectedSubject" class="form-select" @change="filterQuizzes">
                  <option value="">All Subjects</option>
                  <option v-for="subject in uniqueSubjects" :key="subject" :value="subject">{{ subject }}</option>
                </select>
              </div>
            </div>
            
            <div class="row">
              <div v-for="quiz in filteredQuizzes" :key="quiz.id" class="col-md-6 col-lg-4 mb-4">
                <div class="card shadow-sm border-0 quiz-card h-100" @mouseenter="previewQuiz(quiz)" @mouseleave="hidePreview">
                  <div class="card-header bg-white border-bottom">
                    <div class="d-flex justify-content-between align-items-center">
                      <div class="d-flex gap-2">
                        <span class="badge" :class="getDifficultyBadge(quiz.questions_count)">
                          {{ getDifficultyLevel(quiz.questions_count) }}
                        </span>
                        <span class="badge" :class="getQuizStatusBadgeClass(quiz.status)">
                          {{ getQuizStatusText(quiz.status) }}
                        </span>
                      </div>
                      <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>{{ quiz.duration_minutes || quiz.duration }}min
                      </small>
                    </div>
                  </div>
                  <div class="card-body">
                    <h5 class="card-title text-primary">{{ quiz.title }}</h5>
                    <p class="card-text text-muted">{{ quiz.description || 'Test your knowledge in this topic' }}</p>
                    
                    <div class="quiz-meta mb-3">
                      <div class="meta-item">
                        <i class="fas fa-book-open text-primary me-1"></i>
                        <small>{{ quiz.subject }} → {{ quiz.chapter }}</small>
                      </div>
                      <div class="meta-item">
                        <i class="fas fa-question-circle text-info me-1"></i>
                        <small>{{ quiz.questions_count }} questions</small>
                      </div>
                      <div v-if="quiz.start_time" class="meta-item">
                        <i class="fas fa-calendar text-warning me-1"></i>
                        <small>{{ getQuizScheduleText(quiz) }}</small>
                      </div>
                      <div v-if="quiz.status === 'active' && quiz.remaining_time" class="meta-item">
                        <i class="fas fa-hourglass-half text-danger me-1"></i>
                        <small>{{ formatRemainingTime(quiz.remaining_time) }} remaining</small>
                      </div>
                    </div>

                    <!-- Quiz Preview (shown on hover) -->
                    <div v-if="previewedQuiz?.id === quiz.id" class="quiz-preview">
                      <div class="preview-content">
                        <p class="small text-muted mb-2">
                          <i class="fas fa-eye me-1"></i>Preview: This quiz covers fundamental concepts...
                        </p>
                        <div class="estimated-time">
                          <i class="fas fa-stopwatch me-1"></i>
                          <small>Estimated completion: {{ quiz.duration }} min</small>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="card-footer bg-transparent">
                    <button 
                      v-if="quiz.status === 'active'"
                      @click="startQuiz(quiz)"
                      class="btn btn-primary w-100"
                    >
                      <i class="fas fa-play me-2"></i>Start Quiz
                    </button>
                    <button 
                      v-else-if="quiz.status === 'upcoming'"
                      class="btn btn-outline-warning w-100" 
                      disabled
                    >
                      <i class="fas fa-clock me-2"></i>Starts {{ formatStartTime(quiz.start_time) }}
                    </button>
                    <button 
                      v-else-if="quiz.status === 'expired'"
                      class="btn btn-outline-danger w-100" 
                      disabled
                    >
                      <i class="fas fa-times me-2"></i>Quiz Expired
                    </button>
                    <button 
                      v-else
                      class="btn btn-outline-secondary w-100" 
                      disabled
                    >
                      <i class="fas fa-ban me-2"></i>Not Available
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="filteredQuizzes.length === 0" class="text-center text-muted py-5">
              <i class="fas fa-search fa-3x mb-3 opacity-50"></i>
              <h4>No quizzes found</h4>
              <p>Try adjusting your filters or check back later for new content.</p>
            </div>
          </div>
          
          <!-- Performance Tab - Growth Visualization -->
          <div v-if="activeTab === 'performance'" class="tab-content">
            <h2 class="text-primary mb-4">Performance Analytics</h2>
            
            <!-- Performance Overview Cards -->
            <div class="row mb-4">
              <div class="col-md-4">
                <div class="widget-qm text-center">
                  <div class="performance-circle">
                    <canvas ref="accuracyChart" width="120" height="120"></canvas>
                    <div class="circle-text">
                      <div class="percentage">{{ getOverallAccuracy() }}%</div>
                      <div class="label">Accuracy</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-8">
                <div class="widget-qm">
                  <h6 class="text-primary mb-3">Score Progression</h6>
                  <div class="chart-container">
                    <canvas ref="progressChart"></canvas>
                  </div>
                </div>
              </div>
            </div>

            <!-- Subject Performance Breakdown -->
            <div class="card-qm">
              <div class="card-header bg-transparent">
                <h5 class="text-primary mb-0">Subject Performance Breakdown</h5>
              </div>
              <div class="card-body">
                <div v-if="userPerformance?.subject_performance">
                  <div v-for="(performance, subject) in userPerformance.subject_performance" :key="subject" 
                       class="subject-performance-item mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <h6 class="mb-0">{{ subject }}</h6>
                      <span class="badge" :class="getScoreBadgeClass(getSuccessRate(performance))">
                        {{ getSuccessRate(performance) }}%
                      </span>
                    </div>
                    <div class="row">
                      <div class="col-md-8">
                        <div class="qm-progress">
                          <div class="qm-progress-fill" :style="{ width: getSuccessRate(performance) + '%' }"></div>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <small class="text-muted">
                          {{ performance.total_score }}/{{ performance.total_questions }} 
                          ({{ performance.total_attempts }} attempts)
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center text-muted py-4">
                  <i class="fas fa-chart-line fa-3x mb-3 opacity-50"></i>
                  <p>No performance data available yet. Take some quizzes to see your progress!</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Leaderboard Tab -->
          <div v-if="activeTab === 'leaderboard'" class="tab-content">
            <h2 class="text-primary mb-4">Leaderboard</h2>
            
            <!-- Your Rank Card -->
            <div class="card shadow-sm border-0 mb-4">
              <div class="card-header bg-white border-bottom">
                <h5 class="card-title text-primary mb-1">
                  <i class="fas fa-user-circle me-2"></i>Your Current Rank
                </h5>
                <p class="text-muted small mb-0">This week's performance ranking</p>
              </div>
              <div class="card-body">
                <div class="row align-items-center">
                  <div class="col-md-8">
                    <div class="d-flex align-items-center">
                      <div class="rank-display me-3">
                        <span class="rank-number">#{{ currentUserRank?.rank || '—' }}</span>
                      </div>
                      <div>
                        <small class="text-muted d-block">of {{ totalUsers || '0' }} students</small>
                        <small class="text-success">{{ currentUserRank?.points || 0 }} points this week</small>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4 text-end">
                    <button class="btn btn-outline-primary btn-sm" @click="setActiveTab('performance')">
                      <i class="fas fa-chart-line me-1"></i>View Stats
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Top Performers -->
            <div class="card shadow-sm border-0">
              <div class="card-header bg-white border-bottom">
                <div class="d-flex justify-content-between align-items-center">
                  <h5 class="card-title text-primary mb-0">
                    <i class="fas fa-crown me-2"></i>Top Performers This Week
                  </h5>
                  <span class="badge bg-primary">{{ leaderboard.length }} active</span>
                </div>
              </div>
              <div class="card-body">
                <div v-for="(leader, index) in leaderboard" :key="leader.id" class="leaderboard-item">
                  <div class="d-flex align-items-center">
                    <div class="rank-badge me-3">
                      <span v-if="index < 3" class="trophy-icon">
                        <i :class="getTrophyIcon(index)" :style="{ color: getTrophyColor(index) }"></i>
                      </span>
                      <span v-else class="rank-text">#{{ index + 1 }}</span>
                    </div>
                    <div class="leader-info flex-grow-1">
                      <div class="leader-name">{{ leader.username }}</div>
                      <div class="leader-stats text-muted small">
                        {{ leader.total_score }} points • {{ leader.total_attempts }} quizzes
                      </div>
                    </div>
                    <div class="leader-score">
                      <span class="score-value">{{ leader.avg_percentage }}%</span>
                    </div>
                  </div>
                </div>
                
                <div v-if="leaderboard.length === 0" class="text-center text-muted py-4">
                  <i class="fas fa-trophy fa-3x mb-3 opacity-50"></i>
                  <p>Leaderboard data will be available soon!</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Achievements Tab -->
          <div v-if="activeTab === 'achievements'" class="tab-content">
            <h2 class="text-primary mb-4">Your Achievements</h2>
            
            <div class="row">
              <div v-for="achievement in userAchievements" :key="achievement.id" class="col-md-6 col-lg-4 mb-4">
                <div class="achievement-card card-qm h-100">
                  <div class="card-body text-center">
                    <div class="achievement-icon mb-3">
                      <i :class="achievement.icon" :style="{ color: achievement.color, fontSize: '3rem' }"></i>
                    </div>
                    <h5 class="card-title">{{ achievement.title }}</h5>
                    <p class="card-text text-muted">{{ achievement.description }}</p>
                    <div class="badge-qm">{{ achievement.date }}</div>
                  </div>
                </div>
              </div>
              
              <!-- Locked Achievements Preview -->
              <div v-for="locked in lockedAchievements" :key="locked.id" class="col-md-6 col-lg-4 mb-4">
                <div class="achievement-card card-qm h-100 locked">
                  <div class="card-body text-center">
                    <div class="achievement-icon mb-3">
                      <i class="fas fa-lock" style="color: #ccc; font-size: 3rem;"></i>
                    </div>
                    <h5 class="card-title text-muted">{{ locked.title }}</h5>
                    <p class="card-text text-muted small">{{ locked.description }}</p>
                    <div class="progress-to-unlock">
                      <div class="qm-progress">
                        <div class="qm-progress-fill" :style="{ width: locked.progress + '%' }"></div>
                      </div>
                      <small class="text-muted mt-1">{{ locked.progress }}% complete</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="userAchievements.length === 0" class="text-center text-muted py-5">
              <i class="fas fa-trophy fa-3x mb-3 opacity-50"></i>
              <h4>No achievements yet</h4>
              <p>Start taking quizzes to unlock your first achievement!</p>
              <button @click="setActiveTab('quizzes')" class="btn btn-qm-primary">
                <i class="fas fa-play me-2"></i>Take a Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    </template>
  </DashboardTemplate>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Chart, registerables } from 'chart.js'
import DashboardTemplate from '@/components/templates/DashboardTemplate.vue'
import QmBtn from '@/components/atoms/QmBtn.vue'
import UserExport from '@/components/UserExport.vue'
import UserSearch from '@/components/UserSearch.vue'
import ExportButton from '@/components/ExportButton.vue'
import api from '@/services/api'

Chart.register(...registerables)

export default {
  name: 'UserDashboard',
  components: {
    DashboardTemplate,
    QmBtn,
    UserExport,
    UserSearch,
    ExportButton
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // Breadcrumbs data
    const breadcrumbs = ref([
      { text: 'Dashboard', icon: 'fas fa-tachometer-alt' }
    ])
    const activeTab = ref('overview')
    const selectedSubject = ref('')
    const previewedQuiz = ref(null)
    const progressChart = ref(null)
    const accuracyChart = ref(null)
    const searchQuery = ref('')
    const showSearchSuggestions = ref(false)
    const sessionTimeoutId = ref(null)
    const lastActivityTime = ref(Date.now())
    
    // Mock data based on document requirements
    const todayQuizzes = ref(1)
    const communityStats = ref({ totalUsers: 847 })
    
    const user = computed(() => store.getters.currentUser)
    const userPerformance = computed(() => store.state.userPerformance)
    const availableQuizzes = computed(() => store.state.quizzes)
    
    // Breadcrumb navigation handled by ref above
    
    // Search suggestions
    const searchSuggestions = computed(() => {
      if (!searchQuery.value || searchQuery.value.length < 2) return []
      
      const query = searchQuery.value.toLowerCase()
      return availableQuizzes.value
        .filter(quiz => 
          quiz.title?.toLowerCase().includes(query) ||
          quiz.subject?.toLowerCase().includes(query)
        )
        .slice(0, 5)
        .map(quiz => ({
          id: quiz.id,
          title: quiz.title,
          subject: quiz.subject,
          type: 'quiz'
        }))
    })
    
    // Mock leaderboard data
    const leaderboard = ref([])
    const totalUsers = ref(0)
    const currentUserRank = ref(null)
    
    const filteredQuizzes = computed(() => {
      if (!selectedSubject.value) return availableQuizzes.value
      return availableQuizzes.value.filter(quiz => quiz.subject === selectedSubject.value)
    })
    
    const uniqueSubjects = computed(() => {
      return [...new Set(availableQuizzes.value.map(quiz => quiz.subject))]
    })
    
    // Loading state
    const loading = ref(false)
    
    // Dashboard stats for template
    const dashboardStats = computed(() => [
      {
        title: 'Total Attempts',
        value: userPerformance.value?.total_attempts || 0,
        icon: 'fas fa-play',
        color: 'primary',
        trend: `+${todayQuizzes.value || 0} this week`,
        trendIcon: 'fas fa-arrow-up',
        trendColor: 'success'
      },
      {
        title: 'Best Score',
        value: `${getBestScore()}%`,
        icon: 'fas fa-trophy',
        color: 'success',
        trend: 'Personal best',
        trendIcon: 'fas fa-star',
        trendColor: 'success'
      },
      {
        title: 'Average Score',
        value: `${getAverageScore()}%`,
        icon: 'fas fa-chart-line',
        color: 'info',
        trend: 'Across all quizzes',
        trendIcon: 'fas fa-calculator',
        trendColor: 'info'
      },
      {
        title: 'Current Streak',
        value: getCurrentStreak(),
        icon: 'fas fa-fire',
        color: 'warning',
        trend: 'Days in a row',
        trendIcon: 'fas fa-calendar',
        trendColor: 'warning'
      }
    ])

    // Real achievements data
    const userAchievements = ref([])
    const lockedAchievements = ref([])
    const achievementStats = ref({})
    
    const getBestScore = () => {
      if (!userPerformance.value?.recent_attempts?.length) return 0
      return Math.max(...userPerformance.value.recent_attempts.map(a => a.percentage))
    }
    
    const getAverageScore = () => {
      if (!userPerformance.value?.recent_attempts?.length) return 0
      const total = userPerformance.value.recent_attempts.reduce((sum, a) => sum + a.percentage, 0)
      return Math.round(total / userPerformance.value.recent_attempts.length)
    }

    const getCurrentStreak = () => {
      // Mock streak calculation
      return 5
    }

    const getOverallAccuracy = () => {
      return getAverageScore()
    }



    const getMotivationalMessage = () => {
      const messages = [
        "You're on fire! Keep it up! 🔥",
        "Great progress today! 🎯",
        "One more quiz to reach your goal! 💪",
        "You've got this! 🌟"
      ]
      return messages[todayQuizzes.value] || messages[0]
    }
    
    const getSuccessRate = (performance) => {
      if (!performance.total_questions) return 0
      return Math.round((performance.total_score / performance.total_questions) * 100)
    }
    
    const getScoreBadgeClass = (percentage) => {
      if (percentage >= 80) return 'bg-success'
      if (percentage >= 60) return 'bg-warning'
      return 'bg-danger'
    }

    const getDifficultyLevel = (questionCount) => {
      if (questionCount <= 5) return 'Easy'
      if (questionCount <= 10) return 'Medium' 
      return 'Hard'
    }

    const getDifficultyBadge = (questionCount) => {
      if (questionCount <= 5) return 'bg-success'
      if (questionCount <= 10) return 'bg-warning'
      return 'bg-danger'
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    const previewQuiz = (quiz) => {
      previewedQuiz.value = quiz
    }

    const hidePreview = () => {
      previewedQuiz.value = null
    }

    const trackQuizStart = (quiz) => {
      // Analytics tracking
      console.log('Quiz started:', quiz.title)
      updateActivity()
    }

    const startQuiz = (quiz) => {
      trackQuizStart(quiz)
      router.push(`/quiz/${quiz.id}`)
    }

    const getQuizStatusBadgeClass = (status) => {
      switch (status) {
        case 'active': return 'bg-success'
        case 'upcoming': return 'bg-warning text-dark'
        case 'expired': return 'bg-danger'
        default: return 'bg-secondary'
      }
    }

    const getQuizStatusText = (status) => {
      switch (status) {
        case 'active': return 'Active'
        case 'upcoming': return 'Upcoming'
        case 'expired': return 'Expired'
        default: return 'Inactive'
      }
    }

    const getQuizScheduleText = (quiz) => {
      if (!quiz.start_time) return ''
      const startTime = new Date(quiz.start_time)
      const now = new Date()
      
      if (quiz.status === 'upcoming') {
        return `Starts ${formatStartTime(quiz.start_time)}`
      } else if (quiz.status === 'active') {
        return `Started ${formatStartTime(quiz.start_time)}`
      } else if (quiz.status === 'expired') {
        return `Ended ${formatEndTime(quiz)}`
      }
      return ''
    }

    const formatStartTime = (startTime) => {
      if (!startTime) return ''
      const date = new Date(startTime)
      const now = new Date()
      const diffMs = date.getTime() - now.getTime()
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffDays = Math.floor(diffHours / 24)
      
      if (diffDays > 0) {
        return `in ${diffDays} day${diffDays > 1 ? 's' : ''}`
      } else if (diffHours > 0) {
        return `in ${diffHours} hour${diffHours > 1 ? 's' : ''}`
      } else {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    }

    const formatEndTime = (quiz) => {
      if (!quiz.start_time || !quiz.duration_minutes) return ''
      const startTime = new Date(quiz.start_time)
      const endTime = new Date(startTime.getTime() + quiz.duration_minutes * 60000)
      return endTime.toLocaleString()
    }

    const formatRemainingTime = (remainingMinutes) => {
      if (!remainingMinutes || remainingMinutes <= 0) return '0 min'
      const hours = Math.floor(remainingMinutes / 60)
      const minutes = Math.floor(remainingMinutes % 60)
      
      if (hours > 0) {
        return `${hours}h ${minutes}m`
      }
      return `${minutes}m`
    }

    const filterQuizzes = () => {
      // Filter logic handled by computed property
    }
    
    // Leaderboard helper functions
    const getTrophyIcon = (index) => {
      switch (index) {
        case 0: return 'fas fa-trophy'
        case 1: return 'fas fa-medal'
        case 2: return 'fas fa-award'
        default: return ''
      }
    }
    
    const getTrophyColor = (index) => {
      switch (index) {
        case 0: return '#ffd700' // Gold
        case 1: return '#c0c0c0' // Silver
        case 2: return '#cd7f32' // Bronze
        default: return '#6c757d'
      }
    }
    
    // Tab management
    const setActiveTab = (tab) => {
      activeTab.value = tab
      updateActivity()
    }
    
    // Search functionality
    const clearSearch = () => {
      searchQuery.value = ''
      showSearchSuggestions.value = false
    }
    
    const selectSuggestion = (suggestion) => {
      if (suggestion.type === 'quiz') {
        router.push(`/quiz/${suggestion.id}`)
      }
      clearSearch()
    }
    
    // Session timeout management
    const SESSION_TIMEOUT = 30 * 60 * 1000 // 30 minutes
    
    const updateActivity = () => {
      lastActivityTime.value = Date.now()
      resetSessionTimeout()
    }
    
    const resetSessionTimeout = () => {
      if (sessionTimeoutId.value) {
        clearTimeout(sessionTimeoutId.value)
      }
      
      sessionTimeoutId.value = setTimeout(() => {
        showToast('Session expired due to inactivity. Please log in again.', 'warning')
        handleLogout()
      }, SESSION_TIMEOUT)
    }
    
    // Toast notification system
    const showToast = (message, type = 'info') => {
      // Simple toast implementation - in a real app, you'd use a proper toast library
      const toast = document.createElement('div')
      toast.className = `alert alert-${type} position-fixed`
      toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;'
      toast.innerHTML = `
        <div class="d-flex align-items-center">
          <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
          <span>${message}</span>
          <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
      `
      document.body.appendChild(toast)
      
      setTimeout(() => {
        if (toast.parentElement) {
          toast.remove()
        }
      }, 5000)
    }
    
    const createProgressChart = () => {
      if (!progressChart.value || !userPerformance.value?.recent_attempts) return
      
      const ctx = progressChart.value.getContext('2d')
      const attempts = userPerformance.value.recent_attempts.slice(-10)
      
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: attempts.map((_, index) => `Quiz ${index + 1}`),
          datasets: [{
            label: 'Score %',
            data: attempts.map(a => a.percentage),
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            tension: 0.4,
            fill: true
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
              max: 100
            }
          }
        }
      })
    }

    const createAccuracyChart = () => {
      if (!accuracyChart.value) return
      
      const ctx = accuracyChart.value.getContext('2d')
      const accuracy = getOverallAccuracy()
      
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          datasets: [{
            data: [accuracy, 100 - accuracy],
            backgroundColor: ['#2ecc71', '#ecf0f1'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: false,
          cutout: '70%',
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    }
    

    

    


    

    

    
    const reviewQuiz = (quizId) => {
      router.push(`/quiz/${quizId}/review`)
    }
    

    
    const exportData = async () => {
      try {
        const result = await store.dispatch('exportUserAttempts')
        if (result.success) {
          showToast('Export started! You will receive an email when ready.', 'success')
        } else {
          showToast('Export failed: ' + result.message, 'danger')
        }
      } catch (error) {
        showToast('Export failed: ' + error.message, 'danger')
      }
      updateActivity()
    }
    
    const handleLogout = async () => {
      try {
        await store.dispatch('logout')
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
        // Force logout even if API call fails
        router.push('/login')
      }
    }
    
    // API functions for fetching real data
    const fetchLeaderboard = async (period = 'week') => {
      try {
        const response = await api.get(`/leaderboard?period=${period}&limit=10`)
        leaderboard.value = response.data.leaderboard || []
        totalUsers.value = response.data.total_users || 0
        currentUserRank.value = response.data.current_user
      } catch (error) {
        console.error('Failed to fetch leaderboard:', error)
        // Keep empty arrays as fallback
      }
    }

    const fetchAchievements = async () => {
      try {
        const response = await api.get('/user/achievements')
        userAchievements.value = response.data.achievements || []
        lockedAchievements.value = response.data.locked_achievements || []
        achievementStats.value = response.data.stats || {}
      } catch (error) {
        console.error('Failed to fetch achievements:', error)
        // Keep empty arrays as fallback
      }
    }

    onMounted(async () => {
      await store.dispatch('fetchUserPerformance')
      await store.dispatch('fetchAvailableQuizzes')
      
      // Fetch leaderboard and achievements data
      await fetchLeaderboard()
      await fetchAchievements()
      
      // Initialize session timeout
      resetSessionTimeout()
      
      // Add activity listeners
      document.addEventListener('click', updateActivity)
      document.addEventListener('keypress', updateActivity)
      document.addEventListener('scroll', updateActivity)
      
      nextTick(() => {
        if (activeTab.value === 'performance') {
          createProgressChart()
          createAccuracyChart()
        }
      })
    })
    
    onUnmounted(() => {
      // Clean up session timeout
      if (sessionTimeoutId.value) {
        clearTimeout(sessionTimeoutId.value)
      }
      
      // Remove activity listeners
      document.removeEventListener('click', updateActivity)
      document.removeEventListener('keypress', updateActivity)
      document.removeEventListener('scroll', updateActivity)
    })

    watch(activeTab, (newTab) => {
      if (newTab === 'performance') {
        nextTick(() => {
          createProgressChart()
          createAccuracyChart()
        })
      }
    })
    
    return {
      breadcrumbs,
      activeTab,
      selectedSubject,
      previewedQuiz,
      progressChart,
      accuracyChart,
      searchQuery,
      showSearchSuggestions,
      todayQuizzes,
      loading,
      dashboardStats,

      totalUsers,
      communityStats,
      user,
      userPerformance,
      availableQuizzes,
      filteredQuizzes,
      uniqueSubjects,
      userAchievements,
      lockedAchievements,

      getBestScore,
      getAverageScore,
      getCurrentStreak,
      getMotivationalMessage,

      reviewQuiz,
      leaderboard,
      currentUserRank,
      achievementStats,
      fetchLeaderboard,
      fetchAchievements,
      breadcrumbs,
      searchSuggestions,
      getBestScore,
      getAverageScore,
      getCurrentStreak,
      getOverallAccuracy,
      getMotivationalMessage,
      getSuccessRate,
      getScoreBadgeClass,
      getDifficultyLevel,
      getDifficultyBadge,
      getTrophyIcon,
      getTrophyColor,
      formatDate,
      previewQuiz,
      hidePreview,
      trackQuizStart,
      startQuiz,
      getQuizStatusBadgeClass,
      getQuizStatusText,
      getQuizScheduleText,
      formatStartTime,
      formatEndTime,
      formatRemainingTime,
      filterQuizzes,
      setActiveTab,
      clearSearch,
      selectSuggestion,
      showToast,
      exportData,
      handleLogout,
      
      // Search event handlers
      handleQuizSelected: (quiz) => {
        console.log('Quiz selected:', quiz)
        previewQuiz(quiz)
      },
      handleStartQuiz: (quiz) => {
        console.log('Start quiz:', quiz)
        startQuiz(quiz)
      },
      handleSubjectSelected: (subject) => {
        console.log('Subject selected:', subject)
        // Filter quizzes by subject or navigate to subject view
        selectedSubject.value = subject.name
        filterQuizzes()
      },
      handleExploreSubject: (subject) => {
        console.log('Explore subject:', subject)
        // Navigate to subject exploration page
        router.push(`/subjects/${subject.id}`)
      }
    }
  }
}
</script>

<style scoped>
/* Enhanced Color Scheme */
:root {
  --dashboard-primary: #1E3A8A;
  --dashboard-secondary: #3B82F6;
  --dashboard-accent: #0EA5E9;
  --dashboard-success: #059669;
  --dashboard-warning: #D97706;
  --dashboard-danger: #DC2626;
  --dashboard-light: #F8FAFC;
  --dashboard-dark: #1E293B;
  --dashboard-gradient-primary: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #0EA5E9 100%);
  --dashboard-gradient-secondary: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 50%, #CBD5E1 100%);
  --dashboard-shadow-primary: 0 4px 20px rgba(30, 58, 138, 0.15);
  --dashboard-shadow-hover: 0 8px 30px rgba(30, 58, 138, 0.25);
}

/* Stat Cards */
.stat-card {
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: var(--dashboard-shadow-primary);
  position: relative;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--dashboard-gradient-primary);
}

.stat-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: var(--dashboard-shadow-hover);
}

.stat-card-primary {
  border-left: 4px solid var(--dashboard-primary);
}

.stat-card-success {
  border-left: 4px solid var(--dashboard-success);
}

.stat-card-warning {
  border-left: 4px solid var(--dashboard-warning);
}

.stat-card-danger {
  border-left: 4px solid var(--dashboard-danger);
}

.stat-card-body {
  padding: 2rem 1.5rem;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  font-family: var(--qm-font-heading);
  background: var(--dashboard-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--dashboard-dark);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  background: var(--dashboard-gradient-primary);
  box-shadow: 0 4px 16px rgba(30, 58, 138, 0.3);
  transition: all 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: rotate(5deg) scale(1.1);
}

.stat-trend {
  font-size: 0.75rem;
  font-weight: 500;
}

/* Card Enhancements */
.card {
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(30, 58, 138, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: var(--dashboard-shadow-primary);
  overflow: hidden;
  position: relative;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--dashboard-gradient-primary);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card:hover {
  transform: translateY(-6px);
  box-shadow: var(--dashboard-shadow-hover);
  border-color: rgba(30, 58, 138, 0.2);
}

.card:hover::before {
  opacity: 1;
}

.card-header {
  border-radius: 16px 16px 0 0 !important;
  padding: 1.5rem 2rem;
  background: var(--dashboard-gradient-secondary);
  border-bottom: 1px solid rgba(30, 58, 138, 0.1);
  position: relative;
}

.card-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--dashboard-gradient-primary);
  opacity: 0.3;
}

.card-body {
  padding: 2rem;
  background: rgba(255, 255, 255, 0.98);
}

.card-title {
  font-family: var(--qm-font-heading);
  font-weight: 700;
  margin-bottom: 0;
  color: var(--dashboard-primary);
  font-size: 1.25rem;
}

.dashboard-container {
  min-height: 100vh;
  background: var(--dashboard-gradient-secondary);
  position: relative;
}

.dashboard-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(30, 58, 138, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(14, 165, 233, 0.03) 0%, transparent 50%);
  pointer-events: none;
  z-index: -1;
}

.welcome-hero {
  border-radius: 0 0 24px 24px;
  margin: -1.5rem -15px 0 -15px;
  background: var(--dashboard-gradient-primary);
  position: relative;
  overflow: hidden;
}

.welcome-hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 30% 70%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 70% 30%, rgba(255, 255, 255, 0.08) 0%, transparent 50%);
  pointer-events: none;
}

.hero-illustration {
  animation: float 3s ease-in-out infinite;
  filter: drop-shadow(0 4px 16px rgba(0, 0, 0, 0.2));
}

@keyframes float {
  0%, 100% { 
    transform: translateY(0px) rotate(0deg); 
  }
  50% { 
    transform: translateY(-10px) rotate(2deg); 
  }
}

/* User Profile Section */
.user-profile-section .user-avatar {
  width: 40px;
  height: 40px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-profile-section .btn {
  transition: all 0.3s ease;
}

.user-profile-section .btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline-item {
  position: relative;
  margin-bottom: 20px;
  padding-left: 25px;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 0;
  bottom: -20px;
  width: 2px;
  background: var(--qm-light-gray);
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-marker {
  position: absolute;
  left: -15px;
  top: 5px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.timeline-marker.bg-success {
  background: var(--success);
}

.timeline-marker.bg-warning {
  background: #F59E0B;
}

.timeline-marker.bg-danger {
  background: var(--danger);
}

.quiz-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.quiz-preview {
  background: rgba(59, 130, 246, 0.05);
  padding: 10px;
  border-radius: var(--qm-border-radius);
  margin-top: 10px;
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.quiz-meta {
  font-size: 0.85rem;
}

.meta-item {
  display: block;
  margin-bottom: 4px;
}

.performance-circle {
  position: relative;
  display: inline-block;
}

.circle-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.circle-text .percentage {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--success);
}

.circle-text .label {
  font-size: 0.8rem;
  color: var(--text-subtle);
}

.subject-performance-item {
  padding: 15px;
  border: 1px solid var(--qm-light-gray);
  border-radius: var(--qm-border-radius);
}

.achievement-card.locked {
  opacity: 0.6;
  transform: none !important;
}

.achievement-card.locked:hover {
  transform: none !important;
}

.progress-to-unlock {
  margin-top: 10px;
}

.goal-progress {
  text-align: center;
}

.quick-stats .stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.chart-container {
  position: relative;
  height: 200px;
}

/* Search Suggestions */
.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-top: none;
  border-radius: 0 0 0.375rem 0.375rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f8f9fa;
  cursor: pointer;
  transition: background-color 0.2s;
}

.suggestion-item:hover {
  background-color: #f8f9fa;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-title {
  font-weight: 500;
  color: #495057;
}

.suggestion-subject {
  font-size: 0.875rem;
  color: #6c757d;
}

/* Breadcrumb Navigation */
.breadcrumb-nav {
  background: transparent;
  padding: 0;
  margin-bottom: 1.5rem;
}

.breadcrumb-nav .breadcrumb {
  background: transparent;
  padding: 0;
  margin: 0;
}

.breadcrumb-nav .breadcrumb-item {
  font-size: 0.875rem;
}

.breadcrumb-nav .breadcrumb-item + .breadcrumb-item::before {
  content: "/";
  color: #6c757d;
}

.breadcrumb-nav .breadcrumb-item.active {
  color: #495057;
  font-weight: 500;
}

/* Leaderboard Styles */
.rank-display {
  text-align: center;
}

.rank-number {
  font-size: 2rem;
  font-weight: bold;
  color: var(--primary);
  display: block;
  line-height: 1;
}

.leaderboard-item {
  padding: 1rem 0;
  border-bottom: 1px solid #f8f9fa;
}

.leaderboard-item:last-child {
  border-bottom: none;
}

.rank-badge {
  width: 50px;
  text-align: center;
}

.trophy-icon {
  font-size: 1.5rem;
}

.rank-text {
  font-weight: bold;
  color: #6c757d;
  font-size: 1.1rem;
}

.leader-name {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.leader-stats {
  font-size: 0.875rem;
}

.leader-score {
  text-align: right;
}

.score-value {
  font-size: 1.25rem;
  font-weight: bold;
  color: var(--primary);
}

/* Toast Notifications */
.alert.position-fixed {
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .welcome-hero {
    margin: -1rem -15px 0 -15px;
    padding: 2rem 0 !important;
  }
  
  .stat-card {
    margin-bottom: 1rem;
  }
  
  .timeline {
    padding-left: 20px;
  }
  
  .timeline-item {
    padding-left: 15px;
  }
  
  .rank-display {
    text-align: center;
    margin-top: 1rem;
  }
  
  .rank-number {
    font-size: 1.5rem;
  }
  
  .leader-score {
    text-align: center;
    margin-top: 0.5rem;
  }
  
  .search-suggestions {
    position: fixed;
    left: 1rem;
    right: 1rem;
    top: auto;
  }
}
</style>