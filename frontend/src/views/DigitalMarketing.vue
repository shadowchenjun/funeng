<template>
  <div class="digital-marketing-container">
    <div class="header-mobile">
      <h2>📱 数字营销</h2>
    </div>
    
    <!-- 快捷入口 -->
    <el-row :gutter="10" class="quick-nav">
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'stats'">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据概览</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'member'">
          <el-icon><User /></el-icon>
          <span>会员管理</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'campaign'">
          <el-icon><Present /></el-icon>
          <span>营销活动</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'channel'">
          <el-icon><ChatDotRound /></el-icon>
          <span>营销渠道</span>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 数据概览 -->
    <div v-if="activeTab === 'stats'">
      <el-row :gutter="10" class="stat-cards">
        <el-col :span="12" v-for="stat in marketingStats" :key="stat.title">
          <el-card class="stat-card" :style="{ borderLeft: `4px solid ${stat.color}` }">
            <div class="stat-info">
              <h3>{{ stat.value }}</h3>
              <p>{{ stat.title }}</p>
              <span :class="['trend', stat.trend > 0 ? 'up' : 'down']">
                {{ stat.trend > 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}%
              </span>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 营销渠道 -->
      <el-row :gutter="10" class="channel-section">
        <el-col :span="8">
          <el-card class="channel-card">
            <div class="channel-icon">
              <el-icon :size="32" color="#07C160">
                <VideoCamera />
              </el-icon>
            </div>
            <h4>直播带货</h4>
            <p>直播: <span class="highlight">3</span></p>
            <p>销售额: <span class="highlight">¥12,580</span></p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="channel-card">
            <div class="channel-icon">
              <el-icon :size="32" color="#FF6B00">
                <ChatDotRound />
              </el-icon>
            </div>
            <h4>社交推广</h4>
            <p>粉丝: <span class="highlight">28,560</span></p>
            <p>新增: <span class="highlight">+856</span></p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="channel-card">
            <div class="channel-icon">
              <el-icon :size="32" color="#0089FF">
                <ShoppingCart />
              </el-icon>
            </div>
            <h4>电商管理</h4>
            <p>商品: <span class="highlight">156</span></p>
            <p>订单: <span class="highlight">23</span></p>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 会员管理 -->
    <el-card v-if="activeTab === 'member'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>👥 会员管理</span>
          <el-button type="primary" size="small" @click="showMemberDialog()">+ 添加会员</el-button>
        </div>
      </template>
      
      <!-- 移动端卡片式会员列表 -->
      <div class="member-cards">
        <el-card v-for="member in members" :key="member.id" class="member-card">
          <div class="member-info">
            <el-avatar :size="40" :style="{ backgroundColor: getLevelColor(member.level) }">
              {{ member.name.charAt(0) }}
            </el-avatar>
            <div class="member-detail">
              <div class="member-name">{{ member.name }}</div>
              <div class="member-phone">{{ member.phone }}</div>
            </div>
            <el-tag :type="getLevelType(member.level)" size="small">{{ member.level }}</el-tag>
          </div>
          <div class="member-stats">
            <span>积分: {{ member.points }}</span>
            <span>消费: {{ member.totalSpent }}</span>
          </div>
          <div class="member-actions">
            <el-button type="primary" link size="small" @click="editMember(member)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteMember(member)">删除</el-button>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 营销活动 -->
    <el-card v-if="activeTab === 'campaign'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🎯 营销活动</span>
          <el-button type="primary" size="small" @click="showCampaignDialog()">+ 创建活动</el-button>
        </div>
      </template>
      
      <!-- 移动端卡片式活动列表 -->
      <div class="campaign-cards">
        <el-card v-for="campaign in campaigns" :key="campaign.id" class="campaign-card">
          <div class="campaign-header">
            <h4>{{ campaign.name }}</h4>
            <el-tag :type="campaign.status === '进行中' ? 'success' : 'info'" size="small">
              {{ campaign.status }}
            </el-tag>
          </div>
          <div class="campaign-info">
            <span>类型: {{ campaign.type }}</span>
            <span>参与: {{ campaign.participants }}人</span>
            <span>销售额: {{ campaign.sales }}</span>
            <span>截止: {{ campaign.endDate }}</span>
          </div>
          <div class="campaign-actions">
            <el-button type="primary" link size="small" @click="editCampaign(campaign)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteCampaign(campaign)">删除</el-button>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 营销渠道详情 -->
    <el-card v-if="activeTab === 'channel'" class="section-card">
      <template #header>
        <span>📢 营销渠道</span>
      </template>
      
      <el-row :gutter="10">
        <el-col :span="12">
          <el-card class="channel-detail-card">
            <el-icon :size="32" color="#07C160"><VideoCamera /></el-icon>
            <h4>直播带货</h4>
            <p>进行中: 3</p>
            <p>今日销售额: ¥12,580</p>
            <el-button type="primary" size="small" style="margin-top: 8px;">管理</el-button>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="channel-detail-card">
            <el-icon :size="32" color="#FF6B00"><ChatDotRound /></el-icon>
            <h4>社交推广</h4>
            <p>粉丝: 28,560</p>
            <p>今日新增: +856</p>
            <el-button type="primary" size="small" style="margin-top: 8px;">管理</el-button>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="channel-detail-card">
            <el-icon :size="32" color="#0089FF"><ShoppingCart /></el-icon>
            <h4>电商管理</h4>
            <p>在售: 156</p>
            <p>待处理: 23</p>
            <el-button type="primary" size="small" style="margin-top: 8px;">管理</el-button>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="channel-detail-card">
            <el-icon :size="32" color="#F56C6C"><Message /></el-icon>
            <h4>消息推送</h4>
            <p>发送: 1,280</p>
            <p>打开率: 68%</p>
            <el-button type="primary" size="small" style="margin-top: 8px;">管理</el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 添加/编辑会员对话框 -->
    <el-dialog v-model="memberDialogVisible" :title="isEditMember ? '编辑会员' : '添加会员'" width="95%">
      <el-form :model="memberForm" label-width="70px" size="small">
        <el-form-item label="姓名" required>
          <el-input v-model="memberForm.name" placeholder="会员姓名" />
        </el-form-item>
        <el-form-item label="电话" required>
          <el-input v-model="memberForm.phone" placeholder="手机号码" />
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="memberForm.level" style="width: 100%">
            <el-option label="普通会员" value="普通" />
            <el-option label="银牌会员" value="银牌" />
            <el-option label="金牌会员" value="金牌" />
            <el-option label="VIP会员" value="VIP" />
          </el-select>
        </el-form-item>
        <el-form-item label="积分">
          <el-input-number v-model="memberForm.points" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="消费额">
          <el-input v-model="memberForm.totalSpent" placeholder="如: ¥10,000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="memberDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveMember" size="small">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 创建/编辑活动对话框 -->
    <el-dialog v-model="campaignDialogVisible" :title="isEditCampaign ? '编辑活动' : '创建活动'" width="95%">
      <el-form :model="campaignForm" label-width="70px" size="small">
        <el-form-item label="活动名称" required>
          <el-input v-model="campaignForm.name" placeholder="活动名称" />
        </el-form-item>
        <el-form-item label="活动类型">
          <el-select v-model="campaignForm.type" style="width: 100%">
            <el-option label="满减活动" value="满减活动" />
            <el-option label="折扣活动" value="折扣活动" />
            <el-option label="试用活动" value="试用活动" />
            <el-option label="抽奖活动" value="抽奖活动" />
            <el-option label="秒杀活动" value="秒杀活动" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="campaignForm.status" style="width: 100%">
            <el-option label="进行中" value="进行中" />
            <el-option label="未开始" value="未开始" />
            <el-option label="已结束" value="已结束" />
          </el-select>
        </el-form-item>
        <el-form-item label="参与人数">
          <el-input-number v-model="campaignForm.participants" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="销售额">
          <el-input v-model="campaignForm.sales" placeholder="如: ¥100,000" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="campaignForm.endDate" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="campaignDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveCampaign" size="small">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataAnalysis, User, Present, ChatDotRound, VideoCamera, ShoppingCart, Message } from '@element-plus/icons-vue'

