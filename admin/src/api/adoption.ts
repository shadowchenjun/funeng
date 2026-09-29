import request from '../utils/request'
import type { OrderStatus, StatusUpdateBody, AdoptionCategory, AdoptionConfig, AdoptionOrder, CreatedResponse, MessageResponse, PageResponse } from '../types'

/** 认养管理 API（/api/admin/adoption/*），写接口以 JSON body 提交。 */
export const adoptionApi = {
  // 认养分类
  getCategories() {
    return request.get<AdoptionCategory[]>('/admin/adoption/categories')
  },

  createCategory(data: { name: string; code: string; icon?: string; description?: string; sort_order?: number }) {
    return request.post<CreatedResponse>('/admin/adoption/categories', data)
  },

  updateCategory(id: number, data: Partial<{ name: string; icon: string; description: string; sort_order: number; is_active: boolean }>) {
    return request.put<MessageResponse>(`/admin/adoption/categories/${id}`, data)
  },

  deleteCategory(id: number) {
    return request.delete<MessageResponse>(`/admin/adoption/categories/${id}`)
  },

  // 认养配置
  getConfigs(params?: { category_id?: number; is_active?: boolean }) {
    return request.get<AdoptionConfig[]>('/admin/adoption/configs', { params })
  },

  getConfig(id: number) {
    return request.get<AdoptionConfig>(`/admin/adoption/configs/${id}`)
  },

  /** benefits / images 为数组时会被序列化为 JSON 字符串（后端按 JSON 字符串存储） */
  createConfig(data: {
    category_id: number
    name: string
    price: number
    duration_days: number
    description?: string
    unit?: string
    benefits?: string[]
    images?: string[]
    stock?: number
  }) {
    return request.post<CreatedResponse>('/admin/adoption/configs', data)
  },

  // 认养订单
  getOrders(params?: {
    status?: string
    user_id?: number
    config_id?: number
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) {
    return request.get<PageResponse<AdoptionOrder>>('/admin/adoption/orders', { params })
  },

  getOrder(id: number) {
    return request.get<AdoptionOrder>(`/admin/adoption/orders/${id}`)
  },

  updateOrderStatus(id: number, status: OrderStatus, remark?: string) {
    const body: StatusUpdateBody = { status, remark: remark || undefined }
    return request.put<MessageResponse>(`/admin/adoption/orders/${id}/status`, body)
  }
}
