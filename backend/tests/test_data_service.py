"""
数据服务测试
Data Service Tests
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.data_service import DataService
from app.utils.exceptions import DataLoadError, DataValidationError


class TestDataService:
    """数据服务测试类"""
    
    @pytest.fixture
    def data_service(self):
        """创建数据服务实例"""
        return DataService()
    
    @pytest.fixture
    def sample_data(self):
        """创建示例数据"""
        dates = pd.date_range('2024-01-01', periods=24, freq='H')
        return pd.DataFrame({
            'time': dates,
            'temp': np.random.normal(25, 5, 24),
            'usage': np.random.normal(100, 20, 24)
        })
    
    @pytest.mark.asyncio
    async def test_get_historical_data_success(self, data_service, sample_data):
        """测试成功获取历史数据"""
        # Mock数据加载器
        with patch.object(data_service.data_loader, 'load_historical_data', new_callable=AsyncMock) as mock_load:
            with patch.object(data_service.data_validator, 'validate_raw_data', new_callable=AsyncMock) as mock_validate:
                with patch.object(data_service.data_processor, '_extract_features', new_callable=AsyncMock) as mock_extract:
                    
                    # 设置mock返回值
                    mock_load.return_value = sample_data
                    mock_validate.return_value = {"is_valid": True, "errors": []}
                    mock_extract.return_value = sample_data
                    
                    # 执行测试
                    result = await data_service.get_historical_data(
                        start_date="2024-01-01",
                        end_date="2024-01-02"
                    )
                    
                    # 验证结果
                    assert result["total_count"] == 24
                    assert "historical_data" in result
                    assert "statistics" in result
                    assert "data_quality" in result
                    
                    # 验证调用
                    mock_load.assert_called_once()
                    mock_validate.assert_called_once()
                    mock_extract.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_historical_data_validation_failure(self, data_service, sample_data):
        """测试数据验证失败"""
        with patch.object(data_service.data_loader, 'load_historical_data', new_callable=AsyncMock) as mock_load:
            with patch.object(data_service.data_validator, 'validate_raw_data', new_callable=AsyncMock) as mock_validate:
                
                # 设置mock返回值
                mock_load.return_value = sample_data
                mock_validate.return_value = {"is_valid": False, "errors": ["数据格式错误"]}
                
                # 执行测试并验证异常
                with pytest.raises(DataValidationError):
                    await data_service.get_historical_data()
    
    @pytest.mark.asyncio
    async def test_get_context_info_success(self, data_service):
        """测试成功获取情景信息"""
        result = await data_service.get_context_info()
        
        # 验证结果
        assert "context_data" in result
        assert "total_count" in result
        assert isinstance(result["context_data"], list)
    
    @pytest.mark.asyncio
    async def test_get_context_info_with_date_range(self, data_service):
        """测试带日期范围的情景信息获取"""
        result = await data_service.get_context_info(("2024-01-01", "2024-01-31"))
        
        # 验证结果
        assert "context_data" in result
        assert "date_range" in result
    
    @pytest.mark.asyncio
    async def test_validate_data_file_success(self, data_service):
        """测试成功验证数据文件"""
        with patch.object(data_service.data_loader, '__init__', return_value=None):
            with patch.object(data_service, 'data_loader') as mock_loader:
                mock_temp_loader = Mock()
                mock_temp_loader.load_raw_data = AsyncMock(return_value=pd.DataFrame())
                mock_temp_loader.get_data_info.return_value = {"total_rows": 100}
                
                with patch('app.services.data_service.DataLoader', return_value=mock_temp_loader):
                    with patch.object(data_service.data_validator, 'validate_raw_data', new_callable=AsyncMock) as mock_validate:
                        
                        mock_validate.return_value = {"is_valid": True, "errors": []}
                        
                        result = await data_service.validate_data_file("test.csv")
                        
                        assert result["validation_result"]["is_valid"] is True
                        assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_get_data_summary_success(self, data_service):
        """测试成功获取数据摘要"""
        with patch.object(data_service.data_loader, 'get_data_info') as mock_info:
            with patch.object(data_service.data_loader, 'is_data_loaded', return_value=True):
                with patch.object(data_service.data_processor, 'get_feature_info') as mock_feature_info:
                    
                    mock_info.return_value = {"total_rows": 1000}
                    mock_feature_info.return_value = {"features": ["temp", "usage"]}
                    
                    result = await data_service.get_data_summary()
                    
                    assert "data_info" in result
                    assert "processor_info" in result
                    assert "system_status" in result
    
    @pytest.mark.asyncio
    async def test_export_data_historical(self, data_service):
        """测试导出历史数据"""
        with patch.object(data_service, 'get_historical_data', new_callable=AsyncMock) as mock_get_data:
            mock_get_data.return_value = {
                "historical_data": [{"timestamp": "2024-01-01T00:00:00", "usage": 100}]
            }
            
            result = await data_service.export_data(
                data_type="historical",
                format="csv"
            )
            
            assert "filename" in result
            assert "record_count" in result
            assert result["format"] == "csv"
    
    @pytest.mark.asyncio
    async def test_export_data_context(self, data_service):
        """测试导出情景数据"""
        with patch.object(data_service, 'get_context_info', new_callable=AsyncMock) as mock_get_context:
            mock_get_context.return_value = {
                "context_data": [{"date": "2024-01-01", "temperature": 25}]
            }
            
            result = await data_service.export_data(
                data_type="context",
                format="json"
            )
            
            assert "filename" in result
            assert "record_count" in result
            assert result["format"] == "json"
    
    @pytest.mark.asyncio
    async def test_export_data_invalid_type(self, data_service):
        """测试导出无效数据类型"""
        with pytest.raises(DataValidationError):
            await data_service.export_data(data_type="invalid")
    
    @pytest.mark.asyncio
    async def test_clear_cache_success(self, data_service):
        """测试成功清除缓存"""
        # 添加一些缓存项
        data_service._cache["test_key"] = "test_value"
        
        result = await data_service.clear_cache()
        
        assert result["cleared_items"] == 1
        assert len(data_service._cache) == 0
    
    def test_convert_to_data_points(self, data_service, sample_data):
        """测试转换DataFrame为数据点列表"""
        import asyncio
        
        async def run_test():
            result = await data_service._convert_to_data_points(sample_data)
            
            assert len(result) == 24
            assert all("timestamp" in point for point in result)
            assert all("temperature" in point for point in result)
            assert all("usage" in point for point in result)
        
        asyncio.run(run_test())
    
    def test_calculate_data_statistics(self, data_service, sample_data):
        """测试计算数据统计信息"""
        import asyncio
        
        async def run_test():
            result = await data_service._calculate_data_statistics(sample_data)
            
            assert "temp" in result
            assert "usage" in result
            assert "mean" in result["temp"]
            assert "std" in result["temp"]
            assert "min" in result["temp"]
            assert "max" in result["temp"]
        
        asyncio.run(run_test())
    
    def test_assess_data_quality_good(self, data_service, sample_data):
        """测试评估良好数据质量"""
        import asyncio
        
        async def run_test():
            result = await data_service._assess_data_quality(sample_data)
            
            assert "quality_score" in result
            assert "quality_level" in result
            assert "issues" in result
            assert result["quality_score"] > 90  # 应该是高质量数据
        
        asyncio.run(run_test())
    
    def test_assess_data_quality_with_missing_values(self, data_service):
        """测试评估有缺失值的数据质量"""
        import asyncio
        
        # 创建有缺失值的数据
        dates = pd.date_range('2024-01-01', periods=10, freq='H')
        data_with_missing = pd.DataFrame({
            'time': dates,
            'temp': [25, np.nan, 26, 24, np.nan, 27, 25, 26, 24, 25],
            'usage': [100, 105, np.nan, 95, 110, 98, 102, 107, 99, 101]
        })
        
        async def run_test():
            result = await data_service._assess_data_quality(data_with_missing)
            
            assert result["quality_score"] < 100  # 应该扣分
            assert len(result["issues"]) > 0  # 应该有问题报告
        
        asyncio.run(run_test())
    
    def test_generate_data_recommendations_valid(self, data_service):
        """测试生成数据建议 - 有效数据"""
        import asyncio
        
        async def run_test():
            validation_result = {"is_valid": True, "warnings": []}
            result = await data_service._generate_data_recommendations(validation_result)
            
            assert isinstance(result, list)
            assert len(result) > 0
        
        asyncio.run(run_test())
    
    def test_generate_data_recommendations_invalid(self, data_service):
        """测试生成数据建议 - 无效数据"""
        import asyncio
        
        async def run_test():
            validation_result = {"is_valid": False, "warnings": ["数据格式错误"]}
            result = await data_service._generate_data_recommendations(validation_result)
            
            assert isinstance(result, list)
            assert any("数据验证失败" in rec for rec in result)
        
        asyncio.run(run_test())
    
    def test_calculate_data_coverage_success(self, data_service):
        """测试计算数据覆盖范围"""
        import asyncio
        
        async def run_test():
            with patch.object(data_service.data_loader, 'is_data_loaded', return_value=True):
                with patch.object(data_service.data_loader, 'get_data_info') as mock_info:
                    mock_info.return_value = {
                        "date_range": {
                            "start": "2024-01-01T00:00:00",
                            "end": "2024-01-02T00:00:00"
                        },
                        "total_rows": 24
                    }
                    
                    result = await data_service._calculate_data_coverage()
                    
                    assert "start_date" in result
                    assert "end_date" in result
                    assert "coverage_percentage" in result
        
        asyncio.run(run_test())
    
    def test_calculate_data_coverage_no_data(self, data_service):
        """测试计算数据覆盖范围 - 无数据"""
        import asyncio
        
        async def run_test():
            with patch.object(data_service.data_loader, 'is_data_loaded', return_value=False):
                result = await data_service._calculate_data_coverage()
                
                assert result["status"] == "数据未加载"
        
        asyncio.run(run_test())
