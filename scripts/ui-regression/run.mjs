// 前台 UI 统一 · 浏览器回归（review R1/R2/R3）
//
// 自包含：在全新临时 SQLite 上启动后端（开发模式自动建表+默认数据）与 Vite，经真实登录表单登录后执行检查。
// 用法（仓库根目录）：
//   npm --prefix scripts/ui-regression install
//   npm --prefix scripts/ui-regression test
// 环境变量：CHROME_PATH（默认 macOS Chrome）、UI_REG_OUT（产物目录，默认 scripts/ui-regression/output）
// 产物：output/results.json（commit、数据集、每项结果）与各页截图。任一检查失败则退出码 1。
// 边界：数据为本地种子数据，不代表生产 Supabase；高德地图需联网，离线时地图相关检查记为 skipped。
import { spawn, execSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import puppeteer from 'puppeteer-core'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const OUT = process.env.UI_REG_OUT || path.join(ROOT, 'scripts/ui-regression/output')
const CHROME = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
const API_PORT = 8010
const WEB_PORT = 5180
const BASE = `http://localhost:${WEB_PORT}`
const ADMIN = { username: 'johnnychenjun', password: 'test123456' } // 后端开发模式默认账号（管理员）
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

fs.mkdirSync(OUT, { recursive: true })
const results = []
const record = (name, status, detail = {}) => {
  results.push({ name, status, ...detail })
  const mark = status === 'pass' ? '✓' : status === 'skipped' ? '-' : '✗'
  console.log(`${mark} ${name}${detail.note ? ` — ${detail.note}` : ''}`)
}
const check = async (name, fn) => {
  try {
    const detail = (await fn()) || {}
    record(name, detail.skipped ? 'skipped' : 'pass', detail)
  } catch (e) {
    record(name, 'fail', { error: String(e && e.message ? e.message : e) })
  }
}
const expect = (cond, msg) => { if (!cond) throw new Error(msg) }

// ---------- 启动服务 ----------
const children = []
const start = (cmd, args, opts) => {
  const p = spawn(cmd, args, { ...opts, stdio: ['ignore', 'pipe', 'pipe'] })
  const log = fs.createWriteStream(path.join(OUT, `${path.basename(cmd)}.log`))
  p.stdout.pipe(log); p.stderr.pipe(log)
  children.push(p)
  return p
}
const waitFor = async (url, ms = 60000) => {
  const t0 = Date.now()
  while (Date.now() - t0 < ms) {
    try { const r = await fetch(url); if (r.ok) return } catch { /* not up yet */ }
    await sleep(500)
  }
  throw new Error(`timeout waiting for ${url}`)
}
const cleanup = () => { for (const c of children) { try { c.kill('SIGTERM') } catch { /* gone */ } } }
process.on('exit', cleanup)
process.on('SIGINT', () => { cleanup(); process.exit(130) })

const dbDir = fs.mkdtempSync(path.join(os.tmpdir(), 'funeng-ui-reg-'))
start(path.join(ROOT, 'backend/.venv/bin/uvicorn'), ['main:app', '--port', String(API_PORT)], {
  cwd: path.join(ROOT, 'backend'),
  env: { ...process.env, DATABASE_URL: `sqlite:///${dbDir}/ui.db`, ENVIRONMENT: 'development' }
})
start(path.join(ROOT, 'frontend/node_modules/.bin/vite'), ['--port', String(WEB_PORT), '--strictPort'], {
  cwd: path.join(ROOT, 'frontend'),
  env: { ...process.env, API_TARGET: `http://localhost:${API_PORT}` }
})
await waitFor(`http://localhost:${API_PORT}/health`)
await waitFor(BASE)

const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new' })
const page = await browser.newPage()
const consoleErrors = []
page.on('pageerror', (e) => consoleErrors.push(`${page.url()} ${e.message}`))
page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(`${page.url()} ${m.text()}`) })
const apiCalls = []
const httpErrors = []
page.on('response', (r) => { if (r.status() >= 400 && r.url().includes('/api/')) httpErrors.push(`${r.status()} ${r.request().method()} ${new URL(r.url()).pathname} @${new URL(page.url()).pathname}`) })
page.on('request', (r) => { const u = r.url(); if (u.includes('/api/')) apiCalls.push(new URL(u).pathname) })

