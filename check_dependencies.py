#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖检查和自动安装脚本
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        print(f"   当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def install_package(package_name, use_mirror=False):
    """安装Python包"""
    try:
        if use_mirror:
            cmd = [sys.executable, "-m", "pip", "install", package_name, 
                   "-i", "https://pypi.tuna.tsinghua.edu.cn/simple/"]
        else:
            cmd = [sys.executable, "-m", "pip", "install", package_name]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"   安装失败: {e}")
        return False

def check_and_install_package(package_name, import_name=None):
    """检查并安装包"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} 已安装")
        return True
    except ImportError:
        print(f"⚠️ {package_name} 未安装，正在安装...")
        
        # 先尝试正常安装
        if install_package(package_name):
            print(f"✅ {package_name} 安装成功")
            return True
        
        # 如果失败，尝试使用国内镜像
        print(f"   尝试使用国内镜像源...")
        if install_package(package_name, use_mirror=True):
            print(f"✅ {package_name} 安装成功（使用镜像源）")
            return True
        
        print(f"❌ {package_name} 安装失败")
        return False

def install_from_requirements():
    """从requirements.txt安装依赖"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        return False
    
    print("📦 从requirements.txt安装依赖...")
    try:
        # 先尝试正常安装
        cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ requirements.txt 依赖安装成功")
            return True
        
        # 如果失败，尝试使用国内镜像
        print("   尝试使用国内镜像源...")
        cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt",
               "-i", "https://pypi.tuna.tsinghua.edu.cn/simple/"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ requirements.txt 依赖安装成功（使用镜像源）")
            return True
        
        print("❌ requirements.txt 依赖安装失败")
        print(f"   错误信息: {result.stderr}")
        return False
        
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        return False

def main():
    """主函数"""
    print("🔍 检查Python环境和依赖...")
    print()
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    print()
    
    # 核心依赖列表
    core_dependencies = [
        ("psutil", "psutil"),  # (包名, 导入名)
    ]
    
    # 检查是否有requirements.txt
    if Path("requirements.txt").exists():
        print("📋 发现requirements.txt文件")
        if install_from_requirements():
            print()
            print("✅ 所有依赖安装完成")
            return True
    
    # 逐个检查核心依赖
    print("📦 检查核心依赖...")
    all_success = True
    
    for package_name, import_name in core_dependencies:
        if not check_and_install_package(package_name, import_name):
            all_success = False
    
    print()
    
    if all_success:
        print("✅ 所有依赖检查完成")
        return True
    else:
        print("❌ 部分依赖安装失败")
        print()
        print("手动安装命令:")
        for package_name, _ in core_dependencies:
            print(f"   pip install {package_name}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("\n按回车键退出...")
        sys.exit(1)
