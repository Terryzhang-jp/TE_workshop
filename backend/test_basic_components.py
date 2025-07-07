#!/usr/bin/env python3
"""
第一性原理测试：检查AI Agent的基础组件
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

async def test_gemini_connection():
    """测试Gemini API连接"""
    print("🔍 测试1: Gemini API连接")
    print("-" * 30)
    
    try:
        from ai_agent.utils.gemini_client import GeminiClient
        
        # 检查API密钥
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('AI_AGENT_GEMINI_API_KEY')
        if not api_key:
            print("❌ 没有找到Gemini API密钥")
            return False
        
        print(f"✅ API密钥存在: {api_key[:10]}...")
        
        # 创建客户端
        client = GeminiClient()
        print("✅ Gemini客户端创建成功")
        
        # 测试简单请求
        print("🔄 测试简单API调用...")
        response = await client.generate_response("Hello, this is a test.")
        
        if response:
            print(f"✅ API调用成功，响应长度: {len(response)} 字符")
            print(f"   响应预览: {response[:100]}...")
            return True
        else:
            print("❌ API调用失败，返回空响应")
            return False
            
    except Exception as e:
        print(f"❌ Gemini连接测试失败: {e}")
        return False

async def test_data_access():
    """测试数据访问"""
    print("\n🔍 测试2: 数据访问")
    print("-" * 30)
    
    try:
        from ai_agent.data_access.experiment_data import ExperimentDataAccess
        
        # 创建数据访问实例
        data_access = ExperimentDataAccess()
        print("✅ 数据访问实例创建成功")
        
        # 测试上下文信息加载
        context_info = data_access.get_contextual_information()
        if context_info:
            print(f"✅ 上下文信息加载成功，包含 {len(context_info)} 个字段")
            print(f"   字段: {list(context_info.keys())}")
            return True
        else:
            print("❌ 上下文信息加载失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据访问测试失败: {e}")
        return False

async def test_thinking_node():
    """测试思考节点"""
    print("\n🔍 测试3: 思考节点")
    print("-" * 30)
    
    try:
        from ai_agent.nodes.thinking import thinking_node
        from ai_agent.core.state import create_initial_state
        
        # 创建初始状态
        state = create_initial_state(
            human_decision_intent="简单测试",
            human_reasoning="测试思考节点是否正常工作",
            session_id="basic-test"
        )
        print("✅ 初始状态创建成功")
        
        # 执行思考节点
        print("🔄 执行思考节点...")
        result = await thinking_node(state)
        
        if result:
            print("✅ 思考节点执行成功")
            print(f"   返回字段: {list(result.keys())}")
            
            # 检查关键字段
            if 'insights' in result:
                insights = result['insights']
                print(f"   Insights: {len(insights)} 个")
            
            if 'questions' in result:
                questions = result['questions']
                print(f"   Questions: {len(questions)} 个")
                
            if 'next_action' in result:
                print(f"   下一步行动: {result['next_action']}")
            
            return True
        else:
            print("❌ 思考节点返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ 思考节点测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_agent_flow():
    """测试简化的Agent流程"""
    print("\n🔍 测试4: 简化Agent流程")
    print("-" * 30)
    
    try:
        from ai_agent.core.state import create_initial_state
        from ai_agent.nodes.thinking import thinking_node
        
        # 创建状态
        state = create_initial_state(
            human_decision_intent="测试简化流程",
            human_reasoning="验证Agent的基本执行流程",
            session_id="simple-flow-test"
        )
        
        print("🔄 执行单步思考...")
        
        # 只执行一步思考
        result = await thinking_node(state)
        
        if result:
            print("✅ 单步执行成功")
            
            # 更新状态
            for key, value in result.items():
                if key in state:
                    if isinstance(state[key], list) and isinstance(value, list):
                        state[key].extend(value)
                    else:
                        state[key] = value
            
            print(f"   状态更新完成，当前循环: {state.get('loop_count', 0)}")
            print(f"   下一步行动: {state.get('next_action', 'unknown')}")
            
            return True
        else:
            print("❌ 单步执行失败")
            return False
            
    except Exception as e:
        print(f"❌ 简化流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 第一性原理：AI Agent基础组件测试")
    print("=" * 60)
    
    tests = [
        ("Gemini API连接", test_gemini_connection),
        ("数据访问", test_data_access),
        ("思考节点", test_thinking_node),
        ("简化Agent流程", test_simple_agent_flow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 基础组件测试报告")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{len(tests)} 测试通过")
    
    if passed == len(tests):
        print("🎉 所有基础组件正常！问题可能在复杂的流程逻辑中")
    elif passed >= len(tests) * 0.5:
        print("⚠️ 部分组件有问题，需要修复")
    else:
        print("❌ 多个基础组件失败，需要从根本解决")
    
    # 给出具体建议
    print("\n🔧 问题定位建议:")
    if not results[0][1]:  # Gemini API
        print("- 检查Gemini API密钥配置")
        print("- 检查网络连接")
    if not results[1][1]:  # 数据访问
        print("- 检查experiment_data目录和文件")
    if not results[2][1]:  # 思考节点
        print("- 检查thinking节点的逻辑")
        print("- 检查Gemini响应解析")
    if not results[3][1]:  # 简化流程
        print("- 检查状态管理逻辑")

if __name__ == "__main__":
    asyncio.run(main())
