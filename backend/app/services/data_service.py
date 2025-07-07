"""
数据服务
Data Service
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import asyncio

from app.core.data.loader import DataLoader
from app.core.data.processor import DataProcessor
from app.core.data.validator import DataValidator
from app.models.schemas import HistoricalDataPoint, ContextInfo
from app.utils.exceptions import DataLoadError, DataValidationError
from app.utils.constants import CONTEXT_INFO_DATA, SUCCESS_MESSAGES, ERROR_MESSAGES
from app.utils.helpers import convert_numpy_types
from app.config import settings

logger = logging.getLogger("power_prediction")


class DataService:
    """数据服务类"""
    
    def __init__(self):
        """初始化数据服务"""
        self.data_loader = DataLoader()
        self.data_processor = DataProcessor()
        self.data_validator = DataValidator()
        self._cache: Dict[str, Any] = {}
        
    async def get_historical_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_features: bool = True
    ) -> Dict[str, Any]:
        """获取历史数据
        
        Args:
            start_date: 开始日期，格式为 YYYY-MM-DD
            end_date: 结束日期，格式为 YYYY-MM-DD
            include_features: 是否包含特征工程后的数据
            
        Returns:
            历史数据响应
        """
        try:
            logger.info(f"获取历史数据: {start_date} 到 {end_date}")
            
            # 使用默认日期范围如果未提供
            if start_date is None or end_date is None:
                start_date = settings.training_start_date if start_date is None else start_date
                end_date = settings.training_end_date if end_date is None else end_date
            
            # 检查缓存
            cache_key = f"historical_data_{start_date}_{end_date}_{include_features}"
            if cache_key in self._cache:
                logger.info("从缓存返回历史数据")
                return self._cache[cache_key]
            
            # 加载历史数据
            historical_df = await self.data_loader.load_historical_data(start_date, end_date)
            
            # 验证数据
            validation_result = await self.data_validator.validate_raw_data(historical_df)
            if not validation_result["is_valid"]:
                raise DataValidationError(f"历史数据验证失败: {validation_result['errors']}")
            
            # 特征工程（如果需要）
            if include_features:
                historical_df = await self.data_processor._extract_features(historical_df)
            
            # 转换为数据模型
            data_points = await self._convert_to_data_points(historical_df)
            
            # 计算统计信息
            stats = await self._calculate_data_statistics(historical_df)
            
            result = {
                "historical_data": data_points,
                "total_count": len(data_points),
                "date_range": (
                    historical_df['time'].min().isoformat(),
                    historical_df['time'].max().isoformat()
                ),
                "statistics": stats,
                "validation_result": validation_result,
                "data_quality": await self._assess_data_quality(historical_df),
                "retrieved_at": datetime.now().isoformat()
            }
            
            # 缓存结果
            self._cache[cache_key] = result
            
            logger.info(f"历史数据获取成功，共 {len(data_points)} 条记录")
            
            return convert_numpy_types(result)
            
        except Exception as e:
            logger.error(f"获取历史数据失败: {str(e)}")
            if isinstance(e, (DataLoadError, DataValidationError)):
                raise
            else:
                raise DataLoadError(f"获取历史数据过程中发生错误: {str(e)}")
    
    async def get_context_info(self, date_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """获取情景信息
        
        Args:
            date_range: 日期范围，格式为 (start_date, end_date)
            
        Returns:
            情景信息响应
        """
        try:
            logger.info("获取情景信息")
            
            # 过滤日期范围内的情景信息
            context_data = CONTEXT_INFO_DATA.copy()
            
            if date_range:
                start_date, end_date = date_range
                filtered_data = []
                
                for item in context_data:
                    item_date = item["date"]
                    if start_date <= item_date <= end_date:
                        filtered_data.append(item)
                
                context_data = filtered_data
            
            # 转换为数据模型
            context_info_list = []
            for item in context_data:
                context_info = ContextInfo(
                    date=item["date"],
                    day_of_week=item["day_of_week"],
                    temperature=item["temperature"],
                    demand_estimate=item["demand_estimate"],
                    increase_percentage=item["increase_percentage"],
                    reserve_rate=item.get("reserve_rate"),
                    special_notes=item["special_notes"]
                )
                context_info_list.append(context_info)
            
            result = {
                "context_data": [info.dict() for info in context_info_list],
                "date_range": (
                    min(item["date"] for item in context_data) if context_data else None,
                    max(item["date"] for item in context_data) if context_data else None
                ),
                "total_count": len(context_info_list),
                "retrieved_at": datetime.now().isoformat()
            }
            
            logger.info(f"情景信息获取成功，共 {len(context_info_list)} 条记录")
            
            return result
            
        except Exception as e:
            logger.error(f"获取情景信息失败: {str(e)}")
            raise DataLoadError(f"获取情景信息过程中发生错误: {str(e)}")
    
    async def validate_data_file(self, file_path: str) -> Dict[str, Any]:
        """验证数据文件
        
        Args:
            file_path: 数据文件路径
            
        Returns:
            验证结果
        """
        try:
            logger.info(f"验证数据文件: {file_path}")
            
            # 创建临时数据加载器
            temp_loader = DataLoader(file_path)
            
            # 加载数据
            data = await temp_loader.load_raw_data()
            
            # 验证数据
            validation_result = await self.data_validator.validate_raw_data(data)
            
            # 获取数据信息
            data_info = temp_loader.get_data_info()
            
            result = {
                "file_path": file_path,
                "validation_result": validation_result,
                "data_info": data_info,
                "recommendations": await self._generate_data_recommendations(validation_result),
                "validated_at": datetime.now().isoformat()
            }
            
            logger.info(f"数据文件验证完成: {'通过' if validation_result['is_valid'] else '失败'}")
            
            return result
            
        except Exception as e:
            logger.error(f"数据文件验证失败: {str(e)}")
            raise DataValidationError(f"数据文件验证过程中发生错误: {str(e)}")
    
    async def get_data_summary(self) -> Dict[str, Any]:
        """获取数据摘要
        
        Returns:
            数据摘要信息
        """
        try:
            logger.info("获取数据摘要")
            
            # 检查缓存
            cache_key = "data_summary"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # 获取数据加载器信息
            data_info = self.data_loader.get_data_info()
            
            # 如果数据未加载，先加载
            if not self.data_loader.is_data_loaded():
                await self.data_loader.load_raw_data()
                data_info = self.data_loader.get_data_info()
            
            # 获取数据处理器信息
            processor_info = self.data_processor.get_feature_info()
            
            # 计算数据覆盖范围
            coverage_info = await self._calculate_data_coverage()
            
            result = {
                "data_info": data_info,
                "processor_info": processor_info,
                "coverage_info": coverage_info,
                "system_status": {
                    "data_loaded": self.data_loader.is_data_loaded(),
                    "processor_fitted": self.data_processor.is_fitted,
                    "cache_size": len(self._cache)
                },
                "generated_at": datetime.now().isoformat()
            }
            
            # 缓存结果
            self._cache[cache_key] = result
            
            logger.info("数据摘要获取成功")
            
            return result
            
        except Exception as e:
            logger.error(f"获取数据摘要失败: {str(e)}")
            raise DataLoadError(f"获取数据摘要过程中发生错误: {str(e)}")
    
    async def export_data(
        self,
        data_type: str = "historical",
        format: str = "csv",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """导出数据
        
        Args:
            data_type: 数据类型 ("historical", "context")
            format: 导出格式 ("csv", "json")
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            导出结果信息
        """
        try:
            logger.info(f"导出数据: 类型={data_type}, 格式={format}")
            
            if data_type == "historical":
                data_result = await self.get_historical_data(start_date, end_date)
                data_to_export = data_result["historical_data"]
            elif data_type == "context":
                data_result = await self.get_context_info((start_date, end_date) if start_date and end_date else None)
                data_to_export = data_result["context_data"]
            else:
                raise DataValidationError(f"不支持的数据类型: {data_type}")
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{data_type}_data_{timestamp}.{format}"
            
            # 导出数据（这里简化处理，实际应用中可能需要写入文件系统）
            export_info = {
                "filename": filename,
                "format": format,
                "data_type": data_type,
                "record_count": len(data_to_export),
                "date_range": (start_date, end_date) if start_date and end_date else None,
                "exported_at": datetime.now().isoformat(),
                "download_url": f"/api/v1/data/download/{filename}",  # 假设的下载URL
                "file_size": len(str(data_to_export))  # 简化的文件大小计算
            }
            
            logger.info(f"数据导出成功: {filename}")
            
            return export_info
            
        except Exception as e:
            logger.error(f"数据导出失败: {str(e)}")
            raise DataLoadError(f"数据导出过程中发生错误: {str(e)}")
    
    async def clear_cache(self) -> Dict[str, Any]:
        """清除缓存
        
        Returns:
            清除结果
        """
        try:
            cache_size = len(self._cache)
            self._cache.clear()
            
            result = {
                "cleared_items": cache_size,
                "cleared_at": datetime.now().isoformat(),
                "message": f"已清除 {cache_size} 个缓存项"
            }
            
            logger.info(f"缓存已清除，共 {cache_size} 个项目")
            
            return result
            
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            raise DataLoadError(f"清除缓存过程中发生错误: {str(e)}")
    
    async def _convert_to_data_points(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """转换DataFrame为数据点列表"""
        data_points = []
        
        for _, row in df.iterrows():
            data_point = {
                "timestamp": row['time'].isoformat(),
                "temperature": float(row['temp']),
                "usage": float(row['usage']),
                "hour": int(row.get('hour', row['time'].hour)),
                "day_of_week": int(row.get('day_of_week', row['time'].dayofweek)),
                "week_of_month": int(row.get('week_of_month', ((row['time'].day - 1) // 7) + 1))
            }
            data_points.append(data_point)
        
        return data_points
    
    async def _calculate_data_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算数据统计信息"""
        numeric_columns = ['temp', 'usage']
        stats = {}
        
        for col in numeric_columns:
            if col in df.columns:
                stats[col] = {
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "median": float(df[col].median()),
                    "q25": float(df[col].quantile(0.25)),
                    "q75": float(df[col].quantile(0.75))
                }
        
        return stats
    
    async def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """评估数据质量"""
        quality_score = 100.0
        issues = []
        
        # 检查缺失值
        missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_percentage > 0:
            quality_score -= missing_percentage * 10
            issues.append(f"存在 {missing_percentage:.1f}% 的缺失值")
        
        # 检查重复值
        duplicate_percentage = (df.duplicated().sum() / len(df)) * 100
        if duplicate_percentage > 0:
            quality_score -= duplicate_percentage * 5
            issues.append(f"存在 {duplicate_percentage:.1f}% 的重复值")
        
        # 检查数据连续性
        if 'time' in df.columns:
            time_gaps = df['time'].diff().dropna()
            expected_interval = time_gaps.mode().iloc[0] if len(time_gaps.mode()) > 0 else pd.Timedelta(hours=1)
            irregular_intervals = (time_gaps != expected_interval).sum()
            
            if irregular_intervals > 0:
                quality_score -= (irregular_intervals / len(time_gaps)) * 20
                issues.append(f"存在 {irregular_intervals} 个不规则时间间隔")
        
        quality_score = max(0, quality_score)
        
        return {
            "quality_score": quality_score,
            "quality_level": "excellent" if quality_score >= 90 else "good" if quality_score >= 70 else "fair" if quality_score >= 50 else "poor",
            "issues": issues,
            "recommendations": await self._generate_quality_recommendations(quality_score, issues)
        }
    
    async def _generate_data_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """生成数据建议"""
        recommendations = []
        
        if not validation_result["is_valid"]:
            recommendations.append("数据验证失败，请检查并修复数据问题")
        
        if validation_result.get("warnings"):
            recommendations.append("存在数据警告，建议进行数据清洗")
        
        if len(recommendations) == 0:
            recommendations.append("数据质量良好，可以用于模型训练")
        
        return recommendations
    
    async def _generate_quality_recommendations(self, quality_score: float, issues: List[str]) -> List[str]:
        """生成质量改进建议"""
        recommendations = []
        
        if quality_score < 70:
            recommendations.append("数据质量较低，建议进行全面的数据清洗")
        
        if "缺失值" in str(issues):
            recommendations.append("处理缺失值：使用插值或删除缺失数据")
        
        if "重复值" in str(issues):
            recommendations.append("移除重复数据以提高数据质量")
        
        if "不规则时间间隔" in str(issues):
            recommendations.append("检查并修复时间序列的连续性")
        
        if len(recommendations) == 0:
            recommendations.append("数据质量优秀，无需特殊处理")
        
        return recommendations
    
    async def _calculate_data_coverage(self) -> Dict[str, Any]:
        """计算数据覆盖范围"""
        try:
            if not self.data_loader.is_data_loaded():
                return {"status": "数据未加载"}
            
            data_info = self.data_loader.get_data_info()
            
            if "date_range" in data_info:
                start_date = datetime.fromisoformat(data_info["date_range"]["start"])
                end_date = datetime.fromisoformat(data_info["date_range"]["end"])
                
                total_days = (end_date - start_date).days + 1
                expected_hours = total_days * 24
                actual_hours = data_info.get("total_rows", 0)
                
                coverage_percentage = (actual_hours / expected_hours) * 100 if expected_hours > 0 else 0
                
                return {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_days": total_days,
                    "expected_hours": expected_hours,
                    "actual_hours": actual_hours,
                    "coverage_percentage": coverage_percentage
                }
            
            return {"status": "无法计算覆盖范围"}
            
        except Exception as e:
            logger.error(f"计算数据覆盖范围失败: {str(e)}")
            return {"status": "计算失败", "error": str(e)}
