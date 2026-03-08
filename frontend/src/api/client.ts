import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// Auth API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login', credentials),
  getMe: () =>
    api.get('/auth/me'),
  logout: () => {
    localStorage.removeItem('auth_token')
  }
}

// User API
export const userAPI = {
  register: (user: { username: string; email: string; password: string; full_name?: string }) =>
    api.post('/users/', user),
  getProfile: (userId: number) =>
    api.get(`/users/${userId}`),
  listUsers: (skip = 0, limit = 100) =>
    api.get('/users/', { params: { skip, limit } })
}

// Collections API
export const collectionsAPI = {
  create: (collection: { name: string; description?: string; slug: string }) =>
    api.post('/collections/', collection),
  get: (id: number) =>
    api.get(`/collections/${id}`),
  getBySlug: (slug: string) =>
    api.get(`/collections/by-slug/${slug}`),
  list: (skip = 0, limit = 100) =>
    api.get('/collections/', { params: { skip, limit } }),
  update: (id: number, data: any) =>
    api.put(`/collections/${id}`, data),
  delete: (id: number) =>
    api.delete(`/collections/${id}`)
}

// Documents API
export const documentsAPI = {
  create: (document: any) =>
    api.post('/documents/', document),
  get: (id: number) =>
    api.get(`/documents/${id}`),
  getBySlug: (slug: string) =>
    api.get(`/documents/by-slug/${slug}`),
  list: (skip = 0, limit = 100, collectionId?: number, ownerId?: number) =>
    api.get('/documents/', { params: { skip, limit, collection_id: collectionId, owner_id: ownerId } }),
  update: (id: number, data: any) =>
    api.put(`/documents/${id}`, data),
  delete: (id: number) =>
    api.delete(`/documents/${id}`),
  render: (id: number) =>
    api.post(`/documents/${id}/render/`)
}

// Assets API
export const assetsAPI = {
  upload: (file: File, collectionId?: number) => {
    const formData = new FormData()
    formData.append('file', file)
    if (collectionId) {
      formData.append('collection_id', collectionId.toString())
    }
    return api.post('/assets/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  uploadMultiple: (files: File[], collectionId?: number) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    if (collectionId) {
      formData.append('collection_id', collectionId.toString())
    }
    return api.post('/assets/upload-multiple/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  get: (id: number) =>
    api.get(`/assets/${id}`),
  list: (skip = 0, limit = 100, collectionId?: number, fileType?: string, uploadedBy?: number) =>
    api.get('/assets/', { 
      params: { skip, limit, collection_id: collectionId, file_type: fileType, uploaded_by: uploadedBy } 
    }),
  download: (id: number) =>
    api.get(`/assets/${id}/download`, { responseType: 'blob' }),
  delete: (id: number) =>
    api.delete(`/assets/${id}`),
  linkToDocument: (assetId: number, documentId: number) =>
    api.post(`/assets/${assetId}/link-to-document/${documentId}`),
  unlinkFromDocument: (assetId: number, documentId: number) =>
    api.delete(`/assets/${assetId}/unlink-from-document/${documentId}`),
  stats: () =>
    api.get('/assets/stats/')
}

// Comments API
export const commentsAPI = {
  create: (documentId: number, comment: any) =>
    api.post(`/documents/${documentId}/comments/`, comment),
  list: (documentId: number) =>
    api.get(`/documents/${documentId}/comments/`),
  resolve: (commentId: number) =>
    api.post(`/comments/${commentId}/resolve/`),
  delete: (commentId: number) =>
    api.delete(`/comments/${commentId}`)
}
