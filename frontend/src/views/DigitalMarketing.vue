<template>
  <div class="digital-marketing-container">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">📱 数字营销</h1>
        <p class="page-subtitle">数据驱动 · 精准触达 · 高效转化</p>
      </div>
    </header>

    <!-- 快捷入口 -->
    <div class="quick-nav-grid">
      <div
        v-for="(item, index) in navItems"
        :key="item.key"
        class="nav-card"
        :style="{ '--accent': item.color, '--delay': `${index * 0.05}s` }"
        @click="setActiveTab(item.key)"
      >
        <div class="nav-card-glow"></div>
        <div class="nav-card-content">
          <div class="nav-icon-wrapper">
            <el-icon :size="28" :color="item.color">
              <component :is="item.icon" />
            </el-icon>
          </div>
          <span class="nav-label">{{ item.label }}</span>
        </div>
      </div>
    </div>

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
      <el-form :model="memberForm" label-width="80px" size="small">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="姓名" required>
              <el-input v-model="memberForm.name" placeholder="会员姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="memberForm.gender" style="width: 100%">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="电话" required>
              <el-input v-model="memberForm.phone" placeholder="手机号码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生日">
              <el-date-picker v-model="memberForm.birthday" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="邮箱">
              <el-input v-model="memberForm.email" placeholder="邮箱地址" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="地址">
              <el-input v-model="memberForm.address" placeholder="联系地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">会员信息</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="等级">
              <el-select v-model="memberForm.level" style="width: 100%">
                <el-option label="普通会员" value="普通" />
                <el-option label="银牌会员" value="银牌" />
                <el-option label="金牌会员" value="金牌" />
                <el-option label="VIP会员" value="VIP" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="注册日期">
              <el-date-picker v-model="memberForm.registerDate" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="积分">
              <el-input-number v-model="memberForm.points" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="消费额">
              <el-input v-model="memberForm.totalSpent" placeholder="如: ¥10,000" />
            </el-form-item>
          </el-col>
        </el-row>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataAnalysis, User, Present, ChatDotRound, VideoCamera, ShoppingCart, Message } from '@element-plus/icons-vue'
import axios from 'axios'

const activeTab = ref('stats')
const setActiveTab = (tab: string) => { activeTab.value = tab }

const navItems = [
  { key: 'stats', label: '数据概览', icon: DataAnalysis, color: '#3B82F6' },
  { key: 'member', label: '会员管理', icon: User, color: '#10B981' },
  { key: 'campaign', label: '营销活动', icon: Present, color: '#F59E0B' },
  { key: 'channel', label: '营销渠道', icon: ChatDotRound, color: '#8B5CF6' }
]

// 会员数据
const members = ref<any[]>([])

// 加载会员数据
const loadMembers = async () => {
  try {
    const res = await axios.get('/api/digital-marketing/members')
    members.value = res.data.map((m: any) => ({
      id: m.id,
      name: m.name,
      phone: m.phone || '未填写',
      level: m.level || '普通',
      points: m.points || 0,
      totalSpent: m.totalSpent || '¥0',
      gender: m.gender,
      birthday: m.birthday,
      email: m.email,
      address: m.address,
      registerDate: m.registerDate
    }))
  } catch (e) {
    console.error('加载会员失败', e)
    ElMessage.error('加载会员数据失败')
  }
}

// 活动数据
const campaigns = ref<any[]>([])

// 加载活动数据
const loadCampaigns = async () => {
  try {
    const res = await axios.get('/api/digital-marketing/campaigns')
    campaigns.value = res.data.map((c: any) => ({
      id: c.id,
      name: c.name,
      type: c.type || '满减活动',
      status: c.status || '未开始',
      participants: c.participants || 0,
      sales: c.sales || '¥0',
      endDate: c.endDate || ''
    }))
  } catch (e) {
    console.error('加载活动失败', e)
    ElMessage.error('加载活动数据失败')
  }
}

// 营销数据
const marketingStats = ref([
  { title: '今日销售额', value: '¥28,560', color: '#67C23A', trend: 12.5 },
  { title: '访客数量', value: '3,256', color: '#409EFF', trend: 8.2 },
  { title: '转化率', value: '4.8%', color: '#E6A23C', trend: -2.1 },
  { title: '新增会员', value: '128', color: '#F56C6C', trend: 15.3 }
])

// 会员对话框
const memberDialogVisible = ref(false)
const isEditMember = ref(false)
const editingMemberId = ref<number>()
const memberForm = reactive({
  name: '', phone: '', level: '普通', points: 0, totalSpent: '¥0',
  gender: '男', birthday: '', email: '', address: '', registerDate: ''
})

