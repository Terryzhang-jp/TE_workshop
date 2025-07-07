#!/usr/bin/env python3
"""
真实场景演示：AI Agent完整决策流程

模拟一个真实的电力预测调整场景，展示AI Agent的每一步思考过程
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
import time

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """打印大标题"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}")

def print_section(text):
    """打印章节标题"""
    print(f"\n{'─'*60}")
    print(f"  {text}")
    print(f"{'─'*60}")

def print_step(step_num, text):
    """打印步骤"""
    print(f"\n🔸 步骤 {step_num}: {text}")

def print_thinking(text):
    """打印思考过程"""
    print(f"🤔 {text}")

def print_insight(text):
    """打印洞察"""
    print(f"💡 洞察: {text}")

def print_question(text):
    """打印问题"""
    print(f"❓ 问题: {text}")

def print_action(text):
    """打印行动"""
    print(f"🎯 行动: {text}")

def print_info(text):
    """打印信息"""
    print(f"ℹ️  {text}")

def print_success(text):
    """打印成功"""
    print(f"✅ {text}")

def print_warning(text):
    """打印警告"""
    print(f"⚠️  {text}")

class AIAgentMonitor:
    """AI Agent监控器 - 实时跟踪Agent的思考过程"""
    
    def __init__(self):
        self.step_count = 0
        self.total_insights = 0
        self.total_questions = 0
        self.start_time = None
    
    def log_step(self, step_type, content, next_action=None, insights=None, questions=None):
        """记录每一步的详细信息"""
        self.step_count += 1
        
        print_step(self.step_count, f"{step_type}")
        
        # 显示思考内容
        if content:
            print_thinking("思考过程:")
            # 分段显示思考内容
            lines = content.split('\n')
            for line in lines[:10]:  # 显示前10行
                if line.strip():
                    print(f"   {line.strip()}")
            if len(lines) > 10:
                print(f"   ... (还有 {len(lines) - 10} 行)")
        
        # 显示洞察
        if insights:
            for insight in insights:
                if isinstance(insight, dict):
                    confidence = insight.get('confidence', 0)
                    content = insight.get('content', '')
                    print_insight(f"{content} (置信度: {confidence})")
                    self.total_insights += 1
        
        # 显示问题
        if questions:
            for question in questions:
                if isinstance(question, dict):
                    priority = question.get('priority', 0)
                    content = question.get('content', '')
                    target = question.get('target_source', '')
                    print_question(f"{content} (优先级: {priority}, 目标: {target})")
                    self.total_questions += 1
        
        # 显示下一步行动
        if next_action:
            print_action(f"下一步: {next_action}")
        
        print(f"   ⏱️  累计用时: {self.get_elapsed_time():.1f}秒")
        print(f"   📊 累计洞察: {self.total_insights} 个")
        print(f"   📋 累计问题: {self.total_questions} 个")
    
    def start_monitoring(self):
        """开始监控"""
        self.start_time = datetime.now()
    
    def get_elapsed_time(self):
        """获取已用时间"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0

async def run_real_scenario_demo():
    """运行真实场景演示"""
    
    print_header("🌟 AI Agent 真实场景演示")
    print_info("场景：极寒天气下的电力预测紧急调整")
    
    # 场景设定
    scenario = {
        "situation": "明天预报极寒天气，最低温度-15°C，比正常低10°C",
        "human_intent": "我需要紧急调整明天的电力消费预测，特别是供暖需求激增的影响",
        "human_reasoning": """
        基于以下考虑需要调整预测：
        1. 极寒天气将导致供暖需求大幅增加
        2. 早晨6-9点和晚上18-22点是用电高峰
        3. 工业用电可能因为设备防冻也会增加
        4. 需要确保电网稳定，避免供电不足
        5. 历史数据显示类似天气用电量增加15-25%
        """,
        "expected_challenges": [
            "量化温度变化对用电的具体影响",
            "识别最需要调整的时间段",
            "平衡供需关系",
            "考虑电网承载能力"
        ]
    }
    
    print_section("📋 场景背景")
    print_info(f"情况: {scenario['situation']}")
    print_info(f"人类意图: {scenario['human_intent']}")
    print_info("人类推理:")
    for line in scenario['human_reasoning'].strip().split('\n'):
        if line.strip():
            print(f"   {line.strip()}")
    
    print_section("🚀 启动AI Agent决策流程")
    
    # 初始化监控器
    monitor = AIAgentMonitor()
    monitor.start_monitoring()
    
    try:
        from ai_agent.core.agent import DecisionCoPilot
        
        print_thinking("正在初始化AI Agent...")
        agent = DecisionCoPilot()
        print_success("AI Agent初始化成功")
        
        print_thinking("开始处理人类决策意图...")
        
        # 创建自定义的状态监控
        results = await run_monitored_agent(
            agent, 
            scenario['human_intent'], 
            scenario['human_reasoning'],
            monitor
        )
        
        print_section("🎯 最终决策结果")
        
        if results:
            print_success("AI Agent决策流程完成")
            print_info(f"总处理时间: {results.get('processing_time', 0):.1f}秒")
            print_info(f"总循环次数: {results.get('loop_count', 0)}")
            print_info(f"最终置信度: {results.get('confidence_level', 0):.2f}")
            
            if results.get('final_adjustments'):
                print_info("最终调整建议:")
                adjustments = results['final_adjustments']
                if isinstance(adjustments, dict):
                    for key, value in adjustments.items():
                        print(f"   - {key}: {value}")
                else:
                    print(f"   {adjustments}")
            
            if results.get('reasoning_explanation'):
                print_info("决策推理:")
                print(f"   {results['reasoning_explanation'][:300]}...")
            
            if results.get('recommendations'):
                print_info("具体建议:")
                for i, rec in enumerate(results['recommendations'][:5], 1):
                    print(f"   {i}. {rec}")
        
        print_section("📊 决策过程统计")
        print_info(f"总步骤数: {monitor.step_count}")
        print_info(f"总洞察数: {monitor.total_insights}")
        print_info(f"总问题数: {monitor.total_questions}")
        print_info(f"总用时: {monitor.get_elapsed_time():.1f}秒")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

async def run_monitored_agent(agent, intent, reasoning, monitor):
    """运行带监控的AI Agent - 真实执行并实时监控"""

    print_thinking("正在执行真实的AI Agent决策流程...")

    # 创建自定义的监控版本
    from ai_agent.core.state import create_initial_state
    from ai_agent.nodes.thinking import thinking_node
    from ai_agent.nodes.information import information_access_node
    from ai_agent.nodes.analysis import analysis_node
    from ai_agent.nodes.decision import decision_node
    from ai_agent.nodes.execution import execution_node

    # 创建初始状态
    state = create_initial_state(
        human_decision_intent=intent,
        human_reasoning=reasoning,
        session_id="real-scenario-demo"
    )

    print_thinking("开始逐步执行AI Agent决策流程...")

    step_count = 0
    max_steps = 15  # 防止无限循环

    while step_count < max_steps and not state.get('is_complete', False):
        step_count += 1
        current_action = state.get('next_action', 'think')

        print_section(f"🔄 执行步骤 {step_count}: {current_action}")

        try:
            if current_action == 'think':
                print_thinking("执行思考节点...")
                result = await thinking_node(state)

                # 显示思考结果
                monitor.log_step(
                    "思考分析",
                    result.get('current_thinking', ''),
                    result.get('next_action'),
                    result.get('insights', []),
                    result.get('active_questions', [])
                )

            elif current_action in ['access_context', 'access_data', 'access_model', 'access_prediction']:
                action_map = {
                    'access_context': '访问上下文信息',
                    'access_data': '访问数据分析',
                    'access_model': '访问模型解释性',
                    'access_prediction': '访问用户预测'
                }
                print_thinking(f"执行信息访问节点: {action_map.get(current_action, current_action)}")
                result = await information_access_node(state)

                monitor.log_step(
                    action_map.get(current_action, current_action),
                    f"成功访问 {current_action} 信息",
                    result.get('next_action'),
                    [],
                    []
                )

            elif current_action == 'analyze':
                print_thinking("执行分析节点...")
                result = await analysis_node(state)

                monitor.log_step(
                    "综合分析",
                    "对收集的信息进行综合分析",
                    result.get('next_action'),
                    [],
                    []
                )

            elif current_action == 'decide':
                print_thinking("执行决策节点...")
                result = await decision_node(state)

                monitor.log_step(
                    "制定决策",
                    "基于分析结果制定具体决策",
                    result.get('next_action'),
                    [],
                    []
                )

            elif current_action == 'execute':
                print_thinking("执行最终执行节点...")
                result = await execution_node(state)

                monitor.log_step(
                    "执行决策",
                    "生成最终建议和执行方案",
                    result.get('next_action'),
                    [],
                    []
                )
                break

            else:
                print_warning(f"未知行动: {current_action}")
                break

            # 更新状态
            if result:
                for key, value in result.items():
                    if key in state:
                        if isinstance(state[key], list) and isinstance(value, list):
                            state[key].extend(value)
                        else:
                            state[key] = value

            # 检查是否应该结束
            if state.get('loop_count', 0) >= state.get('max_loops', 15):
                print_warning("达到最大循环次数，结束流程")
                break

        except Exception as e:
            print(f"❌ 步骤 {step_count} 执行失败: {e}")
            break

    print_success(f"AI Agent决策流程完成，共执行 {step_count} 步")
    return state

async def main():
    """主函数"""
    await run_real_scenario_demo()

if __name__ == "__main__":
    asyncio.run(main())