// Vite 首次按需预构建依赖会触发整页重载（frame detached），重试即可；与被测功能无关
const go = async (route, wait = 700) => {
  for (let attempt = 0; ; attempt++) {
    try {
      await page.goto(BASE + route, { waitUntil: 'networkidle0' })
      await sleep(wait)
      return
    } catch (e) {
      if (attempt >= 3 || !/detached|ERR_ABORTED|Execution context was destroyed/.test(String(e))) throw e
      await sleep(2000)
    }
  }
}
const clickText = (selector, text) => page.evaluate((s, t) => {
  const el = [...document.querySelectorAll(s)].find((e) => e.textContent.trim() === t)
  if (!el) throw new Error(`not found: ${s} "${t}"`)
  el.click()
}, selector, text)
const navTo = async (label) => { await clickText('.nav-menu .nav-item, .drawer-item', label); await sleep(1200) }
const visibleDialog = () => page.evaluate(() => {
  const d = [...document.querySelectorAll('.el-dialog')].find((e) => e.offsetParent)
  return d ? { width: Math.round(d.getBoundingClientRect().width), cls: d.className } : null
})
// 已在登录页（例如刚经由下拉退出）时不整页刷新——整页刷新会清空 keep-alive，测不到缓存隔离
const login = async ({ username, password }) => {
  if (new URL(page.url()).pathname !== '/login') await go('/login')
  await page.type('input[placeholder="请输入用户名"]', username)
  await page.type('input[placeholder="请输入密码"]', password)
  await clickText('button', '登录')
  await page.waitForFunction(() => location.pathname !== '/login', { timeout: 10000 })
  await sleep(800)
}
// 通过用户下拉「退出登录」触发 store.logout，与真实路径一致（需桌面宽度）
const logout = async () => {
  await page.evaluate(() => document.querySelector('.user-btn')?.click()); await sleep(400)
  await page.evaluate(() => [...document.querySelectorAll('.el-dropdown-menu__item')].find((e) => e.textContent.includes('退出登录'))?.click())
  await page.waitForFunction(() => location.pathname === '/login', { timeout: 5000 })
  await sleep(500)
}

const ROUTES = ['/', '/dashboard', '/products', '/categories', '/smart-agriculture', '/digital-marketing', '/cold-chain', '/supply-chain-finance', '/admin']
const stamp = Date.now().toString().slice(-6)

