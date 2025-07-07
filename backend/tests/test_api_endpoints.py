"""
API端点集成测试
API Endpoints Integration Tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from app.main import app
from app.api.deps import get_data_service, get_prediction_service


class TestDataEndpoints:
    """数据端点测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_data_service(self):
        """模拟数据服务"""
        service = AsyncMock()
        service.get_historical_data.return_value = {
            "historical_data": [
                {"timestamp": "2024-01-01T00:00:00", "temperature": 25.0, "usage": 100.0}
            ],
            "total_count": 1,
            "statistics": {"temp": {"mean": 25.0}, "usage": {"mean": 100.0}}
        }
        service.get_context_info.return_value = {
            "context_data": [
                {"date": "2024-01-01", "temperature": 25.0, "demand_estimate": 100.0}
            ],
            "total_count": 1
        }
        service.get_data_summary.return_value = {
            "data_info": {"total_rows": 1000},
            "system_status": {"data_loaded": True}
        }
        return service
    
    def test_get_historical_data_success(self, client, mock_data_service):
        """测试成功获取历史数据"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_data_service):
            app.dependency_overrides[get_data_service] = lambda: mock_data_service
            
            response = client.get("/api/v1/data/historical?start_date=2024-01-01&end_date=2024-01-02")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert data["data"]["total_count"] == 1
            
            # 清理
            app.dependency_overrides.clear()
    
    def test_get_historical_data_with_features(self, client, mock_data_service):
        """测试获取包含特征的历史数据"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_data_service):
            app.dependency_overrides[get_data_service] = lambda: mock_data_service
            
            response = client.get("/api/v1/data/historical?include_features=true")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            app.dependency_overrides.clear()
    
    def test_get_context_info_success(self, client, mock_data_service):
        """测试成功获取情景信息"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_data_service):
            app.dependency_overrides[get_data_service] = lambda: mock_data_service
            
            response = client.get("/api/v1/data/context-info")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["total_count"] == 1
            
            app.dependency_overrides.clear()
    
    def test_validate_data_file_success(self, client, mock_data_service):
        """测试成功验证数据文件"""
        mock_data_service.validate_data_file.return_value = {
            "validation_result": {"is_valid": True},
            "recommendations": ["数据质量良好"]
        }
        
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_data_service):
            app.dependency_overrides[get_data_service] = lambda: mock_data_service
            
            response = client.post("/api/v1/data/validate", json={"file_path": "test.csv"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            app.dependency_overrides.clear()
    
    def test_get_data_summary_success(self, client, mock_data_service):
        """测试成功获取数据摘要"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_data_service):
            app.dependency_overrides[get_data_service] = lambda: mock_data_service
            
            response = client.get("/api/v1/data/summary")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data_info" in data["data"]
            
            app.dependency_overrides.clear()
    
    def test_export_data_success(self, client, mock_data_service):
        """测试成功导出数据"""
        mock_data_service.export_data.return_value = {
            "filename": "historical_data_20240101.csv",
            "record_count": 100,
            "format": "csv"
        }
        
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_data_service):
            app.dependency_overrides[get_data_service] = lambda: mock_data_service
            
            response = client.get("/api/v1/data/export?data_type=historical&format=csv")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["format"] == "csv"
            
            app.dependency_overrides.clear()
    
    def test_clear_data_cache_success(self, client, mock_data_service):
        """测试成功清除数据缓存"""
        mock_data_service.clear_cache.return_value = {
            "cleared_items": 5,
            "message": "已清除 5 个缓存项"
        }
        
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_data_service):
            app.dependency_overrides[get_data_service] = lambda: mock_data_service
            
            response = client.delete("/api/v1/data/cache")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["cleared_items"] == 5
            
            app.dependency_overrides.clear()
    
    def test_check_data_health_success(self, client, mock_data_service):
        """测试数据服务健康检查"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_data_service):
            app.dependency_overrides[get_data_service] = lambda: mock_data_service
            
            response = client.get("/api/v1/data/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["status"] == "healthy"
            
            app.dependency_overrides.clear()


class TestPredictionEndpoints:
    """预测端点测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_prediction_service(self):
        """模拟预测服务"""
        service = AsyncMock()
        service.train_model.return_value = {
            "training_completed": True,
            "target_date": "2024-01-01",
            "training_time": 120.5
        }
        service.get_prediction.return_value = {
            "predictions": [
                {"hour": i, "predicted_usage": 100 + i * 5}
                for i in range(24)
            ],
            "model_metrics": {"mae": 10.5, "rmse": 15.2}
        }
        service.get_hourly_prediction.return_value = {
            "datetime": "2024-01-01T10:00:00",
            "predicted_usage": 105.5
        }
        service.batch_predict.return_value = {
            "results": [{"predicted_usage": 105.5}],
            "summary": {"total_requests": 1, "successful_predictions": 1}
        }
        service.get_model_metrics.return_value = {
            "model_type": "XGBoost",
            "training_metrics": {"mae": 10.5}
        }
        return service
    
    def test_train_model_success(self, client, mock_prediction_service):
        """测试成功训练模型"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_prediction_service):
            app.dependency_overrides[get_prediction_service] = lambda: mock_prediction_service
            
            payload = {
                "target_date": "2024-01-01",
                "weeks_before": 3,
                "validation_split": 0.2
            }
            
            response = client.post("/api/v1/prediction/train", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["training_completed"] is True
            
            app.dependency_overrides.clear()
    
    def test_get_prediction_success(self, client, mock_prediction_service):
        """测试成功获取预测"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_prediction_service):
            app.dependency_overrides[get_prediction_service] = lambda: mock_prediction_service
            
            response = client.get("/api/v1/prediction/?target_date=2024-01-01")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]["predictions"]) == 24
            
            app.dependency_overrides.clear()
    
    def test_get_prediction_with_temperature(self, client, mock_prediction_service):
        """测试带温度预报的预测"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_prediction_service):
            app.dependency_overrides[get_prediction_service] = lambda: mock_prediction_service
            
            temperature_forecast = ",".join([str(25.0)] * 24)
            response = client.get(f"/api/v1/prediction/?temperature_forecast={temperature_forecast}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            app.dependency_overrides.clear()
    
    def test_get_hourly_prediction_success(self, client, mock_prediction_service):
        """测试成功获取单小时预测"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_prediction_service):
            app.dependency_overrides[get_prediction_service] = lambda: mock_prediction_service
            
            response = client.get("/api/v1/prediction/hourly?target_datetime=2024-01-01T10:00:00&temperature=25.0")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["predicted_usage"] == 105.5
            
            app.dependency_overrides.clear()
    
    def test_batch_predict_success(self, client, mock_prediction_service):
        """测试成功批量预测"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_prediction_service):
            app.dependency_overrides[get_prediction_service] = lambda: mock_prediction_service
            
            payload = [
                {"datetime": "2024-01-01T10:00:00", "temperature": 25.0},
                {"datetime": "2024-01-01T11:00:00", "temperature": 26.0}
            ]
            
            response = client.post("/api/v1/prediction/batch", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["summary"]["total_requests"] == 1
            
            app.dependency_overrides.clear()
    
    def test_get_model_metrics_success(self, client, mock_prediction_service):
        """测试成功获取模型指标"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_prediction_service):
            app.dependency_overrides[get_prediction_service] = lambda: mock_prediction_service
            
            response = client.get("/api/v1/prediction/metrics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["model_type"] == "XGBoost"
            
            app.dependency_overrides.clear()
    
    def test_load_model_success(self, client, mock_prediction_service):
        """测试成功加载模型"""
        mock_prediction_service.load_model.return_value = {
            "load_success": True,
            "model_path": "/path/to/model.joblib"
        }
        
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_prediction_service):
            app.dependency_overrides[get_prediction_service] = lambda: mock_prediction_service
            
            response = client.post("/api/v1/prediction/load-model", json="/path/to/model.joblib")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["load_success"] is True
            
            app.dependency_overrides.clear()
    
    def test_evaluate_model_success(self, client, mock_prediction_service):
        """测试成功评估模型"""
        mock_prediction_service.evaluate_model.return_value = {
            "test_samples": 200,
            "metrics": {"mae": 12.5, "rmse": 18.2}
        }
        
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_prediction_service):
            app.dependency_overrides[get_prediction_service] = lambda: mock_prediction_service
            
            response = client.post("/api/v1/prediction/evaluate", json=None)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["test_samples"] == 200
            
            app.dependency_overrides.clear()
    
    def test_clear_prediction_cache_success(self, client, mock_prediction_service):
        """测试成功清除预测缓存"""
        mock_prediction_service.clear_cache.return_value = {
            "cleared_model_cache": 1,
            "cleared_prediction_cache": 2,
            "total_cleared": 3
        }
        
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_prediction_service):
            app.dependency_overrides[get_prediction_service] = lambda: mock_prediction_service
            
            response = client.delete("/api/v1/prediction/cache")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["total_cleared"] == 3
            
            app.dependency_overrides.clear()
    
    def test_check_prediction_health_success(self, client, mock_prediction_service):
        """测试预测服务健康检查"""
        with patch.object(app.dependency_overrides, 'get', return_value=lambda: mock_prediction_service):
            app.dependency_overrides[get_prediction_service] = lambda: mock_prediction_service
            
            response = client.get("/api/v1/prediction/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["status"] == "healthy"
            
            app.dependency_overrides.clear()


class TestApplicationEndpoints:
    """应用端点测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """测试根端点"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "电力需求预测系统" in data["message"]
    
    def test_health_check_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "power-prediction-api"
        assert "version" in data
    
    def test_invalid_endpoint(self, client):
        """测试无效端点"""
        response = client.get("/api/v1/invalid")
        
        assert response.status_code == 404
    
    def test_invalid_method(self, client):
        """测试无效HTTP方法"""
        response = client.patch("/api/v1/data/historical")
        
        assert response.status_code == 405
