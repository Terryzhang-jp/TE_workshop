"""
机器学习模型定义
Machine Learning Model Definition
"""

import joblib
import numpy as np
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime

import xgboost as xgb
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from app.config import settings
from app.utils.exceptions import ModelTrainingError, ModelNotFoundError
from app.utils.helpers import ensure_directory_exists, calculate_model_metrics
from app.utils.constants import MODEL_METRICS_KEYS

logger = logging.getLogger("power_prediction")


class PowerPredictionModel:
    """电力需求预测模型类"""
    
    def __init__(self, model_params: Optional[Dict[str, Any]] = None):
        """初始化模型
        
        Args:
            model_params: 模型参数，如果为None则使用配置中的参数
        """
        self.model_params = model_params or settings.xgboost_params.copy()
        self.model: Optional[xgb.XGBRegressor] = None
        self.is_trained: bool = False
        self.training_info: Dict[str, Any] = {}
        self.feature_importance: Dict[str, float] = {}
        
        # 初始化模型
        self._initialize_model()
        
    def _initialize_model(self):
        """初始化XGBoost模型"""
        try:
            self.model = xgb.XGBRegressor(**self.model_params)
            logger.info(f"XGBoost模型初始化完成，参数: {self.model_params}")
        except Exception as e:
            logger.error(f"模型初始化失败: {str(e)}")
            raise ModelTrainingError(f"模型初始化失败: {str(e)}")
    
    async def train(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """训练模型
        
        Args:
            X_train: 训练特征
            y_train: 训练目标
            X_val: 验证特征（可选）
            y_val: 验证目标（可选）
            
        Returns:
            训练结果字典
        """
        try:
            logger.info("开始训练XGBoost模型")
            start_time = datetime.now()
            
            # 准备验证数据
            eval_set = None
            if X_val is not None and y_val is not None:
                eval_set = [(X_train, y_train), (X_val, y_val)]
                logger.info(f"使用验证集，训练集大小: {X_train.shape}, 验证集大小: {X_val.shape}")
            else:
                logger.info(f"仅使用训练集，大小: {X_train.shape}")
            
            # 训练模型
            self.model.fit(
                X_train, 
                y_train,
                eval_set=eval_set,
                verbose=False
            )
            
            # 记录训练时间
            training_time = (datetime.now() - start_time).total_seconds()
            
            # 标记为已训练
            self.is_trained = True
            
            # 计算特征重要性
            self.feature_importance = await self._calculate_feature_importance()
            
            # 评估模型
            train_metrics = await self._evaluate_model(X_train, y_train, "训练集")
            
            val_metrics = {}
            if X_val is not None and y_val is not None:
                val_metrics = await self._evaluate_model(X_val, y_val, "验证集")
            
            # 交叉验证
            cv_scores = await self._cross_validate(X_train, y_train)
            
            # 保存训练信息
            self.training_info = {
                "training_time": training_time,
                "training_samples": X_train.shape[0],
                "feature_count": X_train.shape[1],
                "model_params": self.model_params,
                "train_metrics": train_metrics,
                "val_metrics": val_metrics,
                "cv_scores": cv_scores,
                "feature_importance": self.feature_importance,
                "trained_at": datetime.now().isoformat()
            }
            
            logger.info(f"模型训练完成，耗时: {training_time:.2f}秒")
            logger.info(f"训练集指标: MAE={train_metrics['mae']:.2f}, RMSE={train_metrics['rmse']:.2f}, R²={train_metrics['r2_score']:.3f}")
            
            if val_metrics:
                logger.info(f"验证集指标: MAE={val_metrics['mae']:.2f}, RMSE={val_metrics['rmse']:.2f}, R²={val_metrics['r2_score']:.3f}")
            
            return self.training_info
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            raise ModelTrainingError(f"模型训练过程中发生错误: {str(e)}")
    
    async def predict(self, X: np.ndarray) -> np.ndarray:
        """进行预测
        
        Args:
            X: 特征矩阵
            
        Returns:
            预测结果
        """
        try:
            if not self.is_trained:
                raise ModelNotFoundError("模型尚未训练")
            
            logger.info(f"开始预测，输入形状: {X.shape}")
            
            predictions = self.model.predict(X)
            
            # 确保预测值为正数（电力使用量不能为负）
            predictions = np.maximum(predictions, 0)
            
            logger.info(f"预测完成，输出形状: {predictions.shape}")
            logger.info(f"预测值范围: {predictions.min():.2f} - {predictions.max():.2f}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"预测失败: {str(e)}")
            if isinstance(e, ModelNotFoundError):
                raise
            else:
                raise ModelTrainingError(f"预测过程中发生错误: {str(e)}")
    
    async def save_model(self, file_path: Optional[str] = None) -> str:
        """保存模型
        
        Args:
            file_path: 保存路径，如果为None则使用默认路径
            
        Returns:
            实际保存的文件路径
        """
        try:
            if not self.is_trained:
                raise ModelNotFoundError("模型尚未训练，无法保存")
            
            # 确定保存路径
            if file_path is None:
                ensure_directory_exists(settings.model_save_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"{settings.model_save_path}/xgboost_model_{timestamp}.joblib"
            
            # 准备保存的数据
            model_data = {
                "model": self.model,
                "model_params": self.model_params,
                "training_info": self.training_info,
                "feature_importance": self.feature_importance,
                "is_trained": self.is_trained
            }
            
            # 保存模型
            joblib.dump(model_data, file_path)
            
            logger.info(f"模型已保存到: {file_path}")
            
            return file_path
            
        except Exception as e:
            logger.error(f"模型保存失败: {str(e)}")
            raise ModelTrainingError(f"模型保存过程中发生错误: {str(e)}")
    
    async def load_model(self, file_path: str) -> bool:
        """加载模型
        
        Args:
            file_path: 模型文件路径
            
        Returns:
            加载是否成功
        """
        try:
            if not Path(file_path).exists():
                raise ModelNotFoundError(f"模型文件不存在: {file_path}")
            
            logger.info(f"开始加载模型: {file_path}")
            
            # 加载模型数据
            model_data = joblib.load(file_path)
            
            # 恢复模型状态
            self.model = model_data["model"]
            self.model_params = model_data["model_params"]
            self.training_info = model_data["training_info"]
            self.feature_importance = model_data["feature_importance"]
            self.is_trained = model_data["is_trained"]
            
            logger.info("模型加载成功")
            logger.info(f"模型训练时间: {self.training_info.get('trained_at', 'Unknown')}")
            
            return True
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            if isinstance(e, ModelNotFoundError):
                raise
            else:
                raise ModelTrainingError(f"模型加载过程中发生错误: {str(e)}")
    
    async def _calculate_feature_importance(self) -> Dict[str, float]:
        """计算特征重要性"""
        if not self.is_trained:
            return {}
        
        try:
            # 获取XGBoost的特征重要性
            importance_scores = self.model.feature_importances_
            
            # 创建特征重要性字典
            from app.utils.constants import FEATURE_NAMES
            feature_importance = {}
            
            for i, feature_name in enumerate(FEATURE_NAMES):
                if i < len(importance_scores):
                    feature_importance[feature_name] = float(importance_scores[i])
            
            logger.info(f"特征重要性计算完成: {feature_importance}")
            
            return feature_importance
            
        except Exception as e:
            logger.error(f"特征重要性计算失败: {str(e)}")
            return {}
    
    async def _evaluate_model(self, X: np.ndarray, y: np.ndarray, dataset_name: str) -> Dict[str, float]:
        """评估模型性能"""
        try:
            predictions = await self.predict(X)
            metrics = calculate_model_metrics(y, predictions)
            
            logger.info(f"{dataset_name}评估完成: {metrics}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"{dataset_name}评估失败: {str(e)}")
            return {}
    
    async def _cross_validate(self, X: np.ndarray, y: np.ndarray, cv_folds: int = 5) -> Dict[str, Any]:
        """交叉验证"""
        try:
            logger.info(f"开始 {cv_folds} 折交叉验证")
            
            # 使用时间序列分割
            tscv = TimeSeriesSplit(n_splits=cv_folds)
            
            # 计算交叉验证分数
            cv_scores = cross_val_score(
                self.model, X, y, 
                cv=tscv, 
                scoring='neg_mean_absolute_error',
                n_jobs=-1
            )
            
            # 转换为正值
            cv_scores = -cv_scores
            
            cv_result = {
                "scores": cv_scores.tolist(),
                "mean": float(cv_scores.mean()),
                "std": float(cv_scores.std()),
                "min": float(cv_scores.min()),
                "max": float(cv_scores.max())
            }
            
            logger.info(f"交叉验证完成: 平均MAE={cv_result['mean']:.2f}±{cv_result['std']:.2f}")
            
            return cv_result
            
        except Exception as e:
            logger.error(f"交叉验证失败: {str(e)}")
            return {}
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "is_trained": self.is_trained,
            "model_type": "XGBoost",
            "model_params": self.model_params,
            "training_info": self.training_info,
            "feature_importance": self.feature_importance
        }
