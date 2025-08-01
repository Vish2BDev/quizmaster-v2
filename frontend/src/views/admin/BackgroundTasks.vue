<template>
  <div class="background-tasks">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="fas fa-cogs me-2"></i>Background Tasks</h2>
      <div class="btn-group">
        <button class="btn btn-outline-primary" @click="refreshTasks">
          <i class="fas fa-sync-alt me-1"></i>Refresh
        </button>
        <button class="btn btn-outline-secondary" @click="clearHistory">
          <i class="fas fa-trash me-1"></i>Clear History
        </button>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5><i class="fas fa-bell me-2"></i>Daily Reminders</h5>
          </div>
          <div class="card-body">
            <p class="text-muted">Send daily quiz reminders to all active users</p>
            <button 
              class="btn btn-primary" 
              @click="triggerDailyReminder"
              :disabled="isLoading"
            >
              <i class="fas fa-paper-plane me-1"></i>
              {{ isLoading ? 'Sending...' : 'Send Daily Reminder' }}
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5><i class="fas fa-chart-line me-2"></i>Monthly Reports</h5>
          </div>
          <div class="card-body">
            <p class="text-muted">Generate monthly performance reports for all users</p>
            <button 
              class="btn btn-success" 
              @click="triggerMonthlyReport"
              :disabled="isLoading"
            >
              <i class="fas fa-file-alt me-1"></i>
              {{ isLoading ? 'Generating...' : 'Generate Monthly Report' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Task History -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5><i class="fas fa-history me-2"></i>Task History</h5>
        <span class="badge bg-secondary">{{ tasks.length }} tasks</span>
      </div>
      <div class="card-body">
        <div v-if="tasks.length === 0" class="text-center text-muted py-4">
          <i class="fas fa-inbox fa-3x mb-3"></i>
          <p>No tasks executed yet</p>
        </div>
        <div v-else>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Task</th>
                  <th>Status</th>
                  <th>Started</th>
                  <th>Duration</th>
                  <th>Result</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="task in sortedTasks" :key="task.id">
                  <td>
                    <i :class="getTaskIcon(task.type)" class="me-2"></i>
                    {{ task.name }}
                  </td>
                  <td>
                    <span :class="getStatusBadgeClass(task.status)" class="badge">
                      <i :class="getStatusIcon(task.status)" class="me-1"></i>
                      {{ task.status }}
                    </span>
                  </td>
                  <td>{{ formatTime(task.startTime) }}</td>
                  <td>
                    <span v-if="task.endTime">
                      {{ getDuration(task.startTime, task.endTime) }}
                    </span>
                    <span v-else-if="task.status === 'running'" class="text-muted">
                      <i class="fas fa-spinner fa-spin me-1"></i>Running...
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <span v-if="task.result" class="text-success">
                      {{ task.result }}
                    </span>
                    <span v-else-if="task.error" class="text-danger">
                      {{ task.error }}
                    </span>
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
  name: 'BackgroundTasks',
  setup() {
    const instance = getCurrentInstance()
    const tasks = ref([])
    const isLoading = ref(false)
    const taskIdCounter = ref(1)

    const sortedTasks = computed(() => {
      return [...tasks.value].sort((a, b) => new Date(b.startTime) - new Date(a.startTime))
    })

    const addTask = (name, type) => {
      const task = {
        id: taskIdCounter.value++,
        name,
        type,
        status: 'running',
        startTime: new Date().toISOString(),
        endTime: null,
        result: null,
        error: null
      }
      tasks.value.unshift(task)
      return task
    }

    const updateTask = (taskId, updates) => {
      const taskIndex = tasks.value.findIndex(t => t.id === taskId)
      if (taskIndex !== -1) {
        tasks.value[taskIndex] = { ...tasks.value[taskIndex], ...updates }
      }
    }

    const triggerDailyReminder = async () => {
      if (isLoading.value) return
      
      isLoading.value = true
      const task = addTask('Daily Quiz Reminder', 'reminder')
      
      // Show toast notification
      if (instance?.parent?.ctx?.showToast) {
        instance.parent.ctx.showToast('Daily reminder task started', 'info')
      }
      
      try {
        const response = await api.post('/admin/test-daily-reminder')
        
        updateTask(task.id, {
          status: 'success',
          endTime: new Date().toISOString(),
          result: response.data.message || 'Daily reminders sent successfully'
        })
        
        if (instance?.parent?.ctx?.showToast) {
          instance.parent.ctx.showToast('Daily reminders sent successfully!', 'success')
        }
      } catch (error) {
        updateTask(task.id, {
          status: 'error',
          endTime: new Date().toISOString(),
          error: error.response?.data?.error || 'Failed to send daily reminders'
        })
        
        if (instance?.parent?.ctx?.showToast) {
          instance.parent.ctx.showToast('Failed to send daily reminders', 'error')
        }
      } finally {
        isLoading.value = false
      }
    }

    const triggerMonthlyReport = async () => {
      if (isLoading.value) return
      
      isLoading.value = true
      const task = addTask('Monthly Performance Report', 'report')
      
      // Show toast notification
      if (instance?.parent?.ctx?.showToast) {
        instance.parent.ctx.showToast('Monthly report generation started', 'info')
      }
      
      try {
        const response = await api.post('/admin/test-monthly-report')
        
        updateTask(task.id, {
          status: 'success',
          endTime: new Date().toISOString(),
          result: `Report generated: ${response.data.total_users} users, ${response.data.total_attempts} attempts`
        })
        
        if (instance?.parent?.ctx?.showToast) {
          instance.parent.ctx.showToast('Monthly report generated successfully!', 'success')
        }
      } catch (error) {
        updateTask(task.id, {
          status: 'error',
          endTime: new Date().toISOString(),
          error: error.response?.data?.error || 'Failed to generate monthly report'
        })
        
        if (instance?.parent?.ctx?.showToast) {
          instance.parent.ctx.showToast('Failed to generate monthly report', 'error')
        }
      } finally {
        isLoading.value = false
      }
    }

    const refreshTasks = () => {
      // In a real app, this would fetch tasks from the server
      console.log('Refreshing tasks...')
    }

    const clearHistory = () => {
      tasks.value = []
      if (instance?.parent?.ctx?.showToast) {
        instance.parent.ctx.showToast('Task history cleared', 'info')
      }
    }

    const getTaskIcon = (type) => {
      switch (type) {
        case 'reminder': return 'fas fa-bell text-primary'
        case 'report': return 'fas fa-chart-line text-success'
        case 'export': return 'fas fa-download text-info'
        default: return 'fas fa-cog text-secondary'
      }
    }

    const getStatusBadgeClass = (status) => {
      switch (status) {
        case 'running': return 'bg-warning'
        case 'success': return 'bg-success'
        case 'error': return 'bg-danger'
        default: return 'bg-secondary'
      }
    }

    const getStatusIcon = (status) => {
      switch (status) {
        case 'running': return 'fas fa-spinner fa-spin'
        case 'success': return 'fas fa-check'
        case 'error': return 'fas fa-times'
        default: return 'fas fa-question'
      }
    }

    const formatTime = (isoString) => {
      return new Date(isoString).toLocaleString()
    }

    const getDuration = (startTime, endTime) => {
      const start = new Date(startTime)
      const end = new Date(endTime)
      const diff = end - start
      return `${(diff / 1000).toFixed(1)}s`
    }

    onMounted(() => {
      // Load any existing task history from localStorage
      const savedTasks = localStorage.getItem('adminTaskHistory')
      if (savedTasks) {
        try {
          tasks.value = JSON.parse(savedTasks)
          taskIdCounter.value = Math.max(...tasks.value.map(t => t.id), 0) + 1
        } catch (e) {
          console.error('Failed to load task history:', e)
        }
      }
    })

    // Save tasks to localStorage whenever they change
    const saveTasksToStorage = () => {
      localStorage.setItem('adminTaskHistory', JSON.stringify(tasks.value))
    }

    // Watch for changes and save
    const unwatchTasks = ref(null)
    onMounted(() => {
      unwatchTasks.value = tasks.value
      // Simple reactive save - in a real app you'd use a proper watcher
      setInterval(() => {
        if (tasks.value !== unwatchTasks.value) {
          saveTasksToStorage()
          unwatchTasks.value = tasks.value
        }
      }, 1000)
    })

    return {
      tasks,
      sortedTasks,
      isLoading,
      triggerDailyReminder,
      triggerMonthlyReport,
      refreshTasks,
      clearHistory,
      getTaskIcon,
      getStatusBadgeClass,
      getStatusIcon,
      formatTime,
      getDuration
    }
  }
}
</script>

<style scoped>
.background-tasks {
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