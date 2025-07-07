#!/usr/bin/env python3
"""
严格数据使用测试 - 确保AI Agent只使用实际数据，不进行推测
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

async def test_strict_data_usage():
    """严格数据使用测试"""
    print("🔍 严格数据使用测试")
    print("="*60)
    
    # 加载环境变量
    load_env_file()
    
    # 故意使用与实际数据不符的用户输入来测试AI Agent是否会被误导
    test_request = {
        "intention": "分析明天35°C高温天气对电力需求的影响",  # 故意错误的场景
        "reasoning": "根据气象预报，明天将是炎热的夏日，空调负荷会激增",  # 故意错误的推理
        "options": {
            "max_iterations": 3,
            "timeout_seconds": 120,
            "include_debug": True,
            "structured_output": True
        }
    }
    
    print("🎯 测试目标: 验证AI Agent是否会被用户输入误导")
    print(f"📝 故意错误的用户输入: {test_request['intention']}")
    print(f"🧠 故意错误的用户推理: {test_request['reasoning']}")
    print("✅ 期望结果: AI Agent应该基于实际数据（2022年1月7日冬季大雪）进行分析")
    
    try:
        start_time = time.time()
        data_consistency_check = {
            "mentioned_summer": False,
            "mentioned_winter": False,
            "mentioned_35c": False,
            "mentioned_snow": False,
            "mentioned_jan_7": False,
            "mentioned_2022": False,
            "used_actual_data": False
        }
        
        print("\n🔄 开始严格测试...")
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
                            print(f"🚀 会话开始: {event_data.get('session_id')}")
                            
                        elif event_type == 'thinking_step_complete':
                            print(f"\n📋 步骤 {step_number} - 迭代 {iteration} ({elapsed:.1f}s)")
                            
                            structured_step = data.get('structured_step', {})
                            thinking_content = structured_step.get('thinking_content', '')
                            new_insights = structured_step.get('new_insights', [])
                            
                            # 检查AI Agent是否使用了实际数据
                            content_lower = thinking_content.lower()
                            
                            # 检查错误内容（基于用户输入的假设）
                            if '35°c' in content_lower or '35度' in content_lower or '高温' in content_lower:
                                data_consistency_check["mentioned_35c"] = True
                                print(f"   ⚠️ 发现提及35°C高温（错误）")
                            
                            if '夏' in content_lower or 'summer' in content_lower:
                                data_consistency_check["mentioned_summer"] = True
                                print(f"   ⚠️ 发现提及夏季（错误）")
                            
                            # 检查正确内容（基于实际数据）
                            if '雪' in content_lower or 'snow' in content_lower or '大雪' in content_lower:
                                data_consistency_check["mentioned_snow"] = True
                                print(f"   ✅ 发现提及大雪（正确）")
                            
                            if '冬' in content_lower or 'winter' in content_lower or '低温' in content_lower:
                                data_consistency_check["mentioned_winter"] = True
                                print(f"   ✅ 发现提及冬季（正确）")
                            
                            if '1月7日' in content_lower or 'january 7' in content_lower:
                                data_consistency_check["mentioned_jan_7"] = True
                                print(f"   ✅ 发现提及1月7日（正确）")
                            
                            if '2022' in content_lower:
                                data_consistency_check["mentioned_2022"] = True
                                print(f"   ✅ 发现提及2022年（正确）")
                            
                            # 检查是否引用了具体数据
                            if '数据来源' in thinking_content or '基于' in thinking_content:
                                data_consistency_check["used_actual_data"] = True
                                print(f"   ✅ 发现引用实际数据")
                            
                            # 显示思考内容摘要
                            print(f"   💭 思考摘要: {thinking_content[:150]}...")
                            
                            # 显示洞察
                            if new_insights:
                                print(f"   💡 新洞察 ({len(new_insights)}个):")
                                for insight in new_insights:
                                    content = insight.get('content', '')
                                    print(f"      • {content[:100]}...")
                            
                        elif event_type == 'process_complete':
                            print(f"\n🎉 流程完成!")
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
        print("📊 数据一致性检查结果")
        print("="*60)
        
        # 分析结果
        errors = []
        successes = []
        
        if data_consistency_check["mentioned_35c"]:
            errors.append("❌ AI Agent提及了35°C高温（应该基于实际数据：-3.5°C低温）")
        else:
            successes.append("✅ AI Agent没有被用户输入的35°C误导")
            
        if data_consistency_check["mentioned_summer"]:
            errors.append("❌ AI Agent提及了夏季（应该基于实际数据：冬季）")
        else:
            successes.append("✅ AI Agent没有被用户输入的夏季场景误导")
            
        if data_consistency_check["mentioned_snow"]:
            successes.append("✅ AI Agent正确识别了大雪天气（基于实际数据）")
        else:
            errors.append("❌ AI Agent没有识别实际的大雪天气")
            
        if data_consistency_check["mentioned_winter"]:
            successes.append("✅ AI Agent正确识别了冬季（基于实际数据）")
        else:
            errors.append("❌ AI Agent没有识别实际的冬季场景")
            
        if data_consistency_check["mentioned_jan_7"]:
            successes.append("✅ AI Agent正确识别了1月7日（基于实际数据）")
        else:
            errors.append("❌ AI Agent没有识别实际的日期")
            
        if data_consistency_check["mentioned_2022"]:
            successes.append("✅ AI Agent正确识别了2022年（基于实际数据）")
        else:
            errors.append("❌ AI Agent没有识别实际的年份")
            
        if data_consistency_check["used_actual_data"]:
            successes.append("✅ AI Agent引用了实际数据")
        else:
            errors.append("❌ AI Agent没有明确引用实际数据")
        
        print(f"⏱️ 总测试时间: {total_time:.1f}秒")
        print(f"\n🎯 测试结果:")
        
        for success in successes:
            print(f"  {success}")
        
        for error in errors:
            print(f"  {error}")
        
        # 判断测试是否通过
        critical_errors = [
            data_consistency_check["mentioned_35c"],
            data_consistency_check["mentioned_summer"]
        ]
        
        critical_successes = [
            data_consistency_check["mentioned_snow"] or data_consistency_check["mentioned_winter"],
            data_consistency_check["mentioned_jan_7"] or data_consistency_check["mentioned_2022"]
        ]
        
        if any(critical_errors):
            print(f"\n❌ 测试失败: AI Agent被用户输入误导，没有使用实际数据")
            return False
        elif all(critical_successes):
            print(f"\n✅ 测试通过: AI Agent正确使用了实际数据，没有被用户输入误导")
            return True
        else:
            print(f"\n⚠️ 测试部分通过: AI Agent没有被误导，但数据使用不够明确")
            return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    success = await test_strict_data_usage()
    
    print("\n" + "="*60)
    print("🎯 最终结果")
    print("="*60)
    
    if success:
        print("🎉 AI Agent严格数据使用测试通过!")
        print("💡 AI Agent能够正确使用实际数据，不被用户输入误导")
    else:
        print("❌ AI Agent严格数据使用测试失败")
        print("💡 需要进一步加强数据约束和提示词")

if __name__ == "__main__":
    asyncio.run(main())
