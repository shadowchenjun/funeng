import request from '../utils/request'
import type { AdminUser } from '../types'

export interface LoginData {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  admin: AdminUser
}

export const authApi = {
  login(data: LoginData) {
    return request.post<LoginResponse>('/admin/auth/login', data)
  },

  logout() {
    return request.post('/admin/auth/logout')
  },

  getProfile() {
    return request.get<AdminUser>('/admin/auth/profile')
  },

  updateProfile(data: Partial<AdminUser>) {
    return request.put('/admin/auth/profile', data)
  },

  changePassword(oldPassword: string, newPassword: string) {
    return request.post('/admin/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
  }
}
