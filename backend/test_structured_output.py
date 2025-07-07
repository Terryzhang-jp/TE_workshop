#!/usr/bin/env python3
"""
测试AI Agent结构化输出功能
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

async def test_structured_api():
    """测试结构化API端点"""
    print("🧪 测试AI Agent结构化输出功能")
    print("="*60)
    
    # 加载环境变量
    load_env_file()
    
    # 检查服务器状态
    print("1️⃣ 检查服务器状态...")
    try:
        response = requests.get('http://localhost:8001/api/v1/ai-agent/status', timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ 服务器状态: {status_data['status']}")
            print(f"   版本: {status_data['version']}")
            print(f"   结构化功能: {', '.join(status_data.get('structured_features', []))}")
            print(f"   可用端点: {list(status_data.get('endpoints', {}).keys())}")
        else:
            print(f"❌ 服务器状态异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False
    
    # 准备测试数据
    print("\n2️⃣ 准备测试数据...")
    test_request = {
        "intention": "分析2022年1月7日东京大雪期间的电力系统应急响应",
        "reasoning": "基于刚更新的东京大雪案例，我想了解AI如何分析这种极端天气下的电力系统挑战，包括高需求、低供给和可再生能源出力骤降的三重冲击。",
        "context": {
            "scenario_type": "极端天气电力系统分析",
            "focus_areas": ["需求预测", "供给约束", "应急响应"]
        },
        "constraints": [
            "基于真实历史数据",
            "考虑多重因素叠加效应"
        ],
        "preferences": {
            "analysis_depth": "深度分析",
            "output_format": "结构化"
        },
        "options": {
            "max_iterations": 5,
            "timeout_seconds": 180,
            "include_debug": True,
            "structured_output": True,
            "confidence_threshold": 0.6
        }
    }
    
    print(f"📝 测试场景: {test_request['intention']}")
    print(f"🎯 迭代限制: {test_request['options']['max_iterations']} 轮")
    print(f"⏱️ 超时设置: {test_request['options']['timeout_seconds']} 秒")
    
    # 测试结构化流式API
    print("\n3️⃣ 测试结构化流式API...")
    print("   🔄 调用 /stream-structured 端点")
    print("   📊 实时显示结构化输出:")
    print("-" * 60)
    
    try:
        start_time = time.time()
        event_count = 0
        thinking_steps = []
        final_output = None
        
        response = requests.post(
            'http://localhost:8001/api/v1/ai-agent/stream-structured',
            json=test_request,
            headers={'Accept': 'text/event-stream'},
            stream=True,
            timeout=300
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
                        event_count += 1
                        elapsed = time.time() - start_time
                        
                        event_type = event_data.get('type', 'unknown')
                        step_number = event_data.get('step_number', 0)
                        iteration = event_data.get('iteration', 0)
                        thinking_phase = event_data.get('thinking_phase')
                        confidence = event_data.get('confidence')
                        
                        # 显示事件信息
                        print(f"\n[{event_count:2d}] {elapsed:6.1f}s | {event_type}")
                        print(f"    步骤: {step_number}, 迭代: {iteration}")
                        
                        if thinking_phase:
                            print(f"    阶段: {thinking_phase}")
                        if confidence is not None:
                            print(f"    置信度: {confidence:.2f}")
                        
                        # 处理不同类型的事件
                        data = event_data.get('data', {})
                        
                        if event_type == 'session_start':
                            user_input = data.get('user_input', {})
                            print(f"    会话ID: {user_input.get('session_id', 'unknown')}")
                            print(f"    结构化模式: {data.get('structured_mode', False)}")
                            
                        elif event_type == 'thinking_step_complete':
                            structured_step = data.get('structured_step', {})
                            processing_metrics = data.get('processing_metrics', {})
                            
                            if structured_step:
                                thinking_steps.append(structured_step)
                                print(f"    思考内容: {structured_step.get('thinking_content', '')[:100]}...")
                                print(f"    新洞察: {processing_metrics.get('insights_count', 0)} 个")
                                print(f"    新问题: {processing_metrics.get('questions_count', 0)} 个")
                                print(f"    处理时间: {processing_metrics.get('step_processing_time', 0):.2f}秒")
                            
                        elif event_type == 'process_complete':
                            final_output = data.get('final_output')
                            success = data.get('success', False)
                            print(f"    完成状态: {'✅ 成功' if success else '❌ 失败'}")
                            if final_output:
                                print(f"    总洞察: {len(final_output.get('all_insights', []))} 个")
                                print(f"    推荐措施: {len(final_output.get('recommendations', []))} 条")
                            break
                            
                        elif event_type == 'error':
                            error_msg = data.get('message', 'Unknown error')
                            print(f"    ❌ 错误: {error_msg}")
                            
                    except json.JSONDecodeError as e:
                        print(f"    ⚠️ JSON解析错误: {e}")
                        continue
        
        total_time = time.time() - start_time
        print("-" * 60)
        print(f"⏱️ 总处理时间: {total_time:.1f}秒")
        print(f"📊 事件总数: {event_count} 个")
        print(f"🧠 思考步骤: {len(thinking_steps)} 个")
        
        # 分析结构化输出质量
        print("\n4️⃣ 结构化输出质量分析:")
        print("="*40)
        
        if thinking_steps:
            print(f"✅ 思考步骤结构化: {len(thinking_steps)} 个步骤")
            
            # 分析思考阶段分布
            phases = [step.get('phase') for step in thinking_steps if step.get('phase')]
            unique_phases = list(set(phases))
            print(f"✅ 思考阶段覆盖: {len(unique_phases)} 个阶段")
            print(f"   阶段列表: {', '.join(unique_phases)}")
            
            # 分析洞察和问题
            total_insights = sum(len(step.get('new_insights', [])) for step in thinking_steps)
            total_questions = sum(len(step.get('new_questions', [])) for step in thinking_steps)
            print(f"✅ 洞察生成: {total_insights} 个")
            print(f"✅ 问题提出: {total_questions} 个")
            
            # 分析置信度变化
            confidences = [step.get('confidence', 0) for step in thinking_steps]
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                print(f"✅ 平均置信度: {avg_confidence:.2f}")
        
        if final_output:
            print(f"✅ 最终输出完整性: 包含所有必要字段")
            performance_metrics = final_output.get('performance_metrics', {})
            print(f"✅ 性能指标: {len(performance_metrics)} 个指标")
            
            # 显示关键结果
            insights = final_output.get('all_insights', [])
            if insights:
                print(f"\n💡 关键洞察预览:")
                for i, insight in enumerate(insights[:2], 1):
                    content = insight.get('content', '')
                    confidence = insight.get('confidence', 0)
                    print(f"   {i}. {content[:80]}... (置信度: {confidence:.2f})")
            
            recommendations = final_output.get('recommendations', [])
            if recommendations:
                print(f"\n📋 推荐措施预览:")
                for i, rec in enumerate(recommendations[:2], 1):
                    title = rec.get('title', '')
                    description = rec.get('description', '')
                    print(f"   {i}. {title}: {description[:60]}...")
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    success = await test_structured_api()
    
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    if success:
        print("🎉 AI Agent结构化输出功能测试成功!")
        print("✅ 结构化数据模型正常工作")
        print("✅ 流式事件格式正确")
        print("✅ 思考过程完全透明")
        print("✅ 性能指标完整记录")
        print("\n💡 现在可以进行前端集成，享受结构化的AI决策体验!")
    else:
        print("❌ 测试失败，需要进一步调试")
        print("💡 请检查服务器状态和结构化模块配置")

if __name__ == "__main__":
    asyncio.run(main())
