# 电力需求预测系统 API 文档

## 概述

电力需求预测系统提供基于机器学习的电力需求预测与可解释性分析功能。本API采用RESTful设计，支持JSON格式的数据交换。

## 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **API版本**: v1
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

当前版本暂不需要认证，所有端点均可直接访问。

## 响应格式

所有API响应都遵循统一的格式：

```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

### 错误响应

```json
{
  "success": false,
  "message": "错误描述",
  "error_type": "ErrorType"
}
```

## API 端点

### 1. 数据管理 (`/data`)

#### 1.1 获取历史数据

**GET** `/data/historical`

获取指定时间范围内的历史电力使用数据。

**查询参数:**
- `start_date` (可选): 开始日期，格式 YYYY-MM-DD
- `end_date` (可选): 结束日期，格式 YYYY-MM-DD
- `include_features` (可选): 是否包含特征工程后的数据，默认 true

**响应示例:**
```json
{
  "success": true,
  "data": {
    "historical_data": [
      {
        "timestamp": "2024-01-01T00:00:00",
        "temperature": 25.0,
        "usage": 100.0,
        "hour": 0,
        "day_of_week": 0
      }
    ],
    "total_count": 1,
    "statistics": {
      "temp": {"mean": 25.0, "std": 5.0},
      "usage": {"mean": 100.0, "std": 20.0}
    },
    "data_quality": {
      "quality_score": 95.0,
      "quality_level": "excellent"
    }
  }
}
```

#### 1.2 获取情景信息

**GET** `/data/context-info`

获取特定日期的情景信息，包括天气、节假日等影响因素。

**查询参数:**
- `start_date` (可选): 开始日期
- `end_date` (可选): 结束日期

#### 1.3 验证数据文件

**POST** `/data/validate`

验证上传的数据文件格式和质量。

**请求体:**
```json
{
  "file_path": "path/to/data.csv"
}
```

#### 1.4 获取数据摘要

**GET** `/data/summary`

获取当前加载数据的摘要信息。

#### 1.5 导出数据

**GET** `/data/export`

导出指定类型的数据。

**查询参数:**
- `data_type`: 数据类型 (historical, context)
- `format`: 导出格式 (csv, json)
- `start_date` (可选): 开始日期
- `end_date` (可选): 结束日期

### 2. 预测管理 (`/prediction`)

#### 2.1 训练模型

**POST** `/prediction/train`

训练新的预测模型。

**请求体:**
```json
{
  "target_date": "2024-01-01",
  "weeks_before": 3,
  "validation_split": 0.2,
  "model_params": {},
  "force_retrain": false
}
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "training_completed": true,
    "target_date": "2024-01-01",
    "training_time": 120.5,
    "model_path": "/path/to/model.joblib",
    "training_metrics": {
      "mae": 10.5,
      "rmse": 15.2,
      "r2_score": 0.85
    }
  }
}
```

#### 2.2 获取预测结果

**GET** `/prediction/`

获取指定日期的24小时电力需求预测。

**查询参数:**
- `target_date` (可选): 目标日期，格式 YYYY-MM-DD
- `temperature_forecast` (可选): 24小时温度预报，逗号分隔
- `use_cache` (可选): 是否使用缓存，默认 true

**响应示例:**
```json
{
  "success": true,
  "data": {
    "predictions": [
      {
        "hour": 0,
        "predicted_usage": 95.5,
        "confidence_interval": [85.0, 105.0],
        "original_prediction": 95.5
      }
    ],
    "model_metrics": {
      "mae": 10.5,
      "rmse": 15.2,
      "r2_score": 0.85
    },
    "target_date": "2024-01-01"
  }
}
```

#### 2.3 获取单小时预测

**GET** `/prediction/hourly`

获取指定时间点的单小时预测。

**查询参数:**
- `target_datetime`: 目标时间，格式 YYYY-MM-DD HH:MM:SS
- `temperature`: 温度，默认 25.0

#### 2.4 批量预测

**POST** `/prediction/batch`

批量预测多个时间点的电力需求。

**请求体:**
```json
[
  {
    "datetime": "2024-01-01T10:00:00",
    "temperature": 25.0
  },
  {
    "datetime": "2024-01-01T11:00:00",
    "temperature": 26.0
  }
]
```

#### 2.5 获取模型指标

**GET** `/prediction/metrics`

获取当前模型的评估指标。

#### 2.6 加载预训练模型

**POST** `/prediction/load-model`

加载已保存的预训练模型。

**请求体:**
```json
"/path/to/model.joblib"
```

### 3. 可解释性分析 (`/explanation`)

#### 3.1 初始化解释服务

**POST** `/explanation/initialize`

初始化SHAP和LIME解释器。

**请求体:**
```json
{
  "background_data": [[25.0, 0, 1], [26.0, 1, 2]],
  "training_data": [[25.0, 0, 1], [26.0, 1, 2]]
}
```

#### 3.2 获取SHAP分析

**GET** `/explanation/shap`

获取SHAP可解释性分析结果。

**查询参数:**
- `analysis_type`: 分析类型 (global, local, hourly)
- `instances` (可选): 实例数据，JSON格式
- `hours` (可选): 小时列表，逗号分隔

#### 3.3 获取LIME分析

**POST** `/explanation/lime`

获取LIME可解释性分析结果。

**请求体:**
```json
{
  "instances": [[25.0, 0, 1], [26.0, 1, 2]],
  "analysis_type": "single",
  "hours": [0, 1],
  "num_features": 4
}
```

#### 3.4 获取特征重要性

**GET** `/explanation/feature-importance`

获取模型特征重要性分析。

#### 3.5 获取综合解释

**POST** `/explanation/comprehensive`

获取综合的可解释性分析（SHAP + LIME）。

### 4. 预测调整 (`/adjustment`)

#### 4.1 应用全局调整

**POST** `/adjustment/global`

对预测结果应用全局调整。

**请求体:**
```json
{
  "predictions": [
    {
      "hour": 0,
      "predicted_usage": 100.0,
      "confidence_interval": [90.0, 110.0]
    }
  ],
  "adjustment": {
    "start_hour": 9,
    "end_hour": 17,
    "direction": "increase",
    "percentage": 10.0
  },
  "save_original": true
}
```

#### 4.2 应用局部调整

**POST** `/adjustment/local`

对特定时间点应用局部调整。

**请求体:**
```json
{
  "predictions": [...],
  "adjustments": [
    {
      "hour": 10,
      "new_value": 120.0
    }
  ],
  "save_original": true
}
```

#### 4.3 应用混合调整

**POST** `/adjustment/mixed`

同时应用全局和局部调整。

#### 4.4 重置调整

**POST** `/adjustment/reset`

重置所有调整，恢复到原始预测。

#### 4.5 优化调整参数

**POST** `/adjustment/optimize`

自动优化调整参数以达到目标总量。

**请求体:**
```json
{
  "predictions": [...],
  "target_total": 2500.0,
  "adjustment_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17]
}
```

#### 4.6 获取调整历史

**GET** `/adjustment/history`

获取调整操作历史记录。

**查询参数:**
- `adjustment_type`: 调整类型 (all, global, local)

## 状态码

- `200`: 成功
- `400`: 请求错误
- `404`: 资源未找到
- `422`: 参数验证失败
- `500`: 服务器内部错误

## 错误类型

- `DataLoadError`: 数据加载错误
- `DataValidationError`: 数据验证错误
- `ModelTrainingError`: 模型训练错误
- `ModelNotFoundError`: 模型未找到错误
- `PredictionError`: 预测错误
- `ExplanationError`: 解释错误
- `AdjustmentError`: 调整错误

## 使用示例

### Python 示例

```python
import requests

