<template>
  <div class="home-container">
    <!-- 导航栏 -->
    <header class="main-nav">
      <div class="nav-brand">
        <img src="/logo-new.png" class="brand-icon" alt=" Logo" />
        <span class="brand-text"></span>
      </div>
      <nav class="nav-links">
        <a href="/" class="nav-link active">首页</a>
        <a href="/products" class="nav-link">产品</a>
        <a href="/categories" class="nav-link">分类</a>
        <a href="/dashboard" class="nav-link">仪表盘</a>
      </nav>
      <div class="nav-actions">
        <template v-if="!isLoggedIn">
          <button class="btn-nav-outline" @click="$router.push('/login')">登录</button>
          <button class="btn-nav-primary" @click="$router.push('/register')">注册</button>
        </template>
        <template v-else>
          <button class="btn-nav-primary" @click="$router.push('/dashboard')">进入控制台</button>
        </template>
      </div>
    </header>

    <!-- Hero 区域 -->
    <section class="hero-section">
      <div class="hero-bg-pattern"></div>
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-dot"></span>
          现代农业数字化赋能平台
        </div>
        <h1 class="hero-title">
          <span class="title-line">智慧农业</span>
          <span class="title-line accent">赋能未来</span>
        </h1>
        <p class="hero-description">
          融合物联网、大数据与人工智能技术，构建覆盖农业生产、<br class="hide-mobile">
          冷链物流、数字营销的一体化智能管理平台
        </p>
        <div class="hero-actions">
          <button class="btn-hero-primary" @click="handleHeroAction()">
            <span>{{ isLoggedIn ? '进入控制台' : '立即体验' }}</span>
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>
          <button class="btn-hero-secondary" @click="$router.push('/products')">
            浏览产品
          </button>
        </div>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-number">1000K+</span>
            <span class="stat-label">活跃用户</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-number">3000+</span>
            <span class="stat-label">合作企业</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-number">99.95%</span>
            <span class="stat-label">服务可用性</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 核心模块 -->
    <section class="modules-section">
      <div class="section-header">
        <span class="section-tag">核心功能</span>
        <h2 class="section-title">一站式农业数字化解决方案</h2>
        <p class="section-desc">覆盖农业生产到销售的全流程数字化管理</p>
      </div>

      <div class="modules-grid">
        <div
          v-for="(module, index) in modules"
          :key="module.name"
          class="module-card"
          :style="{ '--accent-color': module.color }"
          @click="goToModule(module.path)"
        >
          <div class="card-glow"></div>
          <div class="card-content">
            <div class="card-icon-wrapper">
              <el-icon :size="32" :color="module.color">
                <component :is="module.icon" />
              </el-icon>
            </div>
            <h3 class="card-title">{{ module.name }}</h3>
            <p class="card-desc">{{ module.description }}</p>
            <div class="card-footer">
              <span class="card-link">
                立即访问
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 平台特色 -->
    <section class="features-section">
      <div class="features-bg"></div>
      <div class="section-header">
        <span class="section-tag">为什么选择我们</span>
        <h2 class="section-title">领先的智能化能力</h2>
      </div>

      <div class="features-grid">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="feature-card"
        >
          <div class="feature-icon-wrapper" :style="{ background: feature.bgColor }">
            <el-icon :size="28" :color="feature.color">
              <component :is="feature.icon" />
            </el-icon>
          </div>
          <div class="feature-content">
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 数据展示 -->
    <section class="metrics-section">
      <div class="metrics-container">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="metric-item"
        >
          <span class="metric-value">{{ stat.value }}</span>
          <span class="metric-label">{{ stat.label }}</span>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="home-footer">
      <div class="footer-content">
        <div class="footer-brand">
          <img src="/logo-new.png" class="footer-icon" alt=" Logo" />
          <span class="footer-text"></span>
        </div>
        <p class="footer-slogan">智慧农业赋能农业现代化发展</p>
        <div class="footer-links">
          <a href="#">隐私政策</a>
          <span class="footer-divider">|</span>
          <a href="#">使用条款</a>
          <span class="footer-divider">|</span>
          <a href="#">联系我们</a>
        </div>
        <p class="footer-copyright">© 2024 🌾. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  DataAnalysis,
  Box,
  TrendCharts,
  Management,
  ShoppingCart,
  UserFilled,
  SetUp,
  Sell,
  ColdDrink,
  Wallet
} from '@element-plus/icons-vue'

