#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拼豆识别系统 - 启动器
打包后的 Windows 可执行文件入口
自动启动服务并打开浏览器
"""
import os
import sys
import time
import threading
import webbrowser
import socket
from app import app, init_ocr, load_color_mapping

# 配置
HOST = '127.0.0.1'
PORT = 8080
URL = f'http://{HOST}:{PORT}'


def is_port_available(port):
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((HOST, port))
        sock.close()
        return result != 0
    except:
        return False


def find_available_port(start_port=8080, max_attempts=10):
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    return start_port


def open_browser(delay=2):
    """延迟后打开浏览器"""
    def _open():
        time.sleep(delay)
        # 尝试多种浏览器打开方式
        try:
            webbrowser.open(URL, new=2)  # new=2 表示在新标签页打开
            print(f"✓ 已自动打开浏览器: {URL}")
        except Exception as e:
            print(f"⚠ 自动打开浏览器失败，请手动访问: {URL}")
            print(f"  错误信息: {e}")
    
    thread = threading.Thread(target=_open)
    thread.daemon = True
    thread.start()


def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              🎨 拼豆识别系统 v1.0                        ║
║                                                          ║
║     基于 PaddleOCR 的智能颜色识别与统计工具              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """主函数"""
    global PORT, URL
    
    # 设置工作目录为程序所在目录（解决资源路径问题）
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        application_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(application_path)
    
    # 打印启动信息
    print_banner()
    
    # 查找可用端口
    PORT = find_available_port(PORT)
    URL = f'http://{HOST}:{PORT}'
    
    print(f"📂 工作目录: {application_path}")
    print(f"🌐 服务地址: {URL}")
    print(f"🚀 正在启动服务，请稍候...\n")
    
    # 初始化 OCR（加载模型）
    print("⏳ 正在初始化 OCR 引擎，首次启动可能需要几分钟...")
    try:
        init_ocr()
    except Exception as e:
        print(f"❌ OCR 引擎初始化失败: {e}")
        print("请确保系统已正确安装 PaddleOCR 依赖")
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 加载颜色映射
    print("⏳ 正在加载颜色映射表...")
    try:
        load_color_mapping()
    except Exception as e:
        print(f"⚠ 颜色映射表加载失败: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ 服务已启动！")
    print(f"🌐 请访问: {URL}")
    print("=" * 60 + "\n")
    
    # 自动打开浏览器
    open_browser(delay=1.5)
    
    # 启动 Flask 服务
    try:
        app.run(
            host=HOST,
            port=PORT,
            debug=False,  # 生产环境关闭调试模式
            threaded=True,
            use_reloader=False  # 打包后禁用重载器
        )
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止，感谢使用！")
    except Exception as e:
        print(f"\n❌ 服务运行出错: {e}")
        input("\n按回车键退出...")


if __name__ == '__main__':
    main()
