"""
数据模型定义
Data Model Definitions
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Literal
from pydantic import BaseModel, Field, validator


class HistoricalDataPoint(BaseModel):
    """历史数据点模型"""
    timestamp: datetime
    temperature: float = Field(..., description="温度（摄氏度）")
    usage: float = Field(..., description="电力使用量")
    hour: int = Field(..., ge=0, le=23, description="小时（0-23）")
    day_of_week: int = Field(..., ge=0, le=6, description="星期几（0-6）")
    week_of_month: int = Field(..., ge=1, le=5, description="月中第几周（1-5）")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PredictionResult(BaseModel):
    """预测结果模型"""
    hour: int = Field(..., ge=0, le=23, description="小时（0-23）")
    predicted_usage: float = Field(..., description="预测电力使用量")
    confidence_interval: Tuple[float, float] = Field(..., description="置信区间")
    original_prediction: Optional[float] = Field(None, description="原始预测值（调整前）")
    
    @validator('confidence_interval')
    def validate_confidence_interval(cls, v):
        if len(v) != 2:
            raise ValueError('置信区间必须包含两个值')
        if v[0] > v[1]:
            raise ValueError('置信区间下界不能大于上界')
        return v


class GlobalAdjustment(BaseModel):
    """全局调整参数模型"""
    start_hour: int = Field(..., ge=0, le=23, description="开始小时")
    end_hour: int = Field(..., ge=0, le=23, description="结束小时")
    direction: Literal["increase", "decrease"] = Field(..., description="调整方向")
    percentage: float = Field(..., gt=0, le=100, description="调整百分比")
    
    @validator('end_hour')
    def validate_hour_range(cls, v, values):
        if 'start_hour' in values and v < values['start_hour']:
            raise ValueError('结束小时不能小于开始小时')
        return v


class LocalAdjustment(BaseModel):
    """局部调整参数模型"""
    hour: int = Field(..., ge=0, le=23, description="调整的小时")
    new_value: float = Field(..., gt=0, description="新的预测值")


class ModelMetrics(BaseModel):
    """模型评估指标模型"""
    mae: float = Field(..., description="平均绝对误差")
    rmse: float = Field(..., description="均方根误差")
    r2_score: float = Field(..., description="R²决定系数")
    mape: float = Field(..., description="平均绝对百分比误差")


class FeatureImportance(BaseModel):
    """特征重要性模型"""
    feature_name: str = Field(..., description="特征名称")
    importance: float = Field(..., description="重要性分数")
    rank: int = Field(..., description="重要性排名")


class SHAPValue(BaseModel):
    """SHAP值模型"""
    hour: int = Field(..., ge=0, le=23, description="小时")
    feature_values: Dict[str, float] = Field(..., description="特征SHAP值")
    base_value: float = Field(..., description="基准值")
    prediction: float = Field(..., description="预测值")


class LIMEExplanation(BaseModel):
    """LIME解释模型"""
    hour: int = Field(..., ge=0, le=23, description="小时")
    feature_contributions: Dict[str, float] = Field(..., description="特征贡献度")
    intercept: float = Field(..., description="截距")
    r2_score: float = Field(..., description="局部模型R²分数")


class ContextInfo(BaseModel):
    """情景信息模型"""
    date: str = Field(..., description="日期")
    day_of_week: str = Field(..., description="星期几")
    temperature: float = Field(..., description="温度")
    demand_estimate: str = Field(..., description="需求估计")
    increase_percentage: str = Field(..., description="增长百分比")
    reserve_rate: Optional[str] = Field(None, description="余裕率")
    special_notes: str = Field(..., description="特殊说明")


class TrainingInfo(BaseModel):
    """训练信息模型"""
    training_start_date: datetime = Field(..., description="训练开始日期")
    training_end_date: datetime = Field(..., description="训练结束日期")
    training_samples: int = Field(..., description="训练样本数")
    model_type: str = Field(..., description="模型类型")
    training_time: float = Field(..., description="训练时间（秒）")
    model_params: Dict[str, Any] = Field(..., description="模型参数")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 用户管理相关模型
class UserSession(BaseModel):
    """用户会话模型"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    session_id: str = Field(..., description="会话ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    last_active: datetime = Field(default_factory=datetime.now, description="最后活跃时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserDecision(BaseModel):
    """用户决策模型"""
    decision_id: str = Field(..., description="决策ID")
    label: str = Field(..., description="决策标签")
    reason: str = Field(..., description="决策理由")
    status: Literal["active", "completed", "disabled"] = Field(..., description="决策状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserAdjustment(BaseModel):
    """用户调整模型"""
    adjustment_id: str = Field(..., description="调整ID")
    decision_id: str = Field(..., description="关联的决策ID")
    hour: int = Field(..., ge=0, le=23, description="调整的小时")
    original_value: float = Field(..., description="原始值")
    adjusted_value: float = Field(..., description="调整后的值")
    timestamp: datetime = Field(default_factory=datetime.now, description="调整时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExperimentResult(BaseModel):
    """实验结果模型"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    session_id: str = Field(..., description="会话ID")
    experiment_start_time: datetime = Field(..., description="实验开始时间")
    experiment_end_time: datetime = Field(..., description="实验结束时间")
    decisions: List[UserDecision] = Field(default_factory=list, description="用户决策列表")
    adjustments: List[UserAdjustment] = Field(default_factory=list, description="用户调整列表")
    final_predictions: List[PredictionResult] = Field(default_factory=list, description="最终预测结果")
    experiment_duration_minutes: Optional[float] = Field(None, description="实验持续时间（分钟）")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
