// 管理员相关类型
export interface AdminUser {
  id: number
  username: string
  full_name?: string
  email?: string
  phone?: string
  avatar?: string
  role?: AdminRole
  last_login?: string
  created_at: string
}

export interface AdminRole {
  id: number
  name: string
  code: string
  description?: string
  permissions?: string
}

// 土地相关类型
export interface LandParcel {
  id: number
  name: string
  code: string
  area: number
  location?: string
  status: string
  type: string
  description?: string
  image_url?: string
  created_at: string
}

// 认养相关类型
export interface AdoptionCategory {
  id: number
  name: string
  code: string
  icon?: string
  description?: string
  sort_order: number
  is_active: boolean
  created_at: string
}

export interface AdoptionConfig {
  id: number
  category_id: number
  category_name?: string
  name: string
  description?: string
  price: number
  unit: string
  duration_days: number
  benefits?: string[]
  images?: string[]
  is_active: boolean
  stock: number
  created_at: string
}

export interface AdoptionOrder {
  id: number
  order_no: string
  user_id: number
  user_name?: string
  config_id: number
  config_name?: string
  land_parcel_id?: number
  land_parcel_name?: string
  quantity: number
  total_amount: number
  status: string
  start_date?: string
  end_date?: string
  harvest_info?: any
  remark?: string
  created_at: string
}

// 设备相关类型
export interface DeviceType {
  id: number
  name: string
  code: string
  icon?: string
  description?: string
  specifications?: any
  is_active: boolean
  created_at: string
}

export interface Device {
  id: number
  name: string
  code: string
  device_type_id: number
  device_type_name?: string
  land_parcel_id?: number
  land_parcel_name?: string
  location?: string
  status: string
  last_active?: string
  firmware_version?: string
  created_at: string
}

export interface MonitoringPoint {
  id: number
  device_id: number
  device_name?: string
  name: string
  data_type: string
  unit?: string
  threshold_min?: number
  threshold_max?: number
  is_active: boolean
}

// 用户相关类型
export interface User {
  id: number
  username: string
  email?: string
  full_name?: string
  is_active: boolean
  is_admin: boolean
  created_at: string
}

// 营销相关类型
export interface Coupon {
  id: number
  name: string
  code: string
  type: string
  discount_value: number
  min_amount: number
  max_discount?: number
  total_count: number
  used_count: number
  per_user_limit: number
  valid_from: string
  valid_until: string
  is_active: boolean
  created_at: string
}

export interface Activity {
  id: number
  name: string
  type: string
  description?: string
  rules?: any
  start_time: string
  end_time: string
  status: string
  banner_url?: string
  created_at: string
}

// 溯源相关类型
export interface TraceabilityConfig {
  id: number
  name: string
  code: string
  description?: string
  land_parcel_id?: number
  land_parcel_name?: string
  is_active: boolean
  created_at: string
}

export interface TraceabilityNode {
  id: number
  config_id: number
  name: string
  node_type: string
  description?: string
  icon?: string
  sort_order: number
  data_fields?: any[]
  is_active: boolean
  created_at: string
}

// 分页响应
export interface PageResponse<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

// 看板统计
export interface DashboardStats {
  users: {
    total: number
    new_today: number
    new_month: number
  }
  land: {
    total: number
    available: number
    rented: number
  }
  adoption_orders: {
    total: number
    today: number
    pending: number
    active: number
    revenue: number
  }
  rental_orders: {
    total: number
    today: number
    pending: number
    revenue: number
  }
  devices: {
    total: number
    online: number
    offline: number
  }
  products: {
    total: number
    categories: number
  }
}
