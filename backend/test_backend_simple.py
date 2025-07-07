#!/usr/bin/env python3
"""
简化的后端测试，不依赖Google AI
"""

import asyncio
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

async def test_backend_without_ai():
    """测试后端基础功能，不使用AI Agent"""
    
    print("🧪 测试后端基础功能")
    print("="*40)
    
    try:
        # 测试基础API端点
        from app.api.v1.endpoints.ai_agent import get_ai_agent_status
        
        status = await get_ai_agent_status()
        print(f"✅ AI Agent状态API正常: {status['status']}")
        
        # 测试数据模型
        from app.api.v1.endpoints.ai_agent import AIAgentRequest
        
        test_request = AIAgentRequest(
            intention="测试请求",
            reasoning="验证数据模型是否正常"
        )
        print(f"✅ 数据模型正常: {test_request.intention}")
        
        # 测试SSE事件创建
        from app.api.v1.endpoints.ai_agent import create_sse_event
        
        test_event = create_sse_event(
            "test",
            {"message": "测试"},
            "test-session"
        )
        print(f"✅ SSE事件创建正常: {len(test_event)} 字符")
        
        print("\n🎉 后端基础功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 后端测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_backend_without_ai()
    if success:
        print("\n✅ 后端基础功能正常，可以启动服务")
    else:
        print("\n❌ 后端存在问题，需要修复")

if __name__ == "__main__":
    asyncio.run(main())
