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
                <li class="breadcrumb-item">
              <router-link :to="`/admin/chapters/${chapterId}/quizzes`">{{ chapterName }}</router-link>
                </li>
            <li class="breadcrumb-item active">{{ quizTitle }} - Questions</li>
              </ol>
            </nav>
        <h2>Manage Questions</h2>
          </div>
      <button @click="showCreateModal" class="btn btn-primary">
        <i class="fas fa-plus me-2"></i>Add New Question
          </button>
        </div>

        <!-- Questions List -->
    <div class="row">
      <div v-for="(question, index) in questions" :key="question.id" class="col-12 mb-4">
                <div class="card">
                  <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">Question {{ index + 1 }}</h6>
            <div>
              <button @click="editQuestion(question)" class="btn btn-outline-secondary btn-sm me-2">
                <i class="fas fa-edit me-1"></i>Edit
                      </button>
              <button @click="deleteQuestion(question.id)" class="btn btn-outline-danger btn-sm">
                <i class="fas fa-trash me-1"></i>Delete
                      </button>
                    </div>
                  </div>
                  <div class="card-body">
            <div class="question-preview">
              <p class="fw-bold mb-3">{{ question.text }}</p>
                    <div class="row">
                      <div class="col-md-6">
                  <div class="option" :class="{ 'correct-option': question.correct_option === 'a' }">
                    <strong>A.</strong> {{ question.option_a }}
                        </div>
                  <div class="option" :class="{ 'correct-option': question.correct_option === 'b' }">
                    <strong>B.</strong> {{ question.option_b }}
                        </div>
                      </div>
                      <div class="col-md-6">
                  <div class="option" :class="{ 'correct-option': question.correct_option === 'c' }">
                    <strong>C.</strong> {{ question.option_c }}
                        </div>
                  <div class="option" :class="{ 'correct-option': question.correct_option === 'd' }">
                    <strong>D.</strong> {{ question.option_d }}
                  </div>
                </div>
              </div>
              <div class="mt-2">
                <small class="text-muted">
                  <i class="fas fa-check-circle text-success me-1"></i>
                  Correct Answer: {{ question.correct_option.toUpperCase() }}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="questions.length === 0" class="text-center text-muted">
      <i class="fas fa-question-circle fa-3x mb-3"></i>
      <p>No questions created yet. Add your first question to get started!</p>
    </div>

    <!-- Create/Edit Question Modal -->
    <div class="modal fade" id="questionModal" tabindex="-1">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editMode ? 'Edit Question' : 'Create New Question' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="saveQuestion">
          <div class="modal-body">
              <div class="mb-4">
                <label for="questionText" class="form-label">Question Text</label>
                <textarea 
                  class="form-control" 
                  id="questionText"
                  v-model="form.text"
                  :class="{ 'is-invalid': errors.text }"
                  rows="3"
                  placeholder="Enter your question here..."
                  required
                ></textarea>
                <div class="invalid-feedback">{{ errors.text }}</div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="optionA" class="form-label">Option A</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="optionA"
                    v-model="form.option_a"
                    :class="{ 'is-invalid': errors.option_a }"
                    placeholder="Enter option A"
                    required
                  >
                  <div class="invalid-feedback">{{ errors.option_a }}</div>
                </div>
                <div class="col-md-6">
                  <label for="optionB" class="form-label">Option B</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="optionB"
                    v-model="form.option_b"
                    :class="{ 'is-invalid': errors.option_b }"
                    placeholder="Enter option B"
                    required
                  >
                  <div class="invalid-feedback">{{ errors.option_b }}</div>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="optionC" class="form-label">Option C</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="optionC"
                    v-model="form.option_c"
                    :class="{ 'is-invalid': errors.option_c }"
                    placeholder="Enter option C"
                    required
                  >
                  <div class="invalid-feedback">{{ errors.option_c }}</div>
                </div>
                <div class="col-md-6">
                  <label for="optionD" class="form-label">Option D</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="optionD"
                    v-model="form.option_d"
                    :class="{ 'is-invalid': errors.option_d }"
                    placeholder="Enter option D"
                    required
                  >
                  <div class="invalid-feedback">{{ errors.option_d }}</div>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Correct Answer</label>
                <div class="d-flex gap-3">
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="radio" 
                      name="correctOption"
                      id="correctA"
                      value="a"
                      v-model="form.correct_option"
                      required
                    >
                    <label class="form-check-label" for="correctA">A</label>
                  </div>
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="radio" 
                      name="correctOption"
                      id="correctB"
                      value="b"
                      v-model="form.correct_option"
                      required
                    >
                    <label class="form-check-label" for="correctB">B</label>
                  </div>
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="radio" 
                      name="correctOption"
                      id="correctC"
                      value="c"
                      v-model="form.correct_option"
                      required
                    >
                    <label class="form-check-label" for="correctC">C</label>
                  </div>
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="radio" 
                      name="correctOption"
                      id="correctD"
                      value="d"
                      v-model="form.correct_option"
                      required
                    >
                    <label class="form-check-label" for="correctD">D</label>
                  </div>
                </div>
              </div>
              
              <!-- Question Preview -->
              <div class="mt-4" v-if="form.text || form.option_a || form.option_b || form.option_c || form.option_d">
                <h6>Preview:</h6>
                <div class="card bg-light">
                  <div class="card-body">
                    <p class="fw-bold" v-if="form.text">{{ form.text }}</p>
                    <div class="row" v-if="form.option_a || form.option_b || form.option_c || form.option_d">
                      <div class="col-md-6">
                        <div class="option" v-if="form.option_a" :class="{ 'correct-option': form.correct_option === 'a' }">
                          <strong>A.</strong> {{ form.option_a }}
                        </div>
                        <div class="option" v-if="form.option_b" :class="{ 'correct-option': form.correct_option === 'b' }">
                          <strong>B.</strong> {{ form.option_b }}
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="option" v-if="form.option_c" :class="{ 'correct-option': form.correct_option === 'c' }">
                          <strong>C.</strong> {{ form.option_c }}
                        </div>
                        <div class="option" v-if="form.option_d" :class="{ 'correct-option': form.correct_option === 'd' }">
                          <strong>D.</strong> {{ form.option_d }}
                        </div>
                      </div>
                    </div>
                  </div>
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
  name: 'ManageQuestions',
  setup() {
    const store = useStore()
    const route = useRoute()
    const quizId = route.params.quizId
    
    const editMode = ref(false)
    const loading = ref(false)
    const currentQuestion = ref(null)
    const quizTitle = ref('')
    const chapterName = ref('')
    const subjectName = ref('')
    const subjectId = ref(null)
    const chapterId = ref(null)
    
    const form = ref({
      text: '',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      correct_option: ''
    })

    const errors = ref({})
    
    const questions = computed(() => store.state.questions)
    
    const showCreateModal = () => {
      editMode.value = false
      form.value = {
        text: '',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_option: ''
      }
      errors.value = {}
      const modal = new Modal(document.getElementById('questionModal'))
      modal.show()
    }
    
    const editQuestion = (question) => {
      editMode.value = true
      currentQuestion.value = question
      form.value = { ...question }
      errors.value = {}
      const modal = new Modal(document.getElementById('questionModal'))
      modal.show()
    }
    
    const validateForm = () => {
      errors.value = {}
      
      if (!form.value.text.trim()) {
        errors.value.text = 'Question text is required'
      }
      
      if (!form.value.option_a.trim()) {
        errors.value.option_a = 'Option A is required'
      }
      
      if (!form.value.option_b.trim()) {
        errors.value.option_b = 'Option B is required'
      }
      
      if (!form.value.option_c.trim()) {
        errors.value.option_c = 'Option C is required'
      }
      
      if (!form.value.option_d.trim()) {
        errors.value.option_d = 'Option D is required'
      }
      
      if (!form.value.correct_option) {
        errors.value.correct_option = 'Please select the correct answer'
      }
      
      return Object.keys(errors.value).length === 0
    }

    const saveQuestion = async () => {
      if (!validateForm()) return
      
      loading.value = true
      
      let result
      if (editMode.value) {
        result = await store.dispatch('updateQuestion', {
          id: currentQuestion.value.id,
          data: form.value
        })
        } else {
        result = await store.dispatch('createQuestion', {
          quizId: quizId,
          questionData: form.value
        })
      }
      
      if (result.success) {
        const modal = Modal.getInstance(document.getElementById('questionModal'))
        modal.hide()
        showSuccessMessage(`Question ${editMode.value ? 'updated' : 'created'} successfully.`)
      } else {
        alert('Error: ' + result.message)
      }
      
      loading.value = false
    }
    
    const deleteQuestion = async (questionId) => {
      if (confirm('Are you sure you want to delete this question?')) {
        const result = await store.dispatch('deleteQuestion', questionId)
        if (result.success) {
          showSuccessMessage('Question deleted successfully.')
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
    
    const fetchBreadcrumbData = async () => {
      try {
        await store.dispatch('fetchSubjects')
        const subjects = store.state.subjects
        
        for (const subject of subjects) {
          await store.dispatch('fetchChapters', subject.id)
          const chapters = store.state.chapters
          
          for (const chapter of chapters) {
            await store.dispatch('fetchQuizzes', chapter.id)
            const quiz = store.state.quizzes.find(q => q.id == quizId)
            if (quiz) {
              quizTitle.value = quiz.title
              chapterName.value = chapter.name
              subjectName.value = subject.name
              subjectId.value = subject.id
              chapterId.value = chapter.id
              return
            }
          }
        }
      } catch (error) {
        console.error('Error fetching breadcrumb data:', error)
      }
    }
    
    onMounted(async () => {
      await fetchBreadcrumbData()
      await store.dispatch('fetchQuestions', quizId)
    })

    return {
      editMode,
      loading,
      form,
      errors,
      questions,
      quizTitle,
      chapterName,
      subjectName,
      subjectId,
      chapterId,
      showCreateModal,
      editQuestion,
      saveQuestion,
      deleteQuestion
    }
  }
}
</script>

<style scoped>
.option {
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  border-radius: 0.375rem;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
}

.correct-option {
  background-color: #d1edff;
  border-color: #0d6efd;
  color: #0d6efd;
}

.question-preview {
  font-size: 0.95rem;
}

.modal-xl .modal-body {
  max-height: 70vh;
  overflow-y: auto;
}
</style> 