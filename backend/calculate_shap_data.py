"""
Calculate SHAP Data for Visualizations
计算SHAP可视化数据并输出为JSON和CSV格式
"""

import pandas as pd
import numpy as np
import json
import shap
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import lime
import lime.lime_tabular
import warnings
warnings.filterwarnings('ignore')

class SHAPDataCalculator:
    """SHAP数据计算器"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.model = None
        self.scaler = None
        self.explainer = None
        self.shap_values = None
        self.lime_explainer = None
        self.feature_columns = ['temp', 'hour', 'day_of_week', 'week_of_month']
        self.feature_names = ['Temperature', 'Hour', 'Day_of_Week', 'Week_of_Month']
        
    def load_and_prepare_data(self):
        """加载和准备数据"""
        print("📊 加载数据...")
        
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
        
        print(f"✅ 训练数据: {len(self.train_data)} 条")
        print(f"✅ 预测数据: {len(self.predict_data)} 条")
        
        return df
        
    def train_model(self):
        """训练模型"""
        print("🤖 训练XGBoost模型...")
        
        X_train = self.train_data[self.feature_columns].values
        y_train = self.train_data['actual_power'].values
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        self.model = xgb.XGBRegressor(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42, objective='reg:squarederror'
        )
        self.model.fit(X_train_scaled, y_train)
        
        # 计算训练指标
        y_pred = self.model.predict(X_train_scaled)
        mae = mean_absolute_error(y_train, y_pred)
        rmse = np.sqrt(mean_squared_error(y_train, y_pred))
        
        print(f"✅ 模型训练完成 - MAE: {mae:.2f} MW, RMSE: {rmse:.2f} MW")
        
    def initialize_shap(self):
        """初始化SHAP"""
        print("🔍 初始化SHAP分析器...")
        
        X_train_scaled = self.scaler.transform(self.train_data[self.feature_columns].values)
        self.explainer = shap.TreeExplainer(self.model, data=X_train_scaled)
        
        X_predict_scaled = self.scaler.transform(self.predict_data[self.feature_columns].values)
        self.shap_values = self.explainer.shap_values(X_predict_scaled)
        
        print("✅ SHAP分析器初始化完成")

    def initialize_lime(self):
        """初始化LIME分析器"""
        print("🔍 初始化LIME分析器...")

        X_train_scaled = self.scaler.transform(self.train_data[self.feature_columns].values)

        # 创建LIME解释器
        self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            X_train_scaled,
            feature_names=self.feature_names,
            class_names=['Power_Consumption'],
            mode='regression',
            discretize_continuous=False,  # 不离散化连续特征
            random_state=42
        )

        print("✅ LIME分析器初始化完成")
        
    def calculate_feature_importance_data(self):
        """计算特征重要性数据"""
        print("📊 计算特征重要性数据...")
        
        # 计算平均绝对SHAP值
        mean_abs_shap = np.mean(np.abs(self.shap_values), axis=0)
        
        # 创建数据
        importance_data = []
        for i, (feature, importance) in enumerate(zip(self.feature_names, mean_abs_shap)):
            importance_data.append({
                'feature': feature,
                'feature_chinese': ['温度', '小时', '星期', '周数'][i],
                'importance': float(importance),
                'rank': int(np.argsort(mean_abs_shap)[::-1].tolist().index(i) + 1)
            })
        
        # 按重要性排序
        importance_data.sort(key=lambda x: x['importance'], reverse=True)
        
        return importance_data
        
    def calculate_dependence_data(self):
        """使用训练数据计算真正的特征依赖数据"""
        print("📈 计算特征依赖数据...")

        # 对训练数据计算SHAP值
        X_train_scaled = self.scaler.transform(self.train_data[self.feature_columns].values)
        train_shap_values = self.explainer.shap_values(X_train_scaled)

        dependence_data = {}

        # 为每个特征计算dependence数据
        for feature_idx, (feature_name, feature_chinese) in enumerate(zip(self.feature_names, ['温度', '小时', '星期', '周数'])):
            print(f"   计算 {feature_chinese} 的依赖数据...")

            # 提取该特征的值和对应的SHAP值
            feature_values = self.train_data[self.feature_columns[feature_idx]].values
            shap_values = train_shap_values[:, feature_idx]

            # 创建数据点
            feature_data = []
            for i, (feat_val, shap_val) in enumerate(zip(feature_values, shap_values)):
                feature_data.append({
                    'feature_value': float(feat_val),
                    'shap_value': float(shap_val),
                    'sample_index': i
                })

            # 按特征值排序
            feature_data.sort(key=lambda x: x['feature_value'])

            dependence_data[feature_name] = {
                'feature': feature_name,
                'feature_chinese': feature_chinese,
                'data_points': feature_data,
                'value_range': {
                    'min': float(np.min(feature_values)),
                    'max': float(np.max(feature_values))
                },
                'shap_range': {
                    'min': float(np.min(shap_values)),
                    'max': float(np.max(shap_values))
                },
                'total_points': len(feature_data),
                'unique_values': len(np.unique(feature_values))
            }

        return dependence_data

    def calculate_lime_data(self):
        """计算每个小时的LIME解释"""
        print("🍋 计算LIME解释数据...")

        lime_data = {
            'hourly_explanations': [],
            'feature_importance_by_hour': {},
            'summary': {
                'total_hours': len(self.predict_data),
                'features': self.feature_names,
                'features_chinese': ['温度', '小时', '星期', '周数']
            }
        }

        # 为每个预测小时生成LIME解释
        for i, row in self.predict_data.iterrows():
            hour_idx = i - self.predict_data.index[0]
            hour = int(row['hour'])

            print(f"   计算 {hour}:00 的LIME解释...")

            # 准备实例数据
            instance = self.predict_data[self.feature_columns].iloc[hour_idx].values
            instance_scaled = self.scaler.transform([instance])[0]

            # 获取模型预测
            prediction = self.model.predict([instance_scaled])[0]

            # 生成LIME解释
            explanation = self.lime_explainer.explain_instance(
                instance_scaled,
                self.model.predict,
                num_features=len(self.feature_names),
                num_samples=1000
            )

            # 提取特征贡献
            feature_contributions = {}
            explanation_list = explanation.as_list()
            explanation_map = explanation.as_map()

            # 获取局部预测值和截距
            local_pred = explanation.local_pred[0] if hasattr(explanation, 'local_pred') else prediction
            intercept = explanation.intercept[0] if hasattr(explanation, 'intercept') else 0

            for feature_idx, (feature_name, feature_chinese) in enumerate(zip(self.feature_names, ['温度', '小时', '星期', '周数'])):
                # 从LIME解释中获取该特征的贡献
                lime_contribution = 0

                # 方法1: 使用as_map()获取特征贡献
                if 1 in explanation_map:  # 回归任务通常使用类别1
                    for feat_idx, contribution in explanation_map[1]:
                        if feat_idx == feature_idx:
                            lime_contribution = contribution
                            break

                # 方法2: 如果as_map()没有结果，使用as_list()
                if lime_contribution == 0:
                    for feature_desc, contribution in explanation_list:
                        if feature_name in feature_desc or f"feature_{feature_idx}" in feature_desc:
                            lime_contribution = contribution
                            break

                feature_contributions[feature_name] = {
                    'contribution': float(lime_contribution),
                    'feature_value': float(instance[feature_idx]),
                    'feature_chinese': feature_chinese
                }

            # 按贡献度排序
            sorted_contributions = sorted(
                feature_contributions.items(),
                key=lambda x: abs(x[1]['contribution']),
                reverse=True
            )

            hour_explanation = {
                'hour': hour,
                'time': row['time'].strftime('%H:%M'),
                'prediction': float(prediction),
                'feature_contributions': feature_contributions,
                'sorted_contributions': [
                    {
                        'feature': item[0],
                        'feature_chinese': item[1]['feature_chinese'],
                        'contribution': item[1]['contribution'],
                        'feature_value': item[1]['feature_value'],
                        'abs_contribution': abs(item[1]['contribution'])
                    }
                    for item in sorted_contributions
                ],
                'explanation_text': self._generate_lime_explanation_text(sorted_contributions, hour)
            }

            lime_data['hourly_explanations'].append(hour_explanation)

        # 计算每个特征在不同小时的重要性变化
        for feature_name in self.feature_names:
            lime_data['feature_importance_by_hour'][feature_name] = [
                exp['feature_contributions'][feature_name]['contribution']
                for exp in lime_data['hourly_explanations']
            ]

        return lime_data

    def _generate_lime_explanation_text(self, sorted_contributions, hour):
        """生成LIME解释文本"""
        if not sorted_contributions:
            return f"{hour}:00 - 无法生成解释"

        top_positive = None
        top_negative = None

        for feature, data in sorted_contributions:
            if data['contribution'] > 0 and top_positive is None:
                top_positive = (feature, data)
            elif data['contribution'] < 0 and top_negative is None:
                top_negative = (feature, data)

            if top_positive and top_negative:
                break

        explanation_parts = [f"{hour}:00时刻"]

        if top_positive:
            explanation_parts.append(
                f"{top_positive[1]['feature_chinese']}最大程度增加用电需求(+{top_positive[1]['contribution']:.1f})"
            )

        if top_negative:
            explanation_parts.append(
                f"{top_negative[1]['feature_chinese']}最大程度减少用电需求({top_negative[1]['contribution']:.1f})"
            )

        return "，".join(explanation_parts)
        
    def calculate_all_data(self):
        """计算SHAP和LIME数据"""
        print("🚀 开始计算SHAP和LIME数据...")

        # 准备数据和模型
        self.load_and_prepare_data()
        self.train_model()
        self.initialize_shap()
        self.initialize_lime()

        # 计算核心数据
        all_data = {
            'metadata': {
                'date': '2022-01-07',
                'description': 'SHAP and LIME analysis for January 7th power prediction',
                'features': self.feature_names,
                'features_chinese': ['温度', '小时', '星期', '周数'],
                'base_prediction': float(self.explainer.expected_value),
                'total_hours': len(self.predict_data)
            },
            'shap_analysis': {
                'feature_importance': self.calculate_feature_importance_data(),
                'feature_dependence': self.calculate_dependence_data()
            },
            'lime_analysis': self.calculate_lime_data()
        }

        return all_data
        
    def save_data(self, data, output_dir='/Users/yichuanzhang/Desktop/workshop_TE/backend/'):
        """保存数据为JSON和CSV格式"""
        print("💾 保存数据...")

        # 保存完整JSON
        json_path = f"{output_dir}shap_data_complete.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 完整JSON数据已保存: {json_path}")

        # 保存各部分CSV
        # 1. SHAP特征重要性
        importance_df = pd.DataFrame(data['shap_analysis']['feature_importance'])
        importance_csv = f"{output_dir}shap_feature_importance.csv"
        importance_df.to_csv(importance_csv, index=False, encoding='utf-8')
        print(f"✅ SHAP特征重要性CSV已保存: {importance_csv}")

        # 2. SHAP特征依赖数据 - 为每个特征保存单独的CSV
        dependence_csvs = {}
        for feature_name, feature_data in data['shap_analysis']['feature_dependence'].items():
            # 展开数据点
            dependence_df = pd.DataFrame(feature_data['data_points'])
            dependence_df['feature_name'] = feature_name
            dependence_df['feature_chinese'] = feature_data['feature_chinese']

            dependence_csv = f"{output_dir}shap_dependence_{feature_name.lower()}.csv"
            dependence_df.to_csv(dependence_csv, index=False, encoding='utf-8')
            dependence_csvs[feature_name] = dependence_csv
            print(f"✅ SHAP {feature_data['feature_chinese']}依赖CSV已保存: {dependence_csv}")

        # 3. LIME小时解释数据
        lime_hourly_df = pd.DataFrame(data['lime_analysis']['hourly_explanations'])
        lime_hourly_csv = f"{output_dir}lime_hourly_explanations.csv"
        lime_hourly_df.to_csv(lime_hourly_csv, index=False, encoding='utf-8')
        print(f"✅ LIME小时解释CSV已保存: {lime_hourly_csv}")

        # 4. LIME特征重要性时间序列
        lime_importance_data = []
        for hour_data in data['lime_analysis']['hourly_explanations']:
            for feature_name, contrib_data in hour_data['feature_contributions'].items():
                lime_importance_data.append({
                    'hour': hour_data['hour'],
                    'time': hour_data['time'],
                    'feature': feature_name,
                    'feature_chinese': contrib_data['feature_chinese'],
                    'contribution': contrib_data['contribution'],
                    'feature_value': contrib_data['feature_value']
                })

        lime_importance_df = pd.DataFrame(lime_importance_data)
        lime_importance_csv = f"{output_dir}lime_feature_importance_by_hour.csv"
        lime_importance_df.to_csv(lime_importance_csv, index=False, encoding='utf-8')
        print(f"✅ LIME特征重要性时间序列CSV已保存: {lime_importance_csv}")

        return {
            'json': json_path,
            'csvs': {
                'shap_feature_importance': importance_csv,
                'shap_dependence': dependence_csvs,
                'lime_hourly_explanations': lime_hourly_csv,
                'lime_feature_importance_by_hour': lime_importance_csv
            }
        }

def main():
    """主函数"""
    print("🎯 SHAP数据计算器")
    print("=" * 50)
    
    # 初始化计算器
    data_path = "/Users/yichuanzhang/Desktop/workshop_TE/backend/data/worst_day_1_2022_01_07_winter_extreme_cold.csv"
    calculator = SHAPDataCalculator(data_path)
    
    # 计算所有数据
    all_data = calculator.calculate_all_data()
    
    # 保存数据
    file_paths = calculator.save_data(all_data)
    
    print("\n🎉 SHAP和LIME数据计算完成！")
    print("📁 生成的文件:")
    print(f"   📄 完整JSON: {file_paths['json']}")
    print("   📊 CSV文件:")
    print(f"      • SHAP特征重要性: {file_paths['csvs']['shap_feature_importance']}")
    for feature_name, path in file_paths['csvs']['shap_dependence'].items():
        print(f"      • SHAP {feature_name}依赖: {path}")
    print(f"      • LIME小时解释: {file_paths['csvs']['lime_hourly_explanations']}")
    print(f"      • LIME特征重要性时间序列: {file_paths['csvs']['lime_feature_importance_by_hour']}")

    # 显示数据摘要
    print(f"\n📈 数据摘要:")
    print(f"   🔍 SHAP分析:")
    print(f"     • 特征重要性: {len(all_data['shap_analysis']['feature_importance'])} 个特征")
    print(f"     • 特征依赖: {len(all_data['shap_analysis']['feature_dependence'])} 个特征")
    for feature_name, feature_data in all_data['shap_analysis']['feature_dependence'].items():
        print(f"       - {feature_data['feature_chinese']}: {feature_data['total_points']} 个数据点")

    print(f"   🍋 LIME分析:")
    print(f"     • 小时解释: {len(all_data['lime_analysis']['hourly_explanations'])} 个小时")
    print(f"     • 每小时特征贡献: {len(all_data['lime_analysis']['feature_importance_by_hour'])} 个特征")

if __name__ == "__main__":
    main()
