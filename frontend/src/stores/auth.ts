/**
 * 认证状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE = '/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const userInfo = ref<{ is_admin?: boolean; username?: string } | null>(null)

  // 修复：如果 localStorage 存的是 "undefined" 字符串
  if (!user.value || user.value === 'undefined') {
    user.value = null
    localStorage.removeItem('user')
  }

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.is_admin || false)

  // 配置 axios
  function updateAxiosConfig() {
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }

  // 登录
  async function login(username: string, password: string) {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await axios.post(`${API_BASE}/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      const { access_token, user: userData } = response.data
      
      token.value = access_token
      user.value = userData
      userInfo.value = userData
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      updateAxiosConfig()
      
      return { success: true }
    } catch (error: any) {
      const message = error.response?.data?.detail || '登录失败'
      return { success: false, message }
    }
  }

  // 注册
  async function register(userData: {
    username: string
    password: string
    email?: string
    full_name?: string
  }) {
    try {
      const response = await axios.post(`${API_BASE}/auth/register`, userData)
      return { success: true, data: response.data }
    } catch (error: any) {
      const message = error.response?.data?.detail || '注册失败'
      return { success: false, message }
    }
  }

  // 获取当前用户信息
  async function fetchUserInfo() {
    if (!token.value) return
    
    try {
      updateAxiosConfig()
      const response = await axios.get(`${API_BASE}/auth/me`)
      userInfo.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (error) {
      logout()
    }
  }

  // 登出
  function logout() {
    token.value = ''
    user.value = null
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
  }

  // 初始化
  function init() {
    if (token.value) {
      updateAxiosConfig()
      // 如果本地存储的用户信息存在，先设置 userInfo
      if (user.value && typeof user.value === 'object' && user.value.is_admin !== undefined) {
        userInfo.value = user.value
      }
      fetchUserInfo()
    }
  }

  return {
    token,
    user,
    userInfo,
    isLoggedIn,
    isAdmin,
    login,
    register,
    fetchUserInfo,
    logout,
    init
  }
})
