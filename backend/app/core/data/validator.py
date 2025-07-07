"""
数据验证器
Data Validator
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.utils.exceptions import DataValidationError
from app.utils.constants import (
    TIME_COLUMN, TEMPERATURE_COLUMN, TARGET_COLUMN,
    FEATURE_NAMES, MIN_ADJUSTMENT_PERCENTAGE, MAX_ADJUSTMENT_PERCENTAGE
)

logger = logging.getLogger("power_prediction")


class DataValidator:
    """数据验证器类"""
    
    def __init__(self):
        """初始化数据验证器"""
        self.validation_rules = {
            TEMPERATURE_COLUMN: {"min": -50, "max": 60},  # 温度范围
            TARGET_COLUMN: {"min": 0, "max": 10000},      # 电力使用量范围
            "hour": {"min": 0, "max": 23},                # 小时范围
            "day_of_week": {"min": 0, "max": 6},          # 星期范围
            "week_of_month": {"min": 1, "max": 5}         # 月中周数范围
        }
    
    async def validate_raw_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """验证原始数据
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            验证结果字典
        """
        try:
            logger.info("开始验证原始数据")
            
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "statistics": {}
            }
            
            # 基本结构验证
            structure_result = await self._validate_structure(df)
            validation_result["errors"].extend(structure_result["errors"])
            validation_result["warnings"].extend(structure_result["warnings"])
            
            # 数据质量验证
            quality_result = await self._validate_data_quality(df)
            validation_result["errors"].extend(quality_result["errors"])
            validation_result["warnings"].extend(quality_result["warnings"])
            
            # 数据范围验证
            range_result = await self._validate_data_ranges(df)
            validation_result["errors"].extend(range_result["errors"])
            validation_result["warnings"].extend(range_result["warnings"])
            
            # 时间序列验证
            if TIME_COLUMN in df.columns:
                time_result = await self._validate_time_series(df)
                validation_result["errors"].extend(time_result["errors"])
                validation_result["warnings"].extend(time_result["warnings"])
            
            # 生成统计信息
            validation_result["statistics"] = await self._generate_statistics(df)
            
            # 判断整体验证结果
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            if validation_result["is_valid"]:
                logger.info("原始数据验证通过")
            else:
                logger.error(f"原始数据验证失败，发现 {len(validation_result['errors'])} 个错误")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"数据验证过程中发生错误: {str(e)}")
            raise DataValidationError(f"数据验证失败: {str(e)}")
    
    async def validate_training_data(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """验证训练数据
        
        Args:
            X: 特征矩阵
            y: 目标向量
            
        Returns:
            验证结果字典
        """
        try:
            logger.info("开始验证训练数据")
            
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "statistics": {}
            }
            
            # 检查数据形状
            if X.shape[0] != y.shape[0]:
                validation_result["errors"].append("特征矩阵和目标向量的样本数不匹配")
            
            if X.shape[1] != len(FEATURE_NAMES):
                validation_result["errors"].append(f"特征数量不正确，期望 {len(FEATURE_NAMES)}，实际 {X.shape[1]}")
            
            # 检查数据类型
            if not np.issubdtype(X.dtype, np.number):
                validation_result["errors"].append("特征矩阵包含非数值数据")
            
            if not np.issubdtype(y.dtype, np.number):
                validation_result["errors"].append("目标向量包含非数值数据")
            
            # 检查缺失值
            if np.isnan(X).any():
                validation_result["errors"].append("特征矩阵包含缺失值")
            
            if np.isnan(y).any():
                validation_result["errors"].append("目标向量包含缺失值")
            
            # 检查无穷值
            if np.isinf(X).any():
                validation_result["errors"].append("特征矩阵包含无穷值")
            
            if np.isinf(y).any():
                validation_result["errors"].append("目标向量包含无穷值")
            
            # 检查数据范围
            if (y < 0).any():
                validation_result["warnings"].append("目标向量包含负值")
            
            # 检查数据量
            if X.shape[0] < 100:
                validation_result["warnings"].append(f"训练样本数量较少: {X.shape[0]}")
            
            # 生成统计信息
            validation_result["statistics"] = {
                "sample_count": int(X.shape[0]),
                "feature_count": int(X.shape[1]),
                "target_stats": {
                    "mean": float(np.mean(y)),
                    "std": float(np.std(y)),
                    "min": float(np.min(y)),
                    "max": float(np.max(y))
                },
                "feature_stats": {
                    "mean": np.mean(X, axis=0).tolist(),
                    "std": np.std(X, axis=0).tolist(),
                    "min": np.min(X, axis=0).tolist(),
                    "max": np.max(X, axis=0).tolist()
                }
            }
            
            # 判断整体验证结果
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            if validation_result["is_valid"]:
                logger.info("训练数据验证通过")
            else:
                logger.error(f"训练数据验证失败，发现 {len(validation_result['errors'])} 个错误")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"训练数据验证过程中发生错误: {str(e)}")
            raise DataValidationError(f"训练数据验证失败: {str(e)}")
    
    async def validate_adjustment_params(self, adjustment_data: Dict[str, Any]) -> bool:
        """验证调整参数
        
        Args:
            adjustment_data: 调整参数字典
            
        Returns:
            验证是否通过
        """
        try:
            logger.info("开始验证调整参数")
            
            adjustment_type = adjustment_data.get("adjustment_type")
            
            if adjustment_type == "global":
                return await self._validate_global_adjustment(adjustment_data)
            elif adjustment_type == "local":
                return await self._validate_local_adjustment(adjustment_data)
            else:
                raise DataValidationError(f"不支持的调整类型: {adjustment_type}")
                
        except Exception as e:
            logger.error(f"调整参数验证失败: {str(e)}")
            if isinstance(e, DataValidationError):
                raise
            else:
                raise DataValidationError(f"调整参数验证过程中发生错误: {str(e)}")
    
    async def _validate_structure(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """验证数据结构"""
        errors = []
        warnings = []
        
        # 检查必需的列
        required_columns = [TIME_COLUMN, TEMPERATURE_COLUMN, TARGET_COLUMN]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"缺少必需的列: {missing_columns}")
        
        # 检查数据行数
        if len(df) == 0:
            errors.append("数据为空")
        elif len(df) < 24:
            warnings.append(f"数据行数较少: {len(df)}")
        
        return {"errors": errors, "warnings": warnings}
    
    async def _validate_data_quality(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """验证数据质量"""
        errors = []
        warnings = []
        
        # 检查缺失值
        missing_counts = df.isnull().sum()
        for column, count in missing_counts.items():
            if count > 0:
                percentage = (count / len(df)) * 100
                if percentage > 50:
                    errors.append(f"列 {column} 缺失值过多: {percentage:.1f}%")
                elif percentage > 10:
                    warnings.append(f"列 {column} 存在缺失值: {percentage:.1f}%")
        
        # 检查重复行
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            warnings.append(f"存在 {duplicate_count} 行重复数据")
        
        return {"errors": errors, "warnings": warnings}
    
    async def _validate_data_ranges(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """验证数据范围"""
        errors = []
        warnings = []
        
        for column, rules in self.validation_rules.items():
            if column in df.columns:
                min_val = df[column].min()
                max_val = df[column].max()
                
                if min_val < rules["min"]:
                    errors.append(f"列 {column} 存在超出最小值的数据: {min_val} < {rules['min']}")
                
                if max_val > rules["max"]:
                    errors.append(f"列 {column} 存在超出最大值的数据: {max_val} > {rules['max']}")
        
        return {"errors": errors, "warnings": warnings}
    
    async def _validate_time_series(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """验证时间序列"""
        errors = []
        warnings = []
        
        if TIME_COLUMN not in df.columns:
            return {"errors": errors, "warnings": warnings}
        
        # 检查时间列格式
        try:
            time_series = pd.to_datetime(df[TIME_COLUMN])
        except Exception:
            errors.append(f"时间列 {TIME_COLUMN} 格式无效")
            return {"errors": errors, "warnings": warnings}
        
        # 检查时间顺序
        if not time_series.is_monotonic_increasing:
            warnings.append("时间序列不是单调递增的")
        
        # 检查时间间隔
        time_diffs = time_series.diff().dropna()
        if len(time_diffs) > 0:
            most_common_diff = time_diffs.mode().iloc[0] if len(time_diffs.mode()) > 0 else None
            if most_common_diff:
                irregular_intervals = (time_diffs != most_common_diff).sum()
                if irregular_intervals > 0:
                    warnings.append(f"存在 {irregular_intervals} 个不规则时间间隔")
        
        return {"errors": errors, "warnings": warnings}
    
    async def _generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """生成数据统计信息"""
        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
            "datetime_columns": len(df.select_dtypes(include=['datetime64']).columns)
        }
        
        # 数值列统计
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty:
            stats["numeric_stats"] = numeric_df.describe().to_dict()
        
        return stats
    
    async def _validate_global_adjustment(self, data: Dict[str, Any]) -> bool:
        """验证全局调整参数"""
        required_fields = ["start_hour", "end_hour", "direction", "percentage"]
        
        for field in required_fields:
            if field not in data:
                raise DataValidationError(f"全局调整缺少必需参数: {field}")
        
        start_hour = data["start_hour"]
        end_hour = data["end_hour"]
        direction = data["direction"]
        percentage = data["percentage"]
        
        # 验证小时范围
        if not (0 <= start_hour <= 23):
            raise DataValidationError(f"开始小时无效: {start_hour}")
        
        if not (0 <= end_hour <= 23):
            raise DataValidationError(f"结束小时无效: {end_hour}")
        
        if start_hour > end_hour:
            raise DataValidationError("开始小时不能大于结束小时")
        
        # 验证方向
        if direction not in ["increase", "decrease"]:
            raise DataValidationError(f"调整方向无效: {direction}")
        
        # 验证百分比
        if not (MIN_ADJUSTMENT_PERCENTAGE <= percentage <= MAX_ADJUSTMENT_PERCENTAGE):
            raise DataValidationError(
                f"调整百分比超出范围: {percentage}, "
                f"应在 {MIN_ADJUSTMENT_PERCENTAGE} 到 {MAX_ADJUSTMENT_PERCENTAGE} 之间"
            )
        
        return True
    
    async def _validate_local_adjustment(self, data: Dict[str, Any]) -> bool:
        """验证局部调整参数"""
        adjustments = data.get("adjustments", [])
        
        if not adjustments:
            raise DataValidationError("局部调整缺少调整数据")
        
        for i, adj in enumerate(adjustments):
            if "hour" not in adj:
                raise DataValidationError(f"局部调整第 {i+1} 项缺少小时参数")
            
            if "new_value" not in adj:
                raise DataValidationError(f"局部调整第 {i+1} 项缺少新值参数")
            
            hour = adj["hour"]
            new_value = adj["new_value"]
            
            if not (0 <= hour <= 23):
                raise DataValidationError(f"局部调整第 {i+1} 项小时无效: {hour}")
            
            if new_value <= 0:
                raise DataValidationError(f"局部调整第 {i+1} 项新值必须大于0: {new_value}")
        
        return True
