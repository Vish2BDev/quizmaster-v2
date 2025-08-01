<template>
  <DashboardTemplate 
    page-title="Leaderboard"
    page-description="See how you rank against other students"
    page-icon="fas fa-trophy"
    :breadcrumbs="breadcrumbs"
  >
    <div class="row">
      <div class="col-12">
        <QmCard>
          <template #header>
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="card-title text-primary mb-0">
                <i class="fas fa-trophy me-2"></i>Top Performers
              </h5>
              <div class="filter-options">
                <select v-model="selectedPeriod" class="form-select form-select-sm" @change="fetchLeaderboard">
                  <option value="all">All Time</option>
                  <option value="month">This Month</option>
                  <option value="week">This Week</option>
                </select>
              </div>
            </div>
          </template>
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="text-muted mt-2">Loading leaderboard...</p>
            </div>
            
            <div v-else-if="leaderboard.length === 0" class="text-center py-5">
              <i class="fas fa-users text-muted" style="font-size: 4rem;"></i>
              <h4 class="text-muted mt-3">No Data Available</h4>
              <p class="text-muted">Be the first to take a quiz and appear on the leaderboard!</p>
            </div>
            
            <div v-else>
              <div class="leaderboard-list">
                <div 
                  v-for="(user, index) in leaderboard" 
                  :key="user.id"
                  class="leaderboard-item d-flex align-items-center p-3 mb-3 rounded"
                  :class="{
                    'bg-warning bg-opacity-10 border border-warning': index === 0,
                    'bg-secondary bg-opacity-10 border border-secondary': index === 1,
                    'bg-info bg-opacity-10 border border-info': index === 2,
                    'bg-light': index > 2,
                    'current-user': user.username === currentUser?.username
                  }"
                >
                  <div class="rank-badge me-3">
                    <QmBadge 
                      :variant="index === 0 ? 'warning' : index === 1 ? 'secondary' : index === 2 ? 'info' : 'primary'"
                      class="fs-6 px-3 py-2"
                    >
                      <i v-if="index === 0" class="fas fa-crown me-1"></i>
                      <i v-else-if="index === 1" class="fas fa-medal me-1"></i>
                      <i v-else-if="index === 2" class="fas fa-award me-1"></i>
                      #{{ index + 1 }}
                    </QmBadge>
                  </div>
                  
                  <div class="user-info flex-grow-1">
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <h6 class="mb-1 fw-bold">
                          {{ user.username }}
                          <QmBadge v-if="user.username === currentUser?.username" variant="success" class="ms-2">You</QmBadge>
                        </h6>
                        <small class="text-muted">
                          <i class="fas fa-chart-line me-1"></i>
                          {{ user.total_attempts }} attempts
                        </small>
                      </div>
                      <div class="text-end">
                        <div class="score-display">
                          <span class="h5 mb-0 text-primary fw-bold">{{ user.average_score }}%</span>
                          <br>
                          <small class="text-muted">Avg Score</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Current User Position (if not in top 10) -->
              <div v-if="currentUserRank && currentUserRank > 10" class="mt-4 pt-3 border-top">
                <h6 class="text-muted mb-3">Your Position</h6>
                <div class="leaderboard-item d-flex align-items-center p-3 rounded bg-primary bg-opacity-10 border border-primary current-user">
                  <div class="rank-badge me-3">
                    <QmBadge variant="primary" class="fs-6 px-3 py-2">#{{ currentUserRank }}</QmBadge>
                  </div>
                  <div class="user-info flex-grow-1">
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <h6 class="mb-1 fw-bold">
                          {{ currentUser?.username }}
                          <QmBadge variant="success" class="ms-2">You</QmBadge>
                        </h6>
                        <small class="text-muted">
                          <i class="fas fa-chart-line me-1"></i>
                          {{ currentUserStats?.total_attempts || 0 }} attempts
                        </small>
                      </div>
                      <div class="text-end">
                        <div class="score-display">
                          <span class="h5 mb-0 text-primary fw-bold">{{ currentUserStats?.average_score || 0 }}%</span>
                          <br>
                          <small class="text-muted">Avg Score</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
        </QmCard>
      </div>
    </div>
  </DashboardTemplate>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import DashboardTemplate from '@/components/templates/DashboardTemplate.vue'
import QmCard from '@/components/atoms/QmCard.vue'
import QmBadge from '@/components/atoms/QmBadge.vue'

export default {
  name: 'Leaderboard',
  components: {
    DashboardTemplate,
    QmCard,
    QmBadge
  },
  setup() {
    const store = useStore()
    const leaderboard = ref([])
    const loading = ref(false)
    const selectedPeriod = ref('all')
    const currentUserRank = ref(null)
    const currentUserStats = ref(null)
    
    const breadcrumbs = [
      { text: 'Dashboard', to: '/dashboard', icon: 'fas fa-tachometer-alt' },
      { text: 'Leaderboard', icon: 'fas fa-trophy' }
    ]
    
    const currentUser = computed(() => store.getters.currentUser)
    
    const fetchLeaderboard = async () => {
      loading.value = true
      try {
        // Mock data for now - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        leaderboard.value = [
          {
            id: 1,
            username: 'alice_student',
            average_score: 95,
            total_attempts: 25
          },
          {
            id: 2,
            username: 'bob_learner',
            average_score: 88,
            total_attempts: 20
          },
          {
            id: 3,
            username: 'charlie_quiz',
            average_score: 82,
            total_attempts: 18
          },
          {
            id: 4,
            username: currentUser.value?.username || 'vishal123',
            average_score: 75,
            total_attempts: 12
          },
          {
            id: 5,
            username: 'diana_smart',
            average_score: 70,
            total_attempts: 15
          }
        ]
        
        // Find current user rank
        const userIndex = leaderboard.value.findIndex(user => user.username === currentUser.value?.username)
        if (userIndex !== -1) {
          currentUserRank.value = userIndex + 1
          currentUserStats.value = leaderboard.value[userIndex]
        }
        
      } catch (error) {
        console.error('Error fetching leaderboard:', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      fetchLeaderboard()
    })
    
    return {
      leaderboard,
      loading,
      selectedPeriod,
      currentUserRank,
      currentUserStats,
      breadcrumbs,
      currentUser,
      fetchLeaderboard
    }
  }
}
</script>

<style scoped>
.leaderboard-item {
  transition: all 0.3s ease;
}

.leaderboard-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.current-user {
  border-width: 2px !important;
}

.rank-badge .badge {
  min-width: 50px;
}

.score-display {
  text-align: center;
}
</style>