<template>
  <div class="document-editor-page">
    <div v-if="isLoading" class="loading">Loading document...</div>
    
    <div v-else class="editor-container">
      <div v-if="isEditing" class="edit-mode">
        <form @submit.prevent="saveDocument">
          <div class="editor-header">
            <div class="form-group">
              <input v-model="document.title" type="text" placeholder="Document Title" required />
            </div>
            <div class="header-actions">
              <button type="submit" class="primary">💾 Save</button>
              <button type="button" @click="isEditing = false" class="secondary">Cancel</button>
            </div>
          </div>

          <div class="form-group">
            <label>Slug</label>
            <input v-model="document.slug" type="text" required />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Status</label>
              <select v-model="document.status">
                <option value="draft">Draft</option>
                <option value="review">Review</option>
                <option value="published">Published</option>
              </select>
            </div>

            <div class="form-group">
              <label>Collection</label>
              <select v-model="document.collection_id">
                <option :value="null">None</option>
                <option v-for="collection in collections" :key="collection.id" :value="collection.id">
                  {{ collection.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Tags</label>
            <input v-model="tagInput" type="text" placeholder="Comma-separated tags" />
          </div>

          <div class="form-group">
            <label>Content (Markdown)</label>
            <textarea v-model="document.content" placeholder="Write your document here..." rows="20"></textarea>
          </div>
        </form>
      </div>

      <div v-else class="view-mode">
        <div class="view-header">
          <div>
            <h1>{{ document.title }}</h1>
            <p class="slug">{{ document.slug }}</p>
            <div class="metadata">
              <span v-if="document.status" class="badge" :class="document.status">{{ document.status }}</span>
              <span class="meta-item">v{{ document.version }}</span>
              <span class="meta-item">Updated {{ formatDate(document.updated_at) }}</span>
            </div>
          </div>
          <div class="view-actions">
            <button @click="isEditing = true" class="primary">✏️ Edit</button>
            <button @click="deleteDocument" class="secondary">🗑️ Delete</button>
          </div>
        </div>

        <div class="document-content" v-html="document.html_content"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { documentsAPI, collectionsAPI } from '@/api/client'

const route = useRoute()
const router = useRouter()

const document = ref<any>({
  title: '',
  slug: '',
  content: '',
  html_content: '',
  status: 'draft',
  collection_id: null,
  tags: [],
  version: 1,
  updated_at: new Date().toISOString()
})

const collections = ref<any[]>([])
const isLoading = ref(true)
const isEditing = ref(false)
const tagInput = ref('')

onMounted(async () => {
  const docId = route.params.id ? parseInt(route.params.id as string) : null
  
  if (docId) {
    try {
      const response = await documentsAPI.get(docId)
      document.value = response.data
      tagInput.value = document.value.tags?.join(', ') || ''
    } catch (error) {
      console.error('Error loading document:', error)
    }
  } else {
    isEditing.value = true
  }

  // Load collections
  try {
    const response = await collectionsAPI.list(0, 100)
    collections.value = response.data
  } catch (error) {
    console.error('Error loading collections:', error)
  }

  isLoading.value = false
})

const saveDocument = async () => {
  document.value.tags = tagInput.value.split(',').map(t => t.trim()).filter(t => t)
  
  try {
    if (document.value.id) {
      await documentsAPI.update(document.value.id, document.value)
    } else {
      const response = await documentsAPI.create(document.value)
      document.value = response.data
    }
    
    // Render the document
    if (document.value.id) {
      const renderResponse = await documentsAPI.render(document.value.id)
      document.value.html_content = renderResponse.data.html_content
    }
    
    isEditing.value = false
  } catch (error) {
    console.error('Error saving document:', error)
  }
}

const deleteDocument = async () => {
  if (confirm('Are you sure you want to delete this document?')) {
    try {
      await documentsAPI.delete(document.value.id)
      router.push('/documents')
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}
</script>

<style scoped>
.document-editor-page {
  animation: fadeIn 0.3s ease-in;
}

.editor-container {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2rem;
}

/* Edit Mode */
.edit-mode .editor-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: flex-start;
}

.edit-mode .editor-header .form-group {
  flex: 1;
  margin-bottom: 0;
}

.edit-mode .editor-header input {
  font-size: 2rem;
  font-weight: 600;
  padding: 12px;
}

.editor-header .header-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 2px;
}

.editor-header .header-actions button {
  white-space: nowrap;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text);
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-family: inherit;
  font-size: 14px;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 300px;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 13px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* View Mode */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border);
}

.view-header h1 {
  margin: 0 0 0.5rem 0;
}

.slug {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0 0 1rem 0;
}

.metadata {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.draft {
  background-color: #fef3c7;
  color: #92400e;
}

.badge.review {
  background-color: #dbeafe;
  color: #1e40af;
}

.badge.published {
  background-color: #dcfce7;
  color: #15803d;
}

.meta-item {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.view-actions {
  display: flex;
  gap: 0.5rem;
}

.view-actions button {
  white-space: nowrap;
}

.document-content {
  line-height: 1.8;
  color: var(--text);
}

.document-content h2 {
  margin: 2rem 0 1rem 0;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.5rem;
}

.document-content h3 {
  margin: 1.5rem 0 0.5rem 0;
}

.document-content p {
  margin: 1rem 0;
}

.document-content code {
  background-color: var(--surface);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.document-content pre {
  background-color: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.document-content pre code {
  background: none;
  padding: 0;
}

.document-content ul,
.document-content ol {
  margin: 1rem 0 1rem 2rem;
}

.document-content li {
  margin: 0.5rem 0;
}

.loading {
  text-align: center;
  padding: 3rem;
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

@media (max-width: 768px) {
  .view-header {
    flex-direction: column;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .editor-container {
    padding: 1rem;
  }
}
</style>
