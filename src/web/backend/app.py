import sys
from pathlib import Path
import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import shutil
import torch
import cv2
from fastapi.websockets import WebSocket

FILE = Path(__file__).resolve()
ROOT = FILE.parents[3]  # 项目根目录
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "external_project"))

from src.utils.load_video import extract_frames
from src.utils.frame_processor import FrameProcessor
from src.make_train_dataset.make_train_dataset import MakeDataSet


app = FastAPI(title="泥石流视频处理系统", description="基于SAM的泥石流视频处理Web界面")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 存储WebSocket连接
websocket_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        websocket_connections.remove(websocket)

# 发送进度信息给所有连接的客户端
async def send_progress(progress: float, message: str):
    for connection in websocket_connections:
        try:
            await connection.send_json({
                "progress": progress,
                "message": message
            })
        except Exception:
            # 忽略失败的发送
            pass

class MakeDatasetModel(BaseModel):
    """用于处理数据集创建请求的模型"""
    save_folder: str
    video_file_path: str
    is_debrisflow: bool
    data_type: str
    frame_idx: int
    slice_windows_size: int = 75
    extract_freq: int = 1
    point_coordinates: Optional[List[List[int]]] = None
    sam_video_sign: bool = False
    sam_model_type: Optional[str] = "vit_h"
    sam_model_device: Optional[str] = None
    sam_checkpoint: Optional[str] = "models/pretrained/sam/sam_vit_h_4b8939.pth"
    
    # 批处理参数
    batch_mode: bool = False
    batch_start_frame: Optional[int] = None
    batch_end_frame: Optional[int] = None
    batch_step: Optional[int] = None


@app.get("/")
async def root():
    """API根路径"""
    return {"message": "泥石流视频处理系统API"}


