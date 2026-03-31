import request from '../utils/request'
import type { User, PageResponse } from '../types'

export const userApi = {
  getUsers(params?: {
    keyword?: string
    is_active?: boolean
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) {
    return request.get<PageResponse<User>>('/admin/user/users', { params })
  },

  getUser(id: number) {
    return request.get(`/admin/user/users/${id}`)
  },

  updateUserStatus(id: number, isActive: boolean) {
    return request.put(`/admin/user/users/${id}/status`, { is_active: isActive })
  },

  // 用户分组
  getGroups() {
    return request.get('/admin/user/groups')
  },

  createGroup(data: { name: string; code: string; description?: string; criteria?: string }) {
    return request.post('/admin/user/groups', data)
  },

  updateGroup(id: number, data: Partial<{ name: string; description: string; criteria: string; is_active: boolean }>) {
    return request.put(`/admin/user/groups/${id}`, data)
  },

  deleteGroup(id: number) {
    return request.delete(`/admin/user/groups/${id}`)
  }
}
