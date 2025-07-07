"""
API v1主路由
API v1 Main Router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import data, prediction, explanation, adjustment

# 创建v1路由器
api_router = APIRouter()

# 注册各个端点路由
api_router.include_router(
    data.router,
    prefix="/data",
    tags=["数据管理"]
)

api_router.include_router(
    prediction.router,
    prefix="/prediction",
    tags=["预测服务"]
)

api_router.include_router(
    explanation.router,
    prefix="/explanation",
    tags=["可解释性分析"]
)

api_router.include_router(
    adjustment.router,
    prefix="/adjustment",
    tags=["预测调整"]
)
