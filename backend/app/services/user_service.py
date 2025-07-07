"""
用户管理服务
User Management Service
"""

import os
import json
import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.models.user_models import (
    UserData, UserExperimentData, UserSessionInfo, ExperimentSummary,
    UserLoginRequest, UserLoginResponse, ExperimentSubmissionRequest,
    ExperimentSubmissionResponse, UserAdjustment, UserInteraction, Decision
)
from app.utils.exceptions import UserError, SessionError, DataStorageError
from app.config.settings import settings

logger = logging.getLogger("power_prediction")


class UserService:
    """用户管理服务类"""
    
    def __init__(self):
        """初始化用户服务"""
        self.data_dir = Path(settings.data_dir) / "user_experiments"
        self.sessions_dir = Path(settings.data_dir) / "user_sessions"
        self.results_dir = Path(settings.data_dir) / "experiment_results"
        
        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 活跃会话缓存
        self._active_sessions: Dict[str, UserSessionInfo] = {}
        
        logger.info("用户服务初始化完成")
    
    async def login_user(self, request: UserLoginRequest) -> UserLoginResponse:
        """用户登录"""
        try:
            # 验证用户名
            username = request.username.strip()
            if not username:
                raise UserError("用户名不能为空")
            
            if len(username) < 3 or len(username) > 20:
                raise UserError("用户名长度必须在3-20个字符之间")
            
            # 生成用户数据
            user_id = f"user_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:8]}"
            session_id = f"session_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:8]}"
            login_time = datetime.now(timezone.utc)
            
            user_data = UserData(
                user_id=user_id,
                username=username,
                session_id=session_id,
                login_time=login_time
            )
            
            # 创建会话信息
            session_info = UserSessionInfo(
                session_id=session_id,
                user_id=user_id,
                username=username,
                login_time=login_time,
                last_activity=login_time,
                is_active=True,
                experiment_status='not_started'
            )
            
            # 保存会话信息
            await self._save_session_info(session_info)
            self._active_sessions[session_id] = session_info
            
            logger.info(f"用户登录成功: {username} (ID: {user_id})")
            
            return UserLoginResponse(
                user_data=user_data,
                session_info={
                    "session_id": session_id,
                    "login_time": login_time.isoformat(),
                    "experiment_status": "not_started"
                }
            )
            
        except Exception as e:
            logger.error(f"用户登录失败: {str(e)}")
            if isinstance(e, UserError):
                raise
            else:
                raise UserError(f"登录过程中发生错误: {str(e)}")
    
    async def get_session_info(self, session_id: str) -> UserSessionInfo:
        """获取会话信息"""
        try:
            # 先从缓存中查找
            if session_id in self._active_sessions:
                session_info = self._active_sessions[session_id]
                
                # 检查会话是否过期
                if self._is_session_expired(session_info):
                    await self._expire_session(session_id)
                    raise SessionError("会话已过期")
                
                return session_info
            
            # 从文件中加载
            session_file = self.sessions_dir / f"{session_id}.json"
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                session_info = UserSessionInfo(**session_data)
                
                # 检查会话是否过期
                if self._is_session_expired(session_info):
                    await self._expire_session(session_id)
                    raise SessionError("会话已过期")
                
                self._active_sessions[session_id] = session_info
                return session_info
            
            raise SessionError("会话不存在")
            
        except Exception as e:
            logger.error(f"获取会话信息失败: {str(e)}")
            if isinstance(e, SessionError):
                raise
            else:
                raise SessionError(f"获取会话信息时发生错误: {str(e)}")
    
    async def update_session_activity(self, session_id: str) -> None:
        """更新会话活动时间"""
        try:
            session_info = await self.get_session_info(session_id)
            session_info.last_activity = datetime.now(timezone.utc)
            
            await self._save_session_info(session_info)
            self._active_sessions[session_id] = session_info
            
        except Exception as e:
            logger.error(f"更新会话活动时间失败: {str(e)}")
            # 这个操作失败不应该影响主要功能，所以不抛出异常
    
    async def start_experiment(self, session_id: str) -> UserExperimentData:
        """开始实验"""
        try:
            session_info = await self.get_session_info(session_id)
            
            # 创建实验数据
            experiment_data = UserExperimentData(
                user_id=session_info.user_id,
                username=session_info.username,
                session_id=session_id,
                start_time=datetime.now(timezone.utc),
                decisions=[],
                adjustments=[],
                interactions=[],
                status='in_progress'
            )
            
            # 保存实验数据
            await self._save_experiment_data(experiment_data)
            
            # 更新会话状态
            session_info.experiment_status = 'in_progress'
            await self._save_session_info(session_info)
            
            logger.info(f"实验开始: 用户 {session_info.username} (会话: {session_id})")
            
            return experiment_data
            
        except Exception as e:
            logger.error(f"开始实验失败: {str(e)}")
            if isinstance(e, (SessionError, UserError)):
                raise
            else:
                raise UserError(f"开始实验时发生错误: {str(e)}")
    
    async def save_experiment_data(self, experiment_data: UserExperimentData) -> None:
        """保存实验数据"""
        try:
            await self._save_experiment_data(experiment_data)
            
            # 更新会话活动时间
            await self.update_session_activity(experiment_data.session_id)
            
        except Exception as e:
            logger.error(f"保存实验数据失败: {str(e)}")
            raise DataStorageError(f"保存实验数据时发生错误: {str(e)}")
    
    async def complete_experiment(self, request: ExperimentSubmissionRequest) -> ExperimentSubmissionResponse:
        """完成实验"""
        try:
            experiment_data = request.experiment_data
            
            # 设置完成时间（使用UTC时区）
            experiment_data.completion_time = datetime.now(timezone.utc)
            experiment_data.status = 'completed'
            
            # 保存最终实验数据
            await self._save_experiment_data(experiment_data)
            
            # 生成实验摘要
            summary = self._generate_experiment_summary(experiment_data)
            
            # 保存到结果目录
            submission_id = f"submission_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:8]}"
            result_file = self.results_dir / f"{submission_id}.json"

            result_data = {
                "submission_id": submission_id,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "experiment_data": experiment_data.dict(),
                "experiment_summary": summary.dict()
            }
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 更新会话状态
            try:
                session_info = await self.get_session_info(experiment_data.session_id)
                session_info.experiment_status = 'completed'
                await self._save_session_info(session_info)
            except:
                pass  # 会话可能已过期，不影响实验提交
            
            logger.info(f"实验完成: 用户 {experiment_data.username} (提交ID: {submission_id})")
            
            return ExperimentSubmissionResponse(
                submission_id=submission_id,
                submitted_at=datetime.now(timezone.utc),
                experiment_summary=summary
            )
            
        except Exception as e:
            logger.error(f"完成实验失败: {str(e)}")
            if isinstance(e, (UserError, DataStorageError)):
                raise
            else:
                raise UserError(f"完成实验时发生错误: {str(e)}")
    
    async def get_experiment_data(self, session_id: str) -> Optional[UserExperimentData]:
        """获取实验数据"""
        try:
            session_info = await self.get_session_info(session_id)
            experiment_file = self.data_dir / f"{session_info.user_id}_{session_id}.json"
            
            if experiment_file.exists():
                with open(experiment_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserExperimentData(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"获取实验数据失败: {str(e)}")
            return None
    
    def _generate_experiment_summary(self, experiment_data: UserExperimentData) -> ExperimentSummary:
        """生成实验摘要"""
        # 确保所有时间都是UTC时区
        start_time = experiment_data.start_time
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        end_time = experiment_data.completion_time or datetime.now(timezone.utc)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        
        # 计算调整统计
        adjustments = experiment_data.adjustments
        adjustment_stats = {
            "total_adjustments": len(adjustments),
            "hours_adjusted": len(set(adj.hour for adj in adjustments)),
            "average_adjustment": sum(abs(adj.adjusted_value - adj.original_value) for adj in adjustments) / len(adjustments) if adjustments else 0,
            "max_adjustment": max(abs(adj.adjusted_value - adj.original_value) for adj in adjustments) if adjustments else 0,
            "most_adjusted_hour": max(set(adj.hour for adj in adjustments), key=lambda h: sum(1 for adj in adjustments if adj.hour == h)) if adjustments else None
        }
        
        return ExperimentSummary(
            total_decisions=len(experiment_data.decisions),
            total_adjustments=len(experiment_data.adjustments),
            total_interactions=len(experiment_data.interactions),
            experiment_duration=duration_minutes,
            status=experiment_data.status,
            adjustment_statistics=adjustment_stats
        )
    
    async def _save_session_info(self, session_info: UserSessionInfo) -> None:
        """保存会话信息"""
        session_file = self.sessions_dir / f"{session_info.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_info.dict(), f, ensure_ascii=False, indent=2, default=str)
    
    async def _save_experiment_data(self, experiment_data: UserExperimentData) -> None:
        """保存实验数据"""
        experiment_file = self.data_dir / f"{experiment_data.user_id}_{experiment_data.session_id}.json"
        with open(experiment_file, 'w', encoding='utf-8') as f:
            json.dump(experiment_data.dict(), f, ensure_ascii=False, indent=2, default=str)
    
    def _is_session_expired(self, session_info: UserSessionInfo) -> bool:
        """检查会话是否过期"""
        if not session_info.is_active:
            return True
        
        # 会话超时时间：2小时
        timeout_hours = 2
        timeout_delta = timedelta(hours=timeout_hours)
        
        return datetime.now(timezone.utc) - session_info.last_activity > timeout_delta
    
    async def _expire_session(self, session_id: str) -> None:
        """使会话过期"""
        if session_id in self._active_sessions:
            session_info = self._active_sessions[session_id]
            session_info.is_active = False
            await self._save_session_info(session_info)
            del self._active_sessions[session_id]
