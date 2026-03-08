<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Documents</h3>
        <p class="stat-number">{{ stats.documents }}</p>
      </div>
      <div class="stat-card">
        <h3>Collections</h3>
        <p class="stat-number">{{ stats.collections }}</p>
      </div>
      <div class="stat-card">
        <h3>Assets</h3>
        <p class="stat-number">{{ stats.assets }}</p>
      </div>
      <div class="stat-card">
        <h3>Storage Used</h3>
        <p class="stat-number">{{ stats.storageUsed }}</p>
      </div>
    </div>

    <div class="quick-actions">
      <h2>Quick Actions</h2>
      <div class="action-buttons">
        <router-link to="/documents" class="action-button primary">
          <span class="icon">📄</span>
          <span>New Document</span>
        </router-link>
        <router-link to="/collections" class="action-button primary">
          <span class="icon">📁</span>
          <span>New Collection</span>
        </router-link>
        <router-link to="/assets" class="action-button primary">
          <span class="icon">📤</span>
          <span>Upload Asset</span>
        </router-link>
      </div>
    </div>

    <div class="recent-section">
      <h2>Recent Activity</h2>
      <p v-if="!authStore.user" class="loading">Loading...</p>
      <p v-else class="welcome-text">
        Welcome back, <strong>{{ authStore.user.username }}</strong>!<br>
        You are logged in as a <strong>{{ authStore.user.role }}</strong>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { documentsAPI, collectionsAPI, assetsAPI } from '@/api/client'

const authStore = useAuthStore()

const stats = ref({
  documents: 0,
  collections: 0,
  assets: 0,
  storageUsed: '0 MB'
})

onMounted(async () => {
  try {
    const [docsRes, collectionsRes, assetsRes, statsRes] = await Promise.all([
      documentsAPI.list(0, 1),
      collectionsAPI.list(0, 1),
      assetsAPI.list(0, 1),
      assetsAPI.stats()
    ])

    // These would normally come from pagination headers or separate count endpoints
    stats.value.documents = docsRes.data.length || 0
    stats.value.collections = collectionsRes.data.length || 0
    stats.value.assets = statsRes.data.total_assets || 0
    stats.value.storageUsed = `${statsRes.data.total_storage_mb} MB`
  } catch (error) {
    console.error('Error loading stats:', error)
  }
})
</script>

<style scoped>
.dashboard {
  animation: fadeIn 0.3s ease-in;
}

h1 {
  margin-bottom: 2rem;
  color: var(--text);
}

h2 {
  margin-bottom: 1rem;
  color: var(--text);
  font-size: 1.25rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  transition: all 0.2s;
}

.stat-card:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
}

.stat-card h3 {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary);
}

.quick-actions {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.action-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-radius: 8px;
  text-decoration: none;
  background-color: var(--primary);
  color: white;
  transition: all 0.2s;
  font-weight: 500;
}

.action-button:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
}

.icon {
  font-size: 1.5rem;
}

.recent-section {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
}

.welcome-text {
  color: var(--text-secondary);
  line-height: 1.8;
}

.loading {
  color: var(--text-secondary);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
