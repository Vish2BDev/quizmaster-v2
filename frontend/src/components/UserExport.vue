<template>
  <div class="user-export-component">
    <!-- Export Card -->
    <div class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="fas fa-download me-2 text-primary"></i>
          Export My Quiz Data
        </h5>
        <span class="badge bg-info">CSV Format</span>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-8">
            <p class="text-muted mb-3">
              Export your complete quiz history including scores, dates, and performance metrics.
              You'll receive an email notification when your export is ready.
            </p>
            
            <div class="export-info mb-3">
              <h6 class="text-primary">Export includes:</h6>
              <ul class="list-unstyled">
                <li><i class="fas fa-check text-success me-2"></i>Quiz titles and subjects</li>
                <li><i class="fas fa-check text-success me-2"></i>Scores and percentages</li>
                <li><i class="fas fa-check text-success me-2"></i>Attempt dates and times</li>
                <li><i class="fas fa-check text-success me-2"></i>Time taken per quiz</li>
              </ul>
            </div>
          </div>
          <div class="col-md-4 text-center">
            <div class="export-action">
              <button 
                class="btn btn-primary btn-lg"
                @click="triggerExport"
                :disabled="isExporting || hasActiveExport"
              >
                <i class="fas fa-download me-2" v-if="!isExporting"></i>
                <i class="fas fa-spinner fa-spin me-2" v-if="isExporting"></i>
                {{ exportButtonText }}
              </button>
              
              <div v-if="hasActiveExport" class="mt-3">
                <div class="alert alert-info">
                  <i class="fas fa-clock me-2"></i>
                  Export in progress...
                </div>
                <div class="progress">
                  <div 
                    class="progress-bar progress-bar-striped progress-bar-animated" 
                    :style="{ width: exportProgress + '%' }"
                  ></div>
                </div>
                <small class="text-muted mt-2 d-block">{{ exportStatus }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Export History -->
    <div class="card" v-if="exportHistory.length > 0">
      <div class="card-header">
        <h5 class="mb-0">
          <i class="fas fa-history me-2 text-secondary"></i>
          Recent Exports
        </h5>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Date</th>
                <th>Status</th>
                <th>Records</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="export_item in exportHistory" :key="export_item.id">
                <td>
                  <small class="text-muted">
                    {{ formatDate(export_item.createdAt) }}
                  </small>
                </td>
                <td>
                  <span 
                    class="badge"
                    :class="getStatusBadgeClass(export_item.status)"
                  >
                    <i :class="getStatusIcon(export_item.status)" class="me-1"></i>
                    {{ export_item.status }}
                  </span>
                </td>
                <td>
                  <span class="text-muted">{{ export_item.recordCount || '-' }}</span>
                </td>
                <td>
                  <button 
                    v-if="export_item.status === 'completed'"
                    class="btn btn-sm btn-outline-primary"
                    @click="checkExportStatus(export_item.taskId)"
                  >
                    <i class="fas fa-refresh me-1"></i>
                    Check Status
                  </button>
                  <span v-else class="text-muted">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/services/api'

export default {
  name: 'UserExport',
  emits: ['show-toast'],
  setup(props, { emit }) {
    // Reactive state
    const isExporting = ref(false)
    const hasActiveExport = ref(false)
    const exportProgress = ref(0)
    const exportStatus = ref('')
    const currentTaskId = ref(null)
    const exportHistory = ref([])
    const statusCheckInterval = ref(null)

    // Computed properties
    const exportButtonText = computed(() => {
      if (isExporting.value) return 'Starting Export...'
      if (hasActiveExport.value) return 'Export in Progress'
      return 'Export My Data'
    })

    // Methods
    const triggerExport = async () => {
      if (isExporting.value || hasActiveExport.value) return
      
      isExporting.value = true
      
      try {
        const response = await api.post('/user/export-csv')
        
        if (response.data.success) {
          currentTaskId.value = response.data.task_id
          hasActiveExport.value = true
          exportStatus.value = 'Export started...'
          exportProgress.value = 10
          
          // Add to history
          exportHistory.value.unshift({
            id: Date.now(),
            taskId: response.data.task_id,
            createdAt: new Date(),
            status: 'pending',
            recordCount: null
          })
          
          // Start checking status
          startStatusCheck()
          
          emit('show-toast', {
            title: 'Export Started',
            message: response.data.message,
            type: 'success'
          })
        }
      } catch (error) {
        emit('show-toast', {
          title: 'Export Failed',
          message: error.response?.data?.error || 'Failed to start export',
          type: 'error'
        })
      } finally {
        isExporting.value = false
      }
    }

    const checkExportStatus = async (taskId = null) => {
      const id = taskId || currentTaskId.value
      if (!id) return
      
      try {
        const response = await api.get(`/user/export-status/${id}`)
        const status = response.data
        
        exportStatus.value = status.status || 'Checking status...'
        
        if (status.state === 'PROGRESS') {
          exportProgress.value = status.progress || 50
        } else if (status.state === 'SUCCESS') {
          exportProgress.value = 100
          hasActiveExport.value = false
          stopStatusCheck()
          
          // Update history
          const historyItem = exportHistory.value.find(item => item.taskId === id)
          if (historyItem) {
            historyItem.status = 'completed'
          }
          
          emit('show-toast', {
            title: 'Export Complete',
            message: 'Your data has been exported and emailed to you!',
            type: 'success'
          })
        } else if (status.state === 'FAILURE') {
          hasActiveExport.value = false
          stopStatusCheck()
          
          // Update history
          const historyItem = exportHistory.value.find(item => item.taskId === id)
          if (historyItem) {
            historyItem.status = 'failed'
          }
          
          emit('show-toast', {
            title: 'Export Failed',
            message: status.status || 'Export failed',
            type: 'error'
          })
        }
      } catch (error) {
        console.error('Error checking export status:', error)
      }
    }

    const startStatusCheck = () => {
      if (statusCheckInterval.value) {
        clearInterval(statusCheckInterval.value)
      }
      
      statusCheckInterval.value = setInterval(() => {
        checkExportStatus()
      }, 3000) // Check every 3 seconds
    }

    const stopStatusCheck = () => {
      if (statusCheckInterval.value) {
        clearInterval(statusCheckInterval.value)
        statusCheckInterval.value = null
      }
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleString()
    }

    const getStatusBadgeClass = (status) => {
      switch (status) {
        case 'completed': return 'bg-success'
        case 'failed': return 'bg-danger'
        case 'pending': return 'bg-warning'
        default: return 'bg-secondary'
      }
    }

    const getStatusIcon = (status) => {
      switch (status) {
        case 'completed': return 'fas fa-check'
        case 'failed': return 'fas fa-times'
        case 'pending': return 'fas fa-clock'
        default: return 'fas fa-question'
      }
    }

    // Lifecycle
    onMounted(() => {
      // Load any existing export history from localStorage
      const savedHistory = localStorage.getItem('exportHistory')
      if (savedHistory) {
        try {
          exportHistory.value = JSON.parse(savedHistory)
        } catch (e) {
          console.error('Error loading export history:', e)
        }
      }
    })

    onUnmounted(() => {
      stopStatusCheck()
      // Save export history to localStorage
      localStorage.setItem('exportHistory', JSON.stringify(exportHistory.value))
    })

    return {
      isExporting,
      hasActiveExport,
      exportProgress,
      exportStatus,
      exportHistory,
      exportButtonText,
      triggerExport,
      checkExportStatus,
      formatDate,
      getStatusBadgeClass,
      getStatusIcon
    }
  }
}
</script>

<style scoped>
.user-export-component {
  max-width: 800px;
}

.export-action {
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 0.5rem;
  border: 2px dashed #dee2e6;
}

.export-info ul {
  margin-bottom: 0;
}

.export-info li {
  padding: 0.25rem 0;
}

.progress {
  height: 8px;
  border-radius: 4px;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
  font-size: 0.875rem;
}

.table td {
  vertical-align: middle;
}

.badge {
  font-size: 0.75rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .user-export-component {
    max-width: 100%;
  }
  
  .export-action {
    margin-top: 1rem;
  }
}
</style>