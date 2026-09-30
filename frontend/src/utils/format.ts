/**
 * 金额格式化（全站唯一实现，见 UI 统一设计 spec §3.5）
 * 两种口径不可混用：统计概览用 compact，明细/订单用 exact。
 */

/** 万/亿两级缩写，用于统计卡等概览数字：¥1.23亿、¥4.5万、¥800 */
export const formatMoneyCompact = (value: number): string => {
  const n = Number(value || 0)
  if (n >= 100000000) return `¥${(n / 100000000).toFixed(2)}亿`
  if (n >= 10000) return `¥${(n / 10000).toFixed(1)}万`
  return `¥${n.toLocaleString()}`
}

/** ¥ + 千分位，最多两位小数，用于订单、明细等需要精确金额的场景 */
export const formatMoneyExact = (value: number): string =>
  `¥${Number(value || 0).toLocaleString('zh-CN', { maximumFractionDigits: 2 })}`
