"""
数据加载器
Data Loader
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path
import logging

from app.config import settings
from app.utils.exceptions import DataLoadError, FileProcessingError
from app.utils.helpers import validate_file_path, validate_date_format, calculate_date_range
from app.utils.constants import TIME_COLUMN, TEMPERATURE_COLUMN, TARGET_COLUMN

logger = logging.getLogger("power_prediction")


class DataLoader:
    """数据加载器类"""
    
    def __init__(self, data_file_path: Optional[str] = None):
        """初始化数据加载器
        
        Args:
            data_file_path: 数据文件路径，如果为None则使用配置中的路径
        """
        self.data_file_path = data_file_path or settings.data_file_path
        self._raw_data: Optional[pd.DataFrame] = None
        
    async def load_raw_data(self) -> pd.DataFrame:
        """加载原始数据"""
        try:
            logger.info(f"开始加载数据文件: {self.data_file_path}")
            
            # 验证文件路径
            validate_file_path(self.data_file_path)
            
            # 读取CSV文件
            df = pd.read_csv(self.data_file_path)
            
            # 基本数据验证
            if df.empty:
                raise DataLoadError("数据文件为空")
            
            # 检查必需的列
            required_columns = [TIME_COLUMN, TEMPERATURE_COLUMN, TARGET_COLUMN]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise DataLoadError(f"数据文件缺少必需的列: {missing_columns}")
            
            # 转换时间列
            df[TIME_COLUMN] = pd.to_datetime(df[TIME_COLUMN])
            
            # 排序数据
            df = df.sort_values(TIME_COLUMN).reset_index(drop=True)
            
            self._raw_data = df
            
            logger.info(f"数据加载成功，共 {len(df)} 行数据")
            logger.info(f"数据时间范围: {df[TIME_COLUMN].min()} 到 {df[TIME_COLUMN].max()}")
            
            return df
            
        except Exception as e:
            logger.error(f"数据加载失败: {str(e)}")
            if isinstance(e, (DataLoadError, FileProcessingError)):
                raise
            else:
                raise DataLoadError(f"数据加载过程中发生错误: {str(e)}")
    
    async def load_training_data(
        self, 
        target_date: Optional[str] = None,
        weeks_before: int = 3
    ) -> pd.DataFrame:
        """加载训练数据
        
        Args:
            target_date: 目标预测日期，格式为 YYYY-MM-DD
            weeks_before: 使用目标日期前几周的数据进行训练
            
        Returns:
            训练数据DataFrame
        """
        try:
            # 如果原始数据未加载，先加载
            if self._raw_data is None:
                await self.load_raw_data()
            
            # 使用配置中的目标日期或传入的日期
            target_date = target_date or settings.target_date
            
            # 计算训练数据的日期范围
            start_date, end_date = calculate_date_range(target_date, weeks_before)
            
            logger.info(f"加载训练数据，日期范围: {start_date.date()} 到 {end_date.date()}")
            
            # 筛选训练数据
            mask = (
                (self._raw_data[TIME_COLUMN] >= start_date) & 
                (self._raw_data[TIME_COLUMN] <= end_date)
            )
            training_data = self._raw_data[mask].copy()
            
            if training_data.empty:
                raise DataLoadError(f"指定日期范围内没有找到训练数据: {start_date.date()} 到 {end_date.date()}")
            
            logger.info(f"训练数据加载成功，共 {len(training_data)} 行数据")
            
            return training_data
            
        except Exception as e:
            logger.error(f"训练数据加载失败: {str(e)}")
            if isinstance(e, DataLoadError):
                raise
            else:
                raise DataLoadError(f"训练数据加载过程中发生错误: {str(e)}")
    
    async def load_historical_data(
        self, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """加载指定日期范围的历史数据
        
        Args:
            start_date: 开始日期，格式为 YYYY-MM-DD
            end_date: 结束日期，格式为 YYYY-MM-DD
            
        Returns:
            历史数据DataFrame
        """
        try:
            # 如果原始数据未加载，先加载
            if self._raw_data is None:
                await self.load_raw_data()
            
            # 验证日期格式
            start_dt = validate_date_format(start_date)
            end_dt = validate_date_format(end_date)
            
            if start_dt > end_dt:
                raise DataLoadError("开始日期不能晚于结束日期")
            
            logger.info(f"加载历史数据，日期范围: {start_date} 到 {end_date}")
            
            # 筛选历史数据
            mask = (
                (self._raw_data[TIME_COLUMN] >= start_dt) & 
                (self._raw_data[TIME_COLUMN] <= end_dt)
            )
            historical_data = self._raw_data[mask].copy()
            
            if historical_data.empty:
                raise DataLoadError(f"指定日期范围内没有找到历史数据: {start_date} 到 {end_date}")
            
            logger.info(f"历史数据加载成功，共 {len(historical_data)} 行数据")
            
            return historical_data
            
        except Exception as e:
            logger.error(f"历史数据加载失败: {str(e)}")
            if isinstance(e, DataLoadError):
                raise
            else:
                raise DataLoadError(f"历史数据加载过程中发生错误: {str(e)}")
    
    def get_data_info(self) -> dict:
        """获取数据基本信息"""
        if self._raw_data is None:
            return {"status": "未加载数据"}
        
        return {
            "total_rows": len(self._raw_data),
            "columns": list(self._raw_data.columns),
            "date_range": {
                "start": self._raw_data[TIME_COLUMN].min().isoformat(),
                "end": self._raw_data[TIME_COLUMN].max().isoformat()
            },
            "missing_values": self._raw_data.isnull().sum().to_dict(),
            "data_types": self._raw_data.dtypes.astype(str).to_dict()
        }
    
    def is_data_loaded(self) -> bool:
        """检查数据是否已加载"""
        return self._raw_data is not None and not self._raw_data.empty
