<template>
  <div class="page-container">
    <PageHeader title="供应链金融" subtitle="订单融资 · 应收账款 · 农业保险 · 信用评估">
      <template #actions>
        <el-button :icon="Refresh" :loading="loading" @click="refreshData">刷新数据</el-button>
      </template>
    </PageHeader>

    <!-- 金融数据概览 -->
    <div class="stat-grid" v-loading="loading">
      <StatCard
        v-for="stat in financeStats"
        :key="stat.title"
        :value="stat.value"
        :title="stat.title"
        :type="stat.type"
        :icon="stat.icon"
      />
    </div>

    <div class="section-stack">
      <!-- 融资申请 -->
      <SectionCard title="订单融资" :icon="CreditCard">
        <template #extra>
          <el-button type="primary" @click="showFinanceDialog('order')">申请融资</el-button>
        </template>
        <el-table :data="orderFinance" v-loading="loading" empty-text="暂无融资数据">
          <el-table-column prop="order_no" label="订单号" width="160" />
          <el-table-column label="订单金额">
            <template #default="{ row }">{{ formatMoney(row.amount) }}</template>
          </el-table-column>
          <el-table-column label="融资金额">
            <template #default="{ row }">{{ formatMoney(row.financed_amount) }}</template>
          </el-table-column>
          <el-table-column label="利率">
            <template #default="{ row }">{{ row.rate }}%</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="apply_date" label="申请日期" />
        </el-table>
      </SectionCard>

      <!-- 应收账款 -->
      <SectionCard title="应收账款" :icon="Tickets">
        <template #extra>
          <el-button type="primary" @click="showFinanceDialog('receivable')">转让应收款</el-button>
        </template>
        <el-table :data="receivables" v-loading="loading" empty-text="暂无应收账款">
          <el-table-column prop="invoice_no" label="发票号" width="160" />
          <el-table-column prop="debtor" label="买方" min-width="140" />
          <el-table-column label="金额">
            <template #default="{ row }">{{ formatMoney(row.amount) }}</template>
          </el-table-column>
          <el-table-column prop="due_date" label="到期日" />
          <el-table-column prop="status" label="状态" width="160">
            <template #default="{ row }">
              <el-tag :type="getReceivableStatusType(row.status)">{{ row.status }}</el-tag>
              <el-tag v-if="row.financing_order_id" type="info" class="transferred-tag">已转让</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button
                v-if="['未到期', '即将到期'].includes(row.status) && !row.financing_order_id"
                type="primary"
                link
                @click="showTransferDialog(row)"
              >转让</el-button>
              <el-button type="primary" link>详情</el-button>
              <el-button type="primary" link>催收</el-button>
            </template>
          </el-table-column>
        </el-table>
      </SectionCard>

      <div class="section-split">
        <!-- 农业保险 -->
        <SectionCard title="农业保险" :icon="Umbrella">
          <template #extra>
            <el-button type="primary" @click="showInsuranceDialog">购买保险</el-button>
          </template>
          <el-table :data="insurances" v-loading="loading" empty-text="暂无保单">
            <el-table-column label="险种">
              <template #default="{ row }">{{ row.type }} - {{ row.crop }}</template>
            </el-table-column>
            <el-table-column label="保额">
              <template #default="{ row }">{{ formatMoney(row.coverage) }}</template>
            </el-table-column>
            <el-table-column label="保费">
              <template #default="{ row }">{{ formatMoney(row.premium) }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '生效中' ? 'success' : 'info'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </SectionCard>

        <!-- 信用评估 -->
        <SectionCard title="信用评估" :icon="Medal">
          <EmptyState
            v-if="!creditScore && !loading"
            :icon="Medal"
            title="暂无信用评估数据"
            description="完成首次评估后将在此展示信用分与各维度得分"
          />
          <div v-else-if="creditScore" class="credit-score">
            <el-progress
              type="circle"
              :percentage="scorePercentage(creditScore.credit_score)"
              :color="getScoreColor(creditScore.credit_score)"
              :width="150"
              :stroke-width="10"
            >
              <template #default>
                <div class="score-content">
                  <span class="score">{{ creditScore.credit_score }}</span>
                  <span class="label">信用分</span>
                </div>
              </template>
            </el-progress>
            <dl class="credit-info">
              <div class="credit-row">
                <dt>信用等级</dt>
                <dd><el-tag :type="getLevelType(creditScore.level)">{{ creditScore.level }}</el-tag></dd>
              </div>
              <div class="credit-row">
                <dt>评估主体</dt>
                <dd>{{ creditScore.entity_name }}（{{ creditScore.entity_type }}）</dd>
              </div>
              <div class="credit-row">
                <dt>财务 / 经营</dt>
                <dd>{{ creditScore.factors.financial }} / {{ creditScore.factors.operation }}</dd>
              </div>
              <div class="credit-row">
                <dt>管理 / 行业</dt>
                <dd>{{ creditScore.factors.management }} / {{ creditScore.factors.industry }}</dd>
              </div>
              <div class="credit-row">
                <dt>下次复评</dt>
                <dd>{{ creditScore.next_review }}</dd>
              </div>
            </dl>
          </div>
        </SectionCard>
      </div>
    </div>

    <!-- 融资申请对话框 -->
    <el-dialog v-model="financeDialogVisible" :title="financeType === 'order' ? '订单融资申请' : '应收账款转让'" class="dialog-sm">
      <el-form ref="financeFormRef" :model="financeForm" :rules="financeRules" label-width="100px">
        <el-form-item label="融资类型">
          <el-select v-model="financeType" disabled>
            <el-option label="订单融资" value="order" />
            <el-option label="应收账款转让" value="receivable" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="financeType === 'order'" label="订单标的" prop="product">
          <el-input v-model="financeForm.product" maxlength="100" placeholder="如：有机大米订单" />
        </el-form-item>
        <el-form-item v-else label="应收账款" prop="receivableId">
          <el-select v-model="financeForm.receivableId" placeholder="选择未到期的应收账款" class="full-width" @change="onReceivableChange">
            <el-option
              v-for="r in transferableReceivables"
              :key="r.id"
              :label="`${r.invoice_no} · ${r.debtor} · ${formatMoney(r.amount - r.paid_amount)}`"
              :value="r.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="融资金额" prop="amount">
          <el-input-number v-model="financeForm.amount" :min="1000" :max="maxFinanceAmount" :step="1000" />
          <div v-if="financeType === 'receivable' && selectedReceivable" class="form-tip">
            最高可融资未回款金额的 90%：{{ formatMoney(maxFinanceAmount) }}
          </div>
        </el-form-item>
        <el-form-item label="融资期限" prop="term">
          <el-select v-model="financeForm.term">
            <el-option label="30天" :value="30" />
            <el-option label="60天" :value="60" />
            <el-option label="90天" :value="90" />
            <el-option label="120天" :value="120" />
            <el-option label="180天" :value="180" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="financeType === 'order'" label="担保方式">
          <el-radio-group v-model="financeForm.guarantee">
            <el-radio label="信用">信用</el-radio>
            <el-radio label="质押">质押</el-radio>
            <el-radio label="抵押">抵押</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="financeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitFinance">提交申请</el-button>
      </template>
    </el-dialog>
    
    <!-- 保险购买对话框 -->
    <el-dialog v-model="insuranceDialogVisible" title="购买农业保险" class="dialog-sm">
      <el-form ref="insuranceFormRef" :model="insuranceForm" :rules="insuranceRules" label-width="100px">
        <el-form-item label="险种类型" prop="type">
          <el-select v-model="insuranceForm.type">
            <el-option v-for="t in insuranceTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="保险标的" prop="crop">
          <el-input v-model="insuranceForm.crop" maxlength="50" placeholder="如：水稻、生猪" />
        </el-form-item>
        <el-form-item label="投保面积(亩)" prop="area">
          <el-input-number v-model="insuranceForm.area" :min="0" :max="100000" :precision="1" />
        </el-form-item>
        <el-form-item label="保额" prop="coverage">
          <el-input-number v-model="insuranceForm.coverage" :min="10000" :max="1000000" :step="10000" />
        </el-form-item>
        <el-form-item label="保险期限" prop="term_months">
          <el-select v-model="insuranceForm.term_months">
            <el-option label="3个月" :value="3" />
            <el-option label="6个月" :value="6" />
            <el-option label="12个月" :value="12" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="insuranceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitInsurance">立即投保</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'
