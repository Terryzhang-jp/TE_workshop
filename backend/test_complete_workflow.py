#!/usr/bin/env python3
"""
完整AI Agent决策工作流程测试

这个脚本测试AI Agent从接收人类决策意图到输出最终建议的完整流程。
"""
import asyncio
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title):
    """打印标题"""
    print(f"\n{'='*80}")
    print(f"🤖 {title}")
    print(f"{'='*80}")

def print_section(title):
    """打印章节"""
    print(f"\n{'─'*60}")
    print(f"📋 {title}")
    print(f"{'─'*60}")

def print_step(step, description):
    """打印步骤"""
    print(f"\n🔸 步骤 {step}: {description}")

def print_success(message):
    """打印成功消息"""
    print(f"✅ {message}")

def print_info(message):
    """打印信息"""
    print(f"ℹ️  {message}")

def print_thinking(message):
    """打印思考过程"""
    print(f"🧠 {message}")

def print_decision(message):
    """打印决策信息"""
    print(f"💡 {message}")

async def test_complete_workflow():
    """测试完整的AI Agent决策工作流程"""
    
    print_header("AI Agent 完整决策工作流程测试")
    
    # 测试场景
    human_intent = "基于历史极端天气数据，调整1月7日早高峰和晚高峰的电力消费预测"
    human_reasoning = """通过分析上下文信息中的历史极端天气场景，我发现在极端天气条件下，早高峰(7-9点)和晚高峰(18-20点)的电力需求会显著增加。特别是供暖负荷在这些时段会叠加正常的商业和居民用电需求。考虑到1月7日是极寒天气，我认为需要对这些关键时段进行上调，以避免供电不足的风险。"""
    
    print_section("测试场景设置")
    print_info(f"人类决策意图: {human_intent}")
    print_info(f"人类推理过程: {human_reasoning}")
    
    try:
        # 导入AI Agent
        from ai_agent.core.agent import DecisionCoPilot
        from ai_agent.config.settings import get_settings
        
        print_section("初始化AI Agent")
        
        # 检查配置
        settings = get_settings()
        print_info(f"使用模型: {settings.gemini_model}")
        print_info(f"最大思考循环: {settings.max_thinking_loops}")
        print_info(f"API密钥配置: {'是' if settings.gemini_api_key else '否'}")
        
        # 创建AI Agent
        agent = DecisionCoPilot()
        print_success("AI Agent初始化成功")
        
        print_section("开始决策处理")
        start_time = time.time()
        
        # 处理人类决策
        print_step(1, "AI Agent接收人类决策意图")
        print_thinking("开始分析人类的决策意图和推理...")
        
        results = await agent.process_human_decision(
            human_decision_intent=human_intent,
            human_reasoning=human_reasoning,
            session_id="complete-workflow-test"
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print_success(f"决策处理完成，耗时: {processing_time:.2f}秒")
        
        # 分析结果
        print_section("决策过程分析")
        
        print_step(2, "思考过程分析")
        thinking_steps = results.get('thinking_steps', 0)
        loop_count = results.get('loop_count', 0)
        print_info(f"总思考步骤: {thinking_steps}")
        print_info(f"循环次数: {loop_count}")
        print_info(f"是否完成: {results.get('is_complete', False)}")
        
        # 显示思考历史
        thinking_history = results.get('thinking_history', [])
        if thinking_history:
            print_thinking("AI Agent思考轨迹:")
            for i, thought in enumerate(thinking_history, 1):
                print(f"   {i}. {thought}")
        
        print_step(3, "信息访问分析")
        accessed_info = results.get('accessed_info', {})
        print_info("已访问的信息源:")
        for source, accessed in accessed_info.items():
            status = "✅" if accessed else "❌"
            print(f"   {status} {source}")
        
        print_step(4, "分析结果")
        analysis_results = results.get('analysis_results', {})
        identified_patterns = results.get('identified_patterns', [])
        
        if analysis_results:
            print_info("分析结果概要:")
            if 'patterns_identified' in analysis_results:
                print("   识别的模式:")
                for pattern in analysis_results['patterns_identified']:
                    print(f"     • {pattern}")
            
            if 'risk_assessment' in analysis_results:
                risk_assessment = analysis_results['risk_assessment']
                print("   风险评估:")
                for level, risks in risk_assessment.items():
                    if risks:
                        print(f"     {level.upper()}: {', '.join(risks)}")
        
        if identified_patterns:
            print_info("识别的关键模式:")
            for pattern in identified_patterns:
                print(f"   • {pattern}")
        
        print_section("决策结果")
        
        print_step(5, "决策策略")
        decision_strategy = results.get('decision_strategy')
        if decision_strategy:
            print_decision("AI Agent决策策略:")
            print(f"   方法: {decision_strategy.get('approach', 'N/A')}")
            print(f"   目标时段: {decision_strategy.get('target_hours', [])}")
            print(f"   调整类型: {decision_strategy.get('adjustment_type', 'N/A')}")
        
        print_step(6, "具体调整计划")
        adjustment_plan = results.get('adjustment_plan', {})
        final_adjustments = results.get('final_adjustments', {})
        
        adjustments_to_show = final_adjustments or adjustment_plan
        
        if adjustments_to_show:
            print_decision("具体调整建议:")
            total_adjustments = 0
            total_increase = 0
            
            for hour_key, adjustment in adjustments_to_show.items():
                if isinstance(adjustment, dict):
                    original = adjustment.get('original', 0)
                    adjusted = adjustment.get('adjusted', 0)
                    reason = adjustment.get('reason', 'N/A')
                    
                    if original and adjusted:
                        increase = adjusted - original
                        percentage = (increase / original) * 100
                        total_adjustments += 1
                        total_increase += increase
                        
                        print(f"   {hour_key}: {original} MW → {adjusted} MW (+{increase} MW, +{percentage:.1f}%)")
                        print(f"      理由: {reason}")
            
            if total_adjustments > 0:
                avg_increase = total_increase / total_adjustments
                print_info(f"总调整时段: {total_adjustments}个")
                print_info(f"平均增加: {avg_increase:.1f} MW")
        
        print_step(7, "置信度和建议")
        confidence_level = results.get('confidence_level', 0)
        print_info(f"AI Agent置信度: {confidence_level:.1%}")
        
        recommendations = results.get('recommendations', [])
        if recommendations:
            print_decision("AI Agent建议:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print_step(8, "推理解释")
        reasoning_explanation = results.get('reasoning_explanation', '')
        if reasoning_explanation:
            print_decision("完整推理解释:")
            print("─" * 60)
            print(reasoning_explanation)
            print("─" * 60)
        
        # 错误检查
        error_messages = results.get('error_messages', [])
        if error_messages:
            print_section("错误信息")
            for error in error_messages:
                print(f"❌ {error}")
        
        print_section("测试总结")
        print_success("✨ 完整工作流程测试成功完成！")
        print_info(f"总处理时间: {processing_time:.2f}秒")
        print_info(f"会话ID: {results.get('session_id', 'N/A')}")
        
        # 评估结果质量
        quality_score = 0
        max_score = 7
        
        if results.get('is_complete'): quality_score += 1
        if thinking_steps > 0: quality_score += 1
        if any(accessed_info.values()): quality_score += 1
        if analysis_results: quality_score += 1
        if decision_strategy: quality_score += 1
        if adjustments_to_show: quality_score += 1
        if recommendations: quality_score += 1
        
        print_info(f"结果质量评分: {quality_score}/{max_score} ({quality_score/max_score*100:.1f}%)")
        
        if quality_score >= 6:
            print_success("🎉 AI Agent表现优秀！")
        elif quality_score >= 4:
            print_info("👍 AI Agent表现良好")
        else:
            print("⚠️ AI Agent需要改进")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_scenarios():
    """测试多个决策场景"""
    
    print_header("多场景决策测试")
    
    scenarios = [
        {
            "name": "极寒天气早高峰调整",
            "intent": "根据极寒天气调整早高峰电力预测",
            "reasoning": "极寒天气下供暖需求激增，早高峰时段(7-9点)需要特别关注"
        },
        {
            "name": "晚高峰保守调整",
            "intent": "对晚高峰时段进行保守的预测调整",
            "reasoning": "考虑到数据的不确定性，对晚高峰(18-20点)进行适度保守调整"
        },
        {
            "name": "全天候综合调整",
            "intent": "基于SHAP分析结果进行全天候预测优化",
            "reasoning": "利用模型解释性分析，对重要时段进行数据驱动的调整"
        }
    ]
    
    from ai_agent.core.agent import DecisionCoPilot
    agent = DecisionCoPilot()
    
    for i, scenario in enumerate(scenarios, 1):
        print_section(f"场景 {i}: {scenario['name']}")
        print_info(f"意图: {scenario['intent']}")
        print_info(f"推理: {scenario['reasoning']}")
        
        try:
            results = await agent.process_human_decision(
                human_decision_intent=scenario['intent'],
                human_reasoning=scenario['reasoning'],
                session_id=f"scenario-{i}"
            )
            
            print_success(f"场景 {i} 处理完成")
            print_info(f"思考步骤: {results.get('thinking_steps', 0)}")
            print_info(f"置信度: {results.get('confidence_level', 0):.1%}")
            
            adjustments = results.get('final_adjustments') or results.get('adjustment_plan', {})
            if adjustments:
                print_info(f"调整时段数: {len(adjustments)}")
            
        except Exception as e:
            print(f"❌ 场景 {i} 处理失败: {e}")

async def main():
    """主函数"""
    
    print_header("AI Agent 完整工作流程测试套件")
    print_info(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试1: 完整工作流程
    print("\n" + "="*80)
    print("🧪 测试1: 完整决策工作流程")
    success1 = await test_complete_workflow()
    
    # 测试2: 多场景测试
    print("\n" + "="*80)
    print("🧪 测试2: 多场景决策测试")
    try:
        await test_multiple_scenarios()
        success2 = True
    except Exception as e:
        print(f"❌ 多场景测试失败: {e}")
        success2 = False
    
    # 总结
    print_header("测试套件总结")
    print_info(f"测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success1 and success2:
        print_success("🎉 所有测试成功完成！AI Agent工作流程正常！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试脚本出错: {e}")
        sys.exit(1)
