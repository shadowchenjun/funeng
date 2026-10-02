<template>
  <section ref="screen" class="industry-screen" aria-label="农业产业大数据大屏">
    <div class="screen-toolbar">
      <div class="screen-status" role="status">
        <strong>产业大数据</strong>
        <span v-if="snapshot">最近入库 {{ importTime }} · {{ snapshot.meta.automatic_collection ? '行情每日定时采集' : '定时采集未启用' }} · 行情 {{ snapshot.meta.price_to || '暂无数据' }}</span>
        <span v-else>正在读取已入库的产业资料</span>
      </div>
      <div class="screen-actions">
        <el-button :loading="loading" @click="load">刷新数据</el-button>
        <el-button :icon="FullScreen" @click="fullscreen">全屏展示</el-button>
      </div>
    </div>
    <div v-if="loading" class="screen-empty" role="status">正在加载产业统计、市场行情和数据来源…</div>
    <div v-else-if="error" class="screen-empty" role="alert">
      <p>{{ error }}</p>
      <el-button type="primary" @click="load">重新加载</el-button>
    </div>
    <template v-else-if="snapshot">
      <p v-if="snapshot.meta.automatic_collection" class="coverage-note" role="status">
        行情每日北京时间 20 点检查更新，补查最近三天；周报按实际发布期入库。年报、季度统计仍按报告更新。
        <span v-if="failedSources">最近采集异常：{{ failedSources }}；已保留历史数据。</span>
      </p>
      <p v-if="snapshot.meta.market_truncated" class="coverage-note">
        当前展示最新 {{ snapshot.meta.market_returned }} 条行情，数据库共 {{ snapshot.meta.market_total }} 条。
      </p>
      <iframe :srcdoc="frameHtml" title="农业产业驾驶舱：总览、种植养殖、行情、冷链、风险、金融" allow="fullscreen" sandbox="allow-scripts allow-downloads allow-modals allow-popups allow-popups-to-escape-sandbox" class="industry-frame" />
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { FullScreen } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from '../utils/error'
import { buildIndustryFrame, type DashboardSnapshot } from '../utils/industryFrame'
import industryTemplate from '../dashboard/industry.html?raw'
import marketTemplate from '../dashboard/market.html?raw'
import centers from '../dashboard/mapCenters.json'

const auth = useAuthStore()
const router = useRouter()
const screen = ref<HTMLElement | null>(null)
const snapshot = ref<DashboardSnapshot | null>(null)
const loading = ref(false)
const error = ref('')
let controller: AbortController | null = null
const frameHtml = computed(() => snapshot.value ? buildIndustryFrame(snapshot.value, industryTemplate, marketTemplate, centers) : '')
const importTime = computed(() => snapshot.value?.meta.last_import_at
  ? new Date(snapshot.value.meta.last_import_at).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false })
  : '暂无导入记录')
const failedSources = computed(() => snapshot.value?.meta.collection_runs
  ?.filter(run => ['failed', 'partial'].includes(run.status)).map(run => run.source_id).join('、') || '')

async function load(): Promise<void> {
  controller?.abort()
  const active = new AbortController()
  controller = active
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get<DashboardSnapshot>('/api/industry-dashboard/snapshot', {
      headers: { Authorization: `Bearer ${auth.token}` }, timeout: 25000, signal: active.signal
    })
    if (controller === active) snapshot.value = response.data
  } catch (cause) {
    if (active.signal.aborted || controller !== active) return
    if (axios.isAxiosError(cause) && cause.response?.status === 401) {
      auth.logout()
      await router.replace('/login')
      return
    }
    error.value = getErrorMessage(cause, '产业数据加载失败，请重试')
  } finally {
    if (controller === active) loading.value = false
  }
}

async function fullscreen(): Promise<void> {
  try {
    if (document.fullscreenElement) await document.exitFullscreen()
    else if (screen.value?.requestFullscreen) await screen.value.requestFullscreen()
    else ElMessage.info('当前浏览器不支持全屏，请使用窗口最大化')
  } catch {
    ElMessage.info('请使用浏览器窗口最大化查看大屏')
  }
}
onMounted(load)
onBeforeUnmount(() => controller?.abort())
</script>

<style scoped>
.industry-screen { background: #081411; color: #edf4e8; min-height: calc(100vh - 96px); }
.screen-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 28px; border-bottom: 1px solid #284038; }
.screen-status { display: flex; gap: 16px; flex-wrap: wrap; font-size: 12px; color: #9aafa5; }
.screen-status strong { color: #d4ed98; font-size: 14px; }
.screen-actions { display: flex; gap: 8px; flex-shrink: 0; }
.industry-frame { display: block; border: 0; width: 100%; height: calc(100vh - 160px); min-height: 640px; background: #081411; }
.screen-empty { display: grid; place-content: center; gap: 16px; min-height: 65vh; text-align: center; color: #9aafa5; }
.coverage-note { padding: 8px 28px; margin: 0; color: #edb874; font-size: 12px; }
.industry-screen:fullscreen { overflow: auto; }
.industry-screen:fullscreen .industry-frame { height: calc(100vh - 65px); }
@media (max-width: 760px) { .screen-toolbar { padding: 14px; align-items: flex-start; flex-direction: column; } .industry-frame { height: calc(100vh - 190px); min-height: 680px; } }
</style>