import type { Component } from 'vue'
import { CreditCard, Medal, Money, Refresh, Tickets, TrendCharts, Umbrella, Wallet } from '@element-plus/icons-vue'
import { formatMoneyCompact as formatMoney } from '../utils/format'

const API = '/api/supply-chain-finance'

interface FinancingOrder {
  id: string
  order_no: string
  applicant: string
  product: string
  amount: number
  financed_amount: number
  rate: number
  term: number
  status: string
  apply_date: string
}

interface FinancingStats {
  total_financed: number
  active_orders: number
  total_amount: number
  avg_rate: number
}

interface Receivable {
  id: string
  invoice_no: string
  creditor: string
  debtor: string
  amount: number
  paid_amount: number
  due_date: string
  status: string
  financing_order_id: string | null
}

interface ReceivablesStats {
  total_amount: number
  outstanding: number
  overdue: number
  collection_rate: number
}

interface Insurance {
  id: string
  policy_no: string
  type: string
  crop: string
  coverage: number
  premium: number
  status: string
}

interface InsuranceStats {
  total_coverage: number
  active_policies: number
}

interface CreditAssessment {
  id: string
  entity_name: string
  entity_type: string
  credit_score: number
  level: string
  next_review: string
  factors: {
    financial: number
    operation: number
    management: number
    industry: number
  }
}

