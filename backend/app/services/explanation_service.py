"""
解释服务
Explanation Service
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.core.explanation.shap_analyzer import SHAPAnalyzer
from app.core.explanation.lime_analyzer import LIMEAnalyzer
from app.core.ml.model import PowerPredictionModel
from app.core.data.processor import DataProcessor
from app.models.schemas import FeatureImportance, SHAPValue, LIMEExplanation
from app.utils.exceptions import ExplanationError, ModelNotFoundError
from app.utils.helpers import convert_numpy_types
from app.utils.constants import FEATURE_NAMES, FEATURE_NAME_MAPPING

logger = logging.getLogger("power_prediction")


class ExplanationService:
    """解释服务类"""
    
    def __init__(self):
        """初始化解释服务"""
        self.shap_analyzer = SHAPAnalyzer()
        self.lime_analyzer = LIMEAnalyzer()
        self.data_processor = DataProcessor()
        self._explanation_cache: Dict[str, Any] = {}
        self._is_initialized = False
        
    async def initialize(
        self,
        model: PowerPredictionModel,
        background_data: np.ndarray,
        training_data: np.ndarray
    ) -> Dict[str, Any]:
        """初始化解释服务
        
        Args:
            model: 训练好的模型
            background_data: SHAP背景数据
            training_data: LIME训练数据
            
        Returns:
            初始化结果
        """
        try:
            logger.info("开始初始化解释服务")
            
            # 初始化SHAP分析器
            self.shap_analyzer.model = model
            shap_success = await self.shap_analyzer.initialize(background_data)
            
            # 初始化LIME分析器
            self.lime_analyzer.model = model
            lime_success = await self.lime_analyzer.initialize(training_data)
            
            self._is_initialized = shap_success and lime_success
            
            result = {
                "shap_initialized": shap_success,
                "lime_initialized": lime_success,
                "overall_success": self._is_initialized,
                "background_data_size": background_data.shape[0],
                "training_data_size": training_data.shape[0],
                "initialized_at": datetime.now().isoformat()
            }
            
            if self._is_initialized:
                logger.info("解释服务初始化成功")
            else:
                logger.error("解释服务初始化失败")
            
            return result
            
        except Exception as e:
            logger.error(f"解释服务初始化失败: {str(e)}")
            raise ExplanationError(f"解释服务初始化过程中发生错误: {str(e)}")
    
    async def get_shap_analysis(
        self,
        analysis_type: str = "global",
        instances: Optional[np.ndarray] = None,
        hours: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """获取SHAP分析结果
        
        Args:
            analysis_type: 分析类型 ("global", "local", "hourly")
            instances: 要分析的实例（局部分析时需要）
            hours: 小时列表（按小时分析时需要）
            
        Returns:
            SHAP分析结果
        """
        try:
            if not self._is_initialized:
                raise ExplanationError("解释服务尚未初始化")
            
            logger.info(f"开始SHAP分析，类型: {analysis_type}")
            
            # 检查缓存
            cache_key = f"shap_{analysis_type}_{hash(str(instances.tolist() if instances is not None else None))}_{hash(str(hours))}"
            if cache_key in self._explanation_cache:
                logger.info("从缓存返回SHAP分析结果")
                return self._explanation_cache[cache_key]
            
            if analysis_type == "global":
                result = await self.shap_analyzer.explain_global()
            elif analysis_type == "local":
                if instances is None:
                    raise ExplanationError("局部SHAP分析需要提供实例数据")
                result = await self.shap_analyzer.explain_local(instances)
            elif analysis_type == "hourly":
                if instances is None or hours is None:
                    raise ExplanationError("按小时SHAP分析需要提供实例数据和小时列表")
                result = await self.shap_analyzer.explain_prediction_for_hours(instances, hours)
            else:
                raise ExplanationError(f"不支持的SHAP分析类型: {analysis_type}")
            
            # 格式化结果
            formatted_result = await self._format_shap_result(result, analysis_type)
            
            # 缓存结果
            self._explanation_cache[cache_key] = formatted_result
            
            logger.info(f"SHAP分析完成，类型: {analysis_type}")
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"SHAP分析失败: {str(e)}")
            if isinstance(e, ExplanationError):
                raise
            else:
                raise ExplanationError(f"SHAP分析过程中发生错误: {str(e)}")
    
    async def get_lime_analysis(
        self,
        instances: np.ndarray,
        analysis_type: str = "single",
        hours: Optional[List[int]] = None,
        num_features: int = 4
    ) -> Dict[str, Any]:
        """获取LIME分析结果
        
        Args:
            instances: 要分析的实例
            analysis_type: 分析类型 ("single", "batch", "hourly", "compare")
            hours: 小时列表（按小时分析时需要）
            num_features: 要显示的特征数量
            
        Returns:
            LIME分析结果
        """
        try:
            if not self._is_initialized:
                raise ExplanationError("解释服务尚未初始化")
            
            logger.info(f"开始LIME分析，类型: {analysis_type}")
            
            # 检查缓存
            cache_key = f"lime_{analysis_type}_{hash(str(instances.tolist()))}_{hash(str(hours))}_{num_features}"
            if cache_key in self._explanation_cache:
                logger.info("从缓存返回LIME分析结果")
                return self._explanation_cache[cache_key]
            
            if analysis_type == "single":
                if instances.shape[0] != 1:
                    raise ExplanationError("单实例LIME分析只能处理一个实例")
                result = await self.lime_analyzer.explain_instance(instances[0], num_features)
            elif analysis_type == "batch":
                result = await self.lime_analyzer.explain_batch(instances, num_features)
            elif analysis_type == "hourly":
                if hours is None:
                    raise ExplanationError("按小时LIME分析需要提供小时列表")
                result = await self.lime_analyzer.explain_hourly_predictions(instances, hours, num_features)
            elif analysis_type == "compare":
                if hours is None:
                    hours = [f"实例{i+1}" for i in range(instances.shape[0])]
                result = await self.lime_analyzer.compare_explanations(instances, hours)
            else:
                raise ExplanationError(f"不支持的LIME分析类型: {analysis_type}")
            
            # 格式化结果
            formatted_result = await self._format_lime_result(result, analysis_type)
            
            # 缓存结果
            self._explanation_cache[cache_key] = formatted_result
            
            logger.info(f"LIME分析完成，类型: {analysis_type}")
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"LIME分析失败: {str(e)}")
            if isinstance(e, ExplanationError):
                raise
            else:
                raise ExplanationError(f"LIME分析过程中发生错误: {str(e)}")
    
    async def get_feature_importance(self) -> Dict[str, Any]:
        """获取特征重要性分析
        
        Returns:
            特征重要性分析结果
        """
        try:
            if not self._is_initialized:
                raise ExplanationError("解释服务尚未初始化")
            
            logger.info("开始特征重要性分析")
            
            # 检查缓存
            cache_key = "feature_importance"
            if cache_key in self._explanation_cache:
                logger.info("从缓存返回特征重要性分析结果")
                return self._explanation_cache[cache_key]
            
            # 获取全局SHAP分析
            shap_result = await self.shap_analyzer.explain_global()
            
            # 提取特征重要性
            global_importance = shap_result.get("global_importance", [])
            
            # 格式化特征重要性
            feature_importance_list = []
            for item in global_importance:
                feature_importance = FeatureImportance(
                    feature_name=item["feature"],
                    importance=item["importance"],
                    rank=item["rank"]
                )
                feature_importance_list.append(feature_importance.dict())
            
            # 添加中文名称映射
            for item in feature_importance_list:
                item["feature_name_cn"] = FEATURE_NAME_MAPPING.get(item["feature_name"], item["feature_name"])
            
            result = {
                "feature_importance": feature_importance_list,
                "total_features": len(feature_importance_list),
                "analysis_method": "SHAP",
                "summary_stats": shap_result.get("summary_stats", {}),
                "generated_at": datetime.now().isoformat()
            }
            
            # 缓存结果
            self._explanation_cache[cache_key] = result
            
            logger.info("特征重要性分析完成")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"特征重要性分析失败: {str(e)}")
            if isinstance(e, ExplanationError):
                raise
            else:
                raise ExplanationError(f"特征重要性分析过程中发生错误: {str(e)}")
    
    async def get_comprehensive_explanation(
        self,
        instances: np.ndarray,
        hours: List[int]
    ) -> Dict[str, Any]:
        """获取综合解释分析
        
        Args:
            instances: 要分析的实例
            hours: 小时列表
            
        Returns:
            综合解释分析结果
        """
        try:
            if not self._is_initialized:
                raise ExplanationError("解释服务尚未初始化")
            
            logger.info("开始综合解释分析")
            
            # 并行执行SHAP和LIME分析
            shap_task = self.get_shap_analysis("hourly", instances, hours)
            lime_task = self.get_lime_analysis(instances, "hourly", hours)
            feature_importance_task = self.get_feature_importance()
            
            # 等待所有分析完成
            shap_result, lime_result, feature_importance_result = await asyncio.gather(
                shap_task, lime_task, feature_importance_task
            )
            
            # 综合分析结果
            comprehensive_result = {
                "shap_analysis": shap_result,
                "lime_analysis": lime_result,
                "feature_importance": feature_importance_result,
                "analysis_summary": await self._generate_analysis_summary(
                    shap_result, lime_result, feature_importance_result
                ),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info("综合解释分析完成")
            
            return convert_numpy_types(comprehensive_result)
            
        except Exception as e:
            logger.error(f"综合解释分析失败: {str(e)}")
            if isinstance(e, ExplanationError):
                raise
            else:
                raise ExplanationError(f"综合解释分析过程中发生错误: {str(e)}")
    
    async def compare_explanations(
        self,
        instances_list: List[np.ndarray],
        labels: List[str]
    ) -> Dict[str, Any]:
        """比较不同实例的解释
        
        Args:
            instances_list: 实例列表
            labels: 实例标签列表
            
        Returns:
            解释比较结果
        """
        try:
            if not self._is_initialized:
                raise ExplanationError("解释服务尚未初始化")
            
            logger.info(f"开始比较 {len(instances_list)} 组实例的解释")
            
            comparison_results = []
            
            for i, (instances, label) in enumerate(zip(instances_list, labels)):
                # 获取SHAP分析
                shap_result = await self.get_shap_analysis("local", instances)
                
                # 获取LIME分析
                lime_result = await self.get_lime_analysis(instances, "batch")
                
                comparison_results.append({
                    "label": label,
                    "instance_index": i,
                    "shap_analysis": shap_result,
                    "lime_analysis": lime_result
                })
            
            # 生成比较摘要
            comparison_summary = await self._generate_comparison_summary(comparison_results)
            
            result = {
                "comparison_results": comparison_results,
                "comparison_summary": comparison_summary,
                "total_comparisons": len(instances_list),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info("解释比较完成")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"解释比较失败: {str(e)}")
            if isinstance(e, ExplanationError):
                raise
            else:
                raise ExplanationError(f"解释比较过程中发生错误: {str(e)}")
    
    async def clear_cache(self) -> Dict[str, Any]:
        """清除缓存
        
        Returns:
            清除结果
        """
        try:
            cache_size = len(self._explanation_cache)
            self._explanation_cache.clear()
            
            result = {
                "cleared_items": cache_size,
                "cleared_at": datetime.now().isoformat(),
                "message": f"已清除 {cache_size} 个解释缓存项"
            }
            
            logger.info(f"解释服务缓存已清除，共 {cache_size} 个项目")
            
            return result
            
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            raise ExplanationError(f"清除缓存过程中发生错误: {str(e)}")
    
    async def _format_shap_result(self, result: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """格式化SHAP结果"""
        formatted_result = {
            "analysis_type": "SHAP",
            "analysis_subtype": analysis_type,
            "result": result,
            "formatted_at": datetime.now().isoformat()
        }
        
        return convert_numpy_types(formatted_result)
    
    async def _format_lime_result(self, result: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """格式化LIME结果"""
        formatted_result = {
            "analysis_type": "LIME",
            "analysis_subtype": analysis_type,
            "result": result,
            "formatted_at": datetime.now().isoformat()
        }
        
        return convert_numpy_types(formatted_result)
    
    async def _generate_analysis_summary(
        self,
        shap_result: Dict[str, Any],
        lime_result: Dict[str, Any],
        feature_importance_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成分析摘要"""
        # 提取最重要的特征
        top_features = feature_importance_result.get("feature_importance", [])[:3]
        
        # 分析一致性
        shap_features = set()
        lime_features = set()
        
        # 从SHAP结果中提取重要特征
        if "result" in shap_result and "analysis_summary" in shap_result["result"]:
            shap_features = set(shap_result["result"]["analysis_summary"].get("most_important_features", []))
        
        # 从LIME结果中提取重要特征
        if "result" in lime_result and "feature_trends" in lime_result["result"]:
            lime_features = set(lime_result["result"]["feature_trends"].keys())
        
        # 计算一致性
        common_features = shap_features.intersection(lime_features)
        consistency_score = len(common_features) / max(len(shap_features), len(lime_features), 1)
        
        summary = {
            "top_features": [
                {
                    "feature": item["feature_name"],
                    "feature_name_cn": item["feature_name_cn"],
                    "importance": item["importance"],
                    "rank": item["rank"]
                }
                for item in top_features
            ],
            "method_consistency": {
                "shap_important_features": list(shap_features),
                "lime_important_features": list(lime_features),
                "common_features": list(common_features),
                "consistency_score": consistency_score
            },
            "analysis_quality": {
                "shap_quality": "good" if shap_result.get("result", {}).get("base_value") is not None else "poor",
                "lime_quality": lime_result.get("result", {}).get("quality_stats", {}).get("quality_assessment", "unknown")
            },
            "recommendations": await self._generate_explanation_recommendations(consistency_score, top_features)
        }
        
        return summary
    
    async def _generate_comparison_summary(self, comparison_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成比较摘要"""
        if not comparison_results:
            return {"error": "没有比较结果"}
        
        # 分析特征重要性的变化
        feature_variations = {}
        
        for result in comparison_results:
            label = result["label"]
            # 这里可以添加更复杂的比较逻辑
            # 简化处理：记录每个实例的标签
            feature_variations[label] = {
                "has_shap": "shap_analysis" in result,
                "has_lime": "lime_analysis" in result
            }
        
        summary = {
            "total_instances": len(comparison_results),
            "instance_labels": [result["label"] for result in comparison_results],
            "feature_variations": feature_variations,
            "comparison_insights": [
                "不同实例间的特征重要性可能存在差异",
                "建议关注一致性较高的特征",
                "局部解释可能因实例特征值不同而变化"
            ]
        }
        
        return summary
    
    async def _generate_explanation_recommendations(
        self,
        consistency_score: float,
        top_features: List[Dict[str, Any]]
    ) -> List[str]:
        """生成解释建议"""
        recommendations = []
        
        if consistency_score > 0.7:
            recommendations.append("SHAP和LIME分析结果一致性较高，解释结果可信度高")
        elif consistency_score > 0.4:
            recommendations.append("SHAP和LIME分析结果存在一定差异，建议结合两种方法综合判断")
        else:
            recommendations.append("SHAP和LIME分析结果差异较大，建议检查数据质量和模型稳定性")
        
        if top_features:
            top_feature_name = top_features[0].get("feature_name_cn", "未知特征")
            recommendations.append(f"最重要的特征是{top_feature_name}，建议重点关注")
        
        recommendations.append("建议结合业务知识验证解释结果的合理性")
        
        return recommendations
    
    def is_initialized(self) -> bool:
        """检查解释服务是否已初始化"""
        return self._is_initialized
