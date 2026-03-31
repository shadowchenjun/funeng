import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AdminUser } from '../types'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('admin_token'))
  const user = ref<AdminUser | null>(null)

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('admin_token', newToken)
  }

  const setUser = (newUser: AdminUser) => {
    user.value = newUser
    localStorage.setItem('admin_user', JSON.stringify(newUser))
  }

  const login = async (username: string, password: string) => {
    const res = await authApi.login({ username, password })
    setToken(res.access_token)
    setUser(res.admin)
    return res
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (e) {
      // ignore
    }
    token.value = null
    user.value = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
  }

  const fetchProfile = async () => {
    if (!token.value) return null
    try {
      const res = await authApi.getProfile()
      user.value = res
      return res
    } catch (e) {
      logout()
      return null
    }
  }

  const initFromStorage = () => {
    const storedUser = localStorage.getItem('admin_user')
    if (storedUser) {
      user.value = JSON.parse(storedUser)
    }
  }

  return {
    token,
    user,
    setToken,
    setUser,
    login,
    logout,
    fetchProfile,
    initFromStorage
  }
})
