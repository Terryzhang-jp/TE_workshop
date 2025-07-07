#!/usr/bin/env python3
"""
详细的结构化输出测试 - 查看AI Agent的完整决策过程
"""

import asyncio
import sys
import os
import time
import json
import requests
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

def load_env_file():
    """手动加载.env文件"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

async def test_detailed_structured():
    """详细的结构化测试"""
    print("🔍 详细结构化输出测试")
    print("="*60)
    
    # 加载环境变量
    load_env_file()
    
    # 测试数据
    test_request = {
        "intention": "分析明天35°C高温天气对电力需求的影响",
        "reasoning": "根据历史数据，高温天气会导致空调负荷激增，我担心当前预测模型可能低估了这种极端情况下的用电需求。需要AI助手帮我分析并提出调整建议。",
        "options": {
            "max_iterations": 5,
            "timeout_seconds": 180,
            "include_debug": True,
            "structured_output": True
        }
    }
    
    print(f"📝 测试场景: {test_request['intention']}")
    print(f"🧠 用户推理: {test_request['reasoning'][:100]}...")
    print(f"🎯 迭代限制: {test_request['options']['max_iterations']} 轮")
    
    try:
        start_time = time.time()
        session_data = {
            "session_id": None,
            "thinking_steps": [],
            "data_accessed": [],
            "insights": [],
            "questions": [],
            "plans": [],
            "actions": []
        }
        
        print("\n🔄 开始详细分析...")
        print("-" * 60)
        
        response = requests.post(
            'http://localhost:8001/api/v1/ai-agent/stream-structured',
            json=test_request,
            headers={'Accept': 'text/event-stream'},
            stream=True,
            timeout=200
        )
        
        if response.status_code != 200:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        
        # 处理流式响应
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        event_data = json.loads(line_str[6:])
                        elapsed = time.time() - start_time
                        
                        event_type = event_data.get('type', 'unknown')
                        step_number = event_data.get('step_number', 0)
                        iteration = event_data.get('iteration', 0)
                        data = event_data.get('data', {})
                        
                        if event_type == 'session_start':
                            session_data["session_id"] = event_data.get('session_id')
                            print(f"🚀 会话开始: {session_data['session_id']}")
                            
                        elif event_type == 'thinking_step_complete':
                            print(f"\n📋 步骤 {step_number} - 迭代 {iteration} ({elapsed:.1f}s)")
                            
                            structured_step = data.get('structured_step', {})
                            processing_metrics = data.get('processing_metrics', {})
                            
                            # 提取关键信息
                            phase = structured_step.get('phase', 'unknown')
                            thinking_content = structured_step.get('thinking_content', '')
                            actions_taken = structured_step.get('actions_taken', [])
                            next_action = structured_step.get('next_action', 'unknown')
                            new_insights = structured_step.get('new_insights', [])
                            new_questions = structured_step.get('new_questions', [])
                            plan = structured_step.get('plan', {})
                            
                            print(f"   🧠 思考阶段: {phase}")
                            print(f"   📊 置信度: {processing_metrics.get('confidence_level', 0):.2f}")
                            print(f"   ⏱️ 处理时间: {processing_metrics.get('step_processing_time', 0):.1f}秒")
                            
                            # 显示计划
                            if plan:
                                print(f"   📋 当前计划:")
                                print(f"      目标: {plan.get('objective', 'N/A')}")
                                print(f"      计划行动: {plan.get('planned_actions', [])}")
                            
                            # 显示已执行的行动
                            if actions_taken:
                                print(f"   ✅ 已执行行动: {actions_taken}")
                            
                            # 显示下一步行动
                            print(f"   ➡️ 下一步行动: {next_action}")
                            
                            # 显示新洞察
                            if new_insights:
                                print(f"   💡 新洞察 ({len(new_insights)}个):")
                                for insight in new_insights:
                                    content = insight.get('content', '')
                                    confidence = insight.get('confidence', 0)
                                    print(f"      • {content[:80]}... (置信度: {confidence:.2f})")
                            
                            # 显示新问题
                            if new_questions:
                                print(f"   ❓ 新问题 ({len(new_questions)}个):")
                                for question in new_questions:
                                    content = question.get('content', '')
                                    target_source = question.get('target_source', '')
                                    priority = question.get('priority', 0)
                                    print(f"      • {content[:80]}... (目标: {target_source}, 优先级: {priority:.2f})")
                            
                            # 显示思考内容摘要
                            if thinking_content:
                                print(f"   💭 思考摘要: {thinking_content[:100]}...")
                            
                            # 保存到会话数据
                            session_data["thinking_steps"].append(structured_step)
                            session_data["insights"].extend(new_insights)
                            session_data["questions"].extend(new_questions)
                            session_data["actions"].extend(actions_taken)
                            if plan:
                                session_data["plans"].append(plan)
                            
                        elif event_type == 'step_progress':
                            action = data.get('action', 'unknown')
                            print(f"   🔄 进度更新: {action}")
                            
                        elif event_type == 'process_complete':
                            print(f"\n🎉 流程完成!")
                            final_output = data.get('final_output', {})
                            if final_output:
                                print("📊 最终输出摘要:")
                                print(f"   总迭代数: {final_output.get('total_iterations', 0)}")
                                print(f"   最终置信度: {final_output.get('performance_metrics', {}).get('final_confidence', 0):.2f}")
                                print(f"   总洞察数: {final_output.get('performance_metrics', {}).get('total_insights_generated', 0)}")
                                print(f"   总问题数: {final_output.get('performance_metrics', {}).get('total_questions_raised', 0)}")
                            break
                            
                        elif event_type == 'error':
                            error_msg = data.get('message', 'Unknown error')
                            print(f"   ❌ 错误: {error_msg}")
                            break
                            
                        # 限制测试时间
                        if elapsed > 180:
                            print(f"   ⏰ 测试超时，停止")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"    ⚠️ JSON解析错误: {e}")
                        continue
        
        total_time = time.time() - start_time
        print("\n" + "="*60)
        print("📊 会话总结")
        print("="*60)
        print(f"🆔 会话ID: {session_data['session_id']}")
        print(f"⏱️ 总时间: {total_time:.1f}秒")
        print(f"🧠 思考步骤: {len(session_data['thinking_steps'])} 个")
        print(f"💡 总洞察: {len(session_data['insights'])} 个")
        print(f"❓ 总问题: {len(session_data['questions'])} 个")
        print(f"📋 计划数: {len(session_data['plans'])} 个")
        print(f"⚡ 行动数: {len(session_data['actions'])} 个")
        
        # 显示访问的数据源
        data_sources = set()
        for step in session_data['thinking_steps']:
            actions = step.get('actions_taken', [])
            for action in actions:
                if 'access' in action.lower():
                    data_sources.add(action)
        
        if data_sources:
            print(f"📊 访问的数据源: {list(data_sources)}")
        
        return len(session_data['thinking_steps']) > 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    success = await test_detailed_structured()
    
    print("\n" + "="*60)
    print("🎯 测试结果")
    print("="*60)
    
    if success:
        print("🎉 详细结构化输出功能正常!")
        print("💡 AI Agent的决策过程完全透明")
    else:
        print("❌ 详细结构化输出有问题")
        print("💡 需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())
