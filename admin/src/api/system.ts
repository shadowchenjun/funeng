import request from '../utils/request'
import type { PageResponse } from '../types'

export interface SystemConfig {
  id: number
  key: string
  value: any
  type: string
  group: string
  description?: string
  is_public: boolean
}

export interface OperationLog {
  id: number
  admin_user_id: number
  admin_username: string
  action: string
  resource: string
  resource_id?: number
  detail?: string
  ip_address?: string
  created_at: string
}

export const systemApi = {
  // 系统配置
  getConfigs(group?: string) {
    return request.get<SystemConfig[]>('/admin/system/configs', { params: { group } })
  },

  getConfig(key: string) {
    return request.get<SystemConfig>(`/admin/system/configs/${key}`)
  },

  updateConfig(key: string, value: string) {
    return request.put(`/admin/system/configs/${key}`, { value })
  },

  createConfig(data: {
    key: string
    value: string
    type?: string
    group?: string
    description?: string
    is_public?: boolean
  }) {
    return request.post('/admin/system/configs', data)
  },

  // 操作日志
  getLogs(params?: {
    admin_user_id?: number
    action?: string
    resource?: string
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) {
    return request.get<PageResponse<OperationLog>>('/admin/system/logs', { params })
  }
}
