<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card shadow">
          <div class="card-body p-5">
            <div class="text-center mb-4">
              <i class="fas fa-user-plus text-primary mb-3" style="font-size: 3rem;"></i>
              <h2 class="card-title">Register</h2>
              <p class="text-muted">Create your account to get started!</p>
            </div>
            
            <form @submit.prevent="handleRegister">
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
                <label for="email" class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  id="email"
                  v-model="form.email"
                  :class="{ 'is-invalid': errors.email }"
                  required
                >
                <div class="invalid-feedback">{{ errors.email }}</div>
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
              
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirm Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="confirmPassword"
                  v-model="form.confirmPassword"
                  :class="{ 'is-invalid': errors.confirmPassword }"
                  required
                >
                <div class="invalid-feedback">{{ errors.confirmPassword }}</div>
              </div>
              
              <div class="alert alert-danger" v-if="errorMessage">
                {{ errorMessage }}
              </div>
              
              <div class="alert alert-success" v-if="successMessage">
                {{ successMessage }}
              </div>
              
              <div class="d-grid">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="isLoading"
                >
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                  Register
                </button>
              </div>
            </form>
            
            <div class="text-center mt-3">
              <p class="mb-0">Already have an account? 
                <router-link to="/login" class="text-primary">Login here</router-link>
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
  name: 'Register',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const form = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })
    
    const errors = ref({})
    const errorMessage = ref('')
    const successMessage = ref('')
    
    const isLoading = computed(() => store.getters.isLoading)
    
    const validateForm = () => {
      errors.value = {}
      
      if (!form.value.username.trim()) {
        errors.value.username = 'Username is required'
      } else if (form.value.username.length < 3) {
        errors.value.username = 'Username must be at least 3 characters'
      }
      
      if (!form.value.email.trim()) {
        errors.value.email = 'Email is required'
      } else if (!/\S+@\S+\.\S+/.test(form.value.email)) {
        errors.value.email = 'Please enter a valid email'
      }
      
      if (!form.value.password.trim()) {
        errors.value.password = 'Password is required'
      } else if (form.value.password.length < 6) {
        errors.value.password = 'Password must be at least 6 characters'
      }
      
      if (form.value.password !== form.value.confirmPassword) {
        errors.value.confirmPassword = 'Passwords do not match'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const handleRegister = async () => {
      if (!validateForm()) return
      
      errorMessage.value = ''
      successMessage.value = ''
      
      const result = await store.dispatch('register', {
        username: form.value.username,
        email: form.value.email,
        password: form.value.password
      })
      
      if (result.success) {
        successMessage.value = 'Registration successful! Redirecting to login...'
        setTimeout(() => {
          router.push('/login')
        }, 2000)
      } else {
        errorMessage.value = result.message
      }
    }
    
    return {
      form,
      errors,
      errorMessage,
      successMessage,
      isLoading,
      handleRegister
    }
  }
}
</script>

<style lang="scss" scoped>
.register-page {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.card {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}
</style> 