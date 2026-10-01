import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'
import test from 'node:test'
import { loadTs } from './helpers.mjs'

const { buildIndustryFrame, scriptJson } = loadTs('src/utils/industryFrame.ts')
const template = name => fs.readFileSync(new URL(`../src/dashboard/${name}.html`, import.meta.url), 'utf8')
const data = () => ({
  meta: { last_import_at: null, automatic_collection: false, market_total: 0, market_returned: 0, market_truncated: false, price_from: null, price_to: null },
  industry: { observations: [], manual_observations: [], sources: [], reference_sources: [], cold_nodes: [], market_record_count: 0 },
  market: { rows: [], history: [], sources: [] }
})
const script = html => html.split('<script>')[1].split('</script>')[0]
function browserContext (html) {
  const elements = new Map()
  const element = id => {
    if (!elements.has(id)) elements.set(id, { innerHTML: '', textContent: '', value: id === 'trend-select' ? '28种蔬菜' : '', style: {}, dataset: {}, events: {}, addEventListener (type, fn) { this.events[type] = fn }, showModal () { this.open = true }, close () { this.open = false } })
    return elements.get(id)
  }
  const ctx = vm.createContext({ document: { getElementById: element, querySelectorAll: () => [], querySelector: () => ({ hidden: false }) }, URL, Blob, setTimeout: () => {}, console })
  vm.runInContext(script(html), ctx)
  return { ctx, element }
}
function frames (input) {
  const html = buildIndustryFrame(input, template('industry'), template('market'), {})
  const ctx = vm.createContext({})
  const declaration = script(html).split('\nconst $=')[0]
  vm.runInContext(`${declaration};globalThis.market=MARKET_DOCUMENT`, ctx)
  return { html, market: ctx.market }
}

test('inline data cannot close scripts, inject HTML or break nested document', () => {
  const hostile = '</script><script>alert(1)</script>&\u2028'
  assert.equal(JSON.parse(scriptJson(hostile)), hostile)
  assert.ok(!scriptJson(hostile).includes('<'))
  const d = data()
  d.industry.sources.push({ name: hostile, source_id: 'evil', url: 'javascript:alert(1)', status: 'collected' })
  const { html, market } = frames(d)
  assert.equal((html.match(/<script>/g) || []).length, 1)
  new vm.Script(script(html))
  new vm.Script(script(market))
  const b = browserContext(html)
  vm.runInContext("$('source-open').onclick()", b.ctx)
  assert.ok(b.element('source-list').innerHTML.includes('&lt;/script&gt;'))
  assert.ok(!b.element('source-list').innerHTML.includes('javascript:'))
})

test('all six pages and both finance modes render genuine empty states', () => {
  const { html, market } = frames(data())
  const b = browserContext(html)
  for (const p of ['overview', 'crop', 'cold', 'risk', 'finance', 'market']) vm.runInContext(`page='${p}';render()`, b.ctx)
  assert.equal(b.element('market-frame').srcdoc, market)
  vm.runInContext("page='finance';mode='platform';render()", b.ctx)
  assert.ok(b.element('content').innerHTML.includes('待接入'))
  const m = browserContext(market)
  assert.equal(m.element('record-count').textContent, '0')
  assert.ok(m.element('national-quotes').innerHTML.includes('暂无'))
})

test('quarterly financial precision and province filtering preserve their population', () => {
  const d = data()
  d.industry.observations = [
    { metric: 'agricultural_related_credit', metric_name: '涉农贷款余额', region: '全国', source_id: 'pbc_credit', value: '53.570001', unit: '万亿元', measure_type: 'balance', frequency: 'quarterly', period_start: '2025-10-01', period_end: '2025-12-31' },
    { metric: 'grain_production', metric_name: '粮食产量', region: '山东省', value: '5771.3', unit: '万吨', frequency: 'annual', period_end: '2025-12-31' }
  ]
  const b = browserContext(frames(d).html)
  vm.runInContext("page='finance';render()", b.ctx)
  assert.ok(b.element('content').innerHTML.includes('53.570001'))
  assert.ok(b.element('content').innerHTML.includes('2025-10-01–2025-12-31'))
  vm.runInContext("page='crop';region='山东省';render()", b.ctx)
  assert.equal(vm.runInContext('exportRows.length', b.ctx), 1)
  vm.runInContext("region='北京市';render()", b.ctx)
  assert.equal(vm.runInContext('exportRows.length', b.ctx), 0)
  assert.ok(b.element('content').innerHTML.includes('暂无该指标数据'))
})

test('market filtering matches details and exports; zero prices render finite trends', () => {
  const d = data()
  const row = { commodity: '28种蔬菜', category: '蔬菜', price_avg: '0', quote_type: 'national_wholesale_mean', observed_date: '2026-09-30', source_id: 'moa_daily', quality_flag: 'ok', source_unit: '元/公斤' }
  d.market.rows = [row, { ...row, commodity: '6种水果', category: '水果' }]
  d.market.history = [row]
  const b = browserContext(frames(d).market)
  assert.ok(!b.element('trend-chart').innerHTML.includes('NaN'))
  vm.runInContext("category='水果';render();renderDetails()", b.ctx)
  assert.equal(vm.runInContext('detailRows().length', b.ctx), 1)
  assert.ok(b.element('detail-body').innerHTML.includes('6种水果'))
  assert.ok(!b.element('detail-body').innerHTML.includes('28种蔬菜'))
  vm.runInContext("search='不存在';renderDetails()", b.ctx)
  assert.equal(vm.runInContext('detailRows().length', b.ctx), 0)
})
