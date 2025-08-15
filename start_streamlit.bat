@echo off
:: AugmentCode Unlimited Streamlit版本启动脚本 (Windows)

echo 🚀 正在启动 AugmentCode Unlimited Streamlit版本...

:: 检查Python3
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ 错误: 未找到python命令
    pause
    exit /b 1
)

:: 检查依赖
echo 📦 检查依赖...
python -c "import streamlit" >nul 2>nul
if %ERRORLEVEL% neq 0 goto :missing_deps
python -c "import plotly" >nul 2>nul
if %ERRORLEVEL% neq 0 goto :missing_deps
python -c "import pandas" >nul 2>nul
if %ERRORLEVEL% neq 0 goto :missing_deps
python -c "import numpy" >nul 2>nul
if %ERRORLEVEL% neq 0 goto :missing_deps
python -c "import psutil" >nul 2>nul
if %ERRORLEVEL% neq 0 goto :missing_deps

goto :start_app

:missing_deps
echo ⚠️ 缺少必要的依赖包
echo 是否自动安装这些依赖? (y/n):
set /p REPLY=
if /i "%REPLY%"=="y" (
    echo 📥 正在安装依赖...
    python -m pip install streamlit>=1.28.0 plotly>=5.15.0 pandas>=1.5.0 numpy>=1.24.0 psutil>=5.9.0
    if %ERRORLEVEL% neq 0 (
        echo ❌ 依赖安装失败，请手动安装以下包:
        echo   pip install streamlit>=1.28.0 plotly>=5.15.0 pandas>=1.5.0 numpy>=1.24.0 psutil>=5.9.0
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
) else (
    echo ❌ 请手动安装以下依赖后再运行:
    echo   pip install streamlit>=1.28.0 plotly>=5.15.0 pandas>=1.5.0 numpy>=1.24.0 psutil>=5.9.0
    pause
    exit /b 1
)

:start_app
:: 启动Streamlit应用
echo 🚀 启动Streamlit应用...
streamlit run streamlit_app.py

pause