const router = useRouter()
const isLoggedIn = ref(false)

onMounted(() => {
  isLoggedIn.value = !!localStorage.getItem('token')
})

const modules = [
  {
    name: '智慧农业',
    description: '设备管理、地块管理、作物监控',
    icon: DataAnalysis,
    color: '#10B981',
    path: '/smart-agriculture',
    auth: true
  },
  {
    name: '数字营销',
    description: '会员管理、营销活动管理',
    icon: TrendCharts,
    color: '#8B5CF6',
    path: '/digital-marketing',
    auth: true
  },
  {
    name: '冷链物流',
    description: '车辆调度、仓库管理',
    icon: ColdDrink,
    color: '#3B82F6',
    path: '/cold-chain',
    auth: true
  },
  {
    name: '供应链金融',
    description: '金融服务、信贷管理',
    icon: Wallet,
    color: '#F59E0B',
    path: '/supply-chain-finance',
    auth: true
  }
]

const features = [
  {
    icon: Box,
    title: '产品展示',
    description: '丰富的农产品信息，支持多种分类筛选',
    color: '#10B981',
    bgColor: 'rgba(16, 185, 129, 0.1)'
  },
  {
    icon: Management,
    title: '分类浏览',
    description: '清晰的产品分类，方便快速查找',
    color: '#8B5CF6',
    bgColor: 'rgba(139, 92, 246, 0.1)'
  },
  {
    icon: TrendCharts,
    title: '数据统计',
    description: '实时更新的销售和库存数据',
    color: '#F59E0B',
    bgColor: 'rgba(245, 158, 11, 0.1)'
  },
  {
    icon: ShoppingCart,
    title: '便捷下单',
    description: '简单快捷的订单流程',
    color: '#3B82F6',
    bgColor: 'rgba(59, 130, 246, 0.1)'
  },
  {
    icon: UserFilled,
    title: '会员系统',
    description: '完善的会员积分体系',
    color: '#EC4899',
    bgColor: 'rgba(236, 72, 153, 0.1)'
  },
  {
    icon: DataAnalysis,
    title: '智能推荐',
    description: '基于偏好的个性化推荐',
    color: '#EF4444',
    bgColor: 'rgba(239, 68, 68, 0.1)'
  }
]

const stats = [
  { value: '1,028', label: '注册用户' },
  { value: '3,256', label: '订单数量' },
  { value: '¥128.5万', label: '总销售额' },
  { value: '156', label: '在售商品' }
]

const goToModule = (path: string) => {
  router.push(path)
}

const handleHeroAction = () => {
  router.push('/products')
}
</script>

<style scoped>
/* ========== 变量定义 ========== */
:root {
  --primary: #165DFF;
  --primary-light: rgba(22, 93, 255, 0.08);
  --primary-dark: #0F4AE6;
  --accent-green: #10B981;
  --accent-amber: #F59E0B;
  --accent-blue: #3B82F6;
  --accent-red: #EF4444;
  --accent-purple: #8B5CF6;
  --accent-pink: #EC4899;

  --bg-primary: #FFFFFF;
  --bg-secondary: #F8FAFC;
  --bg-tertiary: #F1F5F9;

  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-tertiary: #94A3B8;

  --border-color: #E2E8F0;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home-container {
  min-height: 100vh;
  background: var(--bg-primary);
  font-family: 'Inter', 'PingFang SC', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--text-primary);
  line-height: 1.6;
}

/* ========== 导航栏 ========== */
.main-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 48px;
  height: 72px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  font-size: 0;  /* 隐藏 emoji */
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.brand-text {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent-blue) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  padding: 10px 18px;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.nav-link.active {
  color: var(--primary);
  background: var(--primary-light);
}

.nav-actions {
  display: flex;
  gap: 12px;
}

.btn-nav-outline,
.btn-nav-primary {
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-nav-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-nav-outline:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.btn-nav-primary {
  background: var(--primary);
  border: 1px solid var(--primary);
  color: white;
}

.btn-nav-primary:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
}

/* ========== Hero 区域 ========== */
.hero-section {
  position: relative;
  padding: 100px 48px 60px;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  overflow: hidden;
}

.hero-bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(22, 93, 255, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(16, 185, 129, 0.03) 0%, transparent 40%);
  pointer-events: none;
}

