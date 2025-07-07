"""
模型训练器
Model Trainer
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from sklearn.model_selection import train_test_split
import logging
from datetime import datetime

from app.core.data.loader import DataLoader
from app.core.data.processor import DataProcessor
from app.core.data.validator import DataValidator
from app.core.ml.model import PowerPredictionModel
from app.config import settings
from app.utils.exceptions import ModelTrainingError, DataValidationError
from app.utils.constants import TARGET_DATE, TRAINING_START_DATE, TRAINING_END_DATE, TARGET_COLUMN, TIME_COLUMN

logger = logging.getLogger("power_prediction")


class ModelTrainer:
    """模型训练器类"""
    
    def __init__(self):
        """初始化模型训练器"""
        self.data_loader = DataLoader()
        self.data_processor = DataProcessor()
        self.data_validator = DataValidator()
        self.model: Optional[PowerPredictionModel] = None
        self.training_history: Dict[str, Any] = {}
        
    async def train_model(
        self,
        target_date: Optional[str] = None,
        weeks_before: int = 3,
        validation_split: float = 0.2,
        model_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """训练模型
        
        Args:
            target_date: 目标预测日期
            weeks_before: 使用目标日期前几周的数据
            validation_split: 验证集比例
            model_params: 模型参数
            
        Returns:
            训练结果字典
        """
        try:
            logger.info("开始模型训练流程")
            start_time = datetime.now()
            
            # 使用配置中的目标日期或传入的日期
            target_date = target_date or settings.target_date
            
            # 步骤1: 加载训练数据
            logger.info("步骤1: 加载训练数据")
            training_data = await self.data_loader.load_training_data(target_date, weeks_before)

            # 步骤2: 验证原始数据
            logger.info("步骤2: 验证原始数据")
            validation_result = await self.data_validator.validate_raw_data(training_data)
            if not validation_result["is_valid"]:
                raise DataValidationError(f"数据验证失败: {validation_result['errors']}")

            # 步骤3: 基础数据处理（仅特征工程，不涉及统计量计算）
            logger.info("步骤3: 基础数据处理")
            X, y = await self.data_processor.process_training_data(training_data)

            # 步骤4: 分割训练集和验证集（在统计量计算之前）
            logger.info("步骤4: 分割数据集（避免数据泄漏）")
            X_train, X_val, y_train, y_val = await self._split_data(X, y, validation_split)

            # 重新构建DataFrame用于后续处理
            train_df = await self._reconstruct_dataframe(training_data, X_train, y_train)
            val_df = await self._reconstruct_dataframe(training_data, X_val, y_val)

            # 步骤5: 处理训练集和验证集（避免数据泄漏）
            logger.info("步骤5: 处理训练验证数据（无数据泄漏）")
            (X_train_processed, y_train_processed), (X_val_processed, y_val_processed) = await self.data_processor.process_train_val_data_no_leakage(train_df, val_df)

            # 步骤6: 验证处理后的数据
            logger.info("步骤6: 验证处理后的数据")
            processed_validation = await self.data_validator.validate_training_data(X_train_processed, y_train_processed)
            if not processed_validation["is_valid"]:
                raise DataValidationError(f"处理后数据验证失败: {processed_validation['errors']}")

            # 步骤7: 特征缩放（仅在训练集上拟合，避免数据泄漏）
            logger.info("步骤7: 特征缩放（无数据泄漏）")
            X_train_scaled = await self.data_processor.fit_scaler_on_train_only(X_train_processed)
            X_val_scaled = await self.data_processor.transform_validation_set(X_val_processed)

            # 步骤8: 初始化和训练模型
            logger.info("步骤8: 初始化和训练模型")
            self.model = PowerPredictionModel(model_params)
            training_result = await self.model.train(X_train_scaled, y_train_processed, X_val_scaled, y_val_processed)

            # 步骤9: 保存模型
            logger.info("步骤9: 保存模型")
            model_path = await self.model.save_model()
            
            # 记录训练历史
            total_time = (datetime.now() - start_time).total_seconds()
            self.training_history = {
                "target_date": target_date,
                "weeks_before": weeks_before,
                "validation_split": validation_split,
                "total_training_time": total_time,
                "model_path": model_path,
                "data_info": {
                    "total_samples": len(training_data),
                    "training_samples": X_train_scaled.shape[0],
                    "validation_samples": X_val_scaled.shape[0],
                    "feature_count": X_train_scaled.shape[1]
                },
                "training_result": training_result,
                "data_validation": {
                    "raw_data_validation": validation_result,
                    "processed_data_validation": processed_validation
                },
                "completed_at": datetime.now().isoformat()
            }
            
            logger.info(f"模型训练流程完成，总耗时: {total_time:.2f}秒")
            logger.info(f"模型已保存到: {model_path}")
            
            return self.training_history
            
        except Exception as e:
            logger.error(f"模型训练流程失败: {str(e)}")
            if isinstance(e, (ModelTrainingError, DataValidationError)):
                raise
            else:
                raise ModelTrainingError(f"模型训练流程中发生错误: {str(e)}")
    
    async def retrain_model(
        self,
        new_data_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """重新训练模型
        
        Args:
            new_data_path: 新的数据文件路径
            **kwargs: 其他训练参数
            
        Returns:
            重新训练结果
        """
        try:
            logger.info("开始重新训练模型")
            
            # 如果提供了新的数据路径，更新数据加载器
            if new_data_path:
                self.data_loader = DataLoader(new_data_path)
                logger.info(f"使用新的数据文件: {new_data_path}")
            
            # 重置数据处理器
            self.data_processor = DataProcessor()
            
            # 执行训练
            result = await self.train_model(**kwargs)
            
            logger.info("模型重新训练完成")
            
            return result
            
        except Exception as e:
            logger.error(f"模型重新训练失败: {str(e)}")
            raise ModelTrainingError(f"模型重新训练过程中发生错误: {str(e)}")
    
    async def evaluate_model(self, test_data_path: Optional[str] = None) -> Dict[str, Any]:
        """评估模型性能
        
        Args:
            test_data_path: 测试数据路径
            
        Returns:
            评估结果
        """
        try:
            if self.model is None or not self.model.is_trained:
                raise ModelTrainingError("模型尚未训练")
            
            logger.info("开始评估模型性能")
            
            # 加载测试数据
            if test_data_path:
                test_loader = DataLoader(test_data_path)
                test_data = await test_loader.load_raw_data()
            else:
                # 使用训练数据的一部分作为测试数据
                test_data = await self.data_loader.load_training_data()
            
            # 处理测试数据
            X_test, y_test = await self.data_processor.process_training_data(test_data)
            
            # 进行预测
            predictions = await self.model.predict(X_test)
            
            # 计算评估指标
            from app.utils.helpers import calculate_model_metrics
            metrics = calculate_model_metrics(y_test, predictions)
            
            evaluation_result = {
                "test_samples": len(y_test),
                "metrics": metrics,
                "predictions_stats": {
                    "mean": float(np.mean(predictions)),
                    "std": float(np.std(predictions)),
                    "min": float(np.min(predictions)),
                    "max": float(np.max(predictions))
                },
                "actual_stats": {
                    "mean": float(np.mean(y_test)),
                    "std": float(np.std(y_test)),
                    "min": float(np.min(y_test)),
                    "max": float(np.max(y_test))
                },
                "evaluated_at": datetime.now().isoformat()
            }
            
            logger.info(f"模型评估完成: {metrics}")
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"模型评估失败: {str(e)}")
            raise ModelTrainingError(f"模型评估过程中发生错误: {str(e)}")
    
    async def _split_data(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        validation_split: float
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """分割数据集"""
        try:
            if validation_split <= 0 or validation_split >= 1:
                raise ValueError("验证集比例必须在0和1之间")
            
            # 对于时间序列数据，使用顺序分割而不是随机分割
            split_index = int(len(X) * (1 - validation_split))
            
            X_train = X[:split_index]
            X_val = X[split_index:]
            y_train = y[:split_index]
            y_val = y[split_index:]
            
            logger.info(f"数据分割完成: 训练集 {X_train.shape[0]} 样本, 验证集 {X_val.shape[0]} 样本")
            
            return X_train, X_val, y_train, y_val
            
        except Exception as e:
            logger.error(f"数据分割失败: {str(e)}")
            raise ModelTrainingError(f"数据分割过程中发生错误: {str(e)}")

    async def _reconstruct_dataframe(
        self,
        original_df: pd.DataFrame,
        X: np.ndarray,
        y: np.ndarray
    ) -> pd.DataFrame:
        """重构DataFrame用于后续处理

        Args:
            original_df: 原始DataFrame
            X: 特征矩阵
            y: 目标向量

        Returns:
            重构的DataFrame
        """
        try:
            # 获取特征列名
            feature_columns = self.data_processor.feature_columns

            # 创建新的DataFrame
            reconstructed_df = pd.DataFrame(X, columns=feature_columns)
            reconstructed_df[TARGET_COLUMN] = y

            # 如果原始数据有时间列，需要对应添加（用于后续处理）
            if TIME_COLUMN in original_df.columns:
                # 根据数据长度截取对应的时间
                time_data = original_df[TIME_COLUMN].iloc[:len(X)].reset_index(drop=True)
                reconstructed_df[TIME_COLUMN] = time_data

            return reconstructed_df

        except Exception as e:
            logger.error(f"DataFrame重构失败: {str(e)}")
            raise ModelTrainingError(f"DataFrame重构过程中发生错误: {str(e)}")
    
    def get_training_history(self) -> Dict[str, Any]:
        """获取训练历史"""
        return self.training_history
    
    def get_model(self) -> Optional[PowerPredictionModel]:
        """获取训练好的模型"""
        return self.model
    
    async def load_trained_model(self, model_path: str) -> bool:
        """加载已训练的模型
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            加载是否成功
        """
        try:
            self.model = PowerPredictionModel()
            success = await self.model.load_model(model_path)
            
            if success:
                logger.info(f"已加载训练好的模型: {model_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"加载训练好的模型失败: {str(e)}")
            return False
