<template>
  <DashboardTemplate 
    page-title="My Quizzes"
    page-description="View and manage your quiz attempts"
    page-icon="fas fa-play"
    :breadcrumbs="breadcrumbs"
  >
    <div class="row">
      <div class="col-12">
        <QmCard>
          <template #header>
            <h5 class="card-title text-primary mb-0">
              <i class="fas fa-play me-2"></i>My Quiz Attempts
            </h5>
          </template>
            <div v-if="quizAttempts.length === 0" class="text-center py-5">
              <i class="fas fa-clipboard-list text-muted" style="font-size: 4rem;"></i>
              <h4 class="text-muted mt-3">No Quiz Attempts Yet</h4>
              <p class="text-muted">Start taking quizzes to see your attempts here!</p>
              <QmBtn 
                variant="primary" 
                icon="fas fa-arrow-left" 
                @click="$router.push('/dashboard')"
              >
                Back to Dashboard
              </QmBtn>
            </div>
            
            <div v-else>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Quiz Title</th>
                      <th>Subject</th>
                      <th>Score</th>
                      <th>Date Taken</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="attempt in quizAttempts" :key="attempt.id">
                      <td>
                        <strong>{{ attempt.quiz_title }}</strong>
                      </td>
                      <td>
                        <QmBadge variant="primary">{{ attempt.subject_name }}</QmBadge>
                      </td>
                      <td>
                        <span class="fw-bold" :class="getScoreClass(attempt.score_percentage)">
                          {{ attempt.score_percentage }}%
                        </span>
                      </td>
                      <td>
                        {{ formatDate(attempt.completed_at) }}
                      </td>
                      <td>
                        <QmBadge variant="success">Completed</QmBadge>
                      </td>
                    </tr>
                  </tbody>
                </table>
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
import QmBtn from '@/components/atoms/QmBtn.vue'
import QmBadge from '@/components/atoms/QmBadge.vue'

export default {
  name: 'MyQuizzes',
  components: {
    DashboardTemplate,
    QmCard,
    QmBtn,
    QmBadge
  },
  setup() {
    const store = useStore()
    const quizAttempts = ref([])
    
    const breadcrumbs = [
      { text: 'Dashboard', to: '/dashboard', icon: 'fas fa-tachometer-alt' },
      { text: 'My Quizzes', icon: 'fas fa-play' }
    ]
    
    const fetchQuizAttempts = async () => {
      try {
        await store.dispatch('fetchUserQuizAttempts')
        quizAttempts.value = store.getters.userQuizAttempts || []
      } catch (error) {
        console.error('Error fetching quiz attempts:', error)
      }
    }
    
    const getScoreClass = (score) => {
      if (score >= 80) return 'text-success'
      if (score >= 60) return 'text-warning'
      return 'text-danger'
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
    
    onMounted(() => {
      fetchQuizAttempts()
    })
    
    return {
      quizAttempts,
      breadcrumbs,
      getScoreClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.table th {
  background-color: #f8f9fa;
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.table-hover tbody tr:hover {
  background-color: rgba(0, 123, 255, 0.05);
}
</style>