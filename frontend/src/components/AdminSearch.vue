<template>
  <div class="admin-search">
    <!-- Search Header -->
    <div class="search-header">
      <h3 class="search-title">
        <i class="fas fa-search"></i>
        Admin Search
      </h3>
      <p class="search-subtitle">Search across users, subjects, quizzes, and questions</p>
      
      <!-- Admin Access Warning -->
      <div v-if="!canSearch" class="admin-warning">
        <i class="fas fa-exclamation-triangle"></i>
        <strong>Admin Access Required:</strong> You must be logged in as an administrator to use this search feature.
      </div>
    </div>

    <!-- Search Controls -->
    <div class="search-controls">
      <div class="search-input-group">
        <div class="input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Enter search keywords..."
            class="search-input"
            @input="debouncedSearch"
            @keyup.enter="performSearch"
          />
          <button
            v-if="searchQuery"
            @click="clearSearch"
            class="clear-btn"
            type="button"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="entity-selector">
          <select v-model="selectedEntity" @change="performSearch" class="entity-select">
            <option value="all">All Entities</option>
            <option value="user">Users</option>
            <option value="subject">Subjects</option>
            <option value="quiz">Quizzes</option>
            <option value="question">Questions</option>
          </select>
        </div>
        
        <button
          @click="performSearch"
          :disabled="!searchQuery.trim() || isLoading || !canSearch"
          class="search-btn"
          :title="!canSearch ? 'Admin access required' : ''"
        >
          <i class="fas fa-search" v-if="!isLoading"></i>
          <i class="fas fa-spinner fa-spin" v-else></i>
          Search
        </button>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="hasSearched" class="search-results">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner">
          <i class="fas fa-spinner fa-spin"></i>
        </div>
        <p>Searching...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h4>Search Error</h4>
        <p>{{ error }}</p>
        <button @click="performSearch" class="retry-btn">
          <i class="fas fa-redo"></i>
          Try Again
        </button>
      </div>

      <!-- Results -->
      <div v-else class="results-container">
        <!-- Results Summary -->
        <div class="results-summary">
          <h4>
            <i class="fas fa-chart-bar"></i>
            Search Results
            <span class="query-highlight">"{{ lastSearchQuery }}"</span>
          </h4>
          <p class="total-results">
            Found {{ totalResults }} result{{ totalResults !== 1 ? 's' : '' }}
            <span v-if="searchResults.metadata">
              ({{ searchResults.metadata.entity === 'all' ? 'all entities' : searchResults.metadata.entity }})
            </span>
          </p>
        </div>

        <!-- No Results -->
        <div v-if="totalResults === 0" class="no-results">
          <div class="no-results-icon">
            <i class="fas fa-search-minus"></i>
          </div>
          <h4>No Results Found</h4>
          <p>Try adjusting your search terms or selecting a different entity type.</p>
        </div>

        <!-- Results by Entity Type -->
        <div v-else class="results-sections">
          <!-- Users Results -->
          <div v-if="searchResults.users && searchResults.users.results.length > 0" class="result-section">
            <div class="section-header">
              <h5>
                <i class="fas fa-users"></i>
                Users ({{ searchResults.users.results.length }})
              </h5>
            </div>
            <div class="result-cards">
              <div
                v-for="user in searchResults.users.results"
                :key="'user-' + user.id"
                class="result-card user-card"
              >
                <div class="card-header">
                  <div class="card-icon">
                    <i class="fas fa-user"></i>
                  </div>
                  <div class="card-title">
                    <h6>{{ user.username }}</h6>
                    <span class="card-subtitle">{{ user.email }}</span>
                  </div>
                  <div class="card-badge">
                    <span :class="['role-badge', user.role]">
                      {{ user.role }}
                    </span>
                  </div>
                </div>
                <div class="card-content">
                  <div class="user-stats">
                    <div class="stat">
                      <span class="stat-label">Quiz Attempts:</span>
                      <span class="stat-value">{{ user.quiz_attempts_count || 0 }}</span>
                    </div>
                    <div class="stat">
                      <span class="stat-label">Joined:</span>
                      <span class="stat-value">{{ formatDate(user.created_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="searchResults.users.pagination.has_next" class="load-more">
              <button @click="loadMore('users')" class="load-more-btn">
                <i class="fas fa-chevron-down"></i>
                Load More Users
              </button>
            </div>
          </div>

          <!-- Subjects Results -->
          <div v-if="searchResults.subjects && searchResults.subjects.results.length > 0" class="result-section">
            <div class="section-header">
              <h5>
                <i class="fas fa-book"></i>
                Subjects ({{ searchResults.subjects.results.length }})
              </h5>
            </div>
            <div class="result-cards">
              <div
                v-for="subject in searchResults.subjects.results"
                :key="'subject-' + subject.id"
                class="result-card subject-card"
              >
                <div class="card-header">
                  <div class="card-icon">
                    <i class="fas fa-book-open"></i>
                  </div>
                  <div class="card-title">
                    <h6>{{ subject.name }}</h6>
                    <span class="card-subtitle">{{ subject.description || 'No description' }}</span>
                  </div>
                </div>
                <div class="card-content">
                  <div class="subject-stats">
                    <div class="stat">
                      <span class="stat-label">Chapters:</span>
                      <span class="stat-value">{{ subject.chapters_count || 0 }}</span>
                    </div>
                    <div class="stat">
                      <span class="stat-label">Created:</span>
                      <span class="stat-value">{{ formatDate(subject.created_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="searchResults.subjects.pagination.has_next" class="load-more">
              <button @click="loadMore('subjects')" class="load-more-btn">
                <i class="fas fa-chevron-down"></i>
                Load More Subjects
              </button>
            </div>
          </div>

          <!-- Quizzes Results -->
          <div v-if="searchResults.quizzes && searchResults.quizzes.results.length > 0" class="result-section">
            <div class="section-header">
              <h5>
                <i class="fas fa-question-circle"></i>
                Quizzes ({{ searchResults.quizzes.results.length }})
              </h5>
            </div>
            <div class="result-cards">
              <div
                v-for="quiz in searchResults.quizzes.results"
                :key="'quiz-' + quiz.id"
                class="result-card quiz-card"
              >
                <div class="card-header">
                  <div class="card-icon">
                    <i class="fas fa-clipboard-question"></i>
                  </div>
                  <div class="card-title">
                    <h6>{{ quiz.title }}</h6>
                    <span class="card-subtitle">{{ quiz.description || 'No description' }}</span>
                  </div>
                  <div class="card-badge">
                    <span :class="['status-badge', quiz.status]">
                      {{ quiz.status }}
                    </span>
                  </div>
                </div>
                <div class="card-content">
                  <div class="quiz-info">
                    <div class="info-row">
                      <span class="info-label">Subject:</span>
                      <span class="info-value">{{ quiz.subject.name }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">Chapter:</span>
                      <span class="info-value">{{ quiz.chapter.name }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">Questions:</span>
                      <span class="info-value">{{ quiz.questions_count }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">Duration:</span>
                      <span class="info-value">{{ quiz.duration_minutes }} min</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="searchResults.quizzes.pagination.has_next" class="load-more">
              <button @click="loadMore('quizzes')" class="load-more-btn">
                <i class="fas fa-chevron-down"></i>
                Load More Quizzes
              </button>
            </div>
          </div>

          <!-- Questions Results -->
          <div v-if="searchResults.questions && searchResults.questions.results.length > 0" class="result-section">
            <div class="section-header">
              <h5>
                <i class="fas fa-question"></i>
                Questions ({{ searchResults.questions.results.length }})
              </h5>
            </div>
            <div class="result-cards">
              <div
                v-for="question in searchResults.questions.results"
                :key="'question-' + question.id"
                class="result-card question-card"
              >
                <div class="card-header">
                  <div class="card-icon">
                    <i class="fas fa-question"></i>
                  </div>
                  <div class="card-title">
                    <h6>Question #{{ question.id }}</h6>
                  </div>
                </div>
                <div class="card-content">
                  <div class="question-text">
                    <p>{{ question.text }}</p>
                  </div>
                  <div class="question-context">
                    <div class="context-item">
                      <span class="context-label">Quiz:</span>
                      <span class="context-value">{{ question.quiz.title }}</span>
                    </div>
                    <div class="context-item">
                      <span class="context-label">Subject:</span>
                      <span class="context-value">{{ question.subject.name }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="searchResults.questions.pagination.has_next" class="load-more">
              <button @click="loadMore('questions')" class="load-more-btn">
                <i class="fas fa-chevron-down"></i>
                Load More Questions
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { debounce } from 'lodash'
import api from '@/services/api'
import { mapGetters } from 'vuex'

export default {
  name: 'AdminSearch',
  data() {
    return {
      searchQuery: '',
      selectedEntity: 'all',
      searchResults: {},
      isLoading: false,
      error: null,
      hasSearched: false,
      lastSearchQuery: '',
      currentPage: {
        users: 1,
        subjects: 1,
        quizzes: 1,
        questions: 1
      }
    }
  },
  computed: {
    ...mapGetters(['isAdmin', 'user']),
    totalResults() {
      if (!this.searchResults.metadata) return 0
      return this.searchResults.metadata.total_results || 0
    },
    canSearch() {
      return this.isAdmin && this.user
    }
  },
  created() {
    // Create debounced search function
    this.debouncedSearch = debounce(this.performSearch, 500)
  },
  methods: {
    async performSearch() {
      if (!this.searchQuery.trim()) {
        this.hasSearched = false
        this.searchResults = {}
        return
      }

      if (!this.canSearch) {
        this.error = 'Admin access required. Please log in as an administrator to use the search function.'
        this.hasSearched = true
        return
      }

      this.isLoading = true
      this.error = null
      this.hasSearched = true
      this.lastSearchQuery = this.searchQuery

      // Reset pagination
      this.currentPage = {
        users: 1,
        subjects: 1,
        quizzes: 1,
        questions: 1
      }

      try {
        const response = await api.get('/admin/search', {
          params: {
            keyword: this.searchQuery,
            entity: this.selectedEntity,
            page: 1,
            per_page: 10
          }
        })

        this.searchResults = response.data
      } catch (error) {
        console.error('Admin search error:', error)
        if (error.response?.status === 401) {
          this.error = 'Authentication required. Please log in as an admin.'
        } else if (error.response?.status === 403) {
          this.error = 'Admin access required. You do not have permission to perform this search.'
        } else {
          this.error = error.response?.data?.message || error.response?.data?.error || 'Search failed. Please try again.'
        }
        this.searchResults = {}
      } finally {
        this.isLoading = false
      }
    },

    async loadMore(entityType) {
      if (this.isLoading) return

      this.isLoading = true
      this.currentPage[entityType]++

      try {
        const response = await api.get('/admin/search', {
          params: {
            keyword: this.lastSearchQuery,
            entity: entityType,
            page: this.currentPage[entityType],
            per_page: 10
          }
        })

        // Append new results to existing ones
        if (response.data[entityType] && response.data[entityType].results) {
          this.searchResults[entityType].results.push(...response.data[entityType].results)
          this.searchResults[entityType].pagination = response.data[entityType].pagination
        }
      } catch (error) {
        console.error('Load more error:', error)
        this.currentPage[entityType]-- // Revert page increment
      } finally {
        this.isLoading = false
      }
    },

    clearSearch() {
      this.searchQuery = ''
      this.searchResults = {}
      this.hasSearched = false
      this.error = null
      this.lastSearchQuery = ''
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.admin-search {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-header {
  text-align: center;
  margin-bottom: 30px;
}

.search-title {
  color: #1a202c;
  margin-bottom: 8px;
  font-size: 1.8rem;
  font-weight: 600;
}

.search-title i {
  margin-right: 10px;
  color: #2563eb;
}

.search-subtitle {
  color: #4a5568;
  font-size: 1rem;
  margin: 0;
  font-weight: 500;
}

.admin-warning {
  margin-top: 20px;
  padding: 15px 20px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-warning i {
  color: #dc2626;
  font-size: 1.1rem;
}

.search-controls {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.search-input-group {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.input-wrapper {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #bdc3c7;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 12px 45px 12px 45px;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #ffffff;
  color: #1f2937;
}

.search-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.search-input::placeholder {
  color: #6b7280;
}

.clear-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #95a5a6;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: #ecf0f1;
  color: #7f8c8d;
}

.entity-selector {
  min-width: 150px;
}

.entity-select {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  background: #ffffff;
  color: #1f2937;
  cursor: pointer;
  transition: all 0.3s ease;
}

.entity-select:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.search-btn {
  padding: 12px 25px;
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.search-btn:hover:not(:disabled) {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.search-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.search-results {
  min-height: 200px;
}

.loading-state,
.error-state,
.no-results {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  font-size: 2rem;
  color: #2563eb;
  margin-bottom: 15px;
}

.error-icon {
  font-size: 3rem;
  color: #dc2626;
  margin-bottom: 15px;
}

.no-results-icon {
  font-size: 3rem;
  color: #6b7280;
  margin-bottom: 15px;
}

.retry-btn {
  margin-top: 15px;
  padding: 10px 20px;
  background: #dc2626;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.results-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.results-summary {
  padding: 25px;
  background: #f8f9fa;
  border-bottom: 1px solid #ecf0f1;
}

.results-summary h4 {
  margin: 0 0 8px 0;
  color: #111827;
  font-size: 1.3rem;
  font-weight: 700;
}

.query-highlight {
  color: #2563eb;
  font-weight: 600;
}

.total-results {
  margin: 0;
  color: #4b5563;
  font-weight: 500;
}

.results-sections {
  padding: 0;
}

.result-section {
  border-bottom: 1px solid #ecf0f1;
}

.result-section:last-child {
  border-bottom: none;
}

.section-header {
  padding: 20px 25px 15px;
  background: #f8f9fa;
}

.section-header h5 {
  margin: 0;
  color: #111827;
  font-size: 1.1rem;
  font-weight: 600;
}

.section-header i {
  margin-right: 8px;
  color: #2563eb;
}

.result-cards {
  padding: 15px 25px;
  display: grid;
  gap: 15px;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}

.result-card {
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.3s ease;
  background: white;
}

.result-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.user-card .card-icon {
  background: #dbeafe;
  color: #1d4ed8;
}

.subject-card .card-icon {
  background: #dcfce7;
  color: #16a34a;
}

.quiz-card .card-icon {
  background: #fef3c7;
  color: #d97706;
}

.question-card .card-icon {
  background: #f3e8ff;
  color: #7c3aed;
}

.card-title {
  flex: 1;
}

.card-title h6 {
  margin: 0 0 4px 0;
  color: #111827;
  font-size: 1rem;
  font-weight: 600;
}

.card-subtitle {
  color: #4b5563;
  font-size: 0.9rem;
  display: block;
  margin-top: 2px;
  font-weight: 500;
}

.card-badge {
  flex-shrink: 0;
}

.role-badge,
.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.role-badge.admin {
  background: #e74c3c;
  color: white;
}

.role-badge.user {
  background: #3498db;
  color: white;
}

.status-badge.active {
  background: #27ae60;
  color: white;
}

.status-badge.upcoming {
  background: #f39c12;
  color: white;
}

.status-badge.expired {
  background: #95a5a6;
  color: white;
}

.card-content {
  font-size: 0.9rem;
}

.user-stats,
.subject-stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.8rem;
}

.stat-value {
  color: #2c3e50;
  font-weight: 500;
}

.quiz-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  color: #7f8c8d;
  font-size: 0.85rem;
}

.info-value {
  color: #2c3e50;
  font-weight: 500;
}

.question-text {
  margin-bottom: 12px;
}

.question-text p {
  margin: 0;
  color: #2c3e50;
  line-height: 1.5;
}

.question-context {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.context-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.context-label {
  color: #7f8c8d;
  font-size: 0.85rem;
}

.context-value {
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.85rem;
}

.load-more {
  padding: 15px 25px;
  text-align: center;
  border-top: 1px solid #ecf0f1;
}

.load-more-btn {
  padding: 10px 20px;
  background: #ecf0f1;
  color: #7f8c8d;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.load-more-btn:hover {
  background: #d5dbdb;
  color: #2c3e50;
}

@media (max-width: 768px) {
  .search-input-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .input-wrapper {
    min-width: auto;
  }
  
  .result-cards {
    grid-template-columns: 1fr;
  }
  
  .user-stats,
  .subject-stats {
    flex-direction: column;
    gap: 10px;
  }
}
</style>