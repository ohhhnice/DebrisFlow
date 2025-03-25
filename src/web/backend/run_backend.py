import sys
from pathlib import Path
import uvicorn

FILE = Path(__file__).resolve()
ROOT = FILE.parents[3]  # 项目根目录
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

if __name__ == "__main__":
    # 设置工作目录为后端目录
    backend_dir = FILE.parent
    
    # 运行FastAPI应用
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        reload_dirs=[str(backend_dir)]
    ) 