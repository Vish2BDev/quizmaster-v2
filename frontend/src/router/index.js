import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/UserDashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/my-quizzes',
    name: 'MyQuizzes',
    component: () => import('../views/MyQuizzes.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/leaderboard',
    name: 'Leaderboard',
    component: () => import('../views/Leaderboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/my-stats',
    name: 'MyStats',
    component: () => import('../views/MyStats.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/achievements',
    name: 'Achievements',
    component: () => import('../views/Achievements.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/quiz/:id',
    name: 'TakeQuiz',
    component: () => import('../views/TakeQuiz.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/quiz-summary',
    name: 'QuizSummary',
    component: () => import('../views/QuizSummary.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/past-scores',
    name: 'PastScores',
    component: () => import('../views/PastScores.vue'),
    meta: { requiresAuth: true }
  },
  {
      path: '/admin',
      name: 'AdminDashboard',
      component: () => import('@/views/admin/AdminOverview.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
  {
    path: '/admin/subjects',
    name: 'ManageSubjects',
    component: () => import('../views/admin/ManageSubjects.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
          path: '/admin/subjects/:subjectId/chapters',
          name: 'ManageChapters',
          component: () => import('../views/admin/ManageChapters.vue'),
          meta: { requiresAuth: true, requiresAdmin: true }
        },
        {
          path: '/admin/chapters',
          name: 'AllChapters',
          component: () => import('../views/admin/AllChapters.vue'),
          meta: { requiresAuth: true, requiresAdmin: true }
        },
        {
          path: '/admin/chapters/:chapterId/quizzes',
          name: 'ManageQuizzes',
          component: () => import('../views/admin/ManageQuizzes.vue'),
          meta: { requiresAuth: true, requiresAdmin: true }
        },
        {
          path: '/admin/quizzes',
          name: 'AllQuizzes',
          component: () => import('../views/admin/AllQuizzes.vue'),
          meta: { requiresAuth: true, requiresAdmin: true }
        },
  {
    path: '/admin/quizzes/:quizId/questions',
    name: 'ManageQuestions',
    component: () => import('../views/admin/ManageQuestions.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'ManageUsers',
    component: () => import('../views/admin/ManageUsers.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/analytics',
    name: 'AdminAnalytics',
    component: () => import('../views/AdminDashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/real-time',
    name: 'RealTimeEvents',
    component: () => import('../components/RealTimeEvents.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/tasks',
    name: 'BackgroundTasks',
    component: () => import('../views/admin/BackgroundTasks.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/exports',
    name: 'DataExports',
    component: () => import('../views/admin/DataExports.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const isAuthenticated = store.getters.isAuthenticated
  const isAdmin = store.getters.isAdmin

  if (requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (requiresAdmin && !isAdmin) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router