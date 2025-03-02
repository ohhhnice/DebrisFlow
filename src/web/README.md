<!-- @format -->

# 泥石流视频处理系统 - Web 界面

这是一个基于 Vue+FastAPI 的 Web 界面，用于可视化地设置和处理视频数据集的创建，支持设置`MakeDataSet`类的所有参数。

## 目录结构

```
src/web/
├── backend/             # FastAPI后端
│   ├── app.py           # 主应用程序
│   └── run_backend.py   # 后端启动脚本
├── frontend/            # Vue前端
│   ├── css/             # 样式文件
│   │   └── style.css    # 主样式表
│   ├── js/              # JavaScript文件
│   │   └── app.js       # Vue应用程序
│   ├── index.html       # HTML入口文件
│   └── run_frontend.py  # 前端启动脚本
└── README.md            # 本文档
```

## 功能特性

1. 视频上传和选择功能
2. 支持设置所有`MakeDataSet`类参数
3. 响应式表单布局
4. 表单验证
5. 处理结果显示
6. RESTful API 接口

## 运行方式

### 方法一：使用主启动脚本（推荐）

在项目根目录下运行：

```bash
python run/run_web_app.py
```

这将同时启动后端 API 和前端页面，并自动在浏览器中打开应用。

### 方法二：分别启动后端和前端

1. 启动后端服务：

```bash
python src/web/backend/run_backend.py
```

2. 在另一个终端中启动前端服务：

```bash
python src/web/frontend/run_frontend.py
```

## API 接口说明

后端提供以下 API 接口：

- `GET /`: API 根路径，返回欢迎信息
- `GET /list_videos`: 获取可用的视频文件列表
- `POST /upload_video`: 上传视频文件
- `POST /make_dataset`: 创建数据集，支持所有`MakeDataSet`类参数

## 参数说明

Web 界面支持的主要参数包括：

- **基本参数**：

  - `save_folder`: 保存文件夹路径
  - `video_file_path`: 视频文件路径
  - `is_debrisflow`: 是否为泥石流
  - `data_type`: 数据类型（train/val/test）
  - `frame_idx`: 帧索引
  - `slice_windows_size`: 切片窗口大小
  - `extract_freq`: 提取频率
  - `point_coordinates`: 兴趣点坐标

- **SAM 参数**：
  - `sam_video_sign`: 是否启用 SAM 视频处理
  - `sam_model_type`: SAM 模型类型（vit_h/vit_l/vit_b）
  - `sam_model_device`: 运行设备（auto/cpu/cuda）
  - `sam_checkpoint`: SAM 模型权重文件路径

## 注意事项

1. 确保项目根目录下的`data/sam/raw`文件夹存在，用于存放上传的视频文件
2. 确保 SAM 模型权重文件路径正确
3. 如需更改端口，可修改相应启动脚本中的设置：
   - 后端端口: `src/web/backend/run_backend.py` 中的 `port=8000`
   - 前端端口: `src/web/frontend/run_frontend.py` 中的 `PORT = 8080`
