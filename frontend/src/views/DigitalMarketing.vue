<template>
  <div class="page-container">
    <PageHeader title="数字营销" subtitle="数据驱动 · 精准触达 · 高效转化" />

    <ModuleNav v-model="activeTab" :groups="navGroups" aria-label="数字营销功能导航" />

    <!-- 数据概览 -->
    <div v-show="activeTab === 'stats'">
      <div class="stat-grid">
        <StatCard
          v-for="stat in marketingStats"
          :key="stat.title"
          :value="stat.value"
          :title="stat.title"
          :trend="stat.trend"
          :type="stat.type"
          :icon="stat.icon"
        />
      </div>

      <SectionCard title="渠道概览" :icon="ChatDotRound">
        <div class="tile-grid">
          <div v-for="ch in channelCards.slice(0, 3)" :key="ch.name" class="tile channel-tile">
            <span class="channel-icon"><el-icon :size="22"><component :is="ch.icon" /></el-icon></span>
            <div class="channel-body">
              <div class="tile-title">{{ ch.name }}</div>
              <div class="tile-meta">
                <span v-for="row in ch.rows" :key="row.label">{{ row.label }}：<b class="channel-num">{{ row.value }}</b></span>
              </div>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 会员管理 -->
    <div v-show="activeTab === 'member'">
      <SectionCard title="会员管理" :icon="User">
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="showMemberDialog()">添加会员</el-button>
        </template>
        <EmptyState v-if="members.length === 0" :icon="User" title="暂无会员" description="点击「添加会员」创建第一位会员" />
        <div v-else class="tile-grid">
          <div v-for="member in members" :key="member.id" class="tile">
            <div class="tile-header">
              <span class="member-head">
                <el-avatar :size="36" class="member-avatar">{{ member.name.charAt(0) }}</el-avatar>
                <span>
                  <span class="tile-title">{{ member.name }}</span>
                  <span class="member-phone">{{ member.phone }}</span>
                </span>
              </span>
              <el-tag :type="getLevelType(member.level)">{{ member.level }}</el-tag>
            </div>
            <div class="tile-meta">
              <span>积分：{{ member.points }} · 消费：{{ member.totalSpent }}</span>
            </div>
            <div class="tile-actions">
              <el-button type="primary" link @click="editMember(member)">编辑</el-button>
              <el-button type="danger" link @click="deleteMember(member)">删除</el-button>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 营销活动 -->
    <div v-show="activeTab === 'campaign'">
      <SectionCard title="营销活动" :icon="Present">
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="showCampaignDialog()">创建活动</el-button>
        </template>
        <EmptyState v-if="campaigns.length === 0" :icon="Present" title="暂无营销活动" description="点击「创建活动」发起第一个活动" />
        <div v-else class="tile-grid">
          <div v-for="campaign in campaigns" :key="campaign.id" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ campaign.name }}</span>
              <el-tag :type="campaign.status === '进行中' ? 'success' : 'info'">{{ campaign.status }}</el-tag>
            </div>
            <div class="tile-meta">
              <span>类型：{{ campaign.type }} · 参与：{{ campaign.participants }} 人</span>
              <span>销售额：{{ campaign.sales }}</span>
              <span>截止：{{ campaign.endDate || '—' }}</span>
            </div>
            <div class="tile-actions">
              <el-button type="primary" link @click="editCampaign(campaign)">编辑</el-button>
              <el-button type="danger" link @click="deleteCampaign(campaign)">删除</el-button>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 营销渠道 -->
    <div v-show="activeTab === 'channel'">
      <SectionCard title="营销渠道" :icon="ChatDotRound">
        <div class="tile-grid">
          <div v-for="ch in channelCards" :key="ch.name" class="tile channel-tile">
            <span class="channel-icon"><el-icon :size="22"><component :is="ch.icon" /></el-icon></span>
            <div class="channel-body">
              <div class="tile-title">{{ ch.name }}</div>
              <div class="tile-meta">
                <span v-for="row in ch.detail" :key="row.label">{{ row.label }}：<b class="channel-num">{{ row.value }}</b></span>
              </div>
              <div class="tile-actions channel-actions">
                <el-button>管理</el-button>
              </div>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 添加/编辑会员对话框 -->
    <el-dialog v-model="memberDialogVisible" :title="isEditMember ? '编辑会员' : '添加会员'" class="dialog-md">
      <el-form :model="memberForm" label-width="80px">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="姓名" required>
              <el-input v-model="memberForm.name" placeholder="会员姓名" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="性别">
              <el-select v-model="memberForm.gender" class="w-full">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="电话" required>
              <el-input v-model="memberForm.phone" placeholder="手机号码" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="生日">
              <el-date-picker v-model="memberForm.birthday" type="date" placeholder="选择日期" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="邮箱">
              <el-input v-model="memberForm.email" placeholder="邮箱地址" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="地址">
              <el-input v-model="memberForm.address" placeholder="联系地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">会员信息</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="等级">
              <el-select v-model="memberForm.level" class="w-full">
                <el-option label="普通会员" value="普通" />
                <el-option label="银牌会员" value="银牌" />
                <el-option label="金牌会员" value="金牌" />
                <el-option label="VIP会员" value="VIP" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="注册日期">
              <el-date-picker v-model="memberForm.registerDate" type="date" placeholder="选择日期" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="积分">
              <el-input-number v-model="memberForm.points" :min="0" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="消费额">
              <el-input v-model="memberForm.totalSpent" placeholder="如：¥10,000" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="memberDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMember">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 创建/编辑活动对话框 -->
    <el-dialog v-model="campaignDialogVisible" :title="isEditCampaign ? '编辑活动' : '创建活动'" class="dialog-sm">
      <el-form :model="campaignForm" label-width="80px">
        <el-form-item label="活动名称" required>
          <el-input v-model="campaignForm.name" placeholder="活动名称" />
        </el-form-item>
        <el-form-item label="活动类型">
          <el-select v-model="campaignForm.type" class="w-full">
            <el-option label="满减活动" value="满减活动" />
            <el-option label="折扣活动" value="折扣活动" />
            <el-option label="试用活动" value="试用活动" />
            <el-option label="抽奖活动" value="抽奖活动" />
            <el-option label="秒杀活动" value="秒杀活动" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="campaignForm.status" class="w-full">
            <el-option label="进行中" value="进行中" />
            <el-option label="未开始" value="未开始" />
            <el-option label="已结束" value="已结束" />
          </el-select>
        </el-form-item>
        <el-form-item label="参与人数">
          <el-input-number v-model="campaignForm.participants" :min="0" class="w-full" />
        </el-form-item>
        <el-form-item label="销售额">
          <el-input v-model="campaignForm.sales" placeholder="如：¥100,000" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="campaignForm.endDate" type="date" placeholder="选择日期" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="campaignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCampaign">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotRound, DataAnalysis, Message, Money, Plus, Present, ShoppingCart, TrendCharts, User, UserFilled, VideoCamera, View
} from '@element-plus/icons-vue'
import type { Component } from 'vue'
import type { ModuleNavGroup } from '../components/ui/ModuleNav.vue'
import axios from 'axios'
import { formatMoneyExact as formatMoney } from '../utils/format'

