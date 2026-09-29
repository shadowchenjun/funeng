import axios, { type AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const instance = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_user')
        ElMessage.error('登录已过期，请重新登录')
        router.push('/login')
      } else if (status === 403) {
        ElMessage.error('没有权限访问')
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在')
      } else if (status === 500) {
        ElMessage.error('服务器错误')
      } else {
        // FastAPI 422 的 detail 是校验错误数组
        const detail = Array.isArray(data?.detail)
          ? data.detail.map((d: { msg?: string; loc?: unknown[] }) => `${(d.loc || []).slice(-1)[0] ?? ''} ${d.msg ?? ''}`.trim()).join('; ')
          : data?.detail
        ElMessage.error(detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器已把 response 解包为 response.data，因此对外暴露的请求方法
 * 直接返回后端 JSON（Promise<T>），而不是 AxiosResponse<T>。
 *
 * 管理端写接口（POST / PUT）统一以 JSON body 提交，字段名与后端
 * backend/app/schemas/admin.py 中的 Pydantic 模型一致（未声明字段会被 422 拒绝）。
 * `{ params }` 只用于 GET 的筛选 / 分页参数。
 */
export interface RequestClient {
  get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
}

const request: RequestClient = {
  get: (url, config) => instance.get(url, config),
  delete: (url, config) => instance.delete(url, config),
  post: (url, data, config) => instance.post(url, data, config),
  put: (url, data, config) => instance.put(url, data, config)
}

export default request

export type QueryValue = string | number | boolean | null | undefined | object

/**
 * 把筛选对象转换为 GET query 参数（仅用于读接口，写接口请直接传 JSON body）：
 * - 丢弃 undefined / null / 空字符串（避免 FastAPI 对 Optional[int] 等字段解析 '' 报 422）
 * - 数组 / 对象序列化为 JSON 字符串
 */
export function toQuery(data: object): Record<string, string | number | boolean> {
  const out: Record<string, string | number | boolean> = {}
  for (const [key, value] of Object.entries(data as Record<string, QueryValue>)) {
    if (value === undefined || value === null || value === '') continue
    out[key] = typeof value === 'object' ? JSON.stringify(value) : value
  }
  return out
}