# 基础URL
base_url = "http://localhost:8000/api/v1"

# 获取历史数据
response = requests.get(f"{base_url}/data/historical")
data = response.json()

# 训练模型
train_data = {
    "target_date": "2024-01-01",
    "weeks_before": 3
}
response = requests.post(f"{base_url}/prediction/train", json=train_data)

# 获取预测
response = requests.get(f"{base_url}/prediction/?target_date=2024-01-01")
predictions = response.json()
```

### JavaScript 示例

```javascript
// 获取预测结果
fetch('http://localhost:8000/api/v1/prediction/?target_date=2024-01-01')
  .then(response => response.json())
  .then(data => {
    console.log('预测结果:', data.data.predictions);
  });

// 应用调整
const adjustmentData = {
  predictions: predictions,
  adjustment: {
    start_hour: 9,
    end_hour: 17,
    direction: "increase",
    percentage: 10.0
  }
};

fetch('http://localhost:8000/api/v1/adjustment/global', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(adjustmentData)
})
.then(response => response.json())
.then(data => {
  console.log('调整结果:', data);
});
```

## 健康检查

### 系统健康检查

**GET** `/health`

检查整个系统的健康状态。

### 服务健康检查

- **GET** `/data/health` - 数据服务健康检查
- **GET** `/prediction/health` - 预测服务健康检查
- **GET** `/explanation/health` - 解释服务健康检查
- **GET** `/adjustment/health` - 调整服务健康检查

## 限制和注意事项

1. **数据大小限制**: 单次请求的数据量不应超过10MB
2. **并发限制**: 同时进行的模型训练任务不超过1个
3. **缓存策略**: 预测结果默认缓存1小时
4. **温度预报**: 必须提供完整的24小时数据
5. **调整范围**: 调整百分比限制在-50%到+50%之间

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持基础的数据管理、预测、解释和调整功能
