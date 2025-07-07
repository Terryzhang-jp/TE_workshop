#!/usr/bin/env python3
"""
简化版AI Agent工作流程测试

这个脚本测试AI Agent的核心决策流程，不依赖Gemini API。
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

def print_decision(message):
    """打印决策信息"""
    print(f"💡 {message}")

async def simulate_ai_agent_workflow():
    """模拟AI Agent完整工作流程"""
    
    print_header("AI Agent 简化工作流程演示")
    
    # 测试场景
    human_intent = "基于历史极端天气数据，调整1月7日早高峰和晚高峰的电力消费预测"
    human_reasoning = """通过分析上下文信息中的历史极端天气场景，我发现在极端天气条件下，早高峰(7-9点)和晚高峰(18-20点)的电力需求会显著增加。特别是供暖负荷在这些时段会叠加正常的商业和居民用电需求。考虑到1月7日是极寒天气，我认为需要对这些关键时段进行上调，以避免供电不足的风险。"""
    
    print_section("输入场景")
    print_info(f"人类决策意图: {human_intent}")
    print_info(f"人类推理: {human_reasoning}")
    
    # 步骤1: 初始化状态
    print_step(1, "初始化AI Agent状态")
    
    from ai_agent.core.state import create_initial_state, ActionType
    
    state = create_initial_state(
        human_decision_intent=human_intent,
        human_reasoning=human_reasoning,
        session_id="workflow-demo",
        max_loops=10
    )
    
    print_success("状态初始化完成")
    print_info(f"会话ID: {state['session_id']}")
    print_info(f"初始思考步骤: {state['thinking_step']}")
    
    # 步骤2: 数据访问模拟
    print_step(2, "访问实验数据")
    
    from ai_agent.data_access.experiment_data import ExperimentDataAccess
    
    data_access = ExperimentDataAccess("experiment_data")
    
    # 访问所有数据源
    print_info("正在访问上下文信息...")
    contextual_info = data_access.get_contextual_information()
    print_success(f"上下文信息加载完成: {len(contextual_info)} 个键")
    
    print_info("正在访问数据分析信息...")
    data_info = data_access.get_data_analysis_information()
    print_success(f"数据分析信息加载完成: {len(data_info)} 个键")
    
    print_info("正在访问模型解释性信息...")
    model_info = data_access.get_model_interpretability_information()
    print_success(f"模型解释性信息加载完成: {len(model_info)} 个键")
    
    print_info("正在访问用户预测信息...")
    prediction_info = data_access.get_user_prediction_information()
    print_success(f"用户预测信息加载完成: {len(prediction_info)} 个键")
    
    # 更新状态
    state['accessed_info'] = {
        'contextual_information': True,
        'data_analysis': True,
        'model_interpretability': True,
        'user_prediction': True
    }
    state['contextual_info'] = contextual_info
    state['data_analysis_info'] = data_info
    state['model_interpretability_info'] = model_info
    state['user_prediction_info'] = prediction_info
    
    # 步骤3: 分析处理
    print_step(3, "数据分析和模式识别")
    
    # 模拟分析过程
    print_info("分析历史极端天气场景...")
    historical_scenarios = contextual_info.get('historical_scenarios', [])
    extreme_scenarios = [s for s in historical_scenarios if s.get('temperature_celsius', 0) > 35]
    print_success(f"识别到 {len(extreme_scenarios)} 个极端天气场景")
    
    print_info("分析SHAP特征重要性...")
    shap_data = model_info.get('shap_analysis', {})
    feature_importance = shap_data.get('shap_analysis', {}).get('feature_importance_ranking', [])
    print_success(f"获取到 {len(feature_importance)} 个特征重要性排名")
    
    # 显示关键发现
    if feature_importance:
        print_info("特征重要性排名:")
        for feature in feature_importance[:3]:
            print(f"   • {feature.get('feature', 'N/A')}: {feature.get('percentage', 0)}%")
    
    print_info("分析基线预测数据...")
    baseline_predictions = prediction_info.get('baseline_predictions', [])
    morning_peak = [p for p in baseline_predictions if p.get('hour', 0) in [7, 8, 9]]
    evening_peak = [p for p in baseline_predictions if p.get('hour', 0) in [18, 19, 20]]
    
    print_success(f"识别早高峰时段: {len(morning_peak)} 个小时")
    print_success(f"识别晚高峰时段: {len(evening_peak)} 个小时")
    
    # 更新分析结果
    state['analysis_results'] = {
        'extreme_weather_scenarios': len(extreme_scenarios),
        'feature_importance_analyzed': len(feature_importance),
        'peak_periods_identified': len(morning_peak) + len(evening_peak),
        'patterns_identified': [
            "早高峰时段(7-9点)需求模式",
            "晚高峰时段(18-20点)需求模式", 
            "极端天气下的需求增长模式",
            "Hour特征的高重要性(44.6%)"
        ],
        'risk_assessment': {
            'high': [],
            'medium': ['温度特征重要性较低(3.4%)', '极寒天气数据有限'],
            'low': ['时间模式特征稳定', '历史数据充足']
        }
    }
    
    state['identified_patterns'] = state['analysis_results']['patterns_identified']
    
    # 步骤4: 决策制定
    print_step(4, "AI决策制定")
    
    print_info("基于分析结果制定调整策略...")
    
    # 模拟决策过程
    decision_strategy = {
        'approach': '基于极端天气历史数据和特征重要性的保守调整策略',
        'target_hours': [7, 8, 9, 18, 19, 20],
        'adjustment_type': '适度增加',
        'reasoning': '考虑到极寒天气对供暖需求的影响，以及Hour特征的高重要性，对关键时段进行保守上调'
    }
    
    print_decision("决策策略制定完成:")
    print(f"   方法: {decision_strategy['approach']}")
    print(f"   目标时段: {decision_strategy['target_hours']}")
    print(f"   调整类型: {decision_strategy['adjustment_type']}")
    
    # 生成具体调整
    adjustment_plan = {}
    
    # 早高峰调整
    for hour in [7, 8, 9]:
        baseline = next((p for p in baseline_predictions if p.get('hour') == hour), None)
        if baseline:
            original = baseline.get('predicted_power_mw', 0)
            # 基于极寒天气增加2-3%
            adjustment_factor = 1.025 if hour == 7 else 1.03 if hour == 8 else 1.025
            adjusted = int(original * adjustment_factor)
            
            adjustment_plan[f'hour_{hour}'] = {
                'original': original,
                'adjusted': adjusted,
                'increase': adjusted - original,
                'percentage': ((adjusted - original) / original) * 100,
                'reason': f'早高峰极寒天气供暖需求增加'
            }
    
    # 晚高峰调整
    for hour in [18, 19, 20]:
        baseline = next((p for p in baseline_predictions if p.get('hour') == hour), None)
        if baseline:
            original = baseline.get('predicted_power_mw', 0)
            # 晚高峰调整稍微保守一些
            adjustment_factor = 1.02 if hour == 18 else 1.025 if hour == 19 else 1.015
            adjusted = int(original * adjustment_factor)
            
            adjustment_plan[f'hour_{hour}'] = {
                'original': original,
                'adjusted': adjusted,
                'increase': adjusted - original,
                'percentage': ((adjusted - original) / original) * 100,
                'reason': f'晚高峰居民供暖需求增加'
            }
    
    state['decision_strategy'] = decision_strategy
    state['adjustment_plan'] = adjustment_plan
    state['confidence_level'] = 0.82
    
    # 步骤5: 执行和输出
    print_step(5, "生成最终建议")
    
    print_decision("具体调整计划:")
    total_increase = 0
    adjustment_count = 0
    
    for hour_key, adjustment in adjustment_plan.items():
        hour = hour_key.split('_')[1]
        original = adjustment['original']
        adjusted = adjustment['adjusted']
        increase = adjustment['increase']
        percentage = adjustment['percentage']
        reason = adjustment['reason']
        
        print(f"   {hour}:00 - {original} MW → {adjusted} MW (+{increase} MW, +{percentage:.1f}%)")
        print(f"      理由: {reason}")
        
        total_increase += increase
        adjustment_count += 1
    
    # 生成建议
    recommendations = [
        f"对{adjustment_count}个关键时段进行适度上调，总增加{total_increase} MW",
        "重点关注早高峰(7-9点)和晚高峰(18-20点)的供暖负荷叠加效应",
        "建议在实际运行中密切监控极寒天气下的实际消费情况",
        "考虑建立极端天气预警机制，提前调整预测模型参数",
        "定期更新模型训练数据，包含更多极端天气场景"
    ]
    
    reasoning_explanation = f"""
