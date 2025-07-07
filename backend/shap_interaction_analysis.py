#!/usr/bin/env python3
"""
SHAP交互分析 - 三维可视化
计算气温×小时的交互效应对电力预测的影响
"""

import numpy as np
import pandas as pd
import shap
import joblib
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class SHAPInteractionAnalyzer:
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
        print(f"   训练数据: {self.train_data.shape}")
        print(f"   预测数据: {self.predict_data.shape}")
        
    def train_model(self):
        """训练XGBoost模型"""
        print("🤖 训练XGBoost模型...")

        # 准备训练数据
        X_train = self.train_data[self.feature_columns].values
        y_train = self.train_data['actual_power'].values

        # 标准化特征
        from sklearn.preprocessing import StandardScaler
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)

        # 训练XGBoost模型
        import xgboost as xgb
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.model.fit(X_train_scaled, y_train)

        print("✅ 模型训练完成")

    def initialize_shap(self):
        """初始化SHAP解释器"""
        print("🔍 初始化SHAP解释器...")

        X_train_scaled = self.scaler.transform(self.train_data[self.feature_columns].values)
        self.explainer = shap.TreeExplainer(self.model, data=X_train_scaled)

        print("✅ SHAP解释器初始化完成")
        
    def calculate_interaction_values(self):
        """计算SHAP交互值"""
        print("🧮 计算SHAP交互值...")
        
        # 准备预测数据
        X_predict_scaled = self.scaler.transform(self.predict_data[self.feature_columns].values)
        
        # 计算SHAP交互值
        self.shap_interaction_values = self.explainer.shap_interaction_values(X_predict_scaled)
        
        print(f"✅ SHAP交互值计算完成")
        print(f"   交互矩阵形状: {self.shap_interaction_values.shape}")
        
        return self.shap_interaction_values
        
    def analyze_temperature_hour_interaction(self):
        """分析气温×小时的交互效应"""
        print("🌡️⏰ 分析气温×小时交互效应...")
        
        # 特征索引
        temp_idx = self.feature_names.index('Temperature')
        hour_idx = self.feature_names.index('Hour')
        
        # 提取气温×小时的交互值
        temp_hour_interactions = self.shap_interaction_values[:, temp_idx, hour_idx]
        
        # 获取对应的特征值
        temperatures = self.predict_data['temp'].values
        hours = self.predict_data['hour'].values
        
        # 创建交互分析数据
        interaction_data = []
        for i in range(len(temp_hour_interactions)):
            interaction_data.append({
                'hour': int(hours[i]),
                'temperature': float(temperatures[i]),
                'interaction_value': float(temp_hour_interactions[i]),
                'time_str': f"{int(hours[i]):02d}:00"
            })
        
        return interaction_data
        
    def create_interaction_heatmap_data(self):
        """创建交互热力图数据"""
        print("🗺️ 创建交互热力图数据...")
        
        interaction_data = self.analyze_temperature_hour_interaction()
        
        # 创建DataFrame
        df = pd.DataFrame(interaction_data)
        
        # 创建温度和小时的网格
        temp_range = np.arange(-6, 5, 1)  # 温度范围：-6°C到4°C
        hour_range = np.arange(0, 24, 1)   # 小时范围：0-23
        
        # 创建热力图矩阵
        heatmap_matrix = np.zeros((len(temp_range), len(hour_range)))
        
        for i, temp in enumerate(temp_range):
            for j, hour in enumerate(hour_range):
                # 找到最接近的数据点
                closest_data = df[
                    (np.abs(df['temperature'] - temp) <= 0.5) & 
                    (df['hour'] == hour)
                ]
                
                if not closest_data.empty:
                    heatmap_matrix[i, j] = closest_data['interaction_value'].mean()
                else:
                    # 如果没有精确匹配，使用插值
                    temp_close = df[np.abs(df['temperature'] - temp) <= 1.0]
                    if not temp_close.empty:
                        hour_close = temp_close[temp_close['hour'] == hour]
                        if not hour_close.empty:
                            heatmap_matrix[i, j] = hour_close['interaction_value'].mean()
        
        return {
            'matrix': heatmap_matrix.tolist(),
            'temperature_range': temp_range.tolist(),
            'hour_range': hour_range.tolist(),
            'raw_data': interaction_data
        }
        
    def create_interaction_insights(self, interaction_data):
        """生成交互效应洞察"""
        print("💡 生成交互效应洞察...")
        
        df = pd.DataFrame(interaction_data)
        
        insights = []
        
        # 1. 找出最强的正向交互效应
        max_positive = df.loc[df['interaction_value'].idxmax()]
        insights.append({
            'type': 'max_positive',
            'description': f"最强正向交互: {max_positive['temperature']:.1f}°C at {max_positive['time_str']}",
            'value': float(max_positive['interaction_value']),
            'interpretation': f"在{max_positive['time_str']}时，{max_positive['temperature']:.1f}°C的温度与小时因子产生最强的协同增强效应"
        })
        
        # 2. 找出最强的负向交互效应
        min_negative = df.loc[df['interaction_value'].idxmin()]
        insights.append({
            'type': 'max_negative', 
            'description': f"最强负向交互: {min_negative['temperature']:.1f}°C at {min_negative['time_str']}",
            'value': float(min_negative['interaction_value']),
            'interpretation': f"在{min_negative['time_str']}时，{min_negative['temperature']:.1f}°C的温度与小时因子产生最强的抑制效应"
        })
        
        # 3. 分析不同时段的温度敏感性
        morning_peak = df[df['hour'].isin([7, 8, 9])]['interaction_value'].mean()
        evening_peak = df[df['hour'].isin([18, 19, 20])]['interaction_value'].mean()
        
        insights.append({
            'type': 'time_sensitivity',
            'description': f"时段敏感性分析",
            'morning_peak': float(morning_peak),
            'evening_peak': float(evening_peak),
            'interpretation': f"早高峰(7-9时)平均交互值: {morning_peak:.3f}, 晚高峰(18-20时)平均交互值: {evening_peak:.3f}"
        })
        
        # 4. 分析极端温度的影响
        cold_effect = df[df['temperature'] < -2]['interaction_value'].mean()
        mild_effect = df[df['temperature'] > 0]['interaction_value'].mean()
        
        insights.append({
            'type': 'temperature_extremes',
            'description': f"极端温度效应",
            'cold_effect': float(cold_effect) if not np.isnan(cold_effect) else 0,
            'mild_effect': float(mild_effect) if not np.isnan(mild_effect) else 0,
            'interpretation': f"严寒(<-2°C)平均交互值: {cold_effect:.3f}, 温和(>0°C)平均交互值: {mild_effect:.3f}"
        })
        
        return insights
        
    def save_interaction_data(self, output_dir='frontend/public/data'):
        """保存交互分析数据"""
        print("💾 保存交互分析数据...")
        
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 计算交互数据
        interaction_data = self.analyze_temperature_hour_interaction()
        heatmap_data = self.create_interaction_heatmap_data()
        insights = self.create_interaction_insights(interaction_data)
        
        # 保存热力图数据
        with open(f'{output_dir}/shap_temperature_hour_interaction.json', 'w', encoding='utf-8') as file:
            json.dump({
                'metadata': {
                    'title': 'Temperature × Hour SHAP Interaction Analysis',
                    'description': 'SHAP interaction values showing how temperature and hour jointly affect power prediction',
                    'date': '2022-01-07',
                    'features': ['Temperature', 'Hour']
                },
                'heatmap_data': heatmap_data,
                'insights': insights,
                'raw_interactions': interaction_data[:50]  # 保存前50个数据点作为示例
            }, file, indent=2, ensure_ascii=False)
        
        # 保存CSV格式的详细数据
        df = pd.DataFrame(interaction_data)
        df.to_csv(f'{output_dir}/shap_temperature_hour_interactions.csv', index=False)
        
        print(f"✅ 交互分析数据已保存到 {output_dir}")
        
    def run_full_analysis(self):
        """运行完整的交互分析"""
        print("🚀 开始SHAP交互分析...")
        
        # 1. 加载和准备数据
        self.load_and_prepare_data()

        # 2. 训练模型
        self.train_model()

        # 3. 初始化SHAP
        self.initialize_shap()
        
        # 4. 计算交互值
        self.calculate_interaction_values()

        # 5. 保存分析结果
        self.save_interaction_data()
        
        print("🎉 SHAP交互分析完成！")

if __name__ == "__main__":
    analyzer = SHAPInteractionAnalyzer()
    analyzer.run_full_analysis()
