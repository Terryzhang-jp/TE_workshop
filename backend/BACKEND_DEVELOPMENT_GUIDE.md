# 电力需求预测系统后端开发文档

## 1. 项目概述

### 1.1 技术架构
本项目采用现代化的分层架构设计，确保代码的可维护性、可扩展性和可测试性。

**核心技术栈**:
- **框架**: FastAPI 0.104+
- **Python版本**: 3.9+
- **机器学习**: XGBoost, scikit-learn
- **可解释性**: SHAP, LIME
- **数据处理**: Pandas, NumPy
- **异步支持**: asyncio, aiofiles
- **配置管理**: Pydantic Settings
- **日志**: structlog
- **测试**: pytest, pytest-asyncio
- **文档**: Swagger/OpenAPI 自动生成

### 1.2 架构设计原则
- **单一职责原则**: 每个模块只负责一个功能领域
- **依赖注入**: 使用依赖注入模式提高可测试性
- **配置外部化**: 所有配置通过环境变量管理
- **错误处理统一**: 统一的异常处理和错误响应格式
- **API版本控制**: 支持API版本管理
- **异步优先**: 充分利用Python异步特性

## 2. 项目结构设计

```
backend/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── main.py                   # FastAPI应用入口
│   ├── config/                   # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py           # 应用配置
│   │   └── logging.py            # 日志配置
│   ├── api/                      # API层
│   │   ├── __init__.py
│   │   ├── deps.py               # 依赖注入
│   │   ├── middleware.py         # 中间件
│   │   └── v1/                   # API v1版本
│   │       ├── __init__.py
│   │       ├── router.py         # 主路由
│   │       └── endpoints/        # 端点实现
│   │           ├── __init__.py
│   │           ├── data.py       # 数据相关API
│   │           ├── prediction.py # 预测相关API
│   │           ├── explanation.py# 可解释性API
│   │           └── adjustment.py # 调整相关API
│   ├── core/                     # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── data/                 # 数据处理模块
│   │   │   ├── __init__.py
│   │   │   ├── loader.py         # 数据加载
│   │   │   ├── processor.py      # 数据处理
│   │   │   └── validator.py      # 数据验证
│   │   ├── ml/                   # 机器学习模块
│   │   │   ├── __init__.py
│   │   │   ├── model.py          # 模型定义
│   │   │   ├── trainer.py        # 模型训练
│   │   │   └── predictor.py      # 预测服务
│   │   ├── explanation/          # 可解释性模块
│   │   │   ├── __init__.py
│   │   │   ├── shap_analyzer.py  # SHAP分析
│   │   │   └── lime_analyzer.py  # LIME分析
│   │   └── adjustment/           # 预测调整模块
│   │       ├── __init__.py
│   │       ├── global_adjuster.py# 全局调整
│   │       └── local_adjuster.py # 局部调整
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── schemas.py            # Pydantic模型
│   │   └── responses.py          # 响应模型
│   ├── services/                 # 服务层
│   │   ├── __init__.py
│   │   ├── data_service.py       # 数据服务
│   │   ├── prediction_service.py # 预测服务
│   │   ├── explanation_service.py# 解释服务
│   │   └── adjustment_service.py # 调整服务
│   └── utils/                    # 工具模块
│       ├── __init__.py
│       ├── exceptions.py         # 自定义异常
│       ├── helpers.py            # 辅助函数
│       └── constants.py          # 常量定义
├── data/                         # 数据目录
│   ├── raw/                      # 原始数据
│   ├── processed/                # 处理后数据
│   └── models/                   # 训练好的模型
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── conftest.py               # pytest配置
│   ├── unit/                     # 单元测试
│   └── integration/              # 集成测试
├── scripts/                      # 脚本目录
│   ├── train_model.py            # 模型训练脚本
│   └── data_preprocessing.py     # 数据预处理脚本
├── requirements/                 # 依赖管理
│   ├── base.txt                  # 基础依赖
│   ├── dev.txt                   # 开发依赖
│   └── prod.txt                  # 生产依赖
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git忽略文件
├── Dockerfile                    # Docker配置
├── docker-compose.yml            # Docker Compose配置
├── pyproject.toml                # 项目配置
└── README.md                     # 项目说明
```

