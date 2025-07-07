"""
预测服务测试
Prediction Service Tests
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.prediction_service import PredictionService
from app.core.ml.model import PowerPredictionModel
from app.utils.exceptions import PredictionError, ModelTrainingError, ModelNotFoundError


class TestPredictionService:
    """预测服务测试类"""
    
    @pytest.fixture
    def prediction_service(self):
        """创建预测服务实例"""
        return PredictionService()
    
    @pytest.fixture
    def mock_model(self):
        """创建模拟模型"""
        model = Mock(spec=PowerPredictionModel)
        model.is_trained = True
        model.get_model_info.return_value = {
            "is_trained": True,
            "model_type": "XGBoost",
            "training_info": {
                "train_metrics": {"mae": 10.5, "rmse": 15.2, "r2_score": 0.85},
                "val_metrics": {"mae": 12.1, "rmse": 17.8, "r2_score": 0.82},
                "training_time": 120.5,
                "training_samples": 1000
            },
            "feature_importance": {"temp": 0.6, "hour": 0.4}
        }
        return model
    
    @pytest.mark.asyncio
    async def test_train_model_success(self, prediction_service, mock_model):
        """测试成功训练模型"""
        with patch.object(prediction_service.trainer, 'train_model', new_callable=AsyncMock) as mock_train:
            with patch.object(prediction_service.trainer, 'get_model', return_value=mock_model):
                
                mock_train.return_value = {
                    "target_date": "2024-01-01",
                    "total_training_time": 120.5,
                    "model_path": "/path/to/model.joblib",
                    "training_result": {
                        "train_metrics": {"mae": 10.5},
                        "feature_importance": {"temp": 0.6}
                    }
                }
                
                result = await prediction_service.train_model(
                    target_date="2024-01-01",
                    weeks_before=3
                )
                
                assert result["training_completed"] is True
                assert result["target_date"] == "2024-01-01"
                assert "training_metrics" in result
                assert "model_path" in result
    
    @pytest.mark.asyncio
    async def test_train_model_failure(self, prediction_service):
        """测试模型训练失败"""
        with patch.object(prediction_service.trainer, 'train_model', new_callable=AsyncMock) as mock_train:
            mock_train.side_effect = ModelTrainingError("训练失败")
            
            with pytest.raises(ModelTrainingError):
                await prediction_service.train_model()
    
    @pytest.mark.asyncio
    async def test_get_prediction_success(self, prediction_service, mock_model):
        """测试成功获取预测结果"""
        # 模拟预测结果
        mock_predictions = [
            {"hour": i, "predicted_usage": 100 + i * 5, "confidence_interval": (90, 110)}
            for i in range(24)
        ]
        
        with patch.object(prediction_service.predictor, 'is_ready', return_value=True):
            with patch.object(prediction_service.predictor, 'predict_daily_usage', new_callable=AsyncMock) as mock_predict:
                with patch.object(prediction_service.predictor, 'get_model_info', return_value=mock_model.get_model_info()):
                    with patch.object(prediction_service.predictor, 'get_prediction_metadata', return_value={}):
                        
                        mock_predict.return_value = mock_predictions
                        
                        result = await prediction_service.get_prediction(
                            target_date="2024-01-01"
                        )
                        
                        assert "predictions" in result
                        assert "model_metrics" in result
                        assert "training_info" in result
                        assert len(result["predictions"]) == 24
    
    @pytest.mark.asyncio
    async def test_get_prediction_with_temperature_forecast(self, prediction_service, mock_model):
        """测试带温度预报的预测"""
        temperature_forecast = [25.0] * 24
        mock_predictions = [
            {"hour": i, "predicted_usage": 100 + i * 5, "confidence_interval": (90, 110)}
            for i in range(24)
        ]
        
        with patch.object(prediction_service.predictor, 'is_ready', return_value=True):
            with patch.object(prediction_service.predictor, 'predict_daily_usage', new_callable=AsyncMock) as mock_predict:
                with patch.object(prediction_service.predictor, 'get_model_info', return_value=mock_model.get_model_info()):
                    with patch.object(prediction_service.predictor, 'get_prediction_metadata', return_value={}):
                        
                        mock_predict.return_value = mock_predictions
                        
                        result = await prediction_service.get_prediction(
                            target_date="2024-01-01",
                            temperature_forecast=temperature_forecast
                        )
                        
                        assert "predictions" in result
                        mock_predict.assert_called_once_with(
                            target_date="2024-01-01",
                            temperature_forecast=temperature_forecast
                        )
    
    @pytest.mark.asyncio
    async def test_get_prediction_model_not_ready(self, prediction_service):
        """测试模型未准备好时的预测"""
        with patch.object(prediction_service.predictor, 'is_ready', return_value=False):
            with patch.object(prediction_service, '_ensure_model_available', new_callable=AsyncMock) as mock_ensure:
                with patch.object(prediction_service.predictor, 'predict_daily_usage', new_callable=AsyncMock) as mock_predict:
                    with patch.object(prediction_service.predictor, 'get_model_info', return_value={}):
                        with patch.object(prediction_service.predictor, 'get_prediction_metadata', return_value={}):
                            
                            mock_predict.return_value = []
                            
                            await prediction_service.get_prediction()
                            
                            mock_ensure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_hourly_prediction_success(self, prediction_service):
        """测试成功获取单小时预测"""
        mock_result = {
            "datetime": "2024-01-01T10:00:00",
            "hour": 10,
            "predicted_usage": 105.5,
            "confidence_interval": (95.0, 115.0),
            "temperature": 25.0
        }
        
        with patch.object(prediction_service.predictor, 'is_ready', return_value=True):
            with patch.object(prediction_service.predictor, 'predict_hourly_usage', new_callable=AsyncMock) as mock_predict:
                
                mock_predict.return_value = mock_result
                
                result = await prediction_service.get_hourly_prediction(
                    target_datetime="2024-01-01T10:00:00",
                    temperature=25.0
                )
                
                assert result["predicted_usage"] == 105.5
                assert result["hour"] == 10
    
    @pytest.mark.asyncio
    async def test_batch_predict_success(self, prediction_service):
        """测试成功批量预测"""
        prediction_requests = [
            {"datetime": "2024-01-01T10:00:00", "temperature": 25.0},
            {"datetime": "2024-01-01T11:00:00", "temperature": 26.0}
        ]
        
        mock_results = [
            {"datetime": "2024-01-01T10:00:00", "predicted_usage": 105.5},
            {"datetime": "2024-01-01T11:00:00", "predicted_usage": 108.2}
        ]
        
        with patch.object(prediction_service.predictor, 'is_ready', return_value=True):
            with patch.object(prediction_service.predictor, 'batch_predict', new_callable=AsyncMock) as mock_batch:
                
                mock_batch.return_value = mock_results
                
                result = await prediction_service.batch_predict(prediction_requests)
                
                assert result["summary"]["total_requests"] == 2
                assert result["summary"]["successful_predictions"] == 2
                assert len(result["results"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_model_metrics_success(self, prediction_service, mock_model):
        """测试成功获取模型指标"""
        with patch.object(prediction_service.predictor, 'is_ready', return_value=True):
            with patch.object(prediction_service.predictor, 'get_model_info', return_value=mock_model.get_model_info()):
                
                result = await prediction_service.get_model_metrics()
                
                assert "model_type" in result
                assert "training_metrics" in result
                assert "validation_metrics" in result
                assert "feature_importance" in result
    
    @pytest.mark.asyncio
    async def test_get_model_metrics_no_model(self, prediction_service):
        """测试无模型时获取指标"""
        with patch.object(prediction_service.predictor, 'is_ready', return_value=False):
            with patch.object(prediction_service, '_ensure_model_available', new_callable=AsyncMock) as mock_ensure:
                mock_ensure.side_effect = ModelNotFoundError("无法获取可用的模型")
                
                with pytest.raises(ModelNotFoundError):
                    await prediction_service.get_model_metrics()
    
    @pytest.mark.asyncio
    async def test_load_model_success(self, prediction_service):
        """测试成功加载模型"""
        with patch.object(prediction_service.predictor, 'load_model', new_callable=AsyncMock) as mock_load:
            with patch.object(prediction_service.predictor, 'get_model_info', return_value={"is_trained": True}):
                
                mock_load.return_value = True
                
                result = await prediction_service.load_model("/path/to/model.joblib")
                
                assert result["load_success"] is True
                assert result["model_path"] == "/path/to/model.joblib"
    
    @pytest.mark.asyncio
    async def test_load_model_failure(self, prediction_service):
        """测试加载模型失败"""
        with patch.object(prediction_service.predictor, 'load_model', new_callable=AsyncMock) as mock_load:
            mock_load.return_value = False
            
            with pytest.raises(ModelNotFoundError):
                await prediction_service.load_model("/invalid/path.joblib")
    
    @pytest.mark.asyncio
    async def test_evaluate_model_success(self, prediction_service):
        """测试成功评估模型"""
        mock_evaluation = {
            "test_samples": 200,
            "metrics": {"mae": 12.5, "rmse": 18.2, "r2_score": 0.80},
            "evaluated_at": datetime.now().isoformat()
        }
        
        with patch.object(prediction_service.trainer, 'evaluate_model', new_callable=AsyncMock) as mock_evaluate:
            mock_evaluate.return_value = mock_evaluation
            
            result = await prediction_service.evaluate_model()
            
            assert result["test_samples"] == 200
            assert "metrics" in result
    
    @pytest.mark.asyncio
    async def test_clear_cache_success(self, prediction_service):
        """测试成功清除缓存"""
        # 添加一些缓存项
        prediction_service._model_cache["test_model"] = Mock()
        prediction_service._prediction_cache["test_prediction"] = {}
        
        result = await prediction_service.clear_cache()
        
        assert result["cleared_model_cache"] == 1
        assert result["cleared_prediction_cache"] == 1
        assert len(prediction_service._model_cache) == 0
        assert len(prediction_service._prediction_cache) == 0
    
    @pytest.mark.asyncio
    async def test_ensure_model_available_success(self, prediction_service, mock_model):
        """测试确保模型可用 - 成功"""
        with patch.object(prediction_service.predictor, 'is_ready', return_value=False):
            with patch.object(prediction_service, 'train_model', new_callable=AsyncMock) as mock_train:
                with patch.object(prediction_service.predictor, 'is_ready', return_value=True):
                    
                    await prediction_service._ensure_model_available()
                    
                    mock_train.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ensure_model_available_failure(self, prediction_service):
        """测试确保模型可用 - 失败"""
        with patch.object(prediction_service.predictor, 'is_ready', return_value=False):
            with patch.object(prediction_service, 'train_model', new_callable=AsyncMock):
                
                with pytest.raises(ModelNotFoundError):
                    await prediction_service._ensure_model_available()
    
    def test_format_training_result(self, prediction_service):
        """测试格式化训练结果"""
        import asyncio
        
        training_result = {
            "target_date": "2024-01-01",
            "total_training_time": 120.5,
            "model_path": "/path/to/model.joblib",
            "data_info": {"training_samples": 1000},
            "training_result": {
                "train_metrics": {"mae": 10.5},
                "val_metrics": {"mae": 12.1},
                "feature_importance": {"temp": 0.6}
            },
            "completed_at": "2024-01-01T12:00:00"
        }
        
        async def run_test():
            result = await prediction_service._format_training_result(training_result)
            
            assert result["training_completed"] is True
            assert result["target_date"] == "2024-01-01"
            assert result["training_time"] == 120.5
            assert "training_metrics" in result
            assert "validation_metrics" in result
        
        asyncio.run(run_test())
    
    def test_extract_model_metrics(self, prediction_service, mock_model):
        """测试提取模型指标"""
        import asyncio
        
        async def run_test():
            model_info = mock_model.get_model_info()
            result = await prediction_service._extract_model_metrics(model_info)
            
            assert "mae" in result
            assert "rmse" in result
            assert "r2_score" in result
            assert result["mae"] == 10.5
        
        asyncio.run(run_test())
    
    def test_extract_training_info(self, prediction_service, mock_model):
        """测试提取训练信息"""
        import asyncio
        
        async def run_test():
            model_info = mock_model.get_model_info()
            result = await prediction_service._extract_training_info(model_info)
            
            assert "training_samples" in result
            assert "model_type" in result
            assert "training_time" in result
            assert result["training_samples"] == 1000
            assert result["model_type"] == "XGBoost"
        
        asyncio.run(run_test())
