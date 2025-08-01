<template>
  <div class="real-time-events">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">
        <i class="fas fa-satellite-dish me-2 text-primary"></i>
        Real-Time Events
      </h2>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary btn-sm" @click="refreshEvents">
          <i class="fas fa-sync-alt me-1" :class="{ 'fa-spin': isRefreshing }"></i>
          Refresh
        </button>
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" id="autoRefresh" v-model="autoRefresh">
          <label class="form-check-label" for="autoRefresh">
            Auto-refresh
          </label>
        </div>
      </div>
    </div>

    <!-- Event Filters -->
    <div class="event-filters mb-4">
      <div class="row">
        <div class="col-md-6">
          <label class="form-label">Filter by Type:</label>
          <select class="form-select" v-model="selectedEventType">
            <option value="all">All Events</option>
            <option value="quiz_attempt">Quiz Attempts</option>
            <option value="user_registration">User Registrations</option>
            <option value="content_creation">Content Creation</option>
            <option value="system_task">System Tasks</option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">Time Range:</label>
          <select class="form-select" v-model="timeRange">
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Live Status Indicator -->
    <div class="live-status mb-3">
      <div class="d-flex align-items-center">
        <div class="live-indicator me-2">
          <span class="badge bg-success">
            <i class="fas fa-circle fa-xs me-1 blink"></i>
            LIVE
          </span>
        </div>
        <small class="text-muted">
          Last updated: {{ formatTime(lastUpdated) }}
        </small>
      </div>
    </div>

    <!-- Events List -->
    <div class="events-container">
      <div v-if="isLoading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading events...</span>
        </div>
        <p class="mt-2 text-muted">Loading real-time events...</p>
      </div>

      <div v-else-if="filteredEvents.length === 0" class="text-center py-5">
        <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
        <h5 class="text-muted">No events found</h5>
        <p class="text-muted">No events match your current filters.</p>
      </div>

      <div v-else class="events-list">
        <div v-for="event in filteredEvents" :key="event.id" 
             class="event-item card mb-3 border-start border-4"
             :class="getEventBorderClass(event.type)">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <div class="event-content flex-grow-1">
                <div class="d-flex align-items-center mb-2">
                  <i :class="getEventIcon(event.type)" class="me-2"></i>
                  <span class="badge" :class="getEventBadgeClass(event.type)">{{ getEventTypeLabel(event.type) }}</span>
                  <small class="text-muted ms-auto">{{ formatTime(event.timestamp) }}</small>
                </div>
                <h6 class="event-title mb-1">{{ event.title }}</h6>
                <p class="event-description mb-2 text-muted">{{ event.description }}</p>
                <div v-if="event.metadata" class="event-metadata">
                  <small class="text-muted">
                    <span v-for="(value, key) in event.metadata" :key="key" class="me-3">
                      <strong>{{ formatMetadataKey(key) }}:</strong> {{ value }}
                    </span>
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Load More Button -->
    <div v-if="hasMoreEvents" class="text-center mt-4">
      <button class="btn btn-outline-primary" @click="loadMoreEvents" :disabled="isLoadingMore">
        <span v-if="isLoadingMore" class="spinner-border spinner-border-sm me-2"></span>
        {{ isLoadingMore ? 'Loading...' : 'Load More Events' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import api from '../services/api'

export default {
  name: 'RealTimeEvents',
  setup() {
    // Reactive data
    const events = ref([])
    const isLoading = ref(true)
    const isRefreshing = ref(false)
    const isLoadingMore = ref(false)
    const autoRefresh = ref(true)
    const selectedEventType = ref('all')
    const timeRange = ref('24h')
    const lastUpdated = ref(new Date())
    const hasMoreEvents = ref(true)
    const currentPage = ref(1)
    let refreshInterval = null

    // Computed properties
    const filteredEvents = computed(() => {
      let filtered = events.value
      
      if (selectedEventType.value !== 'all') {
        filtered = filtered.filter(event => event.type === selectedEventType.value)
      }
      
      const now = new Date()
      const timeRangeMs = {
        '1h': 60 * 60 * 1000,
        '6h': 6 * 60 * 60 * 1000,
        '24h': 24 * 60 * 60 * 1000,
        '7d': 7 * 24 * 60 * 60 * 1000
      }
      
      const cutoff = new Date(now - timeRangeMs[timeRange.value])
      filtered = filtered.filter(event => new Date(event.timestamp) >= cutoff)
      
      return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    })

    // Methods
    const fetchEvents = async (page = 1, append = false) => {
      try {
        if (!append) {
          isLoading.value = true
        } else {
          isLoadingMore.value = true
        }
        
        const response = await api.get('/admin/events', {
          params: {
            page,
            limit: 20,
            type: selectedEventType.value !== 'all' ? selectedEventType.value : undefined,
            timeRange: timeRange.value
          }
        })
        
        if (append) {
          events.value.push(...response.data.events)
        } else {
          events.value = response.data.events
        }
        
        hasMoreEvents.value = response.data.hasMore
        currentPage.value = page
        lastUpdated.value = new Date()
        
      } catch (error) {
        console.error('Error fetching events:', error)
        // Generate mock data for demonstration
        if (!append) {
          events.value = generateMockEvents()
        }
      } finally {
        isLoading.value = false
        isLoadingMore.value = false
      }
    }

    const refreshEvents = async () => {
      isRefreshing.value = true
      await fetchEvents(1, false)
      isRefreshing.value = false
    }

    const loadMoreEvents = () => {
      fetchEvents(currentPage.value + 1, true)
    }

    const generateMockEvents = () => {
      const mockEvents = []
      const eventTypes = ['quiz_attempt', 'user_registration', 'content_creation', 'system_task']
      const now = new Date()
      
      for (let i = 0; i < 15; i++) {
        const type = eventTypes[Math.floor(Math.random() * eventTypes.length)]
        const timestamp = new Date(now - Math.random() * 24 * 60 * 60 * 1000)
        
        let event = {
          id: i + 1,
          type,
          timestamp: timestamp.toISOString()
        }
        
        switch (type) {
          case 'quiz_attempt':
            event.title = `Quiz Attempt Completed`
            event.description = `User ${['Alice', 'Bob', 'Charlie', 'Diana'][Math.floor(Math.random() * 4)]} completed "${['JavaScript Basics', 'Python Fundamentals', 'Data Structures', 'Algorithms'][Math.floor(Math.random() * 4)]}"`
            event.metadata = {
              score: `${Math.floor(Math.random() * 10) + 1}/10`,
              duration: `${Math.floor(Math.random() * 30) + 5} minutes`
            }
            break
          case 'user_registration':
            event.title = `New User Registration`
            event.description = `User ${['john.doe', 'jane.smith', 'mike.wilson', 'sarah.jones'][Math.floor(Math.random() * 4)]} registered`
            event.metadata = {
              email: 'user@example.com',
              role: 'Student'
            }
            break
          case 'content_creation':
            event.title = `Content Created`
            event.description = `New ${['quiz', 'subject', 'chapter'][Math.floor(Math.random() * 3)]} "${['Advanced Topics', 'Introduction', 'Practice Set'][Math.floor(Math.random() * 3)]}" created`
            event.metadata = {
              author: 'Admin',
              category: 'Programming'
            }
            break
          case 'system_task':
            event.title = `System Task Executed`
            event.description = `${['Daily reminder', 'Monthly report', 'Data backup', 'Cache cleanup'][Math.floor(Math.random() * 4)]} task completed`
            event.metadata = {
              status: 'Success',
              duration: `${Math.floor(Math.random() * 5) + 1}s`
            }
            break
        }
        
        mockEvents.push(event)
      }
      
      return mockEvents
    }

    const getEventIcon = (type) => {
      switch (type) {
        case 'quiz_attempt': return 'fas fa-clipboard-check text-success'
        case 'user_registration': return 'fas fa-user-plus text-info'
        case 'content_creation': return 'fas fa-plus-circle text-primary'
        case 'system_task': return 'fas fa-cog text-warning'
        default: return 'fas fa-circle text-secondary'
      }
    }

    const getEventBorderClass = (type) => {
      switch (type) {
        case 'quiz_attempt': return 'border-success'
        case 'user_registration': return 'border-info'
        case 'content_creation': return 'border-primary'
        case 'system_task': return 'border-warning'
        default: return 'border-secondary'
      }
    }

    const getEventBadgeClass = (type) => {
      switch (type) {
        case 'quiz_attempt': return 'bg-success'
        case 'user_registration': return 'bg-info'
        case 'content_creation': return 'bg-primary'
        case 'system_task': return 'bg-warning'
        default: return 'bg-secondary'
      }
    }

    const getEventTypeLabel = (type) => {
      switch (type) {
        case 'quiz_attempt': return 'Quiz Attempt'
        case 'user_registration': return 'User Registration'
        case 'content_creation': return 'Content Creation'
        case 'system_task': return 'System Task'
        default: return 'Unknown'
      }
    }

    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) return 'Just now'
      if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
    }

    const formatMetadataKey = (key) => {
      return key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')
    }

    // Watchers
    watch([selectedEventType, timeRange], () => {
      fetchEvents(1, false)
    })

    watch(autoRefresh, (newValue) => {
      if (newValue) {
        refreshInterval = setInterval(refreshEvents, 15000) // Refresh every 15 seconds
      } else {
        if (refreshInterval) {
          clearInterval(refreshInterval)
          refreshInterval = null
        }
      }
    })

    // Lifecycle
    onMounted(() => {
      fetchEvents()
      if (autoRefresh.value) {
        refreshInterval = setInterval(refreshEvents, 15000)
      }
    })

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval)
      }
    })

    return {
      events,
      filteredEvents,
      isLoading,
      isRefreshing,
      isLoadingMore,
      autoRefresh,
      selectedEventType,
      timeRange,
      lastUpdated,
      hasMoreEvents,
      refreshEvents,
      loadMoreEvents,
      getEventIcon,
      getEventBorderClass,
      getEventBadgeClass,
      getEventTypeLabel,
      formatTime,
      formatMetadataKey
    }
  }
}
</script>

<style scoped>
.real-time-events {
  max-width: 1200px;
}

.live-indicator .blink {
  animation: blink 2s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}

.event-item {
  transition: all 0.3s ease;
  border-left-width: 4px !important;
}

.event-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.events-container {
  max-height: 800px;
  overflow-y: auto;
}

.event-filters {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
}

.form-check-input:checked {
  background-color: #198754;
  border-color: #198754;
}
</style>