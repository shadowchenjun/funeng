<template>
  <div class="claude-code-container">
    <!-- 顶部导航栏 -->
    <header class="navbar">
      <div class="navbar-left">
        <div class="logo">
          <span class="logo-icon">🤖</span>
          <span class="logo-text">Claude Code</span>
        </div>
      </div>

      <div class="navbar-center">
        <button
          v-for="item in navItems"
          :key="item.id"
          :class="['nav-item', { active: activeNav === item.id }]"
          @click="activeNav = item.id"
        >
          {{ item.label }}
        </button>
      </div>

      <div class="navbar-right">
        <button v-if="!isLoggedIn" class="btn-login" @click="goToLogin">登录</button>
        <div v-else class="user-avatar">
          <span>👤</span>
        </div>
        <button class="hamburger" @click="showMobileMenu = !showMobileMenu">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>

      <!-- 移动端菜单 -->
      <div v-if="showMobileMenu" class="mobile-menu">
        <button
          v-for="item in navItems"
          :key="item.id"
          :class="['mobile-nav-item', { active: activeNav === item.id }]"
          @click="activeNav = item.id; showMobileMenu = false"
        >
          {{ item.label }}
        </button>
        <button v-if="!isLoggedIn" class="mobile-nav-item" @click="goToLogin">登录</button>
      </div>
    </header>

    <!-- 核心交互区 -->
    <main class="main-content">
      <div class="split-view">
        <!-- 左侧：代码输入区 -->
        <div class="code-input-panel" :style="{ width: isWeb ? '45%' : '100%' }">
          <div class="panel-header">
            <span class="panel-title">代码输入</span>
            <div class="panel-actions">
              <button class="action-btn" @click="clearCode" title="清空">清空</button>
              <button class="action-btn" @click="copyCode" title="复制">复制</button>
            </div>
          </div>
          <div class="code-editor">
            <div class="line-numbers">
              <span v-for="n in codeLineCount" :key="n">{{ n }}</span>
            </div>
            <textarea
              v-model="codeInput"
              class="code-textarea"
              placeholder="// 在此输入代码..."
              spellcheck="false"
              @input="updateLineNumbers"
            ></textarea>
          </div>
        </div>

        <!-- 分隔线 (仅 Web 端) -->
        <div v-if="isWeb" class="split-handle" @mousedown="startResize"></div>

        <!-- 右侧：AI 响应区 -->
        <div class="ai-response-panel" :style="{ width: isWeb ? '45%' : '100%' }">
          <div class="panel-header">
            <span class="panel-title">AI 响应</span>
            <div class="panel-actions">
              <button class="action-btn" @click="copyResponse" title="复制">复制</button>
            </div>
          </div>
          <div class="response-content">
            <!-- 加载状态 -->
            <div v-if="isLoading" class="skeleton-loader">
              <div class="skeleton-line" style="width: 60%"></div>
              <div class="skeleton-line" style="width: 80%"></div>
              <div class="skeleton-line" style="width: 45%"></div>
              <div class="skeleton-line" style="width: 70%"></div>
              <div class="skeleton-line" style="width: 55%"></div>
            </div>
            <!-- 错误状态 -->
            <div v-else-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>
            <!-- 响应内容 -->
            <div v-else-if="aiResponse" class="response-text">
              <pre class="code-output">{{ aiResponse.code }}</pre>
              <div class="response-explanation">{{ aiResponse.explanation }}</div>
            </div>
            <!-- 空状态 -->
            <div v-else class="empty-state">
              <span class="empty-icon">💡</span>
              <p>输入代码后点击「发送请求」按钮<br>AI 将为您提供智能分析</p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部操作栏 -->
    <footer class="action-bar">
      <div class="action-bar-main">
        <button
          class="btn-send"
          @click="sendRequest"
          :disabled="isLoading || !codeInput.trim()"
        >
          {{ isLoading ? '处理中...' : '发送请求' }}
        </button>
      </div>
      <div class="action-bar-options">
        <div class="option-group">
          <label>代码语言</label>
          <select v-model="settings.language">
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="java">Java</option>
            <option value="go">Go</option>
            <option value="rust">Rust</option>
          </select>
        </div>
        <div class="option-group">
          <label>输出风格</label>
          <select v-model="settings.style">
            <option value="concise">简洁</option>
            <option value="detailed">详细</option>
            <option value="tutorial">教程式</option>
          </select>
        </div>
        <div class="option-group">
          <label>
            <input type="checkbox" v-model="settings.addComments" />
            添加注释
          </label>
        </div>
        <button class="btn-history" @click="showHistory = !showHistory">
          历史记录
        </button>
      </div>

      <!-- 历史记录面板 -->
      <div v-if="showHistory" class="history-panel">
        <div class="history-header">
          <span>历史记录</span>
          <button @click="showHistory = false">×</button>
        </div>
        <div class="history-list">
          <div
            v-for="(item, index) in history"
            :key="index"
            class="history-item"
            @click="loadFromHistory(item)"
          >
            <div class="history-code">{{ item.code.slice(0, 50) }}...</div>
            <div class="history-time">{{ item.time }}</div>
          </div>
          <div v-if="history.length === 0" class="history-empty">
            暂无历史记录
          </div>
        </div>
      </div>
    </footer>

    <!-- 页面底部 Footer -->
    <div class="page-footer">
      <a href="#">隐私政策</a>
      <span class="divider">|</span>
      <a href="#">关于我们</a>
      <span class="divider">|</span>
      <a href="#">联系方式</a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 响应式检测
