<template>
  <DashboardTemplate 
    page-title="Achievements"
    page-description="Track your progress and unlock new badges"
    page-icon="fas fa-medal"
    :breadcrumbs="breadcrumbs"
  >
    <div class="row">
      <!-- Achievement Progress Overview -->
      <div class="col-12 mb-4">
        <QmCard>
            <div class="row align-items-center">
              <div class="col-md-8">
                <h5 class="text-primary mb-2">
                  <i class="fas fa-trophy me-2"></i>Achievement Progress
                </h5>
                <p class="text-muted mb-3">You've unlocked {{ unlockedCount }} out of {{ totalAchievements }} achievements!</p>
                <div class="progress" style="height: 12px;">
                  <div 
                    class="progress-bar bg-gradient" 
                    :style="{ width: progressPercentage + '%' }"
                  ></div>
                </div>
                <small class="text-muted mt-2 d-block">{{ progressPercentage }}% Complete</small>
              </div>
              <div class="col-md-4 text-center">
                <div class="achievement-stats">
                  <div class="stat-circle">
                    <span class="h3 text-primary fw-bold">{{ unlockedCount }}</span>
                    <br>
                    <small class="text-muted">Unlocked</small>
                  </div>
                </div>
              </div>
            </div>
        </QmCard>
      </div>
    </div>
    
    <!-- Filter Tabs -->
    <div class="row mb-4">
      <div class="col-12">
        <ul class="nav nav-pills justify-content-center">
          <li class="nav-item">
            <button 
              class="nav-link" 
              :class="{ active: activeFilter === 'all' }"
              @click="activeFilter = 'all'"
            >
              <i class="fas fa-list me-2"></i>All
            </button>
          </li>
          <li class="nav-item">
            <button 
              class="nav-link" 
              :class="{ active: activeFilter === 'unlocked' }"
              @click="activeFilter = 'unlocked'"
            >
              <i class="fas fa-unlock me-2"></i>Unlocked
            </button>
          </li>
          <li class="nav-item">
            <button 
              class="nav-link" 
              :class="{ active: activeFilter === 'locked' }"
              @click="activeFilter = 'locked'"
            >
              <i class="fas fa-lock me-2"></i>Locked
            </button>
          </li>
        </ul>
      </div>
    </div>
    
    <!-- Achievements Grid -->
    <div class="row">
      <div 
        v-for="achievement in filteredAchievements" 
        :key="achievement.id"
        class="col-lg-4 col-md-6 mb-4"
      >
        <QmCard 
          :class="{
            'unlocked': achievement.unlocked,
            'locked': !achievement.unlocked
          }"
        >
          <template #content>
            <div class="text-center p-4">
            <div class="achievement-icon mb-3">
              <div 
                class="icon-circle"
                :class="{
                  'bg-gradient-success': achievement.unlocked,
                  'bg-light': !achievement.unlocked
                }"
              >
                <i 
                  :class="achievement.icon"
                  :style="{
                    color: achievement.unlocked ? '#fff' : '#6c757d',
                    fontSize: '2.5rem'
                  }"
                ></i>
              </div>
            </div>
            
            <h5 class="achievement-title mb-2" :class="{ 'text-muted': !achievement.unlocked }">
              {{ achievement.title }}
            </h5>
            
            <p class="achievement-description text-muted small mb-3">
              {{ achievement.description }}
            </p>
            
            <div class="achievement-meta">
              <div v-if="achievement.unlocked" class="unlocked-info">
                <QmBadge variant="success" class="mb-2">
                  <i class="fas fa-check me-1"></i>Unlocked
                </QmBadge>
                <br>
                <small class="text-muted">
                  <i class="fas fa-calendar me-1"></i>
                  {{ formatDate(achievement.unlockedAt) }}
                </small>
              </div>
              
              <div v-else class="locked-info">
                <QmBadge variant="secondary" class="mb-2">
                  <i class="fas fa-lock me-1"></i>Locked
                </QmBadge>
                <br>
                <div v-if="achievement.progress" class="progress-info">
                  <small class="text-muted d-block mb-1">
                    Progress: {{ achievement.progress.current }}/{{ achievement.progress.required }}
                  </small>
                  <div class="progress" style="height: 6px;">
                    <div 
                      class="progress-bar bg-primary"
                      :style="{ width: (achievement.progress.current / achievement.progress.required * 100) + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="achievement.rarity" class="achievement-rarity mt-3">
              <QmBadge 
                :class="{
                  'bg-warning text-dark': achievement.rarity === 'common',
                  'bg-info': achievement.rarity === 'rare',
                  'bg-purple': achievement.rarity === 'epic',
                  'bg-warning': achievement.rarity === 'legendary'
                }"
              >
                {{ achievement.rarity.toUpperCase() }}
              </QmBadge>
            </div>
            </div>
          </template>
        </QmCard>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-if="filteredAchievements.length === 0" class="row">
      <div class="col-12">
        <div class="text-center py-5">
          <i class="fas fa-medal text-muted" style="font-size: 4rem;"></i>
          <h4 class="text-muted mt-3">No achievements found</h4>
          <p class="text-muted">Try changing your filter or start taking quizzes to unlock achievements!</p>
        </div>
      </div>
    </div>
  </DashboardTemplate>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import DashboardTemplate from '../components/templates/DashboardTemplate.vue'
