"""
依赖注入配置
Dependency Injection Configuration
"""

import logging
from typing import Generator
from functools import lru_cache

from app.services.data_service import DataService
from app.services.prediction_service import PredictionService
from app.services.explanation_service import ExplanationService
from app.services.adjustment_service import AdjustmentService


# 服务实例缓存
_data_service_instance = None
_prediction_service_instance = None
_explanation_service_instance = None
_adjustment_service_instance = None


@lru_cache()
def get_data_service() -> DataService:
    """获取数据服务实例"""
    global _data_service_instance
    if _data_service_instance is None:
        _data_service_instance = DataService()
    return _data_service_instance


@lru_cache()
def get_prediction_service() -> PredictionService:
    """获取预测服务实例"""
    global _prediction_service_instance
    if _prediction_service_instance is None:
        _prediction_service_instance = PredictionService()
    return _prediction_service_instance


@lru_cache()
def get_explanation_service() -> ExplanationService:
    """获取解释服务实例"""
    global _explanation_service_instance
    if _explanation_service_instance is None:
        _explanation_service_instance = ExplanationService()
    return _explanation_service_instance


@lru_cache()
def get_adjustment_service() -> AdjustmentService:
    """获取调整服务实例"""
    global _adjustment_service_instance
    if _adjustment_service_instance is None:
        _adjustment_service_instance = AdjustmentService()
    return _adjustment_service_instance


def get_logger() -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger("power_prediction")


def clear_service_cache():
    """清除服务缓存"""
    global _data_service_instance, _prediction_service_instance
    global _explanation_service_instance, _adjustment_service_instance

    _data_service_instance = None
    _prediction_service_instance = None
    _explanation_service_instance = None
    _adjustment_service_instance = None

    # 清除lru_cache
    get_data_service.cache_clear()
    get_prediction_service.cache_clear()
    get_explanation_service.cache_clear()
    get_adjustment_service.cache_clear()


# 数据库依赖（如果需要）
def get_db() -> Generator:
    """获取数据库连接（占位符）"""
    # 这里可以添加数据库连接逻辑
    # 目前项目主要使用文件数据，暂时不需要数据库
    try:
        # db = SessionLocal()
        # yield db
        yield None
    finally:
        # db.close()
        pass


# 认证依赖（如果需要）
def get_current_user():
    """获取当前用户（占位符）"""
    # 这里可以添加用户认证逻辑
    # 目前项目暂时不需要用户认证
    return {"user_id": "anonymous", "username": "anonymous"}


# 权限检查依赖（如果需要）
def check_permissions(required_permission: str):
    """检查权限（占位符）"""
    def permission_checker():
        # 这里可以添加权限检查逻辑
        # 目前项目暂时不需要权限控制
        return True
    return permission_checker
