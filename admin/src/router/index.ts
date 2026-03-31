import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../views/layout/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/DashboardView.vue'),
        meta: { title: '数据看板' }
      },
      {
        path: 'adoption',
        name: 'Adoption',
        component: () => import('../views/adoption/AdoptionView.vue'),
        meta: { title: '认养管理' }
      },
      {
        path: 'land',
        name: 'Land',
        component: () => import('../views/land/LandView.vue'),
        meta: { title: '土地管理' }
      },
      {
        path: 'device',
        name: 'Device',
        component: () => import('../views/device/DeviceView.vue'),
        meta: { title: '设备管理' }
      },
      {
        path: 'traceability',
        name: 'Traceability',
        component: () => import('../views/traceability/TraceabilityView.vue'),
        meta: { title: '溯源管理' }
      },
      {
        path: 'user',
        name: 'User',
        component: () => import('../views/user/UserView.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'marketing',
        name: 'Marketing',
        component: () => import('../views/marketing/MarketingView.vue'),
        meta: { title: '营销管理' }
      },
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('../views/admin/AdminView.vue'),
        meta: { title: '管理员管理' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/settings/SettingsView.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  authStore.initFromStorage()

  if (to.meta.requiresAuth !== false && !authStore.token) {
    next('/login')
    return
  }

  if (to.path === '/login' && authStore.token) {
    next('/')
    return
  }

  next()
})

export default router
