<template>
  <AdminLayout 
    page-title="Manage Subjects"
    page-description="Create, edit, and organize your quiz subjects"
    page-icon="fas fa-book"
    :breadcrumbs="breadcrumbs"
    @quick-add-subject="showCreateModal = true"
  >
    <template #header-actions>
      <button class="btn btn-qm-primary" @click="showCreateModal = true">
        <i class="fas fa-plus me-2"></i>
        Add Subject
      </button>
    </template>

    <!-- Subjects List -->
    <div class="card card-qm">
      <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="subjects.length === 0" class="text-center py-4">
              <i class="fas fa-book fa-3x text-muted mb-3"></i>
              <h5 class="text-muted">No subjects found</h5>
              <p class="text-muted">Create your first subject to get started</p>
            </div>
            
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead class="table-light">
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Chapters</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="subject in subjects" :key="subject.id">
                    <td>
                      <strong>{{ subject.name }}</strong>
                    </td>
                    <td>{{ subject.description || 'No description' }}</td>
                    <td>
                      <span class="badge bg-primary">{{ subject.chapters_count || 0 }}</span>
                    </td>
                    <td>{{ formatDate(subject.created_at) }}</td>
                    <td>
                      <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-outline-primary" @click="viewChapters(subject)">
                          <i class="fas fa-list"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" @click="editSubject(subject)">
                          <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" @click="deleteSubject(subject)">
                          <i class="fas fa-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
      </div>
    </div>

    <!-- Create/Edit Subject Modal -->
    <div class="modal fade" id="subjectModal" tabindex="-1" data-bs-backdrop="static">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingSubject ? 'Edit Subject' : 'Create New Subject' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSubject">
              <div class="mb-3">
                <label for="subjectName" class="form-label">Subject Name *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="subjectName"
                  v-model="subjectForm.name"
                  required
                  placeholder="Enter subject name"
                >
              </div>
              <div class="mb-3">
                <label for="subjectDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="subjectDescription"
                  v-model="subjectForm.description"
                  rows="3"
                  placeholder="Enter subject description"
                ></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-qm-primary" @click="saveSubject" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              {{ editingSubject ? 'Update' : 'Create' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Modal } from 'bootstrap'
import AdminLayout from '@/components/AdminLayout.vue'

export default {
  name: 'ManageSubjects',
  components: {
    AdminLayout
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const subjects = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const showCreateModal = ref(false)
    const editingSubject = ref(null)
    const subjectForm = ref({
      name: '',
      description: ''
    })
    
    const breadcrumbs = ref([
      {
        text: 'Content Management',
        icon: 'fas fa-book',
        to: '/admin/subjects'
      },
      {
        text: 'Subjects',
        icon: 'fas fa-list'
      }
    ])

    const fetchSubjects = async () => {
      loading.value = true
      try {
        await store.dispatch('fetchSubjects')
        subjects.value = store.state.subjects
      } catch (error) {
        console.error('Error fetching subjects:', error)
        window.dispatchEvent(new CustomEvent('show-error-toast', {
          detail: { message: 'Failed to load subjects' }
        }))
      } finally {
        loading.value = false
      }
    }

    const saveSubject = async () => {
      if (!subjectForm.value.name.trim()) return
      
      saving.value = true
      try {
        if (editingSubject.value) {
          await store.dispatch('updateSubject', {
            id: editingSubject.value.id,
            data: subjectForm.value
          })
          window.dispatchEvent(new CustomEvent('show-success-toast', {
            detail: { message: 'Subject updated successfully' }
          }))
        } else {
          await store.dispatch('createSubject', subjectForm.value)
          window.dispatchEvent(new CustomEvent('show-success-toast', {
            detail: { message: 'Subject created successfully' }
          }))
        }
        
        // Close modal and reset form
        const modal = Modal.getInstance(document.getElementById('subjectModal'))
        modal.hide()
        resetForm()
        await fetchSubjects()
      } catch (error) {
        console.error('Error saving subject:', error)
        window.dispatchEvent(new CustomEvent('show-error-toast', {
          detail: { message: error.message || 'Failed to save subject' }
        }))
      } finally {
        saving.value = false
      }
    }

    const editSubject = (subject) => {
      editingSubject.value = subject
      subjectForm.value = {
        name: subject.name,
        description: subject.description || ''
      }
      const modal = new Modal(document.getElementById('subjectModal'))
      modal.show()
    }

    const deleteSubject = async (subject) => {
      if (!confirm(`Are you sure you want to delete "${subject.name}"? This will also delete all associated chapters, quizzes, and questions.`)) {
        return
      }
      
      try {
        await store.dispatch('deleteSubject', subject.id)
        window.dispatchEvent(new CustomEvent('show-success-toast', {
          detail: { message: 'Subject deleted successfully' }
        }))
        await fetchSubjects()
      } catch (error) {
        console.error('Error deleting subject:', error)
        window.dispatchEvent(new CustomEvent('show-error-toast', {
          detail: { message: error.message || 'Failed to delete subject' }
        }))
      }
    }

    const viewChapters = (subject) => {
      router.push(`/admin/subjects/${subject.id}/chapters`)
    }

    const resetForm = () => {
      editingSubject.value = null
      subjectForm.value = {
        name: '',
        description: ''
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    // Watch for showCreateModal changes to show the modal
    watch(showCreateModal, (newValue) => {
      if (newValue) {
        resetForm()
        const modal = new Modal(document.getElementById('subjectModal'))
        modal.show()
        showCreateModal.value = false // Reset the flag
      }
    })

    onMounted(() => {
      fetchSubjects()
    })

    return {
      subjects,
      loading,
      saving,
      showCreateModal,
      editingSubject,
      subjectForm,
      breadcrumbs,
      saveSubject,
      editSubject,
      deleteSubject,
      viewChapters,
      formatDate
    }
  }
}
</script>

<style scoped>
.table th {
  font-weight: 700;
  color: #2c3e50;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
  padding: 1rem 0.75rem;
  border: none;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.table th:first-child {
  border-top-left-radius: 8px;
}

.table th:last-child {
  border-top-right-radius: 8px;
}

.table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.table tbody tr {
  transition: all 0.2s ease;
}

.table tbody tr:hover {
  background-color: #f8f9fa;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.table td {
  padding: 1rem 0.75rem;
  vertical-align: middle;
  border-color: #e9ecef;
}

.btn-group .btn {
  margin-right: 0.25rem;
  transition: all 0.2s ease;
}

.btn-group .btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.btn-group .btn:last-child {
  margin-right: 0;
}

.badge {
  font-size: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 20px;
}

.card-qm {
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}
</style>