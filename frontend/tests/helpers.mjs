// 测试辅助：用项目自带的 typescript 把 .ts 模块或 .vue 中截取的片段转成 JS 运行，无需额外测试框架。
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const require = createRequire(import.meta.url)
const ts = require(path.join(root, 'node_modules/typescript'))

const transpile = (code) =>
  ts.transpileModule(code, { compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS } }).outputText

/** 加载一个无外部依赖的 .ts 模块，返回其导出 */
export function loadTs (relPath) {
  const module = { exports: {} }
  vm.runInNewContext(transpile(fs.readFileSync(path.join(root, relPath), 'utf8')), { module, exports: module.exports })
  return module.exports
}

/** 在给定上下文中运行一段 TS 片段（上下文即被测代码可见的「组件作用域」变量） */
loadTs.inContext = (code, ctx) => {
  vm.createContext(ctx)
  vm.runInContext(transpile(code), ctx)
  return ctx
}

/** 截取文件中 [startMarker, endMarker) 之间的源码 */
export function extractBetween (relPath, startMarker, endMarker) {
  const src = fs.readFileSync(path.join(root, relPath), 'utf8')
  const start = src.indexOf(startMarker)
  const end = src.indexOf(endMarker, start)
  if (start < 0 || end < 0) throw new Error(`markers not found in ${relPath}: ${startMarker} … ${endMarker}`)
  return src.slice(start, end)
}
