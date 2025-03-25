import sys
from pathlib import Path
import os
import http.server
import socketserver
import webbrowser

# 获取当前文件路径
FILE = Path(__file__).resolve()
# 获取前端目录路径
FRONTEND_DIR = FILE.parent
# 项目根目录
ROOT = FILE.parents[3]

# 添加项目根目录到sys.path
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# 服务器配置
PORT = 8080
DIRECTORY = str(FRONTEND_DIR)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # 自定义日志格式
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))


def run_server():
    # 打印启动信息
    print(f"启动前端服务器在 http://localhost:{PORT}")
    print(f"前端目录: {DIRECTORY}")

    # 尝试自动打开浏览器
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except:
        print("无法自动打开浏览器，请手动访问 http://localhost:8080")

    # 启动HTTP服务器
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("按 Ctrl+C 停止服务器...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")


if __name__ == "__main__":
    # 确保工作目录正确
    os.chdir(DIRECTORY)
    run_server()
