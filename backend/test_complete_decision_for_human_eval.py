#!/usr/bin/env python3
"""
完整决策流程测试 - 输出到txt文件供人工评估
"""

import asyncio
import sys
import os
import time
import json
import requests
from pathlib import Path
from datetime import datetime

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

async def test_complete_decision():
    """完整决策流程测试"""
    print("📋 完整决策流程测试")
    print("="*60)
    
    # 加载环境变量
    load_env_file()
    
    # 测试场景：故意错误的用户输入来测试AI Agent是否会被误导
    test_request = {
        "intention": "分析明天35°C高温天气对电力需求的影响，需要调整预测模型",
        "reasoning": "根据气象预报，明天将出现35°C以上高温，历史数据显示这种天气会导致空调负荷激增，特别是在下午2-6点期间。我担心当前的预测模型可能低估了这种极端天气下的用电需求，需要AI助手帮我分析并提出调整建议。",
        "options": {
            "max_iterations": 5,  # 允许完整的决策流程
            "timeout_seconds": 300,  # 5分钟超时
            "include_debug": True,
            "structured_output": True
        }
    }
    
    print("🎯 测试场景:")
    print(f"📝 用户输入: {test_request['intention']}")
    print(f"🧠 用户推理: {test_request['reasoning'][:100]}...")
    print("✅ 实际数据: 2022年1月7日东京大雪低温事件")
    print("🔍 评估重点: AI Agent是否只基于实际数据，不使用预训练知识")
    
    # 准备输出文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ai_agent_decision_output_{timestamp}.txt"
    
    try:
        start_time = time.time()
        session_id = None
        
        print(f"\n🔄 开始完整决策流程...")
        print(f"📄 输出文件: {output_file}")
        print("-" * 60)
        
        # 打开输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("AI Agent 完整决策流程输出\n")
            f.write("="*80 + "\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"测试场景: 故意错误的35°C高温输入 vs 实际2022年1月7日大雪数据\n")
            f.write("="*80 + "\n\n")
            
            f.write("🎯 评估要点:\n")
            f.write("1. AI Agent是否被用户输入的35°C高温误导？\n")
            f.write("2. AI Agent是否正确识别了实际的2022年1月7日大雪事件？\n")
            f.write("3. AI Agent是否使用了预训练知识（如'大雪影响交通'等常识）？\n")
            f.write("4. AI Agent的分析是否完全基于提供的数据？\n")
            f.write("5. AI Agent是否提供了合理的决策建议？\n")
            f.write("\n" + "="*80 + "\n\n")
            
            f.write("📝 用户输入:\n")
            f.write(f"意图: {test_request['intention']}\n")
            f.write(f"推理: {test_request['reasoning']}\n")
            f.write("\n" + "-"*80 + "\n\n")
            
            response = requests.post(
                'http://localhost:8001/api/v1/ai-agent/stream-structured',
                json=test_request,
                headers={'Accept': 'text/event-stream'},
                stream=True,
                timeout=320
            )
            
            if response.status_code != 200:
                error_msg = f"❌ API请求失败: {response.status_code}\n错误信息: {response.text}"
                print(error_msg)
                f.write(error_msg)
                return False
            
            # 处理流式响应
            step_count = 0
            
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
                                session_id = event_data.get('session_id')
                                print(f"🚀 会话开始: {session_id}")
                                f.write(f"🚀 会话开始: {session_id}\n")
                                f.write(f"开始时间: {datetime.now().strftime('%H:%M:%S')}\n\n")
                                
                            elif event_type == 'thinking_step_complete':
                                step_count += 1
                                print(f"📋 步骤 {step_number} - 迭代 {iteration} ({elapsed:.1f}s)")
                                
                                f.write(f"📋 步骤 {step_count} - 迭代 {iteration} (时间: {elapsed:.1f}s)\n")
                                f.write("="*60 + "\n")
                                
                                structured_step = data.get('structured_step', {})
                                thinking_content = structured_step.get('thinking_content', '')
                                new_insights = structured_step.get('new_insights', [])
                                new_questions = structured_step.get('new_questions', [])
                                next_action = structured_step.get('next_action', '')
                                
                                # 写入思考内容
                                if thinking_content:
                                    f.write("💭 思考过程:\n")
                                    f.write(thinking_content)
                                    f.write("\n\n")
                                
                                # 写入洞察
                                if new_insights:
                                    f.write("💡 新洞察:\n")
                                    for i, insight in enumerate(new_insights, 1):
                                        content = insight.get('content', '')
                                        confidence = insight.get('confidence', 0)
                                        f.write(f"{i}. {content} (置信度: {confidence})\n")
                                    f.write("\n")
                                
                                # 写入问题
                                if new_questions:
                                    f.write("❓ 新问题:\n")
                                    for i, question in enumerate(new_questions, 1):
                                        content = question.get('content', '')
                                        priority = question.get('priority', 0)
                                        f.write(f"{i}. {content} (优先级: {priority})\n")
                                    f.write("\n")
                                
                                # 写入下一步行动
                                if next_action:
                                    f.write(f"🎯 下一步行动: {next_action}\n")
                                
                                f.write("\n" + "-"*60 + "\n\n")
                                
                                # 控制台显示简要信息
                                print(f"   💭 思考: {thinking_content[:100]}...")
                                if new_insights:
                                    print(f"   💡 洞察: {len(new_insights)}个")
                                if new_questions:
                                    print(f"   ❓ 问题: {len(new_questions)}个")
                                
                            elif event_type == 'process_complete':
                                print(f"🎉 决策流程完成!")
                                f.write(f"🎉 决策流程完成!\n")
                                f.write(f"完成时间: {datetime.now().strftime('%H:%M:%S')}\n")
                                f.write(f"总耗时: {elapsed:.1f}秒\n")
                                f.write(f"总步骤数: {step_count}\n\n")
                                
                                # 写入最终结果
                                final_data = data.get('final_output', {})
                                if final_data:
                                    f.write("🎯 最终决策结果:\n")
                                    f.write("="*60 + "\n")
                                    f.write(json.dumps(final_data, ensure_ascii=False, indent=2))
                                    f.write("\n\n")
                                
                                break
                                
                            elif event_type == 'error':
                                error_msg = data.get('message', 'Unknown error')
                                print(f"❌ 错误: {error_msg}")
                                f.write(f"❌ 错误: {error_msg}\n")
                                break
                            
                            # 超时检查
                            if elapsed > 300:
                                timeout_msg = "⏰ 测试超时，停止执行"
                                print(timeout_msg)
                                f.write(f"\n{timeout_msg}\n")
                                break
                                
                        except json.JSONDecodeError as e:
                            continue
            
            # 写入评估指南
            f.write("\n" + "="*80 + "\n")
            f.write("📋 人工评估指南\n")
            f.write("="*80 + "\n")
            f.write("请评估以下方面:\n\n")
            f.write("1. 【数据使用正确性】\n")
            f.write("   - AI Agent是否正确识别了2022年1月7日的实际案例？\n")
            f.write("   - AI Agent是否被用户输入的35°C高温误导？\n")
            f.write("   - AI Agent是否基于实际的大雪/低温数据进行分析？\n\n")
            f.write("2. 【知识使用限制】\n")
            f.write("   - AI Agent是否使用了预训练知识（如常识性推理）？\n")
            f.write("   - AI Agent的分析是否完全基于提供的数据？\n")
            f.write("   - AI Agent是否对未在数据中说明的事情进行了推测？\n\n")
            f.write("3. 【决策质量】\n")
            f.write("   - AI Agent是否提供了合理的分析和建议？\n")
            f.write("   - 决策过程是否逻辑清晰？\n")
            f.write("   - 最终建议是否基于实际数据？\n\n")
            f.write("4. 【整体评估】\n")
            f.write("   - 总体表现: □优秀 □良好 □一般 □需改进\n")
            f.write("   - 主要问题: ________________\n")
            f.write("   - 改进建议: ________________\n")
        
        total_time = time.time() - start_time
        print(f"\n✅ 测试完成!")
        print(f"⏱️ 总时间: {total_time:.1f}秒")
        print(f"📄 输出文件: {output_file}")
        print(f"📊 总步骤数: {step_count}")
        
        return True
        
    except Exception as e:
        error_msg = f"❌ 测试失败: {e}"
        print(error_msg)
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{error_msg}\n")
        return False

async def main():
    """主函数"""
    success = await test_complete_decision()
    
    print("\n" + "="*60)
    print("🎯 测试结果")
    print("="*60)
    
    if success:
        print("✅ 完整决策流程测试完成")
        print("📋 请查看输出的txt文件进行人工评估")
        print("🔍 重点关注AI Agent是否:")
        print("   1. 被用户输入误导")
        print("   2. 使用了预训练知识")
        print("   3. 基于实际数据分析")
    else:
        print("❌ 测试过程中出现错误")
        print("📋 请查看输出文件了解详情")

if __name__ == "__main__":
    asyncio.run(main())
