<template>
  <div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/admin">Dashboard</router-link>
            </li>
            <li class="breadcrumb-item active">All Chapters</li>
          </ol>
        </nav>
        <h2>All Chapters</h2>
        <p class="text-muted">View and manage all chapters across all subjects</p>
      </div>
    </div>
    
    <!-- Search and Filter -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="input-group">
          <span class="input-group-text"><i class="fas fa-search"></i></span>
          <input 
            v-model="searchQuery" 
            type="text" 
            class="form-control" 
            placeholder="Search chapters..."
          >
        </div>
      </div>
      <div class="col-md-6">
        <select v-model="selectedSubject" class="form-select">
          <option value="">All Subjects</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
            {{ subject.name }}
          </option>
        </select>
      </div>
    </div>
    
    <!-- Chapters Grid -->
    <div class="row">
      <div v-for="chapter in filteredChapters" :key="chapter.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title">{{ chapter.name }}</h5>
              <span class="badge bg-primary">{{ chapter.subject_name }}</span>
            </div>
            <p class="card-text">{{ chapter.description || 'No description available' }}</p>
            <div class="chapter-meta">
              <small class="text-muted">
                <i class="fas fa-list me-1"></i>{{ chapter.quizzes_count || 0 }} quizzes
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
                <i class="fas fa-eye me-1"></i>View Quizzes
              </router-link>
              <router-link 
                :to="`/admin/subjects/${chapter.subject_id}/chapters`" 
                class="btn btn-outline-secondary btn-sm"
              >
                <i class="fas fa-folder me-1"></i>Subject
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="filteredChapters.length === 0" class="text-center text-muted py-5">
      <i class="fas fa-folder-open fa-3x mb-3"></i>
      <h4>No chapters found</h4>
      <p>Try adjusting your search or filter criteria.</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'AllChapters',
  setup() {
    const store = useStore()
    const searchQuery = ref('')
    const selectedSubject = ref('')
    
    const subjects = computed(() => store.state.subjects)
    const allChapters = computed(() => {
      // Get chapters from store and add subject names
      return store.state.chapters.map(chapter => {
        const subject = subjects.value.find(s => s.id === chapter.subject_id)
        return {
          ...chapter,
          subject_name: subject ? subject.name : 'Unknown Subject'
        }
      })
    })
    
    const filteredChapters = computed(() => {
      let filtered = allChapters.value
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(chapter => 
          chapter.name.toLowerCase().includes(query) ||
          (chapter.description && chapter.description.toLowerCase().includes(query)) ||
          chapter.subject_name.toLowerCase().includes(query)
        )
      }
      
      if (selectedSubject.value) {
        filtered = filtered.filter(chapter => chapter.subject_id == selectedSubject.value)
      }
      
      return filtered
    })
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    const loadAllData = async () => {
      try {
        await store.dispatch('fetchSubjects')
        await store.dispatch('fetchAllChapters')
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
      subjects,
      filteredChapters,
      formatDate
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

.badge {
  font-size: 0.75em;
}
</style>