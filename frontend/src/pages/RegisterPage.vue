<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-box">
        <h1>Create Account</h1>
        <p class="subtitle">Join Clarity</p>

        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <label>Username</label>
            <input v-model="formData.username" type="text" required placeholder="Choose a username" />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input v-model="formData.email" type="email" required placeholder="Enter your email" />
          </div>

          <div class="form-group">
            <label>Full Name (optional)</label>
            <input v-model="formData.fullName" type="text" placeholder="Your full name" />
          </div>

          <div class="form-group">
            <label>Password</label>
            <input v-model="formData.password" type="password" required placeholder="Create a password" />
          </div>

          <div class="form-group">
            <label>Confirm Password</label>
            <input v-model="confirmPassword" type="password" required placeholder="Confirm password" />
          </div>

          <button type="submit" class="primary" :disabled="isLoading">
            {{ isLoading ? 'Creating account...' : 'Sign Up' }}
          </button>

          <p v-if="error" class="error-message">{{ error }}</p>
        </form>

        <p class="login-link">
          Already have an account? <router-link to="/login">Login</router-link>
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

const formData = ref({
  username: '',
  email: '',
  fullName: '',
  password: ''
})
const confirmPassword = ref('')
const isLoading = ref(false)
const error = ref('')

const handleRegister = async () => {
  if (formData.value.password !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  isLoading.value = true
  error.value = ''

  const success = await authStore.register(
    formData.value.username,
    formData.value.email,
    formData.value.password,
    formData.value.fullName
  )

  if (success) {
    router.push('/')
  } else {
    error.value = 'Registration failed. Please try again.'
  }

  isLoading.value = false
}
</script>

<style scoped>
.register-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.register-container {
  width: 100%;
  max-width: 400px;
}

.register-box {
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
  margin-bottom: 1rem;
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
  margin-top: 1rem;
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

.login-link {
  text-align: center;
  color: var(--text-secondary);
  margin-top: 1.5rem;
}

.login-link a {
  color: var(--primary);
  font-weight: 500;
}
</style>
