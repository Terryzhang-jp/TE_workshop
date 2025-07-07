#!/usr/bin/env python3
"""
知识禁用测试 - 确保AI Agent不使用任何预训练知识或常识
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

async def test_knowledge_prohibition():
    """知识禁用测试"""
    print("🧠 知识禁用测试")
    print("="*60)
    
    # 加载环境变量
    load_env_file()
    
    # 故意错误的用户输入
    test_request = {
        "intention": "分析明天35°C高温天气对电力需求的影响",
        "reasoning": "根据气象预报，明天将是炎热的夏日，空调负荷会激增",
        "options": {
            "max_iterations": 3,
            "timeout_seconds": 90,
            "include_debug": True,
            "structured_output": True
        }
    }
    
    print("🎯 测试目标: 验证AI Agent是否完全禁用了预训练知识")
    print("📝 故意错误输入: 35°C高温天气")
    print("✅ 期望: AI Agent不使用任何常识，只基于数据")
    
    # 定义禁用的常识性表述
    forbidden_knowledge = {
        "天气常识": [
            "高温", "炎热", "夏季", "夏天", "空调", "制冷", "降温",
            "通常", "一般", "常见", "经验", "历史上", "往往"
        ],
        "电力常识": [
            "用电量增加", "负荷上升", "需求激增", "峰值", "用电高峰",
            "供电压力", "电网负荷", "用电需求"
        ],
        "推理词汇": [
            "因此", "所以", "由于", "导致", "影响", "造成", "引起",
            "可能", "应该", "会", "将会", "预计", "估计"
        ],
        "假设表述": [
            "假设", "如果", "可能", "大概", "也许", "或许", "似乎"
        ]
    }
    
    try:
        start_time = time.time()
        all_thinking_content = []
        knowledge_violations = []
        
        print("\n🔄 开始知识禁用测试...")
        print("-" * 60)
        
        response = requests.post(
            'http://localhost:8001/api/v1/ai-agent/stream-structured',
            json=test_request,
            headers={'Accept': 'text/event-stream'},
            stream=True,
            timeout=100
        )
        
        if response.status_code != 200:
            print(f"❌ API请求失败: {response.status_code}")
            return False
        
        # 处理流式响应
        event_count = 0
        max_events = 8  # 处理更多事件以获得完整分析
        
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
                            
                            if thinking_content:
                                all_thinking_content.append(thinking_content)
                                print(f"   💭 思考内容: {thinking_content[:150]}...")
                                
                                # 检查是否使用了禁用的知识
                                content_lower = thinking_content.lower()
                                
                                for category, keywords in forbidden_knowledge.items():
                                    for keyword in keywords:
                                        if keyword in content_lower:
                                            violation = {
                                                "category": category,
                                                "keyword": keyword,
                                                "step": event_count,
                                                "context": thinking_content[:200]
                                            }
                                            knowledge_violations.append(violation)
                                            print(f"   ⚠️ 发现禁用知识: {category} - '{keyword}'")
                        
                        elif event_type == 'process_complete':
                            print(f"   🎉 流程完成!")
                            break
                            
                        elif event_type == 'error':
                            error_msg = data.get('message', 'Unknown error')
                            print(f"   ❌ 错误: {error_msg}")
                            break
                        
                        # 超时检查
                        if elapsed > 90:
                            print(f"   ⏰ 超时停止")
                            break
                            
                    except json.JSONDecodeError:
                        continue
            elif event_count >= max_events:
                break
        
        # 分析结果
        total_time = time.time() - start_time
        print("\n" + "="*60)
        print("📊 知识禁用检查结果")
        print("="*60)
        
        print(f"⏱️ 测试时间: {total_time:.1f}秒")
        print(f"📝 思考步骤数: {len(all_thinking_content)}")
        print(f"⚠️ 知识违规数: {len(knowledge_violations)}")
        
        if not knowledge_violations:
            print("\n✅ 测试通过: AI Agent完全禁用了预训练知识")
            print("💡 AI Agent只基于提供的数据进行分析")
            
            # 检查是否正确使用了实际数据
            combined_content = " ".join(all_thinking_content).lower()
            data_usage_score = 0
            
            if '2022' in combined_content:
                data_usage_score += 1
                print("✅ 正确使用了2022年数据")
            
            if '1月7日' in combined_content or 'january 7' in combined_content:
                data_usage_score += 1
                print("✅ 正确使用了1月7日数据")
            
            if '数据' in combined_content or '访问' in combined_content:
                data_usage_score += 1
                print("✅ 显示了数据访问意识")
            
            if data_usage_score >= 2:
                print("🎉 AI Agent正确使用了实际数据而非预训练知识")
                return True
            else:
                print("⚠️ AI Agent虽然没有使用禁用知识，但数据使用不够明确")
                return True
        else:
            print("\n❌ 测试失败: AI Agent使用了禁用的预训练知识")
            print("\n🔍 违规详情:")
            
            # 按类别统计违规
            violation_by_category = {}
            for violation in knowledge_violations:
                category = violation["category"]
                if category not in violation_by_category:
                    violation_by_category[category] = []
                violation_by_category[category].append(violation)
            
            for category, violations in violation_by_category.items():
                print(f"\n📂 {category} ({len(violations)}个违规):")
                for violation in violations[:3]:  # 只显示前3个
                    print(f"   • 关键词: '{violation['keyword']}'")
                    print(f"     步骤: {violation['step']}")
                    print(f"     上下文: {violation['context'][:100]}...")
            
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def main():
    """主函数"""
    success = await test_knowledge_prohibition()
    
    print("\n" + "="*60)
    print("🎯 知识禁用测试结果")
    print("="*60)
    
    if success:
        print("🎉 AI Agent成功禁用了预训练知识!")
        print("💡 AI Agent只基于提供的数据进行分析")
        print("🚀 可以进行完整功能测试")
    else:
        print("❌ AI Agent仍在使用预训练知识")
        print("💡 需要进一步强化提示词约束")

if __name__ == "__main__":
    asyncio.run(main())
