"""
用户相关数据模型
User Related Data Models
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class UserData(BaseModel):
    """用户基础数据模型"""
    user_id: str = Field(..., description="用户唯一标识")
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    session_id: str = Field(..., description="会话唯一标识")
    login_time: datetime = Field(..., description="登录时间")


class UserAdjustment(BaseModel):
    """用户调整记录模型"""
    id: str = Field(..., description="调整记录唯一标识")
    hour: int = Field(..., ge=0, le=23, description="调整的小时")
    original_value: float = Field(..., description="原始预测值")
    adjusted_value: float = Field(..., description="调整后的值")
    timestamp: datetime = Field(..., description="调整时间")
    decision_id: Optional[str] = Field(None, description="关联的决策ID")


class UserInteraction(BaseModel):
    """用户交互记录模型"""
    id: str = Field(..., description="交互记录唯一标识")
    type: Literal['page_view', 'component_interaction', 'decision_action'] = Field(..., description="交互类型")
    component: Optional[str] = Field(None, description="交互的组件名称")
    action: Optional[str] = Field(None, description="具体的交互动作")
    timestamp: datetime = Field(..., description="交互时间")
    duration: Optional[int] = Field(None, description="交互持续时间（毫秒）")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外的元数据")


class Decision(BaseModel):
    """决策记录模型"""
    id: str = Field(..., description="决策唯一标识")
    label: str = Field(..., min_length=10, description="决策标题")
    reason: str = Field(..., min_length=10, description="决策理由")
    status: Literal['active', 'completed', 'disabled'] = Field(..., description="决策状态")
    adjustments: List[UserAdjustment] = Field(default_factory=list, description="相关的调整记录")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class UserExperimentData(BaseModel):
    """用户实验数据模型"""
    user_id: str = Field(..., description="用户唯一标识")
    username: str = Field(..., description="用户名")
    session_id: str = Field(..., description="会话唯一标识")
    start_time: datetime = Field(..., description="实验开始时间")
    decisions: List[Decision] = Field(default_factory=list, description="决策记录列表")
    adjustments: List[UserAdjustment] = Field(default_factory=list, description="调整记录列表")
    interactions: List[UserInteraction] = Field(default_factory=list, description="交互记录列表")
    completion_time: Optional[datetime] = Field(None, description="实验完成时间")
    status: Literal['in_progress', 'completed'] = Field(default='in_progress', description="实验状态")


class ExperimentSummary(BaseModel):
    """实验摘要模型"""
    total_decisions: int = Field(..., description="总决策数")
    total_adjustments: int = Field(..., description="总调整数")
    total_interactions: int = Field(..., description="总交互数")
    experiment_duration: int = Field(..., description="实验持续时间（分钟）")
    status: Literal['in_progress', 'completed'] = Field(..., description="实验状态")
    adjustment_statistics: Dict[str, Any] = Field(..., description="调整统计信息")


class UserLoginRequest(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")


class UserLoginResponse(BaseModel):
    """用户登录响应模型"""
    user_data: UserData = Field(..., description="用户数据")
    session_info: Dict[str, Any] = Field(..., description="会话信息")


class ExperimentSubmissionRequest(BaseModel):
    """实验提交请求模型"""
    experiment_data: UserExperimentData = Field(..., description="完整的实验数据")


class ExperimentSubmissionResponse(BaseModel):
    """实验提交响应模型"""
    submission_id: str = Field(..., description="提交记录唯一标识")
    submitted_at: datetime = Field(..., description="提交时间")
    experiment_summary: ExperimentSummary = Field(..., description="实验摘要")


class UserSessionInfo(BaseModel):
    """用户会话信息模型"""
    session_id: str = Field(..., description="会话唯一标识")
    user_id: str = Field(..., description="用户唯一标识")
    username: str = Field(..., description="用户名")
    login_time: datetime = Field(..., description="登录时间")
    last_activity: datetime = Field(..., description="最后活动时间")
    is_active: bool = Field(..., description="会话是否活跃")
    experiment_status: Literal['not_started', 'in_progress', 'completed'] = Field(..., description="实验状态")


class ExperimentDataExportRequest(BaseModel):
    """实验数据导出请求模型"""
    user_ids: Optional[List[str]] = Field(None, description="指定用户ID列表，为空则导出所有用户")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    format: Literal['json', 'csv', 'excel'] = Field(default='json', description="导出格式")
    include_interactions: bool = Field(default=True, description="是否包含交互记录")


class ExperimentDataExportResponse(BaseModel):
    """实验数据导出响应模型"""
    export_id: str = Field(..., description="导出任务唯一标识")
    total_users: int = Field(..., description="导出的用户总数")
    total_experiments: int = Field(..., description="导出的实验总数")
    file_size: int = Field(..., description="文件大小（字节）")
    download_url: str = Field(..., description="下载链接")
    expires_at: datetime = Field(..., description="下载链接过期时间")


# 用于API响应的通用模型
class UserApiResponse(BaseModel):
    """用户API通用响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


# 错误响应模型
class UserErrorResponse(BaseModel):
    """用户API错误响应模型"""
    success: bool = Field(default=False, description="操作是否成功")
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
