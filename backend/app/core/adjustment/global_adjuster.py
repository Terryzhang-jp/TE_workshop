"""
全局调整器
Global Adjuster
"""

import numpy as np
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.models.schemas import PredictionResult, GlobalAdjustment
from app.utils.exceptions import AdjustmentError
from app.utils.constants import MIN_ADJUSTMENT_PERCENTAGE, MAX_ADJUSTMENT_PERCENTAGE
from app.utils.helpers import convert_numpy_types

logger = logging.getLogger("power_prediction")


class GlobalAdjuster:
    """全局预测调整器"""
    
    def __init__(self):
        """初始化全局调整器"""
        self.adjustment_history: List[Dict[str, Any]] = []
        
    async def apply_adjustment(
        self,
        predictions: List[PredictionResult],
        adjustment: GlobalAdjustment
    ) -> List[PredictionResult]:
        """应用全局调整
        
        Args:
            predictions: 原始预测结果列表
            adjustment: 全局调整参数
            
        Returns:
            调整后的预测结果列表
        """
        try:
            logger.info(f"开始应用全局调整: {adjustment.start_hour}-{adjustment.end_hour}时, {adjustment.direction} {adjustment.percentage}%")
            
            # 验证调整参数
            await self._validate_adjustment(adjustment)
            
            # 验证预测数据
            await self._validate_predictions(predictions)
            
            # 创建调整后的预测结果副本
            adjusted_predictions = []
            
            for pred in predictions:
                # 创建新的预测结果对象
                adjusted_pred = PredictionResult(
                    hour=pred.hour,
                    predicted_usage=pred.predicted_usage,
                    confidence_interval=pred.confidence_interval,
                    original_prediction=pred.original_prediction or pred.predicted_usage
                )
                
                # 检查是否在调整范围内
                if adjustment.start_hour <= pred.hour <= adjustment.end_hour:
                    # 计算调整后的值
                    adjustment_factor = await self._calculate_adjustment_factor(
                        adjustment.direction, adjustment.percentage
                    )
                    
                    adjusted_value = pred.predicted_usage * adjustment_factor
                    
                    # 确保调整后的值为正数
                    adjusted_value = max(0, adjusted_value)
                    
                    # 更新预测值
                    adjusted_pred.predicted_usage = adjusted_value
                    
                    # 调整置信区间
                    adjusted_pred.confidence_interval = await self._adjust_confidence_interval(
                        pred.confidence_interval, adjustment_factor
                    )
                
                adjusted_predictions.append(adjusted_pred)
            
            # 记录调整历史
            adjustment_record = await self._create_adjustment_record(
                adjustment, predictions, adjusted_predictions
            )
            self.adjustment_history.append(adjustment_record)
            
            logger.info(f"全局调整完成，调整了 {adjustment.end_hour - adjustment.start_hour + 1} 个小时的预测")
            
            return adjusted_predictions
            
        except Exception as e:
            logger.error(f"全局调整失败: {str(e)}")
            if isinstance(e, AdjustmentError):
                raise
            else:
                raise AdjustmentError(f"全局调整过程中发生错误: {str(e)}")
    
    async def apply_multiple_adjustments(
        self,
        predictions: List[PredictionResult],
        adjustments: List[GlobalAdjustment]
    ) -> List[PredictionResult]:
        """应用多个全局调整
        
        Args:
            predictions: 原始预测结果列表
            adjustments: 全局调整参数列表
            
        Returns:
            调整后的预测结果列表
        """
        try:
            logger.info(f"开始应用 {len(adjustments)} 个全局调整")
            
            current_predictions = predictions.copy()
            
            for i, adjustment in enumerate(adjustments):
                logger.info(f"应用第 {i+1} 个调整: {adjustment.start_hour}-{adjustment.end_hour}时")
                current_predictions = await self.apply_adjustment(current_predictions, adjustment)
            
            logger.info("多个全局调整完成")
            
            return current_predictions
            
        except Exception as e:
            logger.error(f"多个全局调整失败: {str(e)}")
            raise AdjustmentError(f"多个全局调整过程中发生错误: {str(e)}")
    
    async def calculate_adjustment_impact(
        self,
        original_predictions: List[PredictionResult],
        adjusted_predictions: List[PredictionResult]
    ) -> Dict[str, Any]:
        """计算调整影响
        
        Args:
            original_predictions: 原始预测结果
            adjusted_predictions: 调整后预测结果
            
        Returns:
            调整影响分析结果
        """
        try:
            logger.info("开始计算调整影响")
            
            if len(original_predictions) != len(adjusted_predictions):
                raise AdjustmentError("原始预测和调整后预测的长度不匹配")
            
            # 计算总体影响
            original_total = sum(pred.predicted_usage for pred in original_predictions)
            adjusted_total = sum(pred.predicted_usage for pred in adjusted_predictions)
            total_change = adjusted_total - original_total
            total_change_percentage = (total_change / original_total) * 100 if original_total > 0 else 0
            
            # 计算逐小时影响
            hourly_impacts = []
            for orig, adj in zip(original_predictions, adjusted_predictions):
                change = adj.predicted_usage - orig.predicted_usage
                change_percentage = (change / orig.predicted_usage) * 100 if orig.predicted_usage > 0 else 0
                
                hourly_impacts.append({
                    "hour": orig.hour,
                    "original_value": orig.predicted_usage,
                    "adjusted_value": adj.predicted_usage,
                    "absolute_change": change,
                    "percentage_change": change_percentage,
                    "was_adjusted": abs(change) > 0.01  # 考虑浮点精度
                })
            
            # 统计调整范围
            adjusted_hours = [impact for impact in hourly_impacts if impact["was_adjusted"]]
            
            # 计算峰值影响
            peak_impact = max(hourly_impacts, key=lambda x: abs(x["absolute_change"]))
            
            impact_analysis = {
                "total_impact": {
                    "original_total": original_total,
                    "adjusted_total": adjusted_total,
                    "absolute_change": total_change,
                    "percentage_change": total_change_percentage
                },
                "hourly_impacts": hourly_impacts,
                "adjustment_summary": {
                    "total_hours_adjusted": len(adjusted_hours),
                    "adjustment_range": {
                        "start_hour": min(impact["hour"] for impact in adjusted_hours) if adjusted_hours else None,
                        "end_hour": max(impact["hour"] for impact in adjusted_hours) if adjusted_hours else None
                    },
                    "peak_impact": peak_impact,
                    "average_change": np.mean([impact["absolute_change"] for impact in adjusted_hours]) if adjusted_hours else 0,
                    "average_percentage_change": np.mean([impact["percentage_change"] for impact in adjusted_hours]) if adjusted_hours else 0
                },
                "analysis_time": datetime.now().isoformat()
            }
            
            logger.info(f"调整影响计算完成，总变化: {total_change:.2f} ({total_change_percentage:.1f}%)")
            
            return convert_numpy_types(impact_analysis)
            
        except Exception as e:
            logger.error(f"调整影响计算失败: {str(e)}")
            raise AdjustmentError(f"调整影响计算过程中发生错误: {str(e)}")
    
    async def optimize_adjustment(
        self,
        predictions: List[PredictionResult],
        target_total: float,
        adjustment_hours: Optional[List[int]] = None
    ) -> GlobalAdjustment:
        """优化调整参数以达到目标总量
        
        Args:
            predictions: 原始预测结果
            target_total: 目标总用电量
            adjustment_hours: 允许调整的小时列表，如果为None则使用所有小时
            
        Returns:
            优化后的调整参数
        """
        try:
            logger.info(f"开始优化调整参数，目标总量: {target_total}")
            
            current_total = sum(pred.predicted_usage for pred in predictions)
            required_change = target_total - current_total
            required_change_percentage = (required_change / current_total) * 100 if current_total > 0 else 0
            
            # 确定调整范围
            if adjustment_hours is None:
                start_hour = 0
                end_hour = 23
            else:
                start_hour = min(adjustment_hours)
                end_hour = max(adjustment_hours)
            
            # 确定调整方向
            direction = "increase" if required_change > 0 else "decrease"
            
            # 计算所需的调整百分比
            adjustment_percentage = abs(required_change_percentage)
            
            # 限制调整百分比在允许范围内
            adjustment_percentage = max(MIN_ADJUSTMENT_PERCENTAGE, 
                                      min(MAX_ADJUSTMENT_PERCENTAGE, adjustment_percentage))
            
            optimized_adjustment = GlobalAdjustment(
                start_hour=start_hour,
                end_hour=end_hour,
                direction=direction,
                percentage=adjustment_percentage
            )
            
            logger.info(f"调整参数优化完成: {direction} {adjustment_percentage:.1f}% ({start_hour}-{end_hour}时)")
            
            return optimized_adjustment
            
        except Exception as e:
            logger.error(f"调整参数优化失败: {str(e)}")
            raise AdjustmentError(f"调整参数优化过程中发生错误: {str(e)}")
    
    async def _validate_adjustment(self, adjustment: GlobalAdjustment) -> None:
        """验证调整参数"""
        if adjustment.start_hour > adjustment.end_hour:
            raise AdjustmentError("开始小时不能大于结束小时")
        
        if not (0 <= adjustment.start_hour <= 23):
            raise AdjustmentError(f"开始小时无效: {adjustment.start_hour}")
        
        if not (0 <= adjustment.end_hour <= 23):
            raise AdjustmentError(f"结束小时无效: {adjustment.end_hour}")
        
        if adjustment.direction not in ["increase", "decrease"]:
            raise AdjustmentError(f"调整方向无效: {adjustment.direction}")
        
        if not (MIN_ADJUSTMENT_PERCENTAGE <= adjustment.percentage <= MAX_ADJUSTMENT_PERCENTAGE):
            raise AdjustmentError(
                f"调整百分比超出范围: {adjustment.percentage}, "
                f"应在 {MIN_ADJUSTMENT_PERCENTAGE} 到 {MAX_ADJUSTMENT_PERCENTAGE} 之间"
            )
    
    async def _validate_predictions(self, predictions: List[PredictionResult]) -> None:
        """验证预测数据"""
        if not predictions:
            raise AdjustmentError("预测数据为空")
        
        hours = [pred.hour for pred in predictions]
        if len(set(hours)) != len(hours):
            raise AdjustmentError("预测数据包含重复的小时")
        
        for pred in predictions:
            if pred.predicted_usage < 0:
                raise AdjustmentError(f"预测值不能为负数: {pred.hour}时 = {pred.predicted_usage}")
    
    async def _calculate_adjustment_factor(self, direction: str, percentage: float) -> float:
        """计算调整因子"""
        if direction == "increase":
            return 1.0 + (percentage / 100.0)
        elif direction == "decrease":
            return 1.0 - (percentage / 100.0)
        else:
            raise AdjustmentError(f"未知的调整方向: {direction}")
    
    async def _adjust_confidence_interval(
        self, 
        original_interval: tuple, 
        adjustment_factor: float
    ) -> tuple:
        """调整置信区间"""
        lower, upper = original_interval
        adjusted_lower = max(0, lower * adjustment_factor)
        adjusted_upper = upper * adjustment_factor
        return (adjusted_lower, adjusted_upper)
    
    async def _create_adjustment_record(
        self,
        adjustment: GlobalAdjustment,
        original_predictions: List[PredictionResult],
        adjusted_predictions: List[PredictionResult]
    ) -> Dict[str, Any]:
        """创建调整记录"""
        original_total = sum(pred.predicted_usage for pred in original_predictions)
        adjusted_total = sum(pred.predicted_usage for pred in adjusted_predictions)
        
        return {
            "adjustment_id": len(self.adjustment_history) + 1,
            "adjustment_params": {
                "start_hour": adjustment.start_hour,
                "end_hour": adjustment.end_hour,
                "direction": adjustment.direction,
                "percentage": adjustment.percentage
            },
            "impact": {
                "original_total": original_total,
                "adjusted_total": adjusted_total,
                "total_change": adjusted_total - original_total,
                "percentage_change": ((adjusted_total - original_total) / original_total) * 100 if original_total > 0 else 0
            },
            "applied_at": datetime.now().isoformat()
        }
    
    def get_adjustment_history(self) -> List[Dict[str, Any]]:
        """获取调整历史"""
        return self.adjustment_history.copy()
    
    def clear_adjustment_history(self) -> None:
        """清除调整历史"""
        self.adjustment_history.clear()
        logger.info("调整历史已清除")
