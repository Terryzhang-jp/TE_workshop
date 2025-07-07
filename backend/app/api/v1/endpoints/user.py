"""
用户管理相关API端点
User Management Related API Endpoints
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from datetime import datetime, timedelta
import logging
import uuid
import json
import os

from app.models.schemas import (
    UserSession, UserDecision, UserAdjustment, ExperimentResult, PredictionResult
)
from app.models.responses import StandardResponse
from app.utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES
from app.api.deps import get_logger

logger = logging.getLogger("power_prediction")
router = APIRouter()

# 用户会话存储（简单的内存存储，生产环境应使用数据库）
user_sessions: Dict[str, UserSession] = {}
user_experiments: Dict[str, Dict[str, Any]] = {}

# 实验结果存储目录
EXPERIMENT_RESULTS_DIR = "experiment_results"
os.makedirs(EXPERIMENT_RESULTS_DIR, exist_ok=True)


@router.post("/login", response_model=StandardResponse[UserSession])
async def user_login(
    username: str = Body(..., description="用户名"),
    logger: logging.Logger = Depends(get_logger)
):
    """
    用户登录/创建会话
    
    - **username**: 用户名
    """
    try:
        logger.info(f"API请求: 用户登录 用户名={username}")
        
        if not username or len(username.strip()) < 2:
            raise HTTPException(status_code=400, detail="用户名至少需要2个字符")
        
        username = username.strip()
        user_id = f"user_{username}_{int(datetime.now().timestamp())}"
        session_id = str(uuid.uuid4())
        
        # 创建用户会话
        user_session = UserSession(
            user_id=user_id,
            username=username,
            session_id=session_id,
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        # 存储会话
        user_sessions[session_id] = user_session
        
        # 初始化用户实验数据
        user_experiments[session_id] = {
            "user_session": user_session,
            "decisions": [],
            "adjustments": [],
            "experiment_start_time": datetime.now(),
            "final_predictions": []
        }
        
        logger.info(f"用户会话创建成功: {user_id}")
        
        return StandardResponse(
            success=True,
            data=user_session,
            message="用户登录成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/session/{session_id}", response_model=StandardResponse[UserSession])
async def get_user_session(
    session_id: str,
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取用户会话信息
    
    - **session_id**: 会话ID
    """
    try:
        logger.info(f"API请求: 获取用户会话 会话ID={session_id}")
        
        if session_id not in user_sessions:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        user_session = user_sessions[session_id]
        
        # 更新最后活跃时间
        user_session.last_active = datetime.now()
        
        return StandardResponse(
            success=True,
            data=user_session,
            message="会话信息获取成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/decision", response_model=StandardResponse[UserDecision])
async def create_user_decision(
    session_id: str = Body(..., description="会话ID"),
    label: str = Body(..., description="决策标签"),
    reason: str = Body(..., description="决策理由"),
    logger: logging.Logger = Depends(get_logger)
):
    """
    创建用户决策
    
    - **session_id**: 会话ID
    - **label**: 决策标签
    - **reason**: 决策理由
    """
    try:
        logger.info(f"API请求: 创建用户决策 会话ID={session_id}")
        
        if session_id not in user_experiments:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        if not label or len(label.strip()) < 10:
            raise HTTPException(status_code=400, detail="决策标签至少需要10个字符")
        
        if not reason or len(reason.strip()) < 10:
            raise HTTPException(status_code=400, detail="决策理由至少需要10个字符")
        
        decision_id = f"decision_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # 创建决策
        user_decision = UserDecision(
            decision_id=decision_id,
            label=label.strip(),
            reason=reason.strip(),
            status="active",
            created_at=datetime.now()
        )
        
        # 将之前的决策设为完成状态
        for decision in user_experiments[session_id]["decisions"]:
            if decision.status == "active":
                decision.status = "completed"
                decision.completed_at = datetime.now()
        
        # 添加新决策
        user_experiments[session_id]["decisions"].append(user_decision)
        
        logger.info(f"用户决策创建成功: {decision_id}")
        
        return StandardResponse(
            success=True,
            data=user_decision,
            message="决策创建成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建用户决策失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/adjustment", response_model=StandardResponse[UserAdjustment])