.hero-content {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--primary-light);
  border-radius: 100px;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 20px;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: var(--primary);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

.title-line {
  display: block;
  color: var(--text-primary);
}

.title-line.accent {
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent-blue) 50%, var(--accent-green) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 28px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 40px;
}

.btn-hero-primary,
.btn-hero-secondary {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-hero-primary {
  background: var(--primary);
  border: none;
  color: white;
  box-shadow: 0 4px 14px rgba(22, 93, 255, 0.35);
}

.btn-hero-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(22, 93, 255, 0.45);
}

.btn-hero-primary .btn-icon {
  width: 18px;
  height: 18px;
  transition: transform 0.2s ease;
}

.btn-hero-primary:hover .btn-icon {
  transform: translateX(4px);
}

.btn-hero-secondary {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-hero-secondary:hover {
  border-color: var(--text-tertiary);
  background: var(--bg-secondary);
}

.hero-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 14px;
  color: var(--text-tertiary);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--border-color);
}

/* ========== 核心模块 ========== */
.modules-section {
  padding: 100px 48px;
  max-width: 1400px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-tag {
  display: inline-block;
  padding: 6px 14px;
  background: var(--primary-light);
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 16px;
}

.section-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}

.section-desc {
  font-size: 16px;
  color: var(--text-secondary);
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.module-card {
  position: relative;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 32px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.module-card:hover {
  transform: translateY(-8px);
  border-color: var(--accent-color, var(--primary));
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--accent-color, var(--primary));
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.module-card:hover .card-glow {
  transform: scaleX(1);
}

.card-content {
  position: relative;
}

.card-icon-wrapper {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.module-card:hover .card-icon-wrapper {
  background: rgba(22, 93, 255, 0.08);
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.card-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 20px;
}

.card-footer {
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.card-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-color, var(--primary));
}

.card-link svg {
  width: 16px;
  height: 16px;
  transition: transform 0.2s ease;
}

.module-card:hover .card-link svg {
  transform: translateX(4px);
}

/* ========== 平台特色 ========== */
.features-section {
  position: relative;
  padding: 100px 48px;
  background: var(--bg-secondary);
  overflow: hidden;
}

.features-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 0% 0%, rgba(22, 93, 255, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 100% 100%, rgba(16, 185, 129, 0.03) 0%, transparent 50%);
  pointer-events: none;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.feature-card {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 28px;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.feature-icon-wrapper {
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
}

.feature-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.feature-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* ========== 数据展示 ========== */
.metrics-section {
  padding: 80px 48px;
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
}

.metrics-container {
  display: flex;
  justify-content: center;
  gap: 80px;
  max-width: 1000px;
  margin: 0 auto;
}

.metric-item {
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 42px;
  font-weight: 800;
  color: white;
  letter-spacing: -0.02em;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.6);
}

/* ========== Footer ========== */
.home-footer {
  padding: 60px 48px;
  background: var(--bg-primary);
  border-top: 1px solid var(--border-color);
}

.footer-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.footer-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.footer-icon {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.footer-text {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.footer-slogan {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}

.footer-links a {
  font-size: 14px;
  color: var(--text-tertiary);
  text-decoration: none;
  transition: color 0.2s ease;
}

.footer-links a:hover {
  color: var(--primary);
}

.footer-divider {
  color: var(--border-color);
}

.footer-copyright {
  font-size: 13px;
  color: var(--text-tertiary);
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .main-nav {
    padding: 0 24px;
  }

  .nav-links {
    display: none;
  }

  .hero-section {
    padding: 90px 24px 50px;
  }

  .hero-title {
    font-size: 40px;
  }

  .hero-description {
    font-size: 16px;
  }

  .modules-section,
  .features-section {
    padding: 60px 24px;
  }

  .modules-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .metrics-container {
    flex-wrap: wrap;
    gap: 40px;
  }
}

@media (max-width: 640px) {
  .hero-title {
    font-size: 32px;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .btn-hero-primary,
  .btn-hero-secondary {
    width: 100%;
    max-width: 280px;
    justify-content: center;
  }

  .hero-stats {
    flex-wrap: wrap;
    gap: 24px;
  }

  .stat-divider {
    display: none;
  }

  .modules-grid {
    grid-template-columns: 1fr;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .metrics-container {
    gap: 32px;
  }

  .metric-value {
    font-size: 32px;
  }

  .hide-mobile {
    display: none;
  }
}
</style>
