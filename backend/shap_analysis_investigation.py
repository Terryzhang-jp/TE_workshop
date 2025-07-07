"""
SHAP Analysis Investigation
Deep-dive analysis of SHAP computations and temperature importance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.inspection import permutation_importance
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

class SHAPInvestigator:
    """SHAP分析调查器"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.feature_columns = ['temp', 'hour', 'day_of_week', 'week_of_month']
        self.feature_names = ['Temperature', 'Hour', 'Day_of_Week', 'Week_of_Month']
        
        # 存储分析结果
        self.data = None
        self.train_data = None
        self.predict_data = None
        self.model = None
        self.scaler = None
        self.explainer = None
        self.shap_values = None
        
    def load_and_prepare_data(self):
        """加载和准备数据"""
        print("📊 Loading and preparing data...")
        
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
        self.predict_data = df[df['actual_power'].isna()].copy()
        self.data = df
        
        print(f"✅ Training data: {len(self.train_data)} samples")
        print(f"✅ Prediction data: {len(self.predict_data)} samples")
        
        return df
    
    def analyze_data_characteristics(self):
        """分析数据特征"""
        print("\n" + "="*60)
        print("📈 DATA CHARACTERISTICS ANALYSIS")
        print("="*60)
        
        # 基本统计信息
        print("\n1. FEATURE STATISTICS:")
        for feature in self.feature_columns:
            feature_name = self.feature_names[self.feature_columns.index(feature)]
            train_stats = self.train_data[feature].describe()
            
            print(f"\n{feature_name} ({feature}):")
            print(f"  Mean: {train_stats['mean']:.3f}")
            print(f"  Std:  {train_stats['std']:.3f}")
            print(f"  Min:  {train_stats['min']:.3f}")
            print(f"  Max:  {train_stats['max']:.3f}")
            print(f"  Range: {train_stats['max'] - train_stats['min']:.3f}")
            print(f"  Unique values: {self.train_data[feature].nunique()}")
        
        # 目标变量统计
        print(f"\nTarget Variable (actual_power):")
        target_stats = self.train_data['actual_power'].describe()
        print(f"  Mean: {target_stats['mean']:.3f} MW")
        print(f"  Std:  {target_stats['std']:.3f} MW")
        print(f"  Min:  {target_stats['min']:.3f} MW")
        print(f"  Max:  {target_stats['max']:.3f} MW")
        print(f"  Range: {target_stats['max'] - target_stats['min']:.3f} MW")
        
        # 相关性分析
        print("\n2. CORRELATION ANALYSIS:")
        correlations = {}
        for feature in self.feature_columns:
            feature_name = self.feature_names[self.feature_columns.index(feature)]
            pearson_corr, pearson_p = pearsonr(self.train_data[feature], self.train_data['actual_power'])
            spearman_corr, spearman_p = spearmanr(self.train_data[feature], self.train_data['actual_power'])
            
            correlations[feature_name] = {
                'pearson': pearson_corr,
                'spearman': spearman_corr,
                'pearson_p': pearson_p,
                'spearman_p': spearman_p
            }
            
            print(f"\n{feature_name}:")
            print(f"  Pearson correlation:  {pearson_corr:.4f} (p={pearson_p:.4f})")
            print(f"  Spearman correlation: {spearman_corr:.4f} (p={spearman_p:.4f})")
        
        return correlations
    
    def train_model_and_compute_shap(self):
        """训练模型并计算SHAP值"""
        print("\n" + "="*60)
        print("🤖 MODEL TRAINING AND SHAP COMPUTATION")
        print("="*60)
        
        # 准备训练数据
        X_train = self.train_data[self.feature_columns].values
        y_train = self.train_data['actual_power'].values
        
        # 特征缩放
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # 训练模型
        self.model = xgb.XGBRegressor(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42, objective='reg:squarederror'
        )
        self.model.fit(X_train_scaled, y_train)
        
        # 模型性能
        y_pred = self.model.predict(X_train_scaled)
        mae = mean_absolute_error(y_train, y_pred)
        rmse = np.sqrt(mean_squared_error(y_train, y_pred))
        r2 = self.model.score(X_train_scaled, y_train)
        
        print(f"\nModel Performance:")
        print(f"  MAE:  {mae:.2f} MW")
        print(f"  RMSE: {rmse:.2f} MW")
        print(f"  R²:   {r2:.4f}")
        
        # XGBoost内置特征重要性
        print(f"\nXGBoost Built-in Feature Importance:")
        xgb_importance = self.model.feature_importances_
        for i, feature_name in enumerate(self.feature_names):
            print(f"  {feature_name}: {xgb_importance[i]:.4f}")
        
        # 初始化SHAP
        print(f"\nInitializing SHAP TreeExplainer...")
        self.explainer = shap.TreeExplainer(self.model, data=X_train_scaled)
        
        # 计算预测数据的SHAP值
        X_predict_scaled = self.scaler.transform(self.predict_data[self.feature_columns].values)
        self.shap_values = self.explainer.shap_values(X_predict_scaled)
        
        print(f"✅ SHAP values computed for {len(self.shap_values)} prediction samples")
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'xgb_importance': xgb_importance
        }
    
    def compute_alternative_importance(self):
        """计算替代特征重要性方法"""
        print("\n" + "="*60)
        print("🔄 ALTERNATIVE FEATURE IMPORTANCE METHODS")
        print("="*60)
        
        X_train = self.train_data[self.feature_columns].values
        y_train = self.train_data['actual_power'].values
        X_train_scaled = self.scaler.transform(X_train)
        
        # 1. Permutation Importance
        print("\n1. Permutation Importance:")
        perm_importance = permutation_importance(
            self.model, X_train_scaled, y_train, 
            n_repeats=10, random_state=42, scoring='neg_mean_absolute_error'
        )
        
        for i, feature_name in enumerate(self.feature_names):
            mean_imp = perm_importance.importances_mean[i]
            std_imp = perm_importance.importances_std[i]
            print(f"  {feature_name}: {mean_imp:.4f} ± {std_imp:.4f}")
        
        # 2. SHAP Feature Importance (mean absolute SHAP values)
        print("\n2. SHAP Feature Importance (Mean |SHAP|):")
        shap_importance = np.mean(np.abs(self.shap_values), axis=0)
        for i, feature_name in enumerate(self.feature_names):
            print(f"  {feature_name}: {shap_importance[i]:.4f}")
        
        return {
            'permutation': perm_importance.importances_mean,
            'shap_mean_abs': shap_importance
        }

    def investigate_temperature_importance(self):
        """深入调查温度重要性"""
        print("\n" + "="*60)
        print("🌡️  TEMPERATURE IMPORTANCE INVESTIGATION")
        print("="*60)

        # 1. 温度变化范围分析
        temp_range = self.train_data['temp'].max() - self.train_data['temp'].min()
        temp_std = self.train_data['temp'].std()

        print(f"\n1. Temperature Variation Analysis:")
        print(f"  Temperature range: {temp_range:.2f}°C")
        print(f"  Temperature std: {temp_std:.2f}°C")
        print(f"  Coefficient of variation: {temp_std/self.train_data['temp'].mean():.4f}")

        # 2. 检查是否存在特征泄漏或代理变量
        print(f"\n2. Feature Correlation Matrix:")
        feature_corr = self.train_data[self.feature_columns].corr()
        print(feature_corr.round(4))

        # 3. 分析温度与其他特征的交互
        print(f"\n3. Temperature Interaction Analysis:")

        # 按小时分组的温度变化
        temp_by_hour = self.train_data.groupby('hour')['temp'].agg(['mean', 'std', 'min', 'max'])
        print(f"\nTemperature variation by hour:")
        print(f"  Hour with highest temp variation (std): {temp_by_hour['std'].idxmax()} (std={temp_by_hour['std'].max():.2f})")
        print(f"  Hour with lowest temp variation (std): {temp_by_hour['std'].idxmin()} (std={temp_by_hour['std'].min():.2f})")

        # 按星期分组的温度变化
        temp_by_dow = self.train_data.groupby('day_of_week')['temp'].agg(['mean', 'std', 'min', 'max'])
        print(f"\nTemperature variation by day of week:")
        print(f"  Day with highest temp variation (std): {temp_by_dow['std'].idxmax()} (std={temp_by_dow['std'].max():.2f})")

        # 4. 计算温度对电力的边际效应
        print(f"\n4. Temperature Marginal Effect Analysis:")

        # 简单线性回归系数
        from sklearn.linear_model import LinearRegression
        temp_model = LinearRegression()
        temp_model.fit(self.train_data[['temp']], self.train_data['actual_power'])
        temp_coef = temp_model.coef_[0]
        temp_r2 = temp_model.score(self.train_data[['temp']], self.train_data['actual_power'])

        print(f"  Linear regression coefficient: {temp_coef:.2f} MW/°C")
        print(f"  Temperature-only model R²: {temp_r2:.4f}")

        # 5. 检查数据时间范围和季节性
        print(f"\n5. Temporal Analysis:")
        date_range = self.train_data['time'].max() - self.train_data['time'].min()
        print(f"  Data time range: {date_range.days} days")
        print(f"  Start date: {self.train_data['time'].min()}")
        print(f"  End date: {self.train_data['time'].max()}")

        # 检查是否是冬季数据（温度变化可能有限）
        avg_temp = self.train_data['temp'].mean()
        if avg_temp < 15:
            print(f"  ⚠️  Data appears to be winter period (avg temp: {avg_temp:.1f}°C)")
            print(f"      Limited temperature variation may reduce its predictive importance")

        return {
            'temp_range': temp_range,
            'temp_std': temp_std,
            'temp_coef': temp_coef,
            'temp_r2': temp_r2,
            'avg_temp': avg_temp,
            'feature_corr': feature_corr
        }

    def generate_comprehensive_report(self):
        """生成综合分析报告"""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE SHAP ANALYSIS REPORT")
        print("="*80)

        # 执行所有分析
        self.load_and_prepare_data()
        correlations = self.analyze_data_characteristics()
        model_results = self.train_model_and_compute_shap()
        alt_importance = self.compute_alternative_importance()
        temp_analysis = self.investigate_temperature_importance()

        # 生成报告
        print("\n" + "="*60)
        print("🎯 EXECUTIVE SUMMARY")
        print("="*60)

        print(f"\n1. MODEL PERFORMANCE:")
        print(f"   - R² Score: {model_results['r2']:.4f}")
        print(f"   - RMSE: {model_results['rmse']:.2f} MW")
        print(f"   - MAE: {model_results['mae']:.2f} MW")

        print(f"\n2. FEATURE IMPORTANCE COMPARISON:")
        print(f"   Method                    Temp    Hour    DoW     WoM")
        print(f"   XGBoost Built-in:        {model_results['xgb_importance'][0]:.3f}   {model_results['xgb_importance'][1]:.3f}   {model_results['xgb_importance'][2]:.3f}   {model_results['xgb_importance'][3]:.3f}")
        print(f"   Permutation Importance:  {alt_importance['permutation'][0]:.3f}   {alt_importance['permutation'][1]:.3f}   {alt_importance['permutation'][2]:.3f}   {alt_importance['permutation'][3]:.3f}")
        print(f"   SHAP Mean |values|:      {alt_importance['shap_mean_abs'][0]:.3f}   {alt_importance['shap_mean_abs'][1]:.3f}   {alt_importance['shap_mean_abs'][2]:.3f}   {alt_importance['shap_mean_abs'][3]:.3f}")

        print(f"\n3. TEMPERATURE ANALYSIS FINDINGS:")
        print(f"   - Temperature range: {temp_analysis['temp_range']:.2f}°C")
        print(f"   - Average temperature: {temp_analysis['avg_temp']:.1f}°C")
        print(f"   - Linear effect: {temp_analysis['temp_coef']:.2f} MW/°C")
        print(f"   - Temperature-only R²: {temp_analysis['temp_r2']:.4f}")

        print(f"\n4. CORRELATION WITH TARGET:")
        for feature in self.feature_columns:
            feature_name = self.feature_names[self.feature_columns.index(feature)]
            corr = correlations[feature_name]['pearson']
            print(f"   {feature_name}: {corr:.4f}")

        # 分析结论
        print(f"\n" + "="*60)
        print("🔍 ANALYSIS CONCLUSIONS")
        print("="*60)

        if temp_analysis['avg_temp'] < 15 and temp_analysis['temp_range'] < 20:
            print(f"\n⚠️  TEMPERATURE LOW IMPORTANCE EXPLANATION:")
            print(f"   1. LIMITED VARIATION: Temperature range is only {temp_analysis['temp_range']:.1f}°C")
            print(f"   2. WINTER PERIOD: Data is from winter (avg {temp_analysis['avg_temp']:.1f}°C)")
            print(f"   3. TEMPORAL DOMINANCE: Hour and day patterns capture most variation")
            print(f"   4. PROXY EFFECTS: Time features may capture temperature patterns")

        return {
            'correlations': correlations,
            'model_results': model_results,
            'alt_importance': alt_importance,
            'temp_analysis': temp_analysis
        }

def main():
    """主函数"""
    data_path = "/Users/yichuanzhang/Desktop/workshop_TE/backend/data/worst_day_1_2022_01_07_winter_extreme_cold.csv"

    investigator = SHAPInvestigator(data_path)
    results = investigator.generate_comprehensive_report()

    print(f"\n✅ Analysis complete! Results saved in memory.")
    return results

if __name__ == "__main__":
    results = main()
