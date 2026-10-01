import { onActivated } from 'vue'
import { dataVersions, type DataDomain, type DataSnapshot } from '../utils/dataVersion'

/** 兜底刷新间隔：其他用户或后台的修改最迟在此时间后可见 */
export const CACHE_TTL_MS = 2 * 60 * 1000

/**
 * keep-alive 页面：加载成功后调用 markFresh()；页面再次激活时，
 * 若依赖的数据领域被其他页面写过或已超过 TTL，则调用 refresh()，否则保留缓存（含筛选、分页等界面状态）。
 */
export function useFreshOnActivate(domains: DataDomain[], refresh: () => void | Promise<void>) {
  let snap: DataSnapshot | null = null
  onActivated(() => {
    if (dataVersions.isStale(snap, CACHE_TTL_MS)) void refresh()
  })
  return {
    markFresh() {
      snap = dataVersions.snapshot(domains)
    }
  }
}
