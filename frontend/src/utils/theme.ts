/**
 * 设计令牌的色值副本，仅供无法使用 CSS 变量的场景（el-progress 的 SVG stroke、地图覆盖物等）。
 * 与 App.vue :root 中的 --primary / --color-* 保持一致；能用 CSS 变量的地方一律用变量。
 */
export const themeColors = {
  primary: '#165DFF',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#64748B'
} as const

/** 按阈值取「好 / 中 / 差」三档颜色：value >= good → success，>= fair → warning，否则 danger */
export const levelColor = (value: number, good: number, fair: number): string =>
  value >= good ? themeColors.success : value >= fair ? themeColors.warning : themeColors.danger
