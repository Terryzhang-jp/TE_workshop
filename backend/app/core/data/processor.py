"""
数据处理器
Data Processor
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sklearn.preprocessing import StandardScaler
import logging

from app.utils.exceptions import DataValidationError
from app.utils.helpers import extract_time_features, validate_data_completeness
from app.utils.constants import (
    TIME_COLUMN, TEMPERATURE_COLUMN, TARGET_COLUMN, 
    FEATURE_NAMES, FEATURE_NAME_MAPPING
)

logger = logging.getLogger("power_prediction")


class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns: List[str] = FEATURE_NAMES.copy()
        self.is_fitted: bool = False
        
    async def process_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """处理训练数据（仅进行基础清洗和特征工程，不进行统计量相关的预处理）

        Args:
            df: 原始训练数据DataFrame

        Returns:
            特征矩阵X和目标向量y
        """
        try:
            logger.info("开始处理训练数据（基础清洗和特征工程）")

            # 仅进行基础数据清洗（不涉及统计量计算）
            df_clean = await self._basic_clean_data(df)

            # 特征工程
            df_features = await self._extract_features(df_clean)

            # 验证数据完整性
            required_columns = self.feature_columns + [TARGET_COLUMN]
            validate_data_completeness(df_features, required_columns)

            # 准备特征和目标
            X = df_features[self.feature_columns].values
            y = df_features[TARGET_COLUMN].values

            logger.info(f"训练数据基础处理完成，特征形状: {X.shape}, 目标形状: {y.shape}")

            return X, y

        except Exception as e:
            logger.error(f"训练数据处理失败: {str(e)}")
            if isinstance(e, DataValidationError):
                raise
            else:
                raise DataValidationError(f"训练数据处理过程中发生错误: {str(e)}")
    
    async def process_prediction_data(self, df: pd.DataFrame) -> np.ndarray:
        """处理预测数据
        
        Args:
            df: 原始预测数据DataFrame
            
        Returns:
            处理后的特征矩阵
        """
        try:
            logger.info("开始处理预测数据")
            
            if not self.is_fitted:
                raise DataValidationError("数据处理器尚未拟合，请先处理训练数据")
            
            # 数据清洗
            df_clean = await self._clean_data(df)
            
            # 特征工程
            df_features = await self._extract_features(df_clean)
            
            # 验证数据完整性
            validate_data_completeness(df_features, self.feature_columns)
            
            # 准备特征
            X = df_features[self.feature_columns].values
            
            # 特征缩放
            X_scaled = await self._transform_features(X)
            
            logger.info(f"预测数据处理完成，特征形状: {X_scaled.shape}")
            
            return X_scaled
            
        except Exception as e:
            logger.error(f"预测数据处理失败: {str(e)}")
            if isinstance(e, DataValidationError):
                raise
            else:
                raise DataValidationError(f"预测数据处理过程中发生错误: {str(e)}")
    
    async def create_prediction_template(self, target_date: str) -> pd.DataFrame:
        """创建预测数据模板
        
        Args:
            target_date: 目标日期，格式为 YYYY-MM-DD
            
        Returns:
            预测数据模板DataFrame
        """
        try:
            logger.info(f"创建预测数据模板，目标日期: {target_date}")
            
            # 解析目标日期
            target_dt = pd.to_datetime(target_date)
            
            # 创建24小时的时间序列
            hours = range(24)
            timestamps = [target_dt + pd.Timedelta(hours=h) for h in hours]
            
            # 创建基础DataFrame
            df = pd.DataFrame({
                TIME_COLUMN: timestamps,
                TEMPERATURE_COLUMN: 25.0,  # 默认温度，实际应用中可能需要天气预报数据
            })
            
            # 添加特征
            df_with_features = await self._extract_features(df)
            
            logger.info(f"预测数据模板创建完成，包含 {len(df_with_features)} 行数据")
            
            return df_with_features
            
        except Exception as e:
            logger.error(f"预测数据模板创建失败: {str(e)}")
            raise DataValidationError(f"预测数据模板创建过程中发生错误: {str(e)}")
    
    async def _basic_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """基础数据清洗（不涉及统计量计算，避免数据泄漏）"""
        df_clean = df.copy()

        # 移除重复行
        initial_rows = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        removed_duplicates = initial_rows - len(df_clean)
        if removed_duplicates > 0:
            logger.info(f"移除了 {removed_duplicates} 行重复数据")

        # 仅进行前向填充，不使用均值填充（避免数据泄漏）
        missing_before = df_clean.isnull().sum().sum()
        if missing_before > 0:
            logger.warning(f"发现 {missing_before} 个缺失值")

            # 对于数值列，仅使用前向填充
            numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
            df_clean[numeric_columns] = df_clean[numeric_columns].fillna(method='ffill')

            missing_after = df_clean.isnull().sum().sum()
            logger.info(f"前向填充完成，剩余缺失值: {missing_after}")

        return df_clean

    async def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """完整数据清洗（包含统计量计算，用于预测数据）"""
        df_clean = df.copy()

        # 移除重复行
        initial_rows = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        removed_duplicates = initial_rows - len(df_clean)
        if removed_duplicates > 0:
            logger.info(f"移除了 {removed_duplicates} 行重复数据")

        # 处理缺失值
        missing_before = df_clean.isnull().sum().sum()
        if missing_before > 0:
            logger.warning(f"发现 {missing_before} 个缺失值")

            # 对于数值列，使用前向填充
            numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
            df_clean[numeric_columns] = df_clean[numeric_columns].fillna(method='ffill')

            # 如果仍有缺失值，使用均值填充
            df_clean[numeric_columns] = df_clean[numeric_columns].fillna(df_clean[numeric_columns].mean())

            missing_after = df_clean.isnull().sum().sum()
            logger.info(f"缺失值处理完成，剩余缺失值: {missing_after}")

        # 异常值检测和处理
        if TARGET_COLUMN in df_clean.columns:
            df_clean = await self._handle_outliers(df_clean, TARGET_COLUMN)

        if TEMPERATURE_COLUMN in df_clean.columns:
            df_clean = await self._handle_outliers(df_clean, TEMPERATURE_COLUMN)

        return df_clean
    
    async def _handle_outliers(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """处理异常值"""
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        # 定义异常值边界
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 检测异常值
        outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
        outlier_count = outliers.sum()
        
        if outlier_count > 0:
            logger.info(f"在列 {column} 中发现 {outlier_count} 个异常值")
            
            # 使用边界值替换异常值
            df.loc[df[column] < lower_bound, column] = lower_bound
            df.loc[df[column] > upper_bound, column] = upper_bound
            
            logger.info(f"异常值已处理，使用边界值替换")
        
        return df
    
    async def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """特征工程"""
        df_features = extract_time_features(df, TIME_COLUMN)
        
        # 确保所有特征列都存在
        for feature in self.feature_columns:
            if feature not in df_features.columns:
                if feature == TEMPERATURE_COLUMN and TEMPERATURE_COLUMN in df_features.columns:
                    continue  # 温度列已存在
                else:
                    raise DataValidationError(f"缺少特征列: {feature}")
        
        return df_features
    
    async def _fit_transform_features(self, X: np.ndarray) -> np.ndarray:
        """拟合并转换特征"""
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        self.is_fitted = True
        
        logger.info("特征缩放器拟合完成")
        
        return X_scaled
    
    async def _transform_features(self, X: np.ndarray) -> np.ndarray:
        """转换特征"""
        if self.scaler is None:
            raise DataValidationError("特征缩放器尚未拟合")

        X_scaled = self.scaler.transform(X)
        return X_scaled

    async def fit_scaler_on_train_only(self, X_train: np.ndarray) -> np.ndarray:
        """仅在训练集上拟合特征缩放器（避免数据泄漏）

        Args:
            X_train: 训练集特征

        Returns:
            缩放后的训练集特征
        """
        try:
            logger.info("开始特征缩放（仅在训练集上拟合，避免数据泄漏）")

            # 仅在训练集上拟合缩放器
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            self.is_fitted = True

            logger.info("特征缩放器拟合完成（无数据泄漏）")

            return X_train_scaled

        except Exception as e:
            logger.error(f"特征缩放失败: {str(e)}")
            raise DataValidationError(f"特征缩放失败: {str(e)}")

    async def transform_validation_set(self, X_val: np.ndarray) -> np.ndarray:
        """使用训练集拟合的缩放器转换验证集

        Args:
            X_val: 验证集特征

        Returns:
            缩放后的验证集特征
        """
        try:
            if self.scaler is None:
                raise DataValidationError("特征缩放器尚未拟合，请先在训练集上拟合")

            X_val_scaled = self.scaler.transform(X_val)

            logger.info("验证集特征缩放完成")

            return X_val_scaled

        except Exception as e:
            logger.error(f"验证集特征缩放失败: {str(e)}")
            raise DataValidationError(f"验证集特征缩放失败: {str(e)}")

    async def handle_outliers_train_only(self, df_train: pd.DataFrame, df_val: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """仅基于训练集处理异常值（避免数据泄漏）

        Args:
            df_train: 训练集DataFrame
            df_val: 验证集DataFrame

        Returns:
            处理后的训练集和验证集DataFrame
        """
        try:
            logger.info("开始处理异常值（仅基于训练集统计信息）")

            # 仅基于训练集计算异常值边界
            outlier_bounds = {}

            for column in [TARGET_COLUMN, TEMPERATURE_COLUMN]:
                if column in df_train.columns:
                    # 仅使用训练集计算分位数
                    Q1 = df_train[column].quantile(0.25)
                    Q3 = df_train[column].quantile(0.75)
                    IQR = Q3 - Q1

                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    outlier_bounds[column] = {
                        'lower': lower_bound,
                        'upper': upper_bound
                    }

                    logger.info(f"列 {column} 异常值边界（基于训练集）: [{lower_bound:.2f}, {upper_bound:.2f}]")

            # 应用边界到训练集和验证集
            df_train_clean = df_train.copy()
            df_val_clean = df_val.copy()

            for column, bounds in outlier_bounds.items():
                # 处理训练集异常值
                train_outliers = (df_train_clean[column] < bounds['lower']) | (df_train_clean[column] > bounds['upper'])
                train_outlier_count = train_outliers.sum()

                if train_outlier_count > 0:
                    logger.info(f"训练集列 {column} 发现 {train_outlier_count} 个异常值")
                    df_train_clean.loc[df_train_clean[column] < bounds['lower'], column] = bounds['lower']
                    df_train_clean.loc[df_train_clean[column] > bounds['upper'], column] = bounds['upper']

                # 处理验证集异常值（使用训练集的边界）
                val_outliers = (df_val_clean[column] < bounds['lower']) | (df_val_clean[column] > bounds['upper'])
                val_outlier_count = val_outliers.sum()

                if val_outlier_count > 0:
                    logger.info(f"验证集列 {column} 发现 {val_outlier_count} 个异常值（使用训练集边界）")
                    df_val_clean.loc[df_val_clean[column] < bounds['lower'], column] = bounds['lower']
                    df_val_clean.loc[df_val_clean[column] > bounds['upper'], column] = bounds['upper']

            logger.info("异常值处理完成（无数据泄漏）")

            return df_train_clean, df_val_clean

        except Exception as e:
            logger.error(f"异常值处理失败: {str(e)}")
            raise DataValidationError(f"异常值处理失败: {str(e)}")

    async def process_train_val_data_no_leakage(
        self,
        df_train: pd.DataFrame,
        df_val: pd.DataFrame
    ) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
        """处理训练集和验证集数据（避免数据泄漏）

        Args:
            df_train: 训练集DataFrame
            df_val: 验证集DataFrame

        Returns:
            ((X_train, y_train), (X_val, y_val))
        """
        try:
            logger.info("开始处理训练集和验证集数据（避免数据泄漏）")

            # 步骤1: 基础清洗（不涉及统计量）
            df_train_clean = await self._basic_clean_data(df_train)
            df_val_clean = await self._basic_clean_data(df_val)

            # 步骤2: 处理剩余缺失值（仅基于训练集统计量）
            df_train_filled, df_val_filled = await self._fill_missing_train_only(df_train_clean, df_val_clean)

            # 步骤3: 处理异常值（仅基于训练集统计量）
            df_train_outliers, df_val_outliers = await self.handle_outliers_train_only(df_train_filled, df_val_filled)

            # 步骤4: 特征工程
            df_train_features = await self._extract_features(df_train_outliers)
            df_val_features = await self._extract_features(df_val_outliers)

            # 步骤5: 验证数据完整性
            required_columns = self.feature_columns + [TARGET_COLUMN]
            validate_data_completeness(df_train_features, required_columns)
            validate_data_completeness(df_val_features, self.feature_columns + [TARGET_COLUMN])

            # 步骤6: 准备特征和目标
            X_train = df_train_features[self.feature_columns].values
            y_train = df_train_features[TARGET_COLUMN].values
            X_val = df_val_features[self.feature_columns].values
            y_val = df_val_features[TARGET_COLUMN].values

            logger.info(f"数据处理完成（无数据泄漏）")
            logger.info(f"训练集: X{X_train.shape}, y{y_train.shape}")
            logger.info(f"验证集: X{X_val.shape}, y{y_val.shape}")

            return (X_train, y_train), (X_val, y_val)

        except Exception as e:
            logger.error(f"训练验证数据处理失败: {str(e)}")
            if isinstance(e, DataValidationError):
                raise
            else:
                raise DataValidationError(f"训练验证数据处理过程中发生错误: {str(e)}")

    async def _fill_missing_train_only(
        self,
        df_train: pd.DataFrame,
        df_val: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """仅基于训练集填充缺失值（避免数据泄漏）"""
        try:
            logger.info("开始填充缺失值（仅基于训练集统计量）")

            df_train_filled = df_train.copy()
            df_val_filled = df_val.copy()

            # 检查训练集缺失值
            train_missing = df_train_filled.isnull().sum().sum()
            val_missing = df_val_filled.isnull().sum().sum()

            if train_missing > 0 or val_missing > 0:
                logger.info(f"训练集缺失值: {train_missing}, 验证集缺失值: {val_missing}")

                # 仅基于训练集计算均值
                numeric_columns = df_train_filled.select_dtypes(include=[np.number]).columns
                train_means = df_train_filled[numeric_columns].mean()

                # 应用到训练集
                df_train_filled[numeric_columns] = df_train_filled[numeric_columns].fillna(train_means)

                # 应用到验证集（使用训练集的均值）
                df_val_filled[numeric_columns] = df_val_filled[numeric_columns].fillna(train_means)

                logger.info("缺失值填充完成（使用训练集统计量）")

            return df_train_filled, df_val_filled

        except Exception as e:
            logger.error(f"缺失值填充失败: {str(e)}")
            raise DataValidationError(f"缺失值填充失败: {str(e)}")

    def get_feature_info(self) -> Dict[str, Any]:
        """获取特征信息"""
        return {
            "feature_columns": self.feature_columns,
            "feature_mapping": FEATURE_NAME_MAPPING,
            "is_fitted": self.is_fitted,
            "scaler_info": {
                "mean": self.scaler.mean_.tolist() if self.scaler is not None else None,
                "scale": self.scaler.scale_.tolist() if self.scaler is not None else None
            } if self.is_fitted else None
        }
