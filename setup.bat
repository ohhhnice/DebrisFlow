@echo off

:: 1. 克隆外部 GitHub 项目
echo ==========   Cloning SAM project...   ==========
git clone https://github.com/facebookresearch/segment-anything.git external_project\SAM

:: 2. 创建虚拟环境并激活
echo ==========   Creating and activating virtual environment...   ==========
where py >nul 2>nul
if %errorlevel% == 0 (
    :: 检查是否有 Python 3.10
    py -3.10 --version >nul 2>nul
    if %errorlevel% == 0 (
        echo Python 3.10 found, creating virtual environment...
        py -3.10 -m venv .venv
    ) else (
        echo Python 3.10 not found, using default Python...
        py -m venv .venv
    )
) else (
    echo py launcher not found, falling back to default Python...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

:: 3. 安装依赖
echo ==========   Installing dependencies...   ==========
pip install -r requirements.txt

echo ==========   Project setup completed!   ==========