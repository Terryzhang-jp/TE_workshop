#!/usr/bin/env python3
"""
调试迭代循环问题
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

async def debug_iteration_loop():
    """调试迭代循环"""
    print("🔧 调试迭代循环问题")
    print("="*50)
    
    # 加载环境变量
    load_env_file()
    
    # 简单的测试请求
    test_request = {
        "intention": "测试AI Agent迭代",
        "reasoning": "检查AI Agent是否能正确迭代",
        "options": {
            "max_iterations": 3,  # 只做3轮
            "timeout_seconds": 60,
            "include_debug": True,
            "structured_output": True
        }
    }
    
    try:
        start_time = time.time()
        
        print("🔄 开始调试...")
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
        
        # 跟踪状态变化
        previous_state = None
        step_count = 0
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        event_data = json.loads(line_str[6:])
                        elapsed = time.time() - start_time
                        
                        event_type = event_data.get('type', 'unknown')
                        data = event_data.get('data', {})
                        
                        if event_type == 'thinking_step_complete':
                            step_count += 1
                            print(f"\n📋 步骤 {step_count} ({elapsed:.1f}s)")
                            
                            # 检查状态变化
                            current_state = {
                                'accessed_info': data.get('accessed_info', {}),
                                'loop_count': data.get('loop_count', 0),
                                'next_action': data.get('next_action', ''),
                                'confidence_level': data.get('confidence_level', 0)
                            }
                            
                            print(f"   🔍 状态检查:")
                            print(f"      循环次数: {current_state['loop_count']}")
                            print(f"      下一步行动: {current_state['next_action']}")
                            print(f"      置信度: {current_state['confidence_level']}")
                            print(f"      已访问信息: {current_state['accessed_info']}")
                            
                            # 检查是否有状态变化
                            if previous_state:
                                if current_state == previous_state:
                                    print(f"   ⚠️ 警告: 状态没有变化!")
                                else:
                                    print(f"   ✅ 状态已更新")
                                    
                                    # 显示具体变化
                                    for key, value in current_state.items():
                                        if value != previous_state.get(key):
                                            print(f"      {key}: {previous_state.get(key)} → {value}")
                            
                            previous_state = current_state.copy()
                            
                            # 获取思考内容
                            structured_step = data.get('structured_step', {})
                            thinking_content = structured_step.get('thinking_content', '')
                            
                            if thinking_content:
                                # 只显示前100个字符
                                print(f"   💭 思考: {thinking_content[:100]}...")
                            
                            # 如果连续3步状态都没变化，停止
                            if step_count >= 3:
                                print(f"\n⏰ 已完成3步，停止调试")
                                break
                        
                        elif event_type == 'process_complete':
                            print(f"\n🎉 流程完成!")
                            break
                            
                        elif event_type == 'error':
                            error_msg = data.get('message', 'Unknown error')
                            print(f"\n❌ 错误: {error_msg}")
                            break
                        
                        # 超时检查
                        if elapsed > 60:
                            print(f"\n⏰ 超时停止")
                            break
                            
                    except json.JSONDecodeError:
                        continue
        
        total_time = time.time() - start_time
        print(f"\n📊 调试结果:")
        print(f"   总时间: {total_time:.1f}秒")
        print(f"   总步骤: {step_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        return False

async def main():
    """主函数"""
    await debug_iteration_loop()

if __name__ == "__main__":
    asyncio.run(main())
