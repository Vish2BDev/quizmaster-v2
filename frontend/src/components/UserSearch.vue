<template>
  <div class="user-search">
    <!-- Search Header -->
    <div class="search-header">
      <h3 class="search-title">
        <i class="fas fa-search"></i>
        Find Quizzes & Subjects
      </h3>
      <p class="search-subtitle">Discover quizzes and subjects that match your interests</p>
    </div>

    <!-- Search Controls -->
    <div class="search-controls">
      <div class="search-input-group">
        <div class="input-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search for quizzes, subjects, topics..."
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
        
        <div class="type-selector">
          <select v-model="selectedType" @change="performSearch" class="type-select">
            <option value="all">All Types</option>
            <option value="quiz">Quizzes</option>
            <option value="subject">Subjects</option>
          </select>
        </div>
        
        <button
          @click="performSearch"
          :disabled="!searchQuery.trim() || isLoading"
          class="search-btn"
        >
          <i class="fas fa-search" v-if="!isLoading"></i>
          <i class="fas fa-spinner fa-spin" v-else></i>
          Search
        </button>
      </div>

      <!-- Search Suggestions -->
      <div v-if="showSuggestions && suggestions.length > 0" class="suggestions-dropdown">
        <div class="suggestions-header">
          <span>Suggestions</span>
        </div>
        <div
          v-for="(suggestion, index) in suggestions"
          :key="index"
          @click="applySuggestion(suggestion)"
          class="suggestion-item"
        >
          <i :class="getSuggestionIcon(suggestion.type)"></i>
          <span>{{ suggestion.text }}</span>
          <span class="suggestion-type">{{ suggestion.type }}</span>
        </div>
      </div>
    </div>

    <!-- Quick Filters -->
    <div v-if="hasSearched && !isLoading" class="quick-filters">
      <div class="filter-group">
        <span class="filter-label">Quick filters:</span>
        <button
          v-for="filter in quickFilters"
          :key="filter.value"
          @click="applyQuickFilter(filter)"
          :class="['filter-btn', { active: selectedType === filter.value }]"
        >
          <i :class="filter.icon"></i>
          {{ filter.label }}
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
        <p>Searching for content...</p>
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
              ({{ searchResults.metadata.type === 'all' ? 'all types' : searchResults.metadata.type }})
            </span>
          </p>
        </div>

        <!-- No Results -->
        <div v-if="totalResults === 0" class="no-results">
          <div class="no-results-icon">
            <i class="fas fa-search-minus"></i>
          </div>
          <h4>No Results Found</h4>
          <p>Try different keywords or browse our available content.</p>
          <div class="no-results-actions">
            <button @click="clearSearch" class="browse-btn">
              <i class="fas fa-compass"></i>
              Browse All Content
            </button>
          </div>
        </div>

        <!-- Results by Type -->
        <div v-else class="results-sections">
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
                @click="viewQuiz(quiz)"
              >
                <div class="card-header">
                  <div class="card-icon">
                    <i class="fas fa-clipboard-question"></i>
                  </div>
                  <div class="card-title">
                    <h6>{{ quiz.title }}</h6>
                    <span class="card-subtitle">{{ quiz.description || 'No description available' }}</span>
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
                      <span class="info-label">
                        <i class="fas fa-book"></i>
                        Subject:
                      </span>
                      <span class="info-value">{{ quiz.subject.name }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">
                        <i class="fas fa-bookmark"></i>
                        Chapter:
                      </span>
                      <span class="info-value">{{ quiz.chapter.name }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">
                        <i class="fas fa-question"></i>
                        Questions:
                      </span>
                      <span class="info-value">{{ quiz.questions_count }}</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">
                        <i class="fas fa-clock"></i>
                        Duration:
                      </span>
                      <span class="info-value">{{ quiz.duration_minutes }} minutes</span>
                    </div>
                  </div>
                </div>
                <div class="card-actions">
                  <button
                    v-if="quiz.status === 'active'"
                    @click.stop="startQuiz(quiz)"
                    class="action-btn primary"
                  >
                    <i class="fas fa-play"></i>
                    Start Quiz
                  </button>
                  <button
                    v-else-if="quiz.status === 'upcoming'"
                    disabled
                    class="action-btn disabled"
                  >
                    <i class="fas fa-clock"></i>
                    Coming Soon
                  </button>
                  <button
                    v-else
                    disabled
                    class="action-btn disabled"
                  >
                    <i class="fas fa-ban"></i>
                    Unavailable
                  </button>
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
                @click="viewSubject(subject)"
              >
                <div class="card-header">
                  <div class="card-icon">
                    <i class="fas fa-book-open"></i>
                  </div>
                  <div class="card-title">
                    <h6>{{ subject.name }}</h6>
                    <span class="card-subtitle">{{ subject.description || 'Explore this subject area' }}</span>
                  </div>
                </div>
                <div class="card-content">
                  <div class="subject-stats">
                    <div class="stat">
                      <div class="stat-icon">
                        <i class="fas fa-layer-group"></i>
                      </div>
                      <div class="stat-info">
                        <span class="stat-value">{{ subject.chapters_count || 0 }}</span>
                        <span class="stat-label">Chapters</span>
                      </div>
                    </div>
                    <div class="stat">
                      <div class="stat-icon">
                        <i class="fas fa-calendar-plus"></i>
                      </div>
                      <div class="stat-info">
                        <span class="stat-value">{{ formatDate(subject.created_at) }}</span>
                        <span class="stat-label">Added</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="card-actions">
                  <button @click.stop="exploreSubject(subject)" class="action-btn secondary">
                    <i class="fas fa-compass"></i>
                    Explore
                  </button>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { debounce } from 'lodash'
import api from '@/services/api'

export default {
  name: 'UserSearch',
  data() {
    return {
      searchQuery: '',
      selectedType: 'all',
      searchResults: {},
      isLoading: false,
      error: null,
      hasSearched: false,
      lastSearchQuery: '',
      suggestions: [],
      showSuggestions: false,
      currentPage: {
        quizzes: 1,
        subjects: 1
      },
      quickFilters: [
        { label: 'All', value: 'all', icon: 'fas fa-th' },
        { label: 'Quizzes', value: 'quiz', icon: 'fas fa-question-circle' },
        { label: 'Subjects', value: 'subject', icon: 'fas fa-book' }
      ]
    }
  },
  computed: {
    totalResults() {
      if (!this.searchResults.metadata) return 0
      return this.searchResults.metadata.total_results || 0
    }
  },
  created() {
    // Create debounced search function
    this.debouncedSearch = debounce(this.performSearch, 500)
    // Create debounced suggestions function
    this.debouncedSuggestions = debounce(this.fetchSuggestions, 300)
  },
  watch: {
    searchQuery(newQuery) {
      if (newQuery.length >= 1) {
        this.debouncedSuggestions()
      } else {
        this.suggestions = []
        this.showSuggestions = false
      }
    }
  },
  methods: {
    async performSearch() {
      if (!this.searchQuery.trim()) {
        this.hasSearched = false
        this.searchResults = {}
        return
      }

      this.isLoading = true
      this.error = null
      this.hasSearched = true
      this.lastSearchQuery = this.searchQuery
      this.showSuggestions = false

      // Reset pagination
      this.currentPage = {
        quizzes: 1,
        subjects: 1
      }

      try {
        const response = await api.get('/search', {
          params: {
            query: this.searchQuery,
            type: this.selectedType,
            page: 1,
            per_page: 12
          }
        })

        this.searchResults = response.data
      } catch (error) {
        console.error('Search error:', error)
        this.error = error.response?.data?.message || 'Search failed. Please try again.'
        this.searchResults = {}
      } finally {
        this.isLoading = false
      }
    },

    async fetchSuggestions() {
      if (!this.searchQuery.trim() || this.searchQuery.length < 1) {
        this.suggestions = []
        this.showSuggestions = false
        return
      }

      try {
        const response = await api.get('/search/suggestions', {
          params: {
            q: this.searchQuery,
            type: this.selectedType,
            limit: 5
          }
        })

        this.suggestions = response.data.suggestions || []
        this.showSuggestions = this.suggestions.length > 0
      } catch (error) {
        console.error('Suggestions error:', error)
        this.suggestions = []
        this.showSuggestions = false
      }
    },

    async loadMore(entityType) {
      if (this.isLoading) return

      this.isLoading = true
      this.currentPage[entityType]++

      try {
        const response = await api.get('/search', {
          params: {
            query: this.lastSearchQuery,
            type: entityType,
            page: this.currentPage[entityType],
            per_page: 12
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

    applySuggestion(suggestion) {
      this.searchQuery = suggestion.text
      this.selectedType = suggestion.type === 'quiz' ? 'quiz' : suggestion.type === 'subject' ? 'subject' : 'all'
      this.showSuggestions = false
      this.performSearch()
    },

    applyQuickFilter(filter) {
      this.selectedType = filter.value
      if (this.hasSearched) {
        this.performSearch()
      }
    },

    clearSearch() {
      this.searchQuery = ''
      this.searchResults = {}
      this.hasSearched = false
      this.error = null
      this.lastSearchQuery = ''
      this.suggestions = []
      this.showSuggestions = false
      this.selectedType = 'all'
    },

    getSuggestionIcon(type) {
      switch (type) {
        case 'quiz':
          return 'fas fa-question-circle'
        case 'subject':
          return 'fas fa-book'
        default:
          return 'fas fa-search'
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },

    // Navigation methods
    viewQuiz(quiz) {
      // Emit event or navigate to quiz details
      this.$emit('quiz-selected', quiz)
    },

    startQuiz(quiz) {
      // Emit event or navigate to start quiz
      this.$emit('start-quiz', quiz)
    },

    viewSubject(subject) {
      // Emit event or navigate to subject details
      this.$emit('subject-selected', subject)
    },

    exploreSubject(subject) {
      // Emit event or navigate to explore subject
      this.$emit('explore-subject', subject)
    }
  }
}
</script>

<style scoped>
.user-search {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.search-header {
  text-align: center;
  margin-bottom: 30px;
}

.search-title {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1.8rem;
}

.search-title i {
  margin-right: 10px;
  color: #3498db;
}

.search-subtitle {
  color: #7f8c8d;
  font-size: 1rem;
  margin: 0;
}

.search-controls {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  position: relative;
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
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
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

.type-selector {
  min-width: 130px;
}

.type-select {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-select:focus {
  outline: none;
  border-color: #3498db;
}

.search-btn {
  padding: 12px 25px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.search-btn:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
}

.search-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  transform: none;
}

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 25px;
  right: 25px;
  background: white;
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  margin-top: 5px;
}

.suggestions-header {
  padding: 10px 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #ecf0f1;
  font-size: 0.9rem;
  color: #7f8c8d;
  font-weight: 500;
}

.suggestion-item {
  padding: 12px 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid #f8f9fa;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background: #f8f9fa;
}

.suggestion-type {
  margin-left: auto;
  font-size: 0.8rem;
  color: #95a5a6;
  text-transform: uppercase;
}

.quick-filters {
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-label {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-right: 5px;
}

.filter-btn {
  padding: 8px 15px;
  background: #ecf0f1;
  color: #7f8c8d;
  border: none;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.filter-btn:hover {
  background: #d5dbdb;
  color: #2c3e50;
}

.filter-btn.active {
  background: #3498db;
  color: white;
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
  color: #3498db;
  margin-bottom: 15px;
}

.error-icon,
.no-results-icon {
  font-size: 3rem;
  color: #e74c3c;
  margin-bottom: 15px;
}

.no-results-icon {
  color: #95a5a6;
}

.retry-btn,
.browse-btn {
  margin-top: 15px;
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn {
  background: #e74c3c;
}

.retry-btn:hover {
  background: #c0392b;
}

.browse-btn:hover {
  background: #2980b9;
}

.no-results-actions {
  margin-top: 20px;
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
  color: #2c3e50;
  font-size: 1.3rem;
}

.query-highlight {
  color: #3498db;
  font-weight: normal;
}

.total-results {
  margin: 0;
  color: #7f8c8d;
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
  color: #2c3e50;
  font-size: 1.1rem;
}

.section-header i {
  margin-right: 8px;
  color: #3498db;
}

.result-cards {
  padding: 15px 25px;
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}

.result-card {
  border: 1px solid #ecf0f1;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  background: white;
  cursor: pointer;
}

.result-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 15px;
}

.card-icon {
  width: 45px;
  height: 45px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  flex-shrink: 0;
}

.quiz-card .card-icon {
  background: #e8f4fd;
  color: #3498db;
}

.subject-card .card-icon {
  background: #e8f5e8;
  color: #27ae60;
}

.card-title {
  flex: 1;
}

.card-title h6 {
  margin: 0 0 6px 0;
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
}

.card-subtitle {
  color: #7f8c8d;
  font-size: 0.9rem;
  line-height: 1.4;
}

.card-badge {
  flex-shrink: 0;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.active {
  background: #d5f4e6;
  color: #27ae60;
}

.status-badge.upcoming {
  background: #fef3e8;
  color: #f39c12;
}

.status-badge.expired {
  background: #f5f5f5;
  color: #95a5a6;
}

.card-content {
  margin-bottom: 15px;
}

.quiz-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  color: #7f8c8d;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-value {
  color: #2c3e50;
  font-weight: 500;
  font-size: 0.9rem;
}

.subject-stats {
  display: flex;
  gap: 20px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-icon {
  width: 35px;
  height: 35px;
  border-radius: 8px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7f8c8d;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.9rem;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.8rem;
}

.card-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-weight: 500;
}

.action-btn.primary {
  background: #3498db;
  color: white;
}

.action-btn.primary:hover {
  background: #2980b9;
}

.action-btn.secondary {
  background: #ecf0f1;
  color: #7f8c8d;
}

.action-btn.secondary:hover {
  background: #d5dbdb;
  color: #2c3e50;
}

.action-btn.disabled {
  background: #f8f9fa;
  color: #bdc3c7;
  cursor: not-allowed;
}

.load-more {
  padding: 15px 25px;
  text-align: center;
  border-top: 1px solid #ecf0f1;
}

.load-more-btn {
  padding: 12px 25px;
  background: #ecf0f1;
  color: #7f8c8d;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
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
  
  .subject-stats {
    flex-direction: column;
    gap: 15px;
  }
  
  .filter-group {
    justify-content: center;
  }
}
</style>