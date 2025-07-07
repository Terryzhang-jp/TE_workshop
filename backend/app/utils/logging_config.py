"""
日志配置
Logging Configuration
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from app.config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """设置日志配置
    
    Args:
        log_level: 日志级别，如果为None则使用配置中的级别
    """
    
    # 确定日志级别
    level = log_level or settings.log_level
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    numeric_level = log_level_map.get(level.upper(), logging.INFO)
    
    # 创建日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（如果配置了日志文件路径）
    if hasattr(settings, 'log_file_path') and settings.log_file_path:
        log_file = Path(settings.log_file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 配置特定的日志器
    power_logger = logging.getLogger("power_prediction")
    power_logger.setLevel(numeric_level)
    
    # 禁用一些第三方库的详细日志
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    power_logger.info(f"日志系统初始化完成，级别: {level}")


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    return logging.getLogger(name)
