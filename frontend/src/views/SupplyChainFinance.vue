<template>
  <div class="finance-container">
    <div class="header">
      <h2>💰 供应链金融</h2>
      <el-button type="primary" :loading="loading" @click="refreshData">
        刷新数据
      </el-button>
    </div>
    
    <!-- 金融数据概览 -->
    <el-row :gutter="20" class="stat-cards" v-loading="loading">
      <el-col :span="6" v-for="stat in financeStats" :key="stat.title">
        <el-card class="stat-card" :style="{ borderLeft: `4px solid ${stat.color}` }">
          <div class="stat-info">
            <h3>{{ stat.value }}</h3>
            <p>{{ stat.title }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 融资申请 -->
    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <h3>💳 订单融资</h3>
          <el-button type="primary" size="small" @click="showFinanceDialog('order')">申请融资</el-button>
        </div>
      </template>
      <el-table :data="orderFinance" v-loading="loading" empty-text="暂无融资数据" style="width: 100%">
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
    </el-card>
    
    <!-- 应收账款 -->
    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <h3>📄 应收账款</h3>
          <el-button type="primary" size="small" @click="showFinanceDialog('receivable')">转让应收款</el-button>
        </div>
      </template>
      <el-table :data="receivables" v-loading="loading" empty-text="暂无应收账款" style="width: 100%">
        <el-table-column prop="invoice_no" label="发票号" width="160" />
        <el-table-column prop="debtor" label="买方" />
        <el-table-column label="金额">
          <template #default="{ row }">{{ formatMoney(row.amount) }}</template>
        </el-table-column>
        <el-table-column prop="due_date" label="到期日" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getReceivableStatusType(row.status)">
              {{ row.status }}
            </el-tag>
            <el-tag v-if="row.financing_order_id" type="info" size="small" class="transferred-tag">已转让</el-tag>
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
            <el-button type="success" link>催收</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 农业保险 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <h3>🛡️ 农业保险</h3>
              <el-button type="primary" size="small" @click="showInsuranceDialog">购买保险</el-button>
            </div>
          </template>
          <el-table :data="insurances" v-loading="loading" empty-text="暂无保单" style="width: 100%">
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
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>
            <h3>📊 信用评估</h3>
          </template>
          <el-empty v-if="!creditScore && !loading" description="暂无信用评估数据" />
          <div v-else-if="creditScore" class="credit-score">
            <el-progress type="circle" :percentage="scorePercentage(creditScore.credit_score)" :color="getScoreColor(creditScore.credit_score)" :width="150">
              <template #default>
                <div class="score-content">
                  <span class="score">{{ creditScore.credit_score }}</span>
                  <span class="label">信用分</span>
                </div>
              </template>
            </el-progress>
            <div class="credit-info">
              <h4>信用等级: <el-tag :type="getLevelType(creditScore.level)">{{ creditScore.level }}</el-tag></h4>
              <p>评估主体: <span class="highlight">{{ creditScore.entity_name }}（{{ creditScore.entity_type }}）</span></p>
              <p>财务 / 经营: <span class="highlight">{{ creditScore.factors.financial }} / {{ creditScore.factors.operation }}</span></p>
              <p>管理 / 行业: <span class="highlight">{{ creditScore.factors.management }} / {{ creditScore.factors.industry }}</span></p>
              <p>下次复评: <span class="highlight">{{ creditScore.next_review }}</span></p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 融资申请对话框 -->
    <el-dialog v-model="financeDialogVisible" :title="financeType === 'order' ? '订单融资申请' : '应收账款转让'" width="500px">
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
          <el-select v-model="financeForm.receivableId" placeholder="选择未到期的应收账款" style="width: 100%" @change="onReceivableChange">
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
    <el-dialog v-model="insuranceDialogVisible" title="购买农业保险" width="500px">
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

interface StatCard {
  title: string
  value: string
  color: string
}

const loading = ref(false)
const financeStats = ref<StatCard[]>([])
const orderFinance = ref<FinancingOrder[]>([])
const receivables = ref<Receivable[]>([])
const insurances = ref<Insurance[]>([])
const creditScore = ref<CreditAssessment | null>(null)

const formatMoney = (value: number) => {
  if (value >= 100000000) return `¥${(value / 100000000).toFixed(2)}亿`
  if (value >= 10000) return `¥${(value / 10000).toFixed(1)}万`
  return `¥${value.toLocaleString()}`
}

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
      { title: '总融资额', value: formatMoney(finStatsRes.data.total_financed), color: '#409EFF' },
      { title: '应收未收', value: formatMoney(recStatsRes.data.outstanding), color: '#E6A23C' },
      { title: '平均融资利率', value: `${finStatsRes.data.avg_rate}%`, color: '#67C23A' },
      { title: '保险保障', value: formatMoney(insStatsRes.data.total_coverage), color: '#F56C6C' }
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

const getScoreColor = (score: number) => {
  if (score >= 750) return '#67C23A'
  if (score >= 650) return '#409EFF'
  if (score >= 550) return '#E6A23C'
  return '#F56C6C'
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
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.transferred-tag {
  margin-left: 6px;
}

.finance-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  font-size: 24px;
  color: #303133;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  padding: 20px;
}

.stat-info h3 {
  font-size: 24px;
  margin: 0 0 5px;
  color: #303133;
}

.stat-info p {
  margin: 0;
  color: #909399;
}

.section-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.credit-score {
  display: flex;
  align-items: center;
  gap: 30px;
}

.score-content {
  text-align: center;
}

.score-content .score {
  display: block;
  font-size: 36px;
  font-weight: bold;
  color: #303133;
}

.score-content .label {
  font-size: 14px;
  color: #909399;
}

.credit-info h4 {
  margin: 0 0 15px;
}

.credit-info p {
  margin: 8px 0;
  color: #606266;
}

.credit-info .highlight {
  color: #409EFF;
  font-weight: bold;
}
</style>
