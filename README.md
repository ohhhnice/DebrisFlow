project_name/
│
├── data/                        # 存放数据
│   ├── raw/                     # 原始数据（如视频文件）
│   └── processed/               # 处理后的数据（如提取的特征）
│
├── external_project/                    # 外部GitHub项目
│
├── models/                      # 存放模型
│   ├── pretrained/              # 预训练模型（如有）
│   └── trained/                 # 训练好的模型
│
├── notebooks/                   # Jupyter Notebooks（用于探索性分析）
│
├── src/                         # 源代码
│   ├── data_preprocessing/      # 数据预处理（如特征提取等）
│   ├── model_1/                 # 模型1的实现
│   │   ├── model.py             # 模型1的定义
│   │   ├── train.py             # 模型1的训练代码
│   │   └── evaluate.py          # 模型1的评估代码
│   ├── evaluation/              # 评估代码
│   └── utils/                   # 工具函数（如数据增强、日志记录等）
│
├── scripts/                     # 脚本文件（如训练、测试脚本）
│   ├── train_model.py           # 训练模型脚本
│   └── evaluate_model.py        # 评估模型脚本
│
├── requirements.txt             # 项目依赖
├── README.md                    # 项目说明
└── .gitignore                   # Git忽略文件



克隆外部项目库: 
    git clone https://github.com/username/external_project.git external
