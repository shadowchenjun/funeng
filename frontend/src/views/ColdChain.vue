<template>
  <div class="page-container">
    <PageHeader title="冷链物流" subtitle="全程温控 · 实时追踪 · 安全保障" />

    <ModuleNav v-model="activeTab" :groups="navGroups" aria-label="冷链功能导航" />

    <!-- 实时监控 -->
    <div v-show="activeTab === 'monitor'">
      <div class="stat-grid">
        <StatCard
          v-for="item in monitorData"
          :key="item.title"
          :value="item.value"
          :title="item.title"
          :type="item.type"
          :icon="item.icon"
        />
      </div>

      <SectionCard title="温度监控" :icon="Odometer">
        <div class="tile-grid">
          <div v-for="item in temperatureData" :key="item.warehouse" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ item.warehouse }}</span>
              <el-tag :type="item.status === '正常' ? 'success' : 'danger'">{{ item.status }}</el-tag>
            </div>
            <div class="tile-meta">
              <span>位置：{{ item.location }}</span>
              <span>
                温度：<b v-if="item.currentTemp != null" class="temp-value" :style="{ color: getTempColor(item.currentTemp) }">{{ item.currentTemp }}°C</b>
                <span v-else>暂无读数</span>
              </span>
              <span>湿度：{{ item.humidity }}</span>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 仓库管理 -->
    <div v-show="activeTab === 'warehouse'">
      <div class="stat-grid stat-grid--3">
        <StatCard :value="warehouses.length" title="仓库数" :icon="OfficeBuilding" />
        <StatCard :value="warehouses.filter(w => w.status === '正常').length" title="正常" type="success" :icon="CircleCheck" />
        <StatCard :value="totalCapacity" unit="m³" title="总容量" :icon="Box" />
      </div>

      <SectionCard title="仓库管理" :icon="OfficeBuilding">
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="showWarehouseDialog()">添加仓库</el-button>
        </template>
        <div class="tile-grid">
          <div v-for="wh in warehouses" :key="wh.id" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ wh.name }}</span>
              <el-tag :type="wh.status === '正常' ? 'success' : 'warning'">{{ wh.status }}</el-tag>
            </div>
            <div class="tile-meta">
              <span>地址：{{ wh.address }}</span>
              <span>容量：{{ wh.capacity }}m³ · 面积：{{ wh.area }}㎡</span>
              <span>温度：{{ wh.temperature }}°C · 湿度：{{ wh.humidity }}%</span>
              <span>库存：{{ wh.inventory }} 件</span>
            </div>
            <div class="tile-actions">
              <el-button type="primary" link @click="editWarehouse(wh)">编辑</el-button>
              <el-button type="danger" link @click="deleteWarehouse(wh)">删除</el-button>
            </div>
          </div>
        </div>

        <h4 class="subsection-title">仓库分布</h4>
        <div id="warehouseMap" class="map-box"></div>
      </SectionCard>
    </div>

    <!-- 车辆管理 -->
    <div v-show="activeTab === 'vehicle'">
      <div class="stat-grid stat-grid--3">
        <StatCard :value="vehicles.length" title="车辆数" :icon="Van" />
        <StatCard :value="vehicles.filter(v => v.status === '运输中').length" title="运输中" type="success" :icon="Position" />
        <StatCard :value="vehicles.filter(v => v.status === '空闲').length" title="空闲" :icon="Clock" />
      </div>

      <SectionCard title="车辆管理" :icon="Van">
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="showVehicleDialog()">添加车辆</el-button>
        </template>
        <div class="tile-grid">
          <div v-for="v in vehicles" :key="v.id" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ v.plate }}</span>
              <el-tag :type="v.status === '运输中' ? 'success' : v.status === '维修中' ? 'danger' : 'info'">
                {{ v.status }}
              </el-tag>
            </div>
            <div class="tile-meta">
              <span>司机：{{ v.driver }} · {{ v.phone }}</span>
              <span>当前位置：{{ v.location }}</span>
              <span>车厢温度：{{ v.temperature }}°C · 电量：{{ v.battery }}%</span>
            </div>
            <div class="tile-actions">
              <el-button type="primary" link @click="trackVehicle(v)">追踪</el-button>
              <el-button type="primary" link @click="editVehicle(v)">编辑</el-button>
              <el-button type="danger" link @click="deleteVehicle(v)">删除</el-button>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 运输追踪 -->
    <div v-show="activeTab === 'transport'">
      <SectionCard title="运输追踪" :icon="Location">
        <el-select v-model="selectedTransportId" placeholder="选择运输路线" class="w-full transport-select" @change="onTransportSelectChange">
          <el-option
            v-for="t in transports"
            :key="t.id"
            :label="`${t.vehicle_no} - ${t.route} (${t.status === 'in_transit' ? '运输中' : t.status === 'arrived' ? '已到达' : '等待'})`"
            :value="t.id"
          />
        </el-select>

        <div id="transportMap" class="map-box map-box--lg"></div>

        <el-timeline class="transport-timeline">
          <el-timeline-item
            v-for="(item, index) in transportData"
            :key="index"
            :timestamp="item.timestamp"
            :type="(item.type as any)"
            :hollow="item.hollow"
          >
            <div class="timeline-title">{{ item.title }}</div>
            <div class="timeline-info">{{ item.location }} · 温度 {{ item.temperature }} · 湿度 {{ item.humidity }}</div>
          </el-timeline-item>
        </el-timeline>
      </SectionCard>
    </div>

    <!-- 库存管理 -->
    <div v-show="activeTab === 'inventory'" class="section-stack">
      <div class="stat-grid stat-grid--3 stat-grid--flush">
        <StatCard :value="totalInventory" title="总库存" :icon="Box" />
        <StatCard :value="inventoryData.length" title="SKU 数" :icon="Goods" />
        <StatCard :value="expiringCount" title="临期" type="warning" :icon="Warning" />
      </div>

      <SectionCard title="库存管理" :icon="Box">
        <div class="tile-grid">
          <div v-for="item in inventoryData" :key="item.product" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ item.product }}</span>
              <el-tag>{{ item.storage }}</el-tag>
            </div>
            <div class="tile-meta">
              <span>数量：{{ item.quantity }}</span>
              <span>
                保质期：{{ item.expiry }}
                <el-tag v-if="isExpiring(item.expiry)" type="warning" class="inline-tag">临期</el-tag>
              </span>
            </div>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="质量追溯" :icon="Search">
        <el-form :model="traceForm" inline class="trace-form" @submit.prevent="traceProduct">
          <el-form-item label="追溯码">
            <el-input v-model="traceForm.code" placeholder="请输入追溯码" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="traceProduct">查询</el-button>
          </el-form-item>
        </el-form>

        <dl v-if="traceResult" class="tile trace-result">
          <div><dt>产品</dt><dd>{{ traceResult.product }}</dd></div>
          <div><dt>产地</dt><dd>{{ traceResult.origin }}</dd></div>
          <div><dt>加工日期</dt><dd>{{ traceResult.processDate }}</dd></div>
          <div><dt>存储温度</dt><dd>{{ traceResult.storageTemp }}</dd></div>
          <div><dt>运输路线</dt><dd>{{ traceResult.transportRoute }}</dd></div>
        </dl>
      </SectionCard>
    </div>

    <!-- 数据分析 -->
    <div v-show="activeTab === 'analytics'">
      <SectionCard title="数据分析" :icon="TrendCharts">
        <div class="analytics-grid">
          <div class="analytics-item">
            <h4 class="subsection-title">库存周转</h4>
            <el-progress type="circle" :percentage="72" :width="110" :color="themeColors.primary" />
            <p class="analytics-note">周转率 72%</p>
          </div>
          <div class="analytics-item">
            <h4 class="subsection-title">运输效率</h4>
            <el-progress type="circle" :percentage="85" :width="110" :color="themeColors.success" />
            <p class="analytics-note">准点率 85%</p>
          </div>
        </div>

        <h4 class="subsection-title">温度合规率</h4>
        <el-progress :percentage="98" :stroke-width="16" :color="themeColors.success" />
        <p class="analytics-note">本月温度异常时间：2.3 小时 / 720 小时</p>

        <h4 class="subsection-title">损耗统计</h4>
        <div class="metric-grid">
          <div class="metric"><span class="metric-value">0.5%</span><span class="metric-label">运输损耗</span></div>
          <div class="metric"><span class="metric-value">0.2%</span><span class="metric-label">仓储损耗</span></div>
          <div class="metric"><span class="metric-value">0.7%</span><span class="metric-label">总损耗</span></div>
        </div>
      </SectionCard>
    </div>

    <!-- 品控管理 -->
    <div v-show="activeTab === 'quality'">
      <div class="stat-grid">
        <StatCard :value="qualityInspections.length" title="检查总数" :icon="Document" />
        <StatCard :value="qualityInspections.filter(i => i.result === '合格').length" title="合格" type="success" :icon="CircleCheck" />
        <StatCard :value="qualityInspections.filter(i => i.result === '待复检').length" title="待复检" type="warning" :icon="Clock" />
        <StatCard :value="qualityInspections.filter(i => i.result === '不合格').length" title="不合格" type="danger" :icon="CircleClose" />
      </div>

      <SectionCard title="品控管理" :icon="CircleCheck">
        <template #extra>
          <el-button :icon="Refresh" @click="loadQualityData">刷新</el-button>
        </template>

        <h4 class="subsection-title">品控标准</h4>
        <div class="tile-grid">
          <div v-for="std in qualityStandards" :key="std.id" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ std.name }}</span>
              <el-tag>{{ std.category }}</el-tag>
            </div>
            <div class="tile-meta">
              <span>温度：{{ std.temperature.min }}~{{ std.temperature.max }}{{ std.temperature.unit }}</span>
              <span>湿度：{{ std.humidity.min }}~{{ std.humidity.max }}{{ std.humidity.unit }}</span>
              <span>货架期：{{ std.shelf_days }} 天</span>
            </div>
          </div>
        </div>

        <h4 class="subsection-title">检查记录</h4>
        <el-table :data="qualityInspections">
          <el-table-column prop="id" label="编号" width="100" />
          <el-table-column prop="type" label="类型" width="80" />
          <el-table-column prop="product" label="产品" min-width="120" />
          <el-table-column prop="batch_no" label="批次" width="140" />
          <el-table-column prop="result" label="结果" width="90">
            <template #default="{ row }">
              <el-tag :type="row.result === '合格' ? 'success' : row.result === '不合格' ? 'danger' : 'warning'">
                {{ row.result }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="评分" width="70" />
          <el-table-column prop="inspector" label="质检员" width="90" />
          <el-table-column prop="created_at" label="时间" width="150" />
        </el-table>
      </SectionCard>
    </div>

    <!-- 库存预警 -->
    <div v-show="activeTab === 'alert'">
      <div class="stat-grid stat-grid--3">
        <StatCard :value="inventoryStats.low_stock_count" title="库存不足" type="danger" :icon="Warning" />
        <StatCard :value="inventoryStats.overstock_count" title="库存过多" type="warning" :icon="Box" />
        <StatCard :value="inventoryStats.expiring_soon_count" title="临期预警" type="warning" :icon="Clock" />
      </div>

      <SectionCard title="库存预警" :icon="Bell">
        <template #extra>
          <el-button :icon="Refresh" @click="loadAlertData">刷新</el-button>
        </template>

        <h4 class="subsection-title">预警规则</h4>
        <div class="tile-grid">
          <div v-for="rule in alertRules" :key="rule.id" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ rule.name }}</span>
              <el-switch v-model="rule.enabled" />
            </div>
            <div class="tile-meta">
              <span>类型：{{ rule.type }}</span>
              <span>阈值：{{ rule.threshold }}{{ rule.unit }}</span>
              <span>通知：{{ rule.notify_channels.join('、') }}</span>
            </div>
          </div>
        </div>

        <h4 class="subsection-title">预警列表</h4>
        <div class="tile-grid">
          <div v-for="alert in inventoryAlerts" :key="alert.id" class="tile alert-tile" :class="'alert-' + alert.level">
            <div class="tile-header">
              <span class="alert-head">
                <el-tag :type="alert.level === 'critical' ? 'danger' : alert.level === 'high' ? 'warning' : 'info'">
                  {{ alert.level === 'critical' ? '紧急' : alert.level === 'high' ? '高' : alert.level === 'medium' ? '中' : '低' }}
                </el-tag>
                <span class="tile-title">{{ alert.type }}</span>
              </span>
              <el-tag :type="alert.status === '待处理' ? 'danger' : alert.status === '处理中' ? 'warning' : 'success'">
                {{ alert.status }}
              </el-tag>
            </div>
            <div class="tile-meta">
              <span>产品：{{ alert.product }}</span>
              <span>仓库：{{ alert.warehouse }}</span>
              <span>{{ alert.message }}</span>
            </div>
            <div class="tile-actions alert-footer">
              <span class="alert-time">{{ alert.created_at }}</span>
              <el-button v-if="alert.status === '待处理'" type="primary" link @click="resolveAlert(alert.id)">
                标记处理
              </el-button>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 货主管理 -->
    <div v-show="activeTab === 'owner'">
      <div class="stat-grid">
        <StatCard :value="ownerStats.total" title="货主总数" :icon="User" />
        <StatCard :value="ownerStats.active" title="正常运营" type="success" :icon="CircleCheck" />
        <StatCard :value="ownerStats.warehouses" title="仓库数量" :icon="OfficeBuilding" />
        <StatCard :value="ownerStats.zones" title="温区数量" :icon="Odometer" />
      </div>

      <SectionCard title="货主管理" :icon="User" no-padding>
        <template #extra>
          <el-button :icon="Refresh" @click="loadOwnerData">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="showOwnerDialog()">添加货主</el-button>
        </template>
        <el-table :data="ownerList">
          <el-table-column prop="code" label="货主编码" width="110" />
          <el-table-column prop="name" label="货主名称" min-width="150" />
          <el-table-column prop="contact" label="联系人" width="100" />
          <el-table-column prop="phone" label="联系电话" width="130" />
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column prop="address" label="地址" min-width="180" />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === '正常' ? 'success' : 'danger'">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="130" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="editOwner(row)">编辑</el-button>
              <el-button type="danger" link @click="deleteOwner(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </SectionCard>
    </div>

    <!-- 入库管理 -->
    <div v-show="activeTab === 'inbound'">
      <SectionCard title="入库管理" :icon="Bottom">
        <template #extra>
          <el-radio-group v-model="inboundSubTab">
            <el-radio-button label="appointments">预约管理</el-radio-button>
            <el-radio-button label="orders">入库单</el-radio-button>
            <el-radio-button label="suggestions">上架建议</el-radio-button>
          </el-radio-group>
        </template>

        <el-table v-show="inboundSubTab === 'appointments'" :data="appointmentList">
          <el-table-column prop="id" label="预约号" width="150" />
          <el-table-column prop="owner" label="货主" min-width="110" />
          <el-table-column prop="vehicle_no" label="车牌号" width="110" />
          <el-table-column prop="driver" label="司机" width="80" />
          <el-table-column prop="estimated_arrival" label="预计到达" width="160" />
          <el-table-column prop="expected_quantity" label="预计数量" width="90" />
          <el-table-column prop="dock" label="月台" width="70" />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === '已完成' ? 'success' : row.status === '收货中' ? 'warning' : 'info'">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="showAppointmentDetail(row)">详情</el-button>
              <el-button v-if="row.status === '待签到'" type="primary" link @click="signInAppointment(row)">签到</el-button>
              <el-button v-if="row.status === '已签到'" type="primary" link @click="startReceive(row)">开始收货</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-table v-show="inboundSubTab === 'orders'" :data="inboundOrders">
          <el-table-column prop="id" label="入库单号" width="160" />
          <el-table-column prop="owner" label="货主" min-width="110" />
          <el-table-column prop="inbound_date" label="入库日期" width="120" />
          <el-table-column prop="total_items" label="SKU 数" width="80" />
          <el-table-column prop="total_quantity" label="总数量" width="90" />
          <el-table-column prop="received_quantity" label="已收货" width="90" />
          <el-table-column prop="qualified_quantity" label="合格数" width="90" />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === '已入库' || row.status === '已完成' ? 'success' : row.status === '收货中' ? 'warning' : 'info'">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="130" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="showInboundDetail(row)">详情</el-button>
              <el-button v-if="row.status === '待收货' || row.status === '收货中'" type="primary" link @click="receiveGoods(row)">收货</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-show="inboundSubTab === 'suggestions'">
          <el-alert title="智能上架建议基于商品温度要求、库存均衡、拣货路径优化等因素" type="info" :closable="false" class="section-alert" />
          <el-table :data="putawaySuggestions">
            <el-table-column prop="sku" label="SKU" width="110" />
            <el-table-column prop="name" label="商品名称" min-width="140" />
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="suggested_location" label="推荐货位" width="120" />
            <el-table-column prop="zone" label="温区" width="100" />
            <el-table-column prop="reason" label="推荐原因" width="120">
              <template #default="{ row }">
                <el-tag :type="row.reason === '温度匹配' ? 'success' : row.reason === '库存均衡' ? 'warning' : 'info'">{{ row.reason }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="140">
              <template #default="{ row }">
                <span>{{ (row.confidence * 100).toFixed(2) }}%</span>
                <el-progress
                  :percentage="row.confidence * 100"
                  :color="levelColor(row.confidence, 0.9, 0.8)"
                  :show-text="false"
                  class="confidence-bar"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="confirmPutaway(row)">确认上架</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </SectionCard>
    </div>

    <!-- 作业管理 -->
    <div v-show="activeTab === 'operation'">
      <SectionCard title="作业管理" :icon="Operation">
        <template #extra>
          <el-radio-group v-model="operationSubTab">
            <el-radio-button label="tasks">任务列表</el-radio-button>
            <el-radio-button label="performance">人员绩效</el-radio-button>
            <el-radio-button label="batch">智能批次</el-radio-button>
          </el-radio-group>
        </template>

        <el-table v-show="operationSubTab === 'tasks'" :data="operationTasks">
          <el-table-column prop="id" label="任务编号" width="140" />
          <el-table-column prop="type" label="作业类型" width="90" />
          <el-table-column prop="priority" label="优先级" width="80">
            <template #default="{ row }">
              <el-tag :type="row.priority === '紧急' ? 'danger' : row.priority === '高' ? 'warning' : 'info'">{{ row.priority }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="owner" label="货主" min-width="100" />
          <el-table-column prop="location" label="库位" width="100" />
          <el-table-column prop="quantity" label="数量" width="70" />
          <el-table-column prop="assigned_to" label="执行人" width="90" />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === '已完成' ? 'success' : row.status === '执行中' ? 'warning' : 'info'">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="barcode" label="条码" width="130" />
        </el-table>

        <el-table v-show="operationSubTab === 'performance'" :data="performanceData">
          <el-table-column prop="employee_id" label="工号" width="100" />
          <el-table-column prop="name" label="姓名" width="90" />
          <el-table-column prop="department" label="部门" min-width="100" />
          <el-table-column prop="tasks_completed" label="完成任务" width="90" />
          <el-table-column prop="error_count" label="错误数" width="80" />
          <el-table-column prop="accuracy_rate" label="准确率" width="90">
            <template #default="{ row }">{{ (row.accuracy_rate * 100).toFixed(1) }}%</template>
          </el-table-column>
          <el-table-column prop="avg_task_time" label="平均耗时(分钟)" width="130" />
          <el-table-column prop="score" label="绩效评分" min-width="160">
            <template #default="{ row }">
              <el-progress :percentage="row.score" :color="levelColor(row.score, 80, 60)" />
            </template>
          </el-table-column>
        </el-table>

        <div v-show="operationSubTab === 'batch'">
          <div class="metric-grid batch-metrics">
            <div class="metric"><span class="metric-value">{{ batchStats.pending_orders }}</span><span class="metric-label">待处理订单</span></div>
            <div class="metric"><span class="metric-value">{{ batchStats.suggested_batches }}</span><span class="metric-label">建议批次</span></div>
            <div class="metric"><span class="metric-value">{{ batchStats.estimated_time_saved }}</span><span class="metric-label">预计节省时间</span></div>
          </div>
          <el-table :data="batchSuggestions">
            <el-table-column prop="id" label="批次号" width="120" />
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column prop="description" label="描述" min-width="220" />
            <el-table-column prop="orders" label="包含订单" min-width="180">
              <template #default="{ row }">{{ row.orders.join(', ') }}</template>
            </el-table-column>
            <el-table-column prop="total_items" label="商品数" width="80" />
            <el-table-column prop="estimated_pick_time" label="预计拣货时间" width="120" />
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="row.priority === '高' ? 'danger' : 'info'">{{ row.priority }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default>
                <el-button type="primary" link>创建批次</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </SectionCard>
    </div>

    <!-- 添加/编辑仓库对话框 -->
    <el-dialog v-model="warehouseDialogVisible" :title="isEditWarehouse ? '编辑仓库' : '添加仓库'" class="dialog-md">
      <el-form :model="warehouseForm" label-width="90px">
        <el-form-item label="仓库名称" required>
          <el-input v-model="warehouseForm.name" placeholder="如：北京冷库" />
        </el-form-item>
        <el-form-item label="地址" required>
          <el-input v-model="warehouseForm.address" placeholder="仓库地址" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="容量(m³)">
              <el-input-number v-model="warehouseForm.capacity" :min="1" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="面积(㎡)">
              <el-input-number v-model="warehouseForm.area" :min="1" class="w-full" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="温度(°C)">
              <el-input-number v-model="warehouseForm.temperature" :min="-30" :max="10" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="湿度(%)">
              <el-input-number v-model="warehouseForm.humidity" :min="0" :max="100" class="w-full" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="warehouseForm.status" class="w-full">
            <el-option label="正常" value="正常" />
            <el-option label="维护中" value="维护中" />
            <el-option label="已满" value="已满" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="warehouseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveWarehouse">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑车辆对话框 -->
    <el-dialog v-model="vehicleDialogVisible" :title="isEditVehicle ? '编辑车辆' : '添加车辆'" class="dialog-md">
      <el-form :model="vehicleForm" label-width="90px">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="车牌号" required>
              <el-input v-model="vehicleForm.plate" placeholder="如：京A12345" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="车型">
              <el-select v-model="vehicleForm.vehicleType" class="w-full">
                <el-option label="冷藏车" value="冷藏车" />
                <el-option label="厢式货车" value="厢式货车" />
                <el-option label="保温车" value="保温车" />
                <el-option label="冷冻车" value="冷冻车" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="载重(吨)">
              <el-input-number v-model="vehicleForm.loadCapacity" :min="0.1" :precision="1" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="车厢容积">
              <el-input v-model="vehicleForm.volume" placeholder="如：50立方米" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">司机信息</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="司机" required>
              <el-input v-model="vehicleForm.driver" placeholder="司机姓名" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="电话">
              <el-input v-model="vehicleForm.phone" placeholder="联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">设备信息</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="GPS 设备">
              <el-input v-model="vehicleForm.gpsDevice" placeholder="GPS 设备编号" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="温度范围">
              <el-input v-model="vehicleForm.tempRange" placeholder="如：-25°C~5°C" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="vehicleForm.status" class="w-full">
            <el-option label="空闲" value="空闲" />
            <el-option label="运输中" value="运输中" />
            <el-option label="维修中" value="维修中" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="vehicleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveVehicle">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑货主对话框 -->
    <el-dialog v-model="ownerDialogVisible" :title="isEditOwner ? '编辑货主' : '添加货主'" class="dialog-sm">
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
          <el-select v-model="ownerForm.status" class="w-full">
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
    <el-dialog v-model="appointmentDetailVisible" title="预约详情" class="dialog-md">
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
        <el-button v-if="currentAppointment.status === '待签到'" type="primary" @click="signInAppointment(currentAppointment)">签到</el-button>
        <el-button v-if="currentAppointment.status === '已签到'" type="primary" @click="startReceive(currentAppointment)">开始收货</el-button>
      </template>
    </el-dialog>

    <!-- 入库单详情对话框 -->
    <el-dialog v-model="inboundDetailVisible" title="入库单详情" class="dialog-lg">
      <el-descriptions :column="2" border v-if="currentInboundOrder">
        <el-descriptions-item label="入库单号">{{ currentInboundOrder.id }}</el-descriptions-item>
        <el-descriptions-item label="货主">{{ currentInboundOrder.owner }}</el-descriptions-item>
        <el-descriptions-item label="入库日期">{{ currentInboundOrder.inbound_date }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentInboundOrder.status === '已入库' ? 'success' : currentInboundOrder.status === '收货中' ? 'warning' : 'info'">{{ currentInboundOrder.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="SKU 数">{{ currentInboundOrder.total_items }}</el-descriptions-item>
        <el-descriptions-item label="总数量">{{ currentInboundOrder.total_quantity }}</el-descriptions-item>
        <el-descriptions-item label="已收货">{{ currentInboundOrder.received_quantity }}</el-descriptions-item>
        <el-descriptions-item label="合格数">{{ currentInboundOrder.qualified_quantity }}</el-descriptions-item>
      </el-descriptions>
      <h4 class="subsection-title">货物明细</h4>
      <el-table :data="currentInboundOrder.items || []">
        <el-table-column prop="sku" label="SKU" width="120" />
        <el-table-column prop="name" label="商品名称" min-width="140" />
        <el-table-column prop="expected_qty" label="预期数量" width="90" />
        <el-table-column prop="received_qty" label="已收数量" width="90" />
        <el-table-column prop="qualified_qty" label="合格数" width="90" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '已完成' ? 'success' : row.status === '部分收货' ? 'warning' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="inboundDetailVisible = false">关闭</el-button>
        <el-button v-if="currentInboundOrder.status === '待收货' || currentInboundOrder.status === '收货中'" type="primary" @click="receiveGoods(currentInboundOrder)">收货</el-button>
      </template>
    </el-dialog>

    <!-- 收货对话框 -->
    <el-dialog v-model="receiveDialogVisible" title="收货入库" class="dialog-sm">
      <el-form :model="receiveForm" label-width="90px">
        <el-form-item label="入库单号">
          <el-input v-model="receiveForm.orderId" disabled />
        </el-form-item>
        <el-form-item label="SKU">
          <el-select v-model="receiveForm.sku" placeholder="请选择 SKU" class="w-full">
            <el-option v-for="item in receiveForm.items" :key="item.sku" :label="`${item.sku} - ${item.name}`" :value="item.sku" />
          </el-select>
        </el-form-item>
        <el-form-item label="收货数量">
          <el-input-number v-model="receiveForm.quantity" :min="1" :max="receiveForm.maxQty" class="w-full" />
        </el-form-item>
        <el-form-item label="合格数量">
          <el-input-number v-model="receiveForm.qualifiedQty" :min="0" :max="receiveForm.quantity" class="w-full" />
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Bell, Bottom, Box, CircleCheck, CircleClose, Clock, DataAnalysis, Document, Goods, Location, OfficeBuilding,
  Odometer, Operation, Plus, Position, Refresh, Search, TrendCharts, User, Van, Warning
} from '@element-plus/icons-vue'
import type { ModuleNavGroup } from '../components/ui/ModuleNav.vue'
import { themeColors, levelColor } from '../utils/theme'
import { createLatestGuard } from '../utils/latest'

declare global {
  interface Window {
    AMap: any
  }
}

const activeTab = ref('monitor')
// 11 项按业务分组（spec §3.5）：监测 / 仓储 / 运输 / 运营
const navGroups: ModuleNavGroup[] = [
  {
    label: '监测',
    items: [
      { key: 'monitor', label: '实时监控', icon: DataAnalysis },
      { key: 'alert', label: '库存预警', icon: Warning },
      { key: 'analytics', label: '数据分析', icon: TrendCharts }
    ]
  },
  {
    label: '仓储',
    items: [
      { key: 'warehouse', label: '仓库管理', icon: OfficeBuilding },
      { key: 'inventory', label: '库存管理', icon: Box },
      { key: 'inbound', label: '入库管理', icon: Bottom },
      { key: 'quality', label: '品控管理', icon: CircleCheck }
    ]
  },
  {
    label: '运输',
    items: [
      { key: 'vehicle', label: '车辆管理', icon: Van },
      { key: 'transport', label: '运输追踪', icon: Location }
    ]
  },
  {
    label: '运营',
    items: [
      { key: 'owner', label: '货主管理', icon: User },
      { key: 'operation', label: '作业管理', icon: Operation }
    ]
  }
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
const transportGuard = createLatestGuard()
const warehouseGuard = createLatestGuard()

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
  const isCurrent = warehouseGuard.begin()
  nextTick(async () => {
    await waitForAMap()
    if (!isCurrent() || !window.AMap) return

    const container = document.getElementById('warehouseMap')
    if (!container) return

    // 面板用 v-show 常驻：地图只建一次（首次必须在容器可见时），之后清空覆盖物重画
    if (warehouseMap) {
      warehouseMap.clearMap()
    } else {
      warehouseMap = new window.AMap.Map('warehouseMap', {
        zoom: 10,
        center: [117.12, 36.65],
        viewMode: '2D',
        resizeEnable: true
      })
    }

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
  // 快速切换路线时只认最新一次重画；每个 await 之后校验，过期或已卸载则放弃（review R2）
  const isCurrent = transportGuard.begin()
  nextTick(async () => {
    await waitForAMap()
    if (!isCurrent() || !window.AMap) return

    const container = document.getElementById('transportMap')
    if (!container) return

    // 地图只建一次（无运输记录时也显示底图）；覆盖物在地理编码完成后统一替换
    if (!transportMap) {
      transportMap = new window.AMap.Map('transportMap', {
        zoom: 5,
        center: [117.12, 36.65],
        viewMode: '2D',
        resizeEnable: true
      })
    }

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

      // 先完成全部异步地理编码，再一次性替换覆盖物与时间线，避免过期请求逐步写入
      const startCoord = await getCoord(startCity)
      if (!isCurrent()) return
      const endCoord = await getCoord(endCity)
      if (!isCurrent()) return

      transportMap.clearMap()

      if (startCoord) {
        const startMarker = new window.AMap.Marker({
          position: startCoord,
          title: `起点: ${startCity}`,
          icon: new window.AMap.Icon({ size: [16, 16], image: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-start.png' })
        })
        transportMap.add(startMarker)
      }

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

// GET /monitoring/temperature 的单条传感器读数
interface SensorReading {
  location: string
  address: string | null
  current_temp: number | null
  target_temp: number
  humidity: number | null
  status: string
}

// 加载监控数据
const loadMonitorData = async () => {
  try {
    const res = await axios.get<SensorReading[]>('/api/cold-chain/monitoring/temperature')
    // 接口字段（location / address / current_temp）映射为视图字段
    temperatureData.value = res.data.map((s) => ({
      warehouse: s.location,
      location: s.address ?? '—',
      currentTemp: s.current_temp,
      targetTemp: s.target_temp,
      humidity: s.humidity == null ? '—' : `${s.humidity}%`,
      status: s.status
    }))
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
  // v-show 切换后容器已可见（init 内部 nextTick），不再需要延时
  if (newTab === 'warehouse') {
    initWarehouseMap()
  }
  if (newTab === 'transport') {
    initTransportMap()
  }
})

onBeforeUnmount(() => {
  // 先作废进行中的重画，再销毁地图，避免迟到回调写入已销毁实例
  transportGuard.invalidate()
  warehouseGuard.invalidate()
  warehouseMap?.destroy()
  transportMap?.destroy()
  warehouseMap = null
  transportMap = null
})

// 监控数据
const monitorData = ref<{ title: string; value: string; type: 'primary' | 'success' | 'danger'; icon: typeof Van }[]>([
  { title: '在线车辆', value: '12', type: 'success', icon: Van },
  { title: '在线仓库', value: '5', type: 'primary', icon: OfficeBuilding },
  { title: '温度异常', value: '0', type: 'danger', icon: Warning },
  { title: '今日运输', value: '28', type: 'primary', icon: Position }
])

interface TempTile {
  warehouse: string
  location: string
  currentTemp: number | null
  targetTemp: number
  humidity: string
  status: string
}

const temperatureData = ref<TempTile[]>([
  { warehouse: 'A冷库', location: '北京仓', currentTemp: -18, targetTemp: -18, humidity: '45%', status: '正常' },
  { warehouse: 'B冷库', location: '上海仓', currentTemp: -20, targetTemp: -18, humidity: '42%', status: '正常' },
  { warehouse: '京A12345', location: '运输中-京沪高速', currentTemp: -16, targetTemp: -18, humidity: '50%', status: '正常' },
  { warehouse: '京B67890', location: '运输中-京港澳', currentTemp: -17, targetTemp: -18, humidity: '48%', status: '正常' }
])

// 仓库数据
const warehouses = ref<any[]>([])

// 仓库增删改后，若地图正在显示则重画标记
watch(warehouses, () => {
  if (activeTab.value === 'warehouse') initWarehouseMap()
})

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

// 签到（持久化到后端：待签到 -> 已签到）
const signInAppointment = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确认车辆 ${row.vehicle_no} 签到吗？`, '签到确认', { type: 'info' })
    await axios.put(`/api/cold-chain/inbound/appointments/${row.id}/checkin`)
    ElMessage.success('签到成功')
    appointmentDetailVisible.value = false
    await loadInboundData()
  } catch (e: any) {
    if (e !== 'cancel' && e?.action !== 'cancel') {
      ElMessage.error(e?.response?.data?.detail || '签到失败')
    }
  }
}

// 开始收货（持久化到后端：已签到 -> 收货中，并生成入库单）
const startReceive = async (row: any) => {
  try {
    const res = await axios.put(`/api/cold-chain/inbound/appointments/${row.id}/receive`)
    ElMessage.success(`已开始收货，生成入库单 ${res.data.order_id || ''}`)
    appointmentDetailVisible.value = false
    await loadInboundData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '开始收货失败')
  }
}

// 入库单详情
const inboundDetailVisible = ref(false)
const currentInboundOrder = ref<any>(null)
const showInboundDetail = async (row: any) => {
  // 货物明细来自后端（/inbound/orders 列表已含 items；缺失时拉取详情兜底）
  if (!row.items || row.items.length === 0) {
    try {
      const res = await axios.get(`/api/cold-chain/inbound/orders/${row.id}`)
      Object.assign(row, res.data)
    } catch (e) {
      console.error('加载入库单详情失败', e)
    }
  }
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

const receiveGoods = async (row: any) => {
  let items = row.items
  if (!items || items.length === 0) {
    try {
      const res = await axios.get(`/api/cold-chain/inbound/orders/${row.id}`)
      Object.assign(row, res.data)
      items = row.items
    } catch (e) {
      console.error('加载入库单详情失败', e)
    }
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
  
  // 收货登记持久化到后端（累加 SKU 已收/合格数量，收齐后订单自动变为已入库）
  try {
    await axios.post(`/api/cold-chain/inbound/orders/${receiveForm.value.orderId}/receive`, {
      sku: receiveForm.value.sku,
      quantity: receiveForm.value.quantity,
      qualified_qty: receiveForm.value.qualifiedQty,
      remark: receiveForm.value.remark || undefined
    })
    ElMessage.success('收货成功')
    receiveDialogVisible.value = false
    inboundDetailVisible.value = false
    await loadInboundData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '收货失败')
  }
}

// 确认上架（持久化到后端：记录货位并占用温区托位）
const confirmPutaway = async (row: any) => {
  if (!row.suggested_location || !row.zone_id) {
    ElMessage.warning('该 SKU 无可用温区，无法上架')
    return
  }
  try {
    await axios.post(`/api/cold-chain/inbound/orders/${row.order_id}/putaway`, {
      sku: row.sku,
      zone_id: row.zone_id,
      location: row.suggested_location
    })
    ElMessage.success(`已确认上架到 ${row.suggested_location}`)
    await loadPutawaySuggestions()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '上架失败')
  }
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
    
    // 上架建议来自后端（按温度匹配、温区剩余容量与距出库口距离确定性打分）
    await loadPutawaySuggestions(ordersRes.data)
  } catch (e) {
    console.error('加载入库数据失败', e)
  }
}

// 加载上架建议：取第一个仍有未上架货物的入库单
const loadPutawaySuggestions = async (orders?: any[]) => {
  try {
    let list = orders
    if (!list) {
      const res = await axios.get('/api/cold-chain/inbound/orders')
      list = res.data
    }
    const pending = (list || []).find((o: any) =>
      (o.items || []).some((i: any) => !i.zone_id))
    if (!pending) {
      putawaySuggestions.value = []
      return
    }
    const res = await axios.get(`/api/cold-chain/inbound/suggestions/${pending.id}`)
    putawaySuggestions.value = res.data
  } catch (e) {
    console.error('加载上架建议失败', e)
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
  if (temp > -15) return 'var(--color-danger)'
  if (temp < -20) return 'var(--primary)'
  return 'var(--color-success)'
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
.stat-grid--flush {
  margin-bottom: 0;
}

.temp-value {
  font-weight: 600;
}

.map-box {
  width: 100%;
  height: 240px;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.map-box--lg {
  height: 300px;
  margin-bottom: 20px;
}

.transport-select {
  margin-bottom: 16px;
}

.timeline-title {
  font-size: var(--font-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.timeline-info {
  margin-top: 4px;
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.inline-tag {
  margin-left: 6px;
}

.trace-form {
  margin-bottom: 4px;
}

.trace-result {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 0;
}

.trace-result dt {
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.trace-result dd {
  margin: 2px 0 0;
  font-size: var(--font-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.analytics-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.analytics-note {
  margin: 8px 0 0;
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

/* 预警左侧级别条 */
.alert-tile {
  border-left-width: 4px;
}

.alert-critical { border-left-color: var(--color-danger); }
.alert-high { border-left-color: var(--color-warning); }
.alert-medium { border-left-color: var(--primary); }
.alert-low { border-left-color: var(--color-info); }

.alert-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-footer {
  align-items: center;
  justify-content: space-between;
}

.alert-time {
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.section-alert {
  margin-bottom: 16px;
}

.confidence-bar {
  margin-top: 4px;
}

.batch-metrics {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .analytics-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .map-box--lg {
    height: 240px;
  }
}
</style>
