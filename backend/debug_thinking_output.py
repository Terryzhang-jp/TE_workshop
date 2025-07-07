#!/usr/bin/env python3
"""
调试AI Agent思考输出格式

检查Gemini实际输出的格式，找出解析问题
"""

import asyncio
import sys
import re
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

async def debug_thinking_output():
    """调试思考输出格式"""
    
    print("🔍 调试AI Agent思考输出格式")
    
    try:
        from ai_agent.core.state import create_initial_state
        from ai_agent.nodes.thinking import thinking_node
        
        # 创建测试状态
        state = create_initial_state(
            human_decision_intent="测试问题解析",
            human_reasoning="我需要看到AI Agent如何解析问题和洞察",
            session_id="debug-test"
        )
        
        print("\n📝 执行思考节点...")
        result = await thinking_node(state)
        
        print("\n📄 原始思考输出:")
        thinking_content = result.get('current_thinking', '')
        print("─" * 80)
        print(thinking_content)
        print("─" * 80)
        
        print("\n🔍 检查解析结果:")
        print(f"解析到的洞察数量: {len(result.get('insights', []))}")
        print(f"解析到的问题数量: {len(result.get('active_questions', []))}")
        print(f"解析到的知识缺口数量: {len(result.get('knowledge_gaps', []))}")
        
        # 手动测试正则表达式
        print("\n🧪 手动测试正则表达式:")
        
        # 测试INSIGHT解析
        insight_pattern = r'INSIGHT:\s*([^|]+)\|\s*([0-9.]+)\|\s*(.+)'
        insight_matches = re.findall(insight_pattern, thinking_content)
        print(f"INSIGHT匹配数量: {len(insight_matches)}")
        for i, match in enumerate(insight_matches):
            print(f"  {i+1}. 内容: {match[0].strip()}")
            print(f"     置信度: {match[1]}")
            print(f"     相关问题: {match[2].strip()}")
        
        # 测试QUESTION解析
        question_pattern = r'QUESTION:\s*([^|]+)\|\s*([^|]+)\|\s*([0-9.]+)'
        question_matches = re.findall(question_pattern, thinking_content)
        print(f"\nQUESTION匹配数量: {len(question_matches)}")
        for i, match in enumerate(question_matches):
            print(f"  {i+1}. 内容: {match[0].strip()}")
            print(f"     目标源: {match[1].strip()}")
            print(f"     优先级: {match[2]}")
        
        # 测试GAP解析
        gap_pattern = r'GAP:\s*([^|]+)\|\s*([0-9.]+)\|\s*(.+)'
        gap_matches = re.findall(gap_pattern, thinking_content)
        print(f"\nGAP匹配数量: {len(gap_matches)}")
        for i, match in enumerate(gap_matches):
            print(f"  {i+1}. 描述: {match[0].strip()}")
            print(f"     重要性: {match[1]}")
            print(f"     潜在来源: {match[2].strip()}")
        
        # 检查是否有其他格式的问题
        print("\n🔍 查找其他可能的问题格式:")
        lines = thinking_content.split('\n')
        for i, line in enumerate(lines):
            if '问题' in line or 'QUESTION' in line or '?' in line or '？' in line:
                print(f"  行 {i+1}: {line.strip()}")
        
        print("\n🔍 查找其他可能的洞察格式:")
        for i, line in enumerate(lines):
            if '洞察' in line or 'INSIGHT' in line or '💡' in line:
                print(f"  行 {i+1}: {line.strip()}")
                
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await debug_thinking_output()

if __name__ == "__main__":
    asyncio.run(main())
