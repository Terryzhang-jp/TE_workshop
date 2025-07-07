#!/usr/bin/env python3
"""
自动转换监听脚本
Auto Convert Monitor Script

监听实验结果目录，当有新的JSON文件保存时自动转换为CSV
"""

import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from json_to_csv_converter import ExperimentDataConverter

class ExperimentFileHandler(FileSystemEventHandler):
    def __init__(self, converter: ExperimentDataConverter):
        self.converter = converter
        self.last_conversion = 0
        self.conversion_delay = 2  # 延迟2秒后转换，避免频繁转换
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        if event.src_path.endswith('.json'):
            print(f"📁 检测到新文件: {event.src_path}")
            self.schedule_conversion()
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        if event.src_path.endswith('.json'):
            print(f"📝 检测到文件修改: {event.src_path}")
            self.schedule_conversion()
    
    def schedule_conversion(self):
        """延迟执行转换，避免频繁转换"""
        current_time = time.time()
        self.last_conversion = current_time
        
        def delayed_convert():
            time.sleep(self.conversion_delay)
            # 检查是否有更新的转换请求
            if time.time() - self.last_conversion >= self.conversion_delay - 0.1:
                print("🔄 开始自动转换...")
                try:
                    self.converter.convert_to_csv()
                    print("✅ 自动转换完成")
                except Exception as e:
                    print(f"❌ 自动转换失败: {e}")
        
        # 在新线程中执行延迟转换
        threading.Thread(target=delayed_convert, daemon=True).start()

def main():
    """主函数"""
    print("🔍 实验结果自动转换监听器")
    print("=" * 50)
    
    # 创建转换器
    converter = ExperimentDataConverter()
    
    # 确保监听目录存在
    watch_dir = converter.input_dir
    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)
        print(f"📁 创建监听目录: {watch_dir}")
    
    # 初始转换现有文件
    print("🔄 初始转换现有文件...")
    try:
        converter.convert_to_csv()
    except Exception as e:
        print(f"⚠️ 初始转换失败: {e}")
    
    # 设置文件监听
    event_handler = ExperimentFileHandler(converter)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    
    # 开始监听
    observer.start()
    print(f"👀 开始监听目录: {watch_dir}")
    print("💡 当有新的实验结果JSON文件保存时，将自动转换为CSV")
    print("🛑 按 Ctrl+C 停止监听")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 停止监听...")
        observer.stop()
    
    observer.join()
    print("✅ 监听器已停止")

if __name__ == "__main__":
    main()
