<template>
  <div class="export-button-container">
    <!-- Export Button -->
    <button 
      @click="triggerExport" 
      :disabled="isExporting || isPolling"
      :class="[
        'export-btn',
        {
          'export-btn--loading': isExporting || isPolling,
          'export-btn--admin': exportType === 'admin',
          'export-btn--user': exportType === 'user'
        }
      ]"
    >
      <div class="export-btn__content">
        <svg v-if="!isExporting && !isPolling" class="export-btn__icon" viewBox="0 0 24 24">
          <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
        </svg>
        
        <div v-if="isExporting || isPolling" class="export-btn__spinner"></div>
        
        <span class="export-btn__text">
          {{ buttonText }}
        </span>
      </div>
    </button>

    <!-- Progress Bar -->
    <div v-if="isPolling && progress > 0" class="export-progress">
      <div class="export-progress__bar">
        <div 
          class="export-progress__fill" 
          :style="{ width: progress + '%' }"
        ></div>
      </div>
      <span class="export-progress__text">{{ progress }}%</span>
    </div>

    <!-- Status Messages -->
    <div v-if="statusMessage" :class="[
      'export-status',
      {
        'export-status--success': exportStatus === 'SUCCESS',
        'export-status--error': exportStatus === 'FAILURE',
        'export-status--info': exportStatus === 'PENDING' || exportStatus === 'PROGRESS'
      }
    ]">
      {{ statusMessage }}
    </div>

    <!-- Download Link -->
    <div v-if="downloadUrl" class="export-download">
      <a 
        :href="downloadUrl" 
        @click="handleDownload"
        class="export-download__link"
        download
      >
        <svg class="export-download__icon" viewBox="0 0 24 24">
          <path d="M5,20H19V18H5M19,9H15V3H9V9H5L12,16L19,9Z" />
        </svg>
        Download CSV File
      </a>
    </div>
  </div>
</template>

<script>
import { ref, computed, onUnmounted } from 'vue'
import axios from 'axios'

export default {
  name: 'ExportButton',
  props: {
    exportType: {
      type: String,
      required: true,
      validator: (value) => ['admin', 'user'].includes(value)
    },
    label: {
      type: String,
      default: ''
    }
  },
  emits: ['export-started', 'export-completed', 'export-failed'],
  setup(props, { emit }) {
    const isExporting = ref(false)
    const isPolling = ref(false)
    const progress = ref(0)
    const exportStatus = ref('')
    const statusMessage = ref('')
    const downloadUrl = ref('')
    const currentTaskId = ref('')
    const pollingInterval = ref(null)

    const buttonText = computed(() => {
      if (isExporting.value) {
        return 'Starting Export...'
      }
      if (isPolling.value) {
        return 'Generating CSV...'
      }
      if (props.label) {
        return props.label
      }
      return props.exportType === 'admin' ? 'Export User Data' : 'Export My Quiz History'
    })

    const triggerExport = async () => {
      try {
        isExporting.value = true
        statusMessage.value = ''
        downloadUrl.value = ''
        progress.value = 0

        const endpoint = props.exportType === 'admin' 
          ? '/api/export/admin-data'
          : '/api/export/user-history'

        const response = await axios.post(endpoint)
        
        if (response.data.success) {
          currentTaskId.value = response.data.task_id
          statusMessage.value = response.data.message
          
          emit('export-started', {
            taskId: response.data.task_id,
            type: props.exportType
          })
          
          // Start polling for status
          startPolling()
        } else {
          throw new Error(response.data.message || 'Export failed')
        }
      } catch (error) {
        console.error('Export error:', error)
        statusMessage.value = error.response?.data?.message || error.message || 'Export failed'
        exportStatus.value = 'FAILURE'
        
        emit('export-failed', {
          error: error.message,
          type: props.exportType
        })
      } finally {
        isExporting.value = false
      }
    }

    const startPolling = () => {
      isPolling.value = true
      
      pollingInterval.value = setInterval(async () => {
        try {
          const response = await axios.get(`/api/export/status/${currentTaskId.value}`)
          const data = response.data
          
          exportStatus.value = data.state
          progress.value = data.progress || 0
          statusMessage.value = data.status
          
          if (data.state === 'SUCCESS') {
            stopPolling()
            
            if (data.result && data.result.filename) {
              downloadUrl.value = `/api/export/download/${data.result.filename}`
              statusMessage.value = 'Export completed! Click below to download.'
            }
            
            emit('export-completed', {
              taskId: currentTaskId.value,
              result: data.result,
              type: props.exportType
            })
          } else if (data.state === 'FAILURE') {
            stopPolling()
            statusMessage.value = data.status || 'Export failed'
            
            emit('export-failed', {
              error: data.error || 'Export failed',
              type: props.exportType
            })
          }
        } catch (error) {
          console.error('Polling error:', error)
          stopPolling()
          statusMessage.value = 'Error checking export status'
          exportStatus.value = 'FAILURE'
        }
      }, 2000) // Poll every 2 seconds
    }

    const stopPolling = () => {
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value)
        pollingInterval.value = null
      }
      isPolling.value = false
    }

    const handleDownload = () => {
      // Add token to download request
      const token = localStorage.getItem('token')
      if (token) {
        // Create a temporary link with authorization header
        const link = document.createElement('a')
        link.href = downloadUrl.value
        link.download = ''
        
        // Add authorization header by making an axios request
        axios.get(downloadUrl.value, {
          responseType: 'blob',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }).then(response => {
          const url = window.URL.createObjectURL(new Blob([response.data]))
          const link = document.createElement('a')
          link.href = url
          
          // Extract filename from response headers or use default
          const contentDisposition = response.headers['content-disposition']
          let filename = 'export.csv'
          if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
            if (filenameMatch) {
              filename = filenameMatch[1]
            }
          }
          
          link.setAttribute('download', filename)
          document.body.appendChild(link)
          link.click()
          link.remove()
          window.URL.revokeObjectURL(url)
        }).catch(error => {
          console.error('Download error:', error)
          statusMessage.value = 'Download failed'
        })
      }
    }

    // Cleanup on unmount
    onUnmounted(() => {
      stopPolling()
    })

    return {
      isExporting,
      isPolling,
      progress,
      exportStatus,
      statusMessage,
      downloadUrl,
      buttonText,
      triggerExport,
      handleDownload
    }
  }
}
</script>

<style scoped>
.export-button-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 300px;
}

.export-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 44px;
}

.export-btn--user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.export-btn--admin {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.export-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.export-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.export-btn--loading {
  pointer-events: none;
}

.export-btn__content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.export-btn__icon {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.export-btn__spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.export-btn__text {
  font-size: 14px;
}

.export-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.export-progress__bar {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.export-progress__fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.export-progress__text {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  min-width: 35px;
}

.export-status {
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

.export-status--success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.export-status--error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.export-status--info {
  background: #dbeafe;
  color: #1e40af;
  border: 1px solid #93c5fd;
}

.export-download {
  display: flex;
  justify-content: center;
}

.export-download__link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #10b981;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.export-download__link:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.export-download__icon {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

/* Responsive Design */
@media (max-width: 768px) {
  .export-button-container {
    max-width: 100%;
  }
  
  .export-btn {
    padding: 10px 16px;
    font-size: 13px;
  }
  
  .export-btn__text {
    font-size: 13px;
  }
}
</style>