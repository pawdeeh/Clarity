<template>
  <div class="assets-page">
    <div class="page-header">
      <h1>Assets</h1>
      <div class="header-actions">
        <button @click="showUpload = !showUpload" class="primary">
          {{ showUpload ? '✕ Close' : '+ Upload' }}
        </button>
      </div>
    </div>

    <div v-if="showUpload" class="upload-section">
      <h2>Upload Files</h2>
      <div class="upload-area" @dragover="dragover = true" @dragleave="dragover = false" @drop="handleDrop" :class="{ active: dragover }">
        <input 
          type="file" 
          ref="fileInput" 
          @change="handleFilesSelected" 
          multiple 
          hidden
        />
        <button type="button" @click="$refs.fileInput?.click()" class="secondary">
          Choose Files or Drag & Drop
        </button>
        <p v-if="selectedFiles.length > 0" class="selected-info">
          {{ selectedFiles.length }} file(s) selected
        </p>
      </div>

      <div v-if="selectedFiles.length > 0" class="upload-actions">
        <button @click="uploadFiles" class="primary" :disabled="isUploading">
          {{ isUploading ? 'Uploading...' : 'Upload Files' }}
        </button>
      </div>

      <div v-if="uploadMessage" :class="['upload-message', uploadMessageType]">
        {{ uploadMessage }}
      </div>
    </div>

    <div class="assets-section">
      <h2>Your Assets</h2>
      
      <div class="filters">
        <input v-model="filterType" placeholder="Filter by type (image, document, video, audio)" />
      </div>

      <div v-if="isLoading" class="loading">Loading assets...</div>
      <div v-else-if="filteredAssets.length === 0" class="empty">
        <p>No assets yet. <a href="#" @click.prevent="showUpload = true">Upload one</a></p>
      </div>

      <div v-else class="assets-grid">
        <div v-for="asset in filteredAssets" :key="asset.id" class="asset-card">
          <div class="asset-preview">
            <span class="file-icon">📄</span>
          </div>
          <div class="asset-info">
            <h4>{{ asset.original_filename }}</h4>
            <p class="asset-meta">
              {{ formatFileSize(asset.file_size) }} • {{ asset.file_type }}
            </p>
            <p class="asset-date">{{ formatDate(asset.created_at) }}</p>
          </div>
          <div class="asset-actions">
            <a :href="`/api/assets/${asset.id}/download`" class="secondary" download>Download</a>
            <button @click="deleteAsset(asset.id)" class="secondary">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { assetsAPI } from '@/api/client'

const showUpload = ref(false)
const dragover = ref(false)
const selectedFiles = ref<File[]>([])
const fileInput = ref<HTMLInputElement>()
const isLoading = ref(false)
const isUploading = ref(false)
const assets = ref<any[]>([])
const filterType = ref('')
const uploadMessage = ref('')
const uploadMessageType = ref('')

const filteredAssets = computed(() => {
  if (!filterType.value) return assets.value
  return assets.value.filter(a => a.file_type === filterType.value)
})

onMounted(async () => {
  await loadAssets()
})

const loadAssets = async () => {
  isLoading.value = true
  try {
    const response = await assetsAPI.list(0, 100)
    assets.value = response.data
  } catch (error) {
    console.error('Error loading assets:', error)
  }
  isLoading.value = false
}

const handleFilesSelected = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files) {
    selectedFiles.value = Array.from(input.files)
  }
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  dragover.value = false
  if (e.dataTransfer?.files) {
    selectedFiles.value = Array.from(e.dataTransfer.files)
  }
}

const uploadFiles = async () => {
  if (selectedFiles.value.length === 0) return

  isUploading.value = true
  uploadMessage.value = ''

  try {
    await assetsAPI.uploadMultiple(selectedFiles.value)
    uploadMessage.value = `Successfully uploaded ${selectedFiles.value.length} file(s)`
    uploadMessageType.value = 'success'
    selectedFiles.value = []
    await loadAssets()
    setTimeout(() => {
      showUpload.value = false
      uploadMessage.value = ''
    }, 2000)
  } catch (error: any) {
    uploadMessage.value = error.response?.data?.detail || 'Upload failed'
    uploadMessageType.value = 'error'
  } finally {
    isUploading.value = false
  }
}

const deleteAsset = async (id: number) => {
  if (confirm('Delete this asset?')) {
    try {
      await assetsAPI.delete(id)
      await loadAssets()
    } catch (error) {
      console.error('Error deleting asset:', error)
    }
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
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

.upload-section {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.upload-area {
  border: 2px dashed var(--border);
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  transition: all 0.2s;
  margin-bottom: 1rem;
}

.upload-area.active {
  border-color: var(--primary);
  background-color: rgba(37, 99, 235, 0.05);
}

.upload-area button {
  padding: 12px 24px;
}

.selected-info {
  margin-top: 1rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.upload-actions {
  display: flex;
  gap: 1rem;
}

.upload-actions button {
  flex: 1;
}

.upload-message {
  padding: 1rem;
  border-radius: 6px;
  margin-top: 1rem;
}

.upload-message.success {
  background-color: #dcfce7;
  color: #15803d;
}

.upload-message.error {
  background-color: #fee2e2;
  color: #991b1b;
}

.assets-section {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 2rem;
}

.filters {
  margin-bottom: 1.5rem;
}

.filters input {
  width: 100%;
  max-width: 300px;
}

.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.asset-card {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s;
}

.asset-card:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.asset-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120px;
  background-color: var(--surface);
  border-radius: 6px;
  margin-bottom: 1rem;
}

.file-icon {
  font-size: 3rem;
}

.asset-info h4 {
  margin: 0.5rem 0;
  word-break: break-word;
}

.asset-meta {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0.25rem 0;
}

.asset-date {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin: 0.5rem 0 1rem 0;
}

.asset-actions {
  display: flex;
  gap: 0.5rem;
}

.asset-actions a,
.asset-actions button {
  flex: 1;
  padding: 8px 12px;
  font-size: 0.9rem;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}
</style>
