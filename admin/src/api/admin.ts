import request from '../utils/request'
import type { AdminUser, PageResponse } from '../types'

export interface AdminRole {
  id: number
  name: string
  code: string
  description?: string
  permissions?: string
  is_active: boolean
}

export const adminApi = {
  // 管理员
  getAdmins(params?: {
    role_id?: number
    is_active?: boolean
    keyword?: string
    page?: number
    page_size?: number
  }) {
    return request.get<PageResponse<AdminUser>>('/admin/admin-user/admins', { params })
  },

  getAdmin(id: number) {
    return request.get<AdminUser>(`/admin/admin-user/admins/${id}`)
  },

  createAdmin(data: {
    username: string
    password: string
    email?: string
    full_name?: string
    phone?: string
    role_id?: number
  }) {
    return request.post('/admin/admin-user/admins', data)
  },

  updateAdmin(id: number, data: Partial<{
    email: string
    full_name: string
    phone: string
    avatar: string
    role_id: number
    is_active: boolean
  }>) {
    return request.put(`/admin/admin-user/admins/${id}`, data)
  },

  resetPassword(id: number, password: string) {
    return request.put(`/admin/admin-user/admins/${id}/password`, { password })
  },

  deleteAdmin(id: number) {
    return request.delete(`/admin/admin-user/admins/${id}`)
  },

  // 角色
  getRoles() {
    return request.get<AdminRole[]>('/admin/admin-user/roles')
  },

  createRole(data: { name: string; code: string; description?: string; permissions?: string }) {
    return request.post('/admin/admin-user/roles', data)
  },

  updateRole(id: number, data: Partial<{
    name: string
    description: string
    permissions: string
    is_active: boolean
  }>) {
    return request.put(`/admin/admin-user/roles/${id}`, data)
  },

  deleteRole(id: number) {
    return request.delete(`/admin/admin-user/roles/${id}`)
  }
}
