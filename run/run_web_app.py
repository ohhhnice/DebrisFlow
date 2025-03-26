import sys
from pathlib import Path
import subprocess
import threading
import time
import webbrowser

# 获取项目根目录
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]

# 添加项目根目录到sys.path
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# 后端和前端脚本的路径
BACKEND_SCRIPT = ROOT / "src" / "web" / "backend" / "run_backend.py"
FRONTEND_SCRIPT = ROOT / "src" / "web" / "frontend" / "run_frontend.py"


# 启动后端
def run_backend():
    print("\n" + "=" * 50)
    print("启动后端服务...")
    print("=" * 50)

    backend_process = subprocess.Popen(
        [sys.executable, str(BACKEND_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
    )

    for line in backend_process.stdout:
        print(f"[后端] {line.strip()}")

    backend_process.wait()


# 启动前端
def run_frontend():
    print("\n" + "=" * 50)
    print("启动前端服务...")
    print("=" * 50)

    # 延迟2秒启动前端，确保后端已启动
    time.sleep(2)

    frontend_process = subprocess.Popen(
        [sys.executable, str(FRONTEND_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
    )

    for line in frontend_process.stdout:
        print(f"[前端] {line.strip()}")

    frontend_process.wait()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("泥石流视频处理系统 - Web应用")
    print("=" * 50)
    print("正在启动服务，请稍候...")

    # 创建并启动线程
    backend_thread = threading.Thread(target=run_backend)
    frontend_thread = threading.Thread(target=run_frontend)

    # 将线程设为守护线程，这样当主程序退出时，线程也会退出
    backend_thread.daemon = True
    frontend_thread.daemon = True

    # 启动线程
    backend_thread.start()
    frontend_thread.start()

    # 等待用户按Ctrl+C退出
    try:
        print("\n" + "=" * 50)
        print("服务已启动！")
        print("后端API地址: http://localhost:8000")
        print("前端界面地址: http://localhost:8080")
        print("按 Ctrl+C 停止所有服务")
        print("=" * 50 + "\n")

        # 保持主线程运行，直到用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("正在停止服务...")
        print("=" * 50)
        print("已退出应用")
        sys.exit(0)
