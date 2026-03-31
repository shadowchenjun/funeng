import request from '../utils/request'
import type { AdoptionCategory, AdoptionConfig, AdoptionOrder, PageResponse } from '../types'

export const adoptionApi = {
  // 认养分类
  getCategories() {
    return request.get<AdoptionCategory[]>('/admin/adoption/categories')
  },

  createCategory(data: { name: string; code: string; icon?: string; description?: string; sort_order?: number }) {
    return request.post('/admin/adoption/categories', data)
  },

  // 认养配置
  getConfigs(params?: { category_id?: number; is_active?: boolean }) {
    return request.get<AdoptionConfig[]>('/admin/adoption/configs', { params })
  },

  getConfig(id: number) {
    return request.get<AdoptionConfig>(`/admin/adoption/configs/${id}`)
  },

  createConfig(data: {
    category_id: number
    name: string
    price: number
    duration_days: number
    description?: string
    unit?: string
    benefits?: any
    stock?: number
  }) {
    return request.post('/admin/adoption/configs', data)
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

  updateOrderStatus(id: number, status: string, remark?: string) {
    return request.put(`/admin/adoption/orders/${id}/status`, { status, remark })
  }
}
