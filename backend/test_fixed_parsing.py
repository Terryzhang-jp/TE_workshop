#!/usr/bin/env python3
"""
测试修复后的解析逻辑

验证AI Agent现在能否正确解析问题和洞察，并基于问题进行迭代
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_section(text):
    print(f"\n{'─'*40}")
    print(f"  {text}")
    print(f"{'─'*40}")

def print_success(text):
    print(f"✅ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_thinking(text):
    print(f"🤔 {text}")

def print_insight(text):
    print(f"💡 {text}")

def print_question(text):
    print(f"❓ {text}")

async def test_parsing_fix():
    """测试修复后的解析逻辑"""
    
    print_header("🔧 测试修复后的解析逻辑")
    
    try:
        from ai_agent.core.state import create_initial_state
        from ai_agent.nodes.thinking import thinking_node
        
        # 创建测试状态
        state = create_initial_state(
            human_decision_intent="我需要调整明天的电力预测",
            human_reasoning="明天有极寒天气，需要考虑供暖需求增加",
            session_id="test-parsing-fix"
        )
        
        print_thinking("执行思考节点...")
        result = await thinking_node(state)
        
        print_section("解析结果验证")
        
        # 检查解析结果
        insights = result.get('insights', [])
        questions = result.get('active_questions', [])
        gaps = result.get('knowledge_gaps', [])
        
        print_info(f"解析到的洞察数量: {len(insights)}")
        print_info(f"解析到的问题数量: {len(questions)}")
        print_info(f"解析到的知识缺口数量: {len(gaps)}")
        
        # 显示解析到的洞察
        if insights:
            print_section("解析到的洞察")
            for i, insight in enumerate(insights, 1):
                if isinstance(insight, dict):
                    print_insight(f"{i}. {insight.get('content', '')}")
                    print(f"   置信度: {insight.get('confidence', 0)}")
                    print(f"   相关问题: {insight.get('related_questions', [])}")
        
        # 显示解析到的问题
        if questions:
            print_section("解析到的问题")
            for i, question in enumerate(questions, 1):
                if isinstance(question, dict):
                    print_question(f"{i}. {question.get('content', '')}")
                    print(f"   目标源: {question.get('target_source', '')}")
                    print(f"   优先级: {question.get('priority', 0)}")
        
        # 显示解析到的知识缺口
        if gaps:
            print_section("解析到的知识缺口")
            for i, gap in enumerate(gaps, 1):
                if isinstance(gap, dict):
                    print(f"🔍 {i}. {gap.get('description', '')}")
                    print(f"   重要性: {gap.get('importance', 0)}")
                    print(f"   潜在来源: {gap.get('potential_sources', [])}")
        
        # 检查下一步行动
        next_action = result.get('next_action', '')
        print_section("下一步行动决策")
        print_info(f"决定的下一步行动: {next_action}")
        
        # 验证是否基于问题做出了智能决策
        if questions and next_action:
            high_priority_questions = [q for q in questions if isinstance(q, dict) and q.get('priority', 0) > 0.7]
            if high_priority_questions:
                top_question = max(high_priority_questions, key=lambda q: q.get('priority', 0))
                target_source = top_question.get('target_source', '')
                print_info(f"最高优先级问题的目标源: {target_source}")
                
                # 检查下一步行动是否与最高优先级问题相关
                if target_source.lower() in next_action.lower():
                    print_success("✨ 智能路由成功！下一步行动与最高优先级问题相关")
                else:
                    print(f"⚠️  下一步行动({next_action})与最高优先级问题目标源({target_source})不匹配")
        
        return len(insights) > 0 or len(questions) > 0 or len(gaps) > 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_iterative_behavior():
    """测试迭代行为"""
    
    print_header("🔄 测试迭代行为")
    
    try:
        from ai_agent.core.state import create_initial_state
        from ai_agent.nodes.thinking import thinking_node
        from ai_agent.nodes.information import information_access_node
        
        # 创建初始状态
        state = create_initial_state(
            human_decision_intent="测试迭代行为",
            human_reasoning="我想看到AI Agent如何基于问题进行迭代",
            session_id="test-iterative"
        )
        
        max_iterations = 5
        for iteration in range(max_iterations):
            print_section(f"迭代 {iteration + 1}")
            
            # 执行思考
            print_thinking("执行思考节点...")
            thinking_result = await thinking_node(state)
            
            # 更新状态
            for key, value in thinking_result.items():
                if key in state:
                    if isinstance(state[key], list) and isinstance(value, list):
                        state[key].extend(value)
                    else:
                        state[key] = value
            
            next_action = state.get('next_action', '')
            questions = state.get('active_questions', [])
            
            print_info(f"当前问题数量: {len(questions)}")
            print_info(f"下一步行动: {next_action}")
            
            # 如果有信息访问行动，执行它
            if next_action in ['access_context', 'access_data', 'access_model', 'access_prediction']:
                print_thinking(f"执行信息访问: {next_action}")
                info_result = await information_access_node(state)
                
                # 更新状态
                for key, value in info_result.items():
                    if key in state:
                        if isinstance(state[key], list) and isinstance(value, list):
                            state[key].extend(value)
                        else:
                            state[key] = value
            
            # 检查是否应该继续
            if next_action in ['complete', 'execute'] or iteration >= max_iterations - 1:
                print_success(f"迭代在第 {iteration + 1} 步完成")
                break
        
        return True
        
    except Exception as e:
        print(f"❌ 迭代测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    
    print_header("🧪 AI Agent修复验证测试")
    
    success_count = 0
    total_tests = 2
    
    # 测试1: 解析修复
    if await test_parsing_fix():
        print_success("解析修复测试通过")
        success_count += 1
    else:
        print("❌ 解析修复测试失败")
    
    # 测试2: 迭代行为
    if await test_iterative_behavior():
        print_success("迭代行为测试通过")
        success_count += 1
    else:
        print("❌ 迭代行为测试失败")
    
    print_header("测试结果")
    print_info(f"通过测试: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print_success("🎉 所有修复都成功！AI Agent现在应该能正确解析和迭代了")
    else:
        print(f"❌ 还有 {total_tests - success_count} 个问题需要解决")

if __name__ == "__main__":
    asyncio.run(main())
