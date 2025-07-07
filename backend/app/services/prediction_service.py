"""
预测服务
Prediction Service
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import asyncio

from app.core.ml.trainer import ModelTrainer
from app.core.ml.predictor import PowerPredictor
from app.core.ml.model import PowerPredictionModel
from app.models.schemas import PredictionResult, ModelMetrics, TrainingInfo
from app.utils.exceptions import PredictionError, ModelTrainingError, ModelNotFoundError
from app.utils.helpers import convert_numpy_types, format_prediction_results
from app.utils.constants import TARGET_DATE, SUCCESS_MESSAGES, ERROR_MESSAGES
from app.config import settings

logger = logging.getLogger("power_prediction")


class PredictionService:
    """预测服务类"""
    
    def __init__(self):
        """初始化预测服务"""
        self.trainer = ModelTrainer()
        self.predictor = PowerPredictor()
        self._model_cache: Dict[str, PowerPredictionModel] = {}
        self._prediction_cache: Dict[str, Any] = {}
        
    async def train_model(
        self,
        target_date: Optional[str] = None,
        weeks_before: int = 3,
        validation_split: float = 0.2,
        model_params: Optional[Dict[str, Any]] = None,
        force_retrain: bool = False
    ) -> Dict[str, Any]:
        """训练模型
        
        Args:
            target_date: 目标预测日期
            weeks_before: 使用目标日期前几周的数据
            validation_split: 验证集比例
            model_params: 模型参数
            force_retrain: 是否强制重新训练
            
        Returns:
            训练结果
        """
        try:
            target_date = target_date or settings.target_date
            
            logger.info(f"开始训练模型，目标日期: {target_date}")
            
            # 检查是否需要重新训练
            cache_key = f"model_{target_date}_{weeks_before}_{validation_split}"
            if not force_retrain and cache_key in self._model_cache:
                logger.info("使用缓存的模型")
                model = self._model_cache[cache_key]
                return model.get_model_info()
            
            # 执行模型训练
            training_result = await self.trainer.train_model(
                target_date=target_date,
                weeks_before=weeks_before,
                validation_split=validation_split,
                model_params=model_params
            )
            
            # 获取训练好的模型
            trained_model = self.trainer.get_model()
            if trained_model is None:
                raise ModelTrainingError("模型训练完成但无法获取模型实例")
            
            # 缓存模型
            self._model_cache[cache_key] = trained_model
            
            # 更新预测器的模型和数据处理器
            self.predictor.model = trained_model
            self.predictor.data_processor = self.trainer.data_processor
            
            # 格式化训练结果
            formatted_result = await self._format_training_result(training_result)
            
            logger.info("模型训练完成")
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            if isinstance(e, ModelTrainingError):
                raise
            else:
                raise ModelTrainingError(f"模型训练过程中发生错误: {str(e)}")
    
    async def get_prediction(
        self,
        target_date: Optional[str] = None,
        temperature_forecast: Optional[List[float]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """获取预测结果
        
        Args:
            target_date: 目标日期
            temperature_forecast: 温度预报
            use_cache: 是否使用缓存
            
        Returns:
            预测结果
        """
        try:
            target_date = target_date or settings.target_date
            
            logger.info(f"获取预测结果，目标日期: {target_date}")
            
            # 检查缓存
            cache_key = f"prediction_{target_date}_{hash(str(temperature_forecast))}"
            if use_cache and cache_key in self._prediction_cache:
                logger.info("从缓存返回预测结果")
                return self._prediction_cache[cache_key]
            
            # 确保预测器有可用的模型
            if not self.predictor.is_ready():
                # 尝试加载或训练模型
                await self._ensure_model_available()
            
            # 进行预测
            predictions = await self.predictor.predict_daily_usage(
                target_date=target_date,
                temperature_forecast=temperature_forecast
            )
            
            # 获取模型信息
            model_info = self.predictor.get_model_info()
            prediction_metadata = self.predictor.get_prediction_metadata()
            
            # 格式化预测结果
            result = {
                "predictions": predictions,
                "model_metrics": await self._extract_model_metrics(model_info),
                "training_info": await self._extract_training_info(model_info),
                "target_date": target_date,
                "prediction_metadata": prediction_metadata,
                "generated_at": datetime.now().isoformat()
            }
            
            # 缓存结果
            if use_cache:
                self._prediction_cache[cache_key] = result
            
            logger.info(f"预测结果生成成功，共 {len(predictions)} 个小时")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"获取预测结果失败: {str(e)}")
            if isinstance(e, (PredictionError, ModelNotFoundError)):
                raise
            else:
                raise PredictionError(f"获取预测结果过程中发生错误: {str(e)}")
    
    async def get_hourly_prediction(
        self,
        target_datetime: str,
        temperature: float = 25.0
    ) -> Dict[str, Any]:
        """获取单小时预测
        
        Args:
            target_datetime: 目标时间
            temperature: 温度
            
        Returns:
            单小时预测结果
        """
        try:
            logger.info(f"获取单小时预测: {target_datetime}")
            
            # 确保预测器有可用的模型
            if not self.predictor.is_ready():
                await self._ensure_model_available()
            
            # 进行单小时预测
            result = await self.predictor.predict_hourly_usage(target_datetime, temperature)
            
            logger.info(f"单小时预测完成: {result['predicted_usage']:.2f}")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"单小时预测失败: {str(e)}")
            if isinstance(e, (PredictionError, ModelNotFoundError)):
                raise
            else:
                raise PredictionError(f"单小时预测过程中发生错误: {str(e)}")
    
    async def batch_predict(
        self,
        prediction_requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """批量预测
        
        Args:
            prediction_requests: 预测请求列表
            
        Returns:
            批量预测结果
        """
        try:
            logger.info(f"开始批量预测，请求数量: {len(prediction_requests)}")
            
            # 确保预测器有可用的模型
            if not self.predictor.is_ready():
                await self._ensure_model_available()
            
            # 进行批量预测
            results = await self.predictor.batch_predict(prediction_requests)
            
            # 统计结果
            successful_predictions = [r for r in results if 'error' not in r]
            failed_predictions = [r for r in results if 'error' in r]
            
            batch_result = {
                "results": results,
                "summary": {
                    "total_requests": len(prediction_requests),
                    "successful_predictions": len(successful_predictions),
                    "failed_predictions": len(failed_predictions),
                    "success_rate": len(successful_predictions) / len(prediction_requests) * 100 if prediction_requests else 0
                },
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"批量预测完成，成功: {len(successful_predictions)}, 失败: {len(failed_predictions)}")
            
            return convert_numpy_types(batch_result)
            
        except Exception as e:
            logger.error(f"批量预测失败: {str(e)}")
            if isinstance(e, (PredictionError, ModelNotFoundError)):
                raise
            else:
                raise PredictionError(f"批量预测过程中发生错误: {str(e)}")
    
    async def get_model_metrics(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """获取模型评估指标

        Args:
            target_date: 目标日期，如果指定则获取该日期对应的模型指标

        Returns:
            模型评估指标
        """
        try:
            target_date = target_date or settings.target_date
            logger.info(f"获取模型评估指标，目标日期: {target_date}")

            # 检查是否有该日期的缓存模型
            cache_key = f"model_{target_date}_3_0.2"  # 使用默认参数构建缓存键

            if cache_key in self._model_cache:
                logger.info("使用缓存的模型指标")
                model = self._model_cache[cache_key]
                model_info = model.get_model_info()
            else:
                # 如果没有缓存，尝试训练该日期的模型
                logger.info(f"没有找到目标日期 {target_date} 的模型，开始训练")
                await self.train_model(target_date=target_date)

                if cache_key in self._model_cache:
                    model = self._model_cache[cache_key]
                    model_info = model.get_model_info()
                else:
                    raise ModelNotFoundError(f"无法获取目标日期 {target_date} 的模型")
            
            if not model_info.get("is_trained"):
                raise ModelNotFoundError(f"目标日期 {target_date} 的模型尚未训练")
            
            # 提取训练信息中的指标
            training_info = model_info.get("training_info", {})
            
            metrics = {
                "model_type": model_info.get("model_type", "XGBoost"),
                "training_metrics": training_info.get("train_metrics", {}),
                "validation_metrics": training_info.get("val_metrics", {}),
                "cross_validation": training_info.get("cv_scores", {}),
                "feature_importance": model_info.get("feature_importance", {}),
                "model_params": model_info.get("model_params", {}),
                "training_time": training_info.get("training_time", 0),
                "training_samples": training_info.get("training_samples", 0),
                "retrieved_at": datetime.now().isoformat()
            }
            
            logger.info("模型评估指标获取成功")
            
            return convert_numpy_types(metrics)
            
        except Exception as e:
            logger.error(f"获取模型评估指标失败: {str(e)}")
            if isinstance(e, ModelNotFoundError):
                raise
            else:
                raise PredictionError(f"获取模型评估指标过程中发生错误: {str(e)}")
    
    async def load_model(self, model_path: str) -> Dict[str, Any]:
        """加载预训练模型
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            加载结果
        """
        try:
            logger.info(f"加载预训练模型: {model_path}")
            
            # 加载模型到预测器
            success = await self.predictor.load_model(model_path)
            
            if not success:
                raise ModelNotFoundError(f"无法加载模型: {model_path}")
            
            # 获取模型信息
            model_info = self.predictor.get_model_info()
            
            result = {
                "model_path": model_path,
                "load_success": success,
                "model_info": model_info,
                "loaded_at": datetime.now().isoformat()
            }
            
            logger.info("预训练模型加载成功")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"加载预训练模型失败: {str(e)}")
            if isinstance(e, ModelNotFoundError):
                raise
            else:
                raise PredictionError(f"加载预训练模型过程中发生错误: {str(e)}")
    
    async def evaluate_model(self, test_data_path: Optional[str] = None) -> Dict[str, Any]:
        """评估模型性能
        
        Args:
            test_data_path: 测试数据路径
            
        Returns:
            评估结果
        """
        try:
            logger.info("开始评估模型性能")
            
            # 使用训练器进行模型评估
            evaluation_result = await self.trainer.evaluate_model(test_data_path)
            
            logger.info("模型性能评估完成")
            
            return convert_numpy_types(evaluation_result)
            
        except Exception as e:
            logger.error(f"模型性能评估失败: {str(e)}")
            raise PredictionError(f"模型性能评估过程中发生错误: {str(e)}")
    
    async def clear_cache(self) -> Dict[str, Any]:
        """清除缓存
        
        Returns:
            清除结果
        """
        try:
            model_cache_size = len(self._model_cache)
            prediction_cache_size = len(self._prediction_cache)
            
            self._model_cache.clear()
            self._prediction_cache.clear()
            
            result = {
                "cleared_model_cache": model_cache_size,
                "cleared_prediction_cache": prediction_cache_size,
                "total_cleared": model_cache_size + prediction_cache_size,
                "cleared_at": datetime.now().isoformat()
            }
            
            logger.info(f"预测服务缓存已清除，共 {result['total_cleared']} 个项目")
            
            return result
            
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            raise PredictionError(f"清除缓存过程中发生错误: {str(e)}")
    
    async def _ensure_model_available(self) -> None:
        """确保有可用的模型"""
        if not self.predictor.is_ready():
            # 尝试训练新模型
            logger.info("没有可用模型，开始训练新模型")
            await self.train_model()
            
            if not self.predictor.is_ready():
                raise ModelNotFoundError("无法获取可用的模型")
    
    async def _format_training_result(self, training_result: Dict[str, Any]) -> Dict[str, Any]:
        """格式化训练结果"""
        return {
            "training_completed": True,
            "target_date": training_result.get("target_date"),
            "training_time": training_result.get("total_training_time"),
            "model_path": training_result.get("model_path"),
            "data_info": training_result.get("data_info"),
            "training_metrics": training_result.get("training_result", {}).get("train_metrics", {}),
            "validation_metrics": training_result.get("training_result", {}).get("val_metrics", {}),
            "feature_importance": training_result.get("training_result", {}).get("feature_importance", {}),
            "completed_at": training_result.get("completed_at")
        }
    
    async def _extract_model_metrics(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """提取模型指标"""
        training_info = model_info.get("training_info", {})
        
        return {
            "mae": training_info.get("train_metrics", {}).get("mae", 0),
            "rmse": training_info.get("train_metrics", {}).get("rmse", 0),
            "r2_score": training_info.get("train_metrics", {}).get("r2_score", 0),
            "mape": training_info.get("train_metrics", {}).get("mape", 0)
        }
    
    async def _extract_training_info(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """提取训练信息"""
        training_info = model_info.get("training_info", {})
        
        return {
            "training_start_date": datetime.fromisoformat(training_info.get("trained_at", datetime.now().isoformat())),
            "training_end_date": datetime.fromisoformat(training_info.get("trained_at", datetime.now().isoformat())),
            "training_samples": training_info.get("training_samples", 0),
            "model_type": model_info.get("model_type", "XGBoost"),
            "training_time": training_info.get("training_time", 0),
            "model_params": model_info.get("model_params", {})
        }
