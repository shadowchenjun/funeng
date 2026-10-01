/**
 * 缓存页面（keep-alive）的数据新鲜度追踪。
 *
 * 写入方在增删改成功后 bump(领域)；读取方加载完成时 snapshot(依赖领域)，
 * 页面再次激活时 isStale() 为 true 才重新请求——无变化时保留缓存，超时兜底覆盖其他端的修改。
 * 纯逻辑、无 Vue 依赖，便于单测；页面侧用 composables/useFreshOnActivate.ts。
 */
export type DataDomain = 'products' | 'categories'

export interface DataSnapshot {
  at: number
  domains: DataDomain[]
  versions: number[]
}

export const createDataVersions = (now: () => number = Date.now) => {
  const versions: Record<DataDomain, number> = { products: 0, categories: 0 }
  return {
    bump(domain: DataDomain) {
      versions[domain]++
    },
    snapshot(domains: DataDomain[]): DataSnapshot {
      return { at: now(), domains, versions: domains.map((d) => versions[d]) }
    },
    isStale(snap: DataSnapshot | null, ttlMs: number): boolean {
      if (!snap) return false
      if (now() - snap.at > ttlMs) return true
      return snap.domains.some((d, i) => versions[d] !== snap.versions[i])
    }
  }
}

/** 应用级单例 */
export const dataVersions = createDataVersions()
