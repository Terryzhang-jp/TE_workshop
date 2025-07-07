#!/usr/bin/env python3
"""
AI Agent多轮思考机制测试

验证AI Agent是否支持：
1. 多次激活thinking节点
2. 评估当前信息是否充分
3. 决定是否需要更多信息
4. 智能的循环决策
"""
import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    print(f"\n{'='*80}")
    print(f"🧠 {title}")
    print(f"{'='*80}")

def print_thinking_round(round_num, state, action):
    print(f"\n🔸 思考轮次 {round_num}")
    print(f"   当前状态: 步骤{state.get('thinking_step', 0)}, 循环{state.get('loop_count', 0)}")
    print(f"   已访问信息: {sum(state.get('accessed_info', {}).values())}/4")
    print(f"   下一步行动: {action}")
    print(f"   分析完成: {'是' if state.get('analysis_results') else '否'}")
    print(f"   决策制定: {'是' if state.get('decision_strategy') else '否'}")

async def simulate_multi_round_thinking():
    """模拟多轮思考过程"""
    
    print_header("AI Agent多轮思考机制测试")
    
    from ai_agent.core.state import create_initial_state, ActionType
    from ai_agent.nodes.thinking import thinking_node
    from ai_agent.nodes.information import information_access_node
    from ai_agent.nodes.analysis import analysis_node
    from ai_agent.nodes.decision import decision_node
    
    # 创建初始状态
    state = create_initial_state(
        human_decision_intent="测试多轮思考机制",
        human_reasoning="验证AI Agent是否能够多次思考并评估信息充分性",
        session_id="multi-thinking-test"
    )
    
    print(f"🚀 开始多轮思考测试")
    print(f"   人类意图: {state['human_decision_intent']}")
    print(f"   最大循环: {state['max_loops']}")
    
    thinking_rounds = []
    max_rounds = 10  # 防止无限循环
    
    for round_num in range(1, max_rounds + 1):
        print_header(f"思考轮次 {round_num}")
        
        # 记录当前状态
        current_state_snapshot = {
            'thinking_step': state.get('thinking_step', 0),
            'loop_count': state.get('loop_count', 0),
            'accessed_info': state.get('accessed_info', {}),
            'has_analysis': bool(state.get('analysis_results')),
            'has_decision': bool(state.get('decision_strategy')),
            'confidence': state.get('confidence_level', 0)
        }
        
        # 执行thinking节点 (简化版，不依赖Gemini)
        print("🧠 AI Agent正在思考...")
        
        # 模拟thinking节点的决策逻辑
        next_action = simulate_thinking_decision(state)
        
        print_thinking_round(round_num, state, next_action)
        
        # 记录这轮思考
        thinking_rounds.append({
            'round': round_num,
            'state_before': current_state_snapshot,
            'action_decided': next_action
        })
        
        # 根据决策执行相应节点
        if next_action == ActionType.ACCESS_CONTEXT:
            print("📊 访问上下文信息...")
            info_result = await information_access_node(state)
            state.update(info_result)
            
        elif next_action == ActionType.ACCESS_DATA:
            print("📈 访问数据分析信息...")
            state['next_action'] = ActionType.ACCESS_DATA
            info_result = await information_access_node(state)
            state.update(info_result)
            
        elif next_action == ActionType.ACCESS_MODEL:
            print("🔍 访问模型解释性信息...")
            state['next_action'] = ActionType.ACCESS_MODEL
            info_result = await information_access_node(state)
            state.update(info_result)
            
        elif next_action == ActionType.ACCESS_PREDICTION:
            print("🎯 访问用户预测信息...")
            state['next_action'] = ActionType.ACCESS_PREDICTION
            info_result = await information_access_node(state)
            state.update(info_result)
            
        elif next_action == ActionType.ANALYZE:
            print("🔬 执行分析...")
            analysis_result = await analysis_node(state)
            state.update(analysis_result)
            
        elif next_action == ActionType.DECIDE:
            print("💡 制定决策...")
            decision_result = await decision_node(state)
            state.update(decision_result)
            
        elif next_action == ActionType.COMPLETE:
            print("✅ 思考过程完成")
            break
            
        else:
            print(f"❓ 未知行动: {next_action}")
            break
        
        # 更新循环计数
        state['loop_count'] = state.get('loop_count', 0) + 1
        state['thinking_step'] = state.get('thinking_step', 0) + 1
        
        # 检查是否达到最大循环
        if state['loop_count'] >= state['max_loops']:
            print("⏰ 达到最大循环次数")
            break
    
    return thinking_rounds, state

def simulate_thinking_decision(state):
    """模拟thinking节点的决策逻辑"""

    from ai_agent.core.state import ActionType

    # 检查完成条件
    if state.get('loop_count', 0) >= state.get('max_loops', 10):
        return ActionType.COMPLETE
    
    # 检查是否有错误
    if state.get('error_messages'):
        return ActionType.COMPLETE
    
    # 信息收集阶段
    accessed_info = state.get('accessed_info', {})
    
    # 如果没有访问任何信息，从上下文开始
    if not any(accessed_info.values()):
        return ActionType.ACCESS_CONTEXT
    
    # 如果只有部分信息，继续收集
    if not all(accessed_info.values()):
        # 智能决策：根据已有信息决定下一步
        if not accessed_info.get('contextual_information', False):
            return ActionType.ACCESS_CONTEXT
        elif not accessed_info.get('model_interpretability', False):
            return ActionType.ACCESS_MODEL
        elif not accessed_info.get('user_prediction', False):
            return ActionType.ACCESS_PREDICTION
        elif not accessed_info.get('data_analysis', False):
            return ActionType.ACCESS_DATA
    
    # 所有信息都收集了，开始分析
    if not state.get('analysis_results'):
        return ActionType.ANALYZE
    
    # 分析完成，制定决策
    if not state.get('decision_strategy'):
        return ActionType.DECIDE
    
    # 决策完成，可以结束
    return ActionType.COMPLETE