const isWeb = ref(window.innerWidth >= 768)

// 导航
const activeNav = ref('generate')
const showMobileMenu = ref(false)
const navItems = [
  { id: 'generate', label: '代码生成' },
  { id: 'debug', label: '调试' },
  { id: 'explain', label: '解释' },
  { id: 'knowledge', label: '知识库' }
]

// 登录状态
const isLoggedIn = ref(!!localStorage.getItem('token'))

const goToLogin = () => {
  window.location.href = '/login'
}

// 代码输入
const codeInput = ref('')
const codeLineCount = computed(() => {
  return codeInput.value.split('\n').length || 1
})

const updateLineNumbers = () => {
  // 触发响应式更新
}

// 面板宽度调整
const startResize = (e: MouseEvent) => {
  e.preventDefault()

  const onMouseMove = (_e: MouseEvent) => {
    // 简化处理，实际项目中可实现拖拽调整
  }

  const onMouseUp = () => {
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

// AI 响应
const aiResponse = ref<{ code: string; explanation: string } | null>(null)
const isLoading = ref(false)
const errorMessage = ref('')

// 设置
const settings = ref({
  language: 'python',
  style: 'concise',
  addComments: true
})

// 历史记录
const showHistory = ref(false)
const history = ref<Array<{ code: string; time: string }>>([])

// 操作方法
const clearCode = () => {
  codeInput.value = ''
}

const copyCode = async () => {
  if (codeInput.value) {
    await navigator.clipboard.writeText(codeInput.value)
  }
}

const copyResponse = async () => {
  if (aiResponse.value?.code) {
    await navigator.clipboard.writeText(aiResponse.value.code)
  }
}

const sendRequest = async () => {
  if (!codeInput.value.trim()) return

  isLoading.value = true
  errorMessage.value = ''
  aiResponse.value = null

  // 模拟 API 请求
  setTimeout(() => {
    // 模拟响应
    aiResponse.value = {
      code: `def optimized_function(input_data):
    # Claude Code 优化后的代码
    result = [item for item in input_data if item > 0]
    return result`,
      explanation: '已为您优化代码逻辑，使用列表推导式提升性能，并添加了必要的注释说明。'
    }

    // 保存到历史
    history.value.unshift({
      code: codeInput.value,
      time: new Date().toLocaleString()
    })

    isLoading.value = false
  }, 1500)
}

const loadFromHistory = (item: { code: string; time: string }) => {
  codeInput.value = item.code
  showHistory.value = false
}

// 响应式监听
const handleResize = () => {
  isWeb.value = window.innerWidth >= 768
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* 基础变量 */
:root {
  --primary-blue: #165DFF;
  --bg-light: #F5F7FA;
  --bg-gray: #E5E6EB;
  --white: #FFFFFF;
  --dark-text: #1D2129;
  --error-bg: #FEE2E2;
  --error-text: #991B1B;
}

.claude-code-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg-light);
  font-family: 'Inter', '思源黑体', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 14px;
  color: var(--dark-text);
}

/* ========== 顶部导航栏 ========== */
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 24px;
  background: var(--white);
  border-bottom: 1px solid var(--bg-gray);
}

