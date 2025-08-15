#!/bin/bash
# AugmentCode Unlimited Streamlit版本启动脚本

# 切换到项目目录
cd "$(dirname "$0")"

echo "🚀 正在启动 AugmentCode Unlimited Streamlit版本..."

# 检查是否以root/管理员权限运行
if [ "$(id -u)" != "0" ]; then
    echo "⚠️ 提示: 当前以普通用户权限运行"
    echo "💡 如果遇到权限问题，请尝试使用 'sudo ./start_streamlit.sh' 以管理员权限运行"
    echo ""
else
    echo "✅ 以管理员权限运行"
fi

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3命令"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
REQUIRED_PACKAGES=(
    "streamlit>=1.28.0"
    "plotly>=5.15.0"
    "pandas>=1.5.0"
    "numpy>=1.24.0"
    "psutil>=5.9.0"
)

MISSING_PACKAGES=()
for package in "${REQUIRED_PACKAGES[@]}"; do
    package_name=$(echo "$package" | cut -d'>' -f1)
    if ! python3 -c "import $package_name" &>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

# 安装缺失的依赖
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "⚠️ 缺少以下依赖包:"
    for package in "${MISSING_PACKAGES[@]}"; do
        echo "  - $package"
    done
    
    read -p "是否自动安装这些依赖? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 正在安装依赖..."
        python3 -m pip install "${MISSING_PACKAGES[@]}"
        if [ $? -ne 0 ]; then
            echo "❌ 依赖安装失败，请手动安装以下包:"
            for package in "${MISSING_PACKAGES[@]}"; do
                echo "  pip install $package"
            done
            exit 1
        fi
        echo "✅ 依赖安装完成"
    else
        echo "❌ 请手动安装以下依赖后再运行:"
        for package in "${MISSING_PACKAGES[@]}"; do
            echo "  pip install $package"
        done
        exit 1
    fi
fi

# 启动Streamlit应用
echo "🚀 启动Streamlit应用..."
streamlit run streamlit_app.py
