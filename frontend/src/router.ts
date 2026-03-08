import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Pages
import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import DashboardPage from '@/pages/DashboardPage.vue'
import DocumentsPage from '@/pages/DocumentsPage.vue'
import DocumentEditorPage from '@/pages/DocumentEditorPage.vue'
import AssetsPage from '@/pages/AssetsPage.vue'
import CollectionsPage from '@/pages/CollectionsPage.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'dashboard',
    component: DashboardPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/documents',
    name: 'documents',
    component: DocumentsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/documents/:id/edit',
    name: 'document-editor',
    component: DocumentEditorPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/documents/:id',
    name: 'document-view',
    component: DocumentEditorPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/assets',
    name: 'assets',
    component: AssetsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/collections',
    name: 'collections',
    component: CollectionsPage,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if ((to.name === 'login' || to.name === 'register') && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
