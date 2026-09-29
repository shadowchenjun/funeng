import request from '../utils/request'
import type { Coupon, Activity, CreatedResponse, MessageResponse, PageResponse } from '../types'

/**
 * 营销管理 API（/api/admin/marketing/*），写接口以 JSON body 提交。
 * 时间字段（valid_from / valid_until / start_time / end_time）后端用
 * datetime.fromisoformat 解析，需传 ISO 格式字符串，如 2026-01-01T00:00:00。
 */
export const marketingApi = {
  // 优惠券
  getCoupons(params?: { is_active?: boolean; type?: string; page?: number; page_size?: number }) {
    return request.get<PageResponse<Coupon>>('/admin/marketing/coupons', { params })
  },

  getCoupon(id: number) {
    return request.get<Coupon>(`/admin/marketing/coupons/${id}`)
  },

  createCoupon(data: {
    name: string
    code: string
    discount_value: number
    valid_from: string
    valid_until: string
    type?: string
    min_amount?: number
    max_discount?: number
    total_count?: number
    per_user_limit?: number
  }) {
    return request.post<CreatedResponse>('/admin/marketing/coupons', data)
  },

  updateCoupon(id: number, data: Partial<{
    name: string
    discount_value: number
    valid_from: string
    valid_until: string
    type: string
    min_amount: number
    max_discount: number
    total_count: number
    per_user_limit: number
    is_active: boolean
  }>) {
    return request.put<MessageResponse>(`/admin/marketing/coupons/${id}`, data)
  },

  deleteCoupon(id: number) {
    return request.delete<MessageResponse>(`/admin/marketing/coupons/${id}`)
  },

  // 活动
  getActivities(params?: { status?: string; type?: string; page?: number; page_size?: number }) {
    return request.get<PageResponse<Activity>>('/admin/marketing/activities', { params })
  },

  getActivity(id: number) {
    return request.get<Activity>(`/admin/marketing/activities/${id}`)
  },

  createActivity(data: {
    name: string
    type: string
    start_time: string
    end_time: string
    description?: string
    rules?: object
    banner_url?: string
  }) {
    return request.post<CreatedResponse>('/admin/marketing/activities', data)
  },

  deleteActivity(id: number) {
    return request.delete<MessageResponse>(`/admin/marketing/activities/${id}`)
  }
}
