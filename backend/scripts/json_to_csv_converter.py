#!/usr/bin/env python3
"""
实验结果JSON到CSV转换脚本
Experiment Results JSON to CSV Converter Script

将实验结果JSON文件转换为多个CSV文件，便于数据分析
"""

import json
import csv
import os
import glob
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

class ExperimentDataConverter:
    def __init__(self, input_dir: str = "experiment_results", output_dir: str = "experiment_results_csv"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def load_json_files(self) -> List[Dict[str, Any]]:
        """加载所有JSON实验结果文件"""
        json_files = glob.glob(os.path.join(self.input_dir, "*.json"))
        experiments = []
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['source_file'] = os.path.basename(file_path)
                    experiments.append(data)
                print(f"✅ 加载文件: {file_path}")
            except Exception as e:
                print(f"❌ 加载文件失败 {file_path}: {e}")
        
        return experiments
    
    def convert_to_csv(self):
        """转换JSON数据为CSV文件"""
        experiments = self.load_json_files()
        
        if not experiments:
            print("❌ 没有找到实验数据文件")
            return
        
        print(f"📊 开始转换 {len(experiments)} 个实验结果...")
        
        # 转换各种数据类型
        self.convert_user_sessions(experiments)
        self.convert_decisions(experiments)
        self.convert_adjustments(experiments)
        self.convert_interactions(experiments)
        self.convert_predictions(experiments)
        self.convert_experiment_summary(experiments)
        
        print(f"✅ 转换完成！CSV文件保存在: {self.output_dir}")
    
    def convert_user_sessions(self, experiments: List[Dict]):
        """转换用户会话数据"""
        sessions = []
        
        for exp in experiments:
            session = {
                'user_id': exp.get('user_id'),
                'username': exp.get('username'),
                'session_id': exp.get('session_id'),
                'experiment_start_time': exp.get('experiment_start_time'),
                'experiment_end_time': exp.get('experiment_end_time'),
                'experiment_duration_minutes': exp.get('experiment_duration_minutes'),
                'source_file': exp.get('source_file'),
                'total_decisions': len(exp.get('decisions', [])),
                'total_adjustments': len(exp.get('adjustments', [])),
                'total_interactions': len(exp.get('interactions', [])),
                'total_predictions': len(exp.get('final_predictions', []))
            }
            sessions.append(session)
        
        df = pd.DataFrame(sessions)
        output_path = os.path.join(self.output_dir, 'user_sessions.csv')
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"📄 用户会话数据: {output_path} ({len(sessions)} 条记录)")
    
    def convert_decisions(self, experiments: List[Dict]):
        """转换决策数据"""
        decisions = []
        
        for exp in experiments:
            user_id = exp.get('user_id')
            session_id = exp.get('session_id')
            
            for decision in exp.get('decisions', []):
                decision_record = {
                    'user_id': user_id,
                    'session_id': session_id,
                    'decision_id': decision.get('decision_id'),
                    'label': decision.get('label'),
                    'reason': decision.get('reason'),
                    'status': decision.get('status'),
                    'created_at': decision.get('created_at'),
                    'completed_at': decision.get('completed_at'),
                    'source_file': exp.get('source_file')
                }
                decisions.append(decision_record)
        
        df = pd.DataFrame(decisions)
        output_path = os.path.join(self.output_dir, 'user_decisions.csv')
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"📄 用户决策数据: {output_path} ({len(decisions)} 条记录)")
    
    def convert_adjustments(self, experiments: List[Dict]):
        """转换调整数据"""
        adjustments = []
        
        for exp in experiments:
            user_id = exp.get('user_id')
            session_id = exp.get('session_id')
            
            for adjustment in exp.get('adjustments', []):
                adjustment_record = {
                    'user_id': user_id,
                    'session_id': session_id,
                    'adjustment_id': adjustment.get('adjustment_id'),
                    'decision_id': adjustment.get('decision_id'),
                    'hour': adjustment.get('hour'),
                    'original_value': adjustment.get('original_value'),
                    'adjusted_value': adjustment.get('adjusted_value'),
                    'adjustment_amount': adjustment.get('adjusted_value', 0) - adjustment.get('original_value', 0),
                    'adjustment_percentage': ((adjustment.get('adjusted_value', 0) - adjustment.get('original_value', 0)) / adjustment.get('original_value', 1)) * 100 if adjustment.get('original_value', 0) != 0 else 0,
                    'timestamp': adjustment.get('timestamp'),
                    'source_file': exp.get('source_file')
                }
                adjustments.append(adjustment_record)
        
        df = pd.DataFrame(adjustments)
        output_path = os.path.join(self.output_dir, 'user_adjustments.csv')
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"📄 用户调整数据: {output_path} ({len(adjustments)} 条记录)")
    
    def convert_interactions(self, experiments: List[Dict]):
        """转换交互数据"""
        interactions = []
        
        for exp in experiments:
            user_id = exp.get('user_id')
            session_id = exp.get('session_id')
            
            for interaction in exp.get('interactions', []):
                # 扁平化action_details
                action_details = interaction.get('action_details', {})
                interaction_record = {
                    'user_id': user_id,
                    'session_id': session_id,
                    'interaction_id': interaction.get('interaction_id'),
                    'component': interaction.get('component'),
                    'action_type': interaction.get('action_type'),
                    'timestamp': interaction.get('timestamp'),
                    'source_file': exp.get('source_file')
                }
                
                # 添加action_details的所有字段
                for key, value in action_details.items():
                    interaction_record[f'detail_{key}'] = value
                
                interactions.append(interaction_record)
        
        df = pd.DataFrame(interactions)
        output_path = os.path.join(self.output_dir, 'user_interactions.csv')
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"📄 用户交互数据: {output_path} ({len(interactions)} 条记录)")
    
    def convert_predictions(self, experiments: List[Dict]):
        """转换预测结果数据"""
        predictions = []
        
        for exp in experiments:
            user_id = exp.get('user_id')
            session_id = exp.get('session_id')
            
            for prediction in exp.get('final_predictions', []):
                prediction_record = {
                    'user_id': user_id,
                    'session_id': session_id,
                    'hour': prediction.get('hour'),
                    'predicted_usage': prediction.get('predicted_usage'),
                    'original_prediction': prediction.get('original_prediction'),
                    'confidence_interval_lower': prediction.get('confidence_interval', [None, None])[0],
                    'confidence_interval_upper': prediction.get('confidence_interval', [None, None])[1],
                    'adjustment_amount': prediction.get('predicted_usage', 0) - prediction.get('original_prediction', 0),
                    'was_adjusted': prediction.get('predicted_usage') != prediction.get('original_prediction'),
                    'source_file': exp.get('source_file')
                }
                predictions.append(prediction_record)
        
        df = pd.DataFrame(predictions)
        output_path = os.path.join(self.output_dir, 'final_predictions.csv')
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"📄 最终预测数据: {output_path} ({len(predictions)} 条记录)")
    
    def convert_experiment_summary(self, experiments: List[Dict]):
        """生成实验汇总统计"""
        summary = []
        
        for exp in experiments:
            decisions = exp.get('decisions', [])
            adjustments = exp.get('adjustments', [])
            interactions = exp.get('interactions', [])
            predictions = exp.get('final_predictions', [])
            
            # 计算统计信息
            total_adjustments_made = len([p for p in predictions if p.get('predicted_usage') != p.get('original_prediction')])
            avg_adjustment_amount = sum([abs(a.get('adjusted_value', 0) - a.get('original_value', 0)) for a in adjustments]) / len(adjustments) if adjustments else 0
            
            # 交互统计
            interaction_by_component = {}
            for interaction in interactions:
                component = interaction.get('component', 'Unknown')
                interaction_by_component[component] = interaction_by_component.get(component, 0) + 1
            
            summary_record = {
                'user_id': exp.get('user_id'),
                'username': exp.get('username'),
                'session_id': exp.get('session_id'),
                'experiment_duration_minutes': exp.get('experiment_duration_minutes'),
                'total_decisions': len(decisions),
                'total_adjustments': len(adjustments),
                'total_interactions': len(interactions),
                'total_predictions': len(predictions),
                'predictions_adjusted': total_adjustments_made,
                'adjustment_rate': (total_adjustments_made / len(predictions)) * 100 if predictions else 0,
                'avg_adjustment_amount': avg_adjustment_amount,
                'context_interactions': interaction_by_component.get('ContextInformation', 0),
                'data_analysis_interactions': interaction_by_component.get('DataAnalysis', 0),
                'model_interp_interactions': interaction_by_component.get('ModelInterpretability', 0),
                'user_prediction_interactions': interaction_by_component.get('UserPrediction', 0),
                'decision_making_interactions': interaction_by_component.get('DecisionMaking', 0),
                'source_file': exp.get('source_file')
            }
            summary.append(summary_record)
        
        df = pd.DataFrame(summary)
        output_path = os.path.join(self.output_dir, 'experiment_summary.csv')
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"📄 实验汇总统计: {output_path} ({len(summary)} 条记录)")

def main():
    """主函数"""
    print("🔄 实验结果JSON到CSV转换器")
    print("=" * 50)
    
    converter = ExperimentDataConverter()
    converter.convert_to_csv()
    
    print("\n📊 转换完成的CSV文件:")
    csv_files = glob.glob(os.path.join(converter.output_dir, "*.csv"))
    for csv_file in csv_files:
        file_size = os.path.getsize(csv_file)
        print(f"  📄 {os.path.basename(csv_file)} ({file_size} bytes)")

if __name__ == "__main__":
    main()
