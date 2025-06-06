#!/usr/bin/env python3
"""
构建 Augment Cleaner Unified 的可执行文件

使用 PyInstaller 将 GUI 版本打包成 exe 文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查 PyInstaller 是否安装"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller 已安装，版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装")
        return False

def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"])
        print("✅ PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 安装失败: {e}")
        print("\n💡 解决方案:")
        print("1. 检查网络连接")
        print("2. 尝试使用国内镜像源:")
        print(f"   {sys.executable} -m pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple/")
        print("3. 或者手动下载PyInstaller安装包")
        print("4. 如果使用Anaconda，尝试: conda install pyinstaller -c conda-forge")
        return False

def create_icon():
    """创建简单的图标文件（如果不存在）"""
    icon_path = Path("icon.ico")
    if not icon_path.exists():
        print("📝 创建默认图标...")
        # 这里可以放置一个简单的图标创建逻辑
        # 或者用户可以手动放置 icon.ico 文件
        print("💡 提示: 您可以将 icon.ico 文件放在项目根目录来自定义图标")

def build_executable():
    """构建可执行文件"""
    print("🚀 开始构建可执行文件...")

    # 检查并关闭可能正在运行的exe文件
    exe_path = Path("dist") / "AugmentCleanerUnified.exe"
    if exe_path.exists():
        print("⚠️ 检测到已存在的exe文件，尝试删除...")
        try:
            exe_path.unlink()
            print("✅ 旧exe文件已删除")
        except PermissionError:
            print("⚠️ 无法删除旧exe文件（可能正在运行），PyInstaller会尝试覆盖")
    
    # PyInstaller 命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # 无控制台窗口
        "--name=AugmentCleanerUnified", # 可执行文件名
        "--distpath=dist",              # 输出目录
        "--workpath=build",             # 临时文件目录
        "--specpath=.",                 # spec文件位置
        "--clean",                      # 清理临时文件
        "--noconfirm",                  # 不询问覆盖
        "gui_main.py"                   # 主文件
    ]
    
    # 添加图标（如果存在）
    icon_path = Path("icon.ico")
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
        print(f"📎 使用图标: {icon_path}")
    
    # 添加隐藏导入（确保所有模块都被包含）
    hidden_imports = [
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.scrolledtext",
        "threading",
        "pathlib",
        "sqlite3",
        "json",
        "uuid",
        "hashlib",
        "secrets",
        "shutil",
        "stat",
        "subprocess",
        "time",
        "logging",
    ]
    
    for module in hidden_imports:
        cmd.extend(["--hidden-import", module])
    
    # 添加数据文件（如果需要）
    # cmd.extend(["--add-data", "config;config"])
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行 PyInstaller
        print("正在执行 PyInstaller...")
        result = subprocess.run(cmd, check=False, capture_output=False, text=True)

        # 检查输出文件
        exe_path = Path("dist") / "AugmentCleanerUnified.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("✅ 构建成功!")
            print(f"📦 可执行文件: {exe_path}")
            print(f"📏 文件大小: {size_mb:.1f} MB")
            return True
        else:
            print("❌ 可执行文件未找到")
            print(f"PyInstaller 返回代码: {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ 构建过程出现异常: {e}")

        # 即使出现异常，也检查是否生成了exe文件
        exe_path = Path("dist") / "AugmentCleanerUnified.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("⚠️ 虽然有异常，但exe文件已生成!")
            print(f"📦 可执行文件: {exe_path}")
            print(f"📏 文件大小: {size_mb:.1f} MB")
            return True

        return False



def create_readme():
    """创建使用说明"""
    readme_content = """# Augment Cleaner Unified - 可执行版本

## 🎯 简介
这是 Augment Cleaner Unified 的图形界面版本，已打包成可执行文件，无需安装 Python 即可使用。

## 🚀 快速开始

1. 双击 `AugmentCleanerUnified.exe`
2. 按照界面提示操作

## 📋 使用步骤

1. **准备工作**
   - 关闭所有 IDE（VSCode、JetBrains IDEs、Cursor等）
   - 退出 AugmentCode 插件

2. **运行程序**
   - 双击可执行文件启动
   - 查看系统状态，确认检测到相关软件

3. **配置选项**
   - 选择要处理的IDE类型
   - 建议保持默认设置（创建备份、锁定文件等）

4. **开始清理**
   - 点击"🚀 开始清理"按钮
   - 等待处理完成

5. **完成**
   - 重启 IDE
   - 使用新的 AugmentCode 账户登录

## 🛡️ 安全特性

- ✅ **自动备份**: 修改前自动备份所有文件
- ✅ **文件锁定**: 防止修改被覆盖
- ✅ **详细日志**: 记录所有操作过程
- ✅ **错误恢复**: 出错时可从备份恢复

## 📁 备份位置

备份文件保存在: `C:\\Users\\你的用户名\\.augment_cleaner_backups\\`

## ❓ 常见问题

**Q: 程序无法启动？**
A: 尝试以管理员身份运行，或检查杀毒软件是否误报

**Q: 提示权限不足？**
A: 以管理员身份运行程序

**Q: 清理后还是无法切换账户？**
A: 确保完全关闭了IDE，并重启后再登录

**Q: 如何恢复原始设置？**
A: 从备份目录恢复相应文件

## 📞 技术支持

如有问题，请查看程序内的操作日志，或检查备份目录中的文件。

---

**注意**: 此工具仅用于学习和研究目的，请遵守相关软件的使用条款。
"""
    
    with open("README_EXE.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ 创建使用说明: README_EXE.md")

def main():
    """主函数"""
    print("🔨 Augment Cleaner Unified 构建工具")
    print("=" * 50)
    
    # 检查 PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装 PyInstaller，构建失败")
            return False
    
    # 创建图标
    create_icon()
    
    # 构建可执行文件
    if not build_executable():
        print("❌ 构建失败")
        return False
    
    # 创建说明文件
    create_readme()
    
    print("\n" + "=" * 50)
    print("🎉 构建完成！")
    print("\n📦 输出文件:")
    print("   - dist/AugmentCleanerUnified.exe  (主程序)")
    print("   - README_EXE.md                   (使用说明)")
    print("\n🚀 使用方法:")
    print("   直接运行: 双击 AugmentCleanerUnified.exe")
    
    return True

if __name__ == "__main__":
    main()
