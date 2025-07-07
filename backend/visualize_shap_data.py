"""
SHAP数据可视化脚本
Visualize SHAP Data
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class SHAPDataVisualizer:
    """SHAP数据可视化器"""
    
    def __init__(self, json_path):
        """初始化可视化器"""
        self.json_path = json_path
        self.data = None
        self.load_data()
        
    def load_data(self):
        """加载SHAP数据"""
        print("📊 加载SHAP数据...")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print("✅ 数据加载完成")
        
    def plot_feature_importance(self):
        """绘制特征重要性图"""
        print("📈 绘制特征重要性图...")
        
        importance_data = self.data['feature_importance']
        
        # 准备数据
        features = [item['feature_chinese'] for item in importance_data]
        importances = [item['importance'] for item in importance_data]
        
        # 创建图形
        plt.figure(figsize=(10, 6))
        bars = plt.bar(features, importances, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        
        # 添加数值标签
        for bar, importance in zip(bars, importances):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{importance:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.title('SHAP特征重要性分析', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('特征', fontsize=12)
        plt.ylabel('重要性 (MW)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # 保存图片
        plt.savefig('shap_feature_importance.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_hour_dependence(self):
        """绘制小时依赖图"""
        print("🕐 绘制小时依赖图...")
        
        hour_data = self.data['feature_dependence']['Hour']['data_points']
        
        # 准备数据
        hours = [point['feature_value'] for point in hour_data]
        shap_values = [point['shap_value'] for point in hour_data]
        
        # 创建图形
        plt.figure(figsize=(12, 6))
        
        # 绘制折线图
        plt.plot(hours, shap_values, marker='o', linewidth=2, markersize=6, color='#FF6B6B')
        
        # 添加零线
        plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        
        # 填充正负区域
        plt.fill_between(hours, shap_values, 0, where=np.array(shap_values) >= 0, 
                        color='#FF6B6B', alpha=0.3, label='正向影响')
        plt.fill_between(hours, shap_values, 0, where=np.array(shap_values) < 0, 
                        color='#4ECDC4', alpha=0.3, label='负向影响')
        
        plt.title('小时对用电量的SHAP影响', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('小时', fontsize=12)
        plt.ylabel('SHAP值 (MW)', fontsize=12)
        plt.xticks(range(0, 24, 2))
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        # 保存图片
        plt.savefig('shap_hour_dependence.png', dpi=300, bbox_inches='tight')
        plt.show()

    def plot_temperature_dependence(self):
        """绘制温度依赖图"""
        print("🌡️ 绘制温度依赖图...")

        temp_data = self.data['feature_dependence']['Temperature']['data_points']

        # 准备数据
        temperatures = [point['feature_value'] for point in temp_data]
        shap_values = [point['shap_value'] for point in temp_data]

        # 创建图形
        plt.figure(figsize=(10, 6))

        # 绘制散点图
        scatter = plt.scatter(temperatures, shap_values, c=shap_values, cmap='RdYlBu_r',
                            s=100, alpha=0.7, edgecolors='black', linewidth=0.5)

        # 添加趋势线
        z = np.polyfit(temperatures, shap_values, 2)
        p = np.poly1d(z)
        temp_smooth = np.linspace(min(temperatures), max(temperatures), 100)
        plt.plot(temp_smooth, p(temp_smooth), '--', color='red', linewidth=2, alpha=0.8)

        # 添加零线
        plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

        plt.title('温度对用电量的SHAP影响', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('温度 (°C)', fontsize=12)
        plt.ylabel('SHAP值 (MW)', fontsize=12)
        plt.colorbar(scatter, label='SHAP值 (MW)')
        plt.grid(alpha=0.3)
        plt.tight_layout()

        # 保存图片
        plt.savefig('shap_temperature_dependence.png', dpi=300, bbox_inches='tight')
        plt.show()

    def plot_day_of_week_dependence(self):
        """绘制星期依赖图"""
        print("📅 绘制星期依赖图...")

        dow_data = self.data['feature_dependence']['Day_of_Week']['data_points']

        # 准备数据 - 按星期分组
        feature_values = [point['feature_value'] for point in dow_data]
        shap_values = [point['shap_value'] for point in dow_data]

        # 按星期分组计算平均SHAP值
        import pandas as pd
        df = pd.DataFrame({'day': feature_values, 'shap': shap_values})
        day_avg = df.groupby('day')['shap'].mean()

        # 星期标签
        day_labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        days = list(day_avg.index)
        avg_shap = list(day_avg.values)

        # 创建图形
        plt.figure(figsize=(12, 6))

        # 绘制条形图
        colors = ['#FF6B6B' if shap > 0 else '#4ECDC4' for shap in avg_shap]
        bars = plt.bar([day_labels[int(day)] for day in days], avg_shap,
                      color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)

        # 添加数值标签
        for bar, shap in zip(bars, avg_shap):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (5 if shap > 0 else -15),
                    f'{shap:.1f}', ha='center', va='bottom' if shap > 0 else 'top',
                    fontsize=10, fontweight='bold')

        # 添加零线
        plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

        plt.title('不同星期对用电量的SHAP影响', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('星期', fontsize=12)
        plt.ylabel('平均SHAP值 (MW)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        # 保存图片
        plt.savefig('shap_day_of_week_dependence.png', dpi=300, bbox_inches='tight')
        plt.show()

    def plot_week_of_month_dependence(self):
        """绘制周数依赖图"""
        print("📊 绘制周数依赖图...")

        wom_data = self.data['feature_dependence']['Week_of_Month']['data_points']

        # 准备数据 - 按周数分组
        feature_values = [point['feature_value'] for point in wom_data]
        shap_values = [point['shap_value'] for point in wom_data]

        # 按周数分组计算平均SHAP值
        df = pd.DataFrame({'week': feature_values, 'shap': shap_values})
        week_avg = df.groupby('week')['shap'].mean()

        weeks = list(week_avg.index)
        avg_shap = list(week_avg.values)
        week_labels = [f'第{int(week)}周' for week in weeks]

        # 创建图形
        plt.figure(figsize=(10, 6))

        # 绘制条形图
        colors = ['#FF6B6B' if shap > 0 else '#4ECDC4' for shap in avg_shap]
        bars = plt.bar(week_labels, avg_shap, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)

        # 添加数值标签
        for bar, shap in zip(bars, avg_shap):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (5 if shap > 0 else -15),
                    f'{shap:.1f}', ha='center', va='bottom' if shap > 0 else 'top',
                    fontsize=10, fontweight='bold')

        # 添加零线
        plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

        plt.title('不同周数对用电量的SHAP影响', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('月中周数', fontsize=12)
        plt.ylabel('平均SHAP值 (MW)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        # 保存图片
        plt.savefig('shap_week_of_month_dependence.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_summary_dashboard(self):
        """创建综合仪表板"""
        print("📊 创建综合仪表板...")
        
        # 创建2x3的子图布局
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('SHAP分析综合仪表板', fontsize=20, fontweight='bold', y=0.95)
        
        # 1. 特征重要性
        ax1 = axes[0, 0]
        importance_data = self.data['feature_importance']
        features = [item['feature_chinese'] for item in importance_data]
        importances = [item['importance'] for item in importance_data]
        bars = ax1.bar(features, importances, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        ax1.set_title('特征重要性', fontweight='bold')
        ax1.set_ylabel('重要性 (MW)')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. 小时依赖
        ax2 = axes[0, 1]
        hour_data = self.data['feature_dependence']['Hour']['data_points']
        hours = [point['feature_value'] for point in hour_data]
        hour_shap = [point['shap_value'] for point in hour_data]
        ax2.plot(hours, hour_shap, marker='o', color='#FF6B6B', linewidth=2)
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax2.set_title('小时影响', fontweight='bold')
        ax2.set_xlabel('小时')
        ax2.set_ylabel('SHAP值 (MW)')
        
        # 3. 温度依赖
        ax3 = axes[0, 2]
        temp_data = self.data['feature_dependence']['Temperature']['data_points']
        temperatures = [point['feature_value'] for point in temp_data]
        temp_shap = [point['shap_value'] for point in temp_data]
        scatter = ax3.scatter(temperatures, temp_shap, c=temp_shap, cmap='RdYlBu_r', s=50)
        ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax3.set_title('温度影响', fontweight='bold')
        ax3.set_xlabel('温度 (°C)')
        ax3.set_ylabel('SHAP值 (MW)')
        
        # 4. 星期依赖
        ax4 = axes[1, 0]
        dow_data = self.data['feature_dependence']['Day_of_Week']['data_points']
        dow_features = [point['feature_value'] for point in dow_data]
        dow_shap = [point['shap_value'] for point in dow_data]
        df_dow = pd.DataFrame({'day': dow_features, 'shap': dow_shap})
        dow_avg = df_dow.groupby('day')['shap'].mean()
        ax4.bar(range(len(dow_avg)), dow_avg.values, color='#45B7D1', alpha=0.7)
        ax4.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax4.set_title('星期影响', fontweight='bold')
        ax4.set_xlabel('星期')
        ax4.set_ylabel('SHAP值 (MW)')

        # 5. 周数依赖
        ax5 = axes[1, 1]
        wom_data = self.data['feature_dependence']['Week_of_Month']['data_points']
        wom_features = [point['feature_value'] for point in wom_data]
        wom_shap = [point['shap_value'] for point in wom_data]
        df_wom = pd.DataFrame({'week': wom_features, 'shap': wom_shap})
        wom_avg = df_wom.groupby('week')['shap'].mean()
        ax5.bar(range(len(wom_avg)), wom_avg.values, alpha=0.6, color='#96CEB4')
        ax5.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax5.set_title('周数影响', fontweight='bold')
        ax5.set_xlabel('周数')
        ax5.set_ylabel('SHAP值 (MW)')
        
        # 6. 数据摘要
        ax6 = axes[1, 2]
        ax6.axis('off')
        summary_text = f"""
