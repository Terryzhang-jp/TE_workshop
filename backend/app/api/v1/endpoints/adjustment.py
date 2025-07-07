"""
调整相关API端点
Adjustment Related API Endpoints
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from datetime import datetime
import logging

from app.api.deps import get_adjustment_service, get_logger
from app.services.adjustment_service import AdjustmentService
from app.models.schemas import PredictionResult, GlobalAdjustment, LocalAdjustment
from app.models.responses import StandardResponse
from app.utils.exceptions import AdjustmentError
from app.utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES

logger = logging.getLogger("power_prediction")
router = APIRouter()


@router.post("/global")
async def apply_global_adjustment(
    predictions: List[Dict[str, Any]] = Body(..., description="原始预测结果"),
    adjustment: Dict[str, Any] = Body(..., description="全局调整参数"),
    save_original: bool = Body(True, description="是否保存原始预测"),
    adjustment_service: AdjustmentService = Depends(get_adjustment_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    应用全局调整
    
    - **predictions**: 原始预测结果列表
    - **adjustment**: 全局调整参数
    - **save_original**: 是否保存原始预测
    """
    try:
        logger.info("API请求: 应用全局调整")
        
        # 转换为数据模型
        prediction_objects = [PredictionResult(**pred) for pred in predictions]
        adjustment_object = GlobalAdjustment(**adjustment)
        
        result = await adjustment_service.apply_global_adjustment(
            predictions=prediction_objects,
            adjustment=adjustment_object,
            save_original=save_original
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message=SUCCESS_MESSAGES["adjustment_applied"]
        )
        
    except AdjustmentError as e:
        logger.error(f"全局调整失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"应用全局调整时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/local")
async def apply_local_adjustment(
    predictions: List[Dict[str, Any]] = Body(..., description="原始预测结果"),
    adjustments: List[Dict[str, Any]] = Body(..., description="局部调整参数列表"),
    save_original: bool = Body(True, description="是否保存原始预测"),
    adjustment_service: AdjustmentService = Depends(get_adjustment_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    应用局部调整
    
    - **predictions**: 原始预测结果列表
    - **adjustments**: 局部调整参数列表
    - **save_original**: 是否保存原始预测
    """
    try:
        logger.info(f"API请求: 应用局部调整 {len(adjustments)} 个点")
        
        # 转换为数据模型
        prediction_objects = [PredictionResult(**pred) for pred in predictions]
        adjustment_objects = [LocalAdjustment(**adj) for adj in adjustments]
        
        result = await adjustment_service.apply_local_adjustment(
            predictions=prediction_objects,
            adjustments=adjustment_objects,
            save_original=save_original
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message=SUCCESS_MESSAGES["adjustment_applied"]
        )
        
    except AdjustmentError as e:
        logger.error(f"局部调整失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"应用局部调整时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/mixed")
async def apply_mixed_adjustment(
    predictions: List[Dict[str, Any]] = Body(..., description="原始预测结果"),
    global_adjustments: Optional[List[Dict[str, Any]]] = Body(None, description="全局调整参数列表"),
    local_adjustments: Optional[List[Dict[str, Any]]] = Body(None, description="局部调整参数列表"),
    adjustment_service: AdjustmentService = Depends(get_adjustment_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    应用混合调整（全局+局部）
    
    - **predictions**: 原始预测结果列表
    - **global_adjustments**: 全局调整参数列表
    - **local_adjustments**: 局部调整参数列表
    """
    try:
        logger.info("API请求: 应用混合调整")
        
        # 转换为数据模型
        prediction_objects = [PredictionResult(**pred) for pred in predictions]
        
        global_adjustment_objects = None
        if global_adjustments:
            global_adjustment_objects = [GlobalAdjustment(**adj) for adj in global_adjustments]
        
        local_adjustment_objects = None
        if local_adjustments:
            local_adjustment_objects = [LocalAdjustment(**adj) for adj in local_adjustments]
        
        result = await adjustment_service.apply_mixed_adjustment(
            predictions=prediction_objects,
            global_adjustments=global_adjustment_objects,
            local_adjustments=local_adjustment_objects
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message="混合调整应用成功"
        )
        
    except AdjustmentError as e:
        logger.error(f"混合调整失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"应用混合调整时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/reset")
async def reset_adjustments(
    adjustment_service: AdjustmentService = Depends(get_adjustment_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    重置调整，恢复到原始预测
    """
    try:
        logger.info("API请求: 重置调整")
        
        result = await adjustment_service.reset_adjustments()
        
        return StandardResponse(
            success=True,
            data=result,
            message="调整重置成功"
        )
        
    except AdjustmentError as e:
        logger.error(f"重置调整失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"重置调整时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/optimize")
async def optimize_global_adjustment(
    predictions: List[Dict[str, Any]] = Body(..., description="原始预测结果"),
    target_total: float = Body(..., description="目标总用电量"),
    adjustment_hours: Optional[List[int]] = Body(None, description="允许调整的小时列表"),
    adjustment_service: AdjustmentService = Depends(get_adjustment_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    优化全局调整参数
    
    - **predictions**: 原始预测结果列表
    - **target_total**: 目标总用电量
    - **adjustment_hours**: 允许调整的小时列表
    """
    try:
        logger.info(f"API请求: 优化全局调整参数 目标总量={target_total}")
        
        # 转换为数据模型
        prediction_objects = [PredictionResult(**pred) for pred in predictions]
        
        result = await adjustment_service.optimize_global_adjustment(
            predictions=prediction_objects,
            target_total=target_total,
            adjustment_hours=adjustment_hours
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message="全局调整参数优化完成"
        )
        
    except AdjustmentError as e:
        logger.error(f"优化全局调整参数失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"优化全局调整参数时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/history")
async def get_adjustment_history(
    adjustment_type: str = Query("all", description="调整类型 (all, global, local)"),
    adjustment_service: AdjustmentService = Depends(get_adjustment_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取调整历史
    
    - **adjustment_type**: 调整类型 (all, global, local)
    """
    try:
        logger.info(f"API请求: 获取调整历史 类型={adjustment_type}")
        
        result = await adjustment_service.get_adjustment_history(adjustment_type)
        
        return StandardResponse(
            success=True,
            data=result,
            message="调整历史获取成功"
        )
        
    except AdjustmentError as e:
        logger.error(f"获取调整历史失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取调整历史时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.delete("/history")
async def clear_adjustment_history(
    adjustment_service: AdjustmentService = Depends(get_adjustment_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    清除调整历史
    """
    try:
        logger.info("API请求: 清除调整历史")
        
        result = await adjustment_service.clear_adjustment_history()
        
        return StandardResponse(
            success=True,
            data=result,
            message="调整历史清除成功"
        )
        
    except Exception as e:
        logger.error(f"清除调整历史时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/health")
async def check_adjustment_health(
    adjustment_service: AdjustmentService = Depends(get_adjustment_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    检查调整服务健康状态
    """
    try:
        logger.info("API请求: 检查调整服务健康状态")
        
        # 获取调整历史作为健康检查
        history = await adjustment_service.get_adjustment_history()
        
        health_status = {
            "status": "healthy",
            "global_adjuster_available": True,
            "local_adjuster_available": True,
            "total_adjustments": history.get("total_adjustments", 0),
            "checked_at": datetime.now().isoformat()
        }
        
        return StandardResponse(
            success=True,
            data=health_status,
            message="调整服务运行正常"
        )
        
    except Exception as e:
        logger.error(f"调整服务健康检查失败: {str(e)}")
        
        health_status = {
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.now().isoformat()
        }
        
        return StandardResponse(
            success=False,
            data=health_status,
            message="调整服务异常"
        )