.navbar-left .logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--dark-text);
}

.navbar-center {
  display: flex;
  gap: 8px;
}

.nav-item {
  padding: 8px 16px;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--bg-light);
}

.nav-item.active {
  color: var(--primary-blue);
  background: rgba(22, 93, 255, 0.08);
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-login {
  padding: 8px 20px;
  border: none;
  background: var(--primary-blue);
  color: var(--white);
  font-size: 14px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-login:hover {
  opacity: 0.9;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-gray);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.hamburger {
  display: none;
  flex-direction: column;
  gap: 5px;
  padding: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
}

.hamburger span {
  display: block;
  width: 20px;
  height: 2px;
  background: var(--dark-text);
  border-radius: 1px;
}

.mobile-menu {
  display: none;
  position: absolute;
  top: 56px;
  left: 0;
  right: 0;
  background: var(--white);
  border-bottom: 1px solid var(--bg-gray);
  padding: 12px;
}

.mobile-nav-item {
  display: block;
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: transparent;
  text-align: left;
  font-size: 15px;
  cursor: pointer;
  border-radius: 6px;
}

.mobile-nav-item:hover,
.mobile-nav-item.active {
  background: var(--bg-light);
}

/* ========== 核心交互区 ========== */
.main-content {
  flex: 1;
  padding: 16px;
  overflow: hidden;
}

.split-view {
  display: flex;
  gap: 12px;
  height: calc(100vh - 56px - 140px - 60px);
  min-height: 400px;
}

.split-handle {
  width: 4px;
  background: var(--bg-gray);
  cursor: col-resize;
  border-radius: 2px;
}

/* 面板通用样式 */
.code-input-panel,
.ai-response-panel {
  display: flex;
  flex-direction: column;
  background: var(--white);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-light);
  border-bottom: 1px solid var(--bg-gray);
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--dark-text);
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 4px 12px;
  border: 1px solid var(--bg-gray);
  background: var(--white);
  font-size: 12px;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: var(--primary-blue);
  color: var(--primary-blue);
}

/* 代码输入区 */
.code-editor {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.line-numbers {
  display: flex;
  flex-direction: column;
  padding: 16px 8px;
  background: var(--bg-light);
  color: #999;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  text-align: right;
  user-select: none;
  min-width: 40px;
}

.code-textarea {
  flex: 1;
  padding: 16px;
  border: none;
  outline: none;
  resize: none;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  background: var(--white);
  color: var(--dark-text);
}

/* AI 响应区 */
.response-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.code-output {
  padding: 16px;
  background: #1E1E1E;
  border-radius: 8px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #D4D4D4;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.response-explanation {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-light);
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.8;
  color: #444;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 14px;
  line-height: 1.6;
}

/* 加载骨架屏 */
.skeleton-loader {
  padding: 16px 0;
}

.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, var(--bg-gray) 25%, var(--bg-light) 50%, var(--bg-gray) 75%);
  background-size: 200% 100%;
  border-radius: 4px;
  margin-bottom: 12px;
}

