#!/bin/bash
# AugmentCode Unlimited CLI启动脚本

# 切换到项目目录
cd "$(dirname "$0")"

echo "🚀 正在启动 AugmentCode Unlimited CLI..."

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3命令"
    exit 1
fi

# 启动CLI
python3 cli_cleaner.py "$@"