const activeTab = ref('stats')
const navGroups: ModuleNavGroup[] = [
  {
    items: [
      { key: 'stats', label: '数据概览', icon: DataAnalysis },
      { key: 'member', label: '会员管理', icon: User },
      { key: 'campaign', label: '营销活动', icon: Present },
      { key: 'channel', label: '营销渠道', icon: ChatDotRound }
    ]
  }
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

// 营销数据（来自 /analytics：今日指标及与昨日对比）
const formatNumber = (n: number) => Number(n || 0).toLocaleString('zh-CN')

interface MarketingStat {
  title: string
  value: string
  trend: number
  type: 'primary' | 'success'
  icon: Component
}

const marketingStats = ref<MarketingStat[]>([
  { title: '今日销售额', value: '--', trend: 0, type: 'primary', icon: Money },
  { title: '访客数量', value: '--', trend: 0, type: 'primary', icon: View },
  { title: '转化率', value: '--', trend: 0, type: 'primary', icon: TrendCharts },
  { title: '新增会员', value: '--', trend: 0, type: 'primary', icon: UserFilled }
])

const channelStats = reactive({
  liveSessions: 0, liveSales: 0, followers: 0, newFollowers: 0,
  products: 0, pendingOrders: 0, pushSent: 0, pushOpenRate: 0
})

// 渠道卡片：概览页取前 3 个渠道的摘要（rows），渠道页展示全部 4 个（detail）
const channelCards = computed(() => [
  {
    name: '直播带货', icon: VideoCamera,
    rows: [{ label: '直播', value: channelStats.liveSessions }, { label: '销售额', value: formatMoney(channelStats.liveSales) }],
    detail: [{ label: '进行中', value: channelStats.liveSessions }, { label: '今日销售额', value: formatMoney(channelStats.liveSales) }]
  },
  {
    name: '社交推广', icon: ChatDotRound,
    rows: [{ label: '粉丝', value: formatNumber(channelStats.followers) }, { label: '新增', value: `+${formatNumber(channelStats.newFollowers)}` }],
    detail: [{ label: '粉丝', value: formatNumber(channelStats.followers) }, { label: '今日新增', value: `+${formatNumber(channelStats.newFollowers)}` }]
  },
  {
    name: '电商管理', icon: ShoppingCart,
    rows: [{ label: '商品', value: channelStats.products }, { label: '订单', value: channelStats.pendingOrders }],
    detail: [{ label: '在售', value: channelStats.products }, { label: '待处理', value: channelStats.pendingOrders }]
  },
  {
    name: '消息推送', icon: Message,
    rows: [],
    detail: [{ label: '发送', value: formatNumber(channelStats.pushSent) }, { label: '打开率', value: `${channelStats.pushOpenRate}%` }]
  }
])

const loadAnalytics = async () => {
  try {
    const res = await axios.get('/api/digital-marketing/analytics')
    const t = res.data.today || {}
    const ch = res.data.channels || {}
    marketingStats.value = [
      { title: '今日销售额', value: formatMoney(t.sales), trend: t.sales_trend || 0, type: 'primary', icon: Money },
      { title: '访客数量', value: formatNumber(t.visitors), trend: t.visitors_trend || 0, type: 'primary', icon: View },
      { title: '转化率', value: `${t.conversion_rate || 0}%`, trend: t.conversion_trend || 0, type: 'primary', icon: TrendCharts },
      { title: '新增会员', value: formatNumber(t.new_members), trend: t.new_members_trend || 0, type: 'primary', icon: UserFilled }
    ]
    Object.assign(channelStats, {
      liveSessions: ch.live?.sessions || 0,
      liveSales: ch.live?.sales || 0,
      followers: ch.social?.followers || 0,
      newFollowers: ch.social?.new_followers || 0,
      products: ch.ecommerce?.products || 0,
      pendingOrders: ch.ecommerce?.pending_orders || 0,
      pushSent: ch.push?.sent || 0,
      pushOpenRate: ch.push?.open_rate || 0
    })
  } catch (e) {
    console.error('加载营销数据失败', e)
    ElMessage.error('加载营销数据失败')
  }
}

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
    loadAnalytics()
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
    loadAnalytics()
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
const levelTypes: Record<string, 'primary' | 'warning' | 'info'> = { 'VIP': 'primary', '金牌': 'warning', '银牌': 'info', '普通': 'info' }
const getLevelType = (level: string) => levelTypes[level] || 'info'

// 页面加载时获取数据
onMounted(() => {
  window.scrollTo(0, 0)
  loadMembers()
  loadCampaigns()
  loadAnalytics()
})
</script>

<style scoped>
.channel-tile {
  display: flex;
  gap: 12px;
}

.channel-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  color: var(--primary);
  background: var(--primary-light);
  border-radius: var(--radius-md);
}

.channel-body {
  flex: 1;
  min-width: 0;
}

.channel-body .tile-title {
  display: block;
  margin-bottom: 6px;
}

.channel-num {
  font-weight: 600;
  color: var(--text-primary);
}

.channel-actions {
  justify-content: flex-start;
}

.member-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.member-avatar {
  color: var(--primary);
  background: var(--primary-light);
  font-weight: 600;
}

.member-phone {
  display: block;
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}
</style>
