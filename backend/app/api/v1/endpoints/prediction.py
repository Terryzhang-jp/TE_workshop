"""
预测相关API端点
Prediction Related API Endpoints
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from datetime import datetime, timedelta
import logging

from app.api.deps import get_prediction_service, get_logger
from app.services.prediction_service import PredictionService
from app.models.responses import StandardResponse, PredictionResponse
from app.utils.exceptions import PredictionError, ModelTrainingError, ModelNotFoundError
from app.utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES

logger = logging.getLogger("power_prediction")
router = APIRouter()


@router.post("/train")
async def train_model(
    target_date: Optional[str] = Body(None, description="目标预测日期 (YYYY-MM-DD)"),
    weeks_before: int = Body(3, description="使用目标日期前几周的数据"),
    validation_split: float = Body(0.2, description="验证集比例"),
    model_params: Optional[Dict[str, Any]] = Body(None, description="模型参数"),
    force_retrain: bool = Body(False, description="是否强制重新训练"),
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    训练预测模型
    
    - **target_date**: 目标预测日期，格式为 YYYY-MM-DD
    - **weeks_before**: 使用目标日期前几周的数据进行训练
    - **validation_split**: 验证集比例 (0-1)
    - **model_params**: 自定义模型参数
    - **force_retrain**: 是否强制重新训练
    """
    try:
        logger.info(f"API请求: 训练模型 目标日期={target_date}")
        
        result = await prediction_service.train_model(
            target_date=target_date,
            weeks_before=weeks_before,
            validation_split=validation_split,
            model_params=model_params,
            force_retrain=force_retrain
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message=SUCCESS_MESSAGES["model_trained"]
        )
        
    except ModelTrainingError as e:
        logger.error(f"模型训练失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"训练模型时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/", response_model=StandardResponse[PredictionResponse])
async def get_prediction(
    target_date: Optional[str] = Query(None, description="目标日期 (YYYY-MM-DD)"),
    temperature_forecast: Optional[str] = Query(None, description="24小时温度预报，逗号分隔"),
    use_cache: bool = Query(True, description="是否使用缓存"),
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取预测结果
    
    - **target_date**: 目标日期，格式为 YYYY-MM-DD
    - **temperature_forecast**: 24小时温度预报，逗号分隔的数字
    - **use_cache**: 是否使用缓存
    """
    try:
        logger.info(f"API请求: 获取预测结果 目标日期={target_date}")
        
        # 解析温度预报
        temp_forecast = None
        if temperature_forecast:
            try:
                temp_forecast = [float(x.strip()) for x in temperature_forecast.split(",")]
                if len(temp_forecast) != 24:
                    raise ValueError("温度预报必须包含24个小时的数据")
            except ValueError as e:
                raise HTTPException(status_code=422, detail=f"温度预报格式错误: {str(e)}")
        
        result = await prediction_service.get_prediction(
            target_date=target_date,
            temperature_forecast=temp_forecast,
            use_cache=use_cache
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message=SUCCESS_MESSAGES["prediction_generated"]
        )
        
    except (PredictionError, ModelNotFoundError) as e:
        logger.error(f"获取预测结果失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取预测结果时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/hourly")
async def get_hourly_prediction(
    target_datetime: str = Query(..., description="目标时间 (YYYY-MM-DD HH:MM:SS)"),
    temperature: float = Query(25.0, description="温度"),
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取单小时预测
    
    - **target_datetime**: 目标时间，格式为 YYYY-MM-DD HH:MM:SS
    - **temperature**: 温度
    """
    try:
        logger.info(f"API请求: 获取单小时预测 {target_datetime}")
        
        result = await prediction_service.get_hourly_prediction(
            target_datetime=target_datetime,
            temperature=temperature
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message="单小时预测生成成功"
        )
        
    except (PredictionError, ModelNotFoundError) as e:
        logger.error(f"获取单小时预测失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取单小时预测时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/batch")
async def batch_predict(
    prediction_requests: List[Dict[str, Any]] = Body(..., description="预测请求列表"),
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    批量预测
    
    - **prediction_requests**: 预测请求列表，每个请求包含 datetime 和 temperature
    """
    try:
        logger.info(f"API请求: 批量预测 {len(prediction_requests)} 个请求")
        
        result = await prediction_service.batch_predict(prediction_requests)
        
        return StandardResponse(
            success=True,
            data=result,
            message="批量预测完成"
        )
        
    except (PredictionError, ModelNotFoundError) as e:
        logger.error(f"批量预测失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"批量预测时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/metrics")
async def get_model_metrics(
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取模型评估指标
    """
    try:
        logger.info("API请求: 获取模型评估指标")
        
        result = await prediction_service.get_model_metrics()
        
        return StandardResponse(
            success=True,
            data=result,
            message="模型评估指标获取成功"
        )
        
    except ModelNotFoundError as e:
        logger.error(f"获取模型评估指标失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取模型评估指标时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/load-model")
async def load_model(
    model_path: str = Body(..., description="模型文件路径"),
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    加载预训练模型
    
    - **model_path**: 模型文件路径
    """
    try:
        logger.info(f"API请求: 加载预训练模型 {model_path}")
        
        result = await prediction_service.load_model(model_path)
        
        return StandardResponse(
            success=True,
            data=result,
            message="预训练模型加载成功"
        )
        
    except ModelNotFoundError as e:
        logger.error(f"加载预训练模型失败: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"加载预训练模型时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/evaluate")
async def evaluate_model(
    test_data_path: Optional[str] = Body(None, description="测试数据路径"),
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    评估模型性能
    
    - **test_data_path**: 测试数据路径，如果为空则使用训练数据的一部分
    """
    try:
        logger.info(f"API请求: 评估模型性能 测试数据={test_data_path}")
        
        result = await prediction_service.evaluate_model(test_data_path)
        
        return StandardResponse(
            success=True,
            data=result,
            message="模型性能评估完成"
        )
        
    except PredictionError as e:
        logger.error(f"模型性能评估失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"评估模型性能时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.delete("/cache")
async def clear_prediction_cache(
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    清除预测缓存
    """
    try:
        logger.info("API请求: 清除预测缓存")
        
        result = await prediction_service.clear_cache()
        
        return StandardResponse(
            success=True,
            data=result,
            message="预测缓存清除成功"
        )
        
    except Exception as e:
        logger.error(f"清除预测缓存时发生未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/health")
async def check_prediction_health(
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    检查预测服务健康状态
    """
    try:
        logger.info("API请求: 检查预测服务健康状态")
        
        # 尝试获取模型指标作为健康检查
        try:
            metrics = await prediction_service.get_model_metrics()
            model_available = True
            model_info = metrics
        except ModelNotFoundError:
            model_available = False
            model_info = None
        
        health_status = {
            "status": "healthy" if model_available else "degraded",
            "model_available": model_available,
            "model_info": model_info,
            "checked_at": datetime.now().isoformat()
        }
        
        return StandardResponse(
            success=True,
            data=health_status,
            message="预测服务运行正常" if model_available else "预测服务运行但模型未加载"
        )
        
    except Exception as e:
        logger.error(f"预测服务健康检查失败: {str(e)}")
        
        health_status = {
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.now().isoformat()
        }
        
        return StandardResponse(
            success=False,
            data=health_status,
            message="预测服务异常"
        )


@router.post("/train-sliding-window")
async def train_sliding_window_models(
    start_date: str = Body(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Body(..., description="结束日期 (YYYY-MM-DD)"),
    weeks_before: int = Body(3, description="每次训练使用前几周的数据"),
    validation_split: float = Body(0.2, description="验证集比例"),
    model_params: Optional[Dict[str, Any]] = Body(None, description="模型参数"),
    force_retrain: bool = Body(False, description="是否强制重新训练"),
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    滑动窗口训练模型

    从start_date到end_date，每一天都训练一个模型，使用前3周的数据

    - **start_date**: 开始训练的日期，格式为 YYYY-MM-DD
    - **end_date**: 结束训练的日期，格式为 YYYY-MM-DD
    - **weeks_before**: 每次训练使用前几周的数据
    - **validation_split**: 验证集比例 (0-1)
    - **model_params**: 自定义模型参数
    - **force_retrain**: 是否强制重新训练
    """
    try:
        logger.info(f"API请求: 滑动窗口训练模型 {start_date} 到 {end_date}")

        # 验证日期格式
        from app.utils.helpers import validate_date_format
        start_dt = validate_date_format(start_date)
        end_dt = validate_date_format(end_date)

        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")

        # 计算需要训练的天数
        total_days = (end_dt - start_dt).days + 1
        logger.info(f"将训练 {total_days} 个模型")

        training_results = []
        current_date = start_dt

        while current_date <= end_dt:
            target_date_str = current_date.strftime("%Y-%m-%d")
            logger.info(f"训练目标日期: {target_date_str}")

            try:
                # 为每一天训练模型
                result = await prediction_service.train_model(
                    target_date=target_date_str,
                    weeks_before=weeks_before,
                    validation_split=validation_split,
                    model_params=model_params,
                    force_retrain=force_retrain
                )

                training_results.append({
                    "target_date": target_date_str,
                    "status": "success",
                    "result": result
                })

                logger.info(f"目标日期 {target_date_str} 训练完成")

            except Exception as e:
                logger.error(f"目标日期 {target_date_str} 训练失败: {str(e)}")
                training_results.append({
                    "target_date": target_date_str,
                    "status": "failed",
                    "error": str(e)
                })

            # 移动到下一天
            current_date += timedelta(days=1)

        # 统计结果
        successful_trainings = len([r for r in training_results if r["status"] == "success"])
        failed_trainings = len([r for r in training_results if r["status"] == "failed"])

        summary = {
            "total_models": total_days,
            "successful_trainings": successful_trainings,
            "failed_trainings": failed_trainings,
            "training_results": training_results,
            "completed_at": datetime.now().isoformat()
        }

        logger.info(f"滑动窗口训练完成: 成功 {successful_trainings}/{total_days}")

        return StandardResponse(
            success=True,
            data=summary,
            message=f"滑动窗口训练完成，成功训练 {successful_trainings}/{total_days} 个模型"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"滑动窗口训练失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"滑动窗口训练过程中发生错误: {str(e)}")


@router.get("/model-fitting-history")
async def get_model_fitting_history(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    prediction_service: PredictionService = Depends(get_prediction_service),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取模型拟合历史信息

    返回每日模型训练的详细信息，包括训练数据范围、模型性能等

    - **start_date**: 查询开始日期，格式为 YYYY-MM-DD
    - **end_date**: 查询结束日期，格式为 YYYY-MM-DD
    """
    try:
        logger.info(f"API请求: 获取模型拟合历史 {start_date} 到 {end_date}")

        # 如果没有指定日期范围，默认返回最近7天的数据
        if not start_date or not end_date:
            from datetime import datetime, timedelta
            end_dt = datetime.strptime("2022-06-30", "%Y-%m-%d")  # 使用配置中的基准日期
            start_dt = end_dt - timedelta(days=6)  # 最近7天
            start_date = start_dt.strftime("%Y-%m-%d")
            end_date = end_dt.strftime("%Y-%m-%d")

        # 验证日期格式
        from app.utils.helpers import validate_date_format
        start_dt = validate_date_format(start_date)
        end_dt = validate_date_format(end_date)

        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")

        fitting_history = []
        current_date = start_dt

        while current_date <= end_dt:
            target_date_str = current_date.strftime("%Y-%m-%d")

            try:
                # 获取该日期的模型评估指标
                metrics = await prediction_service.get_model_metrics(target_date=target_date_str)

                # 计算训练数据范围
                from app.utils.helpers import calculate_date_range
                train_start, train_end = calculate_date_range(target_date_str, weeks_before=3)

                fitting_info = {
                    "target_date": target_date_str,
                    "training_data_range": {
                        "start_date": train_start.strftime("%Y-%m-%d"),
                        "end_date": train_end.strftime("%Y-%m-%d"),
                        "days": (train_end - train_start).days + 1
                    },
                    "model_performance": metrics.get("metrics", {}),
                    "training_info": metrics.get("training_info", {}),
                    "model_available": True
                }

            except ModelNotFoundError:
                # 如果模型不存在，记录但不报错
                from app.utils.helpers import calculate_date_range
                train_start, train_end = calculate_date_range(target_date_str, weeks_before=3)

                fitting_info = {
                    "target_date": target_date_str,
                    "training_data_range": {
                        "start_date": train_start.strftime("%Y-%m-%d"),
                        "end_date": train_end.strftime("%Y-%m-%d"),
                        "days": (train_end - train_start).days + 1
                    },
                    "model_performance": None,
                    "training_info": None,
                    "model_available": False
                }

            fitting_history.append(fitting_info)
            current_date += timedelta(days=1)

        summary = {
            "query_range": {
                "start_date": start_date,
                "end_date": end_date,
                "total_days": len(fitting_history)
            },
            "available_models": len([h for h in fitting_history if h["model_available"]]),
            "missing_models": len([h for h in fitting_history if not h["model_available"]]),
            "fitting_history": fitting_history,
            "generated_at": datetime.now().isoformat()
        }

        return StandardResponse(
            success=True,
            data=summary,
            message=f"获取模型拟合历史成功，共 {len(fitting_history)} 天数据"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模型拟合历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型拟合历史过程中发生错误: {str(e)}")


@router.get("/pretrained-models")
async def get_pretrained_models(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    logger: logging.Logger = Depends(get_logger)
):
    """
    获取预训练模型数据

    从预训练的JSON文件中读取模型拟合历史，无需实时训练

    - **start_date**: 筛选开始日期，格式为 YYYY-MM-DD
    - **end_date**: 筛选结束日期，格式为 YYYY-MM-DD
    """
    try:
        logger.info(f"API请求: 获取预训练模型数据 {start_date} 到 {end_date}")

        # 查找最新的预训练数据文件
        import os
        import json
        from pathlib import Path

        data_dir = Path("data/pretrained_models")
        if not data_dir.exists():
            raise HTTPException(status_code=404, detail="预训练数据目录不存在，请先运行预训练脚本")

        # 查找最新的预训练文件
        json_files = list(data_dir.glob("pretrained_models_*.json"))
        if not json_files:
            raise HTTPException(status_code=404, detail="未找到预训练数据文件，请先运行预训练脚本")

        # 选择最新的文件
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"使用预训练数据文件: {latest_file}")

        # 读取预训练数据
        with open(latest_file, 'r', encoding='utf-8') as f:
            pretrained_data = json.load(f)

        # 筛选日期范围
        models = pretrained_data.get("models", {})

        if start_date or end_date:
            from app.utils.helpers import validate_date_format

            filtered_models = {}
            for target_date, model_info in models.items():
                target_dt = validate_date_format(target_date)

                # 检查日期范围
                include = True
                if start_date:
                    start_dt = validate_date_format(start_date)
                    if target_dt < start_dt:
                        include = False

                if end_date and include:
                    end_dt = validate_date_format(end_date)
                    if target_dt > end_dt:
                        include = False

                if include:
                    filtered_models[target_date] = model_info

            models = filtered_models

        # 计算统计信息
        total_models = len(models)
        available_models = len([m for m in models.values() if m.get("model_available", False)])
        missing_models = total_models - available_models

        # 构建响应
        response_data = {
            "metadata": pretrained_data.get("metadata", {}),
            "query_range": {
                "start_date": start_date,
                "end_date": end_date,
                "total_days": total_models
            },
            "available_models": available_models,
            "missing_models": missing_models,
            "models": models,
            "generated_at": datetime.now().isoformat()
        }

        logger.info(f"返回预训练模型数据: {total_models} 个模型，{available_models} 个可用")

        return StandardResponse(
            success=True,
            data=response_data,
            message=f"获取预训练模型数据成功，共 {total_models} 个模型"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取预训练模型数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取预训练模型数据过程中发生错误: {str(e)}")
