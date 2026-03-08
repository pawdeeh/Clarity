import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI, userAPI } from '@/api/client'

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  role: string
  is_active: boolean
  created_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isEditor = computed(() => user.value?.role === 'editor' || user.value?.role === 'admin')

  const login = async (username: string, password: string) => {
    try {
      const response = await authAPI.login({ username, password })
      token.value = response.data.access_token
      localStorage.setItem('auth_token', token.value)
      
      // Get user profile
      const userResponse = await authAPI.getMe()
      user.value = userResponse.data
      
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  const register = async (username: string, email: string, password: string, fullName?: string) => {
    try {
      const response = await userAPI.register({ username, email, password, full_name: fullName })
      // Auto-login after registration
      return await login(username, password)
    } catch (error) {
      console.error('Registration failed:', error)
      return false
    }
  }

  const logout = () => {
    authAPI.logout()
    user.value = null
    token.value = null
  }

  const setUser = (newUser: User) => {
    user.value = newUser
  }

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    isEditor,
    login,
    register,
    logout,
    setUser
  }
})
