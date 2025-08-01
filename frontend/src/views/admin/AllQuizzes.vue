<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/admin">Dashboard</router-link>
            </li>
            <li class="breadcrumb-item active">All Quizzes</li>
          </ol>
        </nav>
        <h2>All Quizzes</h2>
        <p class="text-muted">View and manage all quizzes across all subjects and chapters</p>
      </div>
    </div>
    
    <!-- Search and Filter -->
    <div class="row mb-4">
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
      <div class="col-md-4">
        <select v-model="selectedSubject" class="form-select" @change="onSubjectChange">
          <option value="">All Subjects</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
            {{ subject.name }}
          </option>
        </select>
      </div>
      <div class="col-md-4">
        <select v-model="selectedChapter" class="form-select">
          <option value="">All Chapters</option>
          <option v-for="chapter in availableChapters" :key="chapter.id" :value="chapter.id">
            {{ chapter.name }}
          </option>
        </select>
      </div>
    </div>
    
    <!-- Quizzes Grid -->
    <div class="row">
      <div v-for="quiz in filteredQuizzes" :key="quiz.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title">{{ quiz.title }}</h5>
              <span class="badge" :class="quiz.is_active ? 'bg-success' : 'bg-secondary'">
                {{ quiz.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
            <p class="card-text">{{ quiz.description || 'No description available' }}</p>
            
            <!-- Hierarchy Info -->
            <div class="quiz-hierarchy mb-2">
              <small class="text-primary">
                <i class="fas fa-book me-1"></i>{{ quiz.subject_name }}
              </small><br>
              <small class="text-info">
                <i class="fas fa-bookmark me-1"></i>{{ quiz.chapter_name }}
              </small>
            </div>
            
            <div class="quiz-meta">
              <small class="text-muted">
                <i class="fas fa-question me-1"></i>{{ quiz.questions_count || 0 }} questions
              </small><br>
              <small class="text-muted">
                <i class="fas fa-calendar me-1"></i>{{ formatDate(quiz.created_at) }}
              </small>
            </div>
          </div>
          <div class="card-footer">
            <div class="btn-group w-100" role="group">
              <router-link 
                :to="`/admin/chapters/${quiz.chapter_id}/quizzes`" 
                class="btn btn-outline-primary btn-sm"
              >
                <i class="fas fa-eye me-1"></i>Manage
              </router-link>
              <router-link 
                :to="`/quiz/${quiz.id}`" 
                class="btn btn-outline-success btn-sm"
                target="_blank"
              >
                <i class="fas fa-play me-1"></i>Preview
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="filteredQuizzes.length === 0" class="text-center text-muted py-5">
      <i class="fas fa-question-circle fa-3x mb-3"></i>
      <h4>No quizzes found</h4>
      <p>Try adjusting your search or filter criteria.</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'AllQuizzes',
  setup() {
    const store = useStore()
    const searchQuery = ref('')
    const selectedSubject = ref('')
    const selectedChapter = ref('')
    
    const subjects = computed(() => store.state.subjects)
    const chapters = computed(() => store.state.chapters)
    
    const availableChapters = computed(() => {
      if (!selectedSubject.value) {
        return chapters.value || []
      }
      return (chapters.value || []).filter(chapter => chapter.subject_id == selectedSubject.value)
    })
    
    const allQuizzes = computed(() => {
      // Get quizzes from store and add hierarchy info
      return store.state.quizzes.map(quiz => {
        const chapter = chapters.value.find(c => c.id === quiz.chapter_id)
        const subject = subjects.value.find(s => s.id === chapter?.subject_id)
        return {
          ...quiz,
          subject_name: subject ? subject.name : 'Unknown Subject',
          subject_id: subject ? subject.id : null,
          chapter_name: chapter ? chapter.name : 'Unknown Chapter'
        }
      })
    })
    
    const filteredQuizzes = computed(() => {
      let filtered = allQuizzes.value
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(quiz => 
          quiz.title.toLowerCase().includes(query) ||
          (quiz.description && quiz.description.toLowerCase().includes(query)) ||
          quiz.subject_name.toLowerCase().includes(query) ||
          quiz.chapter_name.toLowerCase().includes(query)
        )
      }
      
      if (selectedSubject.value) {
        filtered = filtered.filter(quiz => quiz.subject_id == selectedSubject.value)
      }
      
      if (selectedChapter.value) {
        filtered = filtered.filter(quiz => quiz.chapter_id == selectedChapter.value)
      }
      
      return filtered
    })
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    const onSubjectChange = () => {
      selectedChapter.value = '' // Reset chapter filter when subject changes
    }
    
    const loadAllData = async () => {
      try {
        await store.dispatch('fetchSubjects')
        await store.dispatch('fetchAllChapters')
        await store.dispatch('fetchAllQuizzes')
      } catch (error) {
        console.error('Error loading data:', error)
      }
    }
    
    onMounted(() => {
      loadAllData()
    })
    
    return {
      searchQuery,
      selectedSubject,
      selectedChapter,
      subjects,
      availableChapters,
      filteredQuizzes,
      formatDate,
      onSubjectChange
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

.quiz-hierarchy {
  border-left: 3px solid #e9ecef;
  padding-left: 0.75rem;
}

.btn-group .btn {
  flex: 1;
}

.badge {
  font-size: 0.75em;
}
</style>