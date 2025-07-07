"""
API v1 路由配置
API v1 Router Configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import data, prediction, explanation, adjustment, users, csv_export

api_router = APIRouter()

# 数据相关端点
api_router.include_router(
    data.router,
    prefix="/data",
    tags=["data"],
    responses={404: {"description": "Not found"}}
)

# 预测相关端点
api_router.include_router(
    prediction.router,
    prefix="/prediction",
    tags=["prediction"],
    responses={404: {"description": "Not found"}}
)

# 解释相关端点
api_router.include_router(
    explanation.router,
    prefix="/explanation",
    tags=["explanation"],
    responses={404: {"description": "Not found"}}
)

# 调整相关端点
api_router.include_router(
    adjustment.router,
    prefix="/adjustment",
    tags=["adjustment"],
    responses={404: {"description": "Not found"}}
)

# 用户管理相关端点
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

# CSV导出相关端点
api_router.include_router(
    csv_export.router,
    prefix="/csv",
    tags=["csv-export"],
    responses={404: {"description": "Not found"}}
)