## 3. API设计规范

### 3.1 RESTful API设计
```python
# API路由设计
/api/v1/data/
├── GET /historical              # 获取历史数据
├── GET /context-info           # 获取情景信息
└── GET /export                 # 导出数据

/api/v1/prediction/
├── GET /                       # 获取预测结果
├── POST /train                 # 训练模型
└── GET /metrics               # 获取模型指标

/api/v1/explanation/
├── GET /shap                   # 获取SHAP分析
├── GET /lime                   # 获取LIME分析
└── GET /feature-importance     # 获取特征重要性

/api/v1/adjustment/
├── POST /global                # 全局调整
├── POST /local                 # 局部调整
└── POST /reset                 # 重置调整

/api/v1/export/
└── GET /results                # 导出结果
```

### 3.2 统一响应格式
```python
# 成功响应格式
{
    "success": true,
    "data": {...},
    "message": "操作成功",
    "timestamp": "2025-01-04T10:00:00Z"
}

# 错误响应格式
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "输入数据验证失败",
        "details": {...}
    },
    "timestamp": "2025-01-04T10:00:00Z"
}
```

### 3.3 HTTP状态码规范
- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未授权
- `403 Forbidden`: 禁止访问
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

## 4. 数据模型设计

### 4.1 核心数据模型
```python
# 历史数据模型
class HistoricalDataPoint(BaseModel):
    timestamp: datetime
    temperature: float
    usage: float
    hour: int
    day_of_week: int
    week_of_month: int

# 预测结果模型
class PredictionResult(BaseModel):
    hour: int
    predicted_usage: float
    confidence_interval: Tuple[float, float]
    original_prediction: Optional[float] = None

# 调整参数模型
class GlobalAdjustment(BaseModel):
    start_hour: int = Field(ge=0, le=23)
    end_hour: int = Field(ge=0, le=23)
    direction: Literal["increase", "decrease"]
    percentage: float = Field(gt=0, le=100)

class LocalAdjustment(BaseModel):
    hour: int = Field(ge=0, le=23)
    new_value: float = Field(gt=0)
```

### 4.2 响应模型
```python
class DataResponse(BaseModel):
    historical_data: List[HistoricalDataPoint]
    total_count: int
    date_range: Tuple[datetime, datetime]

class PredictionResponse(BaseModel):
    predictions: List[PredictionResult]
    model_metrics: Dict[str, float]
    training_info: Dict[str, Any]

class ExplanationResponse(BaseModel):
    feature_importance: Dict[str, float]
    shap_values: List[Dict[str, Any]]
    lime_explanation: Dict[str, Any]
```

## 5. 服务层设计

### 5.1 数据服务 (DataService)
```python
class DataService:
    async def load_historical_data(self, start_date: datetime, end_date: datetime) -> List[HistoricalDataPoint]
    async def get_context_info(self, date: datetime) -> Dict[str, Any]
    async def validate_data(self, data: List[HistoricalDataPoint]) -> bool
    async def export_data(self, format: str = "csv") -> bytes
```

### 5.2 预测服务 (PredictionService)
```python
class PredictionService:
    async def train_model(self, training_data: List[HistoricalDataPoint]) -> Dict[str, Any]
    async def predict(self, target_date: datetime) -> List[PredictionResult]
    async def get_model_metrics(self) -> Dict[str, float]
    async def load_model(self, model_path: str) -> None
```

### 5.3 解释服务 (ExplanationService)
```python
class ExplanationService:
    async def generate_shap_analysis(self, model, data: np.ndarray) -> Dict[str, Any]
    async def generate_lime_analysis(self, model, instance: np.ndarray) -> Dict[str, Any]
    async def get_feature_importance(self, model) -> Dict[str, float]
```

### 5.4 调整服务 (AdjustmentService)
```python
class AdjustmentService:
    async def apply_global_adjustment(self, predictions: List[PredictionResult], adjustment: GlobalAdjustment) -> List[PredictionResult]
    async def apply_local_adjustment(self, predictions: List[PredictionResult], adjustments: List[LocalAdjustment]) -> List[PredictionResult]
    async def reset_adjustments(self, original_predictions: List[PredictionResult]) -> List[PredictionResult]
```

