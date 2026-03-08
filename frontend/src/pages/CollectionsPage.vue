<template>
  <div class="collections-page">
    <div class="page-header">
      <h1>Collections</h1>
      <button @click="showNewForm = !showNewForm" class="primary">
        {{ showNewForm ? '✕ Close' : '+ New Collection' }}
      </button>
    </div>

    <div v-if="showNewForm" class="new-collection-form">
      <form @submit.prevent="createCollection">
        <div class="form-group">
          <label>Name *</label>
          <input v-model="newCollection.name" type="text" required placeholder="Collection name" />
        </div>

        <div class="form-group">
          <label>Slug *</label>
          <input v-model="newCollection.slug" type="text" required placeholder="url-slug" />
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea v-model="newCollection.description" placeholder="Optional description" rows="4"></textarea>
        </div>

        <div class="form-actions">
          <button type="submit" class="primary">Create Collection</button>
          <button type="button" @click="showNewForm = false" class="secondary">Cancel</button>
        </div>
      </form>
    </div>

    <div v-if="isLoading" class="loading">Loading collections...</div>
    <div v-else-if="collections.length === 0" class="empty">
      <p>No collections yet. <a href="#" @click.prevent="showNewForm = true">Create one</a></p>
    </div>

    <div v-else class="collections-grid">
      <div v-for="collection in collections" :key="collection.id" class="collection-card">
        <div class="card-header">
          <h3>{{ collection.name }}</h3>
        </div>

        <p class="slug">{{ collection.slug }}</p>
        <p v-if="collection.description" class="description">{{ collection.description }}</p>
        
        <div class="card-meta">
          <span class="meta-item">Created {{ formatDate(collection.created_at) }}</span>
        </div>

        <div class="card-actions">
          <button @click="editCollection(collection)" class="secondary">Edit</button>
          <button @click="deleteCollection(collection.id)" class="secondary">Delete</button>
        </div>
      </div>
    </div>

    <!-- Edit Form Modal (simplified) -->
    <div v-if="editingCollection" class="edit-modal">
      <div class="modal-content">
        <h2>Edit Collection</h2>
        <form @submit.prevent="updateCollection">
          <div class="form-group">
            <label>Name</label>
            <input v-model="editingCollection.name" type="text" required />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="editingCollection.description" rows="3"></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="primary">Update</button>
            <button type="button" @click="editingCollection = null" class="secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { collectionsAPI } from '@/api/client'

const collections = ref<any[]>([])
const isLoading = ref(false)
const showNewForm = ref(false)
const editingCollection = ref<any>(null)

const newCollection = ref({
  name: '',
  slug: '',
  description: ''
})

onMounted(async () => {
  await loadCollections()
})

const loadCollections = async () => {
  isLoading.value = true
  try {
    const response = await collectionsAPI.list(0, 100)
    collections.value = response.data
  } catch (error) {
    console.error('Error loading collections:', error)
  }
  isLoading.value = false
}

const createCollection = async () => {
  try {
    await collectionsAPI.create(newCollection.value)
    newCollection.value = { name: '', slug: '', description: '' }
    showNewForm.value = false
    await loadCollections()
  } catch (error) {
    console.error('Error creating collection:', error)
  }
}

const editCollection = (collection: any) => {
  editingCollection.value = { ...collection }
}

const updateCollection = async () => {
  if (!editingCollection.value) return
  
  try {
    await collectionsAPI.update(editingCollection.value.id, {
      name: editingCollection.value.name,
      description: editingCollection.value.description
    })
    editingCollection.value = null
    await loadCollections()
  } catch (error) {
    console.error('Error updating collection:', error)
  }
}

const deleteCollection = async (id: number) => {
  if (confirm('Delete this collection?')) {
    try {
      await collectionsAPI.delete(id)
      await loadCollections()
    } catch (error) {
      console.error('Error deleting collection:', error)
    }
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
}

.new-collection-form {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  max-width: 600px;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-family: inherit;
  font-size: 14px;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.form-actions button {
  flex: 1;
}

.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.collection-card {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.2s;
}

.collection-card:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header h3 {
  margin: 0;
}

.slug {
  color: var(--primary);
  font-weight: 500;
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.description {
  color: var(--text-secondary);
  margin: 1rem 0;
  line-height: 1.5;
}

.card-meta {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.meta-item {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.card-actions button {
  flex: 1;
}

.edit-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--background);
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
}

.modal-content h2 {
  margin-top: 0;
}

.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
}
</style>
