<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/admin/subjects">Subjects</router-link>
            </li>
            <li class="breadcrumb-item active">{{ subjectName }} - Chapters</li>
          </ol>
        </nav>
        <h2>Manage Chapters</h2>
      </div>
      <button @click="showCreateModal" class="btn btn-primary">
        <i class="fas fa-plus me-2"></i>Add New Chapter
      </button>
    </div>
    
    <!-- Chapters List -->
    <div class="row">
      <div v-for="chapter in chapters" :key="chapter.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">{{ chapter.name }}</h5>
            <p class="card-text">{{ chapter.description || 'No description available' }}</p>
            <div class="chapter-meta">
              <small class="text-muted">
                <i class="fas fa-list me-1"></i>{{ chapter.quizzes_count }} quizzes
              </small><br>
              <small class="text-muted">
                <i class="fas fa-calendar me-1"></i>{{ formatDate(chapter.created_at) }}
              </small>
            </div>
          </div>
          <div class="card-footer">
            <div class="btn-group w-100" role="group">
              <router-link 
                :to="`/admin/chapters/${chapter.id}/quizzes`" 
                class="btn btn-outline-primary btn-sm"
              >
                <i class="fas fa-eye me-1"></i>Quizzes
              </router-link>
              <button @click="editChapter(chapter)" class="btn btn-outline-secondary btn-sm">
                <i class="fas fa-edit me-1"></i>Edit
              </button>
              <button @click="deleteChapter(chapter.id)" class="btn btn-outline-danger btn-sm">
                <i class="fas fa-trash me-1"></i>Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="chapters.length === 0" class="text-center text-muted">
      <i class="fas fa-folder-open fa-3x mb-3"></i>
      <p>No chapters created yet. Add your first chapter to get started!</p>
    </div>
    
    <!-- Create/Edit Chapter Modal -->
    <div class="modal fade" id="chapterModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editMode ? 'Edit Chapter' : 'Create New Chapter' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveChapter">
            <div class="modal-body">
              <div class="mb-3">
                <label for="chapterName" class="form-label">Chapter Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="chapterName"
                  v-model="form.name"
                  :class="{ 'is-invalid': errors.name }"
                  required
                >
                <div class="invalid-feedback">{{ errors.name }}</div>
              </div>
              
              <div class="mb-3">
                <label for="chapterDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="chapterDescription"
                  v-model="form.description"
                  rows="3"
                  placeholder="Enter chapter description (optional)"
                ></textarea>
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
  name: 'ManageChapters',
  setup() {
    const store = useStore()
    const route = useRoute()
    const subjectId = route.params.subjectId
    
    const editMode = ref(false)
    const loading = ref(false)
    const currentChapter = ref(null)
    const subjectName = ref('')
    
    const form = ref({
      name: '',
      description: ''
    })
    
    const errors = ref({})
    
    const chapters = computed(() => store.state.chapters)
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    const showCreateModal = () => {
      editMode.value = false
      form.value = { name: '', description: '' }
      errors.value = {}
      const modal = new Modal(document.getElementById('chapterModal'))
      modal.show()
    }
    
    const editChapter = (chapter) => {
      editMode.value = true
      currentChapter.value = chapter
      form.value = { ...chapter }
      errors.value = {}
      const modal = new Modal(document.getElementById('chapterModal'))
      modal.show()
    }
    
    const validateForm = () => {
      errors.value = {}
      
      if (!form.value.name.trim()) {
        errors.value.name = 'Chapter name is required'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const saveChapter = async () => {
      if (!validateForm()) return
      
      loading.value = true
      
      let result
      if (editMode.value) {
        result = await store.dispatch('updateChapter', {
          id: currentChapter.value.id,
          data: form.value
        })
      } else {
        result = await store.dispatch('createChapter', {
          subjectId: subjectId,
          chapterData: form.value
        })
      }
      
      if (result.success) {
        const modal = Modal.getInstance(document.getElementById('chapterModal'))
        modal.hide()
        showSuccessMessage(`Chapter ${editMode.value ? 'updated' : 'created'} successfully.`)
      } else {
        alert('Error: ' + result.message)
      }
      
      loading.value = false
    }
    
    const deleteChapter = async (chapterId) => {
      if (confirm('Are you sure you want to delete this chapter? This will also delete all associated quizzes and questions.')) {
        const result = await store.dispatch('deleteChapter', chapterId)
        if (result.success) {
          showSuccessMessage('Chapter deleted successfully.')
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
    
    const fetchSubjectDetails = async () => {
      try {
        const subjects = await store.dispatch('fetchSubjects')
        const subject = store.state.subjects.find(s => s.id == subjectId)
        if (subject) {
          subjectName.value = subject.name
        }
      } catch (error) {
        console.error('Error fetching subject details:', error)
      }
    }
    
    onMounted(async () => {
      await fetchSubjectDetails()
      await store.dispatch('fetchChapters', subjectId)
    })
    
    return {
      editMode,
      loading,
      form,
      errors,
      chapters,
      subjectName,
      formatDate,
      showCreateModal,
      editChapter,
      saveChapter,
      deleteChapter
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

.chapter-meta {
  margin-top: 1rem;
}

.btn-group .btn {
  flex: 1;
}
</style> 