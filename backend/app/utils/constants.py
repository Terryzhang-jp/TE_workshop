"""
常量定义
Constants Definition
"""

from typing import Dict, Any, List

# 情景信息数据
CONTEXT_INFO_DATA: List[Dict[str, Any]] = [
    {
        "date": "2022-06-24",
        "day_of_week": "周五",
        "temperature": 32.6,
        "demand_estimate": "≈ 49 GW",
        "increase_percentage": "+ ≈ 20%",
        "reserve_rate": None,
        "special_notes": "热浪前哨，高于常年均值约 8 GW"
    },
    {
        "date": "2022-06-25",
        "day_of_week": "周六",
        "temperature": 35.4,
        "demand_estimate": "≈ 51 GW",
        "increase_percentage": "+ ≈ 25%",
        "reserve_rate": None,
        "special_notes": "首次进入\"猛暑日\""
    },
    {
        "date": "2022-06-26",
        "day_of_week": "周日",
        "temperature": 36.2,
        "demand_estimate": "≈ 52.5 GW",
        "increase_percentage": "+ ≈ 28%",
        "reserve_rate": None,
        "special_notes": "需求创当年 6 月周末纪录"
    },
    {
        "date": "2022-06-27",
        "day_of_week": "周一",
        "temperature": 35.7,
        "demand_estimate": "≈ 53.3 GW",
        "increase_percentage": "+ ≈ 30%",
        "reserve_rate": "余裕率预估跌至 3%",
        "special_notes": "政府首次连发\"需给ひっ迫注意報\""
    },
    {
        "date": "2022-06-28",
        "day_of_week": "周二",
        "temperature": 35.1,
        "demand_estimate": "≈ 54.5 GW",
        "increase_percentage": "+ ≈ 33%",
        "reserve_rate": "同上",
        "special_notes": "14 – 15 时段逼近 55 GW"
    },
    {
        "date": "2022-06-29",
        "day_of_week": "周三",
        "temperature": 35.4,
        "demand_estimate": "≈ 54.8 GW",
        "increase_percentage": "+ ≈ 33%",
        "reserve_rate": "预测裕度仅 2.6% (16:30 – 17:00)",
        "special_notes": "史上首次 6 月出现\"100% 需给率\"预警"
    }
]

# 模型评估指标键名
MODEL_METRICS_KEYS: List[str] = [
    "mae",      # 平均绝对误差
    "rmse",     # 均方根误差
    "r2_score", # R²决定系数
    "mape"      # 平均绝对百分比误差
]

# 特征名称映射
FEATURE_NAME_MAPPING: Dict[str, str] = {
    "temp": "温度",
    "hour": "小时",
    "day_of_week": "星期几",
    "week_of_month": "月中第几周"
}

# 特征名称（英文）
FEATURE_NAMES: List[str] = ["temp", "hour", "day_of_week", "week_of_month"]

# 目标列名
TARGET_COLUMN: str = "usage"

# 时间列名
TIME_COLUMN: str = "time"

# 温度列名
TEMPERATURE_COLUMN: str = "temp"

# 预测目标日期
TARGET_DATE: str = "2022-06-30"

# 训练数据日期范围
TRAINING_START_DATE: str = "2022-06-09"
TRAINING_END_DATE: str = "2022-06-29"

# 文件路径
DEFAULT_DATA_FILE: str = "temp_usage_data.csv"
DEFAULT_MODEL_PATH: str = "data/models/"

# API限制
MAX_PREDICTION_HOURS: int = 24
MIN_ADJUSTMENT_PERCENTAGE: float = 0.1
MAX_ADJUSTMENT_PERCENTAGE: float = 100.0

# 响应消息
SUCCESS_MESSAGES: Dict[str, str] = {
    "data_loaded": "数据加载成功",
    "model_trained": "模型训练成功",
    "prediction_generated": "预测生成成功",
    "explanation_generated": "可解释性分析生成成功",
    "adjustment_applied": "预测调整应用成功",
    "export_completed": "数据导出完成"
}

ERROR_MESSAGES: Dict[str, str] = {
    "data_not_found": "数据文件未找到",
    "invalid_date_format": "日期格式无效",
    "model_training_failed": "模型训练失败",
    "prediction_failed": "预测生成失败",
    "explanation_failed": "可解释性分析失败",
    "adjustment_failed": "预测调整失败",
    "export_failed": "数据导出失败"
}

# HTTP状态码
HTTP_STATUS_CODES: Dict[str, int] = {
    "OK": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "UNPROCESSABLE_ENTITY": 422,
    "INTERNAL_SERVER_ERROR": 500
}