## 6. 配置管理

### 6.1 环境配置
```python
class Settings(BaseSettings):
    # 应用配置
    app_name: str = "电力需求预测系统"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 数据配置
    data_file_path: str = "data/raw/temp_usage_data.csv"
    model_save_path: str = "data/models/"
    
    # 机器学习配置
    xgboost_params: Dict[str, Any] = {
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1,
        "random_state": 42
    }
    
    # API配置
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
```

## 7. 错误处理和日志

### 7.1 自定义异常
```python
class BaseAPIException(Exception):
    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code

class DataValidationError(BaseAPIException):
    def __init__(self, message: str):
        super().__init__(message, "DATA_VALIDATION_ERROR", 422)

class ModelTrainingError(BaseAPIException):
    def __init__(self, message: str):
        super().__init__(message, "MODEL_TRAINING_ERROR", 500)
```

### 7.2 全局异常处理
```python
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### 7.3 结构化日志
```python
import structlog

logger = structlog.get_logger()

# 使用示例
await logger.ainfo("模型训练开始", model_type="xgboost", data_size=504)
await logger.aerror("数据验证失败", error=str(e), file_path=file_path)
```

## 8. 中间件设计

### 8.1 CORS中间件
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8.2 请求日志中间件
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        "请求处理完成",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    return response
```

## 9. 测试策略

### 9.1 单元测试
```python
# 测试数据服务
@pytest.mark.asyncio
async def test_load_historical_data():
    service = DataService()
    start_date = datetime(2022, 6, 9)
    end_date = datetime(2022, 6, 29)
    
    data = await service.load_historical_data(start_date, end_date)
    
    assert len(data) == 504  # 21天 * 24小时
    assert all(isinstance(point, HistoricalDataPoint) for point in data)
```

### 9.2 集成测试
```python
# 测试完整的预测流程
@pytest.mark.asyncio
async def test_prediction_workflow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 训练模型
        response = await ac.post("/api/v1/prediction/train")
        assert response.status_code == 200
        
        # 获取预测
        response = await ac.get("/api/v1/prediction/")
        assert response.status_code == 200
        assert len(response.json()["data"]["predictions"]) == 24
```

## 10. 部署配置

### 10.1 Docker配置
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements/prod.txt .
RUN pip install -r prod.txt

COPY app/ ./app/
COPY data/ ./data/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 10.2 Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## 11. 开发流程

### 11.1 开发环境设置
1. 创建虚拟环境: `python -m venv venv`
2. 激活虚拟环境: `source venv/bin/activate`
3. 安装依赖: `pip install -r requirements/dev.txt`
4. 复制环境配置: `cp .env.example .env`
5. 运行开发服务器: `uvicorn app.main:app --reload`

### 11.2 代码质量保证
- **代码格式化**: black, isort
- **代码检查**: flake8, mypy
- **测试覆盖率**: pytest-cov
- **预提交钩子**: pre-commit

### 11.3 Git工作流
1. 功能分支开发
2. 代码审查
3. 自动化测试
4. 合并到主分支
5. 自动部署

## 12. 性能优化

### 12.1 异步处理
- 使用async/await处理I/O密集型操作
- 数据加载和模型训练使用异步处理
- API响应使用流式处理大数据

### 12.2 缓存策略
- 模型结果缓存
- 数据查询缓存
- API响应缓存

### 12.3 资源管理
- 连接池管理
- 内存使用优化
- 模型加载优化

## 13. 扩展性设计

### 13.1 用户认证预留
```python
# 用户模型预留
class User(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: datetime

# 认证中间件预留
class AuthMiddleware:
    async def authenticate_user(self, token: str) -> Optional[User]
    async def check_permissions(self, user: User, resource: str) -> bool
```

### 13.2 多租户支持预留
```python
# 租户模型
class Tenant(BaseModel):
    id: str
    name: str
    settings: Dict[str, Any]

# 租户上下文
class TenantContext:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    async def get_data_path(self) -> str:
        return f"data/tenants/{self.tenant_id}/"
```

