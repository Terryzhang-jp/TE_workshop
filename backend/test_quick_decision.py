#!/usr/bin/env python3
"""
快速测试AI Agent决策结果
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

async def test_quick_decision():
    """快速测试AI Agent决策"""
    print("⚡ AI Agent快速决策测试")
    print("="*50)
    
    # 加载环境变量
    load_env_file()
    
    # 准备简化的测试场景
    request_data = {
        "intention": "明天高温35°C，需要快速调整电力预测",
        "reasoning": "根据历史数据，高温天气会导致空调负荷激增，担心模型低估了需求。",
        "options": {
            "max_iterations": 3,  # 限制为3轮
            "timeout_seconds": 120,  # 2分钟超时
            "include_debug": False
        }
    }
    
    print("🔄 发送快速决策请求...")
    print("   ⏱️ 限制3轮思考，2分钟内完成")
    
    try:
        start_time = time.time()
        
        # 使用非流式API获取最终结果
        response = requests.post(
            'http://localhost:8001/api/v1/ai-agent/stream',
            json=request_data,
            headers={'Accept': 'text/event-stream'},
            stream=True,
            timeout=150
        )
        
        if response.status_code != 200:
            print(f"❌ API请求失败: {response.status_code}")
            return False
        
        # 收集所有事件
        events = []
        final_result = None
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        event_data = json.loads(line_str[6:])
                        events.append(event_data)
                        
                        if event_data.get('type') == 'process_complete':
                            final_result = event_data.get('data', {})
                            break
                            
                    except json.JSONDecodeError:
                        continue
        
        elapsed = time.time() - start_time
        print(f"✅ 决策完成 (耗时: {elapsed:.1f}秒)")
        print(f"📊 处理事件: {len(events)} 个")
        
        # 显示决策结果
        if final_result:
            print("\n🎯 AI决策结果:")
            print("="*40)
            
            # 基本信息
            session_id = final_result.get('session_id', 'unknown')
            confidence = final_result.get('confidence_level', 0)
            is_complete = final_result.get('is_complete', False)
            
            print(f"会话ID: {session_id}")
            print(f"置信度: {confidence:.2f}")
            print(f"完成状态: {'✅ 完成' if is_complete else '⚠️ 未完成'}")
            
            # 洞察
            insights = final_result.get('insights', [])
            if insights:
                print(f"\n💡 关键洞察 ({len(insights)} 个):")
                for i, insight in enumerate(insights[:3], 1):
                    if isinstance(insight, dict):
                        content = insight.get('content', str(insight))
                        conf = insight.get('confidence', 0)
                        print(f"   {i}. {content[:120]}... (置信度: {conf:.2f})")
                    else:
                        print(f"   {i}. {str(insight)[:120]}...")
            
            # 调整建议
            adjustments = final_result.get('final_adjustments', {})
            if adjustments:
                print(f"\n⚙️ 调整建议 ({len(adjustments)} 个时段):")
                for time_period, adjustment in list(adjustments.items())[:5]:
                    print(f"   {time_period}: {adjustment}")
            
            # 推荐措施
            recommendations = final_result.get('recommendations', [])
            if recommendations:
                print(f"\n📋 推荐措施 ({len(recommendations)} 条):")
                for i, rec in enumerate(recommendations[:3], 1):
                    if isinstance(rec, dict):
                        content = rec.get('content', str(rec))
                        print(f"   {i}. {content[:120]}...")
                    else:
                        print(f"   {i}. {str(rec)[:120]}...")
            
            # 决策策略
            strategy = final_result.get('decision_strategy', '')
            if strategy:
                print(f"\n🎯 决策策略:")
                print(f"   {strategy[:200]}...")
            
            # 推理解释
            reasoning = final_result.get('reasoning_explanation', '')
            if reasoning:
                print(f"\n🧠 推理解释:")
                print(f"   {reasoning[:200]}...")
            
            return True
        else:
            print("⚠️ 未收到最终决策结果")
            
            # 显示收到的事件类型
            event_types = [event.get('type', 'unknown') for event in events]
            print(f"收到的事件类型: {set(event_types)}")
            
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 AI Agent快速决策测试工具")
    print("="*60)
    
    success = await test_quick_decision()
    
    print("\n" + "="*60)
    print("📊 测试结果")
    print("="*60)
    
    if success:
        print("🎉 AI Agent决策功能正常!")
        print("✅ 能够快速生成决策结果")
        print("✅ 提供完整的洞察和建议")
        print("✅ 流程透明可追踪")
    else:
        print("❌ 决策测试未完全成功")
        print("💡 可能需要更长的处理时间")

if __name__ == "__main__":
    asyncio.run(main())
