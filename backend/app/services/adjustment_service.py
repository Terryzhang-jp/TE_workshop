"""
调整服务
Adjustment Service
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.core.adjustment.global_adjuster import GlobalAdjuster
from app.core.adjustment.local_adjuster import LocalAdjuster
from app.models.schemas import PredictionResult, GlobalAdjustment, LocalAdjustment
from app.utils.exceptions import AdjustmentError
from app.utils.helpers import convert_numpy_types

logger = logging.getLogger("power_prediction")


class AdjustmentService:
    """调整服务类"""
    
    def __init__(self):
        """初始化调整服务"""
        self.global_adjuster = GlobalAdjuster()
        self.local_adjuster = LocalAdjuster()
        self._adjustment_cache: Dict[str, Any] = {}
        self._original_predictions: Optional[List[PredictionResult]] = None
        
    async def apply_global_adjustment(
        self,
        predictions: List[PredictionResult],
        adjustment: GlobalAdjustment,
        save_original: bool = True
    ) -> Dict[str, Any]:
        """应用全局调整
        
        Args:
            predictions: 原始预测结果
            adjustment: 全局调整参数
            save_original: 是否保存原始预测
            
        Returns:
            调整结果
        """
        try:
            logger.info(f"应用全局调整: {adjustment.start_hour}-{adjustment.end_hour}时, {adjustment.direction} {adjustment.percentage}%")
            
            # 保存原始预测（如果需要）
            if save_original:
                self._original_predictions = predictions.copy()
            
            # 应用调整
            adjusted_predictions = await self.global_adjuster.apply_adjustment(predictions, adjustment)
            
            # 计算影响
            impact_analysis = await self.global_adjuster.calculate_adjustment_impact(
                predictions, adjusted_predictions
            )
            
            # 生成调整摘要
            adjustment_summary = await self._generate_global_adjustment_summary(
                adjustment, impact_analysis
            )
            
            result = {
                "adjustment_type": "global",
                "original_predictions": [pred.dict() for pred in predictions],
                "adjusted_predictions": [pred.dict() for pred in adjusted_predictions],
                "adjustment_params": adjustment.dict(),
                "impact_analysis": impact_analysis,
                "adjustment_summary": adjustment_summary,
                "applied_at": datetime.now().isoformat()
            }
            
            logger.info(f"全局调整完成，总变化: {impact_analysis['total_impact']['absolute_change']:.2f}")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"全局调整失败: {str(e)}")
            if isinstance(e, AdjustmentError):
                raise
            else:
                raise AdjustmentError(f"全局调整过程中发生错误: {str(e)}")
    
    async def apply_local_adjustment(
        self,
        predictions: List[PredictionResult],
        adjustments: List[LocalAdjustment],
        save_original: bool = True
    ) -> Dict[str, Any]:
        """应用局部调整
        
        Args:
            predictions: 原始预测结果
            adjustments: 局部调整参数列表
            save_original: 是否保存原始预测
            
        Returns:
            调整结果
        """
        try:
            logger.info(f"应用局部调整，调整点数: {len(adjustments)}")
            
            # 保存原始预测（如果需要）
            if save_original:
                self._original_predictions = predictions.copy()
            
            # 应用调整
            adjusted_predictions = await self.local_adjuster.apply_adjustment(predictions, adjustments)
            
            # 计算影响
            impact_analysis = await self.local_adjuster.calculate_adjustment_impact(
                predictions, adjusted_predictions
            )
            
            # 生成调整摘要
            adjustment_summary = await self._generate_local_adjustment_summary(
                adjustments, impact_analysis
            )
            
            result = {
                "adjustment_type": "local",
                "original_predictions": [pred.dict() for pred in predictions],
                "adjusted_predictions": [pred.dict() for pred in adjusted_predictions],
                "adjustment_params": [adj.dict() for adj in adjustments],
                "impact_analysis": impact_analysis,
                "adjustment_summary": adjustment_summary,
                "applied_at": datetime.now().isoformat()
            }
            
            logger.info(f"局部调整完成，调整了 {len(adjustments)} 个点")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"局部调整失败: {str(e)}")
            if isinstance(e, AdjustmentError):
                raise
            else:
                raise AdjustmentError(f"局部调整过程中发生错误: {str(e)}")
    
    async def apply_mixed_adjustment(
        self,
        predictions: List[PredictionResult],
        global_adjustments: Optional[List[GlobalAdjustment]] = None,
        local_adjustments: Optional[List[LocalAdjustment]] = None
    ) -> Dict[str, Any]:
        """应用混合调整（全局+局部）
        
        Args:
            predictions: 原始预测结果
            global_adjustments: 全局调整参数列表
            local_adjustments: 局部调整参数列表
            
        Returns:
            调整结果
        """
        try:
            logger.info("应用混合调整")
            
            # 保存原始预测
            original_predictions = predictions.copy()
            current_predictions = predictions.copy()
            
            adjustment_steps = []
            
            # 先应用全局调整
            if global_adjustments:
                for i, global_adj in enumerate(global_adjustments):
                    logger.info(f"应用第 {i+1} 个全局调整")
                    current_predictions = await self.global_adjuster.apply_adjustment(
                        current_predictions, global_adj
                    )
                    
                    adjustment_steps.append({
                        "step": i + 1,
                        "type": "global",
                        "params": global_adj.dict()
                    })
            
            # 再应用局部调整
            if local_adjustments:
                logger.info("应用局部调整")
                current_predictions = await self.local_adjuster.apply_adjustment(
                    current_predictions, local_adjustments
                )
                
                adjustment_steps.append({
                    "step": len(adjustment_steps) + 1,
                    "type": "local",
                    "params": [adj.dict() for adj in local_adjustments]
                })
            
            # 计算总体影响
            total_impact = await self._calculate_total_impact(original_predictions, current_predictions)
            
            # 生成混合调整摘要
            adjustment_summary = await self._generate_mixed_adjustment_summary(
                global_adjustments, local_adjustments, total_impact
            )
            
            result = {
                "adjustment_type": "mixed",
                "original_predictions": [pred.dict() for pred in original_predictions],
                "adjusted_predictions": [pred.dict() for pred in current_predictions],
                "adjustment_steps": adjustment_steps,
                "total_impact": total_impact,
                "adjustment_summary": adjustment_summary,
                "applied_at": datetime.now().isoformat()
            }
            
            logger.info("混合调整完成")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"混合调整失败: {str(e)}")
            raise AdjustmentError(f"混合调整过程中发生错误: {str(e)}")
    
    async def reset_adjustments(self) -> Dict[str, Any]:
        """重置调整，恢复到原始预测
        
        Returns:
            重置结果
        """
        try:
            if self._original_predictions is None:
                raise AdjustmentError("没有保存的原始预测数据")
            
            logger.info("重置调整，恢复到原始预测")
            
            result = {
                "reset_successful": True,
                "original_predictions": [pred.dict() for pred in self._original_predictions],
                "reset_at": datetime.now().isoformat(),
                "message": "已恢复到原始预测结果"
            }
            
            logger.info("调整重置完成")
            
            return result
            
        except Exception as e:
            logger.error(f"重置调整失败: {str(e)}")
            raise AdjustmentError(f"重置调整过程中发生错误: {str(e)}")
    
    async def optimize_global_adjustment(
        self,
        predictions: List[PredictionResult],
        target_total: float,
        adjustment_hours: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """优化全局调整参数
        
        Args:
            predictions: 原始预测结果
            target_total: 目标总用电量
            adjustment_hours: 允许调整的小时列表
            
        Returns:
            优化结果
        """
        try:
            logger.info(f"优化全局调整参数，目标总量: {target_total}")
            
            # 使用全局调整器的优化功能
            optimized_adjustment = await self.global_adjuster.optimize_adjustment(
                predictions, target_total, adjustment_hours
            )
            
            # 应用优化后的调整
            adjusted_predictions = await self.global_adjuster.apply_adjustment(
                predictions, optimized_adjustment
            )
            
            # 计算实际达到的总量
            actual_total = sum(pred.predicted_usage for pred in adjusted_predictions)
            
            # 计算优化效果
            optimization_result = {
                "target_total": target_total,
                "actual_total": actual_total,
                "optimization_error": abs(actual_total - target_total),
                "optimization_error_percentage": abs(actual_total - target_total) / target_total * 100 if target_total > 0 else 0,
                "optimized_adjustment": optimized_adjustment.dict(),
                "adjusted_predictions": [pred.dict() for pred in adjusted_predictions]
            }
            
            result = {
                "optimization_successful": True,
                "optimization_result": optimization_result,
                "recommendations": await self._generate_optimization_recommendations(optimization_result),
                "optimized_at": datetime.now().isoformat()
            }
            
            logger.info(f"全局调整参数优化完成，误差: {optimization_result['optimization_error']:.2f}")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"优化全局调整参数失败: {str(e)}")
            raise AdjustmentError(f"优化全局调整参数过程中发生错误: {str(e)}")
    
    async def get_adjustment_history(self, adjustment_type: str = "all") -> Dict[str, Any]:
        """获取调整历史
        
        Args:
            adjustment_type: 调整类型 ("all", "global", "local")
            
        Returns:
            调整历史
        """
        try:
            logger.info(f"获取调整历史，类型: {adjustment_type}")
            
            history = {}
            
            if adjustment_type in ["all", "global"]:
                history["global_history"] = self.global_adjuster.get_adjustment_history()
            
            if adjustment_type in ["all", "local"]:
                history["local_history"] = self.local_adjuster.get_adjustment_history()
            
            # 统计信息
            total_adjustments = 0
            if "global_history" in history:
                total_adjustments += len(history["global_history"])
            if "local_history" in history:
                total_adjustments += len(history["local_history"])
            
            result = {
                "adjustment_history": history,
                "total_adjustments": total_adjustments,
                "history_summary": await self._generate_history_summary(history),
                "retrieved_at": datetime.now().isoformat()
            }
            
            logger.info(f"调整历史获取完成，共 {total_adjustments} 次调整")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"获取调整历史失败: {str(e)}")
            raise AdjustmentError(f"获取调整历史过程中发生错误: {str(e)}")
    
    async def clear_adjustment_history(self) -> Dict[str, Any]:
        """清除调整历史
        
        Returns:
            清除结果
        """
        try:
            global_count = len(self.global_adjuster.get_adjustment_history())
            local_count = len(self.local_adjuster.get_adjustment_history())
            
            self.global_adjuster.clear_adjustment_history()
            self.local_adjuster.clear_adjustment_history()
            
            result = {
                "cleared_global_adjustments": global_count,
                "cleared_local_adjustments": local_count,
                "total_cleared": global_count + local_count,
                "cleared_at": datetime.now().isoformat()
            }
            
            logger.info(f"调整历史已清除，共 {result['total_cleared']} 次调整")
            
            return result
            
        except Exception as e:
            logger.error(f"清除调整历史失败: {str(e)}")
            raise AdjustmentError(f"清除调整历史过程中发生错误: {str(e)}")
    
    async def _generate_global_adjustment_summary(
        self,
        adjustment: GlobalAdjustment,
        impact_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成全局调整摘要"""
        total_impact = impact_analysis.get("total_impact", {})
        adjustment_summary = impact_analysis.get("adjustment_summary", {})
        
        return {
            "adjustment_description": f"{adjustment.start_hour}-{adjustment.end_hour}时 {adjustment.direction} {adjustment.percentage}%",
            "affected_hours": adjustment.end_hour - adjustment.start_hour + 1,
            "total_change": total_impact.get("absolute_change", 0),
            "percentage_change": total_impact.get("percentage_change", 0),
            "peak_impact_hour": adjustment_summary.get("peak_impact", {}).get("hour"),
            "average_change": adjustment_summary.get("average_change", 0)
        }
    
    async def _generate_local_adjustment_summary(
        self,
        adjustments: List[LocalAdjustment],
        impact_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成局部调整摘要"""
        total_impact = impact_analysis.get("total_impact", {})
        adjustment_summary = impact_analysis.get("adjustment_summary", {})
        quality_metrics = impact_analysis.get("quality_metrics", {})
        
        return {
            "adjustment_description": f"调整了 {len(adjustments)} 个数据点",
            "adjusted_hours": [adj.hour for adj in adjustments],
            "total_change": total_impact.get("absolute_change", 0),
            "percentage_change": total_impact.get("percentage_change", 0),
            "max_point_change": adjustment_summary.get("max_change", 0),
            "continuity_score": quality_metrics.get("continuity_score", 0),
            "smoothness_score": quality_metrics.get("smoothness_score", 0)
        }
    
    async def _generate_mixed_adjustment_summary(
        self,
        global_adjustments: Optional[List[GlobalAdjustment]],
        local_adjustments: Optional[List[LocalAdjustment]],
        total_impact: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成混合调整摘要"""
        summary = {
            "total_steps": 0,
            "global_adjustments_count": 0,
            "local_adjustments_count": 0,
            "total_change": total_impact.get("absolute_change", 0),
            "percentage_change": total_impact.get("percentage_change", 0)
        }
        
        if global_adjustments:
            summary["global_adjustments_count"] = len(global_adjustments)
            summary["total_steps"] += len(global_adjustments)
        
        if local_adjustments:
            summary["local_adjustments_count"] = len(local_adjustments)
            summary["total_steps"] += 1  # 局部调整作为一个步骤
        
        return summary
    
    async def _calculate_total_impact(
        self,
        original_predictions: List[PredictionResult],
        final_predictions: List[PredictionResult]
    ) -> Dict[str, Any]:
        """计算总体影响"""
        original_total = sum(pred.predicted_usage for pred in original_predictions)
        final_total = sum(pred.predicted_usage for pred in final_predictions)
        
        return {
            "original_total": original_total,
            "final_total": final_total,
            "absolute_change": final_total - original_total,
            "percentage_change": ((final_total - original_total) / original_total) * 100 if original_total > 0 else 0
        }
    
    async def _generate_optimization_recommendations(
        self,
        optimization_result: Dict[str, Any]
    ) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        error_percentage = optimization_result.get("optimization_error_percentage", 0)
        
        if error_percentage < 1:
            recommendations.append("优化结果非常接近目标值，建议采用此调整方案")
        elif error_percentage < 5:
            recommendations.append("优化结果较为接近目标值，可以考虑采用")
        else:
            recommendations.append("优化结果与目标值差距较大，建议检查目标值的合理性或考虑其他调整策略")
        
        optimized_adjustment = optimization_result.get("optimized_adjustment", {})
        percentage = optimized_adjustment.get("percentage", 0)
        
        if percentage > 50:
            recommendations.append("调整幅度较大，建议分步骤进行调整")
        
        return recommendations
    
    async def _generate_history_summary(self, history: Dict[str, Any]) -> Dict[str, Any]:
        """生成历史摘要"""
        summary = {
            "total_global_adjustments": len(history.get("global_history", [])),
            "total_local_adjustments": len(history.get("local_history", [])),
            "most_recent_adjustment": None,
            "adjustment_frequency": {}
        }
        
        # 找到最近的调整
        all_adjustments = []
        
        for adj in history.get("global_history", []):
            adj["type"] = "global"
            all_adjustments.append(adj)
        
        for adj in history.get("local_history", []):
            adj["type"] = "local"
            all_adjustments.append(adj)
        
        if all_adjustments:
            # 按时间排序
            all_adjustments.sort(key=lambda x: x.get("applied_at", ""), reverse=True)
            summary["most_recent_adjustment"] = all_adjustments[0]
        
        return summary
