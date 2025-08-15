#!/bin/bash
# AugmentCode Unlimited 修复版GUI启动脚本

# 设置环境变量以消除macOS Tk警告
export TK_SILENCE_DEPRECATION=1

# 切换到项目目录
cd "$(dirname "$0")"

echo "🚀 正在启动 AugmentCode Unlimited GUI (修复版)..."

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3命令"
    exit 1
fi

# 启动GUI
python3 gui_main_fixed.py