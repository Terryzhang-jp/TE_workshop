"""
预测器
Predictor
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.core.data.processor import DataProcessor
from app.core.ml.model import PowerPredictionModel
from app.config import settings
from app.utils.exceptions import PredictionError, ModelNotFoundError
from app.utils.helpers import format_prediction_results, calculate_confidence_interval
from app.utils.constants import TARGET_DATE, MAX_PREDICTION_HOURS

logger = logging.getLogger("power_prediction")


class PowerPredictor:
    """电力需求预测器类"""
    
    def __init__(self, model: Optional[PowerPredictionModel] = None):
        """初始化预测器
        
        Args:
            model: 训练好的模型，如果为None则需要后续加载
        """
        self.model = model
        self.data_processor = DataProcessor()
        self.last_predictions: Optional[List[Dict[str, Any]]] = None
        self.prediction_metadata: Dict[str, Any] = {}
        
    async def predict_daily_usage(
        self,
        target_date: Optional[str] = None,
        temperature_forecast: Optional[List[float]] = None
    ) -> List[Dict[str, Any]]:
        """预测日电力使用量
        
        Args:
            target_date: 目标日期，格式为 YYYY-MM-DD
            temperature_forecast: 24小时温度预报，如果为None则使用默认值
            
        Returns:
            24小时预测结果列表
        """
        try:
            if self.model is None or not self.model.is_trained:
                raise ModelNotFoundError("模型尚未加载或训练")
            
            # 使用配置中的目标日期或传入的日期
            target_date = target_date or settings.target_date
            
            logger.info(f"开始预测日电力使用量，目标日期: {target_date}")
            
            # 创建预测数据模板
            prediction_template = await self.data_processor.create_prediction_template(target_date)
            
            # 如果提供了温度预报，更新温度数据
            if temperature_forecast:
                if len(temperature_forecast) != 24:
                    raise PredictionError(f"温度预报数据长度应为24小时，实际为 {len(temperature_forecast)}")
                
                prediction_template['temp'] = temperature_forecast
                logger.info("使用提供的温度预报数据")
            else:
                logger.info("使用默认温度数据")
            
            # 处理预测数据
            X_pred = await self.data_processor.process_prediction_data(prediction_template)
            
            # 进行预测
            predictions = await self.model.predict(X_pred)
            
            # 格式化预测结果
            hours = list(range(24))
            formatted_results = format_prediction_results(predictions, hours)
            
            # 保存预测结果
            self.last_predictions = formatted_results
            
            # 保存预测元数据
            self.prediction_metadata = {
                "target_date": target_date,
                "prediction_time": datetime.now().isoformat(),
                "model_info": self.model.get_model_info(),
                "temperature_source": "forecast" if temperature_forecast else "default",
                "total_predicted_usage": float(np.sum(predictions)),
                "peak_hour": int(np.argmax(predictions)),
                "peak_usage": float(np.max(predictions)),
                "min_hour": int(np.argmin(predictions)),
                "min_usage": float(np.min(predictions))
            }
            
            logger.info(f"预测完成，总用电量: {self.prediction_metadata['total_predicted_usage']:.2f}")
            logger.info(f"峰值时段: {self.prediction_metadata['peak_hour']}时，用电量: {self.prediction_metadata['peak_usage']:.2f}")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"日电力使用量预测失败: {str(e)}")
            if isinstance(e, (PredictionError, ModelNotFoundError)):
                raise
            else:
                raise PredictionError(f"预测过程中发生错误: {str(e)}")
    
    async def predict_hourly_usage(
        self,
        target_datetime: str,
        temperature: float = 25.0
    ) -> Dict[str, Any]:
        """预测单小时电力使用量
        
        Args:
            target_datetime: 目标时间，格式为 YYYY-MM-DD HH:MM:SS
            temperature: 温度
            
        Returns:
            单小时预测结果
        """
        try:
            if self.model is None or not self.model.is_trained:
                raise ModelNotFoundError("模型尚未加载或训练")
            
            logger.info(f"开始预测单小时电力使用量，目标时间: {target_datetime}")
            
            # 解析目标时间
            target_dt = datetime.fromisoformat(target_datetime.replace('Z', '+00:00'))
            
            # 创建单小时数据
            import pandas as pd
            single_hour_data = pd.DataFrame({
                'time': [target_dt],
                'temp': [temperature]
            })
            
            # 处理数据
            X_pred = await self.data_processor.process_prediction_data(single_hour_data)
            
            # 进行预测
            prediction = await self.model.predict(X_pred)
            
            # 计算置信区间
            confidence_interval = calculate_confidence_interval(prediction)[0]
            
            result = {
                "datetime": target_datetime,
                "hour": target_dt.hour,
                "predicted_usage": float(prediction[0]),
                "confidence_interval": confidence_interval,
                "temperature": temperature,
                "prediction_time": datetime.now().isoformat()
            }
            
            logger.info(f"单小时预测完成，预测值: {result['predicted_usage']:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"单小时电力使用量预测失败: {str(e)}")
            if isinstance(e, (PredictionError, ModelNotFoundError)):
                raise
            else:
                raise PredictionError(f"单小时预测过程中发生错误: {str(e)}")
    
    async def batch_predict(
        self,
        prediction_requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """批量预测
        
        Args:
            prediction_requests: 预测请求列表，每个请求包含时间和温度信息
            
        Returns:
            批量预测结果列表
        """
        try:
            if self.model is None or not self.model.is_trained:
                raise ModelNotFoundError("模型尚未加载或训练")
            
            logger.info(f"开始批量预测，请求数量: {len(prediction_requests)}")
            
            if len(prediction_requests) > MAX_PREDICTION_HOURS:
                raise PredictionError(f"批量预测请求数量超过限制: {len(prediction_requests)} > {MAX_PREDICTION_HOURS}")
            
            results = []
            
            for i, request in enumerate(prediction_requests):
                try:
                    target_datetime = request.get("datetime")
                    temperature = request.get("temperature", 25.0)
                    
                    if not target_datetime:
                        raise PredictionError(f"第 {i+1} 个请求缺少datetime参数")
                    
                    # 进行单小时预测
                    result = await self.predict_hourly_usage(target_datetime, temperature)
                    result["request_index"] = i
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"第 {i+1} 个预测请求失败: {str(e)}")
                    error_result = {
                        "request_index": i,
                        "error": str(e),
                        "datetime": request.get("datetime"),
                        "temperature": request.get("temperature")
                    }
                    results.append(error_result)
            
            logger.info(f"批量预测完成，成功: {len([r for r in results if 'error' not in r])}, 失败: {len([r for r in results if 'error' in r])}")
            
            return results
            
        except Exception as e:
            logger.error(f"批量预测失败: {str(e)}")
            if isinstance(e, (PredictionError, ModelNotFoundError)):
                raise
            else:
                raise PredictionError(f"批量预测过程中发生错误: {str(e)}")
    
    async def load_model(self, model_path: str) -> bool:
        """加载模型
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            加载是否成功
        """
        try:
            self.model = PowerPredictionModel()
            success = await self.model.load_model(model_path)
            
            if success:
                logger.info(f"预测器已加载模型: {model_path}")
                
                # 重新初始化数据处理器以匹配模型
                self.data_processor = DataProcessor()
                
                # 如果模型已训练，需要确保数据处理器也已拟合
                # 这里可能需要加载训练时的数据处理器状态
                # 简化处理：假设使用相同的数据处理逻辑
                
            return success
            
        except Exception as e:
            logger.error(f"预测器加载模型失败: {str(e)}")
            return False
    
    def get_last_predictions(self) -> Optional[List[Dict[str, Any]]]:
        """获取最后一次预测结果"""
        return self.last_predictions
    
    def get_prediction_metadata(self) -> Dict[str, Any]:
        """获取预测元数据"""
        return self.prediction_metadata
    
    def is_ready(self) -> bool:
        """检查预测器是否准备就绪"""
        return (
            self.model is not None and 
            self.model.is_trained and 
            self.data_processor is not None
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if self.model is None:
            return {"status": "模型未加载"}
        
        return self.model.get_model_info()
