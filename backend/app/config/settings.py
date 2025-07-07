"""
应用配置设置
Application Configuration Settings
"""

from typing import Dict, Any, List
from pydantic import Field
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    project_name: str = "电力需求预测系统"
    app_name: str = "电力需求预测系统"
    version: str = "1.0.0"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API配置
    api_prefix: str = "/api/v1"
    allowed_hosts: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_HOSTS"
    )
    
    # 数据配置
    data_file_path: str = Field(
        default="data/temp_usage_data.csv",
        env="DATA_FILE_PATH"
    )
    model_save_path: str = Field(
        default="data/models/",
        env="MODEL_SAVE_PATH"
    )
    
    # 机器学习配置
    xgboost_params: Dict[str, Any] = {
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1,
        "random_state": 42,
        "objective": "reg:squarederror"
    }
    
    # 预测配置
    target_date: str = "2022-06-30"
    training_weeks: int = 3  # 前3周数据用于训练
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # 安全配置
    api_rate_limit: str = Field(default="100/minute", env="API_RATE_LIMIT")
    max_file_size: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB

    # AI Agent配置
    ai_agent_enabled: bool = Field(default=True, env="AI_AGENT_ENABLED")
    ai_agent_max_concurrent: int = Field(default=5, env="AI_AGENT_MAX_CONCURRENT")
    ai_agent_timeout: int = Field(default=600, env="AI_AGENT_TIMEOUT")  # 10分钟
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    ai_agent_gemini_api_key: str = Field(default="", env="AI_AGENT_GEMINI_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()