@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    """上传视频文件"""
    try:
        # 确保目录存在
        upload_dir = Path(ROOT) / "data" / "sam" / "raw"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存上传的文件
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 获取视频信息
        video_info = get_video_info(str(file_path))
        
        return {
            "filename": file.filename, 
            "file_path": str(file_path),
            "video_info": video_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/make_dataset")
async def make_dataset(data: MakeDatasetModel):
    """创建数据集"""
    try:
        # 如果未指定设备，则自动选择
        if data.sam_model_device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            data.sam_model_device = str(device)
            
        # 如果不是批处理模式，则直接处理单个帧
        if not data.batch_mode:
            # 创建MakeDataSet实例
            dataset_maker = MakeDataSet(
                save_folder=data.save_folder,
                video_file_path=data.video_file_path,
                is_debrisflow=data.is_debrisflow,
                data_type=data.data_type,
                frame_idx=data.frame_idx,
                slice_windows_size=data.slice_windows_size,
                extract_freq=data.extract_freq,
                point_coordinates=data.point_coordinates,
                sam_video_sign=data.sam_video_sign,
                sam_model_type=data.sam_model_type,
                sam_model_device=data.sam_model_device,
                sam_checkpoint=data.sam_checkpoint
            )
            
            # 处理数据集
            dataset_maker.make_dataset()
            
            return {
                "success": True,
                "message": f"数据集创建成功，已保存到 {data.save_folder}"
            }
        else:
            # 批处理模式
            if data.batch_start_frame is None or data.batch_end_frame is None or data.batch_step is None:
                raise HTTPException(status_code=400, detail="批处理模式下必须提供起始帧、结束帧和步长")
            
            # 计算要处理的帧列表
            frames_to_process = list(range(
                data.batch_start_frame, 
                min(data.batch_end_frame + 1, int(cv2.VideoCapture(data.video_file_path).get(cv2.CAP_PROP_FRAME_COUNT))),
                data.batch_step
            ))
            
            # 处理结果
            results = []
            total_frames = len(frames_to_process)
            
            # 批量处理每一帧
            for i, frame_idx in enumerate(frames_to_process):
                try:
                    # 计算并发送进度信息
                    progress = (i / total_frames) * 100
                    await send_progress(
                        progress, 
                        f"正在处理第 {i+1}/{total_frames} 帧 (帧索引: {frame_idx})"
                    )
                    
                    # 创建MakeDataSet实例
                    dataset_maker = MakeDataSet(
                        save_folder=data.save_folder,
                        video_file_path=data.video_file_path,
                        is_debrisflow=data.is_debrisflow,
                        data_type=data.data_type,
                        frame_idx=frame_idx,
                        slice_windows_size=data.slice_windows_size,
                        extract_freq=data.extract_freq,
                        point_coordinates=data.point_coordinates,
                        sam_video_sign=data.sam_video_sign,
                        sam_model_type=data.sam_model_type,
                        sam_model_device=data.sam_model_device,
                        sam_checkpoint=data.sam_checkpoint
                    )
                    
                    # 处理数据集
                    dataset_maker.make_dataset()
                    
                    results.append({
                        "frame_idx": frame_idx,
                        "success": True,
                        "save_folder": data.save_folder
                    })
                    
                except Exception as e:
                    results.append({
                        "frame_idx": frame_idx,
                        "success": False,
                        "error": str(e)
                    })
            
            # 发送完成进度
            await send_progress(100, "处理完成")
            
            # 统计成功和失败的数量
            success_count = sum(1 for r in results if r["success"])
            
            return {
                "success": True,
                "message": f"批处理完成，共处理 {len(frames_to_process)} 个帧，成功 {success_count} 个，失败 {len(frames_to_process) - success_count} 个",
                "results": results
            }
            
    except Exception as e:
        print(f"处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list_videos")
async def list_videos():
    """列出可用的视频文件"""
    try:
        videos_dir = Path(ROOT) / "data" / "sam" / "raw"
        videos_dir.mkdir(parents=True, exist_ok=True)
        
        video_files = []
        for file in videos_dir.glob("*.mp4"):
            # 获取视频信息
            video_info = get_video_info(str(file))
            
            video_files.append({
                "name": file.name,
                "path": str(file),
                "size": file.stat().st_size,
                "modified": file.stat().st_mtime,
                "info": video_info
            })
        
        return {"videos": video_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/video_info/{video_name}")
async def video_info(video_name: str):
    """获取指定视频的详细信息"""
    try:
        video_path = Path(ROOT) / "data" / "sam" / "raw" / video_name
        if not video_path.exists():
            raise HTTPException(status_code=404, detail=f"视频 {video_name} 不存在")
        
        video_info = get_video_info(str(video_path))
        
        return {
            "filename": video_name, 
            "file_path": str(video_path),
            "info": video_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/frame_images")
async def get_frame_images(
    video_path: str, 
    frame_idx: int, 
    window_size: int = 75, 
    extract_freq: int = 1,
    point_x: Optional[int] = None,
    point_y: Optional[int] = None
):
    """获取指定视频的帧图像"""
    try:
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail=f"视频文件 {video_path} 不存在")
        
        # 使用FrameProcessor获取帧图像
        frames_data = FrameProcessor.get_range_frames(
            video_path=video_path,
            center_idx=frame_idx,
            window_size=window_size,
            extract_freq=extract_freq
        )
        
        # 如果提供了兴趣点坐标，则在帧上绘制点
        point_coordinates = None
        if point_x is not None and point_y is not None:
            point_coordinates = [point_x, point_y]
            
            # 获取原始帧
            start_frame = FrameProcessor.get_frame(video_path, frames_data['start_idx'])
            end_frame = FrameProcessor.get_frame(video_path, frames_data['end_idx'])
            
            # 使用坐标绘制兴趣点并编码
            frames_data['start_frame'] = FrameProcessor.encode_frame_with_point(
                start_frame, point_coordinates
            )
            frames_data['end_frame'] = FrameProcessor.encode_frame_with_point(
                end_frame, point_coordinates
            )
        
        return frames_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_video_info(video_path: str):
    """获取视频的详细信息"""
    try:
        # 使用extract_frames函数获取基本信息
        fps, total_frames, resolution = extract_frames(video_path)
        
        return {
            "fps": fps,
            "total_frames": total_frames,
            "resolution": resolution
        }
    except Exception as e:
        print(f"获取视频信息失败: {str(e)}")
        return {
            "fps": 0,
            "total_frames": 0,
            "resolution": "未知",
            "error": str(e)
        }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 