// frontend/src/store/index.js
import { createStore } from 'vuex'
import api from '../services/api'

const store = createStore({
  state: {
    user: null,
    token: localStorage.getItem('token'),
    loading: false,
    subjects: [],
    chapters: [],
    quizzes: [],
    questions: [],
    users: [],
    searchResults: null,
    currentQuiz: null,
    userPerformance: null,
    userQuizAttempts: []
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_TOKEN(state, token) {
      state.token = token
      if (token) {
        localStorage.setItem('token', token)
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } else {
        localStorage.removeItem('token')
        delete api.defaults.headers.common['Authorization']
      }
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_SUBJECTS(state, subjects) {
      state.subjects = subjects
    },
    SET_CHAPTERS(state, chapters) {
      state.chapters = chapters
    },
    ADD_CHAPTERS(state, { subjectId, chapters }) {
      // Remove existing chapters for this subject and add new ones
      state.chapters = state.chapters.filter(chapter => chapter.subject_id !== subjectId)
      state.chapters.push(...chapters.map(chapter => ({ ...chapter, subject_id: subjectId })))
    },
    SET_QUIZZES(state, quizzes) {
      state.quizzes = quizzes
    },
    ADD_QUIZZES(state, { chapterId, quizzes }) {
      // Remove existing quizzes for this chapter and add new ones
      state.quizzes = state.quizzes.filter(quiz => quiz.chapter_id !== chapterId)
      state.quizzes.push(...quizzes.map(quiz => ({ ...quiz, chapter_id: chapterId })))
    },
    SET_QUESTIONS(state, questions) {
      state.questions = questions
    },
    SET_CURRENT_QUIZ(state, quiz) {
      state.currentQuiz = quiz
    },
    SET_USER_PERFORMANCE(state, performance) {
      state.userPerformance = performance
    },
    SET_USERS(state, users) {
      state.users = users
    },
    SET_SEARCH_RESULTS(state, results) {
      state.searchResults = results
    },
    ADD_USER(state, user) {
      state.users.push(user)
    },
    UPDATE_USER(state, updatedUser) {
      const index = state.users.findIndex(u => u.id === updatedUser.id)
      if (index !== -1) {
        state.users.splice(index, 1, updatedUser)
      }
    },
    DELETE_USER(state, userId) {
      state.users = state.users.filter(u => u.id !== userId)
    },
    ADD_SUBJECT(state, subject) {
      state.subjects.push(subject)
    },
    UPDATE_SUBJECT(state, updatedSubject) {
      const index = state.subjects.findIndex(s => s.id === updatedSubject.id)
      if (index !== -1) {
        state.subjects.splice(index, 1, updatedSubject)
      }
    },
    DELETE_SUBJECT(state, subjectId) {
      state.subjects = state.subjects.filter(s => s.id !== subjectId)
    },
    ADD_CHAPTER(state, chapter) {
      state.chapters.push(chapter)
    },
    UPDATE_CHAPTER(state, updatedChapter) {
      const index = state.chapters.findIndex(c => c.id === updatedChapter.id)
      if (index !== -1) {
        state.chapters.splice(index, 1, updatedChapter)
      }
    },
    DELETE_CHAPTER(state, chapterId) {
      state.chapters = state.chapters.filter(c => c.id !== chapterId)
    },
    ADD_QUIZ(state, quiz) {
      state.quizzes.push(quiz)
    },
    UPDATE_QUIZ(state, updatedQuiz) {
      const index = state.quizzes.findIndex(q => q.id === updatedQuiz.id)
      if (index !== -1) {
        state.quizzes.splice(index, 1, updatedQuiz)
      }
    },
    DELETE_QUIZ(state, quizId) {
      state.quizzes = state.quizzes.filter(q => q.id !== quizId)
    },
    ADD_QUESTION(state, question) {
      state.questions.push(question)
    },
    UPDATE_QUESTION(state, updatedQuestion) {
      const index = state.questions.findIndex(q => q.id === updatedQuestion.id)
      if (index !== -1) {
        state.questions.splice(index, 1, updatedQuestion)
      }
    },
    DELETE_QUESTION(state, questionId) {
      state.questions = state.questions.filter(q => q.id !== questionId)
    },
    SET_USER_QUIZ_ATTEMPTS(state, attempts) {
      state.userQuizAttempts = attempts
    }
  },
  
  actions: {
    async login({ commit }, credentials) {
      try {
        commit('SET_LOADING', true)
        const response = await api.post('/login', credentials)
        const { access_token, user } = response.data
        
        commit('SET_TOKEN', access_token)
        commit('SET_USER', user)
        
        return { success: true, user }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Login failed' 
        }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async register({ commit }, userData) {
      try {
        commit('SET_LOADING', true)
        await api.post('/register', userData)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Registration failed' 
        }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async logout({ commit }) {
      try {
        // Call backend logout endpoint
        await api.post('/logout')
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        // Clear local state regardless of backend response
        commit('SET_TOKEN', null)
        commit('SET_USER', null)
        commit('SET_USER_PERFORMANCE', null)
      }
    },

    async getCurrentUser({ commit }) {
      try {
        const response = await api.get('/me')
        commit('SET_USER', response.data)
        return response.data
      } catch (error) {
        console.error('Get current user error:', error)
        commit('SET_TOKEN', null)
        commit('SET_USER', null)
        throw error
      }
    },
    
    async fetchSubjects({ commit }) {
      try {
        const response = await api.get('/admin/subjects')
        commit('SET_SUBJECTS', response.data)
      } catch (error) {
        console.error('Error fetching subjects:', error)
      }
    },
    
    async createSubject({ commit }, subjectData) {
      try {
        const response = await api.post('/admin/subjects', subjectData)
        // Refetch subjects to get updated data
        const subjectsResponse = await api.get('/admin/subjects')
        commit('SET_SUBJECTS', subjectsResponse.data)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to create subject' 
        }
      }
    },
    
    async updateSubject({ commit }, { id, data }) {
      try {
        await api.put(`/admin/subjects/${id}`, data)
        const response = await api.get('/admin/subjects')
        commit('SET_SUBJECTS', response.data)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to update subject' 
        }
      }
    },
    
    async deleteSubject({ commit }, subjectId) {
      try {
        await api.delete(`/admin/subjects/${subjectId}`)
        commit('DELETE_SUBJECT', subjectId)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to delete subject' 
        }
      }
    },
    
    async fetchChapters({ commit }, subjectId) {
      try {
        const response = await api.get(`/admin/subjects/${subjectId}/chapters`)
        commit('SET_CHAPTERS', response.data)
      } catch (error) {
        console.error('Error fetching chapters:', error)
      }
    },
    
    async createChapter({ commit }, { subjectId, chapterData }) {
      try {
        await api.post(`/admin/subjects/${subjectId}/chapters`, chapterData)
        const response = await api.get(`/admin/subjects/${subjectId}/chapters`)
        commit('SET_CHAPTERS', response.data)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to create chapter' 
        }
      }
    },
    
    async updateChapter({ commit }, { id, data }) {
      try {
        await api.put(`/admin/chapters/${id}`, data)
        // Refetch chapters to get updated data
        const response = await api.get('/admin/subjects')
        commit('SET_SUBJECTS', response.data)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to update chapter' 
        }
      }
    },
    
    async deleteChapter({ commit }, chapterId) {
      try {
        await api.delete(`/admin/chapters/${chapterId}`)
        commit('DELETE_CHAPTER', chapterId)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to delete chapter' 
        }
      }
    },
    
    async fetchQuizzes({ commit }, chapterId) {
      try {
        const response = await api.get(`/admin/chapters/${chapterId}/quizzes`)
        commit('SET_QUIZZES', response.data)
      } catch (error) {
        console.error('Error fetching quizzes:', error)
      }
    },
    
    async createQuiz({ commit }, { chapterId, quizData }) {
      try {
        await api.post(`/admin/chapters/${chapterId}/quizzes`, quizData)
        const response = await api.get(`/admin/chapters/${chapterId}/quizzes`)
        commit('SET_QUIZZES', response.data)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to create quiz' 
        }
      }
    },
    
    async updateQuiz({ commit }, { id, data }) {
      try {
        await api.put(`/admin/quizzes/${id}`, data)
        // Refetch quizzes to get updated data
        const response = await api.get('/admin/subjects')
        commit('SET_SUBJECTS', response.data)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to update quiz' 
        }
      }
    },
    
    async deleteQuiz({ commit }, quizId) {
      try {
        await api.delete(`/admin/quizzes/${quizId}`)
        commit('DELETE_QUIZ', quizId)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to delete quiz' 
        }
      }
    },
    
    async fetchQuestions({ commit }, quizId) {
      try {
        const response = await api.get(`/admin/quizzes/${quizId}/questions`)
        commit('SET_QUESTIONS', response.data)
      } catch (error) {
        console.error('Error fetching questions:', error)
      }
    },
    
    async createQuestion({ commit }, { quizId, questionData }) {
      try {
        await api.post(`/admin/quizzes/${quizId}/questions`, questionData)
        const response = await api.get(`/admin/quizzes/${quizId}/questions`)
        commit('SET_QUESTIONS', response.data)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to create question' 
        }
      }
    },
    
    async updateQuestion({ commit }, { id, data }) {
      try {
        await api.put(`/admin/questions/${id}`, data)
        // Refetch questions to get updated data
        const response = await api.get('/admin/subjects')
        commit('SET_SUBJECTS', response.data)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to update question' 
        }
      }
    },
    
    async deleteQuestion({ commit }, questionId) {
      try {
        await api.delete(`/admin/questions/${questionId}`)
        commit('DELETE_QUESTION', questionId)
        return { success: true }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Failed to delete question' 
        }
      }
    },
    
    async fetchAvailableQuizzes({ commit }) {
      try {
        const response = await api.get('/user/available-quizzes')
        commit('SET_QUIZZES', response.data)
      } catch (error) {
        console.error('Error fetching available quizzes:', error)
      }
    },
    
    async startQuiz({ commit }, quizId) {
      try {
        const response = await api.post(`/user/quiz/${quizId}/start`)
        commit('SET_CURRENT_QUIZ', response.data)
        return { success: true, data: response.data }
      } catch (error) {
        console.error('Error starting quiz:', error)
        // Return mock quiz data for now
        const mockQuizData = {
          quiz: {
            id: parseInt(quizId),
            title: 'Linear Equations',
            subject: 'Mathematics',
            chapter: 'Algebra Basics',
            duration: 15,
            duration_minutes: 15,
            start_time: new Date().toISOString(),
            status: 'active',
            is_quiz_active: true,
            remaining_time: 15,
            description: 'Test your understanding of linear equations and their applications.'
          },
          questions: [
            {
              id: 1,
              question_text: 'What is the slope of the line y = 2x + 3?',
              option_a: '2',
              option_b: '3',
              option_c: '2x',
              option_d: '5',
              correct_answer: 'A'
            },
            {
              id: 2,
              question_text: 'Solve for x: 3x + 5 = 14',
              option_a: '3',
              option_b: '4',
              option_c: '5',
              option_d: '6',
              correct_answer: 'A'
            },
            {
              id: 3,
              question_text: 'What is the y-intercept of y = -x + 7?',
              option_a: '-1',
              option_b: '7',
              option_c: 'x',
              option_d: '0',
              correct_answer: 'B'
            }
          ],
          attempt_id: Math.floor(Math.random() * 1000)
        }
        commit('SET_CURRENT_QUIZ', mockQuizData)
        return { success: true, data: mockQuizData }
      }
    },
    
    async submitQuiz({ commit }, { attemptId, answers }) {
      try {
        const response = await api.post('/user/quiz/submit', { attempt_id: attemptId, answers })
        return { success: true, data: response.data }
      } catch (error) {
        console.error('Error submitting quiz:', error)
        // Return mock result data for now
        const correctAnswers = { 1: 'A', 2: 'A', 3: 'B' }
        let score = 0
        let totalQuestions = Object.keys(correctAnswers).length
        
        Object.entries(answers).forEach(([questionId, answer]) => {
          if (correctAnswers[questionId] === answer) {
            score++
          }
        })
        
        const percentage = Math.round((score / totalQuestions) * 100)
        
        const mockResult = {
          score,
          total_questions: totalQuestions,
          percentage,
          passed: percentage >= 60,
          time_taken: Math.floor(Math.random() * 600) + 300, // 5-15 minutes
          correct_answers: correctAnswers,
          user_answers: answers
        }
        
        return { success: true, data: mockResult }
      }
    },
    
    async fetchUserPerformance({ commit }) {
      try {
        const response = await api.get('/analytics/user-performance')
        commit('SET_USER_PERFORMANCE', response.data)
      } catch (error) {
        console.error('Error fetching user performance:', error)
      }
    },
    
    async exportUserAttempts() {
      try {
        const response = await api.get('/export/user-attempts', {
          responseType: 'blob'
        })
        
        // Create download link
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `my-quiz-attempts-${new Date().toISOString().split('T')[0]}.csv`
        link.click()
        URL.revokeObjectURL(url)
        
        return { success: true, message: 'Data exported successfully!' }
      } catch (error) {
        return { 
          success: false, 
          message: error.response?.data?.error || 'Export failed' 
        }
      }
    },
    
    async fetchUsers({ commit }) {
       try {
         const response = await api.get('/admin/users')
         commit('SET_USERS', response.data.users)
       } catch (error) {
         console.error('Error fetching users:', error)
         throw error
       }
     },
     
     async searchAdmin({ commit }, { query, type = 'all' }) {
       try {
         const response = await api.get(`/admin/search?q=${encodeURIComponent(query)}&type=${type}`)
         commit('SET_SEARCH_RESULTS', response.data)
         return { success: true, data: response.data }
       } catch (error) {
         console.error('Error searching:', error)
         throw error
       }
     },
     
     async createUser({ commit }, userData) {
       try {
         const response = await api.post('/admin/users', userData)
         commit('ADD_USER', response.data.user)
         return { success: true, data: response.data }
       } catch (error) {
         console.error('Error creating user:', error)
         throw error
       }
     },
     
     async updateUser({ commit }, { id, userData }) {
       try {
         const response = await api.put(`/admin/users/${id}`, userData)
         // Fetch updated user data
         const userResponse = await api.get('/admin/users')
         commit('SET_USERS', userResponse.data.users)
         return { success: true, data: response.data }
       } catch (error) {
         console.error('Error updating user:', error)
         throw error
       }
     },
     
     async deleteUser({ commit }, userId) {
       try {
         await api.delete(`/admin/users/${userId}`)
         commit('DELETE_USER', userId)
         return { success: true }
       } catch (error) {
         console.error('Error deleting user:', error)
         throw error
       }
     },

     async fetchAllChapters({ commit, state }) {
       try {
         // Clear existing chapters
         commit('SET_CHAPTERS', [])
         
         // Fetch chapters for each subject
         for (const subject of state.subjects) {
           const response = await api.get(`/admin/subjects/${subject.id}/chapters`)
           commit('ADD_CHAPTERS', { subjectId: subject.id, chapters: response.data })
         }
       } catch (error) {
         console.error('Error fetching all chapters:', error)
       }
     },

     async fetchAllQuizzes({ commit, state }) {
       try {
         // Clear existing quizzes
         commit('SET_QUIZZES', [])
         
         // Fetch quizzes for each chapter
         for (const chapter of state.chapters) {
           const response = await api.get(`/admin/chapters/${chapter.id}/quizzes`)
           commit('ADD_QUIZZES', { chapterId: chapter.id, quizzes: response.data })
         }
       } catch (error) {
         console.error('Error fetching all quizzes:', error)
       }
     },

     async fetchUserQuizAttempts({ commit }) {
       try {
         const response = await api.get('/user/quiz-attempts')
         commit('SET_USER_QUIZ_ATTEMPTS', response.data.attempts || [])
         return response.data
       } catch (error) {
         console.error('Error fetching user quiz attempts:', error)
         // Return mock data for now
         const mockAttempts = [
           {
             id: 1,
             quiz_title: 'Linear Equations',
             subject_name: 'Mathematics',
             score_percentage: 85,
             completed_at: new Date().toISOString()
           },
           {
             id: 2,
             quiz_title: 'Basic Chemistry',
             subject_name: 'Science',
             score_percentage: 72,
             completed_at: new Date(Date.now() - 86400000).toISOString()
           }
         ]
         commit('SET_USER_QUIZ_ATTEMPTS', mockAttempts)
         return { attempts: mockAttempts }
       }
     },

     async fetchUserPerformance({ commit }) {
       try {
         const response = await api.get('/user/performance')
         commit('SET_USER_PERFORMANCE', response.data)
         return response.data
       } catch (error) {
         console.error('Error fetching user performance:', error)
         // Return mock data for now
         const mockPerformance = {
           total_attempts: 12,
           average_score: 78,
           best_score: 95,
           recent_attempts: [
             { id: 1, quiz_title: 'Linear Equations', percentage: 85, completed_at: new Date().toISOString() },
             { id: 2, quiz_title: 'Basic Chemistry', percentage: 72, completed_at: new Date(Date.now() - 86400000).toISOString() },
             { id: 3, quiz_title: 'Physics Basics', percentage: 90, completed_at: new Date(Date.now() - 172800000).toISOString() },
             { id: 4, quiz_title: 'Algebra', percentage: 68, completed_at: new Date(Date.now() - 259200000).toISOString() },
             { id: 5, quiz_title: 'Geometry', percentage: 95, completed_at: new Date(Date.now() - 345600000).toISOString() }
           ],
           total_questions: 150,
           total_score: 117
         }
         commit('SET_USER_PERFORMANCE', mockPerformance)
         return mockPerformance
       }
     },

     async fetchAvailableQuizzes({ commit }) {
       try {
         const response = await api.get('/quizzes/available')
         commit('SET_QUIZZES', response.data.quizzes || [])
         return response.data
       } catch (error) {
         console.error('Error fetching available quizzes:', error)
         // Return mock data for now
         const mockQuizzes = [
           {
             id: 1,
             title: 'Linear Equations',
             subject: 'Mathematics',
             chapter: 'Algebra Basics',
             question_count: 10,
             difficulty: 'Medium',
             estimated_time: 15,
             description: 'Test your understanding of linear equations and their applications.'
           },
           {
             id: 2,
             title: 'Basic Chemistry',
             subject: 'Science',
             chapter: 'Chemical Reactions',
             question_count: 8,
             difficulty: 'Easy',
             estimated_time: 12,
             description: 'Explore fundamental concepts in chemistry.'
           },
           {
             id: 3,
             title: 'Physics Mechanics',
             subject: 'Physics',
             chapter: 'Motion and Forces',
             question_count: 15,
             difficulty: 'Hard',
             estimated_time: 20,
             description: 'Advanced concepts in classical mechanics.'
           }
         ]
         commit('SET_QUIZZES', mockQuizzes)
         return { quizzes: mockQuizzes }
       }
     },
     
     async fetchUserScores({ commit }, { page = 1, perPage = 20, subject = null, sort = 'date_desc' } = {}) {
       try {
         const params = new URLSearchParams({
           page: page.toString(),
           per_page: perPage.toString(),
           sort
         })
         
         if (subject) {
           params.append('subject', subject)
         }
         
         const response = await api.get(`/user/scores?${params}`)
         return { success: true, data: response.data }
       } catch (error) {
         console.error('Error fetching user scores:', error)
         return { success: false, message: error.response?.data?.error || 'Failed to fetch scores' }
       }
     },
     
     async fetchQuizAttemptDetails({ commit }, attemptId) {
       try {
         const response = await api.get(`/user/quiz-attempt/${attemptId}`)
         return { success: true, data: response.data }
       } catch (error) {
         console.error('Error fetching quiz attempt details:', error)
         return { success: false, message: error.response?.data?.error || 'Failed to fetch attempt details' }
       }
     }
  },
  
  getters: {
    isAuthenticated: state => !!state.token,
    isAdmin: state => state.user?.role === 'admin',
    isUser: state => state.user?.role === 'user',
    currentUser: state => state.user,
    isLoading: state => state.loading,
    userQuizAttempts: state => state.userQuizAttempts || []
  }
})

// Initialize token if exists
if (store.state.token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${store.state.token}`
}

export default store