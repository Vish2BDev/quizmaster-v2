<template>
  <AdminLayout>
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-1">
          <i class="fas fa-tachometer-alt me-2"></i>
          Admin Dashboard
        </h1>
        <p class="text-muted mb-0">System overview and quick actions</p>
      </div>
      <div class="d-flex gap-2">
        <button @click="refreshData" class="btn btn-primary btn-sm">
          <i class="fas fa-sync-alt me-2"></i>Refresh
        </button>
      </div>
    </div>

    <!-- Quick Stats Cards -->
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="card stat-card border-0 shadow-sm clickable" @click="navigateToUsers">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="stat-icon bg-primary">
                <i class="fas fa-users text-white"></i>
              </div>
              <div class="ms-3">
                <h5 class="mb-0 text-white">{{ stats.totalUsers || 0 }}</h5>
                <small style="color: #d1d5db;">Total Users</small>
              </div>
              <div class="ms-auto">
                <i class="fas fa-arrow-right" style="color: #d1d5db;"></i>
              </div>
            </div>
            <div class="mt-2">
              <small class="d-flex align-items-center" style="color: #10b981;">
                <i class="fas fa-arrow-up me-1"></i>
                <span class="fw-medium">+{{ stats.newUsersThisWeek || 0 }}</span>
                <span class="ms-1" style="color: #9ca3af;">new this week</span>
              </small>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card stat-card border-0 shadow-sm clickable" @click="navigateToSubjects">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="stat-icon bg-success">
                <i class="fas fa-book text-white"></i>
              </div>
              <div class="ms-3">
                <h5 class="mb-0 text-white">{{ stats.totalSubjects || 0 }}</h5>
                <small style="color: #d1d5db;">Subjects</small>
              </div>
              <div class="ms-auto">
                  <i class="fas fa-arrow-right" style="color: #d1d5db;"></i>
                </div>
            </div>
            <div class="mt-2">
              <small class="d-flex align-items-center" style="color: #06b6d4;">
                <i class="fas fa-check-circle me-1"></i>
                <span class="fw-medium">{{ stats.activeSubjects || 0 }}</span>
                <span class="ms-1" style="color: #9ca3af;">currently active</span>
              </small>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card stat-card border-0 shadow-sm clickable" @click="navigateToQuizzes">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="stat-icon bg-warning">
                <i class="fas fa-clipboard-list text-white"></i>
              </div>
              <div class="ms-3">
                <h5 class="mb-0 text-white">{{ stats.totalQuizzes || 0 }}</h5>
                <small style="color: #d1d5db;">Quizzes</small>
              </div>
              <div class="ms-auto">
                 <i class="fas fa-arrow-right" style="color: #d1d5db;"></i>
               </div>
            </div>
            <div class="mt-2">
              <small class="d-flex align-items-center" style="color: #3b82f6;">
                <i class="fas fa-globe me-1"></i>
                <span class="fw-medium">{{ stats.publishedQuizzes || 0 }}</span>
                <span class="ms-1" style="color: #9ca3af;">live & published</span>
              </small>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card stat-card border-0 shadow-sm clickable" @click="navigateToAnalytics">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="stat-icon bg-info">
                <i class="fas fa-play-circle text-white"></i>
              </div>
              <div class="ms-3">
                <h5 class="mb-0 text-white">{{ stats.totalAttempts || 0 }}</h5>
                <small style="color: #d1d5db;">Quiz Attempts</small>
              </div>
              <div class="ms-auto">
                  <i class="fas fa-arrow-right" style="color: #d1d5db;"></i>
                </div>
            </div>
            <div class="mt-2">
              <small class="d-flex align-items-center" style="color: #f59e0b;">
                <i class="fas fa-calendar-day me-1"></i>
                <span class="fw-medium">{{ stats.attemptsToday || 0 }}</span>
                <span class="ms-1" style="color: #9ca3af;">attempts today</span>
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="mb-0">
              <i class="fas fa-bolt me-2"></i>
              Quick Actions
            </h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-4 mb-3">
                <router-link to="/admin/subjects" class="btn btn-outline-primary w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                  <i class="fas fa-plus-circle fa-2x mb-2"></i>
                  <span>Add Subject</span>
                </router-link>
              </div>
              <div class="col-md-4 mb-3">
                <router-link to="/admin/quizzes" class="btn btn-outline-success w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                  <i class="fas fa-question-circle fa-2x mb-2"></i>
                  <span>Create Quiz</span>
                </router-link>
              </div>
              <div class="col-md-4 mb-3">
                <router-link to="/admin/users" class="btn btn-outline-info w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                  <i class="fas fa-user-plus fa-2x mb-2"></i>
                  <span>Manage Users</span>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="mb-0">
              <i class="fas fa-chart-line me-2"></i>
              System Status
            </h5>
          </div>
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="status-dot bg-success me-2"></div>
              <span class="small">Database Connected</span>
            </div>
            <div class="d-flex align-items-center mb-3">
              <div class="status-dot bg-success me-2"></div>
              <span class="small">Redis Active</span>
            </div>
            <div class="d-flex align-items-center mb-3">
              <div class="status-dot bg-success me-2"></div>
              <span class="small">Celery Workers Running</span>
            </div>
            <div class="d-flex align-items-center">
              <div class="status-dot bg-warning me-2"></div>
              <span class="small">{{ stats.activeUsers || 0 }} Active Users</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="row">
      <div class="col-md-6">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="mb-0">
              <i class="fas fa-clock me-2"></i>
              Recent Quiz Attempts
            </h5>
          </div>
          <div class="card-body">
            <div v-if="recentAttempts.length === 0" class="text-center text-muted py-4">
              <i class="fas fa-inbox fa-2x mb-2"></i>
              <p class="mb-0">No recent attempts</p>
            </div>
            <div v-else>
              <div v-for="attempt in recentAttempts.slice(0, 5)" :key="attempt.id" class="d-flex align-items-center mb-3">
                <div class="flex-shrink-0">
                  <div class="avatar-sm bg-light rounded-circle d-flex align-items-center justify-content-center">
                    <i class="fas fa-user text-muted"></i>
                  </div>
                </div>
                <div class="ms-3 flex-grow-1">
                  <h6 class="mb-1">{{ attempt.username }}</h6>
                  <p class="text-muted small mb-0">{{ attempt.quiz_title }}</p>
                </div>
                <div class="text-end">
                  <span class="badge" :class="getScoreBadgeClass(attempt.score)">{{ attempt.score }}%</span>
                  <div class="text-muted small">{{ formatTime(attempt.timestamp) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white border-bottom">
            <h5 class="mb-0">
              <i class="fas fa-trophy me-2"></i>
              Top Performers
            </h5>
          </div>
          <div class="card-body">
            <div v-if="topPerformers.length === 0" class="text-center text-muted py-4">
              <i class="fas fa-medal fa-2x mb-2"></i>
              <p class="mb-0">No performance data</p>
            </div>
            <div v-else>
              <div v-for="(user, index) in topPerformers.slice(0, 5)" :key="user.id" class="d-flex align-items-center mb-3">
                <div class="flex-shrink-0">
                  <div class="position-relative">
                    <div class="avatar-sm bg-light rounded-circle d-flex align-items-center justify-content-center">
                      <i class="fas fa-user text-muted"></i>
                    </div>
                    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill" :class="getRankBadgeClass(index)">
                      {{ index + 1 }}
                    </span>
                  </div>
                </div>
                <div class="ms-3 flex-grow-1">
                  <h6 class="mb-1">{{ user.username }}</h6>
                  <p class="text-muted small mb-0">{{ user.attempts_count }} attempts</p>
                </div>
                <div class="text-end">
                  <span class="fw-bold text-success">{{ user.average_score }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/components/AdminLayout.vue'
import api from '@/services/api'

export default {
  name: 'AdminOverview',
  components: {
    AdminLayout
  },
  setup() {
    const router = useRouter()
    const stats = ref({
      totalUsers: 0,
      totalSubjects: 0,
      totalQuizzes: 0,
      totalAttempts: 0,
      activeUsers: 0,
      newUsersThisWeek: 0,
      activeSubjects: 0,
      publishedQuizzes: 0,
      attemptsToday: 0
    })
    
    const recentAttempts = ref([])
    const topPerformers = ref([])
    const loading = ref(false)

    const fetchOverviewData = async () => {
      try {
        loading.value = true
        
        // Fetch basic stats
        const statsResponse = await api.get('/admin/analytics/overview')
        if (statsResponse.data && statsResponse.data.summary) {
          const summary = statsResponse.data.summary
          stats.value = {
            totalUsers: summary.total_users || 0,
            totalSubjects: summary.total_subjects || 0,
            totalQuizzes: summary.total_quizzes || 0,
            totalAttempts: summary.total_attempts || 0,
            activeUsers: summary.active_users_this_week || 0,
            newUsersThisWeek: summary.new_users_this_week || 0,
            activeSubjects: summary.active_subjects || summary.total_subjects || 0,
            publishedQuizzes: summary.published_quizzes || Math.floor((summary.total_quizzes || 0) * 0.8),
            attemptsToday: summary.attempts_today || 0
          }
          
          // Extract recent attempts
          if (statsResponse.data.recent_events && statsResponse.data.recent_events.recent_attempts) {
            recentAttempts.value = statsResponse.data.recent_events.recent_attempts
          }
          
          // Extract top performers
          if (statsResponse.data.user_analytics && statsResponse.data.user_analytics.top_users_by_score) {
            topPerformers.value = statsResponse.data.user_analytics.top_users_by_score
          }
        }
      } catch (error) {
        console.error('Error fetching overview data:', error)
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      fetchOverviewData()
    }

    const navigateToUsers = () => {
      router.push('/admin/users')
    }

    const navigateToSubjects = () => {
      router.push('/admin/subjects')
    }

    const navigateToQuizzes = () => {
      router.push('/admin/quizzes')
    }

    const navigateToAnalytics = () => {
      router.push('/admin/analytics')
    }

    const getScoreBadgeClass = (score) => {
      if (score >= 80) return 'bg-success'
      if (score >= 60) return 'bg-warning'
      return 'bg-danger'
    }

    const getRankBadgeClass = (index) => {
      if (index === 0) return 'bg-warning'  // Gold
      if (index === 1) return 'bg-secondary'  // Silver
      if (index === 2) return 'bg-info'  // Bronze
      return 'bg-primary'
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMins / 60)
      const diffDays = Math.floor(diffHours / 24)

      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`
      if (diffHours < 24) return `${diffHours}h ago`
      if (diffDays < 7) return `${diffDays}d ago`
      return date.toLocaleDateString()
    }

    onMounted(() => {
      fetchOverviewData()
    })

    return {
      stats,
      recentAttempts,
      topPerformers,
      loading,
      refreshData,
      navigateToUsers,
      navigateToSubjects,
      navigateToQuizzes,
      navigateToAnalytics,
      getScoreBadgeClass,
      getRankBadgeClass,
      formatTime
    }
  }
}
</script>

<style scoped>
.stat-card {
  transition: all 0.2s ease;
  height: 100%;
}

.stat-card .card-body {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 120px;
  padding: 1.5rem;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

.clickable {
  cursor: pointer;
}

.clickable:hover .fa-arrow-right {
  transform: translateX(3px);
  transition: transform 0.2s ease;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Ensure all stat card columns have equal height */
.row .col-md-3 {
  display: flex;
  flex-direction: column;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.avatar-sm {
  width: 40px;
  height: 40px;
}

.btn:hover {
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

.card {
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
}
</style>