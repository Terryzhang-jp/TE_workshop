#!/usr/bin/env python3
"""
批量预训练脚本
Batch Pre-training Script

用于预先训练所有需要的模型并保存结果到data文件夹
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.prediction_service import PredictionService
from app.utils.helpers import validate_date_format
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pretraining")

class ModelPretrainer:
    """模型预训练器"""
    
    def __init__(self):
        self.prediction_service = PredictionService()
        self.data_dir = project_root / "data" / "pretrained_models"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    async def pretrain_date_range(
        self, 
        start_date: str, 
        end_date: str,
        weeks_before: int = 3
    ) -> dict:
        """预训练指定日期范围的所有模型
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            weeks_before: 使用前几周的数据训练
            
        Returns:
            预训练结果汇总
        """
        logger.info(f"开始预训练模型：{start_date} 到 {end_date}")
        
        # 验证日期格式
        start_dt = validate_date_format(start_date)
        end_dt = validate_date_format(end_date)
        
        if start_dt > end_dt:
            raise ValueError("开始日期不能晚于结束日期")
        
        # 计算需要训练的天数
        total_days = (end_dt - start_dt).days + 1
        logger.info(f"将预训练 {total_days} 个模型")
        
        results = {
            "metadata": {
                "start_date": start_date,
                "end_date": end_date,
                "total_days": total_days,
                "weeks_before": weeks_before,
                "generated_at": datetime.now().isoformat(),
                "version": "2.0",
                "data_leakage_fixed": True,
                "improvements": [
                    "特征缩放仅在训练集上拟合",
                    "异常值处理仅基于训练集统计",
                    "消除了验证集信息泄漏到训练过程"
                ]
            },
            "models": {}
        }
        
        current_date = start_dt
        successful_count = 0
        failed_count = 0
        
        while current_date <= end_dt:
            target_date_str = current_date.strftime("%Y-%m-%d")
            logger.info(f"预训练目标日期: {target_date_str}")
            
            try:
                # 训练模型
                training_result = await self.prediction_service.train_model(
                    target_date=target_date_str,
                    weeks_before=weeks_before,
                    force_retrain=True  # 强制重新训练以获取最新结果
                )
                
                # 获取模型评估指标
                metrics = await self.prediction_service.get_model_metrics(
                    target_date=target_date_str
                )
                
                # 计算训练数据范围
                from app.utils.helpers import calculate_date_range
                train_start, train_end = calculate_date_range(target_date_str, weeks_before)
                
                # 保存模型信息
                model_info = {
                    "target_date": target_date_str,
                    "training_data_range": {
                        "start_date": train_start.strftime("%Y-%m-%d"),
                        "end_date": train_end.strftime("%Y-%m-%d"),
                        "days": (train_end - train_start).days + 1
                    },
                    "model_performance": {
                        "training_metrics": metrics.get("training_metrics", {}),
                        "validation_metrics": metrics.get("validation_metrics", {}),
                        "cross_validation": metrics.get("cross_validation", {})
                    },
                    "training_info": {
                        "training_time": training_result.get("training_result", {}).get("training_time", 0),
                        "training_samples": training_result.get("data_info", {}).get("training_samples", 0),
                        "validation_samples": training_result.get("data_info", {}).get("validation_samples", 0),
                        "feature_count": training_result.get("data_info", {}).get("feature_count", 0)
                    },
                    "model_available": True,
                    "trained_at": datetime.now().isoformat()
                }
                
                results["models"][target_date_str] = model_info
                successful_count += 1
                logger.info(f"✓ 目标日期 {target_date_str} 预训练完成")
                
            except Exception as e:
                logger.error(f"✗ 目标日期 {target_date_str} 预训练失败: {str(e)}")
                
                # 记录失败信息
                from app.utils.helpers import calculate_date_range
                train_start, train_end = calculate_date_range(target_date_str, weeks_before)
                
                results["models"][target_date_str] = {
                    "target_date": target_date_str,
                    "training_data_range": {
                        "start_date": train_start.strftime("%Y-%m-%d"),
                        "end_date": train_end.strftime("%Y-%m-%d"),
                        "days": (train_end - train_start).days + 1
                    },
                    "model_performance": None,
                    "training_info": None,
                    "model_available": False,
                    "error": str(e),
                    "failed_at": datetime.now().isoformat()
                }
                failed_count += 1
            
            # 移动到下一天
            current_date += timedelta(days=1)
        
        # 更新汇总信息
        results["metadata"]["successful_models"] = successful_count
        results["metadata"]["failed_models"] = failed_count
        results["metadata"]["success_rate"] = successful_count / total_days * 100
        
        logger.info(f"预训练完成: 成功 {successful_count}/{total_days} ({results['metadata']['success_rate']:.1f}%)")
        
        return results
    
    def save_results(self, results: dict, filename: str = None) -> str:
        """保存预训练结果到文件
        
        Args:
            results: 预训练结果
            filename: 文件名，如果不指定则自动生成
            
        Returns:
            保存的文件路径
        """
        if filename is None:
            start_date = results["metadata"]["start_date"].replace("-", "")
            end_date = results["metadata"]["end_date"].replace("-", "")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pretrained_models_{start_date}_{end_date}_{timestamp}.json"
        
        file_path = self.data_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"预训练结果已保存到: {file_path}")
        return str(file_path)
    
    def load_results(self, filename: str) -> dict:
        """从文件加载预训练结果
        
        Args:
            filename: 文件名
            
        Returns:
            预训练结果
        """
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"预训练结果文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        logger.info(f"预训练结果已加载: {file_path}")
        return results

async def main():
    """主函数"""
    pretrainer = ModelPretrainer()
    
    # 预训练6月1日到7月31日的模型
    start_date = "2022-06-01"
    end_date = "2022-07-31"
    
    try:
        results = await pretrainer.pretrain_date_range(start_date, end_date)
        file_path = pretrainer.save_results(results)
        
        print(f"\n🎉 预训练完成！")
        print(f"📊 成功训练: {results['metadata']['successful_models']} 个模型")
        print(f"❌ 训练失败: {results['metadata']['failed_models']} 个模型")
        print(f"📈 成功率: {results['metadata']['success_rate']:.1f}%")
        print(f"💾 结果保存到: {file_path}")
        
    except Exception as e:
        logger.error(f"预训练过程发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
