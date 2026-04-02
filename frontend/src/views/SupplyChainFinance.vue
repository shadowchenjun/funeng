<template>
  <div class="finance-container">
    <div class="header">
      <h2>💰 供应链金融</h2>
      <el-button type="primary" @click="refreshData">
        刷新数据
      </el-button>
    </div>
    
    <!-- 金融数据概览 -->
    <el-row :gutter="20" class="stat-cards">
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
      <el-table :data="orderFinance" style="width: 100%">
        <el-table-column prop="orderId" label="订单号" width="120" />
        <el-table-column prop="amount" label="订单金额" />
        <el-table-column prop="financeAmount" label="融资金额" />
        <el-table-column prop="rate" label="利率" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applyDate" label="申请日期" />
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
      <el-table :data="receivables" style="width: 100%">
        <el-table-column prop="invoiceNo" label="发票号" width="150" />
        <el-table-column prop="buyer" label="买方" />
        <el-table-column prop="amount" label="金额" />
        <el-table-column prop="dueDate" label="到期日" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === '已到期' ? 'danger' : row.status === '待收款' ? 'warning' : 'success'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="">
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
          <el-table :data="insurances" style="width: 100%">
            <el-table-column prop="type" label="险种" />
            <el-table-column prop="coverage" label="保额" />
            <el-table-column prop="premium" label="保费" />
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
          <div class="credit-score">
            <el-progress type="circle" :percentage="creditScore.score" :color="getScoreColor(creditScore.score)" :width="150">
              <template #default>
                <div class="score-content">
                  <span class="score">{{ creditScore.score }}</span>
                  <span class="label">信用分</span>
                </div>
              </template>
            </el-progress>
            <div class="credit-info">
              <h4>信用等级: <el-tag :type="getLevelType(creditScore.level)">{{ creditScore.level }}</el-tag></h4>
              <p>可贷款额度: <span class="highlight">¥{{ creditScore.creditLimit }}</span></p>
              <p>当前已用: <span class="highlight">¥{{ creditScore.used }}</span></p>
              <p>可用额度: <span class="highlight">¥{{ creditScore.available }}</span></p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 融资申请对话框 -->
    <el-dialog v-model="financeDialogVisible" :title="financeType === 'order' ? '订单融资申请' : '应收账款转让'" width="500px">
      <el-form :model="financeForm" label-width="100px">
        <el-form-item label="融资类型">
          <el-select v-model="financeType" disabled>
            <el-option label="订单融资" value="order" />
            <el-option label="应收账款转让" value="receivable" />
          </el-select>
        </el-form-item>
        <el-form-item label="融资金额">
          <el-input-number v-model="financeForm.amount" :min="1000" :max="1000000" />
        </el-form-item>
        <el-form-item label="融资期限">
          <el-select v-model="financeForm.term">
            <el-option label="30天" :value="30" />
            <el-option label="60天" :value="60" />
            <el-option label="90天" :value="90" />
          </el-select>
        </el-form-item>
        <el-form-item label="担保方式">
          <el-radio-group v-model="financeForm.guarantee">
            <el-radio label="信用">信用</el-radio>
            <el-radio label="质押">质押</el-radio>
            <el-radio label="抵押">抵押</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="financeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFinance">提交申请</el-button>
      </template>
    </el-dialog>
    
    <!-- 保险购买对话框 -->
    <el-dialog v-model="insuranceDialogVisible" title="购买农业保险" width="500px">
      <el-form :model="insuranceForm" label-width="100px">
        <el-form-item label="险种类型">
          <el-select v-model="insuranceForm.type">
            <el-option label="种植险" value="planting" />
            <el-option label="养殖险" value="breeding" />
            <el-option label="财产险" value="property" />
          </el-select>
        </el-form-item>
        <el-form-item label="保额">
          <el-input-number v-model="insuranceForm.coverage" :min="10000" :max="1000000" />
        </el-form-item>
        <el-form-item label="保险期限">
          <el-select v-model="insuranceForm.term">
            <el-option label="3个月" :value="3" />
            <el-option label="6个月" :value="6" />
            <el-option label="12个月" :value="12" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="insuranceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitInsurance">立即投保</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

onMounted(() => {
  window.scrollTo(0, 0)
})

const financeStats = ref([
  { title: '总融资额', value: '¥256万', color: '#409EFF' },
  { title: '待还款', value: '¥85万', color: '#E6A23C' },
  { title: '信用额度', value: '¥500万', color: '#67C23A' },
  { title: '保险保障', value: '¥1200万', color: '#F56C6C' }
])

const orderFinance = ref([
  { orderId: 'ORD20260201', amount: '¥50,000', financeAmount: '¥40,000', rate: '3.5%', status: '已放款', applyDate: '2026-02-01' },
  { orderId: 'ORD20260205', amount: '¥80,000', financeAmount: '¥64,000', rate: '3.5%', status: '审核中', applyDate: '2026-02-05' },
  { orderId: 'ORD20260210', amount: '¥120,000', financeAmount: '¥96,000', rate: '3.5%', status: '待还款', applyDate: '2026-02-10' }
])

const receivables = ref([
  { invoiceNo: 'INV202602001', buyer: '某大型超市', amount: '¥80,000', dueDate: '2026-03-15', status: '待收款' },
  { invoiceNo: 'INV202601028', buyer: '某电商平台', amount: '¥120,000', dueDate: '2026-02-28', status: '已到期' },
  { invoiceNo: 'INV202602015', buyer: '某批发商', amount: '¥56,000', dueDate: '2026-04-01', status: '已收讫' }
])

const insurances = ref([
  { type: '种植险 - 大棚蔬菜', coverage: '¥50万', premium: '¥5,000/年', status: '生效中' },
  { type: '养殖险 - 家禽', coverage: '¥30万', premium: '¥3,000/年', status: '生效中' },
  { type: '财产险 - 仓库', coverage: '¥100万', premium: '¥8,000/年', status: '待生效' }
])

const creditScore = ref({
  score: 780,
  level: 'AAA',
  creditLimit: 5000000,
  used: 850000,
  available: 4150000
})

const financeDialogVisible = ref(false)
const financeType = ref('order')
const financeForm = reactive({
  amount: 0,
  term: 30,
  guarantee: '信用'
})

const insuranceDialogVisible = ref(false)
const insuranceForm = reactive({
  type: 'planting',
  coverage: 100000,
  term: 12
})

const refreshData = () => {
  ElMessage.success('数据已刷新')
}

const getStatusType = (status: string) => {
  switch (status) {
    case '已放款': return 'success'
    case '审核中': return 'warning'
    case '待还款': return 'danger'
    default: return 'info'
  }
}

const getScoreColor = (score: number) => {
  if (score >= 900) return '#67C23A'
  if (score >= 750) return '#409EFF'
  if (score >= 600) return '#E6A23C'
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

const showFinanceDialog = (type: string) => {
  financeType.value = type
  financeDialogVisible.value = true
}

const showInsuranceDialog = () => {
  insuranceDialogVisible.value = true
}

const submitFinance = () => {
  ElMessage.success('融资申请已提交，审核中...')
  financeDialogVisible.value = false
}

const submitInsurance = () => {
  ElMessage.success('保险购买成功！')
  insuranceDialogVisible.value = false
}
</script>

<style scoped>
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
