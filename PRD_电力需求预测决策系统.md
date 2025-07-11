# 电力需求预测决策系统 PRD 文档

## 1. 项目概述

### 1.1 项目背景
开发一个基于机器学习的电力需求预测决策系统，用于研究和实验目的。系统将基于历史电力使用数据和温度数据，使用XGBoost模型预测2022年6月30日的24小时电力需求，并提供模型可解释性分析和预测结果调整功能。

### 1.2 项目目标
- 基于历史数据预测2022年6月30日的24小时电力需求
- 提供SHAP和LIME模型可解释性分析
- 支持用户对预测结果进行全局和局部调整
- 提供直观的数据可视化界面
- 支持预测结果的保存和导出

### 1.3 目标用户
- 研究人员和数据科学家
- 电力系统分析师
- 学术研究用户

## 2. 技术架构

### 2.1 前端技术栈
- **框架**: Next.js
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **图表库**: Chart.js 或 Recharts
- **状态管理**: React Hooks

### 2.2 后端技术栈
- **框架**: FastAPI
- **语言**: Python 3.8+
- **机器学习**: XGBoost
- **可解释性**: SHAP、LIME
- **数据处理**: Pandas、NumPy
- **API文档**: Swagger/OpenAPI

### 2.3 数据源
- **文件**: `temp_usage_data.csv`
- **字段结构**:
  - `time`: 时间戳（小时级别，格式：YYYY-MM-DD HH:MM:SS）
  - `temp`: 温度（摄氏度，浮点数）
  - `usage`: 电力使用量（数值）
- **数据范围**: 2020年4月 - 2022年10月
- **训练数据**: 2022年6月9日 - 2022年6月29日（前三周，504小时）
- **预测目标**: 2022年6月30日24小时电力需求

## 3. 功能模块设计

### 3.1 界面布局
系统界面采用固定布局，分为上下两个主要区域：

#### 上半部分（三个并列模块）
```
┌─────────────────┬─────────────────┬─────────────────┐
│   情景信息       │  历史数据分析    │  模型可解释性    │
│ Context Info    │ Data Analysis   │ Interpretability│
└─────────────────┴─────────────────┴─────────────────┘
```

#### 下半部分（两个并列模块）
```
┌─────────────────────────────────┬─────────────────┐
│          用户预测                │     调整功能     │
│       User Prediction           │   Adjustment    │
└─────────────────────────────────┴─────────────────┘
```

### 3.2 详细功能说明

#### 3.2.1 情景信息模块 (Context Information)
显示2022年6月24日-29日的关键信息：

**数据内容**:
- **6月24日 (周五)**: 32.6°C, ≈49 GW, +≈20%, 热浪前哨，高于常年均值约8 GW
- **6月25日 (周六)**: 35.4°C, ≈51 GW, +≈25%, 首次进入"猛暑日"
- **6月26日 (周日)**: 36.2°C, ≈52.5 GW, +≈28%, 需求创当年6月周末纪录
- **6月27日 (周一)**: 35.7°C, ≈53.3 GW, +≈30%, 余裕率预估跌至3%, 政府首次连发"需给ひっ迫注意報"
- **6月28日 (周二)**: 35.1°C, ≈54.5 GW, +≈33%, 14-15时段逼近55 GW
- **6月29日 (周三)**: 35.4°C, ≈54.8 GW, +≈33%, 预测裕度仅2.6% (16:30-17:00), 史上首次6月出现"100%需给率"预警

**UI组件**:
- 下拉选择框：天气信息、特殊事件、假期信息
- 文本显示区域：显示选中日期的详细信息

#### 3.2.2 历史数据分析模块 (Data Analysis Information)
- **电力使用历史**: 显示历史电力使用量和AI预测对比图表
- **温度变化**: 显示温度变化趋势图
- **数据时间范围**: 2022年6月9日-6月29日（预测日前三周）
- **图表类型**: 时间序列折线图
- **图例**: 历史电力使用量（蓝线）、AI预测（红线）、温度变化（橙线）

**UI组件**:
- 双轴折线图（电力使用量 + 温度）
- 图表控制按钮（缩放、重置）
- 数据点悬停提示

#### 3.2.3 模型可解释性模块 (Model Interpretability)
- **特征重要性表格**: 显示各特征对预测结果的重要性评分
  - hour（小时）: 重要性评分
  - temp（温度）: 重要性评分  
  - day_of_week（星期几）: 重要性评分
  - week_of_month（月中第几周）: 重要性评分
- **SHAP值可视化**: 显示正负贡献值
- **LIME分析**: 显示局部可解释性分析结果
- **预测值显示**: 显示具体的预测数值和置信区间

**UI组件**:
- 特征重要性表格
- SHAP值条形图（正负值用不同颜色）
- 预测值数字显示