const activeTab = ref('stats')

// 营销数据
const marketingStats = ref([
  { title: '今日销售额', value: '¥28,560', color: '#67C23A', trend: 12.5 },
  { title: '访客数量', value: '3,256', color: '#409EFF', trend: 8.2 },
  { title: '转化率', value: '4.8%', color: '#E6A23C', trend: -2.1 },
  { title: '新增会员', value: '128', color: '#F56C6C', trend: 15.3 }
])

// 会员数据
const members = ref([
  { id: 1, name: '张先生', phone: '138****8888', level: 'VIP', points: 12580, totalSpent: '¥25,680' },
  { id: 2, name: '李女士', phone: '139****9999', level: '金牌', points: 8560, totalSpent: '¥18,560' },
  { id: 3, name: '王先生', phone: '137****7777', level: '银牌', points: 4280, totalSpent: '¥8,960' },
  { id: 4, name: '赵女士', phone: '136****6666', level: '普通', points: 1280, totalSpent: '¥2,580' },
  { id: 5, name: '刘先生', phone: '135****5555', level: '金牌', points: 15680, totalSpent: '¥32,800' }
])

// 活动数据
const campaigns = ref([
  { id: 1, name: '新春大促', type: '满减活动', status: '进行中', participants: 856, sales: '¥125,680', endDate: '2026-02-28' },
  { id: 2, name: '会员专享', type: '折扣活动', status: '进行中', participants: 456, sales: '¥68,900', endDate: '2026-03-15' },
  { id: 3, name: '新品试用', type: '试用活动', status: '已结束', participants: 280, sales: '¥12,500', endDate: '2026-02-10' },
  { id: 4, name: '五一特惠', type: '秒杀活动', status: '未开始', participants: 0, sales: '¥0', endDate: '2026-05-01' }
])

