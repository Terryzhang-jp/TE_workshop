"""
用户管理API端点
User Management API Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from datetime import datetime
import logging

from app.services.user_service import UserService
from app.models.user_models import (
    UserLoginRequest, UserLoginResponse, UserSessionInfo,
    UserApiResponse, UserErrorResponse, ExperimentSubmissionRequest,
    ExperimentSubmissionResponse, UserExperimentData
)
from app.utils.exceptions import UserError, SessionError, DataStorageError
from app.utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES

logger = logging.getLogger("power_prediction")
router = APIRouter()

# 用户服务实例
user_service = UserService()


def get_session_id_from_header(x_session_id: Optional[str] = Header(None)) -> str:
    """从请求头获取会话ID"""
    if not x_session_id:
        raise HTTPException(status_code=401, detail="会话ID缺失")
    return x_session_id


@router.post("/login", response_model=UserApiResponse)
async def login_user(request: UserLoginRequest):
    """
    用户登录
    
    - **username**: 用户名（3-20个字符）
    """
    try:
        logger.info(f"API请求: 用户登录 - 用户名: {request.username}")
        
        response = await user_service.login_user(request)
        
        return UserApiResponse(
            success=True,
            message="登录成功",
            data=response.dict()
        )
        
    except UserError as e:
        logger.error(f"用户登录失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"用户登录时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/session", response_model=UserApiResponse)
async def get_session_info(session_id: str = Depends(get_session_id_from_header)):
    """
    获取会话信息
    
    需要在请求头中提供 X-Session-Id
    """
    try:
        logger.info(f"API请求: 获取会话信息 - 会话ID: {session_id}")
        
        session_info = await user_service.get_session_info(session_id)
        
        return UserApiResponse(
            success=True,
            message="会话信息获取成功",
            data=session_info.dict()
        )
        
    except SessionError as e:
        logger.error(f"获取会话信息失败: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"获取会话信息时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/session/activity", response_model=UserApiResponse)
async def update_session_activity(session_id: str = Depends(get_session_id_from_header)):
    """
    更新会话活动时间
    
    需要在请求头中提供 X-Session-Id
    """
    try:
        await user_service.update_session_activity(session_id)
        
        return UserApiResponse(
            success=True,
            message="会话活动时间更新成功",
            data={"updated_at": datetime.now().isoformat()}
        )
        
    except SessionError as e:
        logger.error(f"更新会话活动时间失败: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"更新会话活动时间时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/logout", response_model=UserApiResponse)
async def logout_user(session_id: str = Depends(get_session_id_from_header)):
    """
    用户登出
    
    需要在请求头中提供 X-Session-Id
    """
    try:
        logger.info(f"API请求: 用户登出 - 会话ID: {session_id}")
        
        # 获取会话信息（验证会话存在）
        session_info = await user_service.get_session_info(session_id)
        
        # 使会话过期
        await user_service._expire_session(session_id)
        
        return UserApiResponse(
            success=True,
            message="登出成功",
            data={"logged_out_at": datetime.now().isoformat()}
        )
        
    except SessionError as e:
        logger.error(f"用户登出失败: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"用户登出时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/experiment/start", response_model=UserApiResponse)
async def start_experiment(session_id: str = Depends(get_session_id_from_header)):
    """
    开始实验
    
    需要在请求头中提供 X-Session-Id
    """
    try:
        logger.info(f"API请求: 开始实验 - 会话ID: {session_id}")
        
        experiment_data = await user_service.start_experiment(session_id)
        
        return UserApiResponse(
            success=True,
            message="实验开始成功",
            data=experiment_data.dict()
        )
        
    except (SessionError, UserError) as e:
        logger.error(f"开始实验失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"开始实验时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/experiment/save", response_model=UserApiResponse)
async def save_experiment_data(
    experiment_data: UserExperimentData,
    session_id: str = Depends(get_session_id_from_header)
):
    """
    保存实验数据
    
    需要在请求头中提供 X-Session-Id
    """
    try:
        logger.info(f"API请求: 保存实验数据 - 会话ID: {session_id}")
        
        # 验证会话ID匹配
        if experiment_data.session_id != session_id:
            raise HTTPException(status_code=400, detail="会话ID不匹配")
        
        await user_service.save_experiment_data(experiment_data)
        
        return UserApiResponse(
            success=True,
            message="实验数据保存成功",
            data={"saved_at": datetime.now().isoformat()}
        )
        
    except DataStorageError as e:
        logger.error(f"保存实验数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except SessionError as e:
        logger.error(f"保存实验数据失败: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"保存实验数据时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/experiment/complete", response_model=UserApiResponse)
async def complete_experiment(
    request: ExperimentSubmissionRequest,
    session_id: str = Depends(get_session_id_from_header)
):
    """
    完成实验
    
    需要在请求头中提供 X-Session-Id
    """
    try:
        logger.info(f"API请求: 完成实验 - 会话ID: {session_id}")
        
        # 验证会话ID匹配
        if request.experiment_data.session_id != session_id:
            raise HTTPException(status_code=400, detail="会话ID不匹配")
        
        response = await user_service.complete_experiment(request)
        
        return UserApiResponse(
            success=True,
            message="实验完成成功",
            data=response.dict()
        )
        
    except (UserError, DataStorageError) as e:
        logger.error(f"完成实验失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SessionError as e:
        logger.error(f"完成实验失败: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"完成实验时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/experiment/data", response_model=UserApiResponse)
async def get_experiment_data(session_id: str = Depends(get_session_id_from_header)):
    """
    获取实验数据
    
    需要在请求头中提供 X-Session-Id
    """
    try:
        logger.info(f"API请求: 获取实验数据 - 会话ID: {session_id}")
        
        experiment_data = await user_service.get_experiment_data(session_id)
        
        if experiment_data is None:
            return UserApiResponse(
                success=True,
                message="暂无实验数据",
                data=None
            )
        
        return UserApiResponse(
            success=True,
            message="实验数据获取成功",
            data=experiment_data.dict()
        )
        
    except SessionError as e:
        logger.error(f"获取实验数据失败: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"获取实验数据时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/health", response_model=UserApiResponse)
async def health_check():
    """
    健康检查
    """
    return UserApiResponse(
        success=True,
        message="用户服务运行正常",
        data={
            "service": "user_service",
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    )
