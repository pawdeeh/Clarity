<template>
  <div class="app">
    <nav v-if="authStore.isAuthenticated" class="navbar">
      <div class="navbar-container">
        <router-link to="/" class="navbar-brand">
          <strong>Clarity</strong> Documentation
        </router-link>
        
        <div class="navbar-links">
          <router-link to="/documents" class="nav-link">Documents</router-link>
          <router-link to="/collections" class="nav-link">Collections</router-link>
          <router-link to="/assets" class="nav-link">Assets</router-link>
        </div>

        <div class="navbar-user">
          <span class="user-name">{{ authStore.user?.username }}</span>
          <button @click="logout" class="secondary">Logout</button>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--surface);
}

.navbar {
  background-color: var(--background);
  border-bottom: 1px solid var(--border);
  padding: 1rem 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.navbar-brand {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text);
  text-decoration: none;
  margin-right: auto;
}

.navbar-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: var(--primary);
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.user-name {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.main-content {
  flex: 1;
  overflow: auto;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0 1rem;
    gap: 1rem;
  }

  .navbar-links {
    gap: 1rem;
  }

  .main-content {
    padding: 1rem;
  }
}
</style>
