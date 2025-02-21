#!/bin/bash

# 1. 克隆外部 GitHub 项目
echo "Cloning external GitHub project..."
# 确保 external_project 文件夹存在
mkdir -p external_project
cd external_project
git clone https://github.com/username/repo.git
cd ..

# 2. 创建虚拟环境并激活
echo "Creating and activating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 4. 数据准备（如有必要，提供下载或其他数据准备步骤）
echo "Preparing data..."
# 这里可以写数据准备的相关命令，或者给出下载数据的链接

echo "Project setup completed!"
