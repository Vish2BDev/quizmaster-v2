<template>
  <DashboardTemplate
    title="Analytics Dashboard"
    subtitle="Real-time insights and performance metrics"
    :breadcrumbs="breadcrumbs"
    :show-stats="true"
    :stats="overallStatsCards"
    :stats-loading="loading"
    stats-title="System Overview"
    stats-subtitle="Key performance indicators"
    :show-search="false"
    :show-theme-toggle="true"
    :last-updated="lastUpdated"
    footer-text="Quiz Master Analytics © 2024"
  >
    <template #header-actions>
      <QmBtn
        variant="primary"
        size="sm"
        icon="fas fa-sync-alt"
        @click="refreshAnalytics"
        :loading="loading"
      >
        Refresh
      </QmBtn>
    </template>
     
    <template #content>
      <!-- Admin Search Section -->
      <QmCard title="Advanced Search" variant="outlined" class="mb-4">
        <AdminSearch
          @user-selected="handleUserSelected"
          @quiz-selected="handleQuizSelected"
          @subject-selected="handleSubjectSelected"
          @question-selected="handleQuestionSelected"
        />
      </QmCard>

      <!-- Analytics Sections -->
      <div class="row g-4">
        <!-- Overall Metrics Section -->
        <div class="col-12">
          <ChartCards
            title="Overall Metrics"
            subtitle="System-wide performance indicators"
            icon="fas fa-chart-bar"
            :charts="overallCharts"
            :loading="loading"
            :theme="theme"
            :auto-refresh="autoRefresh"
            @refresh="refreshData"
            @export="exportData"
            @time-range-change="changeTimeRange"
          />
        </div>
        
        <!-- User Analytics Section -->
        <div class="col-lg-6">
          <ChartCards
            title="User Analytics"
            subtitle="User engagement and performance insights"
            icon="fas fa-users"
            :charts="userCharts"
            :loading="loading"
            :theme="theme"
            :auto-refresh="autoRefresh"
            @refresh="refreshData"
            @export="exportData"
          />
        </div>
        
        <!-- Subject Analytics Section -->
        <div class="col-lg-6">
          <ChartCards
            title="Subject Analytics"
            subtitle="Subject-wise performance and distribution"
            icon="fas fa-book"
            :charts="subjectCharts"
            :loading="loading"
            :theme="theme"
            :auto-refresh="autoRefresh"
            @refresh="refreshData"
            @export="exportData"
          />
        </div>
            
        <!-- Quiz Analytics Section -->
        <div class="col-12">
          <ChartCards
            title="Quiz Analytics"
            subtitle="Quiz performance and engagement metrics"
            icon="fas fa-clipboard-list"
            :charts="quizCharts"
            :loading="loading"
            :theme="theme"
            :auto-refresh="autoRefresh"
            @refresh="refreshData"
            @export="exportData"
          />
        </div>
      </div>

    </template>
    
  </DashboardTemplate>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick, getCurrentInstance } from 'vue'
import { useStore } from 'vuex'
import api from '../services/api'
import DashboardTemplate from '@/components/templates/DashboardTemplate.vue'
import QmCard from '@/components/atoms/QmCard.vue'
import QmBtn from '@/components/atoms/QmBtn.vue'
import ChartCards from '@/components/ui/ChartCards.vue'
import AdminSearch from '@/components/AdminSearch.vue'
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register Chart.js components
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

