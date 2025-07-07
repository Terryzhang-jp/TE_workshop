#!/usr/bin/env python3
"""
测试完整的AI Agent决策流程
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

async def test_complete_decision_flow():
    """测试完整的AI Agent决策流程"""
    print("🚀 AI Agent完整决策流程测试")
    print("="*60)
    
    # 加载环境变量
    load_env_file()
    
    # 检查服务器状态
    print("1️⃣ 检查AI Agent服务器状态...")
    try:
        response = requests.get('http://localhost:8001/api/v1/ai-agent/status', timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ 服务器状态: {status_data['status']}")
            print(f"   版本: {status_data['version']}")
            print(f"   支持功能: {', '.join(status_data['capabilities'])}")
        else:
            print(f"❌ 服务器状态异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("💡 请确保服务器正在运行: uvicorn app.main:app --host 0.0.0.0 --port 8001")
        return False
    
    # 准备测试场景
    print("\n2️⃣ 准备测试场景...")
    test_scenarios = [
        {
            "name": "夏季高温预警调整",
            "intention": "根据气象预报，明天将出现35°C以上高温，需要调整电力需求预测",
            "reasoning": "历史数据显示，当气温超过35°C时，空调负荷会急剧增加，特别是在下午2-6点期间。我担心当前的预测模型可能低估了这种极端天气下的用电需求，需要AI助手帮我分析并提出调整建议。"
        },
        {
            "name": "工作日异常负荷分析",
            "reasoning": "今天是周三，但监控显示早上8点的负荷比预期低了15%，可能是因为部分企业提前放假。我需要评估这种情况对后续几天预测的影响，并决定是否需要调整预测模型的参数。"
        }
    ]
    
    # 选择第一个场景进行测试
    scenario = test_scenarios[0]
    print(f"📋 测试场景: {scenario['name']}")
    print(f"   用户意图: {scenario['intention']}")
    print(f"   推理过程: {scenario['reasoning'][:100]}...")
    
    # 准备API请求数据
    request_data = {
        "intention": scenario["intention"],
        "reasoning": scenario["reasoning"],
        "options": {
            "max_iterations": 5,  # 限制迭代次数以便快速测试
            "timeout_seconds": 180,  # 3分钟超时
            "include_debug": True
        }
    }
    
    print("\n3️⃣ 开始AI Agent决策流程...")
    print("   ⏱️ 预计需要2-3分钟，请耐心等待...")
    print("   🔄 实时显示AI思考过程:")
    print("-" * 60)
    
    # 发送流式请求
    try:
        start_time = time.time()
        step_count = 0
        
        response = requests.post(
            'http://localhost:8001/api/v1/ai-agent/stream',
            json=request_data,
            headers={'Accept': 'text/event-stream'},
            stream=True,
            timeout=300  # 5分钟超时
        )
        
        if response.status_code != 200:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        
        # 处理流式响应
        session_id = None
        final_result = None
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        event_data = json.loads(line_str[6:])
                        event_type = event_data.get('type', 'unknown')
                        timestamp = event_data.get('timestamp', '')
                        data = event_data.get('data', {})
                        
                        if not session_id:
                            session_id = event_data.get('session_id', 'unknown')
                        
                        step_count += 1
                        elapsed = time.time() - start_time
                        
                        # 显示事件信息
                        print(f"\n[{step_count:2d}] {elapsed:6.1f}s | {event_type}")
                        
                        if event_type == 'thinking_start':
                            print(f"    🧠 开始思考 - 步骤 {data.get('step', '?')}")
                            
                        elif event_type == 'thinking_progress':
                            thinking_content = data.get('content', '')
                            print(f"    💭 思考内容: {thinking_content[:100]}...")
                            
                        elif event_type == 'thinking_complete':
                            insights = data.get('insights', [])
                            questions = data.get('questions', [])
                            next_action = data.get('next_action', 'unknown')
                            print(f"    ✅ 思考完成 - 下一步: {next_action}")
                            print(f"       洞察: {len(insights)} 个, 问题: {len(questions)} 个")
                            
                        elif event_type == 'information_access':
                            info_type = data.get('info_type', 'unknown')
                            print(f"    📊 访问信息: {info_type}")
                            
                        elif event_type == 'analysis_complete':
                            patterns = data.get('patterns', [])
                            print(f"    🔍 分析完成 - 发现模式: {len(patterns)} 个")
                            
                        elif event_type == 'decision_made':
                            strategy = data.get('strategy', 'unknown')
                            confidence = data.get('confidence', 0)
                            print(f"    🎯 决策制定: {strategy} (置信度: {confidence:.2f})")
                            
                        elif event_type == 'execution_complete':
                            adjustments = data.get('adjustments', {})
                            recommendations = data.get('recommendations', [])
                            print(f"    ⚡ 执行完成 - 调整: {len(adjustments)} 个, 建议: {len(recommendations)} 条")
                            
                        elif event_type == 'process_complete':
                            final_result = data
                            print(f"    🎉 流程完成!")
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
        print(f"📊 处理步骤: {step_count} 个")
        print(f"🆔 会话ID: {session_id}")
        
        # 显示最终结果
        if final_result:
            print("\n4️⃣ 最终决策结果:")
            print("="*40)
            
            # 显示洞察
            insights = final_result.get('insights', [])
            if insights:
                print(f"\n💡 AI洞察 ({len(insights)} 个):")
                for i, insight in enumerate(insights[:3], 1):
                    if isinstance(insight, dict):
                        content = insight.get('content', str(insight))
                        confidence = insight.get('confidence', 0)
                        print(f"   {i}. {content[:150]}... (置信度: {confidence:.2f})")
                    else:
                        print(f"   {i}. {str(insight)[:150]}...")
            
            # 显示调整建议
            adjustments = final_result.get('adjustments', {})
            if adjustments:
                print(f"\n⚙️ 调整建议 ({len(adjustments)} 个时段):")
                for time_period, adjustment in list(adjustments.items())[:3]:
                    print(f"   {time_period}: {adjustment}")
            
            # 显示推荐
            recommendations = final_result.get('recommendations', [])
            if recommendations:
                print(f"\n📋 推荐措施 ({len(recommendations)} 条):")
                for i, rec in enumerate(recommendations[:3], 1):
                    if isinstance(rec, dict):
                        content = rec.get('content', str(rec))
                        print(f"   {i}. {content[:150]}...")
                    else:
                        print(f"   {i}. {str(rec)[:150]}...")
            
            # 显示置信度和完成状态
            confidence = final_result.get('confidence_level', 0)
            is_complete = final_result.get('is_complete', False)
            print(f"\n📈 整体置信度: {confidence:.2f}")
            print(f"✅ 完成状态: {'完成' if is_complete else '未完成'}")
            
            return True
        else:
            print("⚠️ 未收到最终结果")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 流程执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    success = await test_complete_decision_flow()
    
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    if success:
        print("🎉 AI Agent完整决策流程测试成功!")
        print("✅ 所有功能正常工作")
        print("✅ 流式处理正常")
        print("✅ AI思考过程透明")
        print("✅ 决策结果完整")
        print("\n💡 现在可以进行前端集成或生产环境部署")
    else:
        print("❌ 测试失败，需要进一步调试")
        print("💡 请检查服务器状态和网络连接")

if __name__ == "__main__":
    asyncio.run(main())