// 会员对话框
const memberDialogVisible = ref(false)
const isEditMember = ref(false)
const editingMemberId = ref<number>()
const memberForm = reactive({
  name: '',
  phone: '',
  level: '普通',
  points: 0,
  totalSpent: '¥0'
})

const showMemberDialog = () => {
  isEditMember.value = false
  Object.assign(memberForm, { name: '', phone: '', level: '普通', points: 0, totalSpent: '¥0' })
  memberDialogVisible.value = true
}

const editMember = (member: any) => {
  isEditMember.value = true
  editingMemberId.value = member.id
  Object.assign(memberForm, member)
  memberDialogVisible.value = true
}

const saveMember = () => {
  if (!memberForm.name || !memberForm.phone) {
    ElMessage.warning('请填写姓名和电话')
    return
  }
  
  if (isEditMember.value && editingMemberId.value) {
    const index = members.value.findIndex(m => m.id === editingMemberId.value)
    if (index !== -1) {
      members.value[index] = { ...memberForm, id: editingMemberId.value }
    }
    ElMessage.success('会员更新成功')
  } else {
    members.value.push({
      id: Date.now(),
      ...memberForm
    })
    ElMessage.success('会员添加成功')
  }
  memberDialogVisible.value = false
}

const deleteMember = async (member: any) => {
  try {
    await ElMessageBox.confirm(`确定删除会员 "${member.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    members.value = members.value.filter(m => m.id !== member.id)
    ElMessage.success('删除成功')
  } catch {}
}

// 活动对话框
const campaignDialogVisible = ref(false)
const isEditCampaign = ref(false)
const editingCampaignId = ref<number>()
const campaignForm = reactive({
  name: '',
  type: '满减活动',
  status: '未开始',
  participants: 0,
  sales: '¥0',
  endDate: ''
})

const showCampaignDialog = () => {
  isEditCampaign.value = false
  Object.assign(campaignForm, { name: '', type: '满减活动', status: '未开始', participants: 0, sales: '¥0', endDate: '' })
  campaignDialogVisible.value = true
}

const editCampaign = (campaign: any) => {
  isEditCampaign.value = true
  editingCampaignId.value = campaign.id
  Object.assign(campaignForm, campaign)
  campaignDialogVisible.value = true
}

const saveCampaign = () => {
  if (!campaignForm.name) {
    ElMessage.warning('请填写活动名称')
    return
  }
  
  if (isEditCampaign.value && editingCampaignId.value) {
    const index = campaigns.value.findIndex(c => c.id === editingCampaignId.value)
    if (index !== -1) {
      campaigns.value[index] = { ...campaignForm, id: editingCampaignId.value }
    }
    ElMessage.success('活动更新成功')
  } else {
    campaigns.value.push({
      id: Date.now(),
      ...campaignForm
    })
    ElMessage.success('活动创建成功')
  }
  campaignDialogVisible.value = false
}

const deleteCampaign = async (campaign: any) => {
  try {
    await ElMessageBox.confirm(`确定删除活动 "${campaign.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    campaigns.value = campaigns.value.filter(c => c.id !== campaign.id)
    ElMessage.success('删除成功')
  } catch {}
}

// 工具函数
const getLevelType = (level: string) => {
  const types: any = { 'VIP': 'danger', '金牌': 'warning', '银牌': 'info', '普通': '' }
  return types[level] || ''
}

const getLevelColor = (level: string) => {
  const colors: any = { 'VIP': '#F56C6C', '金牌': '#E6A23C', '银牌': '#909399', '普通': '#67C23A' }
  return colors[level] || '#67C23A'
}
</script>

<style scoped>
.digital-marketing-container {
  padding: 10px;
}

.header-mobile h2 {
  font-size: 16px;
  margin: 0 0 10px 0;
}

.quick-nav {
  margin-bottom: 10px;
}

.nav-card {
  text-align: center;
  padding: 10px 5px;
  cursor: pointer;
}

.nav-card :deep(.el-card__body) {
  padding: 10px;
}

.nav-card .el-icon {
  font-size: 24px;
  color: #409eff;
  display: block;
  margin-bottom: 4px;
}

.nav-card span {
  font-size: 11px;
  color: #606266;
}

.stat-cards {
  margin-bottom: 10px;
}

.stat-card {
  margin-bottom: 10px;
}

.stat-card h3 {
  margin: 0;
  font-size: 18px;
}

.stat-card p {
  margin: 5px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.stat-card .trend {
  font-size: 12px;
}

.trend.up { color: #67C23A; }
.trend.down { color: #F56C6C; }

.channel-section {
  margin-bottom: 10px;
}

.channel-card {
  text-align: center;
}

.channel-card h4 {
  margin: 8px 0;
  font-size: 14px;
}

.channel-card p {
  margin: 3px 0;
  font-size: 12px;
  color: #606266;
}

.highlight {
  color: #409eff;
  font-weight: bold;
}

.section-card {
  margin-bottom: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-size: 14px;
  font-weight: 500;
}

/* 会员卡片 */
.member-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-card {
  padding: 10px;
}

.member-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.member-detail {
  flex: 1;
}

.member-name {
  font-size: 14px;
  font-weight: 500;
}

.member-phone {
  font-size: 12px;
  color: #909399;
}

.member-stats {
  display: flex;
  gap: 15px;
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
}

.member-actions {
  display: flex;
  gap: 5px;
  margin-top: 8px;
}

/* 活动卡片 */
.campaign-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.campaign-card {
  padding: 10px;
}

.campaign-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.campaign-header h4 {
  margin: 0;
  font-size: 14px;
}

.campaign-info {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
}

.campaign-actions {
  display: flex;
  gap: 5px;
  margin-top: 8px;
}

/* 渠道详情 */
.channel-detail-card {
  text-align: center;
  margin-bottom: 10px;
}

.channel-detail-card h4 {
  margin: 8px 0;
  font-size: 13px;
}

.channel-detail-card p {
  margin: 3px 0;
  font-size: 12px;
  color: #606266;
}
</style>
