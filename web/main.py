from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import Optional
import shutil
from pathlib import Path
import sys
import tempfile
import cv2

# 设置路径
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # 获取项目根目录
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "external_project"))

from src.make_train_dataset.make_train_dataset import MakeDataSet

app = FastAPI(title="数据集生成工具")

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保目录存在
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# 挂载模板
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/")
async def home(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
        return JSONResponse(
            content={"error": "页面加载失败，请检查服务器日志"}, status_code=500
        )


@app.post("/generate_dataset")
async def generate_dataset(
    video_file: UploadFile = File(...),
    save_folder: str = Form(...),
    is_debrisflow: str = Form("0"),  # 值为"0"或"1"
    data_type: str = Form("train"),
    frame_idx: int = Form(100),
    slice_windows_size: int = Form(75),
    extract_freq: int = Form(1),
    use_sam: str = Form("1"),  # 新增参数：是否使用SAM，值为"0"或"1"
    sam_model_type: Optional[str] = Form(None),
    sam_model_device: Optional[str] = Form(None),
    sam_checkpoint: Optional[str] = Form(None),
    show_photo: bool = Form(False),
    point_x: Optional[int] = Form(None),
    point_y: Optional[int] = Form(None),
):
    # 创建临时文件存储上传的视频
    temp_video_path = None

    try:
        # 将相对路径转换为绝对路径
        absolute_save_folder = os.path.join(ROOT, save_folder)

        # 检查保存路径是否存在
        if not os.path.exists(absolute_save_folder):
            try:
                os.makedirs(absolute_save_folder, exist_ok=True)
            except Exception as e:
                raise ValueError(
                    f"无法创建保存文件夹: {absolute_save_folder}, 错误: {str(e)}"
                )

        # 将上传的视频保存到临时文件
        _, temp_video_path = tempfile.mkstemp(suffix=".mp4")
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)

        # 转换为布尔值
        is_debrisflow_bool = is_debrisflow == "1"
        use_sam_bool = use_sam == "1"

        # 如果不使用SAM，则直接保存视频和最后一帧
        if not use_sam_bool:
            # 创建用于保存的文件夹
            label_dir = "1" if is_debrisflow_bool else "0"
            output_dir = os.path.join(absolute_save_folder, data_type, label_dir)
            os.makedirs(output_dir, exist_ok=True)

            # 读取视频
            cap = cv2.VideoCapture(temp_video_path)
            if not cap.isOpened():
                raise ValueError("无法打开视频文件")

            # 获取视频属性
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # 检查帧索引是否有效
            if frame_idx >= frame_count:
                frame_idx = frame_count - 1

            # 计算视频切片的起始和结束帧
            start_frame = frame_idx - slice_windows_size
            if start_frame < 0:
                start_frame = 0

            # 跳转到起始帧
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            # 保存图像文件名
            image_filename = (
                os.path.splitext(os.path.basename(video_file.filename))[0] + ".jpg"
            )
            image_path = os.path.join(output_dir, image_filename)

            # 保存视频文件名
            video_filename = (
                os.path.splitext(os.path.basename(video_file.filename))[0] + ".mp4"
            )
            video_path = os.path.join(output_dir, video_filename)

            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            video_writer = cv2.VideoWriter(
                video_path,
                fourcc,
                fps,
                (
                    int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                ),
            )

            # 读取帧并保存到视频
            last_frame = None
            frames_to_extract = frame_idx - start_frame + 1
            frame_count = 0

            while frame_count < frames_to_extract:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % extract_freq == 0:
                    video_writer.write(frame)
                    last_frame = frame.copy()

                frame_count += 1

            # 释放资源
            video_writer.release()

            # 保存最后一帧作为图像
            if last_frame is not None:
                cv2.imwrite(image_path, last_frame)

            cap.release()

            return JSONResponse(
                content={"message": f"成功保存视频和图像到 {output_dir}"},
                status_code=200,
            )
        else:
            # 使用SAM进行处理
            # 验证SAM相关参数
            if (
                sam_checkpoint is None
                or sam_model_type is None
                or sam_model_device is None
            ):
                raise ValueError("使用SAM时必须提供检查点路径、模型类型和运行设备")

            # 将SAM检查点相对路径转换为绝对路径
            absolute_sam_checkpoint = os.path.join(ROOT, sam_checkpoint)

            # 检查检查点文件是否存在
            if not os.path.exists(absolute_sam_checkpoint):
                raise FileNotFoundError(f"检查点文件不存在: {absolute_sam_checkpoint}")

            # 设置点坐标
            point_coordinates = None
            if point_x is not None and point_y is not None:
                point_coordinates = [point_x, point_y]

            # 创建数据集
            dataset_maker = MakeDataSet(
                save_folder=absolute_save_folder,
                video_file_path=temp_video_path,
                is_debrisflow=is_debrisflow_bool,
                data_type=data_type,
                frame_idx=frame_idx,
                slice_windows_size=slice_windows_size,
                extract_freq=extract_freq,
                point_coordinates=point_coordinates,
                sam_video_sign=False,
                sam_model_type=sam_model_type,
                sam_model_device=sam_model_device,
                sam_checkpoint=absolute_sam_checkpoint,
            )

            dataset_maker.make_dataset()

            return JSONResponse(
                content={"message": "数据集生成成功！"}, status_code=200
            )

    except Exception as e:
        print(f"Error generating dataset: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        # 清理临时文件
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
            except:
                pass


def start():
    """启动服务器"""
    uvicorn.run("web.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    print(f"模板目录: {TEMPLATES_DIR}")
    start()
