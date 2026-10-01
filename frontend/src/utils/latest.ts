/**
 * 「只认最新一次」守卫：异步流程开始时 begin() 拿到一个检查函数，
 * 每个 await 之后调用它，返回 false 说明已有更新的请求或组件已卸载，应立即放弃写入。
 */
export interface LatestGuard {
  begin: () => () => boolean
  invalidate: () => void
}

export const createLatestGuard = (): LatestGuard => {
  let seq = 0
  return {
    begin() {
      const id = ++seq
      return () => id === seq
    },
    invalidate() {
      seq++
    }
  }
}
