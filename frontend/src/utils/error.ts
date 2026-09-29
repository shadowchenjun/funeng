import axios from 'axios'

/**
 * 从请求异常中提取可展示的错误信息。
 * 兼容 FastAPI 的 `detail` 字符串与 422 校验错误数组，其余情况返回 fallback。
 */
export function getErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail: unknown = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      const msgs = detail
        .map((d) => (d && typeof d === 'object' && 'msg' in d ? String(d.msg) : ''))
        .filter(Boolean)
      if (msgs.length) return msgs.join('；')
    }
  }
  return fallback
}
