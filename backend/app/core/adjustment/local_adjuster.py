"""
局部调整器
Local Adjuster
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

from app.models.schemas import PredictionResult, LocalAdjustment
from app.utils.exceptions import AdjustmentError
from app.utils.helpers import convert_numpy_types, calculate_confidence_interval

logger = logging.getLogger("power_prediction")


class LocalAdjuster:
    """局部预测调整器"""
    
    def __init__(self):
        """初始化局部调整器"""
        self.adjustment_history: List[Dict[str, Any]] = []
        
    async def apply_adjustment(
        self,
        predictions: List[PredictionResult],
        adjustments: List[LocalAdjustment]
    ) -> List[PredictionResult]:
        """应用局部调整
        
        Args:
            predictions: 原始预测结果列表
            adjustments: 局部调整参数列表
            
        Returns:
            调整后的预测结果列表
        """
        try:
            logger.info(f"开始应用局部调整，调整点数: {len(adjustments)}")
            
            # 验证调整参数
            await self._validate_adjustments(adjustments, predictions)
            
            # 创建调整映射
            adjustment_map = {adj.hour: adj.new_value for adj in adjustments}
            
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
                
                # 检查是否需要调整
                if pred.hour in adjustment_map:
                    new_value = adjustment_map[pred.hour]
                    
                    # 更新预测值
                    adjusted_pred.predicted_usage = new_value
                    
                    # 重新计算置信区间
                    adjusted_pred.confidence_interval = await self._recalculate_confidence_interval(
                        new_value, pred.confidence_interval, pred.predicted_usage
                    )
                
                adjusted_predictions.append(adjusted_pred)
            
            # 应用平滑处理（可选）
            smoothed_predictions = await self._apply_smoothing(adjusted_predictions, adjustment_map)
            
            # 记录调整历史
            adjustment_record = await self._create_adjustment_record(
                adjustments, predictions, smoothed_predictions
            )
            self.adjustment_history.append(adjustment_record)
            
            logger.info(f"局部调整完成，调整了 {len(adjustments)} 个数据点")
            
            return smoothed_predictions
            
        except Exception as e:
            logger.error(f"局部调整失败: {str(e)}")
            if isinstance(e, AdjustmentError):
                raise
            else:
                raise AdjustmentError(f"局部调整过程中发生错误: {str(e)}")
    
    async def apply_single_adjustment(
        self,
        predictions: List[PredictionResult],
        hour: int,
        new_value: float
    ) -> List[PredictionResult]:
        """应用单个局部调整
        
        Args:
            predictions: 原始预测结果列表
            hour: 要调整的小时
            new_value: 新的预测值
            
        Returns:
            调整后的预测结果列表
        """
        try:
            adjustment = LocalAdjustment(hour=hour, new_value=new_value)
            return await self.apply_adjustment(predictions, [adjustment])
            
        except Exception as e:
            logger.error(f"单个局部调整失败: {str(e)}")
            raise AdjustmentError(f"单个局部调整过程中发生错误: {str(e)}")
    
    async def interpolate_adjustments(
        self,
        predictions: List[PredictionResult],
        anchor_points: List[Tuple[int, float]],
        interpolation_method: str = "linear"
    ) -> List[PredictionResult]:
        """基于锚点进行插值调整
        
        Args:
            predictions: 原始预测结果列表
            anchor_points: 锚点列表，每个元素为 (hour, value)
            interpolation_method: 插值方法 ("linear", "cubic")
            
        Returns:
            调整后的预测结果列表
        """
        try:
            logger.info(f"开始插值调整，锚点数: {len(anchor_points)}, 方法: {interpolation_method}")
            
            if len(anchor_points) < 2:
                raise AdjustmentError("插值调整至少需要2个锚点")
            
            # 排序锚点
            anchor_points = sorted(anchor_points, key=lambda x: x[0])
            
            # 验证锚点
            for hour, value in anchor_points:
                if not (0 <= hour <= 23):
                    raise AdjustmentError(f"锚点小时无效: {hour}")
                if value <= 0:
                    raise AdjustmentError(f"锚点值必须大于0: {value}")
            
            # 创建调整后的预测结果
            adjusted_predictions = []
            
            for pred in predictions:
                adjusted_pred = PredictionResult(
                    hour=pred.hour,
                    predicted_usage=pred.predicted_usage,
                    confidence_interval=pred.confidence_interval,
                    original_prediction=pred.original_prediction or pred.predicted_usage
                )
                
                # 计算插值
                interpolated_value = await self._interpolate_value(
                    pred.hour, anchor_points, interpolation_method
                )
                
                if interpolated_value is not None:
                    adjusted_pred.predicted_usage = interpolated_value
                    adjusted_pred.confidence_interval = await self._recalculate_confidence_interval(
                        interpolated_value, pred.confidence_interval, pred.predicted_usage
                    )
                
                adjusted_predictions.append(adjusted_pred)
            
            # 记录调整历史
            adjustment_record = {
                "adjustment_id": len(self.adjustment_history) + 1,
                "adjustment_type": "interpolation",
                "anchor_points": anchor_points,
                "interpolation_method": interpolation_method,
                "applied_at": datetime.now().isoformat()
            }
            self.adjustment_history.append(adjustment_record)
            
            logger.info("插值调整完成")
            
            return adjusted_predictions
            
        except Exception as e:
            logger.error(f"插值调整失败: {str(e)}")
            raise AdjustmentError(f"插值调整过程中发生错误: {str(e)}")
    
    async def smooth_predictions(
        self,
        predictions: List[PredictionResult],
        smoothing_factor: float = 0.1
    ) -> List[PredictionResult]:
        """平滑预测结果
        
        Args:
            predictions: 预测结果列表
            smoothing_factor: 平滑因子 (0-1)
            
        Returns:
            平滑后的预测结果列表
        """
        try:
            logger.info(f"开始平滑预测结果，平滑因子: {smoothing_factor}")
            
            if not (0 <= smoothing_factor <= 1):
                raise AdjustmentError("平滑因子必须在0到1之间")
            
            if len(predictions) < 3:
                return predictions  # 数据点太少，无需平滑
            
            # 按小时排序
            sorted_predictions = sorted(predictions, key=lambda x: x.hour)
            
            # 应用移动平均平滑
            smoothed_predictions = []
            
            for i, pred in enumerate(sorted_predictions):
                if i == 0 or i == len(sorted_predictions) - 1:
                    # 边界点不平滑
                    smoothed_predictions.append(pred)
                else:
                    # 计算移动平均
                    prev_value = sorted_predictions[i-1].predicted_usage
                    curr_value = pred.predicted_usage
                    next_value = sorted_predictions[i+1].predicted_usage
                    
                    smoothed_value = (
                        prev_value * smoothing_factor +
                        curr_value * (1 - 2 * smoothing_factor) +
                        next_value * smoothing_factor
                    )
                    
                    # 创建平滑后的预测结果
                    smoothed_pred = PredictionResult(
                        hour=pred.hour,
                        predicted_usage=smoothed_value,
                        confidence_interval=pred.confidence_interval,
                        original_prediction=pred.original_prediction or pred.predicted_usage
                    )
                    
                    smoothed_predictions.append(smoothed_pred)
            
            logger.info("预测结果平滑完成")
            
            return smoothed_predictions
            
        except Exception as e:
            logger.error(f"预测结果平滑失败: {str(e)}")
            raise AdjustmentError(f"预测结果平滑过程中发生错误: {str(e)}")
    
    async def calculate_adjustment_impact(
        self,
        original_predictions: List[PredictionResult],
        adjusted_predictions: List[PredictionResult]
    ) -> Dict[str, Any]:
        """计算局部调整影响
        
        Args:
            original_predictions: 原始预测结果
            adjusted_predictions: 调整后预测结果
            
        Returns:
            调整影响分析结果
        """
        try:
            logger.info("开始计算局部调整影响")
            
            if len(original_predictions) != len(adjusted_predictions):
                raise AdjustmentError("原始预测和调整后预测的长度不匹配")
            
            # 计算逐点影响
            point_impacts = []
            total_original = 0
            total_adjusted = 0
            
            for orig, adj in zip(original_predictions, adjusted_predictions):
                change = adj.predicted_usage - orig.predicted_usage
                change_percentage = (change / orig.predicted_usage) * 100 if orig.predicted_usage > 0 else 0
                
                point_impacts.append({
                    "hour": orig.hour,
                    "original_value": orig.predicted_usage,
                    "adjusted_value": adj.predicted_usage,
                    "absolute_change": change,
                    "percentage_change": change_percentage,
                    "was_adjusted": abs(change) > 0.01
                })
                
                total_original += orig.predicted_usage
                total_adjusted += adj.predicted_usage
            
            # 统计调整点
            adjusted_points = [impact for impact in point_impacts if impact["was_adjusted"]]
            
            # 计算连续性指标
            continuity_score = await self._calculate_continuity_score(adjusted_predictions)
            
            # 计算变化分布
            changes = [impact["absolute_change"] for impact in adjusted_points]
            
            impact_analysis = {
                "total_impact": {
                    "original_total": total_original,
                    "adjusted_total": total_adjusted,
                    "absolute_change": total_adjusted - total_original,
                    "percentage_change": ((total_adjusted - total_original) / total_original) * 100 if total_original > 0 else 0
                },
                "point_impacts": point_impacts,
                "adjustment_summary": {
                    "total_points_adjusted": len(adjusted_points),
                    "adjustment_hours": [impact["hour"] for impact in adjusted_points],
                    "max_change": max(changes) if changes else 0,
                    "min_change": min(changes) if changes else 0,
                    "average_change": np.mean(changes) if changes else 0,
                    "std_change": np.std(changes) if changes else 0
                },
                "quality_metrics": {
                    "continuity_score": continuity_score,
                    "smoothness_score": await self._calculate_smoothness_score(adjusted_predictions)
                },
                "analysis_time": datetime.now().isoformat()
            }
            
            logger.info(f"局部调整影响计算完成，调整了 {len(adjusted_points)} 个点")
            
            return convert_numpy_types(impact_analysis)
            
        except Exception as e:
            logger.error(f"局部调整影响计算失败: {str(e)}")
            raise AdjustmentError(f"局部调整影响计算过程中发生错误: {str(e)}")
    
    async def _validate_adjustments(
        self, 
        adjustments: List[LocalAdjustment], 
        predictions: List[PredictionResult]
    ) -> None:
        """验证调整参数"""
        if not adjustments:
            raise AdjustmentError("调整参数为空")
        
        prediction_hours = {pred.hour for pred in predictions}
        
        for adj in adjustments:
            if not (0 <= adj.hour <= 23):
                raise AdjustmentError(f"调整小时无效: {adj.hour}")
            
            if adj.hour not in prediction_hours:
                raise AdjustmentError(f"调整小时不在预测数据中: {adj.hour}")
            
            if adj.new_value <= 0:
                raise AdjustmentError(f"调整值必须大于0: {adj.new_value}")
        
        # 检查重复调整
        adjustment_hours = [adj.hour for adj in adjustments]
        if len(set(adjustment_hours)) != len(adjustment_hours):
            raise AdjustmentError("存在重复的调整小时")
    
    async def _recalculate_confidence_interval(
        self, 
        new_value: float, 
        original_interval: tuple, 
        original_value: float
    ) -> tuple:
        """重新计算置信区间"""
        if original_value <= 0:
            # 使用默认的置信区间计算
            margin = new_value * 0.1  # 10%的误差范围
            return (max(0, new_value - margin), new_value + margin)
        
        # 基于原始置信区间的比例调整
        lower, upper = original_interval
        lower_ratio = lower / original_value if original_value > 0 else 0.9
        upper_ratio = upper / original_value if original_value > 0 else 1.1
        
        new_lower = max(0, new_value * lower_ratio)
        new_upper = new_value * upper_ratio
        
        return (new_lower, new_upper)
    
    async def _apply_smoothing(
        self, 
        predictions: List[PredictionResult], 
        adjustment_map: Dict[int, float]
    ) -> List[PredictionResult]:
        """应用平滑处理"""
        # 如果调整点较少，不需要平滑
        if len(adjustment_map) <= 2:
            return predictions
        
        # 对调整点周围进行轻微平滑
        smoothed_predictions = predictions.copy()
        
        for hour in adjustment_map.keys():
            # 找到相邻的预测点
            for i, pred in enumerate(smoothed_predictions):
                if pred.hour == hour:
                    # 检查前后相邻点
                    if i > 0 and i < len(smoothed_predictions) - 1:
                        prev_pred = smoothed_predictions[i-1]
                        next_pred = smoothed_predictions[i+1]
                        
                        # 轻微调整相邻点以保持连续性
                        smoothing_factor = 0.05  # 5%的平滑
                        
                        if prev_pred.hour not in adjustment_map:
                            adjustment = (pred.predicted_usage - prev_pred.predicted_usage) * smoothing_factor
                            prev_pred.predicted_usage += adjustment
                        
                        if next_pred.hour not in adjustment_map:
                            adjustment = (pred.predicted_usage - next_pred.predicted_usage) * smoothing_factor
                            next_pred.predicted_usage += adjustment
                    
                    break
        
        return smoothed_predictions
    
    async def _interpolate_value(
        self, 
        hour: int, 
        anchor_points: List[Tuple[int, float]], 
        method: str
    ) -> Optional[float]:
        """插值计算"""
        # 检查是否在锚点范围内
        min_hour = min(point[0] for point in anchor_points)
        max_hour = max(point[0] for point in anchor_points)
        
        if hour < min_hour or hour > max_hour:
            return None  # 超出范围，不插值
        
        # 检查是否是锚点
        for anchor_hour, anchor_value in anchor_points:
            if hour == anchor_hour:
                return anchor_value
        
        # 线性插值
        if method == "linear":
            # 找到相邻的两个锚点
            left_point = None
            right_point = None
            
            for anchor_hour, anchor_value in anchor_points:
                if anchor_hour < hour:
                    if left_point is None or anchor_hour > left_point[0]:
                        left_point = (anchor_hour, anchor_value)
                elif anchor_hour > hour:
                    if right_point is None or anchor_hour < right_point[0]:
                        right_point = (anchor_hour, anchor_value)
            
            if left_point and right_point:
                # 线性插值
                x1, y1 = left_point
                x2, y2 = right_point
                
                interpolated_value = y1 + (y2 - y1) * (hour - x1) / (x2 - x1)
                return interpolated_value
        
        return None
    
    async def _calculate_continuity_score(self, predictions: List[PredictionResult]) -> float:
        """计算连续性评分"""
        if len(predictions) < 2:
            return 1.0
        
        # 按小时排序
        sorted_predictions = sorted(predictions, key=lambda x: x.hour)
        
        # 计算相邻点之间的变化率
        changes = []
        for i in range(1, len(sorted_predictions)):
            prev_value = sorted_predictions[i-1].predicted_usage
            curr_value = sorted_predictions[i].predicted_usage
            
            if prev_value > 0:
                change_rate = abs(curr_value - prev_value) / prev_value
                changes.append(change_rate)
        
        if not changes:
            return 1.0
        
        # 连续性评分：变化率越小，连续性越好
        avg_change_rate = np.mean(changes)
        continuity_score = max(0, 1 - avg_change_rate)
        
        return float(continuity_score)
    
    async def _calculate_smoothness_score(self, predictions: List[PredictionResult]) -> float:
        """计算平滑度评分"""
        if len(predictions) < 3:
            return 1.0
        
        # 按小时排序
        sorted_predictions = sorted(predictions, key=lambda x: x.hour)
        
        # 计算二阶差分
        second_diffs = []
        for i in range(1, len(sorted_predictions) - 1):
            prev_value = sorted_predictions[i-1].predicted_usage
            curr_value = sorted_predictions[i].predicted_usage
            next_value = sorted_predictions[i+1].predicted_usage
            
            second_diff = abs(next_value - 2 * curr_value + prev_value)
            second_diffs.append(second_diff)
        
        if not second_diffs:
            return 1.0
        
        # 平滑度评分：二阶差分越小，平滑度越好
        avg_second_diff = np.mean(second_diffs)
        avg_value = np.mean([pred.predicted_usage for pred in predictions])
        
        if avg_value > 0:
            normalized_diff = avg_second_diff / avg_value
            smoothness_score = max(0, 1 - normalized_diff)
        else:
            smoothness_score = 1.0
        
        return float(smoothness_score)
    
    async def _create_adjustment_record(
        self,
        adjustments: List[LocalAdjustment],
        original_predictions: List[PredictionResult],
        adjusted_predictions: List[PredictionResult]
    ) -> Dict[str, Any]:
        """创建调整记录"""
        original_total = sum(pred.predicted_usage for pred in original_predictions)
        adjusted_total = sum(pred.predicted_usage for pred in adjusted_predictions)
        
        return {
            "adjustment_id": len(self.adjustment_history) + 1,
            "adjustment_type": "local",
            "adjustments": [
                {"hour": adj.hour, "new_value": adj.new_value}
                for adj in adjustments
            ],
            "impact": {
                "original_total": original_total,
                "adjusted_total": adjusted_total,
                "total_change": adjusted_total - original_total,
                "percentage_change": ((adjusted_total - original_total) / original_total) * 100 if original_total > 0 else 0,
                "points_adjusted": len(adjustments)
            },
            "applied_at": datetime.now().isoformat()
        }
    
    def get_adjustment_history(self) -> List[Dict[str, Any]]:
        """获取调整历史"""
        return self.adjustment_history.copy()
    
    def clear_adjustment_history(self) -> None:
        """清除调整历史"""
        self.adjustment_history.clear()
        logger.info("局部调整历史已清除")
