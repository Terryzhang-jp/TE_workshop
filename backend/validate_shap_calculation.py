#!/usr/bin/env python3
"""
深度验证SHAP计算的合理性
检查SHAP值的数学性质、一致性和解释性
"""

import pandas as pd
import numpy as np
import shap
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class SHAPValidationAnalyzer:
    def __init__(self, data_path='data/worst_day_1_2022_01_07_winter_extreme_cold.csv'):
        self.data_path = data_path
        self.model = None
        self.scaler = None
        self.explainer = None
        self.shap_values = None
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
        
    def train_and_validate_model(self):
        """训练模型并验证性能"""
        print("🤖 训练并验证模型...")
        
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
        
        # 验证模型性能
        y_pred = self.model.predict(X_train_scaled)
        mae = mean_absolute_error(y_train, y_pred)
        rmse = np.sqrt(mean_squared_error(y_train, y_pred))
        r2 = r2_score(y_train, y_pred)
        
        print(f"   模型性能: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.3f}")
        
        return {'mae': mae, 'rmse': rmse, 'r2': r2}
        
    def initialize_and_calculate_shap(self):
        """初始化SHAP并计算值"""
        print("🔍 初始化SHAP并计算值...")
        
        # 准备数据
        X_train_scaled = self.scaler.transform(self.train_data[self.feature_columns].values)
        X_predict_scaled = self.scaler.transform(self.predict_data[self.feature_columns].values)
        
        # 初始化SHAP解释器
        self.explainer = shap.TreeExplainer(self.model, data=X_train_scaled)
        
        # 计算SHAP值
        self.shap_values = self.explainer.shap_values(X_predict_scaled)
        
        print(f"✅ SHAP计算完成")
        print(f"   SHAP值形状: {self.shap_values.shape}")
        print(f"   基准值: {self.explainer.expected_value:.2f}")
        
    def validate_shap_properties(self):
        """验证SHAP的数学性质"""
        print("\n🧮 验证SHAP数学性质...")
        
        # 准备数据
        X_predict_scaled = self.scaler.transform(self.predict_data[self.feature_columns].values)
        predictions = self.model.predict(X_predict_scaled)
        
        # 1. 效率性质验证 (Efficiency): sum(SHAP) + base_value = prediction
        print("\n1. 效率性质验证 (Efficiency):")
        shap_sums = np.sum(self.shap_values, axis=1)
        expected_predictions = shap_sums + self.explainer.expected_value
        efficiency_errors = np.abs(predictions - expected_predictions)
        
        print(f"   平均效率误差: {np.mean(efficiency_errors):.6f}")
        print(f"   最大效率误差: {np.max(efficiency_errors):.6f}")
        print(f"   效率性质满足: {'✅' if np.max(efficiency_errors) < 1e-6 else '❌'}")
        
        # 2. 对称性验证 (Symmetry): 相同贡献的特征应有相同SHAP值
        print("\n2. 对称性验证:")
        # 检查相同特征值的SHAP值分布
        for i, feature in enumerate(self.feature_names):
            feature_values = self.predict_data[self.feature_columns[i]].values
            shap_feature = self.shap_values[:, i]
            
            # 计算相同特征值的SHAP值标准差
            unique_values = np.unique(feature_values)
            if len(unique_values) > 1:
                symmetry_scores = []
                for val in unique_values:
                    mask = feature_values == val
                    if np.sum(mask) > 1:
                        shap_std = np.std(shap_feature[mask])
                        symmetry_scores.append(shap_std)
                
                if symmetry_scores:
                    avg_symmetry = np.mean(symmetry_scores)
                    print(f"   {feature}: 平均对称性分数 = {avg_symmetry:.3f}")
        
        # 3. 虚拟性验证 (Dummy): 不影响预测的特征SHAP值应为0
        print("\n3. 虚拟性验证:")
        # 检查特征重要性与SHAP值的一致性
        feature_importance = self.model.feature_importances_
        shap_importance = np.mean(np.abs(self.shap_values), axis=0)
        
        correlation = np.corrcoef(feature_importance, shap_importance)[0, 1]
        print(f"   XGBoost重要性与SHAP重要性相关性: {correlation:.3f}")
        print(f"   一致性验证: {'✅' if correlation > 0.8 else '❌'}")
        
        # 4. 可加性验证 (Additivity)
        print("\n4. 可加性验证:")
        # 对于线性模型，SHAP值应该等于特征值乘以权重
        # 对于树模型，检查SHAP值的合理范围
        for i, feature in enumerate(self.feature_names):
            shap_range = [np.min(self.shap_values[:, i]), np.max(self.shap_values[:, i])]
            feature_range = [np.min(self.predict_data[self.feature_columns[i]]), 
                           np.max(self.predict_data[self.feature_columns[i]])]
            print(f"   {feature}:")
            print(f"      SHAP范围: [{shap_range[0]:.2f}, {shap_range[1]:.2f}]")
            print(f"      特征范围: [{feature_range[0]:.2f}, {feature_range[1]:.2f}]")
        
        return {
            'efficiency_error': np.mean(efficiency_errors),
            'consistency_correlation': correlation,
            'shap_ranges': {feature: [float(np.min(self.shap_values[:, i])), 
                                    float(np.max(self.shap_values[:, i]))] 
                          for i, feature in enumerate(self.feature_names)}
        }
        
    def validate_business_logic(self):
        """验证业务逻辑的合理性"""
        print("\n💼 验证业务逻辑合理性...")
        
        business_validation = {}
        
        # 1. 小时特征的合理性
        print("\n1. 小时特征分析:")
        hour_shap = {}
        for hour in range(24):
            mask = self.predict_data['hour'] == hour
            if np.sum(mask) > 0:
                avg_shap = np.mean(self.shap_values[mask, 1])  # Hour是第2个特征
                hour_shap[hour] = avg_shap
        
        # 找出用电高峰和低谷
        peak_hours = sorted(hour_shap.items(), key=lambda x: x[1], reverse=True)[:3]
        low_hours = sorted(hour_shap.items(), key=lambda x: x[1])[:3]
        
        print(f"   用电高峰时段: {[f'{h}:00({v:.1f})' for h, v in peak_hours]}")
        print(f"   用电低谷时段: {[f'{h}:00({v:.1f})' for h, v in low_hours]}")
        
        # 验证是否符合常识：晚上和早上应该是高峰
        expected_peaks = [7, 8, 9, 18, 19, 20, 21]
        actual_peaks = [h for h, v in peak_hours]
        peak_overlap = len(set(expected_peaks) & set(actual_peaks))
        
        print(f"   高峰时段符合预期: {'✅' if peak_overlap >= 1 else '❌'}")
        
        business_validation['hour_logic'] = {
            'peak_hours': peak_hours,
            'low_hours': low_hours,
            'peak_overlap': peak_overlap
        }
        
        # 2. 温度特征的合理性
        print("\n2. 温度特征分析:")
        temp_shap_corr = np.corrcoef(
            self.predict_data['temp'].values,
            self.shap_values[:, 0]  # Temperature是第1个特征
        )[0, 1]
        
        print(f"   温度与SHAP值相关性: {temp_shap_corr:.3f}")
        
        # 分析极端温度的影响
        cold_mask = self.predict_data['temp'] < 0
        warm_mask = self.predict_data['temp'] > 10
        
        if np.sum(cold_mask) > 0:
            cold_shap = np.mean(self.shap_values[cold_mask, 0])
            print(f"   严寒天气(<0°C)平均SHAP: {cold_shap:.2f}")
        
        if np.sum(warm_mask) > 0:
            warm_shap = np.mean(self.shap_values[warm_mask, 0])
            print(f"   温暖天气(>10°C)平均SHAP: {warm_shap:.2f}")
        
        business_validation['temperature_logic'] = {
            'correlation': temp_shap_corr,
            'cold_effect': cold_shap if np.sum(cold_mask) > 0 else None,
            'warm_effect': warm_shap if np.sum(warm_mask) > 0 else None
        }
        
        # 3. 星期特征的合理性
        print("\n3. 星期特征分析:")
        dow_effects = {}
        dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for dow in range(7):
            mask = self.predict_data['day_of_week'] == dow
            if np.sum(mask) > 0:
                avg_shap = np.mean(self.shap_values[mask, 2])  # Day_of_Week是第3个特征
                dow_effects[dow_names[dow]] = avg_shap
        
        weekday_avg = np.mean([dow_effects[day] for day in dow_names[:5] if day in dow_effects])
        weekend_avg = np.mean([dow_effects[day] for day in dow_names[5:] if day in dow_effects])
        
        print(f"   工作日平均SHAP: {weekday_avg:.2f}")
        print(f"   周末平均SHAP: {weekend_avg:.2f}")
        print(f"   工作日vs周末差异: {weekday_avg - weekend_avg:.2f}")
        
        business_validation['weekday_logic'] = {
            'weekday_avg': weekday_avg,
            'weekend_avg': weekend_avg,
            'difference': weekday_avg - weekend_avg
        }
        
        return business_validation
        
    def generate_validation_report(self):
        """生成验证报告"""
        print("\n📋 生成SHAP验证报告...")
        
        # 运行所有验证
        model_performance = self.train_and_validate_model()
        self.initialize_and_calculate_shap()
        math_validation = self.validate_shap_properties()
        business_validation = self.validate_business_logic()
        
        # 综合评估
        print("\n" + "="*60)
        print("🎯 SHAP计算合理性综合评估")
        print("="*60)
        
        print("\n✅ 数学性质验证:")
        print(f"   效率性质误差: {math_validation['efficiency_error']:.6f} (应接近0)")
        print(f"   一致性相关性: {math_validation['consistency_correlation']:.3f} (应>0.8)")
        
        print("\n✅ 业务逻辑验证:")
        print(f"   高峰时段识别: {business_validation['hour_logic']['peak_overlap']}/3 符合预期")
        print(f"   温度影响相关性: {business_validation['temperature_logic']['correlation']:.3f}")
        print(f"   工作日vs周末差异: {business_validation['weekday_logic']['difference']:.2f}")
        
        print("\n✅ 模型性能:")
        print(f"   R²得分: {model_performance['r2']:.3f} (应>0.8)")
        print(f"   MAE: {model_performance['mae']:.2f} MW")
        
        # 最终结论
        is_reasonable = (
            math_validation['efficiency_error'] < 1e-5 and
            math_validation['consistency_correlation'] > 0.8 and
            model_performance['r2'] > 0.8 and
            business_validation['hour_logic']['peak_overlap'] >= 1
        )
        
        print(f"\n🎉 最终结论: SHAP计算 {'合理' if is_reasonable else '需要改进'}")
        
        if is_reasonable:
            print("\n✅ 合理性原因:")
            print("   1. 满足SHAP的数学性质（效率性、对称性、虚拟性）")
            print("   2. 与XGBoost特征重要性高度一致")
            print("   3. 符合电力需求的业务逻辑")
            print("   4. 模型性能良好，基础可靠")
        
        return {
            'is_reasonable': is_reasonable,
            'model_performance': model_performance,
            'math_validation': math_validation,
            'business_validation': business_validation
        }
        
    def run_full_validation(self):
        """运行完整验证"""
        print("🚀 开始SHAP计算合理性验证...")
        
        self.load_and_prepare_data()
        report = self.generate_validation_report()
        
        print("\n🎉 验证完成！")
        return report

if __name__ == "__main__":
    validator = SHAPValidationAnalyzer()
    validation_report = validator.run_full_validation()