async def create_user_adjustment(
    session_id: str = Body(..., description="会话ID"),
    decision_id: str = Body(..., description="决策ID"),
    hour: int = Body(..., description="调整的小时"),
    original_value: float = Body(..., description="原始值"),
    adjusted_value: float = Body(..., description="调整后的值"),
    logger: logging.Logger = Depends(get_logger)
):
    """
    创建用户调整
    
    - **session_id**: 会话ID
    - **decision_id**: 决策ID
    - **hour**: 调整的小时
    - **original_value**: 原始值
    - **adjusted_value**: 调整后的值
    """
    try:
        logger.info(f"API请求: 创建用户调整 会话ID={session_id}, 小时={hour}")
        
        if session_id not in user_experiments:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        if not (0 <= hour <= 23):
            raise HTTPException(status_code=400, detail="小时必须在0-23之间")
        
        adjustment_id = f"adj_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # 创建调整
        user_adjustment = UserAdjustment(
            adjustment_id=adjustment_id,
            decision_id=decision_id,
            hour=hour,
            original_value=original_value,
            adjusted_value=adjusted_value,
            timestamp=datetime.now()
        )
        
        # 移除同一小时的之前调整
        user_experiments[session_id]["adjustments"] = [
            adj for adj in user_experiments[session_id]["adjustments"] 
            if adj.hour != hour
        ]
        
        # 添加新调整
        user_experiments[session_id]["adjustments"].append(user_adjustment)
        
        logger.info(f"用户调整创建成功: {adjustment_id}")
        
        return StandardResponse(
            success=True,
            data=user_adjustment,
            message="调整创建成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建用户调整失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/complete-experiment", response_model=StandardResponse[ExperimentResult])
async def complete_experiment(
    session_id: str = Body(..., description="会话ID"),
    final_predictions: List[Dict[str, Any]] = Body(..., description="最终预测结果"),
    logger: logging.Logger = Depends(get_logger)
):
    """
    完成实验并保存结果
    
    - **session_id**: 会话ID
    - **final_predictions**: 最终预测结果
    """
    try:
        logger.info(f"API请求: 完成实验 会话ID={session_id}")
        
        if session_id not in user_experiments:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        experiment_data = user_experiments[session_id]
        user_session = experiment_data["user_session"]
        
        # 转换预测结果
        prediction_results = [PredictionResult(**pred) for pred in final_predictions]
        
        # 计算实验持续时间
        experiment_end_time = datetime.now()
        duration = (experiment_end_time - experiment_data["experiment_start_time"]).total_seconds() / 60
        
        # 创建实验结果
        experiment_result = ExperimentResult(
            user_id=user_session.user_id,
            username=user_session.username,
            session_id=session_id,
            experiment_start_time=experiment_data["experiment_start_time"],
            experiment_end_time=experiment_end_time,
            decisions=experiment_data["decisions"],
            adjustments=experiment_data["adjustments"],
            final_predictions=prediction_results,
            experiment_duration_minutes=duration
        )
        
        # 保存到文件
        result_filename = f"{EXPERIMENT_RESULTS_DIR}/experiment_{user_session.username}_{session_id[:8]}_{int(experiment_end_time.timestamp())}.json"
        
        with open(result_filename, 'w', encoding='utf-8') as f:
            json.dump(experiment_result.dict(), f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"实验结果保存成功: {result_filename}")
        
        # 清理会话数据
        if session_id in user_sessions:
            del user_sessions[session_id]
        if session_id in user_experiments:
            del user_experiments[session_id]
        
        return StandardResponse(
            success=True,
            data=experiment_result,
            message="实验完成，结果已保存"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"完成实验失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/experiment-results", response_model=StandardResponse[List[str]])
async def list_experiment_results(
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取所有实验结果文件列表
    """
    try:
        logger.info("API请求: 获取实验结果列表")
        
        result_files = []
        if os.path.exists(EXPERIMENT_RESULTS_DIR):
            result_files = [f for f in os.listdir(EXPERIMENT_RESULTS_DIR) if f.endswith('.json')]
        
        return StandardResponse(
            success=True,
            data=result_files,
            message=f"找到 {len(result_files)} 个实验结果文件"
        )
        
    except Exception as e:
        logger.error(f"获取实验结果列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")
