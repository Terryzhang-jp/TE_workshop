"""
验证SHAP计算的正确性
Verify SHAP Calculation Correctness
"""

import pandas as pd
import numpy as np
import json
import shap
import xgboost as xgb
from sklearn.preprocessing import StandardScaler

def verify_shap_calculation():
    """验证SHAP计算的正确性"""
    print("🔍 验证SHAP计算正确性...")
    
    # 1. 重新加载数据和训练模型
    data_path = "/Users/yichuanzhang/Desktop/workshop_TE/backend/data/worst_day_1_2022_01_07_winter_extreme_cold.csv"
    df = pd.read_csv(data_path)
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
    
    feature_columns = ['temp', 'hour', 'day_of_week', 'week_of_month']
    
    # 分离数据
    train_data = df[df['actual_power'].notna()].copy()
    predict_data = df[df['actual_power'].isna()].copy()
    
    # 训练模型
    X_train = train_data[feature_columns].values
    y_train = train_data['actual_power'].values
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    model = xgb.XGBRegressor(
        n_estimators=100, max_depth=6, learning_rate=0.1,
        random_state=42, objective='reg:squarederror'
    )
    model.fit(X_train_scaled, y_train)
    
    # 初始化SHAP
    explainer = shap.TreeExplainer(model, data=X_train_scaled)
    X_predict_scaled = scaler.transform(predict_data[feature_columns].values)
    shap_values = explainer.shap_values(X_predict_scaled)
    
    # 2. 验证SHAP值的加性性质
    print("\n📊 验证SHAP值的加性性质...")
    base_value = explainer.expected_value
    predictions = model.predict(X_predict_scaled)
    
    verification_results = []
    
    for i in range(len(predict_data)):
        shap_sum = np.sum(shap_values[i])
        predicted_value = predictions[i]
        calculated_value = base_value + shap_sum
        
        difference = abs(predicted_value - calculated_value)
        is_correct = difference < 1e-3  # 允许更大的浮点误差（毫瓦级别）
        
        verification_results.append({
            'hour': int(predict_data.iloc[i]['hour']),
            'predicted': float(predicted_value),
            'base_plus_shap': float(calculated_value),
            'difference': float(difference),
            'is_correct': is_correct
        })
        
        if i < 5:  # 显示前5个验证结果
            print(f"   Hour {int(predict_data.iloc[i]['hour']):02d}: "
                  f"Predicted={predicted_value:.2f}, "
                  f"Base+SHAP={calculated_value:.2f}, "
                  f"Diff={difference:.6f}, "
                  f"✓" if is_correct else "✗")
    
    # 3. 验证特征重要性计算
    print("\n📈 验证特征重要性计算...")
    mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
    feature_names = ['Temperature', 'Hour', 'Day_of_Week', 'Week_of_Month']
    
    for i, (feature, importance) in enumerate(zip(feature_names, mean_abs_shap)):
        print(f"   {feature}: {importance:.2f} MW")
    
    # 4. 读取保存的数据进行对比
    print("\n🔄 对比保存的数据...")
    with open('/Users/yichuanzhang/Desktop/workshop_TE/backend/shap_data_complete.json', 'r') as f:
        saved_data = json.load(f)
    
    # 对比特征重要性
    saved_importance = {item['feature']: item['importance'] for item in saved_data['feature_importance']}
    
    print("   特征重要性对比:")
    for i, feature in enumerate(feature_names):
        calculated = mean_abs_shap[i]
        saved = saved_importance[feature]
        diff = abs(calculated - saved)
        print(f"   {feature}: 计算={calculated:.2f}, 保存={saved:.2f}, 差异={diff:.6f}")
    
    # 5. 总体验证结果
    all_correct = all(result['is_correct'] for result in verification_results)
    
    print(f"\n✅ 验证结果:")
    print(f"   • 加性性质验证: {'通过' if all_correct else '失败'}")
    print(f"   • 验证样本数: {len(verification_results)}")
    print(f"   • 最大误差: {max(result['difference'] for result in verification_results):.8f}")
    print(f"   • 基准值: {base_value:.2f} MW")
    
    return all_correct, verification_results

def main():
    """主函数"""
    print("🎯 SHAP计算验证器")
    print("=" * 50)
    
    is_correct, results = verify_shap_calculation()
    
    if is_correct:
        print("\n🎉 SHAP计算完全正确！可以安全使用这些数据。")
    else:
        print("\n⚠️ SHAP计算存在问题，需要检查。")
    
    return is_correct

if __name__ == "__main__":
    main()
