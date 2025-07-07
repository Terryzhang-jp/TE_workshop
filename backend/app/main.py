"""
主应用入口
Main Application Entry Point
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.api.v1.api import api_router
from app.utils.exceptions import (
    DataLoadError, DataValidationError, ModelTrainingError, 
    ModelNotFoundError, PredictionError, ExplanationError, AdjustmentError
)
from app.utils.logging_config import setup_logging

# 设置日志
setup_logging()
logger = logging.getLogger("power_prediction")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("电力需求预测系统启动中...")
    logger.info(f"版本: {settings.version}")
    logger.info(f"环境: {settings.environment}")
    
    yield
    
    # 关闭时执行
    logger.info("电力需求预测系统关闭中...")


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="电力需求预测系统 API - 基于机器学习的电力需求预测与可解释性分析",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts if settings.environment == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# 异常处理器
@app.exception_handler(DataLoadError)
async def data_load_error_handler(request: Request, exc: DataLoadError):
    """数据加载错误处理"""
    logger.error(f"数据加载错误: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc), "error_type": "DataLoadError"}
    )


@app.exception_handler(DataValidationError)
async def data_validation_error_handler(request: Request, exc: DataValidationError):
    """数据验证错误处理"""
    logger.error(f"数据验证错误: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": str(exc), "error_type": "DataValidationError"}
    )


@app.exception_handler(ModelTrainingError)
async def model_training_error_handler(request: Request, exc: ModelTrainingError):
    """模型训练错误处理"""
    logger.error(f"模型训练错误: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc), "error_type": "ModelTrainingError"}
    )


@app.exception_handler(ModelNotFoundError)
async def model_not_found_error_handler(request: Request, exc: ModelNotFoundError):
    """模型未找到错误处理"""
    logger.error(f"模型未找到错误: {str(exc)}")
    return JSONResponse(
        status_code=404,
        content={"success": False, "message": str(exc), "error_type": "ModelNotFoundError"}
    )


@app.exception_handler(PredictionError)
async def prediction_error_handler(request: Request, exc: PredictionError):
    """预测错误处理"""
    logger.error(f"预测错误: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc), "error_type": "PredictionError"}
    )


@app.exception_handler(ExplanationError)
async def explanation_error_handler(request: Request, exc: ExplanationError):
    """解释错误处理"""
    logger.error(f"解释错误: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc), "error_type": "ExplanationError"}
    )


@app.exception_handler(AdjustmentError)
async def adjustment_error_handler(request: Request, exc: AdjustmentError):
    """调整错误处理"""
    logger.error(f"调整错误: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": str(exc), "error_type": "AdjustmentError"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证错误处理"""
    logger.error(f"请求验证错误: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "请求参数验证失败", "details": exc.errors()}
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "内部服务器错误"}
    )


# 包含API路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "电力需求预测系统 API",
        "version": settings.version,
        "environment": settings.environment,
        "docs_url": "/docs" if settings.environment != "production" else None
    }


@app.get("/health")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "service": "power-prediction-api",
        "version": settings.version,
        "environment": settings.environment
    }