#### 3.2.4 用户预测模块 (User Prediction)
- **24小时预测曲线**: 显示2022年6月30日0-23时的电力需求预测
- **数据点标注**: 每小时的具体预测值
- **交互功能**: 
  - 鼠标悬停查看详细数值
  - 支持局部调整（拖拽数据点）
- **图表样式**: 蓝色折线图，红色数据点标注

**UI组件**:
- 可交互的折线图
- 数据点拖拽功能
- 实时数值显示
- 重置按钮

#### 3.2.5 调整功能模块 (Adjustment)

**全局调整 (Global Adjustment)**:
- **Start Time**: 下拉选择框（0-23小时）
- **End Time**: 下拉选择框（0-23小时）
- **Direction**: 下拉选择框（增加 Increase / 减少 Decrease）
- **Adjustment Percentage**: 数字输入框（1-50%）
- **应用按钮**: 执行全局调整

**局部调整 (Local Adjustment)**:
- **拖拽功能**: 直接拖拽预测曲线上的数据点
- **实时更新**: 调整后立即显示新数值
- **重置功能**: 恢复到原始预测值

**UI组件**:
- 调整类型选择（全局/局部）
- 参数输入表单
- 应用/重置按钮
- 调整历史显示

## 4. 后端数据流程

### 4.1 数据处理流程
1. **数据加载**: 读取 `temp_usage_data.csv`
2. **数据筛选**: 选择2022年6月9日-6月29日的数据（前三周）
3. **特征工程**: 
   ```python
   # 提取时间特征
   df['hour'] = df['time'].dt.hour
   df['day_of_week'] = df['time'].dt.dayofweek
   df['week_of_month'] = (df['time'].dt.day - 1) // 7 + 1
   ```
4. **数据清洗**: 处理缺失值、异常值
5. **避免数据泄漏**: 确保训练数据不包含6月30日及之后的数据

### 4.2 模型训练流程
1. **训练数据**: 2022年6月9日-6月29日（3周，504小时）
2. **目标变量**: 电力使用量（usage）
3. **特征变量**: ['temp', 'hour', 'day_of_week', 'week_of_month']
4. **模型配置**: 
   ```python
   xgb_params = {
       'n_estimators': 100,
       'max_depth': 6,
       'learning_rate': 0.1,
       'random_state': 42
   }
   ```
5. **预测目标**: 2022年6月30日24小时电力需求

### 4.3 可解释性分析
1. **SHAP分析**: 
   ```python
   explainer = shap.TreeExplainer(model)
   shap_values = explainer.shap_values(X_test)
   ```
2. **LIME分析**: 
   ```python
   explainer = lime.tabular.LimeTabularExplainer(X_train)
   explanation = explainer.explain_instance(instance, model.predict)
   ```
3. **特征重要性**: 各特征对预测的贡献度排序

### 4.4 API接口设计

#### 4.4.1 数据接口
```python
GET /api/historical-data
# 返回: 前三周历史数据
{
    "data": [
        {"time": "2022-06-09 00:00:00", "temp": 16.8, "usage": 2425.4},
        ...
    ]
}

GET /api/context-info
# 返回: 情景信息数据
{
    "weather_info": {...},
    "special_events": {...},
    "holiday_info": {...}
}
```

#### 4.4.2 预测接口
```python
GET /api/prediction
# 返回: 6月30日24小时预测结果
{
    "predictions": [
        {"hour": 0, "predicted_usage": 3120.08, "confidence_interval": [2950, 3290]},
        ...
    ],
    "model_metrics": {
        "mae": 150.2,
        "rmse": 200.5,
        "r2_score": 0.85
    }
}
```

#### 4.4.3 可解释性接口
```python
GET /api/model-explanation
# 返回: SHAP和LIME可解释性数据
{
    "feature_importance": {
        "temp": 0.45,
        "hour": 0.35,
        "day_of_week": 0.15,
        "week_of_month": 0.05
    },
    "shap_values": [...],
    "lime_explanation": {...}
}
```

#### 4.4.4 调整接口
```python
POST /api/adjust-prediction
# 请求体:
{
    "adjustment_type": "global",  # or "local"
    "start_hour": 10,
    "end_hour": 15,
    "direction": "increase",
    "percentage": 20,
    "local_adjustments": [...]  # for local adjustments
}
# 返回: 调整后的预测结果
```

#### 4.4.5 导出接口
```python
GET /api/export-results?format=csv
# 返回: CSV文件下载
```

## 5. 用户交互流程

### 5.1 系统加载流程
1. 用户访问系统首页
2. 后端自动加载数据并训练模型
3. 生成6月30日24小时预测
4. 计算SHAP和LIME可解释性分析
5. 前端加载并显示所有模块
6. 显示加载完成状态