import QmCard from '../components/atoms/QmCard.vue'
import QmBadge from '../components/atoms/QmBadge.vue'

export default {
  name: 'Achievements',
  components: {
    DashboardTemplate,
    QmCard,
    QmBadge
  },
  setup() {
    const store = useStore()
    const activeFilter = ref('all')
    
    const breadcrumbs = [
      { text: 'Dashboard', to: '/dashboard', icon: 'fas fa-tachometer-alt' },
      { text: 'Achievements', icon: 'fas fa-medal' }
    ]
    
    const achievements = ref([
      {
        id: 1,
        title: 'First Steps',
        description: 'Complete your first quiz',
        icon: 'fas fa-baby',
        unlocked: true,
        unlockedAt: new Date().toISOString(),
        rarity: 'common'
      },
      {
        id: 2,
        title: 'Perfect Score',
        description: 'Score 100% on any quiz',
        icon: 'fas fa-star',
        unlocked: true,
        unlockedAt: new Date(Date.now() - 86400000).toISOString(),
        rarity: 'rare'
      },
      {
        id: 3,
        title: 'Quiz Master',
        description: 'Complete 10 quizzes',
        icon: 'fas fa-graduation-cap',
        unlocked: false,
        progress: { current: 7, required: 10 },
        rarity: 'epic'
      },
      {
        id: 4,
        title: 'Speed Demon',
        description: 'Complete a quiz in under 2 minutes',
        icon: 'fas fa-bolt',
        unlocked: false,
        rarity: 'rare'
      },
      {
        id: 5,
        title: 'Streak Master',
        description: 'Maintain a 5-day quiz streak',
        icon: 'fas fa-fire',
        unlocked: false,
        progress: { current: 3, required: 5 },
        rarity: 'epic'
      },
      {
        id: 6,
        title: 'Scholar',
        description: 'Achieve 90%+ average across all subjects',
        icon: 'fas fa-book',
        unlocked: false,
        rarity: 'legendary'
      }
    ])
    
    const filteredAchievements = computed(() => {
      if (activeFilter.value === 'unlocked') {
        return achievements.value.filter(a => a.unlocked)
      } else if (activeFilter.value === 'locked') {
        return achievements.value.filter(a => !a.unlocked)
      }
      return achievements.value
    })
    
    const unlockedCount = computed(() => {
      return achievements.value.filter(a => a.unlocked).length
    })
    
    const totalAchievements = computed(() => {
      return achievements.value.length
    })
    
    const progressPercentage = computed(() => {
      return Math.round((unlockedCount.value / totalAchievements.value) * 100)
    })
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    }
    
    onMounted(() => {
      // Load achievements from store if available
      // For now using mock data
    })
    
    return {
      activeFilter,
      breadcrumbs,
      achievements,
      filteredAchievements,
      unlockedCount,
      totalAchievements,
      progressPercentage,
      formatDate
    }
  }
}
</script>

<style scoped>
.achievement-card {
  transition: all 0.3s ease;
  border-radius: 12px;
}

.achievement-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

.achievement-card.locked {
  opacity: 0.7;
}

.achievement-card.unlocked {
  border: 2px solid #28a745;
}

.icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  transition: all 0.3s ease;
}

.bg-gradient-success {
  background: linear-gradient(135deg, #28a745, #20c997);
}

.bg-gradient {
  background: linear-gradient(135deg, #007bff, #0056b3);
}

.stat-circle {
  width: 100px;
  height: 100px;
  border: 3px solid #007bff;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.nav-pills .nav-link {
  border-radius: 25px;
  margin: 0 5px;
  transition: all 0.3s ease;
}

.nav-pills .nav-link.active {
  background: linear-gradient(135deg, #007bff, #0056b3);
}

.bg-purple {
  background-color: #6f42c1 !important;
}

.progress {
  border-radius: 10px;
}

.progress-bar {
  border-radius: 10px;
}

.achievement-title {
  font-weight: 600;
}

.achievement-description {
  line-height: 1.4;
}
</style>