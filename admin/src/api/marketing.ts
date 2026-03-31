import request from '../utils/request'
import type { Coupon, Activity, PageResponse } from '../types'

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
    return request.post('/admin/marketing/coupons', data)
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
    rules?: any
    banner_url?: string
  }) {
    return request.post('/admin/marketing/activities', data)
  }
}
