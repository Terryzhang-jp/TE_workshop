"""
辅助函数
Helper Functions
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

from .constants import TARGET_DATE, TRAINING_START_DATE, TRAINING_END_DATE
from .exceptions import DataValidationError, FileProcessingError


def validate_file_path(file_path: str) -> bool:
    """验证文件路径是否存在"""
    if not os.path.exists(file_path):
        raise FileProcessingError(f"文件不存在: {file_path}")
    return True


def validate_date_format(date_str: str) -> datetime:
    """验证并转换日期格式"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise DataValidationError(f"日期格式无效: {date_str}，应为 YYYY-MM-DD 格式")


def calculate_date_range(target_date: str, weeks_before: int = 3) -> Tuple[datetime, datetime]:
    """计算训练数据的日期范围"""
    target_dt = validate_date_format(target_date)
    start_dt = target_dt - timedelta(weeks=weeks_before)
    end_dt = target_dt - timedelta(days=1)  # 不包含目标日期
    return start_dt, end_dt


def extract_time_features(df: pd.DataFrame, time_column: str = "time") -> pd.DataFrame:
    """提取时间特征"""
    df = df.copy()
    
    # 确保时间列是datetime类型
    if not pd.api.types.is_datetime64_any_dtype(df[time_column]):
        df[time_column] = pd.to_datetime(df[time_column])
    
    # 提取特征
    df['hour'] = df[time_column].dt.hour
    df['day_of_week'] = df[time_column].dt.dayofweek
    df['week_of_month'] = ((df[time_column].dt.day - 1) // 7) + 1
    
    return df


def validate_data_completeness(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """验证数据完整性"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise DataValidationError(f"缺少必需的列: {missing_columns}")
    
    # 检查缺失值
    missing_data = df[required_columns].isnull().sum()
    if missing_data.any():
        missing_info = missing_data[missing_data > 0].to_dict()
        raise DataValidationError(f"数据存在缺失值: {missing_info}")
    
    return True


def calculate_confidence_interval(predictions: np.ndarray, confidence: float = 0.95) -> List[Tuple[float, float]]:
    """计算预测的置信区间"""
    # 简化的置信区间计算，实际应用中可能需要更复杂的方法
    std_error = np.std(predictions) * 0.1  # 假设标准误差
    margin = std_error * 1.96  # 95%置信区间
    
    intervals = []
    for pred in predictions:
        lower = max(0, pred - margin)  # 电力使用量不能为负
        upper = pred + margin
        intervals.append((lower, upper))
    
    return intervals


def format_prediction_results(
    predictions: np.ndarray, 
    hours: List[int],
    original_predictions: Optional[np.ndarray] = None
) -> List[Dict[str, Any]]:
    """格式化预测结果"""
    confidence_intervals = calculate_confidence_interval(predictions)
    
    results = []
    for i, (hour, pred) in enumerate(zip(hours, predictions)):
        result = {
            "hour": hour,
            "predicted_usage": float(pred),
            "confidence_interval": confidence_intervals[i],
            "original_prediction": float(original_predictions[i]) if original_predictions is not None else None
        }
        results.append(result)
    
    return results


def ensure_directory_exists(directory_path: str) -> None:
    """确保目录存在，如果不存在则创建"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def get_file_size(file_path: str) -> int:
    """获取文件大小（字节）"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    import re
    # 移除或替换不安全字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 限制文件名长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    return filename


def calculate_model_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """计算模型评估指标"""
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    # 计算MAPE（平均绝对百分比误差）
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2_score": float(r2),
        "mape": float(mape)
    }


def generate_timestamp_string() -> str:
    """生成时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def convert_numpy_types(obj: Any) -> Any:
    """转换numpy类型为Python原生类型"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj
