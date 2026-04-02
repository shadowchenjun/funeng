<template>
  <div class="cold-chain-container">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">❄️ 数字冷链</h1>
        <p class="page-subtitle">全程温控 · 实时追踪 · 安全保障</p>
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

    <!-- 实时监控 -->
    <div v-if="activeTab === 'monitor'">
      <el-row :gutter="10" class="monitor-cards">
        <el-col :span="12" v-for="item in monitorData" :key="item.title">
          <el-card class="monitor-card" :style="{ borderLeft: `4px solid ${item.color}` }">
            <div class="monitor-info">
              <h3>{{ item.value }}</h3>
              <p>{{ item.title }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card class="section-card">
        <template #header>
          <span>🌡️ 温度监控</span>
        </template>
        
        <div class="temp-list">
          <el-card v-for="item in temperatureData" :key="item.warehouse" class="temp-card">
            <div class="temp-header">
              <span class="warehouse-name">{{ item.warehouse }}</span>
              <el-tag :type="item.status === '正常' ? 'success' : 'danger'" size="small">
                {{ item.status }}
              </el-tag>
            </div>
            <div class="temp-info">
              <span>位置: {{ item.location }}</span>
              <span>温度: <b :style="{ color: getTempColor(item.currentTemp) }">{{ item.currentTemp }}°C</b></span>
              <span>湿度: {{ item.humidity }}</span>
            </div>
          </el-card>
        </div>
      </el-card>
    </div>
    
    <!-- 仓库管理 -->
    <el-card v-if="activeTab === 'warehouse'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🏭 仓库管理</span>
          <el-button type="primary" size="small" @click="showWarehouseDialog()">+ 添加仓库</el-button>
        </div>
      </template>
      
      <!-- 仓库统计 -->
      <el-row :gutter="10" class="warehouse-stats">
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ warehouses.length }}</span>
            <span class="label">仓库数</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ warehouses.filter(w => w.status === '正常').length }}</span>
            <span class="label">正常</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ totalCapacity }}m³</span>
            <span class="label">总容量</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 仓库列表 -->
      <div class="warehouse-list">
        <el-card v-for="wh in warehouses" :key="wh.id" class="warehouse-card">
          <div class="warehouse-header">
            <div class="warehouse-title">
              <el-icon :size="24"><OfficeBuilding /></el-icon>
              <span>{{ wh.name }}</span>
            </div>
            <el-tag :type="wh.status === '正常' ? 'success' : 'warning'" size="small">
              {{ wh.status }}
            </el-tag>
          </div>
          <div class="warehouse-info">
            <p>📍 {{ wh.address }}</p>
            <p>📐 容量: {{ wh.capacity }}m³ | 面积: {{ wh.area }}㎡</p>
            <p>🌡️ 温度: {{ wh.temperature }}°C | 湿度: {{ wh.humidity }}%</p>
            <p>📦 库存: {{ wh.inventory }}件</p>
          </div>
          <div class="warehouse-actions">
            <el-button type="primary" link size="small" @click="editWarehouse(wh)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteWarehouse(wh)">删除</el-button>
          </div>
        </el-card>
      </div>
      
      <el-divider>仓库分布</el-divider>
      <div class="warehouse-map">
        <div id="warehouseMap" style="width: 100%; height: 200px; border-radius: 8px;"></div>
      </div>
    </el-card>
    
    <!-- 车辆管理 -->
    <el-card v-if="activeTab === 'vehicle'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🚛 车辆管理</span>
          <el-button type="primary" size="small" @click="showVehicleDialog()">+ 添加车辆</el-button>
        </div>
      </template>
      
      <!-- 车辆统计 -->
      <el-row :gutter="10" class="vehicle-stats">
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ vehicles.length }}</span>
            <span class="label">车辆数</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ vehicles.filter(v => v.status === '运输中').length }}</span>
            <span class="label">运输中</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ vehicles.filter(v => v.status === '空闲').length }}</span>
            <span class="label">空闲</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 车辆列表 -->
      <div class="vehicle-list">
        <el-card v-for="v in vehicles" :key="v.id" class="vehicle-card">
          <div class="vehicle-header">
            <el-icon :size="28" color="#409eff"><Van /></el-icon>
            <div class="vehicle-info">
              <h4>{{ v.plate }}</h4>
              <p>司机: {{ v.driver }} | 电话: {{ v.phone }}</p>
            </div>
            <el-tag :type="v.status === '运输中' ? 'success' : v.status === '维修中' ? 'danger' : 'info'" size="small">
              {{ v.status }}
            </el-tag>
          </div>
          <div class="vehicle-detail">
            <span>📍 当前位置: {{ v.location }}</span>
            <span>🌡️ 车厢温度: {{ v.temperature }}°C</span>
            <span>🔋 电量: {{ v.battery }}%</span>
          </div>
          <div class="vehicle-actions">
            <el-button type="primary" link size="small" @click="trackVehicle(v)">追踪</el-button>
            <el-button type="warning" link size="small" @click="editVehicle(v)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteVehicle(v)">删除</el-button>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 运输追踪 -->
    <el-card v-if="activeTab === 'transport'" class="section-card">
      <template #header>
        <span>🗺️ 运输追踪</span>
      </template>

      <!-- 运输路线选择 -->
      <el-select v-model="selectedTransportId" placeholder="选择运输路线" style="width: 100%; margin-bottom: 15px;" @change="onTransportSelectChange">
        <el-option
          v-for="t in transports"
          :key="t.id"
          :label="`${t.vehicle_no} - ${t.route} (${t.status === 'in_transit' ? '运输中' : t.status === 'arrived' ? '已到达' : '等待'})`"
          :value="t.id"
        />
      </el-select>

      <!-- 运输路线地图 -->
      <div class="transport-map">
        <div id="transportMap" style="width: 100%; height: 250px; border-radius: 8px; margin-bottom: 15px;"></div>
      </div>

      <!-- 运输轨迹 -->
      <el-timeline>
        <el-timeline-item
          v-for="(item, index) in transportData"
          :key="index"
          :timestamp="item.timestamp"
          :type="(item.type as any)"
          :hollow="item.hollow"
        >
          <h4>{{ item.title }}</h4>
          <p>{{ item.location }}</p>
          <p class="timeline-info">
            <span>🌡️ {{ item.temperature }}</span>
            <span>💧 {{ item.humidity }}</span>
          </p>
        </el-timeline-item>
      </el-timeline>
    </el-card>
    
    <!-- 库存管理 -->
    <el-card v-if="activeTab === 'inventory'" class="section-card">
      <template #header>
        <span>📦 库存管理</span>
      </template>
      
      <!-- 库存统计 -->
      <el-row :gutter="10" class="inventory-stats">
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ totalInventory }}</span>
            <span class="label">总库存</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ inventoryData.length }}</span>
            <span class="label">SKU数</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ expiringCount }}</span>
            <span class="label">临期</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 库存列表 -->
      <div class="inventory-list">
        <el-card v-for="item in inventoryData" :key="item.product" class="inventory-card">
          <div class="inventory-header">
            <span class="product-name">{{ item.product }}</span>
            <el-tag size="small">{{ item.storage }}</el-tag>
          </div>
          <div class="inventory-info">
            <span>数量: {{ item.quantity }}</span>
            <span>保质期: {{ item.expiry }}</span>
            <el-tag v-if="isExpiring(item.expiry)" type="warning" size="small">临期</el-tag>
          </div>
        </el-card>
      </div>
      
      <el-divider />
      
      <!-- 质量追溯 -->
      <h4>🔍 质量追溯</h4>
      <el-form :model="traceForm" label-width="80px" size="small">
        <el-form-item label="追溯码">
          <el-input v-model="traceForm.code" placeholder="请输入追溯码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="traceProduct" size="small">查询</el-button>
        </el-form-item>
      </el-form>
      
      <div v-if="traceResult" class="trace-result">
        <h4>追溯信息</h4>
        <p><strong>产品:</strong> {{ traceResult.product }}</p>
        <p><strong>产地:</strong> {{ traceResult.origin }}</p>
        <p><strong>加工日期:</strong> {{ traceResult.processDate }}</p>
        <p><strong>存储温度:</strong> {{ traceResult.storageTemp }}</p>
        <p><strong>运输路线:</strong> {{ traceResult.transportRoute }}</p>
      </div>
    </el-card>
    
    <!-- 数据分析 -->
    <el-card v-if="activeTab === 'analytics'" class="section-card">
      <template #header>
        <span>📊 数据分析</span>
      </template>
      
      <!-- 库存周转 -->
      <el-row :gutter="10" class="analytics-section">
        <el-col :span="12">
          <h4>📦 库存周转</h4>
          <div class="chart-placeholder">
            <el-progress type="circle" :percentage="72" :width="100" />
            <p>周转率 72%</p>
          </div>
        </el-col>
        <el-col :span="12">
          <h4>🚛 运输效率</h4>
          <div class="chart-placeholder">
            <el-progress type="circle" :percentage="85" :width="100" color="#67C23A" />
            <p>准点率 85%</p>
          </div>
        </el-col>
      </el-row>
      
      <!-- 温度合规率 -->
      <el-divider />
      <h4>🌡️ 温度合规率</h4>
      <el-progress :percentage="98" :stroke-width="20" />
      <p class="analytics-note">本月温度异常时间: 2.3小时 / 720小时</p>
      
      <!-- 损耗统计 -->
      <el-divider />
      <h4>📉 损耗统计</h4>
      <el-row :gutter="10">
        <el-col :span="8">
          <div class="loss-item">
            <span class="num">0.5%</span>
            <span class="label">运输损耗</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="loss-item">
            <span class="num">0.2%</span>
            <span class="label">仓储损耗</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="loss-item">
            <span class="num">0.7%</span>
            <span class="label">总损耗</span>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 品控管理 -->
    <el-card v-if="activeTab === 'quality'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>✅ 品控管理</span>
          <el-button type="primary" size="small" @click="loadQualityData">🔄 刷新</el-button>
        </div>
      </template>
      
      <!-- 品控统计 -->
      <el-row :gutter="10" class="quality-stats">
        <el-col :span="6">
          <div class="stat-item">
            <span class="num">{{ qualityInspections.length }}</span>
            <span class="label">检查总数</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="num">{{ qualityInspections.filter(i => i.result === '合格').length }}</span>
            <span class="label">合格</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="num">{{ qualityInspections.filter(i => i.result === '待复检').length }}</span>
            <span class="label">待复检</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="num" style="color: #F56C6C;">{{ qualityInspections.filter(i => i.result === '不合格').length }}</span>
            <span class="label">不合格</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 品控标准 -->
      <el-divider>📋 品控标准</el-divider>
      <div class="quality-standards">
        <el-card v-for="std in qualityStandards" :key="std.id" class="standard-card">
          <div class="standard-header">
            <span class="standard-name">{{ std.name }}</span>
            <el-tag size="small">{{ std.category }}</el-tag>
          </div>
          <div class="standard-info">
            <span>🌡️ 温度: {{ std.temperature.min }}~{{ std.temperature.max }}{{ std.temperature.unit }}</span>
            <span>💧 湿度: {{ std.humidity.min }}~{{ std.humidity.max }}{{ std.humidity.unit }}</span>
            <span>📅 货架期: {{ std.shelf_days }}天</span>
          </div>
        </el-card>
      </div>
      
      <!-- 检查记录 -->
      <el-divider>📝 检查记录</el-divider>
      <el-table :data="qualityInspections" size="small" stripe>
        <el-table-column prop="id" label="编号" width="100" />
        <el-table-column prop="type" label="类型" width="80" />
        <el-table-column prop="product" label="产品" />
        <el-table-column prop="batch_no" label="批次" width="140" />
        <el-table-column prop="result" label="结果" width="70">
          <template #default="{ row }">
            <el-tag :type="row.result === '合格' ? 'success' : row.result === '不合格' ? 'danger' : 'warning'" size="small">
              {{ row.result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="评分" width="60" />
        <el-table-column prop="inspector" label="质检员" width="80" />
        <el-table-column prop="created_at" label="时间" width="130" />
      </el-table>
    </el-card>
    
    <!-- 库存预警 -->
    <el-card v-if="activeTab === 'alert'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🔔 库存预警</span>
          <el-button type="primary" size="small" @click="loadAlertData">🔄 刷新</el-button>
        </div>
      </template>
      
      <!-- 预警统计 -->
      <el-row :gutter="10" class="alert-stats">
        <el-col :span="8">
          <div class="stat-item">
            <span class="num" style="color: #F56C6C;">{{ inventoryStats.low_stock_count }}</span>
            <span class="label">库存不足</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num" style="color: #E6A23C;">{{ inventoryStats.overstock_count }}</span>
            <span class="label">库存过多</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num" style="color: #909399;">{{ inventoryStats.expiring_soon_count }}</span>
            <span class="label">临期预警</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 预警规则 -->
      <el-divider>⚙️ 预警规则</el-divider>
      <div class="alert-rules">
        <el-card v-for="rule in alertRules" :key="rule.id" class="rule-card">
          <div class="rule-header">
            <span class="rule-name">{{ rule.name }}</span>
            <el-switch v-model="rule.enabled" size="small" />
          </div>
          <div class="rule-info">
            <span>类型: {{ rule.type }}</span>
            <span>阈值: {{ rule.threshold }}{{ rule.unit }}</span>
            <span>通知: {{ rule.notify_channels.join(', ') }}</span>
          </div>
        </el-card>
      </div>
      
      <!-- 预警列表 -->
      <el-divider>📋 预警列表</el-divider>
      <div class="alert-list">
        <el-card v-for="alert in inventoryAlerts" :key="alert.id" class="alert-card" 
          :class="'alert-' + alert.level">
          <div class="alert-header">
            <el-tag :type="alert.level === 'critical' ? 'danger' : alert.level === 'high' ? 'warning' : 'info'" size="small">
              {{ alert.level === 'critical' ? '紧急' : alert.level === 'high' ? '高' : alert.level === 'medium' ? '中' : '低' }}
            </el-tag>
            <span class="alert-type">{{ alert.type }}</span>
            <el-tag :type="alert.status === '待处理' ? 'danger' : alert.status === '处理中' ? 'warning' : 'success'" size="small">
              {{ alert.status }}
            </el-tag>
          </div>
          <div class="alert-content">
            <p>📦 产品: {{ alert.product }}</p>
            <p>🏭 仓库: {{ alert.warehouse }}</p>
            <p>📊 {{ alert.message }}</p>
          </div>
          <div class="alert-footer">
            <span class="alert-time">{{ alert.created_at }}</span>
            <el-button v-if="alert.status === '待处理'" type="primary" size="small" link @click="resolveAlert(alert.id)">
              标记处理
            </el-button>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 添加/编辑仓库对话框 -->
    <el-dialog v-model="warehouseDialogVisible" :title="isEditWarehouse ? '编辑仓库' : '添加仓库'" width="95%">
      <el-form :model="warehouseForm" label-width="70px" size="small">
        <el-form-item label="仓库名称" required>
          <el-input v-model="warehouseForm.name" placeholder="如: 北京冷库" />
        </el-form-item>
        <el-form-item label="地址" required>
          <el-input v-model="warehouseForm.address" placeholder="仓库地址" />
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="容量(m³)" style="margin-bottom: 10px;">
              <el-input-number v-model="warehouseForm.capacity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="面积(㎡)" style="margin-bottom: 10px;">
              <el-input-number v-model="warehouseForm.area" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="温度(°C)" style="margin-bottom: 10px;">
              <el-input-number v-model="warehouseForm.temperature" :min="-30" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="湿度(%)" style="margin-bottom: 10px;">
              <el-input-number v-model="warehouseForm.humidity" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="warehouseForm.status" style="width: 100%">
            <el-option label="正常" value="正常" />
            <el-option label="维护中" value="维护中" />
            <el-option label="已满" value="已满" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="warehouseDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveWarehouse" size="small">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加/编辑车辆对话框 -->
    <el-dialog v-model="vehicleDialogVisible" :title="isEditVehicle ? '编辑车辆' : '添加车辆'" width="95%">
      <el-form :model="vehicleForm" label-width="80px" size="small">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="车牌号" required>
              <el-input v-model="vehicleForm.plate" placeholder="如: 京A12345" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车型">
              <el-select v-model="vehicleForm.vehicleType" style="width: 100%">
                <el-option label="冷藏车" value="冷藏车" />
                <el-option label="厢式货车" value="厢式货车" />
                <el-option label="保温车" value="保温车" />
                <el-option label="冷冻车" value="冷冻车" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="载重(吨)">
              <el-input-number v-model="vehicleForm.loadCapacity" :min="0.1" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车厢容积">
              <el-input v-model="vehicleForm.volume" placeholder="如: 50立方米" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">司机信息</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="司机" required>
              <el-input v-model="vehicleForm.driver" placeholder="司机姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话">
              <el-input v-model="vehicleForm.phone" placeholder="联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">设备信息</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="GPS设备">
              <el-input v-model="vehicleForm.gpsDevice" placeholder="GPS设备编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="温度范围">
              <el-input v-model="vehicleForm.tempRange" placeholder="如: -25°C~5°C" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="vehicleForm.status" style="width: 100%">
            <el-option label="空闲" value="空闲" />
            <el-option label="运输中" value="运输中" />
            <el-option label="维修中" value="维修中" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="vehicleDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveVehicle" size="small">保存</el-button>
      </template>
    </el-dialog>

    <!-- 货主管理 -->
    <el-card v-if="activeTab === 'owner'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🏢 货主管理</span>
          <div>
            <el-button type="primary" size="small" @click="showOwnerDialog()">+ 添加货主</el-button>
            <el-button type="primary" size="small" @click="loadOwnerData">🔄 刷新</el-button>
          </div>
        </div>
      </template>
      
      <el-row :gutter="10" class="owner-stats">
        <el-col :span="6">
          <div class="stat-item">
            <span class="num">{{ ownerStats.total }}</span>
            <span class="label">货主总数</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="num" style="color: #67C23A;">{{ ownerStats.active }}</span>
            <span class="label">正常运营</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="num" style="color: #409EFF;">{{ ownerStats.warehouses }}</span>
            <span class="label">仓库数量</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="num" style="color: #E6A23C;">{{ ownerStats.zones }}</span>
            <span class="label">温区数量</span>
          </div>
        </el-col>
      </el-row>
      
      <el-table :data="ownerList" stripe style="width: 100%; margin-top: 15px;">
        <el-table-column prop="code" label="货主编码" width="100" />
        <el-table-column prop="name" label="货主名称" width="150" />
        <el-table-column prop="contact" label="联系人" width="100" />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="address" label="地址" width="180" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === '正常' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="editOwner(row)">编辑</el-button>
            <el-button type="danger" size="small" link @click="deleteOwner(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑货主对话框 -->
    <el-dialog v-model="ownerDialogVisible" :title="isEditOwner ? '编辑货主' : '添加货主'" width="500px">
      <el-form :model="ownerForm" label-width="80px">
        <el-form-item label="货主名称" required>
          <el-input v-model="ownerForm.name" placeholder="请输入货主名称" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="ownerForm.contact" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="ownerForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="ownerForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="ownerForm.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="ownerForm.status" style="width: 100%">
            <el-option label="正常" value="正常" />
            <el-option label="暂停" value="暂停" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ownerDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveOwner">保存</el-button>
      </template>
    </el-dialog>

    <!-- 预约详情对话框 -->
    <el-dialog v-model="appointmentDetailVisible" title="预约详情" width="600px">
      <el-descriptions :column="2" border v-if="currentAppointment">
        <el-descriptions-item label="预约号">{{ currentAppointment.id }}</el-descriptions-item>
        <el-descriptions-item label="货主">{{ currentAppointment.owner }}</el-descriptions-item>
        <el-descriptions-item label="车牌号">{{ currentAppointment.vehicle_no }}</el-descriptions-item>
        <el-descriptions-item label="司机">{{ currentAppointment.driver }}</el-descriptions-item>
        <el-descriptions-item label="司机电话">{{ currentAppointment.driver_phone || '138****1234' }}</el-descriptions-item>
        <el-descriptions-item label="预计到达">{{ currentAppointment.estimated_arrival }}</el-descriptions-item>
        <el-descriptions-item label="预计数量">{{ currentAppointment.expected_quantity }}件</el-descriptions-item>
        <el-descriptions-item label="月台">{{ currentAppointment.dock }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentAppointment.status === '已完成' ? 'success' : currentAppointment.status === '收货中' ? 'warning' : 'info'">{{ currentAppointment.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="货物类型">{{ currentAppointment.cargo_type || '普通货物' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="appointmentDetailVisible = false">关闭</el-button>
        <el-button type="success" @click="signInAppointment(currentAppointment)" v-if="currentAppointment.status === '待签到'">签到</el-button>
        <el-button type="warning" @click="startReceive(currentAppointment)" v-if="currentAppointment.status === '已签到'">开始收货</el-button>
      </template>
    </el-dialog>

    <!-- 入库单详情对话框 -->
    <el-dialog v-model="inboundDetailVisible" title="入库单详情" width="700px">
      <el-descriptions :column="2" border v-if="currentInboundOrder">
        <el-descriptions-item label="入库单号">{{ currentInboundOrder.id }}</el-descriptions-item>
        <el-descriptions-item label="货主">{{ currentInboundOrder.owner }}</el-descriptions-item>
        <el-descriptions-item label="入库日期">{{ currentInboundOrder.inbound_date }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentInboundOrder.status === '已入库' ? 'success' : currentInboundOrder.status === '收货中' ? 'warning' : 'info'">{{ currentInboundOrder.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="SKU数">{{ currentInboundOrder.total_items }}</el-descriptions-item>
        <el-descriptions-item label="总数量">{{ currentInboundOrder.total_quantity }}</el-descriptions-item>
        <el-descriptions-item label="已收货">{{ currentInboundOrder.received_quantity }}</el-descriptions-item>
        <el-descriptions-item label="合格数">{{ currentInboundOrder.qualified_quantity }}</el-descriptions-item>
      </el-descriptions>
      <el-divider>货物明细</el-divider>
      <el-table :data="currentInboundOrder.items || []" stripe size="small">
        <el-table-column prop="sku" label="SKU" width="120" />
        <el-table-column prop="name" label="商品名称" width="150" />
        <el-table-column prop="expected_qty" label="预期数量" width="90" />
        <el-table-column prop="received_qty" label="已收数量" width="90" />
        <el-table-column prop="qualified_qty" label="合格数" width="90" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === '已完成' ? 'success' : row.status === '部分收货' ? 'warning' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="inboundDetailVisible = false">关闭</el-button>
        <el-button type="primary" @click="receiveGoods(currentInboundOrder)" v-if="currentInboundOrder.status === '待收货' || currentInboundOrder.status === '收货中'">收货</el-button>
      </template>
    </el-dialog>

    <!-- 收货对话框 -->
    <el-dialog v-model="receiveDialogVisible" title="收货入库" width="500px">
      <el-form :model="receiveForm" label-width="100px">
        <el-form-item label="入库单号">
          <el-input v-model="receiveForm.orderId" disabled />
        </el-form-item>
        <el-form-item label="SKU">
          <el-select v-model="receiveForm.sku" placeholder="请选择SKU" style="width: 100%">
            <el-option v-for="item in receiveForm.items" :key="item.sku" :label="`${item.sku} - ${item.name}`" :value="item.sku" />
          </el-select>
        </el-form-item>
        <el-form-item label="收货数量">
          <el-input-number v-model="receiveForm.quantity" :min="1" :max="receiveForm.maxQty" style="width: 100%" />
        </el-form-item>
        <el-form-item label="合格数量">
          <el-input-number v-model="receiveForm.qualifiedQty" :min="0" :max="receiveForm.quantity" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="receiveForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="receiveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReceive">确认收货</el-button>
      </template>
    </el-dialog>

    <!-- 入库管理 -->
    <el-card v-if="activeTab === 'inbound'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>📥 入库管理</span>
          <el-radio-group v-model="inboundSubTab" size="small">
            <el-radio-button label="appointments">预约管理</el-radio-button>
            <el-radio-button label="orders">入库单</el-radio-button>
            <el-radio-button label="suggestions">上架建议</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <div v-if="inboundSubTab === 'appointments'">
        <el-table :data="appointmentList" stripe>
          <el-table-column prop="id" label="预约号" width="140" />
          <el-table-column prop="owner" label="货主" width="100" />
          <el-table-column prop="vehicle_no" label="车牌号" width="100" />
          <el-table-column prop="driver" label="司机" width="80" />
          <el-table-column prop="estimated_arrival" label="预计到达" width="150" />
          <el-table-column prop="expected_quantity" label="预计数量" width="90" />
          <el-table-column prop="dock" label="月台" width="60" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === '已完成' ? 'success' : row.status === '收货中' ? 'warning' : 'info'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="showAppointmentDetail(row)">详情</el-button>
              <el-button type="success" size="small" link @click="signInAppointment(row)" v-if="row.status === '待签到'">签到</el-button>
              <el-button type="warning" size="small" link @click="startReceive(row)" v-if="row.status === '已签到'">开始收货</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-if="inboundSubTab === 'orders'">
        <el-table :data="inboundOrders" stripe>
          <el-table-column prop="id" label="入库单号" width="150" />
          <el-table-column prop="owner" label="货主" width="100" />
          <el-table-column prop="inbound_date" label="入库日期" width="120" />
          <el-table-column prop="total_items" label="SKU数" width="70" />
          <el-table-column prop="total_quantity" label="总数量" width="90" />
          <el-table-column prop="received_quantity" label="已收货" width="90" />
          <el-table-column prop="qualified_quantity" label="合格数" width="90" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === '已入库' ? 'success' : row.status === '收货中' ? 'warning' : row.status === '已完成' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="showInboundDetail(row)">详情</el-button>
              <el-button type="success" size="small" link @click="receiveGoods(row)" v-if="row.status === '待收货' || row.status === '收货中'">收货</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-if="inboundSubTab === 'suggestions'">
        <el-alert title="智能上架建议基于商品温度要求、库存均衡、拣货路径优化等因素" type="info" :closable="false" style="margin-bottom: 15px;" />
        <el-table :data="putawaySuggestions" stripe>
          <el-table-column prop="sku" label="SKU" width="100" />
          <el-table-column prop="name" label="商品名称" width="150" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="suggested_location" label="推荐货位" width="120" />
          <el-table-column prop="zone" label="温区" width="100" />
          <el-table-column prop="reason" label="推荐原因" width="180">
            <template #default="{ row }">
              <el-tag size="small" :type="row.reason === '温度匹配' ? 'success' : row.reason === '库存均衡' ? 'warning' : 'info'">{{ row.reason }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="confidence" label="置信度" width="120">
            <template #default="{ row }">
              <span>{{ (row.confidence * 100).toFixed(2) }}%</span>
              <el-progress :percentage="row.confidence * 100" :color="row.confidence > 0.9 ? '#67C23A' : row.confidence > 0.8 ? '#E6A23C' : '#F56C6C'" :show-text="false" style="margin-top: 4px;" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="confirmPutaway(row)">确认上架</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 作业管理 -->
    <el-card v-if="activeTab === 'operation'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>⚙️ 作业管理</span>
          <el-radio-group v-model="operationSubTab" size="small">
            <el-radio-button label="tasks">任务列表</el-radio-button>
            <el-radio-button label="performance">人员绩效</el-radio-button>
            <el-radio-button label="batch">智能批次</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <div v-if="operationSubTab === 'tasks'">
        <el-table :data="operationTasks" stripe>
          <el-table-column prop="id" label="任务编号" width="130" />
          <el-table-column prop="type" label="作业类型" width="80" />
          <el-table-column prop="priority" label="优先级" width="70">
            <template #default="{ row }">
              <el-tag :type="row.priority === '紧急' ? 'danger' : row.priority === '高' ? 'warning' : 'info'" size="small">{{ row.priority }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="owner" label="货主" width="80" />
          <el-table-column prop="location" label="库位" width="100" />
          <el-table-column prop="quantity" label="数量" width="70" />
          <el-table-column prop="assigned_to" label="执行人" width="80" />
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === '已完成' ? 'success' : row.status === '执行中' ? 'warning' : 'info'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="barcode" label="条码" width="120" />
        </el-table>
      </div>
      
      <div v-if="operationSubTab === 'performance'">
        <el-table :data="performanceData" stripe>
          <el-table-column prop="employee_id" label="工号" width="100" />
          <el-table-column prop="name" label="姓名" width="80" />
          <el-table-column prop="department" label="部门" width="100" />
          <el-table-column prop="tasks_completed" label="完成任务" width="90" />
          <el-table-column prop="error_count" label="错误数" width="70" />
          <el-table-column prop="accuracy_rate" label="准确率" width="80">
            <template #default="{ row }">
              {{ (row.accuracy_rate * 100).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="avg_task_time" label="平均耗时(分钟)" width="120" />
          <el-table-column prop="score" label="绩效评分" width="80">
            <template #default="{ row }">
              <el-progress :percentage="row.score" :color="row.score >= 80 ? '#67C23A' : row.score >= 60 ? '#E6A23C' : '#F56C6C'" />
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-if="operationSubTab === 'batch'">
        <el-row :gutter="10" class="batch-stats">
          <el-col :span="8">
            <div class="stat-item">
              <span class="num">{{ batchStats.pending_orders }}</span>
              <span class="label">待处理订单</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <span class="num" style="color: #409EFF;">{{ batchStats.suggested_batches }}</span>
              <span class="label">建议批次</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <span class="num" style="color: #67C23A;">{{ batchStats.estimated_time_saved }}</span>
              <span class="label">预计节省时间</span>
            </div>
          </el-col>
        </el-row>
        <el-table :data="batchSuggestions" stripe style="margin-top: 15px;">
          <el-table-column prop="id" label="批次号" width="120" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="description" label="描述" width="250" />
          <el-table-column prop="orders" label="包含订单" width="180">
            <template #default="{ row }">
              {{ row.orders.join(', ') }}
            </template>
          </el-table-column>
          <el-table-column prop="total_items" label="商品数" width="70" />
          <el-table-column prop="estimated_pick_time" label="预计拣货时间" width="120" />
          <el-table-column prop="priority" label="优先级" width="70">
            <template #default="{ row }">
              <el-tag :type="row.priority === '高' ? 'danger' : 'info'" size="small">{{ row.priority }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default>
              <el-button type="primary" size="small">创建批次</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataAnalysis, OfficeBuilding, Van, Box, Location, TrendCharts, CircleCheck, Warning, User, Bottom, Operation } from '@element-plus/icons-vue'

declare global {
  interface Window {
    AMap: any
  }
}

const activeTab = ref('monitor')
const setActiveTab = (tab: string) => { activeTab.value = tab }

const navItems = [
  { key: 'monitor', label: '实时监控', icon: DataAnalysis, color: '#3B82F6' },
  { key: 'warehouse', label: '仓库管理', icon: OfficeBuilding, color: '#10B981' },
  { key: 'vehicle', label: '车辆管理', icon: Van, color: '#F59E0B' },
  { key: 'transport', label: '运输追踪', icon: Location, color: '#8B5CF6' },
  { key: 'inventory', label: '库存管理', icon: Box, color: '#EC4899' },
  { key: 'analytics', label: '数据分析', icon: TrendCharts, color: '#06B6D4' },
  { key: 'quality', label: '品控管理', icon: CircleCheck, color: '#10B981' },
  { key: 'alert', label: '库存预警', icon: Warning, color: '#EF4444' },
  { key: 'owner', label: '货主管理', icon: User, color: '#F97316' },
  { key: 'inbound', label: '入库管理', icon: Bottom, color: '#6366F1' },
  { key: 'operation', label: '作业管理', icon: Operation, color: '#14B8A6' }
]

// 页面加载时获取数据
onMounted(() => {
  window.scrollTo(0, 0)
  loadMonitorData()
  loadWarehouses()
  loadVehicles()
  loadTransportData()
  loadOwnerData()
})

// 高德地图实例
let warehouseMap: any = null
let transportMap: any = null

// 等待 AMap 加载完成
const waitForAMap = (): Promise<void> => {
  return new Promise((resolve) => {
    if (window.AMap) {
      resolve()
    } else {
      const check = setInterval(() => {
        if (window.AMap) {
          clearInterval(check)
          resolve()
        }
      }, 100)
      setTimeout(() => {
        clearInterval(check)
        resolve()
      }, 5000)
    }
  })
}

// 初始化仓库地图
const initWarehouseMap = () => {
  nextTick(async () => {
    await waitForAMap()
    if (!window.AMap) return

    const container = document.getElementById('warehouseMap')
    if (!container) return

    if (warehouseMap) {
      warehouseMap.destroy()
      warehouseMap = null
    }

    warehouseMap = new window.AMap.Map('warehouseMap', {
      zoom: 10,
      center: [117.12, 36.65],
      viewMode: '2D'
    })

    // 添加仓库标记
    if (warehouses.value.length > 0) {
      warehouses.value.forEach((w: any) => {
        if (w.lat && w.lng) {
          const marker = new window.AMap.Marker({
            position: [w.lng, w.lat],
            title: w.name
          })
          warehouseMap.add(marker)
        }
      })
    }
  })
}

// 初始化运输追踪地图
const initTransportMap = () => {
  nextTick(async () => {
    await waitForAMap()
    if (!window.AMap) return

    const container = document.getElementById('transportMap')
    if (!container) return

    if (transportMap) {
      transportMap.destroy()
      transportMap = null
    }

    transportMap = new window.AMap.Map('transportMap', {
      zoom: 5,
      center: [117.12, 36.65],
      viewMode: '2D'
    })

    // 地理编码器
    const geocoder = new window.AMap.Geocoder({ radius: 1000 })

    // 城市坐标缓存，避免重复请求
    const coordCache: Record<string, [number, number]> = {}

    // 获取坐标（优先用缓存）
    const getCoord = (city: string): Promise<[number, number] | null> => {
      return new Promise((resolve) => {
        if (coordCache[city]) {
          resolve(coordCache[city])
          return
        }
        geocoder.getLocation(city, (status: string, result: any) => {
          if (status === 'complete' && result.geocodes.length > 0) {
            const location = result.geocodes[0].location
            const coord: [number, number] = [location.lng, location.lat]
            coordCache[city] = coord
            resolve(coord)
          } else {
            resolve(null)
          }
        })
      })
    }

    // 绘制轨迹
    if (transports.value.length > 0) {
      // 取第一条运输记录画轨迹（演示用）
      // 根据选中的运输ID获取运输数据
      const selectedId = selectedTransportId.value || (transports.value.length > 0 ? transports.value[0].id : '')
      const t = transports.value.find(tr => tr.id === selectedId) || transports.value[0]
      const route = t.route || '北京-上海'
      const cities = route.split('-')

      // 预处理：出发地 -> 目的地
      const startCity = cities[0] || '北京'
      const endCity = cities[1] || '上海'

      // 添加起点和终点标记
      const startCoord = await getCoord(startCity)
      if (startCoord) {
        const startMarker = new window.AMap.Marker({
          position: startCoord,
          title: `起点: ${startCity}`,
          icon: new window.AMap.Icon({ size: [16, 16], image: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-start.png' })
        })
        transportMap.add(startMarker)
      }

      const endCoord = await getCoord(endCity)
      if (endCoord) {
        const endMarker = new window.AMap.Marker({
          position: endCoord,
          title: `终点: ${endCity}`,
          icon: new window.AMap.Icon({ size: [16, 16], image: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-end.png' })
        })
        transportMap.add(endMarker)
      }

      // 画轨迹线（使用数据库中的route_coords）
      // route_coords格式: [[lng, lat], [lng, lat], ...]
      let path: [number, number][] = []

      // 优先使用route_coords
      if (t.route_coords) {
        try {
          const coords = typeof t.route_coords === 'string' ? JSON.parse(t.route_coords) : t.route_coords
          if (Array.isArray(coords) && coords.length > 0) {
            path = coords.map((c: any) => [Number(c[0]), Number(c[1])] as [number, number])
          }
        } catch (e) {
          console.error('解析route_coords失败', e)
        }
      }

      // 如果没有route_coords，使用waypoints
      if (path.length === 0 && t.waypoints) {
        try {
          const waypoints = typeof t.waypoints === 'string' ? JSON.parse(t.waypoints) : t.waypoints
          if (Array.isArray(waypoints) && waypoints.length > 0) {
            path = waypoints.map((w: any) => [Number(w.lng), Number(w.lat)] as [number, number])
          }
        } catch (e) {
          console.error('解析waypoints失败', e)
        }
      }

      // 如果都没有，使用地理编码获取起点终点
      if (path.length === 0 && startCoord && endCoord) {
        path = [startCoord, endCoord]
      }

      if (path.length > 0) {
        // 绘制折线
        const polyline = new window.AMap.Polyline({
          path: path,
          strokeColor: '#3B82F6',
          strokeWeight: 4,
          strokeOpacity: 0.8
        })
        transportMap.add(polyline)

        // 调整视野
        transportMap.setFitView()
      }

      // 添加当前车辆位置标记
      if (t.current_lat && t.current_lng) {
        const currentMarker = new window.AMap.Marker({
          position: [t.current_lng, t.current_lat],
          title: `当前位置: ${t.vehicle_no || t.id}`
        })
        transportMap.add(currentMarker)
      }

      // 更新运输轨迹时间线数据（使用真实waypoints）
      if (t.waypoints) {
        try {
          const waypoints = typeof t.waypoints === 'string' ? JSON.parse(t.waypoints) : t.waypoints
          if (Array.isArray(waypoints) && waypoints.length > 0) {
            // 计算出发时间（假设每段需要6小时）
            const baseTime = t.departure_time ? new Date(t.departure_time) : new Date()
            transportData.value = waypoints.map((w: any, idx: number) => {
              const isLast = idx === waypoints.length - 1
              const isFirst = idx === 0
              let type = 'primary'
              let hollow = false
              if (isFirst) { type = 'success'; hollow = false }
              if (isLast) { type = 'warning' }
              const time = new Date(baseTime.getTime() + idx * 6 * 60 * 60 * 1000)
              return {
                timestamp: time.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }),
                title: isFirst ? '出发' : (isLast ? '到达' : `途经${w.name}`),
                location: w.name,
                temperature: `${t.temperature || -18}°C`,
                humidity: `${t.humidity || 45}%`,
                type,
                hollow
              }
            })
          }
        } catch (e) {
          console.error('解析waypoints失败', e)
        }
      }
    }
  })
}

// 加载监控数据
const loadMonitorData = async () => {
  try {
    const res = await axios.get('/api/cold-chain/monitoring/temperature')
    temperatureData.value = res.data
  } catch (e) { console.error('加载监控数据失败', e) }
}

// 加载运输数据
const loadTransportData = async () => {
  try {
    const res = await axios.get('/api/cold-chain/transport')
    transports.value = res.data
    // 默认选中第一条
    if (res.data.length > 0 && !selectedTransportId.value) {
      selectedTransportId.value = res.data[0].id
    }
  } catch (e) { console.error('加载运输数据失败', e) }
}

// 选择运输路线变化时更新地图
const onTransportSelectChange = () => {
  initTransportMap()
}

// 监听标签页切换，加载对应数据
watch(activeTab, (newTab) => {
  if (newTab === 'quality' && qualityInspections.value.length === 0) {
    loadQualityData()
  }
  if (newTab === 'alert' && inventoryAlerts.value.length === 0) {
    loadAlertData()
  }
  if (newTab === 'owner' && ownerList.value.length === 0) {
    loadOwnerData()
  }
  if (newTab === 'inbound' && appointmentList.value.length === 0) {
    loadInboundData()
  }
  if (newTab === 'operation' && operationTasks.value.length === 0) {
    loadOperationData()
  }
  if (newTab === 'warehouse') {
    setTimeout(initWarehouseMap, 300)
  }
  if (newTab === 'transport') {
    setTimeout(initTransportMap, 300)
  }
})

// 监控数据
const monitorData = ref([
  { title: '在线车辆', value: '12', color: '#67C23A' },
  { title: '在线仓库', value: '5', color: '#409EFF' },
  { title: '温度异常', value: '0', color: '#F56C6C' },
  { title: '今日运输', value: '28', color: '#E6A23C' }
])

const temperatureData = ref([
  { warehouse: 'A冷库', location: '北京仓', currentTemp: -18, targetTemp: -18, humidity: '45%', status: '正常' },
  { warehouse: 'B冷库', location: '上海仓', currentTemp: -20, targetTemp: -18, humidity: '42%', status: '正常' },
  { warehouse: '京A12345', location: '运输中-京沪高速', currentTemp: -16, targetTemp: -18, humidity: '50%', status: '正常' },
  { warehouse: '京B67890', location: '运输中-京港澳', currentTemp: -17, targetTemp: -18, humidity: '48%', status: '正常' }
])

// 仓库数据
const warehouses = ref<any[]>([])

// 加载仓库数据
const loadWarehouses = async () => {
  try {
    const res = await axios.get('/api/cold-chain/warehouses/list')
    warehouses.value = res.data.map((w: any) => ({
      id: w.id,
      name: w.name,
      address: w.address,
      capacity: w.capacity,
      area: w.area,
      temperature: w.temperature,
      humidity: w.humidity,
      inventory: w.inventory,
      status: w.status
    }))
  } catch (e) {
    console.error('加载仓库数据失败', e)
  }
}

const totalCapacity = computed(() => warehouses.value.reduce((sum, w) => sum + w.capacity, 0))

// 品控数据
const qualityInspections = ref<any[]>([])
const qualityStandards = ref<any[]>([])

// 库存预警数据
const inventoryAlerts = ref<any[]>([])
const inventoryStats = ref({
  total_products: 0,
  total_stock: 0,
  low_stock_count: 0,
  overstock_count: 0,
  expiring_soon_count: 0,
  temp_alert_count: 0,
  today_resolved: 0,
  this_week: { total_alerts: 0, resolved: 0, pending: 0 }
})
const alertRules = ref<any[]>([])

// 加载品控数据
const loadQualityData = async () => {
  try {
    const [inspRes, stdRes] = await Promise.all([
      axios.get('/api/cold-chain/quality/inspections'),
      axios.get('/api/cold-chain/quality/standards')
    ])
    qualityInspections.value = inspRes.data
    qualityStandards.value = stdRes.data.standards
  } catch (e) {
    console.error('加载品控数据失败', e)
  }
}

// 加载库存预警数据
const loadAlertData = async () => {
  try {
    const [alertsRes, rulesRes, statsRes] = await Promise.all([
      axios.get('/api/cold-chain/inventory/alerts'),
      axios.get('/api/cold-chain/inventory/rules'),
      axios.get('/api/cold-chain/inventory/stats')
    ])
    inventoryAlerts.value = alertsRes.data
    alertRules.value = rulesRes.data.rules
    inventoryStats.value = statsRes.data
  } catch (e) {
    console.error('加载库存预警数据失败', e)
  }
}

// 标记预警已处理
const resolveAlert = async (alertId: string) => {
  try {
    await axios.post(`/api/cold-chain/inventory/alerts/${alertId}/resolve`)
    ElMessage.success('已标记为已处理')
    loadAlertData()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// 货主管理数据
const ownerList = ref<any[]>([])
const ownerStats = ref({ total: 0, active: 0, warehouses: 0, zones: 0 })
const ownerDialogVisible = ref(false)
const isEditOwner = ref(false)
const editingOwnerId = ref<number>()
const ownerForm = reactive({
  name: '',
  contact: '',
  phone: '',
  email: '',
  address: '',
  status: '正常'
})

const loadOwnerData = async () => {
  try {
    const res = await axios.get('/api/cold-chain/owner/list')
    ownerList.value = res.data
    ownerStats.value = {
      total: res.data.length,
      active: res.data.filter((o: any) => o.status === '正常').length,
      warehouses: res.data.reduce((sum: number, o: any) => sum + (o.warehouse_count || 0), 0),
      zones: res.data.reduce((sum: number, o: any) => sum + (o.zone_count || 0), 0)
    }
  } catch (e) {
    console.error('加载货主数据失败', e)
  }
}

const showOwnerDialog = () => {
  isEditOwner.value = false
  Object.assign(ownerForm, { name: '', contact: '', phone: '', email: '', address: '', status: '正常' })
  ownerDialogVisible.value = true
}

const editOwner = (row: any) => {
  isEditOwner.value = true
  editingOwnerId.value = row.id
  Object.assign(ownerForm, {
    name: row.name,
    contact: row.contact || '',
    phone: row.phone || '',
    email: row.email || '',
    address: row.address || '',
    status: row.status
  })
  ownerDialogVisible.value = true
}

const saveOwner = async () => {
  if (!ownerForm.name) {
    ElMessage.warning('请输入货主名称')
    return
  }
  try {
    if (isEditOwner.value && editingOwnerId.value) {
      await axios.put(`/api/cold-chain/owner/${editingOwnerId.value}`, ownerForm)
      ElMessage.success('货主更新成功')
    } else {
      await axios.post('/api/cold-chain/owner', ownerForm)
      ElMessage.success('货主添加成功')
    }
    ownerDialogVisible.value = false
    loadOwnerData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '操作失败')
  }
}

const deleteOwner = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除货主 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await axios.delete(`/api/cold-chain/owner/${row.id}`)
    ElMessage.success('删除成功')
    loadOwnerData()
  } catch (e) {
    // 用户取消或删除失败
  }
}

// 预约详情
const appointmentDetailVisible = ref(false)
const currentAppointment = ref<any>(null)
const showAppointmentDetail = (row: any) => {
  currentAppointment.value = row
  appointmentDetailVisible.value = true
}

// 签到
const signInAppointment = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确认车辆 ${row.vehicle_no} 签到吗？`, '签到确认', { type: 'info' })
    row.status = '已签到'
    ElMessage.success('签到成功')
    appointmentDetailVisible.value = false
  } catch (e) {
    // 用户取消
  }
}

// 开始收货
const startReceive = async (row: any) => {
  row.status = '收货中'
  ElMessage.success('已开始收货')
  appointmentDetailVisible.value = false
}

// 入库单详情
const inboundDetailVisible = ref(false)
const currentInboundOrder = ref<any>(null)
const showInboundDetail = (row: any) => {
  // 模拟货物明细
  row.items = Array.from({ length: row.total_items || 3 }, (_, i) => ({
    sku: `SKU${String(i + 1).padStart(3, '0')}`,
    name: `商品${i + 1}`,
    expected_qty: Math.floor(row.total_quantity / (row.total_items || 3)),
    received_qty: Math.floor(Math.random() * 50),
    qualified_qty: 0,
    status: '待收货'
  }))
  currentInboundOrder.value = row
  inboundDetailVisible.value = true
}

// 收货
const receiveDialogVisible = ref(false)
const receiveForm = ref({
  orderId: '',
  sku: '',
  quantity: 0,
  qualifiedQty: 0,
  remark: '',
  items: [] as any[],
  maxQty: 0
})

const receiveGoods = (row: any) => {
  // 确保有商品列表，如果没有则动态生成
  let items = row.items
  if (!items || items.length === 0) {
    items = Array.from({ length: row.total_items || 3 }, (_, i) => ({
      sku: `SKU${String(i + 1).padStart(3, '0')}`,
      name: `商品${i + 1}`,
      expected_qty: Math.floor(row.total_quantity / (row.total_items || 3)),
      received_qty: Math.floor(Math.random() * 50),
      qualified_qty: 0,
      status: '待收货'
    }))
  }
  receiveForm.value = {
    orderId: row.id,
    sku: '',
    quantity: 1,
    qualifiedQty: 1,
    remark: '',
    items: items,
    maxQty: row.total_quantity - row.received_quantity
  }
  receiveDialogVisible.value = true
}

const submitReceive = async () => {
  if (!receiveForm.value.sku) {
    ElMessage.warning('请选择SKU')
    return
  }
  if (receiveForm.value.quantity <= 0) {
    ElMessage.warning('请输入收货数量')
    return
  }
  
  // 更新订单状态
  const order = currentInboundOrder.value
  if (order) {
    order.received_quantity = (order.received_quantity || 0) + receiveForm.value.quantity
    order.qualified_quantity = (order.qualified_quantity || 0) + receiveForm.value.qualifiedQty
    
    // 更新货物明细
    const item = order.items?.find((i: any) => i.sku === receiveForm.value.sku)
    if (item) {
      item.received_qty = (item.received_qty || 0) + receiveForm.value.quantity
      item.qualified_qty = (item.qualified_qty || 0) + receiveForm.value.qualifiedQty
      item.status = item.received_qty >= item.expected_qty ? '已完成' : '部分收货'
    }
    
    // 判断订单是否完成
    if (order.received_quantity >= order.total_quantity) {
      order.status = '已完成'
    } else {
      order.status = '收货中'
    }
  }
  
  ElMessage.success('收货成功')
  receiveDialogVisible.value = false
  inboundDetailVisible.value = false
}

// 确认上架
const confirmPutaway = (row: any) => {
  ElMessage.success(`已确认上架到 ${row.suggested_location}`)
  putawaySuggestions.value = putawaySuggestions.value.filter(item => item.sku !== row.sku)
}

// 入库管理数据
const inboundSubTab = ref('appointments')
const appointmentList = ref<any[]>([])
const inboundOrders = ref<any[]>([])
const putawaySuggestions = ref<any[]>([])
const loadInboundData = async () => {
  try {
    const [apptRes, ordersRes] = await Promise.all([
      axios.get('/api/cold-chain/inbound/appointments'),
      axios.get('/api/cold-chain/inbound/orders')
    ])
    appointmentList.value = apptRes.data
    inboundOrders.value = ordersRes.data
    
    // 模拟上架建议数据 - 带智能推荐逻辑
    const tempZones = [
      { name: '冷藏区A', temp: '0-5°C', suitable: ['蔬菜', '水果', '乳制品'] },
      { name: '冷藏区B', temp: '0-5°C', suitable: ['蔬菜', '水果'] },
      { name: '冷冻区A', temp: '-18°C', suitable: ['肉类', '冷冻食品', '海鲜'] },
      { name: '常温区A', temp: '15-25°C', suitable: ['干果', '罐头', '饮料'] }
    ]
    
    const products = [
      { name: '新鲜草莓', temp: '冷藏', zone: 0 },
      { name: '进口车厘子', temp: '冷藏', zone: 1 },
      { name: '冷冻鸡胸肉', temp: '冷冻', zone: 2 },
      { name: '冷冻海鲜', temp: '冷冻', zone: 2 },
      { name: '纯牛奶', temp: '冷藏', zone: 0 },
      { name: '新鲜蔬菜', temp: '冷藏', zone: 1 },
      { name: '矿泉水', temp: '常温', zone: 3 },
      { name: '薯片零食', temp: '常温', zone: 3 },
      { name: '冷冻猪肉', temp: '冷冻', zone: 2 },
      { name: '新鲜苹果', temp: '冷藏', zone: 0 }
    ]
    
    putawaySuggestions.value = products.map((product, i) => {
      const zone = tempZones[product.zone]
      // 智能推荐逻辑：根据温度匹配度和库存情况计算置信度
      const tempMatch = Math.random() * 0.15 + 0.85 // 温度匹配度
      const inventoryBalance = Math.random() * 0.2 + 0.8 // 库存均衡度
      const proximityScore = Math.random() * 0.15 + 0.85 // 靠近同类/出库口
      
      const confidence = (tempMatch * 0.5 + inventoryBalance * 0.3 + proximityScore * 0.2)
      
      // 推荐原因
      let reason = '温度匹配'
      if (confidence > 0.92) {
        reason = Math.random() > 0.5 ? '温度匹配 + 库存均衡' : '温度匹配 + 靠近出库口'
      } else if (tempMatch > 0.9) {
        reason = '温度匹配'
      } else if (inventoryBalance > 0.9) {
        reason = '库存均衡'
      } else {
        reason = '靠近同类商品'
      }
      
      return {
        sku: `SKU${String(i + 1).padStart(3, '0')}`,
        name: product.name,
        quantity: Math.floor(Math.random() * 200) + 50,
        suggested_location: `${zone.name}-${String(Math.floor(i / 3) + 1).padStart(2, '0')}-${String((i % 3) + 1).padStart(2, '0')}`,
        zone: zone.name,
        reason: reason,
        confidence: confidence
      }
    })
  } catch (e) {
    console.error('加载入库数据失败', e)
  }
}

// 作业管理数据
const operationSubTab = ref('tasks')
const operationTasks = ref<any[]>([])
const performanceData = ref<any[]>([])
const batchSuggestions = ref<any[]>([])
const batchStats = ref({ pending_orders: 0, suggested_batches: 0, estimated_time_saved: '0%' })
const loadOperationData = async () => {
  try {
    const [tasksRes, perfRes, batchRes] = await Promise.all([
      axios.get('/api/cold-chain/operation/tasks'),
      axios.get('/api/cold-chain/operation/performance'),
      axios.get('/api/cold-chain/operation/batch/suggestions')
    ])
    operationTasks.value = tasksRes.data
    performanceData.value = perfRes.data
    batchSuggestions.value = batchRes.data.suggestions
    batchStats.value = batchRes.data.stats
  } catch (e) {
    console.error('加载作业数据失败', e)
  }
}

const warehouseDialogVisible = ref(false)
const isEditWarehouse = ref(false)
const editingWarehouseId = ref<number>()
const warehouseForm = reactive({
  name: '', address: '', capacity: 1000, area: 500, temperature: -18, humidity: 45, status: '正常'
})

const showWarehouseDialog = () => {
  isEditWarehouse.value = false
  Object.assign(warehouseForm, { name: '', address: '', capacity: 1000, area: 500, temperature: -18, humidity: 45, status: '正常' })
  warehouseDialogVisible.value = true
}

const editWarehouse = (wh: any) => {
  isEditWarehouse.value = true
  editingWarehouseId.value = wh.id
  Object.assign(warehouseForm, wh)
  warehouseDialogVisible.value = true
}

const saveWarehouse = async () => {
  if (!warehouseForm.name || !warehouseForm.address) {
    ElMessage.warning('请填写仓库名称和地址')
    return
  }
  try {
    if (isEditWarehouse.value && editingWarehouseId.value) {
      await axios.put(`/api/cold-chain/warehouses/${editingWarehouseId.value}`, warehouseForm)
      ElMessage.success('仓库更新成功')
    } else {
      await axios.post('/api/cold-chain/warehouses', { ...warehouseForm, inventory: 0 })
      ElMessage.success('仓库添加成功')
    }
    warehouseDialogVisible.value = false
    await loadWarehouses()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const deleteWarehouse = async (wh: any) => {
  try {
    await ElMessageBox.confirm(`确定删除仓库 "${wh.name}" 吗？`, '提示', { type: 'warning' })
    await axios.delete(`/api/cold-chain/warehouses/${wh.id}`)
    ElMessage.success('删除成功')
    await loadWarehouses()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

// 车辆数据
const vehicles = ref<any[]>([])

// 加载车辆数据
const loadVehicles = async () => {
  try {
    const res = await axios.get('/api/cold-chain/vehicles/list')
    vehicles.value = res.data.map((v: any) => ({
      id: v.id,
      plate: v.plate,
      vehicleType: v.vehicleType,
      driver: v.driver,
      phone: v.phone,
      loadCapacity: v.loadCapacity,
      volume: v.volume,
      gpsDevice: v.gpsDevice,
      tempRange: v.tempRange,
      status: v.status,
      location: v.location,
      temperature: v.temperature,
      battery: v.battery
    }))
  } catch (e) {
    console.error('加载车辆数据失败', e)
  }
}

// 运输数据
const transports = ref<any[]>([])
const selectedTransportId = ref<string>('')

const vehicleDialogVisible = ref(false)
const isEditVehicle = ref(false)
const editingVehicleId = ref<number>()
const vehicleForm = reactive({
  plate: '', driver: '', phone: '', status: '空闲', location: '', temperature: -18, battery: 100,
  vehicleType: '冷藏车', loadCapacity: 5, volume: '', gpsDevice: '', tempRange: '-25°C~5°C'
})

const showVehicleDialog = () => {
  isEditVehicle.value = false
  Object.assign(vehicleForm, { plate: '', driver: '', phone: '', status: '空闲', location: '', temperature: -18, battery: 100, vehicleType: '冷藏车', loadCapacity: 5, volume: '', gpsDevice: '', tempRange: '-25°C~5°C' })
  vehicleDialogVisible.value = true
}

const editVehicle = (v: any) => {
  isEditVehicle.value = true
  editingVehicleId.value = v.id
  Object.assign(vehicleForm, v)
  vehicleDialogVisible.value = true
}

const saveVehicle = async () => {
  if (!vehicleForm.plate || !vehicleForm.driver) {
    ElMessage.warning('请填写车牌号和司机')
    return
  }
  try {
    if (isEditVehicle.value && editingVehicleId.value) {
      await axios.put(`/api/cold-chain/vehicles/${editingVehicleId.value}`, vehicleForm)
      ElMessage.success('车辆更新成功')
    } else {
      await axios.post('/api/cold-chain/vehicles', vehicleForm)
      ElMessage.success('车辆添加成功')
    }
    vehicleDialogVisible.value = false
    await loadVehicles()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const deleteVehicle = async (v: any) => {
  try {
    await ElMessageBox.confirm(`确定删除车辆 "${v.plate}" 吗？`, '提示', { type: 'warning' })
    await axios.delete(`/api/cold-chain/vehicles/${v.id}`)
    ElMessage.success('删除成功')
    await loadVehicles()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '删除失败')
    }
  }
}

const trackVehicle = (v: any) => {
  ElMessage.success(`正在追踪 ${v.plate}，当前位置: ${v.location}`)
}

// 运输数据
const transportData = ref([
  { timestamp: '2026-02-17 14:30', title: '到达目的地', location: '北京仓储中心', temperature: '-18°C', humidity: '45%', type: 'success', hollow: false },
  { timestamp: '2026-02-17 08:15', title: '离开中转站', location: '济南分拨中心', temperature: '-17°C', humidity: '48%', type: 'primary', hollow: false },
  { timestamp: '2026-02-16 22:00', title: '运输中', location: '南京路段', temperature: '-16°C', humidity: '50%', type: 'warning', hollow: false },
  { timestamp: '2026-02-16 18:00', title: '装货完成', location: '上海仓库', temperature: '-18°C', humidity: '45%', type: 'info', hollow: false }
])

// 库存数据
const inventoryData = ref([
  { product: '有机草莓 2斤装', quantity: '500箱', storage: 'A冷库-01区', expiry: '2026-02-25' },
  { product: '新鲜三文鱼', quantity: '200盒', storage: 'B冷库-02区', expiry: '2026-02-20' },
  { product: '进口车厘子', quantity: '800箱', storage: 'A冷库-03区', expiry: '2026-03-01' },
  { product: '有机西兰花', quantity: '300箱', storage: 'C冷库-01区', expiry: '2026-02-22' }
])

const totalInventory = computed(() => {
  return inventoryData.value.reduce((sum, item) => {
    const num = parseInt(item.quantity)
    return sum + (isNaN(num) ? 0 : num)
  }, 0)
})

const expiringCount = computed(() => {
  const now = new Date()
  return inventoryData.value.filter(item => {
    const exp = new Date(item.expiry)
    const diff = (exp.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    return diff <= 7 && diff > 0
  }).length
})

const isExpiring = (expiry: string) => {
  const now = new Date()
  const exp = new Date(expiry)
  const diff = (exp.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
  return diff <= 7 && diff > 0
}

const traceForm = reactive({ code: '' })
const traceResult = ref<any>(null)

const getTempColor = (temp: number) => {
  if (temp > -15) return '#F56C6C'
  if (temp < -20) return '#409EFF'
  return '#67C23A'
}

const traceProduct = () => {
  if (!traceForm.code) {
    ElMessage.warning('请输入追溯码')
    return
  }
  traceResult.value = {
    product: '有机草莓 2斤装',
    origin: '山东济南生态农场',
    processDate: '2026-02-15',
    storageTemp: '-18°C',
    transportRoute: '济南 → 南京 → 上海 → 北京'
  }
  ElMessage.success('追溯查询成功')
}
</script>

<style scoped>
.cold-chain-container {
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
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.nav-card {
  position: relative;
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 14px;
  padding: 16px 12px;
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
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary, #F8FAFC);
  border-radius: 12px;
  margin: 0 auto 12px;
  transition: all 0.3s ease;
}

.nav-card:hover .nav-icon-wrapper {
  background: color-mix(in srgb, var(--accent) 10%, transparent);
}

.nav-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #0F172A);
}

/* ========== 响应式 ========== */
@media (max-width: 1200px) {
  .quick-nav-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .cold-chain-container {
    padding: 20px;
  }

  .quick-nav-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .nav-card {
    padding: 12px 8px;
  }

  .nav-icon-wrapper {
    width: 40px;
    height: 40px;
  }

  .nav-label {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .quick-nav-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.monitor-cards { margin-bottom: 10px; }
.monitor-card { margin-bottom: 10px; }
.monitor-info h3 { font-size: 24px; margin: 0; }
.monitor-info p { margin: 5px 0 0; font-size: 12px; color: #909399; }

.section-card { margin-bottom: 10px; }
.section-card { animation: fadeIn 0.3s ease; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header span { font-size: 14px; font-weight: 500; }

.stat-item { text-align: center; padding: 10px; background: #f5f7fa; border-radius: 8px; }
.stat-item .num { display: block; font-size: 20px; font-weight: bold; color: #409eff; }
.stat-item .label { font-size: 11px; color: #909399; }

.warehouse-list, .inventory-list { display: flex; flex-direction: column; gap: 10px; }
.vehicle-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
@media (max-width: 768px) {
  .vehicle-list { grid-template-columns: 1fr; }
}
.warehouse-card, .vehicle-card, .inventory-card { padding: 12px; }

.warehouse-header, .vehicle-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.warehouse-title { display: flex; align-items: center; gap: 8px; font-weight: 500; font-size: 14px; }
.warehouse-info p { margin: 2px 0; font-size: 12px; color: #606266; }
.warehouse-actions, .vehicle-actions { display: flex; gap: 5px; margin-top: 6px; }

.vehicle-info { flex: 1; margin: 0 10px; }
.vehicle-info h4 { margin: 0; font-size: 14px; }
.vehicle-info p { margin: 2px 0 0; font-size: 11px; color: #909399; }
.vehicle-detail { display: flex; flex-wrap: wrap; gap: 6px; font-size: 11px; }
.vehicle-detail span { background: #f5f7fa; padding: 2px 6px; border-radius: 4px; }

.inventory-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.product-name { font-weight: 500; font-size: 14px; }
.inventory-info { display: flex; gap: 15px; font-size: 12px; color: #606266; align-items: center; }

.transport-map { margin-bottom: 15px; }
.timeline-info { margin: 5px 0 0; color: #909399; font-size: 12px; }
.timeline-info span { margin-right: 10px; }

.chart-placeholder { text-align: center; padding: 15px; }
.chart-placeholder p { margin: 10px 0 0; font-size: 12px; color: #909399; }
.analytics-note { font-size: 12px; color: #909399; text-align: center; margin-top: 5px; }

.loss-item { text-align: center; padding: 10px; background: #f5f7fa; border-radius: 8px; }
.loss-item .num { display: block; font-size: 18px; font-weight: bold; color: #67C23A; }
.loss-item .label { font-size: 11px; color: #909399; }

.trace-result { padding: 15px; background: #f5f7fa; border-radius: 8px; margin-top: 10px; }
.trace-result h4 { margin: 0 0 10px; }
.trace-result p { margin: 5px 0; font-size: 12px; }

.analytics-section { margin-bottom: 15px; }
.analytics-section h4 { font-size: 14px; margin: 0 0 10px 0; }

/* 品控管理 */
.quality-stats, .alert-stats { margin-bottom: 15px; }
.quality-standards, .alert-rules { display: flex; flex-direction: column; gap: 10px; margin-bottom: 15px; }
.standard-card, .rule-card { padding: 10px; }
.standard-header, .rule-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.standard-name, .rule-name { font-weight: 500; }
.standard-info, .rule-info { font-size: 12px; color: #606266; display: flex; flex-wrap: wrap; gap: 10px; }
.standard-info span, .rule-info span { display: block; }

/* 库存预警 */
.alert-list { display: flex; flex-direction: column; gap: 10px; }
.alert-card { padding: 10px; border-left: 4px solid #909399; }
.alert-card.alert-critical { border-left-color: #F56C6C; }
.alert-card.alert-high { border-left-color: #E6A23C; }
.alert-card.alert-medium { border-left-color: #409EFF; }
.alert-card.alert-low { border-left-color: #909399; }
.alert-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.alert-type { flex: 1; font-weight: 500; }
.alert-content { font-size: 12px; color: #606266; }
.alert-content p { margin: 3px 0; }
.alert-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.alert-time { font-size: 11px; color: #909399; }
</style>
