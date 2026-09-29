import request from '../utils/request'
import type { AdminListItem, MessageResponse, CreatedResponse, PageResponse } from '../types'

export interface AdminRole {
  id: number
  name: string
  code: string
  description?: string
  permissions?: string
  is_active: boolean
  created_at?: string
}

/**
 * 管理员 / 角色管理 API（/api/admin/admin-user/*）。
 * 写接口以 JSON body 提交（字段与后端 app/schemas/admin.py 一致）。
 */
export const adminApi = {
  // 管理员
  getAdmins(params?: {
    role_id?: number
    is_active?: boolean
    keyword?: string
    page?: number
    page_size?: number
  }) {
    return request.get<PageResponse<AdminListItem>>('/admin/admin-user/admins', { params })
  },

  getAdmin(id: number) {
    return request.get<AdminListItem>(`/admin/admin-user/admins/${id}`)
  },

  createAdmin(data: {
    username: string
    password: string
    email?: string
    full_name?: string
    phone?: string
    role_id?: number
  }) {
    return request.post<CreatedResponse>('/admin/admin-user/admins', data)
  },

  updateAdmin(id: number, data: Partial<{
    email: string
    full_name: string
    phone: string
    avatar: string
    role_id: number
    is_active: boolean
  }>) {
    return request.put<MessageResponse>(`/admin/admin-user/admins/${id}`, data)
  },

  resetPassword(id: number, password: string) {
    // 密码只能放在 JSON body 中，不能出现在 URL
    return request.put<MessageResponse>(`/admin/admin-user/admins/${id}/password`, { password })
  },

  deleteAdmin(id: number) {
    return request.delete<MessageResponse>(`/admin/admin-user/admins/${id}`)
  },

  // 角色
  getRoles() {
    return request.get<AdminRole[]>('/admin/admin-user/roles')
  },

  createRole(data: { name: string; code: string; description?: string; permissions?: string }) {
    return request.post<CreatedResponse>('/admin/admin-user/roles', data)
  },

  updateRole(id: number, data: Partial<{
    name: string
    description: string
    permissions: string
    is_active: boolean
  }>) {
    return request.put<MessageResponse>(`/admin/admin-user/roles/${id}`, data)
  },

  deleteRole(id: number) {
    return request.delete<MessageResponse>(`/admin/admin-user/roles/${id}`)
  }
}
