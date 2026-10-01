// 缓存页面的数据新鲜度（review R1）：写入后关联页面需刷新，无变化时保留缓存，超时兜底刷新。
import test from 'node:test'
import assert from 'node:assert/strict'
import { loadTs } from './helpers.mjs'

const { createDataVersions } = loadTs('src/utils/dataVersion.ts')

const setup = () => {
  let t = 1000
  const versions = createDataVersions(() => t)
  return { versions, advance: (ms) => { t += ms } }
}

test('无写入、未超时：缓存仍有效（不重复请求）', () => {
  const { versions, advance } = setup()
  const snap = versions.snapshot(['products', 'categories'])
  advance(30_000)
  assert.equal(versions.isStale(snap, 120_000), false)
})

test('分类页新增分类后，依赖 categories 的产品页需刷新', () => {
  const { versions } = setup()
  const productsPage = versions.snapshot(['products', 'categories'])
  versions.bump('categories')
  assert.equal(versions.isStale(productsPage, 120_000), true)
})

test('产品增删后，分类计数页与看板需刷新；不依赖的快照不受影响', () => {
  const { versions } = setup()
  const categoriesPage = versions.snapshot(['categories', 'products'])
  const onlyCategories = versions.snapshot(['categories'])
  versions.bump('products')
  assert.equal(versions.isStale(categoriesPage, 120_000), true)
  assert.equal(versions.isStale(onlyCategories, 120_000), false)
})

test('超过 TTL 兜底刷新（覆盖其他用户/后台的修改）', () => {
  const { versions, advance } = setup()
  const snap = versions.snapshot(['products'])
  advance(120_001)
  assert.equal(versions.isStale(snap, 120_000), true)
})

test('尚未加载过（无快照）不触发激活刷新，交给 onMounted', () => {
  const { versions } = setup()
  assert.equal(versions.isStale(null, 120_000), false)
})
