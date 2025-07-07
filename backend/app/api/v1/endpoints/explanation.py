"""
解释相关API端点
Explanation Related API Endpoints
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from datetime import datetime
import logging
import numpy as np

from app.api.deps import get_explanation_service, get_logger
from app.services.explanation_service import ExplanationService
from app.models.responses import StandardResponse
from app.utils.exceptions import ExplanationError, ModelNotFoundError
from app.utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES

logger = logging.getLogger("power_prediction")
router = APIRouter()


@router.post("/initialize")
async def initialize_explanation_service(
    background_data: List[List[float]] = Body(..., description="SHAP背景数据"),
    training_data: List[List[float]] = Body(..., description="LIME训练数据"),
    explanation_service: ExplanationService = Depends(get_explanation_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    初始化解释服务
    
    - **background_data**: SHAP分析的背景数据
    - **training_data**: LIME分析的训练数据
    """
    try:
        logger.info("API请求: 初始化解释服务")
        
        # 转换为numpy数组
        background_array = np.array(background_data)
        training_array = np.array(training_data)
        
        # 这里需要从预测服务获取模型
        # 简化处理：假设模型已经可用
        from app.api.deps import get_prediction_service
        prediction_service = get_prediction_service()
        
        # 获取模型（这里需要实际的模型实例）
        # 简化处理：直接初始化
        result = {
            "initialization_requested": True,
            "background_data_shape": background_array.shape,
            "training_data_shape": training_array.shape,
            "message": "解释服务初始化请求已接收，需要配合模型实例完成初始化"
        }
        
        return StandardResponse(
            success=True,
            data=result,
            message="解释服务初始化请求成功"
        )
        
    except Exception as e:
        logger.error(f"初始化解释服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/shap")
async def get_shap_analysis(
    analysis_type: str = Query("global", description="分析类型 (global, local, hourly)"),
    instances: Optional[str] = Query(None, description="实例数据，JSON格式的数组"),
    hours: Optional[str] = Query(None, description="小时列表，逗号分隔"),
    explanation_service: ExplanationService = Depends(get_explanation_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取SHAP分析结果
    
    - **analysis_type**: 分析类型 (global, local, hourly)
    - **instances**: 要分析的实例数据（局部分析时需要）
    - **hours**: 小时列表（按小时分析时需要）
    """
    try:
        logger.info(f"API请求: SHAP分析 类型={analysis_type}")
        
        # 解析实例数据
        instances_array = None
        if instances:
            try:
                import json
                instances_data = json.loads(instances)
                instances_array = np.array(instances_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(status_code=422, detail=f"实例数据格式错误: {str(e)}")
        
        # 解析小时列表
        hours_list = None
        if hours:
            try:
                hours_list = [int(x.strip()) for x in hours.split(",")]
            except ValueError as e:
                raise HTTPException(status_code=422, detail=f"小时列表格式错误: {str(e)}")
        
        result = await explanation_service.get_shap_analysis(
            analysis_type=analysis_type,
            instances=instances_array,
            hours=hours_list
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message="SHAP分析完成"
        )
        
    except ExplanationError as e:
        logger.error(f"SHAP分析失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"SHAP分析时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/lime")
async def get_lime_analysis(
    instances: List[List[float]] = Body(..., description="要分析的实例数据"),
    analysis_type: str = Body("single", description="分析类型 (single, batch, hourly, compare)"),
    hours: Optional[List[int]] = Body(None, description="小时列表（按小时分析时需要）"),
    num_features: int = Body(4, description="要显示的特征数量"),
    explanation_service: ExplanationService = Depends(get_explanation_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取LIME分析结果
    
    - **instances**: 要分析的实例数据
    - **analysis_type**: 分析类型 (single, batch, hourly, compare)
    - **hours**: 小时列表（按小时分析时需要）
    - **num_features**: 要显示的特征数量
    """
    try:
        logger.info(f"API请求: LIME分析 类型={analysis_type}")
        
        # 转换为numpy数组
        instances_array = np.array(instances)
        
        result = await explanation_service.get_lime_analysis(
            instances=instances_array,
            analysis_type=analysis_type,
            hours=hours,
            num_features=num_features
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message="LIME分析完成"
        )
        
    except ExplanationError as e:
        logger.error(f"LIME分析失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"LIME分析时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/feature-importance")
async def get_feature_importance(
    explanation_service: ExplanationService = Depends(get_explanation_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取特征重要性分析
    """
    try:
        logger.info("API请求: 获取特征重要性分析")
        
        result = await explanation_service.get_feature_importance()
        
        return StandardResponse(
            success=True,
            data=result,
            message="特征重要性分析完成"
        )
        
    except ExplanationError as e:
        logger.error(f"特征重要性分析失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"特征重要性分析时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/comprehensive")
async def get_comprehensive_explanation(
    instances: List[List[float]] = Body(..., description="要分析的实例数据"),
    hours: List[int] = Body(..., description="小时列表"),
    explanation_service: ExplanationService = Depends(get_explanation_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取综合解释分析
    
    - **instances**: 要分析的实例数据
    - **hours**: 小时列表
    """
    try:
        logger.info("API请求: 获取综合解释分析")
        
        # 转换为numpy数组
        instances_array = np.array(instances)
        
        result = await explanation_service.get_comprehensive_explanation(
            instances=instances_array,
            hours=hours
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message="综合解释分析完成"
        )
        
    except ExplanationError as e:
        logger.error(f"综合解释分析失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"综合解释分析时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/compare")
async def compare_explanations(
    instances_list: List[List[List[float]]] = Body(..., description="实例列表"),
    labels: List[str] = Body(..., description="实例标签列表"),
    explanation_service: ExplanationService = Depends(get_explanation_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    比较不同实例的解释
    
    - **instances_list**: 实例列表，每个元素是一组实例
    - **labels**: 实例标签列表
    """
    try:
        logger.info(f"API请求: 比较解释 {len(instances_list)} 组实例")
        
        # 转换为numpy数组列表
        instances_arrays = [np.array(instances) for instances in instances_list]
        
        result = await explanation_service.compare_explanations(
            instances_list=instances_arrays,
            labels=labels
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message="解释比较完成"
        )
        
    except ExplanationError as e:
        logger.error(f"解释比较失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"解释比较时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.delete("/cache")
async def clear_explanation_cache(
    explanation_service: ExplanationService = Depends(get_explanation_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    清除解释缓存
    """
    try:
        logger.info("API请求: 清除解释缓存")
        
        result = await explanation_service.clear_cache()
        
        return StandardResponse(
            success=True,
            data=result,
            message="解释缓存清除成功"
        )
        
    except Exception as e:
        logger.error(f"清除解释缓存时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/health")
async def check_explanation_health(
    explanation_service: ExplanationService = Depends(get_explanation_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    检查解释服务健康状态
    """
    try:
        logger.info("API请求: 检查解释服务健康状态")
        
        is_initialized = explanation_service.is_initialized()
        
        health_status = {
            "status": "healthy" if is_initialized else "not_initialized",
            "is_initialized": is_initialized,
            "shap_available": is_initialized,
            "lime_available": is_initialized,
            "checked_at": datetime.now().isoformat()
        }
        
        return StandardResponse(
            success=True,
            data=health_status,
            message="解释服务运行正常" if is_initialized else "解释服务未初始化"
        )
        
    except Exception as e:
        logger.error(f"解释服务健康检查失败: {str(e)}")
        
        health_status = {
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.now().isoformat()
        }
        
        return StandardResponse(
            success=False,
            data=health_status,
            message="解释服务异常"
        )
