#!/usr/bin/env python3
"""
调试洞察和问题的格式

检查为什么演示脚本中洞察和问题的计数为0
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

async def debug_insights_questions():
    """调试洞察和问题的格式"""
    
    print("🔍 调试洞察和问题格式")
    
    try:
        from ai_agent.core.state import create_initial_state
        from ai_agent.nodes.thinking import thinking_node
        
        # 创建测试状态
        state = create_initial_state(
            human_decision_intent="测试洞察和问题格式",
            human_reasoning="我需要看到具体的洞察和问题格式",
            session_id="debug-insights"
        )
        
        print("\n🤔 执行思考节点...")
        result = await thinking_node(state)
        
        print("\n📊 检查返回结果的键:")
        for key in result.keys():
            print(f"  - {key}: {type(result[key])}")
        
        print("\n🔍 检查insights:")
        insights = result.get('insights', [])
        print(f"insights类型: {type(insights)}")
        print(f"insights长度: {len(insights)}")
        if insights:
            print("insights内容:")
            for i, insight in enumerate(insights):
                print(f"  {i+1}. 类型: {type(insight)}")
                print(f"      内容: {insight}")
        else:
            print("insights为空")
        
        print("\n🔍 检查active_questions:")
        questions = result.get('active_questions', [])
        print(f"active_questions类型: {type(questions)}")
        print(f"active_questions长度: {len(questions)}")
        if questions:
            print("active_questions内容:")
            for i, question in enumerate(questions):
                print(f"  {i+1}. 类型: {type(question)}")
                print(f"      内容: {question}")
        else:
            print("active_questions为空")
        
        print("\n🔍 检查knowledge_gaps:")
        gaps = result.get('knowledge_gaps', [])
        print(f"knowledge_gaps类型: {type(gaps)}")
        print(f"knowledge_gaps长度: {len(gaps)}")
        if gaps:
            print("knowledge_gaps内容:")
            for i, gap in enumerate(gaps):
                print(f"  {i+1}. 类型: {type(gap)}")
                print(f"      内容: {gap}")
        else:
            print("knowledge_gaps为空")
        
        print("\n📝 原始思考内容:")
        thinking_content = result.get('current_thinking', '')
        print("─" * 60)
        print(thinking_content[:1000])  # 显示前1000字符
        print("─" * 60)
        
        # 手动检查是否有INSIGHT、QUESTION、GAP标记
        print("\n🔍 手动搜索标记:")
        if 'INSIGHT:' in thinking_content:
            print("✅ 找到INSIGHT标记")
            import re
            insights_found = re.findall(r'INSIGHT:.*', thinking_content)
            print(f"找到 {len(insights_found)} 个INSIGHT标记")
            for insight in insights_found[:3]:
                print(f"  - {insight}")
        else:
            print("❌ 未找到INSIGHT标记")
        
        if 'QUESTION:' in thinking_content:
            print("✅ 找到QUESTION标记")
            import re
            questions_found = re.findall(r'QUESTION:.*', thinking_content)
            print(f"找到 {len(questions_found)} 个QUESTION标记")
            for question in questions_found[:3]:
                print(f"  - {question}")
        else:
            print("❌ 未找到QUESTION标记")
        
        if 'GAP:' in thinking_content:
            print("✅ 找到GAP标记")
            import re
            gaps_found = re.findall(r'GAP:.*', thinking_content)
            print(f"找到 {len(gaps_found)} 个GAP标记")
            for gap in gaps_found[:3]:
                print(f"  - {gap}")
        else:
            print("❌ 未找到GAP标记")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await debug_insights_questions()

if __name__ == "__main__":
    asyncio.run(main())
