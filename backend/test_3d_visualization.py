#!/usr/bin/env python3
"""
测试3D可视化数据
验证生成的数据是否正确
"""

import json
import numpy as np
import matplotlib.pyplot as plt

def test_3d_data():
    """测试3D数据的正确性"""
    print("🧪 测试3D可视化数据...")
    
    datasets = ['temperature_hour', 'day_of_week_hour', 'week_of_month_hour']
    
    for dataset in datasets:
        print(f"\n📊 测试 {dataset} 数据:")
        
        try:
            with open(f'frontend/public/data/{dataset}_3d.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查数据结构
            print(f"   标题: {data['title']}")
            print(f"   X轴: {data['x_axis']['name']} ({len(data['x_axis']['values'])} 个值)")
            print(f"   Y轴: {data['y_axis']['name']} ({len(data['y_axis']['values'])} 个值)")
            
            # 检查矩阵数据
            power_matrix = np.array(data['z_axis']['power_demand_matrix'])
            shap_matrix = np.array(data['z_axis']['shap_effect_matrix'])
            
            print(f"   电力需求矩阵形状: {power_matrix.shape}")
            print(f"   SHAP效应矩阵形状: {shap_matrix.shape}")
            
            print(f"   电力需求范围: [{power_matrix.min():.1f}, {power_matrix.max():.1f}] MW")
            print(f"   SHAP效应范围: [{shap_matrix.min():.1f}, {shap_matrix.max():.1f}] MW")
            
            # 检查是否有异常值
            if np.any(np.isnan(power_matrix)) or np.any(np.isnan(shap_matrix)):
                print("   ⚠️ 发现NaN值")
            else:
                print("   ✅ 数据完整，无NaN值")
                
            # 检查数据变化范围
            power_range = power_matrix.max() - power_matrix.min()
            shap_range = shap_matrix.max() - shap_matrix.min()
            
            if power_range > 0 and shap_range > 0:
                print("   ✅ 数据有合理的变化范围")
            else:
                print("   ⚠️ 数据变化范围可能过小")
                
        except Exception as e:
            print(f"   ❌ 数据加载失败: {e}")
    
    print("\n🎉 3D数据测试完成！")

def create_quick_visualization():
    """创建快速可视化验证"""
    print("\n🎨 创建快速可视化验证...")
    
    try:
        # 加载Temperature × Hour数据
        with open('frontend/public/data/temperature_hour_3d.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取SHAP效应矩阵
        shap_matrix = np.array(data['z_axis']['shap_effect_matrix'])
        
        # 创建热力图
        plt.figure(figsize=(12, 8))
        
        im = plt.imshow(shap_matrix, cmap='RdYlBu_r', aspect='auto', origin='lower')
        
        # 设置标签
        plt.title('Temperature × Hour SHAP Effect Heatmap\n(Quick Verification)', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Hour of Day')
        plt.ylabel('Temperature (°C)')
        
        # 设置刻度
        x_labels = data['x_axis']['labels']
        y_labels = data['y_axis']['labels']
        
        plt.xticks(range(0, len(x_labels), 4), [x_labels[i] for i in range(0, len(x_labels), 4)])
        plt.yticks(range(len(y_labels)), y_labels)
        
        # 添加颜色条
        cbar = plt.colorbar(im)
        cbar.set_label('SHAP Effect (MW)', fontsize=12)
        
        plt.tight_layout()
        plt.savefig('quick_3d_verification.png', dpi=300, bbox_inches='tight')
        print("   💾 保存验证图片: quick_3d_verification.png")
        plt.show()
        
        # 打印一些关键统计信息
        print(f"\n📈 关键统计信息:")
        print(f"   最大SHAP效应: {shap_matrix.max():.2f} MW")
        print(f"   最小SHAP效应: {shap_matrix.min():.2f} MW")
        print(f"   平均SHAP效应: {shap_matrix.mean():.2f} MW")
        
        # 找出最强效应的位置
        max_idx = np.unravel_index(np.argmax(np.abs(shap_matrix)), shap_matrix.shape)
        max_temp = data['y_axis']['labels'][max_idx[0]]
        max_hour = data['x_axis']['labels'][max_idx[1]]
        max_value = shap_matrix[max_idx]
        
        print(f"   最强效应位置: {max_temp} × {max_hour} = {max_value:.2f} MW")
        
    except Exception as e:
        print(f"   ❌ 可视化创建失败: {e}")

if __name__ == "__main__":
    test_3d_data()
    create_quick_visualization()
