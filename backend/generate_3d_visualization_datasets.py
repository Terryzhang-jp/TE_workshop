#!/usr/bin/env python3
"""
生成3D可视化数据集
1. Temperature × Hour → Power Demand
2. Day of Week × Hour → Power Demand  
3. Week of Month × Hour → Power Demand
"""

import numpy as np
import pandas as pd
import json
import shap
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class ThreeDVisualizationDataGenerator:
    def __init__(self, data_path='data/worst_day_1_2022_01_07_winter_extreme_cold.csv'):
        self.data_path = data_path
        self.model = None
        self.scaler = None
        self.explainer = None
        self.feature_columns = ['temp', 'hour', 'day_of_week', 'week_of_month']
        self.feature_names = ['Temperature', 'Hour', 'Day_of_Week', 'Week_of_Month']
        
    def load_and_prepare_data(self):
        """加载和准备数据"""
        print("📂 加载和准备数据...")
        
        # 加载数据
        df = pd.read_csv(self.data_path)
        df['时间'] = pd.to_datetime(df['时间'])
        df = df.rename(columns={
            '时间': 'time', '预测电力': 'predicted_power',
            '真实电力': 'actual_power', '预测天气': 'predicted_temp'
        })
        
        # 特征工程
        df['hour'] = df['time'].dt.hour
        df['day_of_week'] = df['time'].dt.dayofweek
        df['week_of_month'] = (df['time'].dt.day - 1) // 7 + 1
        df['temp'] = df['predicted_temp']
        
        # 分离数据
        self.train_data = df[df['actual_power'].notna()].copy()
        self.predict_data = df[df['predicted_power'].notna()].copy()
        
        print(f"✅ 数据准备完成")
        
    def train_model_and_initialize_shap(self):
        """训练模型并初始化SHAP"""
        print("🤖 训练模型并初始化SHAP...")
        
        # 准备训练数据
        X_train = self.train_data[self.feature_columns].values
        y_train = self.train_data['actual_power'].values
        
        # 标准化特征
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # 训练XGBoost模型
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.model.fit(X_train_scaled, y_train)
        
        # 初始化SHAP
        self.explainer = shap.TreeExplainer(self.model, data=X_train_scaled)
        
        print("✅ 模型训练和SHAP初始化完成")
        
    def generate_temperature_hour_3d_data(self):
        """生成Temperature × Hour → Power Demand 3D数据"""
        print("🌡️⏰ 生成Temperature × Hour 3D数据...")
        
        # 定义网格范围
        temp_range = np.arange(-6, 20, 1)  # -6°C to 19°C
        hour_range = np.arange(0, 24, 1)   # 0-23 hours
        
        # 创建3D数据矩阵
        power_demand_matrix = np.zeros((len(temp_range), len(hour_range)))
        shap_effect_matrix = np.zeros((len(temp_range), len(hour_range)))
        
        # 固定其他特征的典型值
        typical_dow = 3  # Thursday (工作日)
        typical_wom = 2  # Week 2
        
        for i, temp in enumerate(temp_range):
            for j, hour in enumerate(hour_range):
                # 创建特征向量
                features = np.array([[temp, hour, typical_dow, typical_wom]])
                features_scaled = self.scaler.transform(features)
                
                # 预测电力需求
                power_demand = self.model.predict(features_scaled)[0]
                power_demand_matrix[i, j] = power_demand
                
                # 计算SHAP值
                shap_values = self.explainer.shap_values(features_scaled)
                # 温度和小时的联合SHAP效应
                temp_shap = shap_values[0, 0]  # Temperature SHAP
                hour_shap = shap_values[0, 1]  # Hour SHAP
                joint_effect = temp_shap + hour_shap
                shap_effect_matrix[i, j] = joint_effect
        
        return {
            'title': 'Temperature × Hour → Power Demand',
            'x_axis': {
                'name': 'Hour of Day',
                'values': hour_range.tolist(),
                'labels': [f'{h:02d}:00' for h in hour_range]
            },
            'y_axis': {
                'name': 'Temperature (°C)',
                'values': temp_range.tolist(),
                'labels': [f'{t}°C' for t in temp_range]
            },
            'z_axis': {
                'name': 'Power Demand (MW)',
                'power_demand_matrix': power_demand_matrix.tolist(),
                'shap_effect_matrix': shap_effect_matrix.tolist()
            },
            'metadata': {
                'fixed_features': {
                    'day_of_week': typical_dow,
                    'week_of_month': typical_wom
                },
                'description': 'Power demand and SHAP effects across temperature and hour combinations'
            }
        }
        
    def generate_dow_hour_3d_data(self):
        """生成Day of Week × Hour → Power Demand 3D数据"""
        print("📅⏰ 生成Day of Week × Hour 3D数据...")
        
        # 定义网格范围
        dow_range = np.arange(0, 7, 1)     # 0-6 (Monday-Sunday)
        hour_range = np.arange(0, 24, 1)   # 0-23 hours
        
        # 创建3D数据矩阵
        power_demand_matrix = np.zeros((len(dow_range), len(hour_range)))
        shap_effect_matrix = np.zeros((len(dow_range), len(hour_range)))
        
        # 固定其他特征的典型值
        typical_temp = 5.0  # 5°C (moderate temperature)
        typical_wom = 2     # Week 2
        
        for i, dow in enumerate(dow_range):
            for j, hour in enumerate(hour_range):
                # 创建特征向量
                features = np.array([[typical_temp, hour, dow, typical_wom]])
                features_scaled = self.scaler.transform(features)
                
                # 预测电力需求
                power_demand = self.model.predict(features_scaled)[0]
                power_demand_matrix[i, j] = power_demand
                
                # 计算SHAP值
                shap_values = self.explainer.shap_values(features_scaled)
                # 星期和小时的联合SHAP效应
                dow_shap = shap_values[0, 2]   # Day_of_Week SHAP
                hour_shap = shap_values[0, 1]  # Hour SHAP
                joint_effect = dow_shap + hour_shap
                shap_effect_matrix[i, j] = joint_effect
        
        return {
            'title': 'Day of Week × Hour → Power Demand',
            'x_axis': {
                'name': 'Hour of Day',
                'values': hour_range.tolist(),
                'labels': [f'{h:02d}:00' for h in hour_range]
            },
            'y_axis': {
                'name': 'Day of Week',
                'values': dow_range.tolist(),
                'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            },
            'z_axis': {
                'name': 'Power Demand (MW)',
                'power_demand_matrix': power_demand_matrix.tolist(),
                'shap_effect_matrix': shap_effect_matrix.tolist()
            },
            'metadata': {
                'fixed_features': {
                    'temperature': typical_temp,
                    'week_of_month': typical_wom
                },
                'description': 'Power demand and SHAP effects across day of week and hour combinations'
            }
        }
        
    def generate_wom_hour_3d_data(self):
        """生成Week of Month × Hour → Power Demand 3D数据"""
        print("📊⏰ 生成Week of Month × Hour 3D数据...")
        
        # 定义网格范围
        wom_range = np.arange(1, 5, 1)     # 1-4 (Week 1-4)
        hour_range = np.arange(0, 24, 1)   # 0-23 hours
        
        # 创建3D数据矩阵
        power_demand_matrix = np.zeros((len(wom_range), len(hour_range)))
        shap_effect_matrix = np.zeros((len(wom_range), len(hour_range)))
        
        # 固定其他特征的典型值
        typical_temp = 5.0  # 5°C (moderate temperature)
        typical_dow = 3     # Thursday (工作日)
        
        for i, wom in enumerate(wom_range):
            for j, hour in enumerate(hour_range):
                # 创建特征向量
                features = np.array([[typical_temp, hour, typical_dow, wom]])
                features_scaled = self.scaler.transform(features)
                
                # 预测电力需求
                power_demand = self.model.predict(features_scaled)[0]
                power_demand_matrix[i, j] = power_demand
                
                # 计算SHAP值
                shap_values = self.explainer.shap_values(features_scaled)
                # 周数和小时的联合SHAP效应
                wom_shap = shap_values[0, 3]   # Week_of_Month SHAP
                hour_shap = shap_values[0, 1]  # Hour SHAP
                joint_effect = wom_shap + hour_shap
                shap_effect_matrix[i, j] = joint_effect
        
        return {
            'title': 'Week of Month × Hour → Power Demand',
            'x_axis': {
                'name': 'Hour of Day',
                'values': hour_range.tolist(),
                'labels': [f'{h:02d}:00' for h in hour_range]
            },
            'y_axis': {
                'name': 'Week of Month',
                'values': wom_range.tolist(),
                'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4']
            },
            'z_axis': {
                'name': 'Power Demand (MW)',
                'power_demand_matrix': power_demand_matrix.tolist(),
                'shap_effect_matrix': shap_effect_matrix.tolist()
            },
            'metadata': {
                'fixed_features': {
                    'temperature': typical_temp,
                    'day_of_week': typical_dow
                },
                'description': 'Power demand and SHAP effects across week of month and hour combinations'
            }
        }
        
    def save_3d_datasets(self, output_dir='frontend/public/data'):
        """保存3D可视化数据集"""
        print("💾 保存3D可视化数据集...")
        
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 生成所有3D数据集
        temp_hour_data = self.generate_temperature_hour_3d_data()
        dow_hour_data = self.generate_dow_hour_3d_data()
        wom_hour_data = self.generate_wom_hour_3d_data()
        
        # 保存完整数据集
        complete_3d_data = {
            'metadata': {
                'title': '3D Power Demand Visualization Datasets',
                'description': 'Three-dimensional datasets for visualizing power demand interactions',
                'generated_date': '2022-01-07',
                'model_info': {
                    'type': 'XGBoost Regressor',
                    'features': self.feature_names,
                    'base_prediction': float(self.explainer.expected_value)
                }
            },
            'temperature_hour': temp_hour_data,
            'day_of_week_hour': dow_hour_data,
            'week_of_month_hour': wom_hour_data
        }
        
        # 保存主数据文件
        with open(f'{output_dir}/shap_3d_visualization_datasets.json', 'w', encoding='utf-8') as file:
            json.dump(complete_3d_data, file, indent=2, ensure_ascii=False)
        
        # 保存单独的数据集文件（便于前端使用）
        with open(f'{output_dir}/temperature_hour_3d.json', 'w', encoding='utf-8') as file:
            json.dump(temp_hour_data, file, indent=2, ensure_ascii=False)
            
        with open(f'{output_dir}/day_of_week_hour_3d.json', 'w', encoding='utf-8') as file:
            json.dump(dow_hour_data, file, indent=2, ensure_ascii=False)
            
        with open(f'{output_dir}/week_of_month_hour_3d.json', 'w', encoding='utf-8') as file:
            json.dump(wom_hour_data, file, indent=2, ensure_ascii=False)
        
        print(f"✅ 3D数据集已保存到 {output_dir}")
        print("📁 生成的文件:")
        print("   • shap_3d_visualization_datasets.json - 完整3D数据集")
        print("   • temperature_hour_3d.json - 温度×小时数据")
        print("   • day_of_week_hour_3d.json - 星期×小时数据")
        print("   • week_of_month_hour_3d.json - 周数×小时数据")
        
    def run_generation(self):
        """运行完整的数据生成"""
        print("🚀 开始生成3D可视化数据集...")
        
        # 1. 加载和准备数据
        self.load_and_prepare_data()
        
        # 2. 训练模型并初始化SHAP
        self.train_model_and_initialize_shap()
        
        # 3. 生成并保存3D数据集
        self.save_3d_datasets()
        
        print("🎉 3D可视化数据集生成完成！")

if __name__ == "__main__":
    generator = ThreeDVisualizationDataGenerator()
    generator.run_generation()