export default {
  name: 'AdminDashboard',
  components: {
    DashboardTemplate,
    QmBtn,
    QmCard,
    ChartCards,
    AdminSearch
  },
  setup() {
    const store = useStore()
    const analytics = ref(null)
    const isLoading = ref(false)
    const loading = ref(false)
    const activityFilter = ref('all')
    const timeRange = ref('30d')
    const activeSection = ref('overview')
    const theme = ref('light')
    const autoRefresh = ref(true)
    
    // Chart references
    const attemptsChart = ref(null)
    const subjectDistributionChart = ref(null)
    const subjectScoresChart = ref(null)
    const quizPerformanceChart = ref(null)
    const topUsersChart = ref(null)
    
    // Chart instances
    let attemptsChartInstance = null
    let subjectDistributionChartInstance = null
    let subjectScoresChartInstance = null
    let quizPerformanceChartInstance = null
    let topUsersChartInstance = null
    
    // Computed properties
    const currentDate = computed(() => {
      return new Date().toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    })

    const filteredRecentAttempts = computed(() => {
      if (!analytics.value?.recent_events?.recent_attempts) return []
      const attempts = analytics.value.recent_events.recent_attempts
      
      return attempts.filter(attempt => {
        const percentage = getPercentage(attempt)
        const now = new Date()
        const attemptTime = new Date(attempt.completed_at)
        const hoursDiff = (now - attemptTime) / (1000 * 60 * 60)
        
        switch (activityFilter.value) {
          case 'excellent':
            return percentage >= 90
          case 'good':
            return percentage >= 70
          case 'recent':
            return hoursDiff <= 1
          default:
            return true
        }
      })
    })
    
    // ChartCards Data Structures
    const overallStatsCards = computed(() => [
      {
        icon: 'fas fa-users',
        label: 'Total Users',
        value: analytics.value?.summary?.total_users || 0,
        type: 'primary',
        change: analytics.value?.summary?.active_users_this_week ? 
          Math.round((analytics.value.summary.active_users_this_week / analytics.value.summary.total_users) * 100) : null
      },
      {
        icon: 'fas fa-clipboard-list',
        label: 'Total Quizzes',
        value: analytics.value?.summary?.total_quizzes || 0,
        type: 'success',
        change: analytics.value?.recent_events?.new_quizzes_this_week?.length || null
      },
      {
        icon: 'fas fa-book',
        label: 'Subjects',
        value: analytics.value?.summary?.total_subjects || 0,
        type: 'info'
      },
      {
        icon: 'fas fa-question-circle',
        label: 'Questions',
        value: analytics.value?.summary?.total_questions || 0,
        type: 'warning'
      },
      {
        icon: 'fas fa-play-circle',
        label: 'Quiz Attempts',
        value: analytics.value?.summary?.total_attempts || 0,
        type: 'danger',
        trend: analytics.value?.time_analytics?.daily_attempts ? {
          labels: analytics.value.time_analytics.daily_attempts.map(item => new Date(item.date).toLocaleDateString()),
          values: analytics.value.time_analytics.daily_attempts.map(item => item.attempts)
        } : null
      },
      {
        icon: 'fas fa-percentage',
        label: 'Avg Score',
        value: getOverallAverageScore(),
        type: 'primary'
      }
    ])
    
    const overallCharts = computed(() => [
      {
        title: 'Quiz Attempts Over Time',
        subtitle: 'Daily attempt trends',
        icon: 'fas fa-chart-line',
        colClass: 'col-12',
        loading: loading.value,
        timeRanges: [
          { label: 'Last 7 Days', value: '7d' },
          { label: 'Last 30 Days', value: '30d' },
          { label: 'Last 90 Days', value: '90d' }
        ],
        selectedTimeRange: timeRange.value,
        exportable: true,
        config: analytics.value?.time_analytics?.daily_attempts ? {
          type: 'line',
          data: {
            labels: analytics.value.time_analytics.daily_attempts.map(item => 
              new Date(item.date).toLocaleDateString()
            ),
            datasets: [{
              label: 'Quiz Attempts',
              data: analytics.value.time_analytics.daily_attempts.map(item => item.attempts),
              borderColor: '#3498db',
              backgroundColor: 'rgba(52, 152, 219, 0.1)',
              borderWidth: 3,
              fill: true,
              tension: 0.4
            }]
          },
          colorScheme: 'primary'
        } : null
      }
    ])
    
    const userStatsCards = computed(() => [
      {
        icon: 'fas fa-user-check',
        label: 'Active This Week',
        value: analytics.value?.summary?.active_users_this_week || 0,
        type: 'success'
      },
      {
        icon: 'fas fa-user-times',
        label: 'Inactive Users',
        value: analytics.value?.user_stats?.inactive_users || 0,
        type: 'warning'
      },
      {
        icon: 'fas fa-user-plus',
        label: 'New This Week',
        value: analytics.value?.recent_events?.new_users_this_week?.length || 0,
        type: 'info'
      }
    ])
    
    const userCharts = computed(() => [
      {
        title: 'Top Users by Attempts',
        icon: 'fas fa-trophy',
        colClass: 'col-md-6',
        loading: loading.value,
        config: analytics.value?.user_stats?.top_users_by_attempts ? {
          type: 'bar',
          data: {
            labels: analytics.value.user_stats.top_users_by_attempts.slice(0, 5).map(user => user.username),
            datasets: [{
              label: 'Attempts',
              data: analytics.value.user_stats.top_users_by_attempts.slice(0, 5).map(user => user.attempt_count)
            }]
          },
          colorScheme: 'primary'
        } : null
      },
      {
        title: 'Top Users by Score',
        icon: 'fas fa-star',
        colClass: 'col-md-6',
        loading: loading.value,
        config: analytics.value?.user_stats?.top_users_by_score ? {
          type: 'bar',
          data: {
            labels: analytics.value.user_stats.top_users_by_score.slice(0, 5).map(user => user.username),
            datasets: [{
              label: 'Average Score (%)',
              data: analytics.value.user_stats.top_users_by_score.slice(0, 5).map(user => user.average_score)
            }]
          },
          colorScheme: 'success'
        } : null
      }
    ])
    
    const subjectCharts = computed(() => [
      {
        title: 'Quiz Distribution by Subject',
        icon: 'fas fa-chart-pie',
        colClass: 'col-md-6',
        loading: loading.value,
        config: analytics.value?.subject_analytics?.quiz_distribution_by_subject ? {
          type: 'doughnut',
          data: {
            labels: analytics.value.subject_analytics.quiz_distribution_by_subject.map(item => item.subject_name),
            datasets: [{
              data: analytics.value.subject_analytics.quiz_distribution_by_subject.map(item => item.quiz_count)
            }]
          },
          colorScheme: 'gradient'
        } : null
      },
      {
        title: 'Average Score by Subject',
        icon: 'fas fa-chart-bar',
        colClass: 'col-md-6',
        loading: loading.value,
        config: analytics.value?.subject_analytics?.average_score_by_subject ? {
          type: 'bar',
          data: {
            labels: analytics.value.subject_analytics.average_score_by_subject.map(item => item.subject_name),
            datasets: [{
              label: 'Average Score (%)',
              data: analytics.value.subject_analytics.average_score_by_subject.map(item => parseFloat(item.avg_score))
            }]
          },
          colorScheme: 'success'
        } : null
      }
    ])
    
    const quizCharts = computed(() => [
      {
        title: 'Quiz Attempts vs Average Scores',
        icon: 'fas fa-chart-scatter',
        colClass: 'col-md-8',
        loading: loading.value,
        config: analytics.value?.quiz_stats?.quiz_performance ? {
          type: 'scatter',
          data: {
            datasets: [{
              label: 'Quiz Performance',
              data: analytics.value.quiz_stats.quiz_performance.map(quiz => ({
                x: quiz.attempt_count,
                y: quiz.average_score
              })),
              backgroundColor: 'rgba(52, 152, 219, 0.6)',
              borderColor: '#3498db'
            }]
          },
          colorScheme: 'primary'
        } : null
      },
      {
        title: 'Top Performing Quizzes',
        icon: 'fas fa-trophy',
        colClass: 'col-md-4',
        loading: loading.value,
        config: analytics.value?.quiz_stats?.top_quizzes_by_score ? {
          type: 'bar',
          data: {
            labels: analytics.value.quiz_stats.top_quizzes_by_score.slice(0, 5).map(quiz => quiz.title),
            datasets: [{
              label: 'Average Score (%)',
              data: analytics.value.quiz_stats.top_quizzes_by_score.slice(0, 5).map(quiz => quiz.average_score)
            }]
          },
          colorScheme: 'success'
        } : null
      }
    ])
    
    // Utility functions
    const getPercentage = (attempt) => {
      return Math.round((attempt.score / attempt.total_questions) * 100)
    }
    
    const getOverallAverageScore = () => {
      if (!analytics.value?.recent_events?.recent_attempts?.length) return 0
      const total = analytics.value.recent_events.recent_attempts.reduce((sum, attempt) => {
        return sum + getPercentage(attempt)
      }, 0)
      return Math.round(total / analytics.value.recent_events.recent_attempts.length)
    }
    
    const getTodayAttempts = () => {
      if (!analytics.value?.recent_events?.recent_attempts) return 0
      const today = new Date().toDateString()
      return analytics.value.recent_events.recent_attempts.filter(attempt => {
        return new Date(attempt.completed_at).toDateString() === today
      }).length
    }
    
    const getScoreBadgeClass = (percentage) => {
      if (percentage >= 90) return 'score-excellent'
      if (percentage >= 70) return 'score-good'
      if (percentage >= 60) return 'score-average'
      return 'score-needs-improvement'
    }

    const getScoreIcon = (attempt) => {
      const percentage = getPercentage(attempt)
      if (percentage >= 90) return 'fas fa-trophy'
      if (percentage >= 70) return 'fas fa-star'
      return 'fas fa-play-circle'
    }

    const getScoreAvatarClass = (attempt) => {
      const percentage = getPercentage(attempt)
      if (percentage >= 90) return 'avatar-excellent'
      if (percentage >= 70) return 'avatar-good'
      if (percentage >= 60) return 'avatar-average'
      return 'avatar-needs-improvement'
    }

    const getScoreDescription = (attempt) => {
      const percentage = getPercentage(attempt)
      if (percentage >= 90) return 'aced'
      if (percentage >= 70) return 'completed'
      return 'attempted'
    }

    const formatRelativeTime = (dateString) => {
      if (!dateString) return 'Unknown'
      const now = new Date()
      const date = new Date(dateString)
      const diffInMinutes = Math.floor((now - date) / 60000)
      
      if (diffInMinutes < 1) return 'Just now'
      if (diffInMinutes < 60) return `${diffInMinutes}m ago`
      if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
      return `${Math.floor(diffInMinutes / 1440)}d ago`
    }

    // Chart initialization methods
    const initializeAttemptsChart = () => {
      if (!analytics.value?.time_analytics?.daily_attempts) return
      
      const ctx = document.getElementById('attemptsChart')
      if (!ctx) return
      
      if (attemptsChartInstance) {
        attemptsChartInstance.destroy()
      }
      
      const data = analytics.value.time_analytics.daily_attempts
      const labels = data.map(item => new Date(item.date).toLocaleDateString())
      const values = data.map(item => item.attempts)
      
      attemptsChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Quiz Attempts',
            data: values,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
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
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            x: {
              grid: {
                display: false
              }
            }
          }
        }
      })
    }

    const initializeTopUsersChart = () => {
      if (!analytics.value?.user_analytics?.top_users_by_attempts) return
      
      const ctx = document.getElementById('topUsersChart')
      if (!ctx) return
      
      if (topUsersChartInstance) {
        topUsersChartInstance.destroy()
      }
      
      const data = analytics.value.user_analytics.top_users_by_attempts
      const labels = data.map(user => user.username)
      const values = data.map(user => user.attempt_count)
      
      topUsersChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Attempts',
            data: values,
            backgroundColor: [
              '#3b82f6',
              '#10b981',
              '#f59e0b',
              '#ef4444',
              '#8b5cf6'
            ],
            borderRadius: 4
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
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            x: {
              grid: {
                display: false
              }
            }
          }
        }
      })
    }

    const initializeSubjectDistributionChart = () => {
      if (!analytics.value?.subject_analytics?.quiz_distribution_by_subject) return
      
      const ctx = document.getElementById('subjectDistributionChart')
      if (!ctx) return
      
      if (subjectDistributionChartInstance) {
        subjectDistributionChartInstance.destroy()
      }
      
      const data = analytics.value.subject_analytics.quiz_distribution_by_subject
      const labels = data.map(item => item.subject_name)
      const values = data.map(item => item.quiz_count)
      
      subjectDistributionChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: values,
            backgroundColor: [
              '#3b82f6',
              '#10b981',
              '#f59e0b',
              '#ef4444',
              '#8b5cf6',
              '#06b6d4',
              '#84cc16'
            ],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 20,
                usePointStyle: true
              }
            }
          }
        }
      })
    }

    const initializeSubjectScoresChart = () => {
      if (!analytics.value?.subject_analytics?.average_score_by_subject) return
      
      const ctx = document.getElementById('subjectScoresChart')
      if (!ctx) return
      
      if (subjectScoresChartInstance) {
        subjectScoresChartInstance.destroy()
      }
      
      const data = analytics.value.subject_analytics.average_score_by_subject
      const labels = data.map(item => item.subject_name)
      const values = data.map(item => parseFloat(item.avg_score))
      
      subjectScoresChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Average Score (%)',
            data: values,
            backgroundColor: '#10b981',
            borderRadius: 4
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
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              },
              ticks: {
                callback: function(value) {
                  return value + '%'
                }
              }
            },
            x: {
              grid: {
                display: false
              }
            }
          }
        }
      })
    }

    const initializeQuizPerformanceChart = () => {
      if (!analytics.value?.quiz_analytics?.quiz_attempts_vs_scores) return
      
      const ctx = document.getElementById('quizPerformanceChart')
      if (!ctx) return
      
      if (quizPerformanceChartInstance) {
        quizPerformanceChartInstance.destroy()
      }
      
      const data = analytics.value.quiz_analytics.quiz_attempts_vs_scores
      
      quizPerformanceChartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'Quiz Performance',
            data: data.map(quiz => ({
              x: quiz.attempt_count,
              y: parseFloat(quiz.avg_score)
            })),
            backgroundColor: '#3b82f6',
            borderColor: '#3b82f6',
            pointRadius: 6,
            pointHoverRadius: 8
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
                  const quiz = data[context.dataIndex]
                  return `${quiz.title}: ${context.parsed.x} attempts, ${context.parsed.y.toFixed(1)}% avg score`
                }
              }
            }
          },
          scales: {
            x: {
              title: {
                display: true,
                text: 'Number of Attempts'
              },
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Average Score (%)'
              },
              beginAtZero: true,
              max: 100,
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            }
          }
        }
      })
    }

    const initializeAllCharts = () => {
      nextTick(() => {
        initializeAttemptsChart()
        initializeTopUsersChart()
        initializeSubjectDistributionChart()
        initializeSubjectScoresChart()
        initializeQuizPerformanceChart()
      })
    }
    
    // Action methods

    const refreshData = async () => {
      await fetchAnalytics()
    }

    const exportData = () => {
      if (!analytics.value) {
        alert('No data to export')
        return
      }
      
      const dataStr = JSON.stringify(analytics.value, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `analytics-${new Date().toISOString().split('T')[0]}.json`
      link.click()
      URL.revokeObjectURL(url)
    }

    const exportAllData = async () => {
      try {
        loading.value = true
        
        const response = await fetch('http://localhost:5000/admin/export/all-attempts', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        if (!response.ok) {
          throw new Error('Failed to export data')
        }
        
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `all-quiz-data-${new Date().toISOString().split('T')[0]}.csv`
        link.click()
        URL.revokeObjectURL(url)
        
        loading.value = false
        alert('Data exported successfully!')
      } catch (error) {
        loading.value = false
        console.error('Export error:', error)
        alert('Failed to export data. Please try again.')
      }
    }

    const exportAnalytics = () => {
      if (!analytics.value) {
        alert('No analytics data to export')
        return
      }
      
      // Create a comprehensive analytics export
      const analyticsData = {
        exportDate: new Date().toISOString(),
        timeRange: timeRange.value,
        summary: {
          totalUsers: analytics.value.totalUsers,
          totalQuizzes: analytics.value.totalQuizzes,
          totalAttempts: analytics.value.totalAttempts,
          averageScore: analytics.value.averageScore
        },
        recentAttempts: analytics.value.recentAttempts,
        subjectDistribution: analytics.value.subjectDistribution,
        topUsers: analytics.value.topUsers
      }
      
      const dataStr = JSON.stringify(analyticsData, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `analytics-report-${new Date().toISOString().split('T')[0]}.json`
      link.click()
      URL.revokeObjectURL(url)
      
      alert('Analytics exported successfully!')
    }

    const testDailyReminder = async () => {
      try {
        // Add task to history and show toast
        const taskId = Date.now()
        const adminLayout = getCurrentInstance()?.parent?.parent
        if (adminLayout?.setupState?.addTask) {
          adminLayout.setupState.addTask('Daily Reminder Test', 'running')
        }
        
        loading.value = true
        
        // Show initial toast
        if (adminLayout?.setupState?.showToast) {
          adminLayout.setupState.showToast('Task Started', 'Daily reminder test initiated', 'info')
        }
        
        const response = await fetch('http://localhost:5000/admin/test-daily-reminder', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        })
        
        const result = await response.json()
        loading.value = false
        
        if (response.ok) {
          // Update task status to success
          if (adminLayout?.setupState?.updateTaskStatus) {
            adminLayout.setupState.updateTaskStatus(taskId, 'success')
          }
          
          const successMessage = `Daily reminder test completed! Found ${result.inactive_users_count || 0} inactive users. Latest quiz: ${result.latest_quiz || 'None'}`
          
          // Show success toast
          if (adminLayout?.setupState?.showToast) {
            adminLayout.setupState.showToast('Success', successMessage, 'success')
          } else {
            alert(successMessage)
          }
        } else {
          // Update task status to error
          if (adminLayout?.setupState?.updateTaskStatus) {
            adminLayout.setupState.updateTaskStatus(taskId, 'error')
          }
          
          const errorMessage = result.error || 'Unknown error occurred'
          
          // Show error toast
          if (adminLayout?.setupState?.showToast) {
            adminLayout.setupState.showToast('Error', `Daily reminder failed: ${errorMessage}`, 'danger')
          } else {
            alert(`Error: ${errorMessage}`)
          }
        }
      } catch (error) {
        loading.value = false
        console.error('Daily reminder test error:', error)
        
        // Update task status to error
        const adminLayout = getCurrentInstance()?.parent?.parent
        if (adminLayout?.setupState?.updateTaskStatus) {
          adminLayout.setupState.updateTaskStatus(Date.now(), 'error')
        }
        
        const errorMessage = 'Failed to test daily reminder. Please check your connection and try again.'
        
        // Show error toast
        if (adminLayout?.setupState?.showToast) {
          adminLayout.setupState.showToast('Error', errorMessage, 'danger')
        } else {
          alert(errorMessage)
        }
      }
    }

    const testMonthlyReport = async () => {
      try {
        // Add task to history and show toast
        const taskId = Date.now()
        const adminLayout = getCurrentInstance()?.parent?.parent
        if (adminLayout?.setupState?.addTask) {
          adminLayout.setupState.addTask('Monthly Report Generation', 'running')
        }
        
        loading.value = true
        
        // Show initial toast
        if (adminLayout?.setupState?.showToast) {
          adminLayout.setupState.showToast('Task Started', 'Monthly report generation initiated', 'info')
        }
        
        const response = await fetch('http://localhost:5000/admin/test-monthly-report', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        })
        
        const result = await response.json()
        loading.value = false
        
        if (response.ok) {
          // Update task status to success
          if (adminLayout?.setupState?.updateTaskStatus) {
            adminLayout.setupState.updateTaskStatus(taskId, 'success')
          }
          
          let subjectInfo = ''
          if (result.subject_stats) {
            subjectInfo = Object.entries(result.subject_stats)
              .map(([subject, stats]) => `${subject}: ${stats.attempts} attempts`)
              .join('\n')
          }
          
          const successMessage = `Monthly report generated successfully! Period: ${result.report_period || 'Last Month'}, Total Attempts: ${result.total_attempts || 0}, Active Users: ${result.total_users || 0}, Average Score: ${Math.round(result.avg_percentage || 0)}%`
          
          // Show success toast
          if (adminLayout?.setupState?.showToast) {
            adminLayout.setupState.showToast('Success', successMessage, 'success')
          } else {
            alert(successMessage)
          }
        } else {
          // Update task status to error
          if (adminLayout?.setupState?.updateTaskStatus) {
            adminLayout.setupState.updateTaskStatus(taskId, 'error')
          }
          
          const errorMessage = result.error || result.message || 'Unknown error occurred'
          
          // Show error toast
          if (adminLayout?.setupState?.showToast) {
            adminLayout.setupState.showToast('Error', `Monthly report failed: ${errorMessage}`, 'danger')
          } else {
            alert(`Error: ${errorMessage}`)
          }
        }
      } catch (error) {
        loading.value = false
        console.error('Monthly report test error:', error)
        
        // Update task status to error
        const adminLayout = getCurrentInstance()?.parent?.parent
        if (adminLayout?.setupState?.updateTaskStatus) {
          adminLayout.setupState.updateTaskStatus(Date.now(), 'error')
        }
        
        const errorMessage = 'Failed to generate monthly report. Please check your connection and try again.'
        
        // Show error toast
        if (adminLayout?.setupState?.showToast) {
          adminLayout.setupState.showToast('Error', errorMessage, 'danger')
        } else {
          alert(errorMessage)
        }
      }
    }

    const changeTimeRange = (range) => {
      timeRange.value = range
      // In a real implementation, this would refetch data with the new time range
      fetchAnalytics()
    }

    const navigateToSection = (section) => {
      activeSection.value = section
      // Scroll to section or update view
      const element = document.getElementById(section)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' })
      }
    }

    const fetchAnalytics = async () => {
      try {
        loading.value = true
        
        const response = await api.get('/admin/analytics/overview')
        analytics.value = response.data
        
        // Initialize charts after data is loaded
        initializeAllCharts()
        
      } catch (error) {
        console.error('Error fetching analytics:', error)
        alert('Failed to load analytics data. Please try again.')
      } finally {
        loading.value = false
      }
    }

    // Lifecycle hooks
    // Breadcrumbs for navigation
    const breadcrumbs = ref([
      {
        text: 'Analytics',
        icon: 'fas fa-chart-line'
      }
    ])
    
    // Refresh analytics method
    const refreshAnalytics = async () => {
      await fetchAnalytics()
    }

    onMounted(() => {
      fetchAnalytics()
    })

    onUnmounted(() => {
      // Clean up chart instances
      if (attemptsChartInstance) attemptsChartInstance.destroy()
      if (topUsersChartInstance) topUsersChartInstance.destroy()
      if (subjectDistributionChartInstance) subjectDistributionChartInstance.destroy()
      if (subjectScoresChartInstance) subjectScoresChartInstance.destroy()
      if (quizPerformanceChartInstance) quizPerformanceChartInstance.destroy()
    })

    return {
      // Data
      analytics,
      isLoading,
      activityFilter,
      timeRange,
      activeSection,
      breadcrumbs,
      loading,
      theme,
      autoRefresh,
      
      // Computed
      currentDate,
      filteredRecentAttempts,
      overallStatsCards,
      overallCharts,
      userStatsCards,
      userCharts,
      subjectCharts,
      quizCharts,
      
      // Methods
      getPercentage,
      getOverallAverageScore,
      getTodayAttempts,
      getScoreBadgeClass,
      getScoreIcon,
      refreshAnalytics,
      getScoreAvatarClass,
      getScoreDescription,
      formatRelativeTime,
      refreshData,
      exportData,
      exportAllData,
      exportAnalytics,
      testDailyReminder,
      testMonthlyReport,
      changeTimeRange,
      navigateToSection,
      
      // Search event handlers
      handleUserSelected: (user) => {
        console.log('User selected:', user)
        // Navigate to user details or show user modal
      },
      handleQuizSelected: (quiz) => {
        console.log('Quiz selected:', quiz)
        // Navigate to quiz details or show quiz modal
      },
      handleSubjectSelected: (subject) => {
        console.log('Subject selected:', subject)
        // Navigate to subject details or show subject modal
      },
      handleQuestionSelected: (question) => {
        console.log('Question selected:', question)
        // Navigate to question details or show question modal
      },
      
      // Chart references
      attemptsChart,
      subjectDistributionChart,
      subjectScoresChart,
      quizPerformanceChart,
      topUsersChart,
      
      // Chart methods
      initializeAllCharts
    }
  }
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: var(--bg-soft);
}

