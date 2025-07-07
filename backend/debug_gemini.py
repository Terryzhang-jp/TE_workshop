#!/usr/bin/env python3
"""
调试Gemini API连接问题
"""

import asyncio
import sys
import os
import time
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
                    print(f"✅ 设置环境变量: {key}")

async def test_gemini_step_by_step():
    """逐步测试Gemini连接"""
    print("🔍 逐步调试Gemini API连接")
    print("="*50)
    
    # 1. 加载环境变量
    print("1️⃣ 加载环境变量...")
    load_env_file()
    
    api_key = os.getenv('AI_AGENT_GEMINI_API_KEY')
    if not api_key:
        print("❌ AI_AGENT_GEMINI_API_KEY 未设置")
        return False
    
    print(f"✅ API Key: {api_key[:10]}...")
    
    # 2. 测试基础导入
    print("\n2️⃣ 测试基础导入...")
    try:
        import google.generativeai as genai
        print("✅ google.generativeai 导入成功")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    
    # 3. 配置API
    print("\n3️⃣ 配置Gemini API...")
    try:
        genai.configure(api_key=api_key)
        print("✅ API配置成功")
    except Exception as e:
        print(f"❌ API配置失败: {e}")
        return False
    
    # 4. 创建模型
    print("\n4️⃣ 创建Gemini模型...")
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        print("✅ 模型创建成功")
    except Exception as e:
        print(f"❌ 模型创建失败: {e}")
        return False
    
    # 5. 测试简单生成
    print("\n5️⃣ 测试简单生成...")
    try:
        print("🔄 发送简单请求...")
        start_time = time.time()
        
        response = model.generate_content("Hello, please respond with 'Test successful'")
        
        elapsed = time.time() - start_time
        print(f"✅ 简单生成成功 (耗时: {elapsed:.2f}秒)")
        print(f"   响应: {response.text}")
        
    except Exception as e:
        print(f"❌ 简单生成失败: {e}")
        return False
    
    # 6. 测试复杂提示
    print("\n6️⃣ 测试复杂提示...")
    try:
        complex_prompt = """
        你是一个AI决策助手，专门协助电力消费预测调整。
        
        请按照以下格式回应：
        ## 当前思考
        [简单的思考内容]
        
        ## 新洞察
        INSIGHT: 这是一个测试洞察 | 0.9 | 测试问题
        
        ## 新问题
        QUESTION: 这是一个测试问题 | 测试来源 | 0.8
        
        ## 下一步行动
        ACTION: 访问上下文信息
        """
        
        print("🔄 发送复杂请求...")
        start_time = time.time()
        
        response = model.generate_content(complex_prompt)
        
        elapsed = time.time() - start_time
        print(f"✅ 复杂生成成功 (耗时: {elapsed:.2f}秒)")
        print(f"   响应长度: {len(response.text)} 字符")
        print(f"   响应预览: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ 复杂生成失败: {e}")
        return False
    
    # 7. 测试异步调用
    print("\n7️⃣ 测试异步调用...")
    try:
        from ai_agent.utils.gemini_client import GeminiClient
        
        client = GeminiClient()
        print("✅ GeminiClient 创建成功")
        
        print("🔄 测试异步生成...")
        start_time = time.time()
        
        response = await client._generate_with_retry("简单测试：请回复'异步测试成功'")
        
        elapsed = time.time() - start_time
        print(f"✅ 异步生成成功 (耗时: {elapsed:.2f}秒)")
        print(f"   响应: {response}")
        
    except Exception as e:
        print(f"❌ 异步生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 8. 测试超时设置
    print("\n8️⃣ 测试超时设置...")
    try:
        from ai_agent.config.settings import get_settings
        
        settings = get_settings()
        print(f"✅ API超时: {settings.api_timeout}秒")
        print(f"✅ 思考超时: {settings.thinking_timeout}秒")
        print(f"✅ 重试次数: {settings.api_retry_attempts}")
        print(f"✅ 重试延迟: {settings.api_retry_delay}秒")
        
    except Exception as e:
        print(f"❌ 设置检查失败: {e}")
        return False
    
    print("\n🎉 所有测试通过！Gemini API工作正常")
    return True

async def test_thinking_node_directly():
    """直接测试thinking节点"""
    print("\n" + "="*50)
    print("🧠 直接测试thinking节点")
    print("="*50)
    
    try:
        from ai_agent.core.state import create_initial_state
        from ai_agent.nodes.thinking import thinking_node
        
        # 创建简单的初始状态
        initial_state = create_initial_state(
            human_decision_intent="测试thinking节点",
            human_reasoning="验证thinking节点是否能正常工作",
            session_id="debug-test-001",
            max_loops=3
        )
        
        print("✅ 初始状态创建成功")
        print(f"   状态键: {list(initial_state.keys())}")
        
        print("🔄 调用thinking节点...")
        start_time = time.time()
        
        result = await thinking_node(initial_state)
        
        elapsed = time.time() - start_time
        print(f"✅ thinking节点执行成功 (耗时: {elapsed:.2f}秒)")
        print(f"   返回键: {list(result.keys())}")
        print(f"   下一步行动: {result.get('next_action', '未知')}")
        
        return True
        
    except Exception as e:
        print(f"❌ thinking节点测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_langgraph_flow():
    """测试LangGraph流程控制"""
    print("\n" + "="*50)
    print("🔄 测试LangGraph流程控制")
    print("="*50)

    try:
        from ai_agent.core.agent import DecisionCoPilot
        from ai_agent.core.state import create_initial_state

        # 创建AI Agent
        agent = DecisionCoPilot()
        print("✅ DecisionCoPilot 创建成功")

        # 创建初始状态
        initial_state = create_initial_state(
            human_decision_intent="简单测试",
            human_reasoning="测试LangGraph流程是否正常",
            session_id="debug-flow-001",
            max_loops=2  # 限制循环次数
        )

        print("✅ 初始状态创建成功")

        # 创建线程配置
        thread_config = {"configurable": {"thread_id": "debug-flow-001"}}

        print("🔄 开始流式处理...")
        start_time = time.time()

        step_count = 0
        final_state = None

        # 设置超时保护
        timeout_seconds = 60  # 1分钟超时

        async def process_with_timeout():
            nonlocal step_count, final_state

            async for state in agent.compiled_graph.astream(
                initial_state,
                config=thread_config
            ):
                step_count += 1
                final_state = state

                elapsed = time.time() - start_time
                print(f"   步骤 {step_count}: {elapsed:.1f}s - 状态键: {list(state.keys())}")

                # 检查关键状态
                if isinstance(state, dict):
                    current_action = state.get('next_action', '未知')
                    thinking_step = state.get('thinking_step', 0)
                    loop_count = state.get('loop_count', 0)
                    is_complete = state.get('is_complete', False)

                    print(f"      当前行动: {current_action}")
                    print(f"      思考步骤: {thinking_step}")
                    print(f"      循环次数: {loop_count}")
                    print(f"      是否完成: {is_complete}")

                # 防止无限循环
                if step_count > 10:
                    print("⚠️ 步骤数超过10，强制停止")
                    break

                if elapsed > timeout_seconds:
                    print(f"⚠️ 超时 ({timeout_seconds}秒)，强制停止")
                    break

        # 执行带超时的处理
        try:
            await asyncio.wait_for(process_with_timeout(), timeout=timeout_seconds + 10)
        except asyncio.TimeoutError:
            print("❌ 流程处理超时")
            return False

        elapsed = time.time() - start_time
        print(f"✅ 流程处理完成 (耗时: {elapsed:.2f}秒, 步骤数: {step_count})")

        if final_state:
            print(f"   最终状态键: {list(final_state.keys())}")
            print(f"   最终行动: {final_state.get('next_action', '未知')}")
            print(f"   是否完成: {final_state.get('is_complete', False)}")

        return True

    except Exception as e:
        print(f"❌ LangGraph流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("🚀 Gemini API 调试工具")
    print("="*60)

    # 执行逐步测试
    basic_success = await test_gemini_step_by_step()

    if basic_success:
        thinking_success = await test_thinking_node_directly()

        if thinking_success:
            flow_success = await test_langgraph_flow()
        else:
            flow_success = False
    else:
        thinking_success = False
        flow_success = False

    print("\n" + "="*60)
    print("📊 调试报告")
    print("="*60)

    print(f"🔧 基础Gemini API: {'✅ 正常' if basic_success else '❌ 异常'}")
    print(f"🧠 Thinking节点: {'✅ 正常' if thinking_success else '❌ 异常'}")
    print(f"🔄 LangGraph流程: {'✅ 正常' if flow_success else '❌ 异常'}")

    if basic_success and thinking_success and flow_success:
        print("\n🎉 所有组件正常！")
        print("💡 原始问题可能是超时或网络问题")
    elif basic_success and thinking_success:
        print("\n⚠️ 组件正常，但LangGraph流程有问题")
        print("💡 建议：检查状态流转逻辑和循环控制")
    elif basic_success:
        print("\n⚠️ Gemini API正常，但thinking节点有问题")
        print("💡 建议：检查thinking节点的实现和状态管理")
    else:
        print("\n❌ Gemini API连接有问题")
        print("💡 建议：检查网络连接、API密钥和配置")

if __name__ == "__main__":
    asyncio.run(main())
