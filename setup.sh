#!/bin/bash

# 1. 克隆外部 GitHub 项目
echo "==========   Cloning SAM project...   =========="
git clone https://github.com/facebookresearch/segment-anything.git external_project/SAM

# 2. 创建虚拟环境并激活
echo "==========   Creating and activating virtual environment...   =========="

# 检查是否安装 Python 3.10
if command -v python3.10 &> /dev/null; then
    echo "Python 3.10 found, creating virtual environment..."
    python3.10 -m venv .venv
else
    echo "Python 3.10 not found, using default Python..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 3. 安装依赖
echo "==========   Installing dependencies...   =========="
pip install -r requirements.txt

echo "==========   Project setup completed!   =========="
