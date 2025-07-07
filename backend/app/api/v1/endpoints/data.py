"""
数据相关API端点
Data Related API Endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
import logging

from app.api.deps import get_data_service, get_logger
from app.services.data_service import DataService
from app.models.responses import StandardResponse, DataResponse, ContextInfoResponse
from app.utils.exceptions import DataLoadError, DataValidationError
from app.utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES

logger = logging.getLogger("power_prediction")
router = APIRouter()


@router.get("/historical", response_model=StandardResponse[DataResponse])
async def get_historical_data(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    include_features: bool = Query(True, description="是否包含特征工程后的数据"),
    data_service: DataService = Depends(get_data_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取历史数据
    
    - **start_date**: 开始日期，格式为 YYYY-MM-DD
    - **end_date**: 结束日期，格式为 YYYY-MM-DD  
    - **include_features**: 是否包含特征工程后的数据
    """
    try:
        logger.info(f"API请求: 获取历史数据 {start_date} 到 {end_date}")
        
        result = await data_service.get_historical_data(
            start_date=start_date,
            end_date=end_date,
            include_features=include_features
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message=SUCCESS_MESSAGES["data_loaded"]
        )
        
    except (DataLoadError, DataValidationError) as e:
        logger.error(f"获取历史数据失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取历史数据时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/context-info", response_model=StandardResponse[ContextInfoResponse])
async def get_context_info(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    data_service: DataService = Depends(get_data_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取情景信息
    
    - **start_date**: 开始日期，格式为 YYYY-MM-DD
    - **end_date**: 结束日期，格式为 YYYY-MM-DD
    """
    try:
        logger.info(f"API请求: 获取情景信息 {start_date} 到 {end_date}")
        
        date_range = (start_date, end_date) if start_date and end_date else None
        result = await data_service.get_context_info(date_range)
        
        return StandardResponse(
            success=True,
            data=result,
            message="情景信息获取成功"
        )
        
    except DataLoadError as e:
        logger.error(f"获取情景信息失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取情景信息时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/validate")
async def validate_data_file(
    file_path: str,
    data_service: DataService = Depends(get_data_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    验证数据文件
    
    - **file_path**: 数据文件路径
    """
    try:
        logger.info(f"API请求: 验证数据文件 {file_path}")
        
        result = await data_service.validate_data_file(file_path)
        
        return StandardResponse(
            success=True,
            data=result,
            message="数据文件验证完成"
        )
        
    except DataValidationError as e:
        logger.error(f"数据文件验证失败: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"验证数据文件时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/summary")
async def get_data_summary(
    data_service: DataService = Depends(get_data_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取数据摘要信息
    """
    try:
        logger.info("API请求: 获取数据摘要")
        
        result = await data_service.get_data_summary()
        
        return StandardResponse(
            success=True,
            data=result,
            message="数据摘要获取成功"
        )
        
    except DataLoadError as e:
        logger.error(f"获取数据摘要失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取数据摘要时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/export")
async def export_data(
    data_type: str = Query("historical", description="数据类型 (historical, context)"),
    format: str = Query("csv", description="导出格式 (csv, json)"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    data_service: DataService = Depends(get_data_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    导出数据
    
    - **data_type**: 数据类型 (historical, context)
    - **format**: 导出格式 (csv, json)
    - **start_date**: 开始日期，格式为 YYYY-MM-DD
    - **end_date**: 结束日期，格式为 YYYY-MM-DD
    """
    try:
        logger.info(f"API请求: 导出数据 类型={data_type}, 格式={format}")
        
        result = await data_service.export_data(
            data_type=data_type,
            format=format,
            start_date=start_date,
            end_date=end_date
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message=SUCCESS_MESSAGES["export_completed"]
        )
        
    except (DataLoadError, DataValidationError) as e:
        logger.error(f"导出数据失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"导出数据时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.delete("/cache")
async def clear_data_cache(
    data_service: DataService = Depends(get_data_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    清除数据缓存
    """
    try:
        logger.info("API请求: 清除数据缓存")
        
        result = await data_service.clear_cache()
        
        return StandardResponse(
            success=True,
            data=result,
            message="数据缓存清除成功"
        )
        
    except Exception as e:
        logger.error(f"清除数据缓存时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/health")
async def check_data_health(
    data_service: DataService = Depends(get_data_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    检查数据服务健康状态
    """
    try:
        logger.info("API请求: 检查数据服务健康状态")
        
        # 获取数据摘要作为健康检查
        summary = await data_service.get_data_summary()
        
        health_status = {
            "status": "healthy",
            "data_loaded": summary.get("system_status", {}).get("data_loaded", False),
            "processor_fitted": summary.get("system_status", {}).get("processor_fitted", False),
            "cache_size": summary.get("system_status", {}).get("cache_size", 0),
            "checked_at": datetime.now().isoformat()
        }
        
        return StandardResponse(
            success=True,
            data=health_status,
            message="数据服务运行正常"
        )
        
    except Exception as e:
        logger.error(f"数据服务健康检查失败: {str(e)}")
        
        health_status = {
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.now().isoformat()
        }
        
        return StandardResponse(
            success=False,
            data=health_status,
            message="数据服务异常"
        )
