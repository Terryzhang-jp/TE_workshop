#!/usr/bin/env python3
"""
AI Agent Dashboard 服务器

提供AI Agent决策流程实时监控页面
"""
import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def serve_dashboard(port=8080):
    """启动Dashboard服务器"""
    
    # 确保在正确的目录
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # 检查HTML文件是否存在
    html_file = current_dir / "ai_agent_dashboard.html"
    if not html_file.exists():
        print("❌ 错误: ai_agent_dashboard.html 文件不存在")
        return False
    
    try:
        # 创建HTTP服务器
        handler = http.server.SimpleHTTPRequestHandler
        
        # 自定义处理器，默认返回dashboard页面
        class DashboardHandler(handler):
            def do_GET(self):
                if self.path == '/' or self.path == '':
                    self.path = '/ai_agent_dashboard.html'
                return super().do_GET()
        
        with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
            print(f"🚀 AI Agent Dashboard 服务器启动成功!")
            print(f"📍 服务地址: http://localhost:{port}")
            print(f"📁 服务目录: {current_dir}")
            print(f"🌐 正在自动打开浏览器...")
            print(f"💡 按 Ctrl+C 停止服务器")
            
            # 自动打开浏览器
            try:
                webbrowser.open(f'http://localhost:{port}')
            except Exception as e:
                print(f"⚠️  无法自动打开浏览器: {e}")
                print(f"请手动访问: http://localhost:{port}")
            
            print(f"\n{'='*60}")
            print(f"🤖 AI Agent Dashboard 运行中...")
            print(f"{'='*60}")
            
            # 启动服务器
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n\n👋 服务器已停止")
        return True
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 端口 {port} 已被占用，请尝试其他端口")
            print(f"💡 使用方法: python serve_dashboard.py --port 8081")
        else:
            print(f"❌ 服务器启动失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Agent Dashboard 服务器')
    parser.add_argument('--port', type=int, default=8080, 
                       help='服务器端口 (默认: 8080)')
    
    args = parser.parse_args()
    
    print("🤖 AI Agent Dashboard 服务器")
    print("="*50)
    
    success = serve_dashboard(args.port)
    
    if success:
        print("✅ 服务器正常关闭")
    else:
        print("❌ 服务器启动失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