/* 错误状态 */
.error-message {
  padding: 16px;
  background: var(--error-bg);
  color: var(--error-text);
  border-radius: 8px;
  font-size: 14px;
}

/* ========== 底部操作栏 ========== */
.action-bar {
  position: relative;
  padding: 12px 16px;
  background: var(--white);
  border-top: 1px solid var(--bg-gray);
}

.action-bar-main {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.btn-send {
  width: 100%;
  max-width: 400px;
  height: 48px;
  border: none;
  background: var(--primary-blue);
  color: var(--white);
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.3);
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.4);
}

.btn-send:active:not(:disabled) {
  transform: translateY(0);
}

.btn-send:disabled {
  background: #ccc;
  box-shadow: none;
  cursor: not-allowed;
}

.action-bar-options {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.option-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.option-group label {
  font-size: 13px;
  color: #666;
}

.option-group select {
  padding: 6px 10px;
  border: 1px solid var(--bg-gray);
  border-radius: 4px;
  font-size: 13px;
  background: var(--white);
  cursor: pointer;
}

.option-group input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.btn-history {
  padding: 6px 14px;
  border: 1px solid var(--bg-gray);
  background: var(--white);
  font-size: 13px;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-history:hover {
  border-color: var(--primary-blue);
  color: var(--primary-blue);
}

/* 历史记录面板 */
.history-panel {
  position: absolute;
  bottom: 70px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 500px;
  max-height: 300px;
  background: var(--white);
  border: 1px solid var(--bg-gray);
  border-radius: 12px;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-light);
  border-bottom: 1px solid var(--bg-gray);
  font-weight: 600;
}

.history-header button {
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
  color: #999;
}

.history-list {
  max-height: 240px;
  overflow-y: auto;
}

.history-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--bg-light);
  cursor: pointer;
  transition: background 0.2s;
}

.history-item:hover {
  background: var(--bg-light);
}

.history-code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--dark-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.history-empty {
  padding: 32px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

/* ========== 页面底部 Footer ========== */
.page-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 16px;
  font-size: 12px;
  color: #999;
  background: var(--white);
  border-top: 1px solid var(--bg-gray);
}

.page-footer a {
  color: #999;
  text-decoration: none;
  transition: color 0.2s;
}

.page-footer a:hover {
  color: var(--primary-blue);
}

.page-footer .divider {
  color: #ddd;
}

/* ========== 响应式设计 ========== */

/* H5 端 (手机端) */
@media (max-width: 767px) {
  .navbar {
    padding: 0 16px;
  }

  .navbar-center {
    display: none;
  }

  .hamburger {
    display: flex;
  }

  .mobile-menu {
    display: block;
  }

  .btn-login {
    padding: 6px 14px;
    font-size: 13px;
  }

  .user-avatar {
    width: 32px;
    height: 32px;
  }

  .main-content {
    padding: 12px;
  }

  .split-view {
    flex-direction: column;
    height: auto;
    min-height: auto;
  }

  .code-input-panel,
  .ai-response-panel {
    width: 100% !important;
    min-height: 200px;
  }

  .code-input-panel {
    min-height: 250px;
  }

  .ai-response-panel {
    min-height: 200px;
  }

  .split-handle {
    display: none;
  }

  .btn-send {
    height: 52px;
    font-size: 16px;
  }

  .action-bar-options {
    gap: 10px;
  }

  .option-group label {
    font-size: 12px;
  }

  .option-group select {
    padding: 5px 8px;
    font-size: 12px;
  }

  .history-panel {
    width: 95%;
    left: 2.5%;
    transform: none;
  }

  .page-footer {
    padding: 12px;
    font-size: 11px;
  }
}

/* Web 端 (桌面端) */
@media (min-width: 768px) {
  .split-view {
    display: flex;
  }

  .hamburger {
    display: none;
  }

  .mobile-menu {
    display: none !important;
  }
}
</style>
