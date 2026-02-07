import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '首页', requiresAuth: true }
  },
  {
    path: '/add',
    name: 'AddRecord',
    component: () => import('@/views/AddRecord.vue'),
    meta: { title: '记一笔', requiresAuth: true }
  },
  {
    path: '/records',
    name: 'Records',
    component: () => import('@/views/Records.vue'),
    meta: { title: '账单', requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/Statistics.vue'),
    meta: { title: '统计', requiresAuth: true }
  },
  {
    path: '/budget',
    name: 'Budget',
    component: () => import('@/views/Budget.vue'),
    meta: { title: '预算', requiresAuth: true }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/Projects.vue'),
    meta: { title: '项目', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '我的', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Mobile Ledger'
  
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if ((to.name === 'Login' || to.name === 'Register') && token) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
