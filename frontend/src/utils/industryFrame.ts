/** Bind authenticated API data to the existing dashboard designs, never to baked-in observations. */
export interface DashboardSnapshot {
  meta: {
    last_import_at: string | null
    automatic_collection: boolean
    collection_runs?: { source_id: string; status: string; finished_at: string | null }[]
    industry_total: number
    market_total: number
    market_returned: number
    market_truncated: boolean
    price_from: string | null
    price_to: string | null
  }
  industry: Record<string, unknown>
  market: { rows: unknown[]; history: unknown[]; sources: unknown[] }
}

export function scriptJson(value: unknown): string {
  // Escaping '<' also prevents untrusted source text closing an inline script.
  return JSON.stringify(value).replace(/[<>&\u2028\u2029]/g, char =>
    `\\u${char.charCodeAt(0).toString(16).padStart(4, '0')}`
  )
}

export function buildIndustryFrame(
  data: DashboardSnapshot,
  industryTemplate: string,
  marketTemplate: string,
  centers: unknown
): string {
  const bind = (template: string, values: Record<string, unknown>): string =>
    template.replace(/__[A-Z_]+__/g, marker => {
      if (!(marker in values)) throw new Error(`大屏模板缺少数据绑定：${marker}`)
      return scriptJson(values[marker])
    })
  const market = bind(marketTemplate, {
    __ROWS__: data.market.rows,
    __HISTORY__: data.market.history,
    __CENTERS__: centers,
    __META__: data.meta,
    __MARKET_SOURCES__: data.market.sources
  })
  return bind(industryTemplate, {
    __SNAPSHOT__: data.industry,
    __META__: data.meta,
    __MARKET_DOCUMENT__: market
  })
}
