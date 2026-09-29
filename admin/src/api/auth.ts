import request from '../utils/request'
import type { AdminRoleSummary, AdminUser, MessageResponse } from '../types'

export interface LoginData {
  username: string
  password: string
}

/** 登录接口返回的精简管理员信息（role 与 profile 接口结构一致） */
export interface LoginAdmin {
  id: number
  username: string
  full_name?: string | null
  email?: string | null
  avatar?: string | null
  role?: AdminRoleSummary | null
}

export interface LoginResponse {
  access_token: string
  token_type: string
  admin: LoginAdmin
}

/** 管理员认证 API（/api/admin/auth/*） */
export const authApi = {
  // 后端使用 OAuth2 密码模式，需以表单格式提交
  login(data: LoginData) {
    const form = new URLSearchParams({ username: data.username, password: data.password })
    return request.post<LoginResponse>('/admin/auth/login', form)
  },

  logout() {
    return request.post<MessageResponse>('/admin/auth/logout')
  },

  getProfile() {
    return request.get<AdminUser>('/admin/auth/profile')
  },

  updateProfile(data: Partial<Pick<AdminUser, 'full_name' | 'email' | 'phone' | 'avatar'>>) {
    return request.put<MessageResponse>('/admin/auth/profile', data)
  },

  // 密码只能放在 JSON body 中，不能出现在 URL
  changePassword(oldPassword: string, newPassword: string) {
    return request.post<MessageResponse>('/admin/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
  }
}
