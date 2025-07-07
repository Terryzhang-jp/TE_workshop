"""
自定义异常定义
Custom Exception Definitions
"""

from typing import Optional, Dict, Any


class BaseAPIException(Exception):
    """API基础异常类"""
    
    def __init__(
        self, 
        message: str, 
        code: str, 
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DataValidationError(BaseAPIException):
    """数据验证错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATA_VALIDATION_ERROR",
            status_code=422,
            details=details
        )


class DataLoadError(BaseAPIException):
    """数据加载错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATA_LOAD_ERROR",
            status_code=500,
            details=details
        )


class ModelTrainingError(BaseAPIException):
    """模型训练错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="MODEL_TRAINING_ERROR",
            status_code=500,
            details=details
        )


class PredictionError(BaseAPIException):
    """预测错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="PREDICTION_ERROR",
            status_code=500,
            details=details
        )


class ModelNotFoundError(BaseAPIException):
    """模型未找到错误"""
    
    def __init__(self, message: str = "模型文件未找到或未训练"):
        super().__init__(
            message=message,
            code="MODEL_NOT_FOUND",
            status_code=404
        )


class ExplanationError(BaseAPIException):
    """可解释性分析错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EXPLANATION_ERROR",
            status_code=500,
            details=details
        )


class AdjustmentError(BaseAPIException):
    """预测调整错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="ADJUSTMENT_ERROR",
            status_code=400,
            details=details
        )


class FileProcessingError(BaseAPIException):
    """文件处理错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="FILE_PROCESSING_ERROR",
            status_code=400,
            details=details
        )


class ConfigurationError(BaseAPIException):
    """配置错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details=details
        )


class UserError(BaseAPIException):
    """用户相关错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="USER_ERROR",
            status_code=400,
            details=details
        )


class SessionError(BaseAPIException):
    """会话相关错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SESSION_ERROR",
            status_code=401,
            details=details
        )


class DataStorageError(BaseAPIException):
    """数据存储错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DATA_STORAGE_ERROR",
            status_code=500,
            details=details
        )


class ValidationError(BaseAPIException):
    """数据验证错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


class ExperimentError(BaseAPIException):
    """实验相关错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EXPERIMENT_ERROR",
            status_code=400,
            details=details
        )
