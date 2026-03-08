<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-box">
        <h1>Clarity</h1>
        <p class="subtitle">Documentation Platform</p>

        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label>Username</label>
            <input v-model="username" type="text" required placeholder="Enter username" />
          </div>

          <div class="form-group">
            <label>Password</label>
            <input v-model="password" type="password" required placeholder="Enter password" />
          </div>

          <button type="submit" class="primary" :disabled="isLoading">
            {{ isLoading ? 'Logging in...' : 'Login' }}
          </button>

          <p v-if="error" class="error-message">{{ error }}</p>
        </form>

        <div class="divider">or</div>

        <p class="signup-link">
          Don't have an account? <router-link to="/register">Sign up</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''

  const success = await authStore.login(username.value, password.value)
  
  if (success) {
    router.push('/')
  } else {
    error.value = 'Invalid username or password'
  }

  isLoading.value = false
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
}

.login-box {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

h1 {
  text-align: center;
  color: var(--primary);
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text);
}

input {
  width: 100%;
}

button[type="submit"] {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  background-color: var(--primary);
  color: white;
}

button[type="submit"]:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: var(--danger);
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.divider {
  text-align: center;
  color: var(--text-secondary);
  margin: 2rem 0;
  position: relative;
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 45%;
  height: 1px;
  background-color: var(--border);
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.signup-link {
  text-align: center;
  color: var(--text-secondary);
}

.signup-link a {
  color: var(--primary);
  font-weight: 500;
}
</style>
