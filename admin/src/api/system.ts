import request, { toQuery } from '../utils/request'
import type { CreatedResponse, MessageResponse, PageResponse } from '../types'

export type SystemConfigValue = string | number | boolean | object
export type SystemConfigType = 'string' | 'number' | 'boolean' | 'json'

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

/** 系统配置 / 操作日志 API（/api/admin/system/*），写接口以 JSON body 提交。 */
export const systemApi = {
  // 系统配置
  getConfigs(group?: string) {
    return request.get<SystemConfig[]>('/admin/system/configs', { params: toQuery({ group }) })
  },

  getConfig(key: string) {
    return request.get<SystemConfig>(`/admin/system/configs/${key}`)
  },

  /** value 可为字符串，json 类型配置也可直接传对象/数组 */
  updateConfig(key: string, value: SystemConfigValue) {
    return request.put<MessageResponse>(`/admin/system/configs/${key}`, { value })
  },

  createConfig(data: {
    key: string
    value: SystemConfigValue
    type?: SystemConfigType
    group?: string
    description?: string
    is_public?: boolean
  }) {
    return request.post<CreatedResponse>('/admin/system/configs', data)
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
