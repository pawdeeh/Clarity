<template>
  <div class="documents-page">
    <div class="page-header">
      <h1>Documents</h1>
      <button v-if="!isEditing" @click="startNewDocument" class="primary">+ New Document</button>
      <button v-else @click="cancelEdit" class="secondary">Cancel</button>
    </div>

    <div v-if="!isEditing" class="documents-list">
      <div v-if="isLoading" class="loading">Loading documents...</div>
      <div v-else-if="documents.length === 0" class="empty">
        <p>No documents yet. <button @click="startNewDocument" class="link-button">Create one</button></p>
      </div>
      
      <div v-else class="documents-grid">
        <div v-for="doc in documents" :key="doc.id" class="document-card">
          <div class="card-header">
            <h3>{{ doc.title }}</h3>
            <span class="status" :class="doc.status">{{ doc.status }}</span>
          </div>
          <p class="slug">{{ doc.slug }}</p>
          <p class="meta">v{{ doc.version }} • {{ formatDate(doc.updated_at) }}</p>
          <div class="card-actions">
            <router-link :to="`/documents/${doc.id}/edit`" class="secondary">Edit</router-link>
            <button @click="deleteDocument(doc.id)" class="secondary">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="document-editor-container">
      <form @submit.prevent="saveDocument">
        <div class="form-group">
          <label>Title</label>
          <input v-model="currentDocument.title" type="text" required />
        </div>

        <div class="form-group">
          <label>Slug</label>
          <input v-model="currentDocument.slug" type="text" required />
        </div>

        <div class="form-group">
          <label>Description (Front Matter)</label>
          <textarea v-model="currentDocument.front_matter.description"></textarea>
        </div>

        <div class="form-group">
          <label>Content (Markdown)</label>
          <textarea v-model="currentDocument.content" rows="15"></textarea>
        </div>

        <div class="form-group">
          <label>Status</label>
          <select v-model="currentDocument.status">
            <option value="draft">Draft</option>
            <option value="review">Review</option>
            <option value="published">Published</option>
          </select>
        </div>

        <div class="form-actions">
          <button type="submit" class="primary">Save Document</button>
          <button type="button" @click="cancelEdit" class="secondary">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { documentsAPI } from '@/api/client'

const route = useRoute()
const router = useRouter()

const documents = ref<any[]>([])
const isLoading = ref(false)
const isEditing = ref(false)
const currentDocument = ref<any>({
  title: '',
  slug: '',
  content: '',
  status: 'draft',
  front_matter: {},
  tags: [],
  variables: {}
})

onMounted(async () => {
  // Check if we're editing a document
  if (route.params.id) {
    await loadDocument(parseInt(route.params.id as string))
    isEditing.value = true
  } else {
    await loadDocuments()
  }
})

const loadDocuments = async () => {
  isLoading.value = true
  try {
    const response = await documentsAPI.list(0, 50)
    documents.value = response.data
  } catch (error) {
    console.error('Error loading documents:', error)
  }
  isLoading.value = false
}

const loadDocument = async (id: number) => {
  try {
    const response = await documentsAPI.get(id)
    currentDocument.value = response.data
  } catch (error) {
    console.error('Error loading document:', error)
  }
}

const saveDocument = async () => {
  try {
    if (currentDocument.value.id) {
      await documentsAPI.update(currentDocument.value.id, currentDocument.value)
    } else {
      const response = await documentsAPI.create(currentDocument.value)
      currentDocument.value.id = response.data.id
    }
    isEditing.value = false
    await loadDocuments()
  } catch (error) {
    console.error('Error saving document:', error)
  }
}

const deleteDocument = async (id: number) => {
  if (confirm('Are you sure you want to delete this document?')) {
    try {
      await documentsAPI.delete(id)
      await loadDocuments()
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }
}

const startNewDocument = () => {
  currentDocument.value = {
    title: '',
    slug: '',
    content: '',
    status: 'draft',
    front_matter: {},
    tags: [],
    variables: {}
  }
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
  currentDocument.value = {
    title: '',
    slug: '',
    content: '',
    status: 'draft',
    front_matter: {},
    tags: [],
    variables: {}
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

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.document-card {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.2s;
}

.document-card:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.card-header h3 {
  margin: 0;
  flex: 1;
}

.status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status.draft {
  background-color: #fef3c7;
  color: #92400e;
}

.status.review {
  background-color: #dbeafe;
  color: #1e40af;
}

.status.published {
  background-color: #dcfce7;
  color: #15803d;
}

.slug {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0.5rem 0;
}

.meta {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin: 0.5rem 0 1rem 0;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.card-actions a,
.card-actions button {
  flex: 1;
  padding: 8px 12px;
  font-size: 0.9rem;
}

.document-editor-container {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2rem;
  max-width: 900px;
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
.form-group textarea,
.form-group select {
  width: 100%;
  font-family: inherit;
}

.form-group textarea {
  resize: vertical;
  min-height: 200px;
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.form-actions button {
  flex: 1;
}

.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
}

select {
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
}

.link-button {
  background: none;
  border: none;
  color: var(--primary);
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
  font: inherit;
}

.link-button:hover {
  opacity: 0.8;
}
</style>