### 13.3 插件系统预留
```python
# 插件接口
class ModelPlugin(ABC):
    @abstractmethod
    async def train(self, data: np.ndarray) -> Any:
        pass

    @abstractmethod
    async def predict(self, data: np.ndarray) -> np.ndarray:
        pass

# 插件管理器
class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, ModelPlugin] = {}

    def register_plugin(self, name: str, plugin: ModelPlugin):
        self.plugins[name] = plugin
```

## 14. 监控和运维

### 14.1 健康检查
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.app_version,
        "dependencies": {
            "model_loaded": model_manager.is_loaded(),
            "data_accessible": await data_service.check_data_access()
        }
    }
```

### 14.2 指标收集
```python
# Prometheus指标
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')
MODEL_PREDICTIONS = Counter('model_predictions_total', 'Total model predictions')
```

### 14.3 日志聚合
```python
# 结构化日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}
```

## 15. 安全考虑

### 15.1 输入验证
```python
# 严格的数据验证
class DataValidationService:
    @staticmethod
    def validate_file_upload(file: UploadFile) -> bool:
        # 文件类型检查
        if file.content_type not in ["text/csv", "application/csv"]:
            raise ValidationError("只支持CSV文件")

        # 文件大小检查
        if file.size > 100 * 1024 * 1024:  # 100MB
            raise ValidationError("文件大小不能超过100MB")

        return True
```

### 15.2 API限流
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/prediction/")
@limiter.limit("10/minute")
async def get_prediction(request: Request):
    # API实现
    pass
```

### 15.3 数据脱敏
```python
class DataMaskingService:
    @staticmethod
    def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        # 脱敏处理
        masked_data = data.copy()
        if "user_id" in masked_data:
            masked_data["user_id"] = "***"
        return masked_data
```

## 16. 开发检查清单

### 16.1 代码质量检查
- [ ] 所有函数都有类型注解
- [ ] 所有公共方法都有文档字符串
- [ ] 代码通过flake8检查
- [ ] 代码通过mypy类型检查
- [ ] 测试覆盖率 > 80%

### 16.2 API设计检查
- [ ] 所有API都有适当的HTTP状态码
- [ ] 所有API都有统一的响应格式
- [ ] 所有API都有适当的错误处理
- [ ] 所有API都有OpenAPI文档
- [ ] 所有API都有适当的验证

### 16.3 性能检查
- [ ] 数据库查询已优化
- [ ] 大数据处理使用流式处理
- [ ] 适当使用缓存
- [ ] API响应时间 < 2秒
- [ ] 内存使用合理

### 16.4 安全检查
- [ ] 输入数据已验证
- [ ] 敏感数据已脱敏
- [ ] API已实现限流
- [ ] 错误信息不泄露敏感信息
- [ ] 依赖包无已知漏洞

## 17. 部署和运维指南

### 17.1 生产环境部署
```bash
# 1. 构建Docker镜像
docker build -t power-prediction-backend:latest .

# 2. 运行容器
docker run -d \
  --name power-prediction-backend \
  -p 8000:8000 \
  -e DEBUG=false \
  -e LOG_LEVEL=INFO \
  -v /data:/app/data \
  power-prediction-backend:latest

# 3. 健康检查
curl http://localhost:8000/health
```

### 17.2 监控配置
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  backend:
    # ... 应用配置

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 17.3 备份策略
```bash
# 数据备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/power-prediction"

# 备份数据文件
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" /app/data/

# 备份模型文件
tar -czf "$BACKUP_DIR/models_$DATE.tar.gz" /app/data/models/

# 清理30天前的备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

---

**文档版本**: v1.0
**创建日期**: 2025-01-04
**最后更新**: 2025-01-04
**负责人**: 后端开发团队
**技术架构师**: AI Assistant
**审核状态**: 待审核

## 下一步行动

1. **确认架构设计** - 请审核本文档并确认技术方案
2. **环境准备** - 准备开发环境和依赖
3. **项目初始化** - 创建项目结构和基础配置
4. **模块开发** - 按照任务计划逐步实现各个模块
5. **测试验证** - 编写测试用例并验证功能
6. **文档完善** - 补充API文档和使用说明

**准备开始开发？请确认此架构设计方案！**
cd backend && source ve--reload --host 0.0.0.0 --port 8001n app.main:app 
cd frontend && npm run dev
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001