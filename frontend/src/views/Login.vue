<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-body p-5">
            <div class="text-center mb-4">
              <i class="fas fa-sign-in-alt text-primary mb-3" style="font-size: 3rem;"></i>
              <h2 class="card-title">Login</h2>
              <p class="text-muted">Welcome back! Please login to your account.</p>
            </div>
            
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="username"
                  v-model="form.username"
                  :class="{ 'is-invalid': errors.username }"
                  required
                >
                <div class="invalid-feedback">{{ errors.username }}</div>
              </div>
              
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="password"
                  v-model="form.password"
                  :class="{ 'is-invalid': errors.password }"
                  required
                >
                <div class="invalid-feedback">{{ errors.password }}</div>
              </div>
              
              <div class="alert alert-danger" v-if="errorMessage">
                {{ errorMessage }}
              </div>
              
              <div class="d-grid">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="isLoading"
                >
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                  Login
                </button>
              </div>
            </form>
            
            <div class="text-center mt-3">
              <p class="mb-0">Don't have an account? 
                <router-link to="/register" class="text-primary">Register here</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const form = ref({
      username: '',
      password: ''
    })
    
    const errors = ref({})
    const errorMessage = ref('')
    
    const isLoading = computed(() => store.getters.isLoading)
    
    const validateForm = () => {
      errors.value = {}
      
      if (!form.value.username.trim()) {
        errors.value.username = 'Username is required'
      }
      
      if (!form.value.password.trim()) {
        errors.value.password = 'Password is required'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const handleLogin = async () => {
      if (!validateForm()) return
      
      errorMessage.value = ''
      const result = await store.dispatch('login', form.value)
      
      if (result.success) {
        const user = store.getters.currentUser
        if (user.role === 'admin') {
          router.push('/admin')
        } else {
          router.push('/dashboard')
        }
      } else {
        errorMessage.value = result.message
      }
    }
    
    return {
      form,
      errors,
      errorMessage,
      isLoading,
      handleLogin
    }
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.card {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}
</style> 