project_name/
│
├── data/                        # 存放数据
│   ├── raw/                     # 原始数据（如视频文件）
│   ├── processed/               # 处理后的数据（如提取的特征）
|   └── vgg/                     # 用于VGG模型训练的数据（jpg格式）
|       ├── 1/                   # 泥石流图片
|       └── 0/                   # 非泥石流图片
│
├── external_project/            # 外部GitHub项目
│
├── models/                      # 存放模型
│   ├── pretrained/              # 预训练模型（如有）
│   └── trained/                 # 训练好的模型
│       ├── vgg/                 # 训练好的VGG模型
│       └── XGBoost/             # 训练好的XGBoost模型
│
├── notebooks/                   # Jupyter Notebooks（用于探索性分析）
│
├── src/                         # 源代码
│   ├── data_preprocessing/      # 数据预处理（如特征提取等）
│   ├── vgg_model/               # VGG的实现
│   │   ├── load_data.py         # VGG模型对应的数据加载
│   │   └── train.py             # VGG模型训练
|   ├── XGBoost/                 # XGBoost模型代码
|   |   └── train.py             # XGBoost模型训练 
│   └── utils/                   # 工具函数（如数据增强、日志记录等）
│
├── scripts/                     # 脚本文件（如训练、测试脚本）
│   ├── predict.py               # 全流程预测
│   ├── train_model.py           # 训练模型脚本
│   └── evaluate_model.py        # 评估模型脚本
│
├── requirements.txt             # 项目依赖
├── README.md                    # 项目说明
└── .gitignore                   # Git忽略文件



克隆外部项目库: 
    git clone https://github.com/facebookresearch/segment-anything.git external_project/SAM
