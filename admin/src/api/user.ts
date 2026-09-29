import request from '../utils/request'
import type { CreatedResponse, MessageResponse, User, UserDetail, UserGroup, PageResponse } from '../types'

/** C 端用户管理 API（/api/admin/user/*），写接口以 JSON body 提交。 */
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
    return request.get<UserDetail>(`/admin/user/users/${id}`)
  },

  updateUserStatus(id: number, isActive: boolean) {
    return request.put<MessageResponse>(`/admin/user/users/${id}/status`, { is_active: isActive })
  },

  // 用户分组
  getGroups() {
    return request.get<UserGroup[]>('/admin/user/groups')
  },

  createGroup(data: { name: string; code: string; description?: string; criteria?: string }) {
    return request.post<CreatedResponse>('/admin/user/groups', data)
  },

  updateGroup(id: number, data: Partial<{ name: string; description: string; criteria: string; is_active: boolean }>) {
    return request.put<MessageResponse>(`/admin/user/groups/${id}`, data)
  },

  deleteGroup(id: number) {
    return request.delete<MessageResponse>(`/admin/user/groups/${id}`)
  }
}
