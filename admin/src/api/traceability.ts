import request from '../utils/request'
import type { CreatedResponse, MessageResponse, TraceabilityConfig, TraceabilityNode, TraceabilityRecord, PageResponse } from '../types'

/** 溯源管理 API（/api/admin/traceability/*），写接口以 JSON body 提交。 */
export const traceabilityApi = {
  // 溯源配置
  getConfigs(params?: { is_active?: boolean }) {
    return request.get<TraceabilityConfig[]>('/admin/traceability/configs', { params })
  },

  createConfig(data: { name: string; code: string; description?: string; land_parcel_id?: number }) {
    return request.post<CreatedResponse>('/admin/traceability/configs', data)
  },

  updateConfig(id: number, data: Partial<{ name: string; description: string; land_parcel_id: number; is_active: boolean }>) {
    return request.put<MessageResponse>(`/admin/traceability/configs/${id}`, data)
  },

  // 溯源节点
  getNodes(configId: number) {
    return request.get<TraceabilityNode[]>(`/admin/traceability/configs/${configId}/nodes`)
  },

  createNode(data: {
    config_id: number
    name: string
    node_type: string
    icon?: string
    description?: string
    sort_order?: number
    data_fields?: string
  }) {
    return request.post<CreatedResponse>('/admin/traceability/nodes', data)
  },

  updateNode(id: number, data: Partial<{
    name: string
    node_type: string
    icon: string
    description: string
    sort_order: number
    data_fields: string
    is_active: boolean
  }>) {
    return request.put<MessageResponse>(`/admin/traceability/nodes/${id}`, data)
  },

  deleteNode(id: number) {
    return request.delete<MessageResponse>(`/admin/traceability/nodes/${id}`)
  },

  // 溯源记录
  getRecords(params?: {
    node_id?: number
    adoption_order_id?: number
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) {
    return request.get<PageResponse<TraceabilityRecord>>('/admin/traceability/records', { params })
  },

  getRecord(id: number) {
    return request.get<TraceabilityRecord>(`/admin/traceability/records/${id}`)
  },

  createRecord(data: {
    node_id: number
    data: string
    adoption_order_id?: number
    image_url?: string
    operator?: string
  }) {
    return request.post<CreatedResponse>('/admin/traceability/records', data)
  }
}
