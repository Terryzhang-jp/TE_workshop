#!/usr/bin/env python3
"""
创建3D可视化演示
展示Temperature × Hour, Day of Week × Hour, Week of Month × Hour的3D效果
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ThreeDVisualizationDemo:
    def __init__(self):
        self.data = {}
        
    def load_3d_data(self):
        """加载3D数据"""
        print("📂 加载3D可视化数据...")
        
        datasets = ['temperature_hour', 'day_of_week_hour', 'week_of_month_hour']
        
        for dataset in datasets:
            try:
                with open(f'frontend/public/data/{dataset}_3d.json', 'r', encoding='utf-8') as f:
                    self.data[dataset] = json.load(f)
                print(f"   ✅ {dataset} 数据加载成功")
            except Exception as e:
                print(f"   ❌ {dataset} 数据加载失败: {e}")
        
    def create_3d_surface_plot(self, dataset_key, data_type='power_demand'):
        """创建3D表面图"""
        if dataset_key not in self.data:
            print(f"数据集 {dataset_key} 不存在")
            return
            
        data = self.data[dataset_key]
        
        # 获取数据
        if data_type == 'power_demand':
            matrix = np.array(data['z_axis']['power_demand_matrix'])
            title_suffix = "Power Demand"
            z_label = "Power Demand (MW)"
        else:
            matrix = np.array(data['z_axis']['shap_effect_matrix'])
            title_suffix = "SHAP Effect"
            z_label = "SHAP Effect (MW)"
        
        # 创建网格
        x_values = np.array(data['x_axis']['values'])
        y_values = np.array(data['y_axis']['values'])
        X, Y = np.meshgrid(x_values, y_values)
        
        # 创建3D图
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 绘制表面
        surf = ax.plot_surface(X, Y, matrix, cmap='viridis', alpha=0.8, 
                              linewidth=0, antialiased=True)
        
        # 设置标签
        ax.set_xlabel(data['x_axis']['name'], fontsize=12)
        ax.set_ylabel(data['y_axis']['name'], fontsize=12)
        ax.set_zlabel(z_label, fontsize=12)
        ax.set_title(f"{data['title']} - {title_suffix}", fontsize=14, fontweight='bold', pad=20)
        
        # 设置刻度标签
        if len(data['x_axis']['labels']) <= 24:  # 小时数据
            ax.set_xticks(x_values[::4])  # 每4小时显示一次
            ax.set_xticklabels([data['x_axis']['labels'][i] for i in range(0, len(x_values), 4)])
        else:
            ax.set_xticks(x_values)
            ax.set_xticklabels(data['x_axis']['labels'])
            
        ax.set_yticks(y_values)
        ax.set_yticklabels(data['y_axis']['labels'])
        
        # 添加颜色条
        fig.colorbar(surf, shrink=0.5, aspect=20)
        
        # 设置视角
        ax.view_init(elev=30, azim=45)
        
        plt.tight_layout()
        
        # 保存图片
        filename = f'3d_{dataset_key}_{data_type}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"   💾 保存图片: {filename}")
        plt.show()
        
    def create_heatmap_comparison(self):
        """创建热力图对比"""
        print("🗺️ 创建热力图对比...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('3D Power Demand Analysis - Heatmap Comparison', fontsize=16, fontweight='bold')
        
        datasets = ['temperature_hour', 'day_of_week_hour', 'week_of_month_hour']
        data_types = ['power_demand_matrix', 'shap_effect_matrix']
        
        for i, data_type in enumerate(data_types):
            for j, dataset in enumerate(datasets):
                if dataset not in self.data:
                    continue
                    
                ax = axes[i, j]
                data = self.data[dataset]
                matrix = np.array(data['z_axis'][data_type])
                
                # 创建热力图
                im = ax.imshow(matrix, cmap='RdYlBu_r', aspect='auto', origin='lower')
                
                # 设置标题
                title_type = "Power Demand" if data_type == 'power_demand_matrix' else "SHAP Effect"
                ax.set_title(f"{data['title']}\n{title_type}", fontsize=12, fontweight='bold')
                
                # 设置坐标轴
                x_labels = data['x_axis']['labels']
                y_labels = data['y_axis']['labels']
                
                # X轴 (小时)
                if len(x_labels) == 24:  # 小时数据
                    x_ticks = range(0, len(x_labels), 4)
                    ax.set_xticks(x_ticks)
                    ax.set_xticklabels([x_labels[i] for i in x_ticks], rotation=45)
                else:
                    ax.set_xticks(range(len(x_labels)))
                    ax.set_xticklabels(x_labels, rotation=45)
                
                # Y轴
                ax.set_yticks(range(len(y_labels)))
                ax.set_yticklabels(y_labels)
                
                ax.set_xlabel(data['x_axis']['name'])
                ax.set_ylabel(data['y_axis']['name'])
                
                # 添加颜色条
                plt.colorbar(im, ax=ax, shrink=0.8)
        
        plt.tight_layout()
        plt.savefig('3d_heatmap_comparison.png', dpi=300, bbox_inches='tight')
        print("   💾 保存图片: 3d_heatmap_comparison.png")
        plt.show()
        
    def analyze_key_patterns(self):
        """分析关键模式"""
        print("🔍 分析关键模式...")
        
        for dataset_key, data in self.data.items():
            print(f"\n📊 {data['title']} 分析:")
            
            matrix = np.array(data['z_axis']['power_demand_matrix'])
            
            # 找出最高和最低需求
            max_idx = np.unravel_index(np.argmax(matrix), matrix.shape)
            min_idx = np.unravel_index(np.argmin(matrix), matrix.shape)
            
            max_x = data['x_axis']['labels'][max_idx[1]]
            max_y = data['y_axis']['labels'][max_idx[0]]
            max_value = matrix[max_idx]
            
            min_x = data['x_axis']['labels'][min_idx[1]]
            min_y = data['y_axis']['labels'][min_idx[0]]
            min_value = matrix[min_idx]
            
            print(f"   🔥 最高需求: {max_value:.1f} MW at {max_y} × {max_x}")
            print(f"   ❄️ 最低需求: {min_value:.1f} MW at {min_y} × {min_x}")
            
            # 计算平均值和变化范围
            avg_demand = np.mean(matrix)
            demand_range = np.max(matrix) - np.min(matrix)
            
            print(f"   📈 平均需求: {avg_demand:.1f} MW")
            print(f"   📊 需求范围: {demand_range:.1f} MW")
            
            # 分析SHAP效应
            shap_matrix = np.array(data['z_axis']['shap_effect_matrix'])
            max_shap_idx = np.unravel_index(np.argmax(np.abs(shap_matrix)), shap_matrix.shape)
            max_shap_x = data['x_axis']['labels'][max_shap_idx[1]]
            max_shap_y = data['y_axis']['labels'][max_shap_idx[0]]
            max_shap_value = shap_matrix[max_shap_idx]
            
            print(f"   ⚡ 最强SHAP效应: {max_shap_value:.1f} MW at {max_shap_y} × {max_shap_x}")
        
    def run_demo(self):
        """运行完整演示"""
        print("🚀 开始3D可视化演示...")
        
        # 1. 加载数据
        self.load_3d_data()
        
        if not self.data:
            print("❌ 没有可用的数据，请先运行数据生成脚本")
            return
        
        # 2. 分析关键模式
        self.analyze_key_patterns()
        
        # 3. 创建热力图对比
        self.create_heatmap_comparison()
        
        # 4. 创建3D表面图
        for dataset in self.data.keys():
            print(f"\n🏔️ 创建 {dataset} 的3D表面图...")
            self.create_3d_surface_plot(dataset, 'power_demand')
            self.create_3d_surface_plot(dataset, 'shap_effect')
        
        print("\n🎉 3D可视化演示完成！")
        print("📁 生成的图片文件:")
        print("   • 3d_heatmap_comparison.png - 热力图对比")
        print("   • 3d_*_power_demand.png - 电力需求3D图")
        print("   • 3d_*_shap_effect.png - SHAP效应3D图")

if __name__ == "__main__":
    demo = ThreeDVisualizationDemo()
    demo.run_demo()
