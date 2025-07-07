"""
LIME分析器
LIME Analyzer
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

from lime.lime_tabular import LimeTabularExplainer
from app.core.ml.model import PowerPredictionModel
from app.utils.exceptions import ExplanationError
from app.utils.constants import FEATURE_NAMES, FEATURE_NAME_MAPPING
from app.utils.helpers import convert_numpy_types

logger = logging.getLogger("power_prediction")


class LIMEAnalyzer:
    """LIME可解释性分析器"""
    
    def __init__(self, model: Optional[PowerPredictionModel] = None):
        """初始化LIME分析器
        
        Args:
            model: 训练好的模型
        """
        self.model = model
        self.explainer: Optional[LimeTabularExplainer] = None
        self.training_data: Optional[np.ndarray] = None
        self.is_initialized: bool = False
        
    async def initialize(self, training_data: np.ndarray) -> bool:
        """初始化LIME解释器
        
        Args:
            training_data: 训练数据，用于建立LIME解释器
            
        Returns:
            初始化是否成功
        """
        try:
            if self.model is None or not self.model.is_trained:
                raise ExplanationError("模型尚未加载或训练")
            
            logger.info("开始初始化LIME解释器")
            
            # 保存训练数据
            self.training_data = training_data
            
            # 创建LIME解释器
            self.explainer = LimeTabularExplainer(
                training_data=training_data,
                feature_names=FEATURE_NAMES,
                mode='regression',
                discretize_continuous=True,
                random_state=42
            )
            
            self.is_initialized = True
            
            logger.info(f"LIME解释器初始化完成，训练数据形状: {training_data.shape}")
            
            return True
            
        except Exception as e:
            logger.error(f"LIME解释器初始化失败: {str(e)}")
            raise ExplanationError(f"LIME解释器初始化过程中发生错误: {str(e)}")
    
    async def explain_instance(
        self, 
        instance: np.ndarray,
        num_features: int = 4,
        num_samples: int = 1000
    ) -> Dict[str, Any]:
        """解释单个实例
        
        Args:
            instance: 要解释的实例
            num_features: 要显示的特征数量
            num_samples: LIME采样数量
            
        Returns:
            LIME解释结果
        """
        try:
            if not self.is_initialized:
                raise ExplanationError("LIME解释器尚未初始化")
            
            if instance.ndim == 1:
                instance = instance.reshape(1, -1)
            
            logger.info(f"开始LIME实例解释，特征数: {num_features}, 采样数: {num_samples}")
            
            # 定义预测函数
            def predict_fn(X):
                # 确保输入是2D数组
                if X.ndim == 1:
                    X = X.reshape(1, -1)
                
                # 使用模型进行预测
                predictions = []
                for row in X:
                    pred = self.model.model.predict(row.reshape(1, -1))
                    predictions.append(pred[0])
                
                return np.array(predictions)
            
            # 生成解释
            explanation = self.explainer.explain_instance(
                data_row=instance[0],
                predict_fn=predict_fn,
                num_features=num_features,
                num_samples=num_samples
            )
            
            # 获取预测值
            prediction = predict_fn(instance)[0]
            
            # 提取解释信息
            feature_contributions = {}
            explanation_list = explanation.as_list()
            
            for feature_desc, contribution in explanation_list:
                # 解析特征描述以获取特征名
                feature_name = await self._parse_feature_name(feature_desc)
                
                feature_contributions[feature_name] = {
                    "contribution": float(contribution),
                    "description": feature_desc,
                    "feature_name_cn": FEATURE_NAME_MAPPING.get(feature_name, feature_name)
                }
            
            # 获取局部模型信息
            local_model_r2 = explanation.score
            intercept = explanation.intercept[0] if hasattr(explanation, 'intercept') else 0.0
            
            # 计算贡献度排序
            sorted_contributions = sorted(
                feature_contributions.items(),
                key=lambda x: abs(x[1]["contribution"]),
                reverse=True
            )
            
            result = {
                "prediction": float(prediction),
                "local_model_r2": float(local_model_r2),
                "intercept": float(intercept),
                "feature_contributions": feature_contributions,
                "sorted_contributions": [
                    {
                        "feature": item[0],
                        "feature_name_cn": item[1]["feature_name_cn"],
                        "contribution": item[1]["contribution"],
                        "description": item[1]["description"],
                        "abs_contribution": abs(item[1]["contribution"])
                    }
                    for item in sorted_contributions
                ],
                "explanation_quality": {
                    "local_model_r2": float(local_model_r2),
                    "num_features_used": len(feature_contributions),
                    "num_samples_used": num_samples
                },
                "explanation_text": await self._generate_explanation_text(
                    feature_contributions, prediction, intercept
                ),
                "analysis_time": datetime.now().isoformat()
            }
            
            logger.info(f"LIME实例解释完成，局部模型R²: {local_model_r2:.3f}")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"LIME实例解释失败: {str(e)}")
            raise ExplanationError(f"LIME实例解释过程中发生错误: {str(e)}")
    
    async def explain_batch(
        self, 
        instances: np.ndarray,
        num_features: int = 4,
        num_samples: int = 1000
    ) -> List[Dict[str, Any]]:
        """批量解释多个实例
        
        Args:
            instances: 要解释的实例数组
            num_features: 要显示的特征数量
            num_samples: LIME采样数量
            
        Returns:
            批量LIME解释结果
        """
        try:
            logger.info(f"开始批量LIME解释，实例数量: {instances.shape[0]}")
            
            results = []
            
            for i in range(instances.shape[0]):
                try:
                    instance = instances[i:i+1]  # 保持2D形状
                    
                    explanation = await self.explain_instance(
                        instance, num_features, num_samples
                    )
                    
                    explanation["instance_index"] = i
                    results.append(explanation)
                    
                except Exception as e:
                    logger.error(f"第 {i+1} 个实例LIME解释失败: {str(e)}")
                    error_result = {
                        "instance_index": i,
                        "error": str(e),
                        "analysis_time": datetime.now().isoformat()
                    }
                    results.append(error_result)
            
            logger.info(f"批量LIME解释完成，成功: {len([r for r in results if 'error' not in r])}, 失败: {len([r for r in results if 'error' in r])}")
            
            return results
            
        except Exception as e:
            logger.error(f"批量LIME解释失败: {str(e)}")
            raise ExplanationError(f"批量LIME解释过程中发生错误: {str(e)}")
    
    async def explain_hourly_predictions(
        self, 
        prediction_data: np.ndarray,
        hours: List[int],
        num_features: int = 4
    ) -> Dict[str, Any]:
        """为每小时预测生成LIME解释
        
        Args:
            prediction_data: 预测数据（24小时）
            hours: 小时列表
            num_features: 要显示的特征数量
            
        Returns:
            按小时组织的LIME解释结果
        """
        try:
            if len(hours) != prediction_data.shape[0]:
                raise ExplanationError("小时列表长度与预测数据不匹配")
            
            logger.info(f"开始为 {len(hours)} 个小时生成LIME解释")
            
            # 进行批量解释
            batch_explanations = await self.explain_batch(prediction_data, num_features)
            
            # 按小时组织结果
            hourly_explanations = {}
            
            for i, hour in enumerate(hours):
                if i < len(batch_explanations) and 'error' not in batch_explanations[i]:
                    explanation = batch_explanations[i]
                    explanation["hour"] = hour
                    hourly_explanations[str(hour)] = explanation
            
            # 分析特征重要性趋势
            feature_trends = await self._analyze_feature_trends(batch_explanations, hours)
            
            # 计算解释质量统计
            quality_stats = await self._calculate_quality_stats(batch_explanations)
            
            result = {
                "hourly_explanations": hourly_explanations,
                "feature_trends": feature_trends,
                "quality_stats": quality_stats,
                "analysis_summary": {
                    "total_hours": len(hours),
                    "successful_explanations": len([exp for exp in batch_explanations if 'error' not in exp]),
                    "failed_explanations": len([exp for exp in batch_explanations if 'error' in exp]),
                    "average_local_r2": np.mean([
                        exp["local_model_r2"] for exp in batch_explanations 
                        if 'error' not in exp and 'local_model_r2' in exp
                    ]) if batch_explanations else 0.0
                },
                "analysis_time": datetime.now().isoformat()
            }
            
            logger.info("按小时LIME解释完成")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"按小时LIME解释失败: {str(e)}")
            raise ExplanationError(f"按小时LIME解释过程中发生错误: {str(e)}")
    
    async def compare_explanations(
        self, 
        instances: np.ndarray,
        instance_labels: List[str]
    ) -> Dict[str, Any]:
        """比较多个实例的LIME解释
        
        Args:
            instances: 要比较的实例
            instance_labels: 实例标签
            
        Returns:
            比较分析结果
        """
        try:
            logger.info(f"开始比较 {len(instances)} 个实例的LIME解释")
            
            # 获取所有实例的解释
            explanations = await self.explain_batch(instances)
            
            # 提取特征贡献进行比较
            feature_comparison = {}
            
            for feature in FEATURE_NAMES:
                feature_comparison[feature] = {
                    "contributions": [],
                    "labels": [],
                    "feature_name_cn": FEATURE_NAME_MAPPING.get(feature, feature)
                }
            
            for i, explanation in enumerate(explanations):
                if 'error' not in explanation:
                    label = instance_labels[i] if i < len(instance_labels) else f"实例{i+1}"
                    
                    for feature in FEATURE_NAMES:
                        contribution = 0.0
                        if feature in explanation.get("feature_contributions", {}):
                            contribution = explanation["feature_contributions"][feature]["contribution"]
                        
                        feature_comparison[feature]["contributions"].append(contribution)
                        feature_comparison[feature]["labels"].append(label)
            
            # 计算特征贡献的统计信息
            comparison_stats = {}
            for feature, data in feature_comparison.items():
                if data["contributions"]:
                    comparison_stats[feature] = {
                        "mean": float(np.mean(data["contributions"])),
                        "std": float(np.std(data["contributions"])),
                        "min": float(np.min(data["contributions"])),
                        "max": float(np.max(data["contributions"])),
                        "range": float(np.max(data["contributions"]) - np.min(data["contributions"]))
                    }
            
            result = {
                "individual_explanations": explanations,
                "feature_comparison": feature_comparison,
                "comparison_stats": comparison_stats,
                "instance_labels": instance_labels,
                "analysis_time": datetime.now().isoformat()
            }
            
            logger.info("LIME解释比较完成")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"LIME解释比较失败: {str(e)}")
            raise ExplanationError(f"LIME解释比较过程中发生错误: {str(e)}")
    
    async def _parse_feature_name(self, feature_desc: str) -> str:
        """从LIME特征描述中解析特征名"""
        # LIME的特征描述通常包含范围信息，需要提取特征名
        for feature_name in FEATURE_NAMES:
            if feature_name in feature_desc:
                return feature_name
        
        # 如果没有找到匹配的特征名，返回描述的第一部分
        return feature_desc.split()[0] if feature_desc else "unknown"
    
    async def _generate_explanation_text(
        self, 
        feature_contributions: Dict[str, Any], 
        prediction: float, 
        intercept: float
    ) -> str:
        """生成解释文本"""
        explanation_parts = []
        
        # 基准值说明
        explanation_parts.append(f"局部模型基准值为 {intercept:.2f}")
        
        # 按贡献度排序特征
        sorted_features = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]["contribution"]),
            reverse=True
        )
        
        # 说明最重要的特征
        if sorted_features:
            top_feature = sorted_features[0]
            feature_name_cn = top_feature[1]["feature_name_cn"]
            contribution = top_feature[1]["contribution"]
            
            if contribution > 0:
                explanation_parts.append(f"{feature_name_cn}对预测有最大正向贡献 (+{contribution:.2f})")
            else:
                explanation_parts.append(f"{feature_name_cn}对预测有最大负向贡献 ({contribution:.2f})")
        
        # 最终预测说明
        explanation_parts.append(f"最终预测值为 {prediction:.2f}")
        
        return "；".join(explanation_parts)
    
    async def _analyze_feature_trends(
        self, 
        explanations: List[Dict[str, Any]], 
        hours: List[int]
    ) -> Dict[str, Any]:
        """分析特征贡献趋势"""
        trends = {}
        
        for feature in FEATURE_NAMES:
            contributions = []
            valid_hours = []
            
            for i, explanation in enumerate(explanations):
                if 'error' not in explanation and feature in explanation.get("feature_contributions", {}):
                    contribution = explanation["feature_contributions"][feature]["contribution"]
                    contributions.append(contribution)
                    valid_hours.append(hours[i] if i < len(hours) else i)
            
            if contributions:
                trends[feature] = {
                    "feature_name_cn": FEATURE_NAME_MAPPING.get(feature, feature),
                    "contributions": contributions,
                    "hours": valid_hours,
                    "trend_stats": {
                        "mean": float(np.mean(contributions)),
                        "std": float(np.std(contributions)),
                        "min": float(np.min(contributions)),
                        "max": float(np.max(contributions)),
                        "trend_direction": "increasing" if contributions[-1] > contributions[0] else "decreasing"
                    }
                }
        
        return trends
    
    async def _calculate_quality_stats(self, explanations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算解释质量统计"""
        valid_explanations = [exp for exp in explanations if 'error' not in exp]
        
        if not valid_explanations:
            return {"error": "没有有效的解释结果"}
        
        r2_scores = [exp.get("local_model_r2", 0.0) for exp in valid_explanations]
        num_features_used = [len(exp.get("feature_contributions", {})) for exp in valid_explanations]
        
        return {
            "total_explanations": len(explanations),
            "valid_explanations": len(valid_explanations),
            "average_r2": float(np.mean(r2_scores)),
            "min_r2": float(np.min(r2_scores)),
            "max_r2": float(np.max(r2_scores)),
            "std_r2": float(np.std(r2_scores)),
            "average_features_used": float(np.mean(num_features_used)),
            "quality_assessment": "good" if np.mean(r2_scores) > 0.7 else "moderate" if np.mean(r2_scores) > 0.5 else "poor"
        }
