<template>
  <div class="data-exports">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="fas fa-download me-2"></i>Data Exports</h2>
      <div class="btn-group">
        <button class="btn btn-outline-primary" @click="refreshExports">
          <i class="fas fa-sync-alt me-1"></i>Refresh
        </button>
      </div>
    </div>

    <!-- Export Options -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5><i class="fas fa-database me-2"></i>All Data Export</h5>
          </div>
          <div class="card-body">
            <p class="text-muted">Export all quiz data including users, subjects, chapters, quizzes, and attempts</p>
            <button 
              class="btn btn-primary" 
              @click="exportAllData"
              :disabled="isLoading"
            >
              <i class="fas fa-download me-1"></i>
              {{ isLoading ? 'Exporting...' : 'Export All Data' }}
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5><i class="fas fa-chart-bar me-2"></i>Analytics Export</h5>
          </div>
          <div class="card-body">
            <p class="text-muted">Export analytics data including performance metrics and statistics</p>
            <button 
              class="btn btn-success" 
              @click="exportAnalytics"
              :disabled="isLoading"
            >
              <i class="fas fa-chart-line me-1"></i>
              {{ isLoading ? 'Exporting...' : 'Export Analytics' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- User-Specific Exports -->
    <div class="card mb-4">
      <div class="card-header">
        <h5><i class="fas fa-users me-2"></i>User-Specific Exports</h5>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <label for="userSelect" class="form-label">Select User:</label>
            <select id="userSelect" class="form-select" v-model="selectedUserId">
              <option value="">Select a user...</option>
              <option v-for="user in users" :key="user.id" :value="user.id">
                {{ user.username }} ({{ user.email }})
              </option>
            </select>
          </div>
          <div class="col-md-6 d-flex align-items-end">
            <button 
              class="btn btn-info" 
              @click="exportUserData"
              :disabled="!selectedUserId || isLoading"
            >
              <i class="fas fa-user-download me-1"></i>
              Export User Data
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Export History -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5><i class="fas fa-history me-2"></i>Export History</h5>
        <span class="badge bg-secondary">{{ exports.length }} exports</span>
      </div>
      <div class="card-body">
        <div v-if="exports.length === 0" class="text-center text-muted py-4">
          <i class="fas fa-inbox fa-3x mb-3"></i>
          <p>No exports generated yet</p>
        </div>
        <div v-else>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Export Type</th>
                  <th>Status</th>
                  <th>Generated</th>
                  <th>File Size</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="exportItem in sortedExports" :key="exportItem.id">
                  <td>
                    <i :class="getExportIcon(exportItem.type)" class="me-2"></i>
                    {{ exportItem.name }}
                  </td>
                  <td>
                    <span :class="getStatusBadgeClass(exportItem.status)" class="badge">
                      <i :class="getStatusIcon(exportItem.status)" class="me-1"></i>
                      {{ exportItem.status }}
                    </span>
                  </td>
                  <td>{{ formatTime(exportItem.createdAt) }}</td>
                  <td>
                    <span v-if="exportItem.fileSize" class="text-muted">
                      {{ formatFileSize(exportItem.fileSize) }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <button 
                      v-if="exportItem.status === 'completed' && exportItem.downloadUrl"
                      class="btn btn-sm btn-outline-primary"
                      @click="downloadExport(exportItem)"
                    >
                      <i class="fas fa-download me-1"></i>Download
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
  </div>
</template>

<script>
import { ref, computed, onMounted, getCurrentInstance } from 'vue'
import api from '@/services/api'

export default {
  name: 'DataExports',
  setup() {
    const instance = getCurrentInstance()
    const exports = ref([])
    const users = ref([])
    const selectedUserId = ref('')
    const isLoading = ref(false)
    const exportIdCounter = ref(1)

    const sortedExports = computed(() => {
      return [...exports.value].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    })

    const addExport = (name, type) => {
      const exportItem = {
        id: exportIdCounter.value++,
        name,
        type,
        status: 'generating',
        createdAt: new Date().toISOString(),
        fileSize: null,
        downloadUrl: null
      }
      exports.value.unshift(exportItem)
      return exportItem
    }

    const updateExport = (exportId, updates) => {
      const exportIndex = exports.value.findIndex(e => e.id === exportId)
      if (exportIndex !== -1) {
        exports.value[exportIndex] = { ...exports.value[exportIndex], ...updates }
      }
    }

    const exportAllData = async () => {
      if (isLoading.value) return
      
      isLoading.value = true
      const exportItem = addExport('All Data Export', 'all_data')
      
      // Show toast notification
      if (instance?.parent?.ctx?.showToast) {
        instance.parent.ctx.showToast('Starting all data export...', 'info')
      }
      
      try {
        const response = await api.get('/admin/export-all-data', {
          responseType: 'blob'
        })
        
        // Create download link
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `quiz_master_all_data_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        updateExport(exportItem.id, {
          status: 'completed',
          fileSize: blob.size,
          downloadUrl: url
        })
        
        if (instance?.parent?.ctx?.showToast) {
          instance.parent.ctx.showToast('All data exported successfully!', 'success')
        }
      } catch (error) {
        updateExport(exportItem.id, {
          status: 'failed'
        })
        
        if (instance?.parent?.ctx?.showToast) {
          instance.parent.ctx.showToast('Failed to export all data', 'error')
        }
      } finally {
        isLoading.value = false
      }
    }

    const exportAnalytics = async () => {
      if (isLoading.value) return
      
      isLoading.value = true
      const exportItem = addExport('Analytics Export', 'analytics')
      
      // Show toast notification
      if (instance?.parent?.ctx?.showToast) {
        instance.parent.ctx.showToast('Starting analytics export...', 'info')
      }
      
      try {
        const response = await api.get('/admin/export-analytics', {
          responseType: 'blob'
        })
        
        // Create download link
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `quiz_master_analytics_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        updateExport(exportItem.id, {
          status: 'completed',
          fileSize: blob.size,
          downloadUrl: url
        })
        
        if (instance?.parent?.ctx?.showToast) {
          instance.parent.ctx.showToast('Analytics exported successfully!', 'success')
        }
      } catch (error) {
        updateExport(exportItem.id, {
          status: 'failed'
        })
        
        if (instance?.parent?.ctx?.showToast) {
          instance.parent.ctx.showToast('Failed to export analytics', 'error')
        }
      } finally {
        isLoading.value = false
      }
    }

    const exportUserData = async () => {
      if (isLoading.value || !selectedUserId.value) return
      
      isLoading.value = true
      const user = users.value.find(u => u.id === parseInt(selectedUserId.value))
      const exportItem = addExport(`User Data: ${user?.username || 'Unknown'}`, 'user_data')
      
      // Show toast notification
      if (instance?.parent?.ctx?.showToast) {
        instance.parent.ctx.showToast(`Starting export for user ${user?.username}...`, 'info')
      }
      
      try {
        const response = await api.get(`/admin/export-user-data/${selectedUserId.value}`, {
          responseType: 'blob'
        })
        
        // Create download link
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `quiz_master_user_${user?.username}_${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        updateExport(exportItem.id, {
          status: 'completed',
          fileSize: blob.size,
          downloadUrl: url
        })
        
        if (instance?.parent?.ctx?.showToast) {
          instance.parent.ctx.showToast(`User data for ${user?.username} exported successfully!`, 'success')
        }
      } catch (error) {
        updateExport(exportItem.id, {
          status: 'failed'
        })
        
        if (instance?.parent?.ctx?.showToast) {
          instance.parent.ctx.showToast(`Failed to export user data for ${user?.username}`, 'error')
        }
      } finally {
        isLoading.value = false
      }
    }

    const downloadExport = (exportItem) => {
      if (exportItem.downloadUrl) {
        const link = document.createElement('a')
        link.href = exportItem.downloadUrl
        link.download = `${exportItem.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    }

    const refreshExports = () => {
      // In a real app, this would fetch exports from the server
      console.log('Refreshing exports...')
    }

    const loadUsers = async () => {
      try {
        const response = await api.get('/admin/users')
        users.value = response.data.users
      } catch (error) {
        console.error('Failed to load users:', error)
      }
    }

    const getExportIcon = (type) => {
      switch (type) {
        case 'all_data': return 'fas fa-database text-primary'
        case 'analytics': return 'fas fa-chart-bar text-success'
        case 'user_data': return 'fas fa-user text-info'
        default: return 'fas fa-file text-secondary'
      }
    }

    const getStatusBadgeClass = (status) => {
      switch (status) {
        case 'generating': return 'bg-warning'
        case 'completed': return 'bg-success'
        case 'failed': return 'bg-danger'
        default: return 'bg-secondary'
      }
    }

    const getStatusIcon = (status) => {
      switch (status) {
        case 'generating': return 'fas fa-spinner fa-spin'
        case 'completed': return 'fas fa-check'
        case 'failed': return 'fas fa-times'
        default: return 'fas fa-question'
      }
    }

    const formatTime = (isoString) => {
      return new Date(isoString).toLocaleString()
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    onMounted(() => {
      loadUsers()
      
      // Load any existing export history from localStorage
      const savedExports = localStorage.getItem('adminExportHistory')
      if (savedExports) {
        try {
          exports.value = JSON.parse(savedExports)
          exportIdCounter.value = Math.max(...exports.value.map(e => e.id), 0) + 1
        } catch (e) {
          console.error('Failed to load export history:', e)
        }
      }
    })

    return {
      exports,
      sortedExports,
      users,
      selectedUserId,
      isLoading,
      exportAllData,
      exportAnalytics,
      exportUserData,
      downloadExport,
      refreshExports,
      getExportIcon,
      getStatusBadgeClass,
      getStatusIcon,
      formatTime,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.data-exports {
  padding: 20px;
}

.card {
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.btn-group .btn {
  border-radius: 0.375rem;
  margin-left: 0.5rem;
}

.btn-group .btn:first-child {
  margin-left: 0;
}

.badge {
  font-size: 0.75em;
}

.text-muted {
  color: #6c757d !important;
}

.fa-spin {
  animation: fa-spin 1s infinite linear;
}

@keyframes fa-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>