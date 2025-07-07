#!/usr/bin/env python3
"""
快速数据使用检查 - 只测试第一步思考是否正确
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

async def test_quick_data_check():
    """快速数据检查测试"""
    print("⚡ 快速数据使用检查")
    print("="*50)
    
    # 加载环境变量
    load_env_file()
    
    # 故意错误的用户输入
    test_request = {
        "intention": "分析明天35°C高温天气对电力需求的影响",
        "reasoning": "根据气象预报，明天将是炎热的夏日，空调负荷会激增",
        "options": {
            "max_iterations": 2,  # 只做2轮
            "timeout_seconds": 60,  # 1分钟超时
            "include_debug": True,
            "structured_output": True
        }
    }
    
    print(f"📝 故意错误输入: {test_request['intention']}")
    print(f"✅ 期望: AI Agent应该基于实际数据（2022年1月7日大雪）分析")
    
    try:
        start_time = time.time()
        first_thinking_content = ""
        
        print("\n🔄 开始快速测试...")
        print("-" * 50)
        
        response = requests.post(
            'http://localhost:8001/api/v1/ai-agent/stream-structured',
            json=test_request,
            headers={'Accept': 'text/event-stream'},
            stream=True,
            timeout=70
        )
        
        if response.status_code != 200:
            print(f"❌ API请求失败: {response.status_code}")
            return False
        
        # 只处理前几个事件
        event_count = 0
        max_events = 5  # 只处理前5个事件
        
        for line in response.iter_lines():
            if line and event_count < max_events:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        event_data = json.loads(line_str[6:])
                        event_count += 1
                        elapsed = time.time() - start_time
                        
                        event_type = event_data.get('type', 'unknown')
                        data = event_data.get('data', {})
                        
                        print(f"[{event_count}] {elapsed:.1f}s | {event_type}")
                        
                        if event_type == 'thinking_step_complete':
                            structured_step = data.get('structured_step', {})
                            thinking_content = structured_step.get('thinking_content', '')
                            
                            if thinking_content and not first_thinking_content:
                                first_thinking_content = thinking_content
                                print(f"📋 第一次思考内容:")
                                print(f"   {thinking_content[:300]}...")
                                
                                # 立即分析第一次思考
                                break
                        
                        # 超时检查
                        if elapsed > 60:
                            print(f"⏰ 超时停止")
                            break
                            
                    except json.JSONDecodeError:
                        continue
            elif event_count >= max_events:
                break
        
        # 分析第一次思考内容
        print("\n" + "="*50)
        print("📊 第一次思考分析")
        print("="*50)
        
        if not first_thinking_content:
            print("❌ 没有获取到思考内容")
            return False
        
        content_lower = first_thinking_content.lower()
        
        # 检查错误内容
        has_errors = False
        if '35°c' in content_lower or '35度' in content_lower:
            print("❌ 提及了35°C（错误）")
            has_errors = True
        
        if '高温' in content_lower and '低温' not in content_lower:
            print("❌ 提及了高温但没有提及低温（错误）")
            has_errors = True
        
        if '夏' in content_lower and '冬' not in content_lower:
            print("❌ 提及了夏季但没有提及冬季（错误）")
            has_errors = True
        
        # 检查正确内容
        has_correct = False
        if '2022' in content_lower:
            print("✅ 正确提及2022年")
            has_correct = True
        
        if '1月7日' in content_lower or 'january 7' in content_lower:
            print("✅ 正确提及1月7日")
            has_correct = True
        
        if '大雪' in content_lower or '雪' in content_lower:
            print("✅ 正确提及大雪")
            has_correct = True
        
        if '低温' in content_lower or '-3.5' in content_lower:
            print("✅ 正确提及低温")
            has_correct = True
        
        if '东京' in content_lower or 'tokyo' in content_lower:
            print("✅ 正确提及东京")
            has_correct = True
        
        # 检查数据访问意识
        if '访问' in content_lower or '数据' in content_lower:
            print("✅ 显示了数据访问意识")
            has_correct = True
        
        # 总结
        total_time = time.time() - start_time
        print(f"\n⏱️ 测试时间: {total_time:.1f}秒")
        
        if has_errors:
            print("❌ 测试失败: AI Agent仍然被用户输入误导")
            print("💡 需要进一步优化提示词")
            return False
        elif has_correct:
            print("✅ 测试通过: AI Agent正确使用了实际数据")
            print("💡 AI Agent没有被用户输入误导")
            return True
        else:
            print("⚠️ 测试不确定: 需要更多信息判断")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def main():
    """主函数"""
    success = await test_quick_data_check()
    
    print("\n" + "="*50)
    print("🎯 快速测试结果")
    print("="*50)
    
    if success:
        print("🎉 AI Agent数据使用正确!")
        print("💡 可以进行完整功能测试")
    else:
        print("❌ AI Agent数据使用有问题")
        print("💡 需要继续优化")

if __name__ == "__main__":
    asyncio.run(main())