### 5.2 预测调整流程

#### 全局调整流程
1. 用户在调整模块选择"全局调整"
2. 设置开始时间、结束时间、调整方向、调整百分比
3. 点击"应用调整"按钮
4. 系统计算调整后的预测值
5. 更新用户预测模块的图表
6. 显示调整前后的对比

#### 局部调整流程
1. 用户在预测图表上拖拽数据点
2. 系统实时计算新的预测值
3. 立即更新图表显示
4. 显示调整后的具体数值
5. 提供撤销功能

### 5.3 结果导出流程
1. 用户点击"导出结果"按钮
2. 选择导出格式（CSV）
3. 系统生成包含以下内容的文件：
   - 原始预测值
   - 调整后预测值
   - 调整参数
   - 时间戳
4. 自动下载到用户本地

## 6. 技术实现要点

### 6.1 数据处理要点
- 使用pandas处理时间序列数据
- 确保训练数据的时间范围正确（避免数据泄漏）
- 特征工程要考虑时间周期性
- 数据验证和异常值处理

### 6.2 模型训练要点
- XGBoost参数调优
- 交叉验证确保模型稳定性
- 保存训练好的模型用于预测
- 模型性能评估指标

### 6.3 可解释性要点
- SHAP TreeExplainer用于XGBoost模型
- LIME Tabular Explainer用于局部解释
- 可视化SHAP值的正负贡献
- 特征重要性排序和展示

### 6.4 前端实现要点
- 使用Chart.js实现交互式图表
- 拖拽功能使用Chart.js的事件处理
- 响应式布局适配不同屏幕尺寸
- 状态管理和数据同步

### 6.5 性能优化
- 前端图表渲染优化
- 后端API响应时间优化
- 数据缓存策略
- 异步加载机制

## 7. 开发计划

### 阶段1: 后端开发（预计2-3天）
- [ ] 环境搭建和依赖安装
- [ ] 数据处理和特征工程模块
- [ ] XGBoost模型训练模块
- [ ] SHAP和LIME可解释性分析模块
- [ ] FastAPI接口开发
- [ ] API测试和文档

### 阶段2: 前端开发（预计2-3天）
- [ ] Next.js项目初始化和配置
- [ ] Tailwind CSS样式配置
- [ ] 界面布局和组件开发
- [ ] Chart.js图表集成
- [ ] 交互功能实现（拖拽、调整）
- [ ] API集成和数据绑定

### 阶段3: 集成测试（预计1天）
- [ ] 前后端集成测试
- [ ] 功能完整性测试
- [ ] 用户体验测试
- [ ] 性能优化
- [ ] 部署准备

### 阶段4: 文档和部署（预计0.5天）
- [ ] 用户使用文档
- [ ] 技术文档完善
- [ ] 部署配置
- [ ] 最终验收

## 8. 验收标准

### 8.1 功能验收标准
1. ✅ 系统能正确加载历史数据并训练XGBoost模型
2. ✅ 能准确预测2022年6月30日24小时电力需求
3. ✅ SHAP和LIME可解释性分析结果正确显示
4. ✅ 全局调整功能按指定逻辑正确计算
5. ✅ 局部调整（拖拽）功能正常工作
6. ✅ 预测结果能正确导出为CSV文件
7. ✅ 界面布局符合设计要求
8. ✅ 所有图表正确显示历史数据和预测结果

### 8.2 性能验收标准
1. ✅ 系统加载时间 < 10秒
2. ✅ API响应时间 < 2秒
3. ✅ 图表交互响应时间 < 500ms
4. ✅ 支持并发用户数 ≥ 10

### 8.3 用户体验验收标准
1. ✅ 界面布局清晰，信息层次分明
2. ✅ 交互操作直观易懂
3. ✅ 错误提示友好明确
4. ✅ 响应式设计适配不同设备

## 9. 风险评估与应对

### 9.1 技术风险
- **数据质量问题**: 建立数据验证机制
- **模型性能不佳**: 准备多种模型方案
- **前端性能问题**: 优化图表渲染和数据处理

### 9.2 时间风险
- **开发进度延迟**: 合理分配任务优先级
- **集成问题**: 提前进行接口对接测试

### 9.3 用户体验风险
- **界面复杂度**: 简化操作流程
- **学习成本**: 提供详细的使用说明

## 10. 后续扩展计划

### 10.1 功能扩展
- 支持多日期预测
- 增加更多机器学习模型选择
- 添加预测准确性评估功能
- 支持实时数据更新

### 10.2 技术扩展
- 数据库集成
- 用户权限管理
- 云端部署
- 移动端适配

---

**文档版本**: v1.0  
**创建日期**: 2025-01-04  
**最后更新**: 2025-01-04  
**负责人**: 开发团队  
**审核人**: 产品经理
