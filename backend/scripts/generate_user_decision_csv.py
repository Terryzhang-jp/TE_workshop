#!/usr/bin/env python3
"""
用户决策数据CSV生成脚本

为每个用户生成包含所有决策和24小时预测数据的CSV文件
"""

import os
import json
import csv
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserDecisionCSVGenerator:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.experiment_results_dir = self.data_dir / "experiment_results"
        self.user_experiments_dir = self.data_dir / "user_experiments"
        self.csv_output_dir = self.data_dir / "user_decision_csv"
        
        # 创建输出目录
        self.csv_output_dir.mkdir(exist_ok=True)
        
    def load_experiment_data(self, file_path: Path) -> Dict[str, Any]:
        """加载实验数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}
    
    def extract_decision_data(self, experiment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取决策数据，包含24小时预测数据"""
        decisions_data = []
        
        user_id = experiment_data.get('user_id', 'unknown')
        username = experiment_data.get('username', 'unknown')
        session_id = experiment_data.get('session_id', 'unknown')
        start_time = experiment_data.get('start_time', '')
        
        decisions = experiment_data.get('decisions', [])
        
        for decision in decisions:
            decision_id = decision.get('id', '')
            decision_label = decision.get('label', '')
            decision_reason = decision.get('reason', '')
            decision_status = decision.get('status', '')
            created_at = decision.get('created_at', '')
            completed_at = decision.get('completed_at', '')
            
            # 获取预测数据（如果存在）
            prediction_data = decision.get('prediction_data', [])
            
            if prediction_data:
                # 如果有预测数据，为每个小时创建一行
                for hour_data in prediction_data:
                    row = {
                        'user_id': user_id,
                        'username': username,
                        'session_id': session_id,
                        'experiment_start_time': start_time,
                        'decision_id': decision_id,
                        'decision_label': decision_label,
                        'decision_reason': decision_reason,
                        'decision_status': decision_status,
                        'decision_created_at': created_at,
                        'decision_completed_at': completed_at,
                        'hour': hour_data.get('hour', 0),
                        'original_prediction': hour_data.get('original_prediction', 0),
                        'current_prediction': hour_data.get('current_prediction', 0),
                        'confidence_min': hour_data.get('confidence_min', 0),
                        'confidence_max': hour_data.get('confidence_max', 0),
                        'is_adjusted': hour_data.get('is_adjusted', False),
                        'adjustment_amount': hour_data.get('current_prediction', 0) - hour_data.get('original_prediction', 0)
                    }
                    decisions_data.append(row)
            else:
                # 如果没有预测数据，创建一行基本信息
                row = {
                    'user_id': user_id,
                    'username': username,
                    'session_id': session_id,
                    'experiment_start_time': start_time,
                    'decision_id': decision_id,
                    'decision_label': decision_label,
                    'decision_reason': decision_reason,
                    'decision_status': decision_status,
                    'decision_created_at': created_at,
                    'decision_completed_at': completed_at,
                    'hour': None,
                    'original_prediction': None,
                    'current_prediction': None,
                    'confidence_min': None,
                    'confidence_max': None,
                    'is_adjusted': None,
                    'adjustment_amount': None
                }
                decisions_data.append(row)
        
        return decisions_data
    
    def generate_user_csv(self, user_id: str, user_decisions: List[Dict[str, Any]]) -> str:
        """为单个用户生成CSV文件"""
        if not user_decisions:
            logger.warning(f"No decision data for user {user_id}")
            return ""
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        username = user_decisions[0].get('username', 'unknown')
        filename = f"{user_id}_{username}_{timestamp}_decisions.csv"
        filepath = self.csv_output_dir / filename
        
        # 定义CSV列
        columns = [
            'user_id', 'username', 'session_id', 'experiment_start_time',
            'decision_id', 'decision_label', 'decision_reason', 'decision_status',
            'decision_created_at', 'decision_completed_at',
            'hour', 'original_prediction', 'current_prediction',
            'confidence_min', 'confidence_max', 'is_adjusted', 'adjustment_amount'
        ]
        
        try:
            # 创建DataFrame并保存为CSV
            df = pd.DataFrame(user_decisions)
            df = df.reindex(columns=columns)  # 确保列顺序
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"Generated CSV for user {user_id}: {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating CSV for user {user_id}: {e}")
            return ""
    
    def process_all_experiments(self) -> Dict[str, str]:
        """处理所有实验数据并生成CSV文件"""
        if not self.experiment_results_dir.exists():
            logger.error(f"Experiment results directory not found: {self.experiment_results_dir}")
            return {}
        
        user_data = {}  # user_id -> list of decisions
        generated_files = {}  # user_id -> csv_file_path
        
        # 遍历所有实验结果文件
        for file_path in self.experiment_results_dir.glob("*.json"):
            logger.info(f"Processing {file_path.name}")
            
            data = self.load_experiment_data(file_path)
            if not data:
                continue
            
            experiment_data = data.get('experiment_data', {})
            user_id = experiment_data.get('user_id', 'unknown')
            
            # 提取决策数据
            decisions = self.extract_decision_data(experiment_data)
            
            if user_id not in user_data:
                user_data[user_id] = []
            user_data[user_id].extend(decisions)
        
        # 为每个用户生成CSV文件
        for user_id, decisions in user_data.items():
            if decisions:
                csv_file = self.generate_user_csv(user_id, decisions)
                if csv_file:
                    generated_files[user_id] = csv_file
        
        return generated_files
    
    def generate_summary_report(self, generated_files: Dict[str, str]) -> str:
        """生成处理摘要报告"""
        summary_file = self.csv_output_dir / f"generation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("User Decision CSV Generation Summary\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated at: {datetime.now().isoformat()}\n")
            f.write(f"Total users processed: {len(generated_files)}\n\n")
            
            for user_id, csv_file in generated_files.items():
                f.write(f"User ID: {user_id}\n")
                f.write(f"CSV File: {Path(csv_file).name}\n")
                f.write("-" * 30 + "\n")
        
        return str(summary_file)

def main():
    """主函数"""
    generator = UserDecisionCSVGenerator()
    
    logger.info("Starting user decision CSV generation...")
    generated_files = generator.process_all_experiments()
    
    if generated_files:
        summary_file = generator.generate_summary_report(generated_files)
        logger.info(f"Generation complete! Summary: {summary_file}")
        logger.info(f"Generated {len(generated_files)} CSV files")
    else:
        logger.warning("No CSV files generated")

if __name__ == "__main__":
    main()