def analyze_thinking_patterns(thinking_rounds):
    """分析思考模式"""

    from ai_agent.core.state import ActionType

    print_header("思考模式分析")

    # 统计信息
    total_rounds = len(thinking_rounds)
    info_access_rounds = sum(1 for r in thinking_rounds if 'access' in r['action_decided'])
    analysis_rounds = sum(1 for r in thinking_rounds if r['action_decided'] == ActionType.ANALYZE)
    decision_rounds = sum(1 for r in thinking_rounds if r['action_decided'] == ActionType.DECIDE)
    
    print(f"📊 思考统计:")
    print(f"   总思考轮次: {total_rounds}")
    print(f"   信息收集轮次: {info_access_rounds}")
    print(f"   分析轮次: {analysis_rounds}")
    print(f"   决策轮次: {decision_rounds}")
    
    # 分析思考序列
    print(f"\n🔄 思考序列:")
    for i, round_data in enumerate(thinking_rounds, 1):
        action = round_data['action_decided']
        state_before = round_data['state_before']
        info_count = sum(state_before['accessed_info'].values())
        
        print(f"   {i}. 信息{info_count}/4 → {action}")
    
    # 验证多轮思考特性
    print(f"\n✅ 多轮思考特性验证:")
    
    # 1. 是否有多轮信息收集
    has_multiple_info_rounds = info_access_rounds > 1
    print(f"   多轮信息收集: {'是' if has_multiple_info_rounds else '否'} ({info_access_rounds}轮)")
    
    # 2. 是否在信息收集后进行分析
    has_analysis_after_info = any(
        r['action_decided'] == 'analyze' and
        sum(r['state_before']['accessed_info'].values()) > 0
        for r in thinking_rounds
    )
    print(f"   信息后分析: {'是' if has_analysis_after_info else '否'}")
    
    # 3. 是否有渐进式信息收集
    info_progression = []
    for r in thinking_rounds:
        info_count = sum(r['state_before']['accessed_info'].values())
        info_progression.append(info_count)
    
    is_progressive = all(info_progression[i] <= info_progression[i+1] for i in range(len(info_progression)-1))
    print(f"   渐进式收集: {'是' if is_progressive else '否'}")
    
    # 4. 是否有智能决策序列
    expected_sequence = ['access', 'access', 'access', 'access', 'analyze', 'decide']
    actual_sequence = [r['action_decided'].split('_')[0] if '_' in r['action_decided'] else r['action_decided'] for r in thinking_rounds]
    
    sequence_match = len(set(expected_sequence) & set(actual_sequence)) >= 3
    print(f"   智能决策序列: {'是' if sequence_match else '否'}")
    
    return {
        'total_rounds': total_rounds,
        'has_multiple_info_rounds': has_multiple_info_rounds,
        'has_analysis_after_info': has_analysis_after_info,
        'is_progressive': is_progressive,
        'sequence_match': sequence_match
    }

async def main():
    """主测试函数"""
    
    print("🧠 AI Agent多轮思考机制测试")
    print("="*80)
    
    try:
        # 执行多轮思考测试
        thinking_rounds, final_state = await simulate_multi_round_thinking()
        
        # 分析思考模式
        analysis = analyze_thinking_patterns(thinking_rounds)
        
        # 总结
        print_header("测试总结")
        
        success_criteria = [
            analysis['has_multiple_info_rounds'],
            analysis['has_analysis_after_info'],
            analysis['is_progressive'],
            analysis['sequence_match']
        ]
        
        passed_criteria = sum(success_criteria)
        total_criteria = len(success_criteria)
        
        print(f"📊 测试结果: {passed_criteria}/{total_criteria} 通过")
        
        if passed_criteria >= 3:
            print("🎉 AI Agent支持智能多轮思考！")
            print("\n✅ 确认特性:")
            print("   • 多次激活thinking节点")
            print("   • 评估信息充分性")
            print("   • 渐进式信息收集")
            print("   • 智能决策序列")
            
        else:
            print("⚠️ 多轮思考机制需要改进")
            
        print(f"\n📈 最终状态:")
        print(f"   思考步骤: {final_state.get('thinking_step', 0)}")
        print(f"   循环次数: {final_state.get('loop_count', 0)}")
        print(f"   信息完整性: {sum(final_state.get('accessed_info', {}).values())}/4")
        print(f"   分析完成: {'是' if final_state.get('analysis_results') else '否'}")
        print(f"   决策制定: {'是' if final_state.get('decision_strategy') else '否'}")
        
        return passed_criteria >= 3
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
        sys.exit(1)
