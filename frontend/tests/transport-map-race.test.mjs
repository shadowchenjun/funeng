// 冷链运输地图异步重画回归（review R2）：快速切换路线时，迟到的旧请求不得覆盖当前选择，卸载后不得写入。
// 做法：从 ColdChain.vue 截取 initTransportMap 源码，在受控的高德 SDK 桩中手动控制地理编码回调顺序。
// 这是异步控制流测试，不是真实地图渲染验收。运行：npm --prefix frontend test
import test from 'node:test'
import assert from 'node:assert/strict'
import { loadTs, extractBetween } from './helpers.mjs'

const { createLatestGuard } = loadTs('src/utils/latest.ts')
const fnSource = extractBetween('src/views/ColdChain.vue', 'const initTransportMap = () =>', '// GET /monitoring/temperature')

function setup () {
  const pending = []
  const jobs = []
  const maps = []
  class MapStub {
    constructor () { this.overlays = []; maps.push(this) }
    clearMap () { this.overlays = [] }
    add (x) { this.overlays.push(x.options) }
    setFitView () {}
  }
  class Overlay { constructor (options) { this.options = options } }
  const ctx = {
    console, Date,
    transportMap: null,
    transportGuard: createLatestGuard(),
    document: { getElementById: () => ({}) },
    window: { AMap: { Map: MapStub, Marker: Overlay, Icon: Overlay, Polyline: Overlay,
      Geocoder: class { getLocation (city, cb) { pending.push({ city, cb }) } } } },
    nextTick: cb => { jobs.push(Promise.resolve().then(cb)) },
    waitForAMap: async () => {},
    transports: { value: [
      { id: 'A', route: 'Alpha-Omega', waypoints: [{ name: 'A-start', lng: 1, lat: 1 }, { name: 'A-end', lng: 2, lat: 2 }] },
      { id: 'B', route: 'Beta-Delta', waypoints: [{ name: 'B-start', lng: 3, lat: 3 }, { name: 'B-end', lng: 4, lat: 4 }] }
    ] },
    selectedTransportId: { value: 'A' },
    transportData: { value: [] }
  }
  const run = loadTs.inContext(fnSource + '\nglobalThis.__redraw = initTransportMap;', ctx)
  const turn = () => new Promise(resolve => setImmediate(resolve))
  const resolveCity = async (city) => {
    const i = pending.findIndex(x => x.city === city)
    if (i < 0) return false
    pending.splice(i, 1)[0].cb('complete', { geocodes: [{ location: { lng: 1, lat: 1 } }] })
    await turn()
    return true
  }
  const drain = async () => { while (pending.length) await resolveCity(pending[0].city); await Promise.all(jobs) }
  return { ctx, run, maps, turn, resolveCity, drain }
}

const titles = (map) => map.overlays.filter(x => x.title).map(x => x.title)

test('A→B 且 A 的地理编码后返回：只显示 B 的路线与时间线', async () => {
  const { ctx, maps, turn, resolveCity, drain } = setup()
  ctx.__redraw(); await turn()
  ctx.selectedTransportId.value = 'B'
  ctx.__redraw(); await turn()
  await resolveCity('Beta'); await resolveCity('Delta')
  await resolveCity('Alpha'); await resolveCity('Omega')
  await drain()

  assert.equal(maps.length, 1, '地图实例只建一次')
  assert.deepEqual(ctx.transportData.value.map(x => x.location), ['B-start', 'B-end'])
  assert.deepEqual(titles(maps[0]), ['起点: Beta', '终点: Delta'])
})

test('A→B→A 快速切换：最终与选择 A 一致', async () => {
  const { ctx, maps, turn, resolveCity, drain } = setup()
  ctx.__redraw(); await turn()
  ctx.selectedTransportId.value = 'B'; ctx.__redraw(); await turn()
  ctx.selectedTransportId.value = 'A'; ctx.__redraw(); await turn()
  await resolveCity('Beta'); await resolveCity('Delta')
  await drain()

  assert.deepEqual(ctx.transportData.value.map(x => x.location), ['A-start', 'A-end'])
  assert.deepEqual(titles(maps[0]), ['起点: Alpha', '终点: Omega'])
})

test('卸载后迟到的回调不写入地图与时间线', async () => {
  const { ctx, maps, turn, drain } = setup()
  ctx.__redraw(); await turn()
  ctx.transportGuard.invalidate() // onBeforeUnmount 中调用
  await drain()

  assert.deepEqual(ctx.transportData.value, [])
  assert.ok(maps.every(m => m.overlays.length === 0))
})
