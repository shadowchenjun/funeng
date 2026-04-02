import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue')
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('../views/ProductsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('../views/CategoriesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/smart-agriculture',
    name: 'SmartAgriculture',
    component: () => import('../views/SmartAgriculture.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/digital-marketing',
    name: 'DigitalMarketing',
    component: () => import('../views/DigitalMarketing.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/cold-chain',
    name: 'ColdChain',
    component: () => import('../views/ColdChain.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/supply-chain-finance',
    name: 'SupplyChainFinance',
    component: () => import('../views/SupplyChainFinance.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/claude-code',
    name: 'ClaudeCodeAssistant',
    component: () => import('../views/ClaudeCodeAssistant.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null

  // 需要登录的页面
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 需要管理员权限的页面
  if (to.meta.requiresAdmin && !user?.is_admin) {
    next('/dashboard')
    return
  }

  // 已登录用户访问登录/注册页，跳转到仪表盘
  if ((to.path === '/login' || to.path === '/register') && token) {
    next('/dashboard')
    return
  }

  next()
})

export default router
