"""
响应模型定义
Response Model Definitions
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from .schemas import (
    HistoricalDataPoint, PredictionResult, ModelMetrics, 
    FeatureImportance, SHAPValue, LIMEExplanation, 
    ContextInfo, TrainingInfo
)

T = TypeVar('T')


class StandardResponse(GenericModel, Generic[T]):
    """标准响应格式"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[T] = Field(None, description="响应数据")
    message: str = Field(..., description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorDetail(BaseModel):
    """错误详情模型"""
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详细信息")


class ErrorResponse(BaseModel):
    """错误响应格式"""
    success: bool = Field(False, description="请求是否成功")
    error: ErrorDetail = Field(..., description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DataResponse(BaseModel):
    """数据响应模型"""
    historical_data: List[HistoricalDataPoint] = Field(..., description="历史数据")
    total_count: int = Field(..., description="数据总数")
    date_range: tuple[datetime, datetime] = Field(..., description="数据时间范围")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PredictionResponse(BaseModel):
    """预测响应模型"""
    predictions: List[PredictionResult] = Field(..., description="预测结果列表")
    model_metrics: ModelMetrics = Field(..., description="模型评估指标")
    training_info: TrainingInfo = Field(..., description="训练信息")
    target_date: str = Field(..., description="预测目标日期")


class ExplanationResponse(BaseModel):
    """可解释性分析响应模型"""
    feature_importance: List[FeatureImportance] = Field(..., description="特征重要性")
    shap_values: List[SHAPValue] = Field(..., description="SHAP值分析")
    lime_explanations: List[LIMEExplanation] = Field(..., description="LIME解释")
    global_explanation: Dict[str, Any] = Field(..., description="全局解释信息")


class AdjustmentResponse(BaseModel):
    """调整响应模型"""
    adjusted_predictions: List[PredictionResult] = Field(..., description="调整后的预测")
    adjustment_summary: Dict[str, Any] = Field(..., description="调整摘要")
    original_predictions: List[PredictionResult] = Field(..., description="原始预测")


class ContextInfoResponse(BaseModel):
    """情景信息响应模型"""
    context_data: List[ContextInfo] = Field(..., description="情景信息数据")
    date_range: tuple[str, str] = Field(..., description="日期范围")


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="检查时间")
    version: str = Field(..., description="应用版本")
    dependencies: Dict[str, bool] = Field(..., description="依赖服务状态")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExportResponse(BaseModel):
    """导出响应模型"""
    download_url: str = Field(..., description="下载链接")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    export_time: datetime = Field(default_factory=datetime.utcnow, description="导出时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