interface FinanceStat {
  title: string
  value: string
  type: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  icon: Component
}

const loading = ref(false)
const financeStats = ref<FinanceStat[]>([])
const orderFinance = ref<FinancingOrder[]>([])
const receivables = ref<Receivable[]>([])
const insurances = ref<Insurance[]>([])
const creditScore = ref<CreditAssessment | null>(null)


const fetchData = async () => {
  loading.value = true
  try {
    const [ordersRes, finStatsRes, recRes, recStatsRes, insRes, insStatsRes, creditRes] = await Promise.all([
      axios.get<FinancingOrder[]>(`${API}/financing/orders`),
      axios.get<FinancingStats>(`${API}/financing/stats`),
      axios.get<Receivable[]>(`${API}/receivables`),
      axios.get<ReceivablesStats>(`${API}/receivables/stats`),
      axios.get<Insurance[]>(`${API}/insurance`),
      axios.get<InsuranceStats>(`${API}/insurance/stats`),
      axios.get<CreditAssessment[]>(`${API}/credit/assessment`)
    ])
    orderFinance.value = ordersRes.data
    receivables.value = recRes.data
    insurances.value = insRes.data
    creditScore.value = creditRes.data[0] ?? null
    financeStats.value = [
      { title: '总融资额', value: formatMoney(finStatsRes.data.total_financed), type: 'primary', icon: Money },
      { title: '应收未收', value: formatMoney(recStatsRes.data.outstanding), type: 'warning', icon: Wallet },
      { title: '平均融资利率', value: `${finStatsRes.data.avg_rate}%`, type: 'success', icon: TrendCharts },
      { title: '保险保障', value: formatMoney(insStatsRes.data.total_coverage), type: 'primary', icon: Umbrella }
    ]
  } catch (e) {
    const detail = axios.isAxiosError(e) ? e.response?.data?.detail : undefined
    ElMessage.error(detail || '加载供应链金融数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  window.scrollTo(0, 0)
  fetchData()
})

const financeDialogVisible = ref(false)
const financeType = ref('order')
const financeFormRef = ref<FormInstance>()
const financeForm = reactive({
  product: '',
  receivableId: '',
  amount: 100000,
  term: 30,
  guarantee: '信用'
})
const financeRules: FormRules = {
  product: [{ required: true, message: '请填写订单标的', trigger: 'blur' }],
  receivableId: [{ required: true, message: '请选择应收账款', trigger: 'change' }],
  amount: [{ required: true, type: 'number', min: 1000, message: '融资金额不能低于 1000 元', trigger: 'change' }]
}

const insuranceTypes = ['种植保险', '养殖保险', '价格保险', '气象指数保险', '质量保险']
const insuranceDialogVisible = ref(false)
const insuranceFormRef = ref<FormInstance>()
const insuranceForm = reactive({
  type: '种植保险',
  crop: '',
  area: 0,
  coverage: 100000,
  term_months: 12
})
const insuranceRules: FormRules = {
  crop: [{ required: true, message: '请填写保险标的', trigger: 'blur' }],
  coverage: [{ required: true, type: 'number', min: 10000, message: '保额不能低于 1 万元', trigger: 'change' }]
}

const submitting = ref(false)

const showApiError = (e: unknown, fallback: string) => {
  const detail = axios.isAxiosError(e) ? e.response?.data?.detail : undefined
  ElMessage.error(typeof detail === 'string' ? detail : fallback)
}

const refreshData = async () => {
  await fetchData()
}

const getStatusType = (status: string) => {
  switch (status) {
    case '已放款':
    case '已结清':
      return 'success'
    case '审核中':
    case '放款中':
      return 'warning'
    case '已批准':
      return 'primary'
    case '已拒绝':
      return 'danger'
    default:
      return 'info'
  }
}

const getReceivableStatusType = (status: string) => {
  switch (status) {
    case '已逾期':
    case '坏账':
      return 'danger'
    case '即将到期':
      return 'warning'
    case '已收回':
      return 'success'
    default:
      return 'info'
  }
}

// 信用分区间为 300-850，换算为进度百分比
const scorePercentage = (score: number) => Math.min(100, Math.max(0, Math.round(((score - 300) / 550) * 100)))

// el-progress 的 color 写入 SVG stroke，取设计令牌的色值（--color-success / --primary / --color-warning / --color-danger）
const getScoreColor = (score: number) => {
  if (score >= 750) return '#10B981'
  if (score >= 650) return '#165DFF'
  if (score >= 550) return '#F59E0B'
  return '#EF4444'
}

const getLevelType = (level: string) => {
  switch (level) {
    case 'AAA': return 'success'
    case 'AA': return 'primary'
    case 'A': return 'warning'
    default: return 'info'
  }
}

// 应收账款转让：仅未到期/即将到期且未转让的账款，融资额不超过未回款金额的 90%
const transferableReceivables = computed(() =>
  receivables.value.filter((r) => ['未到期', '即将到期'].includes(r.status) && !r.financing_order_id)
)
const selectedReceivable = computed(() => receivables.value.find((r) => r.id === financeForm.receivableId))
const maxFinanceAmount = computed(() => {
  const r = financeType.value === 'receivable' ? selectedReceivable.value : undefined
  return r ? Math.floor((r.amount - r.paid_amount) * 0.9) : 1000000
})
const onReceivableChange = () => {
  const r = selectedReceivable.value
  if (r) financeForm.amount = Math.floor((r.amount - r.paid_amount) * 0.8)
}

const showTransferDialog = (row: Receivable) => {
  showFinanceDialog('receivable')
  financeForm.receivableId = row.id
  onReceivableChange()
}

const showFinanceDialog = (type: string) => {
  financeType.value = type
  financeDialogVisible.value = true
}

const showInsuranceDialog = () => {
  insuranceDialogVisible.value = true
}

const submitFinance = async () => {
  if (!(await financeFormRef.value?.validate().catch(() => false))) return
  submitting.value = true
  try {
    if (financeType.value === 'receivable') {
      await axios.post<FinancingOrder>(`${API}/receivables/${financeForm.receivableId}/transfer`, {
        amount: financeForm.amount,
        term: financeForm.term
      })
    } else {
      await axios.post<FinancingOrder>(`${API}/financing/orders`, {
        product: financeForm.product,
        amount: financeForm.amount,
        term: financeForm.term,
        collateral: financeForm.guarantee
      })
    }
    ElMessage.success(financeType.value === 'receivable' ? '应收账款转让申请已提交，审核中' : '融资申请已提交，审核中')
    financeDialogVisible.value = false
    financeFormRef.value?.resetFields()
    await fetchData()
  } catch (e) {
    showApiError(e, '融资申请提交失败')
  } finally {
    submitting.value = false
  }
}

const submitInsurance = async () => {
  if (!(await insuranceFormRef.value?.validate().catch(() => false))) return
  submitting.value = true
  try {
    await axios.post<Insurance>(`${API}/insurance`, { ...insuranceForm })
    ElMessage.success('投保成功')
    insuranceDialogVisible.value = false
    insuranceFormRef.value?.resetFields()
    await fetchData()
  } catch (e) {
    showApiError(e, '投保失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-tip {
  margin-left: 12px;
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.full-width {
  width: 100%;
}

.transferred-tag {
  margin-left: 6px;
}

.credit-score {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 8px 0;
}

.score-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-content .score {
  font-size: var(--font-2xl);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.score-content .label {
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.credit-info {
  flex: 1;
  min-width: 0;
  margin: 0;
}

.credit-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 0;
  font-size: var(--font-sm);
  border-bottom: 1px solid var(--border-color);
}

.credit-row:last-child {
  border-bottom: none;
}

.credit-row dt {
  color: var(--text-secondary);
}

.credit-row dd {
  margin: 0;
  font-weight: 600;
  color: var(--text-primary);
  text-align: right;
}

@media (max-width: 768px) {
  .credit-score {
    flex-direction: column;
    gap: 16px;
  }

  .credit-info {
    width: 100%;
  }
}
</style>
