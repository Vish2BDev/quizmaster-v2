import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import '@/assets/styles/_qm-theme.scss'

// Initialize app
const app = createApp(App)

// Initialize store and router
app.use(store)
app.use(router)

// Check for existing token and fetch user data on app start
const token = localStorage.getItem('token')
if (token) {
  store.commit('SET_TOKEN', token)
  // Fetch current user data
  store.dispatch('getCurrentUser').catch(() => {
    // If token is invalid, clear it
    store.dispatch('logout')
  })
}

app.mount('#app')