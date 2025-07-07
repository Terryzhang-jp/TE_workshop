#!/usr/bin/env python3
"""
简化的结构化输出测试
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

async def test_simple_structured():
    """简化的结构化测试"""
    print("🧪 简化结构化输出测试")
    print("="*50)
    
    # 加载环境变量
    load_env_file()
    
    # 简化的测试数据
    test_request = {
        "intention": "快速测试AI Agent结构化输出",
        "reasoning": "验证结构化思考步骤是否能正确传递到前端",
        "options": {
            "max_iterations": 3,  # 只做3轮
            "timeout_seconds": 120,  # 2分钟超时
            "include_debug": True,
            "structured_output": True
        }
    }
    
    print(f"📝 测试场景: {test_request['intention']}")
    print(f"🎯 迭代限制: {test_request['options']['max_iterations']} 轮")
    print(f"⏱️ 超时设置: {test_request['options']['timeout_seconds']} 秒")
    
    try:
        start_time = time.time()
        event_count = 0
        structured_events = 0
        
        print("\n🔄 开始测试...")
        print("-" * 50)
        
        response = requests.post(
            'http://localhost:8001/api/v1/ai-agent/stream-structured',
            json=test_request,
            headers={'Accept': 'text/event-stream'},
            stream=True,
            timeout=150
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
                        data = event_data.get('data', {})
                        
                        print(f"[{event_count:2d}] {elapsed:6.1f}s | {event_type}")
                        print(f"    步骤: {step_number}, 迭代: {iteration}")
                        
                        # 检查数据内容
                        if 'state_keys' in data:
                            print(f"    状态键: {data['state_keys']}")
                        if 'has_structured_step' in data:
                            print(f"    结构化步骤: {data['has_structured_step']}")
                        if 'has_processing_metrics' in data:
                            print(f"    处理指标: {data['has_processing_metrics']}")
                        
                        if event_type == 'thinking_step_complete':
                            structured_events += 1
                            structured_step = data.get('structured_step', {})
                            processing_metrics = data.get('processing_metrics', {})
                            
                            print(f"    ✅ 结构化思考事件!")
                            print(f"       阶段: {structured_step.get('phase', 'unknown')}")
                            print(f"       置信度: {processing_metrics.get('confidence_level', 0):.2f}")
                            print(f"       洞察数: {processing_metrics.get('insights_count', 0)}")
                            print(f"       问题数: {processing_metrics.get('questions_count', 0)}")
                            
                        elif event_type == 'step_progress':
                            action = data.get('action', 'unknown')
                            print(f"    行动: {action}")
                            
                        elif event_type == 'process_complete':
                            print(f"    🎉 流程完成!")
                            break
                            
                        elif event_type == 'error':
                            error_msg = data.get('message', 'Unknown error')
                            print(f"    ❌ 错误: {error_msg}")
                            break
                            
                        # 限制测试时间
                        if elapsed > 120:  # 2分钟超时
                            print(f"    ⏰ 测试超时，停止")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"    ⚠️ JSON解析错误: {e}")
                        continue
        
        total_time = time.time() - start_time
        print("-" * 50)
        print(f"⏱️ 总测试时间: {total_time:.1f}秒")
        print(f"📊 总事件数: {event_count} 个")
        print(f"🧠 结构化事件: {structured_events} 个")
        
        # 分析结果
        if structured_events > 0:
            print("✅ 结构化输出正常工作!")
            return True
        else:
            print("❌ 未收到结构化事件，需要调试")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    success = await test_simple_structured()
    
    print("\n" + "="*50)
    print("📊 测试结果")
    print("="*50)
    
    if success:
        print("🎉 结构化输出功能正常!")
        print("💡 可以进行完整测试和前端集成")
    else:
        print("❌ 结构化输出有问题")
        print("💡 需要检查thinking节点和状态传递")

if __name__ == "__main__":
    asyncio.run(main())