try {
  // 预热：Vite 首次按需预构建依赖会整页重载，先把各页走一遍
  await login(ADMIN)
  for (let pass = 0; pass < 2; pass++) {
    for (const r of ROUTES) await go(r, 400)
    await go('/cold-chain', 600)
    for (const t of ['入库管理', '作业管理', '运输追踪']) {
      await page.evaluate((l) => [...document.querySelectorAll('.ui-nav-card')].find((c) => c.textContent.trim() === l)?.click(), t).catch(() => {})
      await sleep(800)
    }
  }
  consoleErrors.length = 0
  httpErrors.length = 0

  // ---------- 1. 断点矩阵 × 角色（R3） ----------
  const BREAKPOINTS = [1440, 1200, 1199, 769, 768, 390]
  await check('断点矩阵（管理员）：9 路由 × 6 宽度无横向溢出、导航形态正确', async () => {
    const bad = []
    for (const w of BREAKPOINTS) {
      await page.setViewport({ width: w, height: 900 })
      for (const r of ROUTES) {
        await go(r, 500)
        const s = await page.evaluate(() => ({
          overflow: document.documentElement.scrollWidth - window.innerWidth,
          menu: getComputedStyle(document.querySelector('.nav-menu')).display,
          toggle: getComputedStyle(document.querySelector('.menu-toggle')).display
        }))
        const navOk = w >= 1200 ? s.menu !== 'none' && s.toggle === 'none' : s.menu === 'none' && s.toggle !== 'none'
        if (s.overflow > 0 || !navOk) bad.push({ w, r, ...s })
        if ([1440, 768, 390].includes(w)) await page.screenshot({ path: path.join(OUT, `w${w}${r === '/' ? '-home' : r.replace(/\//g, '-')}.png`), fullPage: w !== 390 })
      }
    }
    expect(bad.length === 0, JSON.stringify(bad))
    return { note: `${BREAKPOINTS.length * ROUTES.length} 组合` }
  })

  await page.setViewport({ width: 1440, height: 900 })
  const userB = { username: `uireg${stamp}`, password: 'uireg123456' }
  await check('普通用户：无「管理后台」入口、无产品/分类写操作按钮', async () => {
    const r = await fetch(`http://localhost:${API_PORT}/api/auth/register`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: userB.username, email: `${userB.username}@test.com`, password: userB.password })
    })
    expect(r.ok, `register ${r.status}`)
    await logout(); await login(userB)
    await go('/products')
    const s = await page.evaluate(() => ({
      adminNav: [...document.querySelectorAll('.nav-menu .nav-item')].some((e) => e.textContent.includes('管理后台')),
      addBtn: [...document.querySelectorAll('button')].some((e) => e.textContent.trim() === '添加产品')
    }))
    expect(!s.adminNav && !s.addBtn, JSON.stringify(s))
  })

  // ---------- 2. keep-alive 关联数据刷新与会话隔离（R1） ----------
  await check('缓存隔离：切换账号后不沿用上一会话的页面缓存', async () => {
    // 当前为普通用户，已缓存产品页；切到管理员后进入产品页必须重新请求
    await logout(); await login(ADMIN)
    apiCalls.length = 0
    await navTo('产品')
    expect(apiCalls.some((p) => p.startsWith('/api/products')), `no product request after account switch: ${apiCalls}`)
  })

  await check('无数据变化时命中缓存：产品→分类→产品 不重复请求产品', async () => {
    await navTo('产品'); await navTo('分类')
    apiCalls.length = 0
    await navTo('产品')
    expect(!apiCalls.some((p) => p.startsWith('/api/products')), `unexpected: ${apiCalls}`)
  })

  const catName = `回归分类${stamp}`
  await check('分类页新增分类 → 返回产品页，添加产品的分类下拉立即可选', async () => {
    await navTo('分类')
    await clickText('button', '添加分类'); await sleep(500)
    await page.type('.el-dialog input[placeholder="请输入分类名称"]', catName)
    await clickText('.el-dialog__footer button', '保存'); await sleep(1000)
    await navTo('产品')
    await clickText('button', '添加产品'); await sleep(500)
    await page.evaluate(() => [...document.querySelectorAll('.el-dialog .el-form-item')].find((e) => e.textContent.includes('产品分类'))?.querySelector('.el-select__wrapper')?.click())
    await sleep(500)
    const options = await page.evaluate(() => [...document.querySelectorAll('.el-select-dropdown__item')].filter((e) => e.offsetParent).map((e) => e.textContent.trim()))
    expect(options.includes(catName), `options: ${options.join(',')}`)
    await page.keyboard.press('Escape'); await sleep(200)
    await clickText('.el-dialog__footer button', '取消'); await sleep(400)
  })

  const productName = `回归产品${stamp}`
  await check('产品页新增产品 → 分类计数与看板总数同步更新', async () => {
    await go('/dashboard', 900)
    const before = await page.evaluate(() => Number(document.querySelector('.ui-stat-card .stat-value')?.textContent.replace(/[^\d]/g, '')))
    await navTo('产品')
    await clickText('button', '添加产品'); await sleep(500)
    await page.type('.el-dialog input[placeholder="请输入产品名称"]', productName)
    await page.evaluate(() => [...document.querySelectorAll('.el-dialog .el-form-item')].find((e) => e.textContent.includes('产品分类'))?.querySelector('.el-select__wrapper')?.click())
    await sleep(400)
    await page.evaluate((n) => [...document.querySelectorAll('.el-select-dropdown__item')].filter((e) => e.offsetParent).find((e) => e.textContent.trim() === n)?.click(), catName)
    await page.evaluate(() => {
      const input = [...document.querySelectorAll('.el-dialog .el-form-item')].find((e) => e.textContent.includes('价格'))?.querySelector('input')
      input.value = ''; input.dispatchEvent(new Event('input', { bubbles: true }))
    })
    const priceInput = await page.evaluateHandle(() => [...document.querySelectorAll('.el-dialog .el-form-item')].find((e) => e.textContent.includes('价格'))?.querySelector('input'))
    await priceInput.type('9.9'); await page.keyboard.press('Tab')
    await clickText('.el-dialog__footer button', '保存'); await sleep(1200)
    const saved = await page.evaluate(() => ({
      dialogOpen: !!document.querySelector('.el-dialog') && !!document.querySelector('.el-dialog').offsetParent,
      messages: [...document.querySelectorAll('.el-message')].map((m) => m.textContent.trim()),
      price: [...document.querySelectorAll('.el-dialog .el-form-item')].find((e) => e.textContent.includes('价格'))?.querySelector('input')?.value
    }))
    expect(!saved.dialogOpen, `product not saved: ${JSON.stringify(saved)}`)

    await navTo('分类')
    const count = await page.evaluate((n) => [...document.querySelectorAll('.category-card')].find((c) => c.textContent.includes(n))?.querySelector('.category-count')?.textContent, catName)
    expect(count && count.includes('1'), `category count: ${count}`)
    await navTo('看板')
    const after = await page.evaluate(() => Number(document.querySelector('.ui-stat-card .stat-value')?.textContent.replace(/[^\d]/g, '')))
    expect(after === before + 1, `dashboard total ${before} -> ${after}`)
  })

  // ---------- 3. 冷链运输地图快速切换（R2） ----------
  await check('冷链运输追踪：A 的地理编码迟到时切到 B，时间线与选择一致、地图单实例', async () => {
    await go('/cold-chain', 1000)
    const amap = await page.evaluate(() => typeof window.AMap)
    if (amap !== 'object') return { skipped: true, note: '高德地图未加载（离线），跳过' }
    await clickText('.ui-nav-card', '运输追踪'); await sleep(2500)
    const transports = await page.evaluate(async () => (await (await fetch('/api/cold-chain/transport', { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })).json()))
    if (transports.length < 2) return { skipped: true, note: '运输记录少于 2 条' }
    const firstWaypoint = (t) => { const w = typeof t.waypoints === 'string' ? JSON.parse(t.waypoints) : t.waypoints; return Array.isArray(w) && w.length ? w[0].name : null }
    // 选两条起点城市不同且有 waypoints 的路线
    const usable = transports.filter((t) => firstWaypoint(t) && t.route)
    const A = usable.find((t) => t.id !== transports[0].id) || usable[0]
    const B = usable.find((t) => t.id !== A.id && t.route.split('-')[0] !== A.route.split('-')[0])
    if (!A || !B) return { skipped: true, note: '缺少可区分的两条路线' }
    const aCities = A.route.split('-').slice(0, 2)

    // 让 A 的地理编码响应延迟 3s，制造「旧请求迟到」
    await page.setRequestInterception(true)
    const delay = (req) => {
      const u = req.url()
      if (/restapi\.amap\.com\/.*geocode/.test(u) && aCities.some((c) => decodeURIComponent(u).includes(c))) setTimeout(() => req.continue(), 3000)
      else req.continue()
    }
    page.on('request', delay)
    const pick = async (t) => {
      await page.evaluate(() => document.querySelector('.transport-select .el-select__wrapper')?.click()); await sleep(250)
      await page.evaluate((id) => {
        const item = [...document.querySelectorAll('.el-select-dropdown__item')].filter((e) => e.offsetParent).find((e) => e.textContent.includes(id))
        item?.click()
      }, t.vehicle_no)
      await sleep(100)
    }
    await pick(A); await pick(B)
    await sleep(6000) // A 的迟到响应在此期间返回
    page.off('request', delay)
    await page.setRequestInterception(false)

    const s = await page.evaluate(() => ({
      selected: document.querySelector('.transport-select .el-select__wrapper')?.innerText.trim(),
      maps: document.querySelectorAll('#transportMap .amap-maps').length,
      firstTimeline: document.querySelector('.transport-timeline .timeline-info')?.textContent.split(' · ')[0].trim() ?? null
    }))
    await page.screenshot({ path: path.join(OUT, 'coldchain-transport.png'), fullPage: true })
    expect(s.maps === 1, `map instances ${s.maps}`)
    expect(s.selected && s.selected.startsWith(B.vehicle_no), `selection ${s.selected} != ${B.vehicle_no}`)
    expect(s.firstTimeline === firstWaypoint(B), `timeline starts at ${s.firstTimeline}, selected B starts at ${firstWaypoint(B)} (A=${firstWaypoint(A)})`)
    return { note: `A=${A.route} 延迟 3s，B=${B.route}` }
  })

  // ---------- 4. 空态 / 错误态 ----------
  await check('错误态：分类接口失败显示 EmptyState + 重试，重试后恢复', async () => {
    const errorsBefore = consoleErrors.length
    await page.setRequestInterception(true)
    let fail = true
    const handler = (req) => {
      if (fail && req.url().includes('/api/categories/with-count')) req.respond({ status: 500, contentType: 'application/json', body: '{"detail":"injected"}' })
      else req.continue()
    }
    page.on('request', handler)
    await go('/categories', 900)
    const shown = await page.evaluate(() => !!document.querySelector('.ui-empty-state') && document.body.innerText.includes('分类加载失败'))
    fail = false
    await clickText('button', '重试'); await sleep(900)
    const recovered = await page.evaluate(() => document.querySelectorAll('.category-card').length)
    page.off('request', handler)
    await page.setRequestInterception(false)
    consoleErrors.splice(errorsBefore) // 本用例注入的 500 属预期，不计入「无控制台错误」
    expect(shown && recovered > 0, JSON.stringify({ shown, recovered }))
  })

  await check('空态：产品搜索无结果显示「暂无产品」', async () => {
    await go('/products', 800)
    await page.type('.search-input input', `不存在的产品${stamp}`); await sleep(1200)
    const txt = await page.evaluate(() => document.querySelector('.el-table__empty-text')?.textContent.trim())
    expect(txt === '暂无产品', `empty text: ${txt}`)
  })

  // ---------- 5. 弹窗宽度档 ----------
  await check('弹窗宽度档：桌面 480/640，手机满宽减 32px', async () => {
    await page.setViewport({ width: 1440, height: 900 })
    await go('/categories'); await clickText('button', '添加分类'); await sleep(500)
    const sm = await visibleDialog(); await page.keyboard.press('Escape'); await sleep(300)
    await go('/products'); await clickText('button', '添加产品'); await sleep(500)
    const md = await visibleDialog(); await page.keyboard.press('Escape'); await sleep(300)
    await page.setViewport({ width: 390, height: 844 })
    await go('/categories'); await clickText('button', '添加分类'); await sleep(500)
    const mobile = await visibleDialog()
    await page.screenshot({ path: path.join(OUT, 'dialog-mobile.png') })
    await page.setViewport({ width: 1440, height: 900 })
    expect(sm?.width === 480 && md?.width === 640 && mobile?.width === 358, JSON.stringify({ sm, md, mobile }))
  })

  await check('全程无控制台错误', async () => {
    if (consoleErrors.length) console.log('    http errors:', httpErrors.join(' | '))
    expect(consoleErrors.length === 0, consoleErrors.slice(0, 5).join(' | '))
  })
} finally {
  await browser.close()
  const commit = execSync('git rev-parse --short HEAD', { cwd: ROOT }).toString().trim()
  const dirty = execSync('git status --porcelain -- frontend', { cwd: ROOT }).toString().trim() !== ''
  const summary = {
    commit, frontendDirty: dirty, date: new Date().toISOString(),
    dataset: '临时 SQLite，后端开发模式默认种子数据（非生产 Supabase）',
    passed: results.filter((r) => r.status === 'pass').length,
    failed: results.filter((r) => r.status === 'fail').length,
    skipped: results.filter((r) => r.status === 'skipped').length,
    results
  }
  fs.writeFileSync(path.join(OUT, 'results.json'), JSON.stringify(summary, null, 2))
  console.log(`\n${summary.passed} passed, ${summary.failed} failed, ${summary.skipped} skipped · commit ${commit}${dirty ? ' (+未提交改动)' : ''} · ${OUT}`)
  cleanup()
  fs.rmSync(dbDir, { recursive: true, force: true })
  process.exitCode = summary.failed ? 1 : 0
}
