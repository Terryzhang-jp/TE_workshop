#!/usr/bin/env python3
"""
当前用户数据CSV生成脚本

处理现有的实验数据格式，生成用户决策和调整的CSV文件
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

class CurrentUserCSVGenerator:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.experiment_results_dir = self.data_dir / "experiment_results"
        self.csv_output_dir = self.data_dir / "user_csv_exports"
        
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
    
    def extract_user_data(self, experiment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取用户数据，包含决策和调整信息"""
        user_rows = []
        
        # 基本用户信息
        user_id = experiment_data.get('user_id', 'unknown')
        username = experiment_data.get('username', 'unknown')
        session_id = experiment_data.get('session_id', 'unknown')
        start_time = experiment_data.get('start_time', '')
        completion_time = experiment_data.get('completion_time', '')
        status = experiment_data.get('status', '')
        
        decisions = experiment_data.get('decisions', [])
        adjustments = experiment_data.get('adjustments', [])
        
        # 创建调整的映射，按决策ID分组
        adjustments_by_decision = {}
        for adj in adjustments:
            decision_id = adj.get('decision_id', '')
            if decision_id not in adjustments_by_decision:
                adjustments_by_decision[decision_id] = []
            adjustments_by_decision[decision_id].append(adj)
        
        # 为每个决策创建行
        for decision in decisions:
            decision_id = decision.get('id', '')
            decision_label = decision.get('label', '')
            decision_reason = decision.get('reason', '')
            decision_status = decision.get('status', '')
            decision_created_at = decision.get('created_at', '')
            decision_completed_at = decision.get('completed_at', '')
            
            # 获取该决策的调整
            decision_adjustments = adjustments_by_decision.get(decision_id, [])
            
            if decision_adjustments:
                # 为每个调整创建一行
                for adj in decision_adjustments:
                    row = {
                        'user_id': user_id,
                        'username': username,
                        'session_id': session_id,
                        'experiment_start_time': start_time,
                        'experiment_completion_time': completion_time,
                        'experiment_status': status,
                        'decision_id': decision_id,
                        'decision_label': decision_label,
                        'decision_reason': decision_reason,
                        'decision_status': decision_status,
                        'decision_created_at': decision_created_at,
                        'decision_completed_at': decision_completed_at,
                        'adjustment_id': adj.get('id', ''),
                        'adjustment_hour': adj.get('hour', ''),
                        'original_value': adj.get('original_value', ''),
                        'adjusted_value': adj.get('adjusted_value', ''),
                        'adjustment_amount': adj.get('adjusted_value', 0) - adj.get('original_value', 0),
                        'adjustment_timestamp': adj.get('timestamp', ''),
                        'has_adjustment': True
                    }
                    user_rows.append(row)
            else:
                # 没有调整的决策，创建一行基本信息
                row = {
                    'user_id': user_id,
                    'username': username,
                    'session_id': session_id,
                    'experiment_start_time': start_time,
                    'experiment_completion_time': completion_time,
                    'experiment_status': status,
                    'decision_id': decision_id,
                    'decision_label': decision_label,
                    'decision_reason': decision_reason,
                    'decision_status': decision_status,
                    'decision_created_at': decision_created_at,
                    'decision_completed_at': decision_completed_at,
                    'adjustment_id': '',
                    'adjustment_hour': '',
                    'original_value': '',
                    'adjusted_value': '',
                    'adjustment_amount': 0,
                    'adjustment_timestamp': '',
                    'has_adjustment': False
                }
                user_rows.append(row)
        
        return user_rows
    
    def generate_user_csv(self, user_id: str, username: str, user_data: List[Dict[str, Any]]) -> str:
        """为单个用户生成CSV文件"""
        if not user_data:
            logger.warning(f"No data for user {user_id}")
            return ""
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{user_id}_{username}_{timestamp}.csv"
        filepath = self.csv_output_dir / filename
        
        # 定义CSV列
        columns = [
            'user_id', 'username', 'session_id', 
            'experiment_start_time', 'experiment_completion_time', 'experiment_status',
            'decision_id', 'decision_label', 'decision_reason', 'decision_status',
            'decision_created_at', 'decision_completed_at',
            'adjustment_id', 'adjustment_hour', 'original_value', 'adjusted_value', 
            'adjustment_amount', 'adjustment_timestamp', 'has_adjustment'
        ]
        
        try:
            # 创建DataFrame并保存为CSV
            df = pd.DataFrame(user_data)
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
        
        user_data = {}  # user_id -> {username, data}
        generated_files = {}  # user_id -> csv_file_path
        
        # 遍历所有实验结果文件
        for file_path in self.experiment_results_dir.glob("*.json"):
            logger.info(f"Processing {file_path.name}")
            
            data = self.load_experiment_data(file_path)
            if not data:
                continue
            
            experiment_data = data.get('experiment_data', {})
            user_id = experiment_data.get('user_id', 'unknown')
            username = experiment_data.get('username', 'unknown')
            
            # 提取用户数据
            user_rows = self.extract_user_data(experiment_data)
            
            if user_id not in user_data:
                user_data[user_id] = {'username': username, 'data': []}
            user_data[user_id]['data'].extend(user_rows)
        
        # 为每个用户生成CSV文件
        for user_id, user_info in user_data.items():
            if user_info['data']:
                csv_file = self.generate_user_csv(user_id, user_info['username'], user_info['data'])
                if csv_file:
                    generated_files[user_id] = csv_file
        
        return generated_files
    
    def generate_summary_report(self, generated_files: Dict[str, str]) -> str:
        """生成处理摘要报告"""
        summary_file = self.csv_output_dir / f"generation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Current User Data CSV Generation Summary\n")
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
    generator = CurrentUserCSVGenerator()
    
    logger.info("Starting current user data CSV generation...")
    generated_files = generator.process_all_experiments()
    
    if generated_files:
        summary_file = generator.generate_summary_report(generated_files)
        logger.info(f"Generation complete! Summary: {summary_file}")
        logger.info(f"Generated {len(generated_files)} CSV files")
        
        # 打印生成的文件
        for user_id, csv_file in generated_files.items():
            print(f"Generated: {csv_file}")
    else:
        logger.warning("No CSV files generated")

if __name__ == "__main__":
    main()