数据摘要:
• 基准预测: {self.data['metadata']['base_prediction']:.1f} MW
• 预测小时数: {self.data['metadata']['total_hours']} 小时
• 最重要特征: {importance_data[0]['feature_chinese']}
• 重要性: {importance_data[0]['importance']:.1f} MW

特征影响范围:
• 小时: {min(hour_shap):.1f} ~ {max(hour_shap):.1f} MW
• 温度: {min(temp_shap):.1f} ~ {max(temp_shap):.1f} MW
• 星期: {min(dow_shap):.1f} ~ {max(dow_shap):.1f} MW
• 周数: {min(wom_avg.values):.1f} ~ {max(wom_avg.values):.1f} MW
        """
        ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('shap_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def visualize_all(self):
        """生成所有可视化"""
        print("🎨 开始生成所有SHAP可视化...")
        
        self.plot_feature_importance()
        self.plot_hour_dependence()
        self.plot_temperature_dependence()
        self.plot_day_of_week_dependence()
        self.plot_week_of_month_dependence()
        self.create_summary_dashboard()
        
        print("\n🎉 所有可视化已完成！")
        print("📁 生成的图片文件:")
        print("   • shap_feature_importance.png - 特征重要性")
        print("   • shap_hour_dependence.png - 小时依赖")
        print("   • shap_temperature_dependence.png - 温度依赖")
        print("   • shap_day_of_week_dependence.png - 星期依赖")
        print("   • shap_week_of_month_dependence.png - 周数依赖")
        print("   • shap_dashboard.png - 综合仪表板")

def main():
    """主函数"""
    print("🎯 SHAP数据可视化器")
    print("=" * 50)
    
    # 初始化可视化器
    json_path = "/Users/yichuanzhang/Desktop/workshop_TE/backend/shap_data_complete.json"
    visualizer = SHAPDataVisualizer(json_path)
    
    # 生成所有可视化
    visualizer.visualize_all()

if __name__ == "__main__":
    main()
