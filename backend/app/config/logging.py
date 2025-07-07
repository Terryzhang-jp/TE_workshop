"""
日志配置
Logging Configuration
"""

import logging
import sys
from typing import Dict, Any
from .settings import settings


def get_logging_config() -> Dict[str, Any]:
    """获取日志配置"""
    
    if settings.log_format == "json":
        formatter_class = "pythonjsonlogger.jsonlogger.JsonFormatter"
        format_string = "%(asctime)s %(name)s %(levelname)s %(message)s"
    else:
        formatter_class = "logging.Formatter"
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": format_string,
                "class": formatter_class
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout
            }
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console"]
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        }
    }


def setup_logging():
    """设置日志配置"""
    import logging.config
    
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    # 获取应用日志器
    logger = logging.getLogger("power_prediction")
    logger.info("日志系统初始化完成", extra={
        "log_level": settings.log_level,
        "log_format": settings.log_format
    })
    
    return logger
