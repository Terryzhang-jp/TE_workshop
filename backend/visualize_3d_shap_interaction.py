#!/usr/bin/env python3
"""
可视化3D SHAP交互效应
展示气温×小时的联合影响
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class SHAP3DVisualizer:
    def __init__(self):
        self.data = None
        
    def load_data(self):
        """加载3D交互数据"""
        print("📂 加载3D交互数据...")
        
        with open('frontend/public/data/shap_3d_temperature_hour_interaction.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        print("✅ 数据加载完成")
        
    def plot_interaction_heatmap(self):
        """绘制交互热力图"""
        print("🗺️ 绘制交互热力图...")
        
        matrix_data = self.data['interaction_matrix']
        matrix = np.array(matrix_data['matrix'])
        temp_range = matrix_data['temperature_range']
        hour_range = matrix_data['hour_range']
        
        plt.figure(figsize=(14, 8))
        
        # 创建热力图
        im = plt.imshow(matrix, cmap='RdYlBu_r', aspect='auto', origin='lower')
        
        # 设置坐标轴
        plt.xticks(range(len(hour_range)), [f'{h:02d}:00' for h in hour_range], rotation=45)
        plt.yticks(range(len(temp_range)), [f'{t}°C' for t in temp_range])
        
        # 添加颜色条
        cbar = plt.colorbar(im, shrink=0.8)
        cbar.set_label('SHAP Joint Effect (MW)', fontsize=12)
        
        # 标题和标签
        plt.title('Temperature × Hour SHAP Interaction Heatmap\n气温×小时的SHAP交互效应热力图', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Hour of Day (小时)', fontsize=12)
        plt.ylabel('Temperature (°C) (温度)', fontsize=12)
        
        # 添加网格
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('shap_3d_interaction_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_key_scenarios(self):
        """绘制关键场景对比"""
        print("📊 绘制关键场景对比...")
        
        scenarios = self.data['key_scenarios']
        
        # 创建子图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 场景1：同温度不同时间
        cold_scenario = scenarios[0]
        evening = cold_scenario['evening_20h']
        afternoon = cold_scenario['afternoon_13h']
        
        times = ['晚上8点\n(20:00)', '下午1点\n(13:00)']
        joint_effects = [evening['joint_effect'], afternoon['joint_effect']]
        temp_effects = [evening['temp_shap'], afternoon['temp_shap']]
        hour_effects = [evening['hour_shap'], afternoon['hour_shap']]
        
        x = np.arange(len(times))
        width = 0.25
        
        ax1.bar(x - width, temp_effects, width, label='Temperature Effect', color='#FF6B6B', alpha=0.8)
        ax1.bar(x, hour_effects, width, label='Hour Effect', color='#4ECDC4', alpha=0.8)
        ax1.bar(x + width, joint_effects, width, label='Joint Effect', color='#45B7D1', alpha=0.8)
        
        ax1.set_title(f'{cold_scenario["description"]}\n同样是-1°C在不同时间的影响', fontweight='bold')
        ax1.set_ylabel('SHAP Value (MW)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(times)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 添加数值标签
        for i, (temp, hour, joint) in enumerate(zip(temp_effects, hour_effects, joint_effects)):
            ax1.text(i - width, temp + 5, f'{temp:.1f}', ha='center', va='bottom', fontsize=10)
            ax1.text(i, hour + 5, f'{hour:.1f}', ha='center', va='bottom', fontsize=10)
            ax1.text(i + width, joint + 5, f'{joint:.1f}', ha='center', va='bottom', fontsize=10)
        
        # 场景2：不同温度同时间
        temp_scenario = scenarios[1]
        comparisons = temp_scenario['comparisons']
        
        temperatures = [comp['temperature'] for comp in comparisons]
        temp_shaps = [comp['temp_shap'] for comp in comparisons]
        joint_effects_temp = [comp['joint_effect'] for comp in comparisons]
        
        ax2.plot(temperatures, temp_shaps, 'o-', linewidth=3, markersize=8, 
                label='Temperature SHAP', color='#FF6B6B')
        ax2.plot(temperatures, joint_effects_temp, 's-', linewidth=3, markersize=8, 
                label='Joint Effect', color='#45B7D1')
        
        ax2.set_title('Different Temperatures at 20:00\n晚上8点不同温度的影响', fontweight='bold')
        ax2.set_xlabel('Temperature (°C)')
        ax2.set_ylabel('SHAP Value (MW)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 添加数值标签
        for temp, temp_shap, joint in zip(temperatures, temp_shaps, joint_effects_temp):
            ax2.annotate(f'{temp_shap:.1f}', (temp, temp_shap), 
                        textcoords="offset points", xytext=(0,10), ha='center')
            ax2.annotate(f'{joint:.1f}', (temp, joint), 
                        textcoords="offset points", xytext=(0,10), ha='center')
        
        plt.tight_layout()
        plt.savefig('shap_key_scenarios.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_insights_summary(self):
        """绘制洞察总结"""
        print("💡 绘制洞察总结...")
        
        insights = self.data['insights']
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 最强效应
        strongest = insights[0]
        ax1.bar(['最强联合效应'], [strongest['value']], color='#FF6B6B', alpha=0.8)
        ax1.set_title(f'Strongest Joint Effect\n{strongest["description"]}', fontweight='bold')
        ax1.set_ylabel('SHAP Value (MW)')
        ax1.text(0, strongest['value'] + 5, f'{strongest["value"]:.1f} MW', 
                ha='center', va='bottom', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 2. 时段敏感性
        time_sens = insights[1]
        periods = ['深夜\n(0-5h)', '早高峰\n(7-9h)', '下午\n(13-15h)', '晚高峰\n(18-21h)']
        values = [time_sens['night'], time_sens['morning_peak'], 
                 time_sens['afternoon'], time_sens['evening_peak']]
        colors = ['#4ECDC4', '#45B7D1', '#96CEB4', '#FF6B6B']
        
        bars = ax2.bar(periods, values, color=colors, alpha=0.8)
        ax2.set_title('Time Period Sensitivity\n不同时段的温度敏感性', fontweight='bold')
        ax2.set_ylabel('Average SHAP Value (MW)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, value + 2, f'{value:.1f}', 
                    ha='center', va='bottom', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # 3. 温度阈值效应
        temp_thresh = insights[2]
        temp_categories = ['严寒\n(<0°C)', '温和\n(0-6°C)', '温暖\n(>6°C)']
        temp_values = [temp_thresh['cold_effect'], temp_thresh['mild_effect'], 
                      temp_thresh['warm_effect']]
        temp_colors = ['#87CEEB', '#98FB98', '#FFB6C1']
        
        bars = ax3.bar(temp_categories, temp_values, color=temp_colors, alpha=0.8)
        ax3.set_title('Temperature Threshold Effects\n温度阈值效应分析', fontweight='bold')
        ax3.set_ylabel('Average SHAP Value (MW)')
        
        # 添加数值标签
        for bar, value in zip(bars, temp_values):
            ax3.text(bar.get_x() + bar.get_width()/2, value + 2, f'{value:.1f}', 
                    ha='center', va='bottom', fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # 4. 关键发现文本
        ax4.axis('off')
        key_findings = [
            f"🔥 最强影响: {strongest['temperature']}°C at {strongest['hour']}:00 ({strongest['value']:.1f} MW)",
            f"⏰ 晚高峰敏感性最强: {time_sens['evening_peak']:.1f} MW",
            f"🌡️ 严寒效应: {temp_thresh['cold_effect']:.1f} MW",
            f"📈 -1°C晚上8点 vs 下午1点: 相差 197.87 MW",
            f"💡 关键洞察: 低温在用电高峰期的影响被显著放大"
        ]
        
        ax4.text(0.05, 0.9, 'Key Findings / 关键发现:', fontsize=16, fontweight='bold', 
                transform=ax4.transAxes)
        
        for i, finding in enumerate(key_findings):
            ax4.text(0.05, 0.75 - i*0.12, finding, fontsize=12, 
                    transform=ax4.transAxes, wrap=True)
        
        plt.tight_layout()
        plt.savefig('shap_insights_summary.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_3d_surface_plot(self):
        """创建3D表面图"""
        print("🏔️ 创建3D表面图...")
        
        matrix_data = self.data['interaction_matrix']
        matrix = np.array(matrix_data['matrix'])
        temp_range = np.array(matrix_data['temperature_range'])
        hour_range = np.array(matrix_data['hour_range'])
        
        # 创建网格
        H, T = np.meshgrid(hour_range, temp_range)
        
        # 创建3D图
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # 绘制表面
        surf = ax.plot_surface(H, T, matrix, cmap='RdYlBu_r', alpha=0.8, 
                              linewidth=0, antialiased=True)
        
        # 设置标签
        ax.set_xlabel('Hour of Day (小时)', fontsize=12)
        ax.set_ylabel('Temperature (°C) (温度)', fontsize=12)
        ax.set_zlabel('SHAP Joint Effect (MW)', fontsize=12)
        ax.set_title('3D Temperature × Hour SHAP Interaction Surface\n3D气温×小时SHAP交互表面', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # 添加颜色条
        fig.colorbar(surf, shrink=0.5, aspect=20)
        
        # 设置视角
        ax.view_init(elev=30, azim=45)
        
        plt.tight_layout()
        plt.savefig('shap_3d_surface.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_multi_dimensional_interactions(self):
        """绘制多维交互图"""
        print("📊 绘制多维交互图...")

        # 加载多维数据
        with open('frontend/public/data/shap_multi_dimensional_interactions.json', 'r', encoding='utf-8') as f:
            multi_data = json.load(f)

        # 创建2x2子图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))

        # 1. Day of Week × Hour 热力图
        dow_data = multi_data['dow_hour_interaction']
        dow_matrix = np.array(dow_data['matrix'])

        im1 = ax1.imshow(dow_matrix, cmap='RdYlBu_r', aspect='auto', origin='lower')
        ax1.set_xticks(range(len(dow_data['hour_range'])))
        ax1.set_xticklabels([f'{h:02d}:00' for h in dow_data['hour_range']], rotation=45)
        ax1.set_yticks(range(len(dow_data['dow_labels'])))
        ax1.set_yticklabels(dow_data['dow_labels'])
        ax1.set_title('Day of Week × Hour SHAP Interaction\n星期×小时SHAP交互', fontweight='bold')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Day of Week')
        plt.colorbar(im1, ax=ax1, shrink=0.8)

        # 2. Week of Month × Hour 热力图
        wom_data = multi_data['wom_hour_interaction']
        wom_matrix = np.array(wom_data['matrix'])

        im2 = ax2.imshow(wom_matrix, cmap='RdYlBu_r', aspect='auto', origin='lower')
        ax2.set_xticks(range(len(wom_data['hour_range'])))
        ax2.set_xticklabels([f'{h:02d}:00' for h in wom_data['hour_range']], rotation=45)
        ax2.set_yticks(range(len(wom_data['wom_labels'])))
        ax2.set_yticklabels(wom_data['wom_labels'])
        ax2.set_title('Week of Month × Hour SHAP Interaction\n月内周数×小时SHAP交互', fontweight='bold')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Week of Month')
        plt.colorbar(im2, ax=ax2, shrink=0.8)

        # 3. 工作日vs周末模式对比
        patterns = multi_data['key_patterns'][0]  # weekday_vs_weekend
        hours = list(range(24))
        weekday_pattern = patterns['weekday_pattern']
        weekend_pattern = patterns['weekend_pattern']

        ax3.plot(hours, weekday_pattern, 'o-', linewidth=3, markersize=6,
                label='Weekday (工作日)', color='#FF6B6B')
        ax3.plot(hours, weekend_pattern, 's-', linewidth=3, markersize=6,
                label='Weekend (周末)', color='#4ECDC4')
        ax3.set_title('Weekday vs Weekend Patterns\n工作日vs周末模式', fontweight='bold')
        ax3.set_xlabel('Hour of Day')
        ax3.set_ylabel('SHAP Joint Effect (MW)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_xticks(range(0, 24, 4))

        # 4. 月内周数效应
        week_patterns = multi_data['key_patterns'][1]['week_effects']
        weeks = [w['week'] for w in week_patterns]
        avg_shaps = [w['avg_shap'] for w in week_patterns]
        std_shaps = [w['std_shap'] for w in week_patterns]

        bars = ax4.bar(weeks, avg_shaps, yerr=std_shaps, capsize=5,
                      color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'], alpha=0.8)
        ax4.set_title('Week of Month Effects\n月内周数效应', fontweight='bold')
        ax4.set_xlabel('Week of Month')
        ax4.set_ylabel('Average SHAP Value (MW)')
        ax4.set_xticks(weeks)
        ax4.set_xticklabels([f'Week {w}' for w in weeks])
        ax4.grid(True, alpha=0.3)

        # 添加数值标签
        for bar, avg in zip(bars, avg_shaps):
            ax4.text(bar.get_x() + bar.get_width()/2, avg + 5, f'{avg:.1f}',
                    ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig('shap_multi_dimensional_interactions.png', dpi=300, bbox_inches='tight')
        plt.show()

    def visualize_all(self):
        """生成所有可视化"""
        print("🎨 开始生成所有3D SHAP可视化...")

        self.load_data()
        self.plot_interaction_heatmap()
        self.plot_key_scenarios()
        self.plot_insights_summary()
        self.create_3d_surface_plot()
        self.plot_multi_dimensional_interactions()

        print("\n🎉 所有可视化已完成！")
        print("📁 生成的图片文件:")
        print("   • shap_3d_interaction_heatmap.png - 温度×小时交互热力图")
        print("   • shap_key_scenarios.png - 关键场景对比")
        print("   • shap_insights_summary.png - 洞察总结")
        print("   • shap_3d_surface.png - 3D表面图")
        print("   • shap_multi_dimensional_interactions.png - 多维交互图")

if __name__ == "__main__":
    visualizer = SHAP3DVisualizer()
    visualizer.visualize_all()
