@echo off

:: 1. 克隆外部 GitHub 项目
echo ==========Cloning SAM project...==========
git clone https://github.com/facebookresearch/segment-anything.git external_project\SAM

:: 2. 创建虚拟环境并激活
echo ==========Creating and activating virtual environment...==========
python -m venv .venv
.venv\Scripts\activate

:: 3. 安装依赖
echo ==========Installing dependencies...==========
pip install -r requirements.txt

echo ==========Project setup completed!==========
