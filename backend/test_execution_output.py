#!/usr/bin/env python3
"""
直接测试execution节点的输出
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

async def test_execution_output():
    """测试execution节点的输出"""
    
    print("🎯 测试Execution节点输出")
    print("="*50)
    
    try:
        from ai_agent.core.state import create_initial_state
        from ai_agent.nodes.execution import execution_node
        
        # 创建模拟的完整状态
        state = create_initial_state(
            human_decision_intent="我需要紧急调整明天的电力消费预测，特别是供暖需求激增的影响",
            human_reasoning="极寒天气将导致供暖需求大幅增加，特别是早晚高峰时段",
            session_id="test-execution"
        )
        
        # 模拟一些思考历史
        state["thinking_history"] = [
            "分析极寒天气对电力需求的影响",
            "确认明天将面临-15°C的极端低温",
            "历史数据显示类似天气下总用电量增加22%，峰值负荷激增35%",
            "模型在极端低温下响应不足，需要进行外科手术式调整"
        ]
        
        # 设置一些分析结果
        state["confidence_level"] = 0.85
        state["adjustment_plan"] = {
            "morning_peak": "25% increase",
            "evening_peak": "35% increase"
        }
        
        print("🤔 执行execution节点...")
        result = await execution_node(state)
        
        print("\n📊 Execution节点返回结果:")
        print("-" * 40)
        for key, value in result.items():
            print(f"{key}: {type(value)}")
        
        # 显示具体调整建议
        if result.get('final_adjustments'):
            print("\n🎯 具体时间点调整建议:")
            print("-" * 40)
            adjustments = result['final_adjustments']
            if isinstance(adjustments, dict):
                for time_period, details in adjustments.items():
                    print(f"\n⏰ {time_period}:")
                    if isinstance(details, dict):
                        for key, value in details.items():
                            print(f"   {key}: {value}")
                    else:
                        print(f"   {details}")
        
        # 显示具体建议
        if result.get('recommendations'):
            print("\n🎯 具体执行建议:")
            print("-" * 40)
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"{i}. {rec}")
        
        # 显示推理解释
        if result.get('reasoning_explanation'):
            print("\n🧠 AI Agent决策推理:")
            print("-" * 40)
            print(result['reasoning_explanation'])
        
        print("\n✅ Execution节点测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await test_execution_output()

if __name__ == "__main__":
    asyncio.run(main())