AI Agent 决策分析报告

人类决策意图: {human_intent}

决策过程:
1. 数据访问: 成功访问所有4个信息源
2. 模式识别: 识别到{len(state['identified_patterns'])}个关键模式
3. 风险评估: 中等风险{len(state['analysis_results']['risk_assessment']['medium'])}项
4. 策略制定: 保守调整策略，关注关键时段
5. 具体调整: {adjustment_count}个时段，平均增加{total_increase/adjustment_count:.1f} MW

关键发现:
• Hour特征重要性最高(44.6%)，时间模式是预测的关键
• 温度特征重要性较低(3.4%)，但极端条件下影响显著
• 历史极端天气数据显示需求可增加20-35%
• 早晚高峰时段是调整的重点目标

调整策略:
• 早高峰(7-9点): 平均增加2.7%，考虑商业和供暖双重需求
• 晚高峰(18-20点): 平均增加2.0%，重点关注居民供暖需求
• 总体策略: 保守调整，避免过度预测

置信度: {state['confidence_level']:.1%}
"""
    
    state['final_adjustments'] = adjustment_plan
    state['recommendations'] = recommendations
    state['reasoning_explanation'] = reasoning_explanation.strip()
    state['is_complete'] = True
    
    print_success("最终建议生成完成")
    print_info(f"置信度: {state['confidence_level']:.1%}")
    print_info(f"建议数量: {len(recommendations)}")
    
    # 步骤6: 结果展示
    print_section("AI Agent 最终输出")
    
    print_decision("推荐建议:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    print_decision("完整推理解释:")
    print("─" * 60)
    print(reasoning_explanation)
    print("─" * 60)
    
    # 总结
    print_section("工作流程总结")
    print_success("✨ AI Agent 决策流程演示完成！")
    
    processing_summary = {
        '数据源访问': '4/4 完成',
        '模式识别': f"{len(state['identified_patterns'])} 个模式",
        '调整时段': f"{adjustment_count} 个时段",
        '总增加量': f"{total_increase} MW",
        '平均增幅': f"{total_increase/adjustment_count:.1f} MW",
        '置信度': f"{state['confidence_level']:.1%}",
        '建议数量': f"{len(recommendations)} 条"
    }
    
    print_info("处理结果统计:")
    for key, value in processing_summary.items():
        print(f"   • {key}: {value}")
    
    return state

async def main():
    """主函数"""
    
    print_header("AI Agent 工作流程演示")
    print_info(f"演示开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        start_time = time.time()
        final_state = await simulate_ai_agent_workflow()
        end_time = time.time()
        
        print_header("演示总结")
        print_success(f"🎉 演示成功完成！")
        print_info(f"总耗时: {end_time - start_time:.2f}秒")
        print_info(f"会话ID: {final_state.get('session_id', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 演示脚本出错: {e}")
        sys.exit(1)