const showMemberDialog = () => {
  isEditMember.value = false
  Object.assign(memberForm, {
    name: '', phone: '', level: '普通', points: 0, totalSpent: '¥0',
    gender: '男', birthday: '', email: '', address: '', registerDate: ''
  })
  memberDialogVisible.value = true
}

const editMember = (member: any) => {
  isEditMember.value = true
  editingMemberId.value = member.id
  Object.assign(memberForm, member)
  memberDialogVisible.value = true
}

const saveMember = async () => {
  if (!memberForm.name || !memberForm.phone) {
    ElMessage.warning('请填写姓名和电话')
    return
  }

  try {
    if (isEditMember.value && editingMemberId.value) {
      await axios.put(`/api/digital-marketing/members/${editingMemberId.value}`, {
        name: memberForm.name,
        phone: memberForm.phone,
        level: memberForm.level,
        points: memberForm.points,
        total_spent: memberForm.totalSpent,
        gender: memberForm.gender,
        birthday: memberForm.birthday,
        email: memberForm.email,
        address: memberForm.address,
        register_date: memberForm.registerDate
      })
      ElMessage.success('会员更新成功')
    } else {
      await axios.post('/api/digital-marketing/members', {
        name: memberForm.name,
        phone: memberForm.phone,
        level: memberForm.level,
        points: memberForm.points,
        total_spent: memberForm.totalSpent,
        gender: memberForm.gender,
        birthday: memberForm.birthday,
        email: memberForm.email,
        address: memberForm.address,
        register_date: memberForm.registerDate
      })
      ElMessage.success('会员添加成功')
    }
    memberDialogVisible.value = false
    await loadMembers()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const deleteMember = async (member: any) => {
  try {
    await ElMessageBox.confirm(`确定删除会员 "${member.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await axios.delete(`/api/digital-marketing/members/${member.id}`)
    ElMessage.success('删除成功')
    await loadMembers()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
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

const saveCampaign = async () => {
  if (!campaignForm.name) {
    ElMessage.warning('请填写活动名称')
    return
  }

  try {
    if (isEditCampaign.value && editingCampaignId.value) {
      await axios.put(`/api/digital-marketing/campaigns/${editingCampaignId.value}`, {
        name: campaignForm.name,
        campaign_type: campaignForm.type,
        status: campaignForm.status,
        participants: campaignForm.participants,
        sales: campaignForm.sales,
        end_date: campaignForm.endDate
      })
      ElMessage.success('活动更新成功')
    } else {
      await axios.post('/api/digital-marketing/campaigns', {
        name: campaignForm.name,
        campaign_type: campaignForm.type,
        status: campaignForm.status,
        participants: campaignForm.participants,
        sales: campaignForm.sales,
        end_date: campaignForm.endDate
      })
      ElMessage.success('活动创建成功')
    }
    campaignDialogVisible.value = false
    await loadCampaigns()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const deleteCampaign = async (campaign: any) => {
  try {
    await ElMessageBox.confirm(`确定删除活动 "${campaign.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await axios.delete(`/api/digital-marketing/campaigns/${campaign.id}`)
    ElMessage.success('删除成功')
    await loadCampaigns()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
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

// 页面加载时获取数据
onMounted(() => {
  window.scrollTo(0, 0)
  loadMembers()
  loadCampaigns()
})
</script>

<style scoped>
.digital-marketing-container {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
  background: var(--bg-secondary, #F8FAFC);
  min-height: calc(100vh - 64px);
}

/* ========== 页面头部 ========== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #0F172A);
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 15px;
  color: var(--text-secondary, #475569);
  margin: 0;
}

/* ========== 快捷入口导航 ========== */
.quick-nav-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}

.nav-card {
  position: relative;
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 14px;
  padding: 24px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  animation: fadeInUp 0.4s ease forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.nav-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--accent);
}

.nav-card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.nav-card:hover .nav-card-glow {
  transform: scaleX(1);
}

.nav-card-content {
  position: relative;
}

.nav-icon-wrapper {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary, #F8FAFC);
  border-radius: 14px;
  margin: 0 auto 14px;
  transition: all 0.3s ease;
}

.nav-card:hover .nav-icon-wrapper {
  background: color-mix(in srgb, var(--accent) 10%, transparent);
}

.nav-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #0F172A);
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .digital-marketing-container {
    padding: 20px;
  }

  .quick-nav-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .nav-card {
    padding: 20px 12px;
  }

  .nav-icon-wrapper {
    width: 48px;
    height: 48px;
  }

  .nav-label {
    font-size: 13px;
  }
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
