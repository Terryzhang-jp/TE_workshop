"""
SHAP分析器
SHAP Analyzer
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

import shap
from app.core.ml.model import PowerPredictionModel
from app.utils.exceptions import ExplanationError
from app.utils.constants import FEATURE_NAMES, FEATURE_NAME_MAPPING
from app.utils.helpers import convert_numpy_types

logger = logging.getLogger("power_prediction")


class SHAPAnalyzer:
    """SHAP可解释性分析器"""
    
    def __init__(self, model: Optional[PowerPredictionModel] = None):
        """初始化SHAP分析器
        
        Args:
            model: 训练好的模型
        """
        self.model = model
        self.explainer: Optional[shap.TreeExplainer] = None
        self.background_data: Optional[np.ndarray] = None
        self.is_initialized: bool = False
        
    async def initialize(self, background_data: np.ndarray) -> bool:
        """初始化SHAP解释器
        
        Args:
            background_data: 背景数据，用于计算SHAP基准值
            
        Returns:
            初始化是否成功
        """
        try:
            if self.model is None or not self.model.is_trained:
                raise ExplanationError("模型尚未加载或训练")
            
            logger.info("开始初始化SHAP解释器")
            
            # 保存背景数据
            self.background_data = background_data
            
            # 创建TreeExplainer（适用于XGBoost）
            self.explainer = shap.TreeExplainer(
                self.model.model,
                data=background_data,
                feature_perturbation='tree_path_dependent'
            )
            
            self.is_initialized = True
            
            logger.info(f"SHAP解释器初始化完成，背景数据形状: {background_data.shape}")
            
            return True
            
        except Exception as e:
            logger.error(f"SHAP解释器初始化失败: {str(e)}")
            raise ExplanationError(f"SHAP解释器初始化过程中发生错误: {str(e)}")
    
    async def explain_global(self) -> Dict[str, Any]:
        """全局SHAP分析
        
        Returns:
            全局特征重要性分析结果
        """
        try:
            if not self.is_initialized:
                raise ExplanationError("SHAP解释器尚未初始化")
            
            logger.info("开始全局SHAP分析")
            
            # 计算背景数据的SHAP值
            shap_values = self.explainer.shap_values(self.background_data)
            
            # 计算全局特征重要性
            global_importance = await self._calculate_global_importance(shap_values)
            
            # 计算特征交互
            feature_interactions = await self._calculate_feature_interactions(shap_values)
            
            # 生成摘要统计
            summary_stats = await self._generate_summary_stats(shap_values)
            
            result = {
                "global_importance": global_importance,
                "feature_interactions": feature_interactions,
                "summary_stats": summary_stats,
                "base_value": float(self.explainer.expected_value),
                "analysis_time": datetime.now().isoformat(),
                "sample_count": self.background_data.shape[0]
            }
            
            logger.info("全局SHAP分析完成")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"全局SHAP分析失败: {str(e)}")
            raise ExplanationError(f"全局SHAP分析过程中发生错误: {str(e)}")
    
    async def explain_local(self, instances: np.ndarray) -> List[Dict[str, Any]]:
        """局部SHAP分析
        
        Args:
            instances: 要解释的实例
            
        Returns:
            每个实例的SHAP分析结果
        """
        try:
            if not self.is_initialized:
                raise ExplanationError("SHAP解释器尚未初始化")
            
            logger.info(f"开始局部SHAP分析，实例数量: {instances.shape[0]}")
            
            # 计算SHAP值
            shap_values = self.explainer.shap_values(instances)
            
            # 获取预测值
            predictions = await self.model.predict(instances)
            
            results = []
            
            for i in range(instances.shape[0]):
                instance_shap = shap_values[i]
                instance_features = instances[i]
                prediction = predictions[i]
                
                # 创建特征贡献字典
                feature_contributions = {}
                for j, feature_name in enumerate(FEATURE_NAMES):
                    if j < len(instance_shap):
                        feature_contributions[feature_name] = {
                            "shap_value": float(instance_shap[j]),
                            "feature_value": float(instance_features[j]),
                            "feature_name_cn": FEATURE_NAME_MAPPING.get(feature_name, feature_name)
                        }
                
                # 计算贡献度排序
                sorted_contributions = sorted(
                    feature_contributions.items(),
                    key=lambda x: abs(x[1]["shap_value"]),
                    reverse=True
                )
                
                instance_result = {
                    "instance_index": i,
                    "prediction": float(prediction),
                    "base_value": float(self.explainer.expected_value),
                    "feature_contributions": feature_contributions,
                    "sorted_contributions": [
                        {
                            "feature": item[0],
                            "feature_name_cn": item[1]["feature_name_cn"],
                            "shap_value": item[1]["shap_value"],
                            "feature_value": item[1]["feature_value"],
                            "abs_contribution": abs(item[1]["shap_value"])
                        }
                        for item in sorted_contributions
                    ],
                    "total_shap_sum": float(np.sum(instance_shap)),
                    "prediction_explanation": await self._generate_prediction_explanation(
                        feature_contributions, prediction, self.explainer.expected_value
                    )
                }
                
                results.append(instance_result)
            
            logger.info(f"局部SHAP分析完成，处理了 {len(results)} 个实例")
            
            return convert_numpy_types(results)
            
        except Exception as e:
            logger.error(f"局部SHAP分析失败: {str(e)}")
            raise ExplanationError(f"局部SHAP分析过程中发生错误: {str(e)}")
    
    async def explain_prediction_for_hours(
        self, 
        prediction_data: np.ndarray,
        hours: List[int]
    ) -> Dict[str, Any]:
        """为特定小时的预测生成SHAP解释
        
        Args:
            prediction_data: 预测数据（24小时）
            hours: 要解释的小时列表
            
        Returns:
            按小时组织的SHAP解释结果
        """
        try:
            if len(hours) != prediction_data.shape[0]:
                raise ExplanationError("小时列表长度与预测数据不匹配")
            
            logger.info(f"开始为 {len(hours)} 个小时生成SHAP解释")
            
            # 进行局部SHAP分析
            local_explanations = await self.explain_local(prediction_data)
            
            # 按小时组织结果
            hourly_explanations = {}
            
            for i, hour in enumerate(hours):
                if i < len(local_explanations):
                    explanation = local_explanations[i]
                    explanation["hour"] = hour
                    hourly_explanations[str(hour)] = explanation
            
            # 计算小时间的特征重要性变化
            feature_importance_by_hour = await self._calculate_hourly_feature_importance(
                local_explanations, hours
            )
            
            result = {
                "hourly_explanations": hourly_explanations,
                "feature_importance_by_hour": feature_importance_by_hour,
                "analysis_summary": {
                    "total_hours": len(hours),
                    "most_important_features": await self._find_most_important_features(local_explanations),
                    "prediction_range": {
                        "min": min([exp["prediction"] for exp in local_explanations]),
                        "max": max([exp["prediction"] for exp in local_explanations])
                    }
                },
                "analysis_time": datetime.now().isoformat()
            }
            
            logger.info("按小时SHAP解释完成")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"按小时SHAP解释失败: {str(e)}")
            raise ExplanationError(f"按小时SHAP解释过程中发生错误: {str(e)}")
    
    async def _calculate_global_importance(self, shap_values: np.ndarray) -> List[Dict[str, Any]]:
        """计算全局特征重要性"""
        # 计算每个特征的平均绝对SHAP值
        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
        
        importance_list = []
        for i, feature_name in enumerate(FEATURE_NAMES):
            if i < len(mean_abs_shap):
                importance_list.append({
                    "feature": feature_name,
                    "feature_name_cn": FEATURE_NAME_MAPPING.get(feature_name, feature_name),
                    "importance": float(mean_abs_shap[i]),
                    "rank": 0  # 将在排序后设置
                })
        
        # 按重要性排序
        importance_list.sort(key=lambda x: x["importance"], reverse=True)
        
        # 设置排名
        for i, item in enumerate(importance_list):
            item["rank"] = i + 1
        
        return importance_list
    
    async def _calculate_feature_interactions(self, shap_values: np.ndarray) -> Dict[str, Any]:
        """计算特征交互"""
        # 简化的特征交互分析
        # 计算特征之间的相关性
        correlations = np.corrcoef(shap_values.T)
        
        interactions = {}
        for i, feature1 in enumerate(FEATURE_NAMES):
            if i < correlations.shape[0]:
                for j, feature2 in enumerate(FEATURE_NAMES):
                    if j < correlations.shape[1] and i != j:
                        interaction_key = f"{feature1}_{feature2}"
                        interactions[interaction_key] = {
                            "feature1": feature1,
                            "feature2": feature2,
                            "correlation": float(correlations[i, j])
                        }
        
        return interactions
    
    async def _generate_summary_stats(self, shap_values: np.ndarray) -> Dict[str, Any]:
        """生成摘要统计"""
        return {
            "total_samples": shap_values.shape[0],
            "total_features": shap_values.shape[1],
            "mean_prediction_impact": float(np.mean(np.sum(np.abs(shap_values), axis=1))),
            "std_prediction_impact": float(np.std(np.sum(np.abs(shap_values), axis=1))),
            "feature_stats": {
                feature_name: {
                    "mean_shap": float(np.mean(shap_values[:, i])),
                    "std_shap": float(np.std(shap_values[:, i])),
                    "min_shap": float(np.min(shap_values[:, i])),
                    "max_shap": float(np.max(shap_values[:, i]))
                }
                for i, feature_name in enumerate(FEATURE_NAMES)
                if i < shap_values.shape[1]
            }
        }
    
    async def _generate_prediction_explanation(
        self, 
        feature_contributions: Dict[str, Any], 
        prediction: float, 
        base_value: float
    ) -> str:
        """生成预测解释文本"""
        # 找出最重要的正负贡献特征
        positive_contributions = {k: v for k, v in feature_contributions.items() if v["shap_value"] > 0}
        negative_contributions = {k: v for k, v in feature_contributions.items() if v["shap_value"] < 0}
        
        explanation_parts = []
        
        # 基准值说明
        explanation_parts.append(f"基准预测值为 {base_value:.2f}")
        
        # 正贡献说明
        if positive_contributions:
            top_positive = max(positive_contributions.items(), key=lambda x: x[1]["shap_value"])
            explanation_parts.append(
                f"{top_positive[1]['feature_name_cn']}对预测值有最大正向影响 (+{top_positive[1]['shap_value']:.2f})"
            )
        
        # 负贡献说明
        if negative_contributions:
            top_negative = min(negative_contributions.items(), key=lambda x: x[1]["shap_value"])
            explanation_parts.append(
                f"{top_negative[1]['feature_name_cn']}对预测值有最大负向影响 ({top_negative[1]['shap_value']:.2f})"
            )
        
        # 最终预测说明
        explanation_parts.append(f"最终预测值为 {prediction:.2f}")
        
        return "；".join(explanation_parts)
    
    async def _calculate_hourly_feature_importance(
        self, 
        explanations: List[Dict[str, Any]], 
        hours: List[int]
    ) -> Dict[str, List[float]]:
        """计算按小时的特征重要性"""
        hourly_importance = {feature: [] for feature in FEATURE_NAMES}
        
        for explanation in explanations:
            for feature in FEATURE_NAMES:
                if feature in explanation["feature_contributions"]:
                    importance = abs(explanation["feature_contributions"][feature]["shap_value"])
                    hourly_importance[feature].append(importance)
                else:
                    hourly_importance[feature].append(0.0)
        
        return hourly_importance
    
    async def _find_most_important_features(self, explanations: List[Dict[str, Any]]) -> List[str]:
        """找出最重要的特征"""
        feature_total_importance = {feature: 0.0 for feature in FEATURE_NAMES}
        
        for explanation in explanations:
            for feature in FEATURE_NAMES:
                if feature in explanation["feature_contributions"]:
                    feature_total_importance[feature] += abs(
                        explanation["feature_contributions"][feature]["shap_value"]
                    )
        
        # 按总重要性排序
        sorted_features = sorted(
            feature_total_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [feature for feature, _ in sorted_features[:3]]  # 返回前3个最重要的特征
