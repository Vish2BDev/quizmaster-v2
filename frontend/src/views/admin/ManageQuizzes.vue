<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/admin/subjects">Subjects</router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link :to="`/admin/subjects/${subjectId}/chapters`">{{ subjectName }}</router-link>
            </li>
            <li class="breadcrumb-item active">{{ chapterName }} - Quizzes</li>
          </ol>
        </nav>
        <h2>Manage Quizzes</h2>
      </div>
      <button @click="showCreateModal" class="btn btn-primary">
        <i class="fas fa-plus me-2"></i>Add New Quiz
      </button>
    </div>
    
    <!-- Quizzes List -->
    <div class="row">
      <div v-for="quiz in quizzes" :key="quiz.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title">{{ quiz.title }}</h5>
              <span class="badge" :class="quiz.is_active ? 'bg-success' : 'bg-secondary'">
                {{ quiz.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
            <p class="card-text">{{ quiz.description || 'No description available' }}</p>
            <div class="quiz-meta">
              <small class="text-muted">
                <i class="fas fa-clock me-1"></i>{{ quiz.duration }} minutes
              </small><br>
              <small class="text-muted">
                <i class="fas fa-question-circle me-1"></i>{{ quiz.questions_count }} questions
              </small><br>
              <small class="text-muted">
                <i class="fas fa-users me-1"></i>{{ quiz.attempts_count }} attempts
              </small><br>
              <small class="text-muted">
                <i class="fas fa-calendar me-1"></i>{{ formatDate(quiz.created_at) }}
              </small>
            </div>
          </div>
          <div class="card-footer">
            <div class="btn-group w-100" role="group">
              <router-link 
                :to="`/admin/quizzes/${quiz.id}/questions`" 
                class="btn btn-outline-primary btn-sm"
              >
                <i class="fas fa-eye me-1"></i>Questions
              </router-link>
              <button @click="editQuiz(quiz)" class="btn btn-outline-secondary btn-sm">
                <i class="fas fa-edit me-1"></i>Edit
              </button>
              <button @click="deleteQuiz(quiz.id)" class="btn btn-outline-danger btn-sm">
                <i class="fas fa-trash me-1"></i>Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="quizzes.length === 0" class="text-center text-muted">
      <i class="fas fa-clipboard-list fa-3x mb-3"></i>
      <p>No quizzes created yet. Add your first quiz to get started!</p>
    </div>
    
    <!-- Create/Edit Quiz Modal -->
    <div class="modal fade" id="quizModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editMode ? 'Edit Quiz' : 'Create New Quiz' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveQuiz">
            <div class="modal-body">
              <div class="row">
                <div class="col-md-8">
                  <div class="mb-3">
                    <label for="quizTitle" class="form-label">Quiz Title</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="quizTitle"
                      v-model="form.title"
                      :class="{ 'is-invalid': errors.title }"
                      required
                    >
                    <div class="invalid-feedback">{{ errors.title }}</div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label for="quizDuration" class="form-label">Duration (minutes)</label>
                    <input 
                      type="number" 
                      class="form-control" 
                      id="quizDuration"
                      v-model="form.duration_minutes"
                      min="1"
                      max="180"
                      required
                    >
                  </div>
                </div>
              </div>
              
              <!-- Scheduling Fields -->
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="quizStartTime" class="form-label">Start Time (Optional)</label>
                    <input 
                      type="datetime-local" 
                      class="form-control" 
                      id="quizStartTime"
                      v-model="form.start_time"
                      :class="{ 'is-invalid': errors.start_time }"
                    >
                    <div class="form-text">Leave empty for immediate availability</div>
                    <div class="invalid-feedback">{{ errors.start_time }}</div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Quiz Status</label>
                    <div v-if="editMode && form.start_time">
                      <span class="badge" :class="getStatusBadgeClass(form.status)">{{ getStatusText(form.status) }}</span>
                      <div class="form-text mt-1">{{ getStatusDescription(form.status) }}</div>
                    </div>
                    <div v-else class="form-text">
                      Quiz will be immediately available after creation
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label for="quizDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="quizDescription"
                  v-model="form.description"
                  rows="3"
                  placeholder="Enter quiz description (optional)"
                ></textarea>
              </div>
              
              <div class="mb-3" v-if="editMode">
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    id="quizActive"
                    v-model="form.is_active"
                  >
                  <label class="form-check-label" for="quizActive">
                    Quiz is active and available to users
                  </label>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ editMode ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import { Modal } from 'bootstrap'

export default {
  name: 'ManageQuizzes',
  setup() {
    const store = useStore()
    const route = useRoute()
    const chapterId = route.params.chapterId
    
    const editMode = ref(false)
    const loading = ref(false)
    const currentQuiz = ref(null)
    const chapterName = ref('')
    const subjectName = ref('')
    const subjectId = ref(null)
    
    const form = ref({
      title: '',
      description: '',
      duration_minutes: 30,
      start_time: '',
      is_active: true
    })
    
    const errors = ref({})
    
    const quizzes = computed(() => store.state.quizzes)
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    const showCreateModal = () => {
      editMode.value = false
      form.value = { title: '', description: '', duration_minutes: 30, start_time: '', is_active: true }
      errors.value = {}
      const modal = new Modal(document.getElementById('quizModal'))
      modal.show()
    }
    
    const editQuiz = (quiz) => {
      editMode.value = true
      currentQuiz.value = quiz
      form.value = { ...quiz }
      errors.value = {}
      const modal = new Modal(document.getElementById('quizModal'))
      modal.show()
    }
    
    const validateForm = () => {
      errors.value = {}
      
      if (!form.value.title.trim()) {
        errors.value.title = 'Quiz title is required'
      }
      
      if (!form.value.duration_minutes || form.value.duration_minutes < 1) {
        errors.value.duration_minutes = 'Duration must be at least 1 minute'
      }
      
      if (form.value.start_time && new Date(form.value.start_time) < new Date()) {
        errors.value.start_time = 'Start time cannot be in the past'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const saveQuiz = async () => {
      if (!validateForm()) return
      
      loading.value = true
      
      let result
      if (editMode.value) {
        result = await store.dispatch('updateQuiz', {
          id: currentQuiz.value.id,
          data: form.value
        })
      } else {
        result = await store.dispatch('createQuiz', {
          chapterId: chapterId,
          quizData: form.value
        })
      }
      
      if (result.success) {
        const modal = Modal.getInstance(document.getElementById('quizModal'))
        modal.hide()
        showSuccessMessage(`Quiz ${editMode.value ? 'updated' : 'created'} successfully.`)
      } else {
        alert('Error: ' + result.message)
      }
      
      loading.value = false
    }
    
    const deleteQuiz = async (quizId) => {
      if (confirm('Are you sure you want to delete this quiz? This will also delete all associated questions.')) {
        const result = await store.dispatch('deleteQuiz', quizId)
        if (result.success) {
          showSuccessMessage('Quiz deleted successfully.')
        } else {
          alert('Error: ' + result.message)
        }
      }
    }
    
    const showSuccessMessage = (message) => {
      const alertDiv = document.createElement('div')
      alertDiv.className = 'alert alert-success alert-dismissible fade show'
      alertDiv.innerHTML = `
        <strong>Success!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      `
      document.querySelector('.container-fluid').prepend(alertDiv)
      setTimeout(() => alertDiv.remove(), 3000)
    }
    
    const getStatusBadgeClass = (status) => {
      switch (status) {
        case 'active': return 'bg-success'
        case 'upcoming': return 'bg-warning text-dark'
        case 'expired': return 'bg-danger'
        default: return 'bg-secondary'
      }
    }
    
    const getStatusText = (status) => {
      switch (status) {
        case 'active': return 'Active'
        case 'upcoming': return 'Upcoming'
        case 'expired': return 'Expired'
        default: return 'Inactive'
      }
    }
    
    const getStatusDescription = (status) => {
      switch (status) {
        case 'active': return 'Quiz is currently available for attempts'
        case 'upcoming': return 'Quiz will be available soon'
        case 'expired': return 'Quiz is no longer available'
        default: return 'Quiz is not scheduled'
      }
    }
    
    const fetchBreadcrumbData = async () => {
      try {
        await store.dispatch('fetchSubjects')
        const subjects = store.state.subjects
        
        for (const subject of subjects) {
          await store.dispatch('fetchChapters', subject.id)
          const chapter = store.state.chapters.find(c => c.id == chapterId)
          if (chapter) {
            chapterName.value = chapter.name
            subjectName.value = subject.name
            subjectId.value = subject.id
            break
          }
        }
      } catch (error) {
        console.error('Error fetching breadcrumb data:', error)
      }
    }
    
    onMounted(async () => {
      await fetchBreadcrumbData()
      await store.dispatch('fetchQuizzes', chapterId)
    })
    
    return {
      editMode,
      loading,
      form,
      errors,
      quizzes,
      chapterName,
      subjectName,
      subjectId,
      formatDate,
      showCreateModal,
      editQuiz,
      saveQuiz,
      deleteQuiz,
      getStatusBadgeClass,
      getStatusText,
      getStatusDescription
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-5px);
}

.quiz-meta {
  margin-top: 1rem;
}

.btn-group .btn {
  flex: 1;
}
</style>