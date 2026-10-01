# 农产品产业数据驾驶舱 · 设计原型 V1

打开 `agri-market-dashboard.html` 可独立浏览，无需后端或网络依赖。`agri-market-dashboard-preview.jpg` 为 1920×1080 实际页面截图。

页面采用 1,095 条已采集市场快照与 64 个农业农村部价格点。口径、时间和来源在页面的“数据口径”中可查。支持五品类切换、地图地区筛选、行情搜索、来源跳转和 CSV 导出。属于设计评审原型，尚未接入生产接口与调度。

修改 `agri-market-dashboard.template.html` 后，运行 `python3 docs/prototypes/build_agri_prototype.py` 重新生成独立 HTML。数据和地图路径保存在相邻的 `agri-market-dashboard.snapshot.json`，构建无需重新抓取。

已在浏览器检查 1920×1080 一屏展示及窄屏布局；验证奶类日期和口径、水产湖北筛选得到 54 条、鲈鱼搜索得到 2 条，导出按钮显示 2 条结果生成反馈。未验证内置浏览器的下载文件落盘。

地图依据阿里云 DataV 地理数据绘制，供此版原型展示使用，来源保留在 snapshot 中。市场名称按来源去重，跨站名称尚未合并；“31 个省级地区”将新疆生产建设兵团归入新疆。

## 农业产业驾驶舱 V2 · 2026-10-01

打开 `agri-industry-dashboard.html`，同目录保留 V1 行情 HTML。六页包括总览、种植养殖、市场行情、冷链流通、产业风险、农业供应链金融。金融页另有公开背景与平台运营两种视图。

新增 109 条固定官方发布页自动采集记录、12 条人工核对指标和 5 个冷链节点。种植样本、贷款统计、抽检和冷链各自标明年份与资料范围；未接入平台融资业务，不使用种子数据展示实际金额。公开贷款分类重叠不合计，农业保险下限披露保留“超”。

构建：`python3 docs/prototypes/build_industry_prototype.py`。采集：在 backend 中运行 `.venv/bin/python -m scripts.collect_industry_data --output /tmp/funeng-industry.json`，复核新输出后再更新快照。当前命令不会写入生产数据库，也不会替换人工核对数据。

已在浏览器检查桌面 1600×1000 与手机 390×844；验证六页加载、省份筛选、地图筛选、空结果、全国重置、金融视图、来源弹窗与 CSV 内容预览。嵌入行情切换水产显示 167 条。内置浏览器的下载事件未返回文件路径，暂不宣称下载落盘验收通过；CSV 弹窗提供完整内容复制与下载链接。

截图：`agri-industry-overview-preview.jpg`、`agri-industry-finance-preview.jpg`、`agri-industry-platform-finance-preview.jpg`。本期页面为本地评审成果，尚未接入生产读取或自动采集调度。后续独立入库任务已将现有数据写入Supabase，详见[入库报告](../agri-supabase-import.md)；原型页面仍读取本地快照。