/* Sidebar Styles */
.admin-sidebar {
  background: linear-gradient(180deg, var(--primary) 0%, #1E40AF 100%);
  min-height: 100vh;
  box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

.sidebar-content {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.admin-header {
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.brand-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
}

.admin-nav-link {
  color: rgba(255,255,255,0.8);
  border-radius: var(--qm-border-radius);
  padding: 12px 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  border: none;
  background: none;
  text-decoration: none;
  display: flex;
  align-items: center;
}

.admin-nav-link:hover {
  color: white;
  background: rgba(255,255,255,0.1);
  transform: translateX(5px);
}

.admin-nav-link.active {
  color: white;
  background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.nav-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.admin-nav-link.active .nav-indicator {
  transform: scaleY(1);
}

.nav-section-title {
  padding: 0 16px;
}

/* System Status */
.system-status {
  margin-top: auto;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.status-indicators {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Main Content */
.admin-main {
  background: var(--bg-soft);
}

.content-header {
  border-bottom: 1px solid #dee2e6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* KPI Cards */
.kpi-section {
  background: white;
  border-bottom: 1px solid #dee2e6;
}

.kpi-card {
  background: white;
  border-radius: var(--qm-border-radius-lg);
  padding: 0;
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-5px);
}

.kpi-card.gradient-primary {
  background: linear-gradient(135deg, var(--primary) 0%, #1E40AF 100%);
  color: white;
}

.kpi-card.gradient-success {
  background: linear-gradient(135deg, var(--success) 0%, #16A34A 100%);
  color: white;
}

.kpi-card.gradient-info {
  background: linear-gradient(135deg, var(--secondary) 0%, #0284C7 100%);
  color: white;
}

.kpi-card.gradient-warning {
  background: linear-gradient(135deg, #F59E0B 0%, #EAB308 100%);
  color: white;
}

.kpi-content {
  padding: 2rem;
  display: flex;
  align-items: center;
}

.kpi-icon {
  font-size: 3rem;
  margin-right: 1.5rem;
  opacity: 0.8;
}

.kpi-number {
  font-size: 2.5rem;
  font-weight: 700;
  font-family: var(--qm-font-ui);
  line-height: 1;
}

.kpi-label {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0.5rem 0;
}

.kpi-change {
  font-size: 0.85rem;
  font-weight: 600;
}

.kpi-change.positive {
  opacity: 0.9;
}

.kpi-change.neutral {
  opacity: 0.7;
}

/* Activity Feed */
.activity-feed {
  max-height: 500px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: start;
  padding: 1rem;
  border-bottom: 1px solid #f8f9fa;
  transition: all 0.3s ease;
  position: relative;
}

.activity-item:hover {
  background: rgba(52, 152, 219, 0.05);
}

.activity-item.highlight {
  background: linear-gradient(90deg, rgba(46, 204, 113, 0.1) 0%, transparent 100%);
  border-left: 3px solid #2ecc71;
}

.activity-avatar {
  margin-right: 1rem;
  flex-shrink: 0;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.avatar-success {
  background: linear-gradient(135deg, var(--success), #16A34A);
}

.avatar-warning {
  background: linear-gradient(135deg, #F59E0B, #EAB308);
}

.avatar-info {
  background: linear-gradient(135deg, var(--primary), #1E40AF);
}

.activity-content {
  flex: 1;
}

.activity-header {
  margin-bottom: 0.25rem;
}

.activity-action {
  color: var(--qm-medium-gray);
  margin-left: 0.5rem;
}

.activity-details {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.25rem;
}

.quiz-name {
  font-style: italic;
  color: var(--qm-electric-blue);
}

.activity-score {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.activity-score.score-excellent {
  background: rgba(34, 197, 94, 0.2);
  color: var(--success);
}

.activity-score.score-good {
  background: rgba(59, 130, 246, 0.2);
  color: var(--primary);
}

.activity-score.score-needs-improvement {
  background: rgba(239, 68, 68, 0.2);
  color: var(--danger);
}

.activity-time {
  font-size: 0.8rem;
  color: var(--qm-medium-gray);
}

.activity-actions {
  margin-left: 1rem;
}

/* Insights */
.insights-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.insight-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.insight-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.insight-title {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--qm-dark-gray);
}

.insight-description {
  font-size: 0.8rem;
  color: var(--qm-medium-gray);
}

/* Community Stats */
.community-stats .stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
  padding: 0.75rem 1rem;
  background: rgba(52, 152, 219, 0.05);
  border-radius: 8px;
  border-left: 3px solid transparent;
  transition: all 0.3s ease;
}

.community-stats .stat-row:hover {
  background: rgba(52, 152, 219, 0.1);
  border-left-color: var(--qm-electric-blue);
  transform: translateX(2px);
}

.community-stats .stat-row:nth-child(1) {
  border-left-color: #2ecc71;
}

.community-stats .stat-row:nth-child(2) {
  border-left-color: #3498db;
}

.community-stats .stat-row:nth-child(3) {
  border-left-color: #9b59b6;
}

.community-stats .stat-row:nth-child(4) {
  border-left-color: #f39c12;
}

.community-stats .stat-row span {
  color: var(--qm-dark-gray);
  font-weight: 500;
  display: flex;
  align-items: center;
}

.community-stats .stat-row span::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  background: currentColor;
  opacity: 0.6;
}

.community-stats .stat-row strong {
  font-weight: 600;
  font-size: 1.1rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Empty State */
.empty-state {
  padding: 3rem 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-sidebar {
    min-height: auto;
    position: relative;
  }
  
  .sidebar-content {
    position: relative;
    height: auto;
  }
  
  .kpi-content {
    padding: 1.5rem;
    flex-direction: column;
    text-align: center;
  }
  
  .kpi-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  .activity-item {
    flex-direction: column;
    gap: 1rem;
  }
  
  .activity-details {
    flex-direction: column;
    align-items: start;
    gap: 0.5rem;
  }
}

/* Analytics Dashboard Specific Styles */
.analytics-section {
  background: white;
  border-radius: var(--qm-border-radius-lg);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.section-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-content {
  padding: 2rem;
}

/* Chart Containers */
.chart-container {
  position: relative;
  height: 300px;
  margin: 1rem 0;
}

.chart-container.large {
  height: 400px;
}

.chart-container canvas {
  max-height: 100%;
}

/* Time Range Controls */
.time-range-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.time-range-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: var(--qm-border-radius);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
}

.time-range-btn:hover {
  background: #f8f9fa;
  border-color: #3b82f6;
}

.time-range-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* Filter Controls */
.filter-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: var(--qm-border-radius);
  background: white;
  font-size: 0.875rem;
}

/* Metric Cards */
.metric-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  border-radius: var(--qm-border-radius-lg);
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-left: 4px solid #3b82f6;
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-card.success {
  border-left-color: #10b981;
}

.metric-card.warning {
  border-left-color: #f59e0b;
}

.metric-card.danger {
  border-left-color: #ef4444;
}

.metric-card.info {
  border-left-color: #06b6d4;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.metric-label {
  color: #6b7280;
  font-size: 0.875rem;
  font-weight: 500;
}

/* User List */
.user-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.user-item {
  display: flex;
  align-items: center;
  justify-content: between;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: var(--qm-border-radius);
  transition: all 0.3s ease;
}

.user-item:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.user-stats {
  font-size: 0.875rem;
  color: #6b7280;
}

.user-score {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

/* Score Badge Styles */
.score-excellent {
  background: rgba(16, 185, 129, 0.2);
  color: #059669;
}

.score-good {
  background: rgba(59, 130, 246, 0.2);
  color: #2563eb;
}

.score-average {
  background: rgba(245, 158, 11, 0.2);
  color: #d97706;
}

.score-needs-improvement {
  background: rgba(239, 68, 68, 0.2);
  color: #dc2626;
}

/* Avatar Styles */
.avatar-excellent {
  background: linear-gradient(135deg, #10b981, #059669);
}

.avatar-good {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.avatar-average {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.avatar-needs-improvement {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

/* Loading States */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background: white;
  padding: 2rem;
  border-radius: var(--qm-border-radius-lg);
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Recent Events */
.recent-events {
  max-height: 400px;
  overflow-y: auto;
}

.event-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
  transition: all 0.3s ease;
}

.event-item:hover {
  background: #f8f9fa;
}

.event-item:last-child {
  border-bottom: none;
}

.event-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
  margin-right: 1rem;
  flex-shrink: 0;
}

.event-content {
  flex: 1;
}

.event-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.event-details {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.event-time {
  font-size: 0.75rem;
  color: #9ca3af;
}

/* Responsive Design */
@media (max-width: 768px) {
  .metric-cards {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 250px;
  }
  
  .chart-container.large {
    height: 300px;
  }
  
  .filter-controls {
    flex-direction: column;
  }
  
  .time-range-controls {
    flex-wrap: wrap;
  }
  
  .section-content {
    padding: 1rem;
  }
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
  .admin-main {
    background: #1a1a1a;
  }
  
  .content-header {
    background: #2d2d2d;
    color: white;
  }
  
  .kpi-section {
    background: #2d2d2d;
  }
  
  .analytics-section {
    background: #2d2d2d;
    color: white;
  }
  
  .metric-card {
    background: #374151;
    color: white;
  }
  
  .metric-value {
    color: white;
  }
  
  .user-item {
    background: #374151;
  }
  
  .user-item:hover {
    background: #4b5563;
  }
  
  .event-item:hover {
    background: #374151;
  }
  
  .loading-content {
    background: #2d2d2d;
    color: white;
  }
  
  .community-stats .stat-row {
    background: rgba(255, 255, 255, 0.05) !important;
  }
  
  .community-stats .stat-row:hover {
    background: rgba(255, 255, 255, 0.1) !important;
  }
  
  .community-stats .stat-row span {
    color: #ffffff !important;
    opacity: 0.9;
  }
  
  .community-stats .stat-row strong {
    color: #2c3e50 !important;
    background: rgba(255, 255, 255, 0.9) !important;
    font-weight: 700;
  }
}
</style>