#!/usr/bin/env python3
"""
显示AI Agent的最终具体调整建议
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

async def show_final_results():
    """显示最终的具体调整建议"""
    
    print("🎯 AI Agent 最终调整建议展示")
    print("="*60)
    
    try:
        from ai_agent.core.agent import DecisionCoPilot
        
        print("🤔 正在执行完整AI Agent决策流程...")
        agent = DecisionCoPilot()
        
        results = await agent.process_human_decision(
            human_decision_intent="我需要紧急调整明天的电力消费预测，特别是供暖需求激增的影响",
            human_reasoning="""
            基于以下考虑需要调整预测：
            1. 极寒天气将导致供暖需求大幅增加
            2. 早晨6-9点和晚上18-22点是用电高峰
            3. 工业用电可能因为设备防冻也会增加
            4. 需要确保电网稳定，避免供电不足
            5. 历史数据显示类似天气用电量增加15-25%
            """,
            session_id="final-results-demo"
        )
        
        print("\n" + "="*60)
        print("🎯 最终决策结果")
        print("="*60)
        
        if results:
            # 显示具体调整建议
            if results.get('final_adjustments'):
                print("\n📊 具体时间点调整建议:")
                print("-" * 40)
                adjustments = results['final_adjustments']
                if isinstance(adjustments, dict):
                    for time_period, details in adjustments.items():
                        if isinstance(details, dict):
                            print(f"⏰ {time_period}:")
                            print(f"   📈 调整幅度: +{details.get('adjustment_percentage', 0)}%")
                            print(f"   💡 调整原因: {details.get('reason', '未知')}")
                            print(f"   🎯 置信度: {details.get('confidence', 0):.0%}")
                            print()
                else:
                    print(f"   {adjustments}")
            
            # 显示具体建议
            if results.get('recommendations'):
                print("\n🎯 具体执行建议:")
                print("-" * 40)
                for i, rec in enumerate(results['recommendations'], 1):
                    print(f"{i}. {rec}")
            
            # 显示推理解释
            if results.get('reasoning_explanation'):
                print("\n🧠 AI Agent决策推理:")
                print("-" * 40)
                print(results['reasoning_explanation'])
            
            # 显示统计信息
            print("\n📊 决策过程统计:")
            print("-" * 40)
            print(f"总循环次数: {results.get('loop_count', 0)}")
            print(f"最终置信度: {results.get('confidence_level', 0):.0%}")
            print(f"是否完成: {results.get('is_complete', False)}")
            
        else:
            print("❌ 未获得结果")
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await show_final_results()

if __name__ == "__main__":
    asyncio.run(main())
