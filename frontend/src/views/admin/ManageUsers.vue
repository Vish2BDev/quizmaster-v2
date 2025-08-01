<template>
  <div class="manage-users-container">
    <!-- Header Section -->
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h2 class="text-primary mb-1">
            <i class="fas fa-users me-2"></i>User Management
          </h2>
          <p class="text-muted mb-0">Manage system users and their permissions</p>
        </div>
        <div class="d-flex gap-2">
          <div class="search-box">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="fas fa-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control border-start-0" 
                placeholder="Search users..."
                v-model="searchQuery"
                @input="searchUsers"
              >
            </div>
          </div>
          <button class="btn btn-qm-primary" @click="refreshUsers">
            <i class="fas fa-sync-alt me-2"></i>Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="searchResults && searchQuery" class="card-qm mb-4">
      <div class="card-header">
        <h5 class="mb-0">
          <i class="fas fa-search me-2"></i>Search Results
        </h5>
      </div>
      <div class="card-body">
        <div v-if="searchResults.users && searchResults.users.length > 0">
          <h6 class="text-primary">Users ({{ searchResults.users.length }})</h6>
          <div class="row">
            <div v-for="user in searchResults.users" :key="user.id" class="col-md-6 mb-2">
              <div class="search-result-item" @click="viewUserDetails(user)">
                <div class="d-flex align-items-center">
                  <div class="user-avatar me-3">
                    <i class="fas fa-user-circle fa-2x" :class="user.role === 'admin' ? 'text-danger' : 'text-primary'"></i>
                  </div>
                  <div>
                    <div class="fw-bold">{{ user.username }}</div>
                    <div class="text-muted small">{{ user.email }}</div>
                    <span class="badge" :class="user.role === 'admin' ? 'bg-danger' : 'bg-primary'">{{ user.role }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="searchQuery">
          <p class="text-muted mb-0">No users found matching "{{ searchQuery }}"</p>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="card-qm">
      <div class="card-header">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="mb-0">
            <i class="fas fa-table me-2"></i>All Users ({{ users.length }})
          </h5>
          <div class="d-flex gap-2">
            <select class="form-select form-select-sm" v-model="roleFilter" @change="filterUsers">
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="user">User</option>
            </select>
            <select class="form-select form-select-sm" v-model="statusFilter" @change="filterUsers">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>
      </div>
      <div class="card-body p-0">
        <div v-if="loading" class="text-center p-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading users...</p>
        </div>
        
        <div v-else-if="filteredUsers.length === 0" class="text-center p-4">
          <i class="fas fa-users fa-3x text-muted mb-3"></i>
          <h5 class="text-muted">No users found</h5>
          <p class="text-muted">No users match your current filters.</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Quiz Attempts</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>
                  <div class="d-flex align-items-center">
                    <div class="user-avatar me-3">
                      <i class="fas fa-user-circle fa-2x" :class="user.role === 'admin' ? 'text-danger' : 'text-primary'"></i>
                    </div>
                    <div>
                      <div class="fw-bold">{{ user.username }}</div>
                      <div class="text-muted small">ID: {{ user.id }}</div>
                    </div>
                  </div>
                </td>
                <td>{{ user.email }}</td>
                <td>
                  <span class="badge" :class="user.role === 'admin' ? 'bg-danger' : 'bg-primary'">
                    {{ user.role }}
                  </span>
                </td>
                <td>
                  <span class="badge" :class="user.is_active ? 'bg-success' : 'bg-secondary'">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <span class="badge bg-info">{{ user.quiz_attempts_count }}</span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" @click="editUser(user)" title="Edit User">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button 
                      class="btn btn-outline-danger" 
                      @click="deleteUser(user)"
                      :disabled="user.role === 'admin'"
                      title="Delete User"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div class="modal fade" id="editUserModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-user-edit me-2"></i>Edit User
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveUser">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="userForm.username"
                  required
                >
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="userForm.email"
                  required
                >
              </div>
              <div class="mb-3">
                <label class="form-label">Role</label>
                <select class="form-select" v-model="userForm.role" required>
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div class="mb-3">
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    v-model="userForm.is_active"
                    id="isActive"
                  >
                  <label class="form-check-label" for="isActive">
                    Active User
                  </label>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-qm-primary" @click="saveUser" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { Modal } from 'bootstrap'

export default {
  name: 'ManageUsers',
  setup() {
    const store = useStore()
    
    const users = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const searchQuery = ref('')
    const searchResults = ref(null)
    const roleFilter = ref('')
    const statusFilter = ref('')
    const editingUser = ref(null)
    
    const userForm = reactive({
      username: '',
      email: '',
      role: 'user',
      is_active: true
    })
    
    const filteredUsers = computed(() => {
      let filtered = users.value
      
      if (roleFilter.value) {
        filtered = filtered.filter(user => user.role === roleFilter.value)
      }
      
      if (statusFilter.value) {
        const isActive = statusFilter.value === 'active'
        filtered = filtered.filter(user => user.is_active === isActive)
      }
      
      return filtered
    })
    
    const fetchUsers = async () => {
      loading.value = true
      try {
        await store.dispatch('fetchUsers')
        users.value = store.state.users || []
      } catch (error) {
        console.error('Error fetching users:', error)
        alert('Failed to fetch users')
      } finally {
        loading.value = false
      }
    }
    
    const searchUsers = async () => {
      if (!searchQuery.value.trim()) {
        searchResults.value = null
        return
      }
      
      try {
        await store.dispatch('searchAdmin', {
          query: searchQuery.value,
          type: 'users'
        })
        searchResults.value = store.state.searchResults
      } catch (error) {
        console.error('Error searching users:', error)
        alert('Failed to search users')
      }
    }
    
    const refreshUsers = () => {
      searchQuery.value = ''
      searchResults.value = null
      fetchUsers()
    }
    
    const filterUsers = () => {
      // Filtering is handled by computed property
    }
    
    const editUser = (user) => {
      editingUser.value = user
      userForm.username = user.username
      userForm.email = user.email
      userForm.role = user.role
      userForm.is_active = user.is_active
      
      const modal = new Modal(document.getElementById('editUserModal'))
      modal.show()
    }
    
    const saveUser = async () => {
      if (!editingUser.value) return
      
      saving.value = true
      try {
        await store.dispatch('updateUser', {
          id: editingUser.value.id,
          userData: { ...userForm }
        })
        
        alert('User updated successfully')
        
        const modal = Modal.getInstance(document.getElementById('editUserModal'))
        modal.hide()
        
        await fetchUsers()
      } catch (error) {
        console.error('Error updating user:', error)
        alert('Failed to update user')
      } finally {
        saving.value = false
      }
    }
    
    const deleteUser = async (user) => {
      if (user.role === 'admin') {
        alert('Cannot delete admin users')
        return
      }
      
      if (!confirm(`Are you sure you want to delete user "${user.username}"?`)) {
        return
      }
      
      try {
        await store.dispatch('deleteUser', user.id)
        alert('User deleted successfully')
        await fetchUsers()
      } catch (error) {
        console.error('Error deleting user:', error)
        alert('Failed to delete user')
      }
    }
    
    const viewUserDetails = (user) => {
      editUser(user)
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    onMounted(() => {
      fetchUsers()
    })
    
    return {
      users,
      loading,
      saving,
      searchQuery,
      searchResults,
      roleFilter,
      statusFilter,
      editingUser,
      userForm,
      filteredUsers,
      fetchUsers,
      searchUsers,
      refreshUsers,
      filterUsers,
      editUser,
      saveUser,
      deleteUser,
      viewUserDetails,
      formatDate
    }
  }
}
</script>

<style scoped>
.manage-users-container {
  padding: 2rem;
  background: #f8f9fa;
  min-height: 100vh;
}

.page-header {
  background: white;
  padding: 2rem;
  border-radius: var(--qm-border-radius);
  box-shadow: var(--qm-shadow-sm);
}

.search-box {
  width: 300px;
}

.search-result-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: var(--qm-border-radius);
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-result-item:hover {
  border-color: var(--qm-primary);
  box-shadow: var(--qm-shadow-sm);
  transform: translateY(-2px);
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
}

.table th {
  font-weight: 600;
  color: var(--qm-text-primary);
  border-bottom: 2px solid #e9ecef;
}

.table td {
  vertical-align: middle;
  padding: 1rem 0.75rem;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}

.modal-content {
  border: none;
  border-radius: var(--qm-border-radius);
  box-shadow: var(--qm-shadow-lg);
}

.modal-header {
  background: linear-gradient(135deg, var(--qm-primary), var(--qm-secondary));
  color: white;
  border-bottom: none;
}

.modal-header .btn-close {
  filter: invert(1);
}

.badge {
  font-size: 0.75rem;
  padding: 0.35rem 0.65rem;
}

.form-select-sm {
  width: auto;
  min-width: 120px;
}
</style>