#!/usr/bin/env python3
"""
AugmentCode Unlimited - 命令行版本
提供与GUI相同的功能，但使用命令行界面
"""

import sys
import os
import time
import logging
from pathlib import Path
import traceback

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# 全局变量
APP_NAME = "AugmentCode Unlimited CLI"
VERSION = "1.0.0"

try:
    from config.settings import VERSION, APP_NAME
    APP_NAME = f"{APP_NAME} CLI"
except ImportError:
    logger.warning("无法导入配置，使用默认值")

def print_banner():
    """打印程序横幅"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      {APP_NAME} v{VERSION}                       ║
║                                                                              ║
║  解除AugmentCode设备限制，实现无限账户切换                                   ║
║  支持: JetBrains IDEs, VSCode, VSCode Insiders, Cursor等                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

def init_components():
    """初始化组件"""
    print("🔧 正在初始化组件...")
    
    try:
        # 导入基础模块
        from utils.paths import PathManager
        from utils.backup import BackupManager
        print("✅ 基础模块加载成功")
        
        # 初始化基础组件
        path_manager = PathManager()
        backup_manager = BackupManager()
        print("✅ 基础组件初始化成功")
        
        # 导入核心处理模块
        from core.jetbrains_handler import JetBrainsHandler
        from core.vscode_handler import VSCodeHandler
        from core.db_cleaner import DatabaseCleaner
        print("✅ 核心模块加载成功")
        
        # 初始化核心组件
        jetbrains_handler = JetBrainsHandler(path_manager, backup_manager)
        vscode_handler = VSCodeHandler(path_manager, backup_manager)
        database_cleaner = DatabaseCleaner(path_manager, backup_manager)
        print("✅ 核心组件初始化成功")
        
        return {
            "path_manager": path_manager,
            "backup_manager": backup_manager,
            "jetbrains_handler": jetbrains_handler,
            "vscode_handler": vscode_handler,
            "database_cleaner": database_cleaner
        }
        
    except Exception as e:
        print(f"❌ 组件初始化失败: {str(e)}")
        traceback.print_exc()
        return None

def scan_system(components):
    """扫描系统"""
    print("\n🔍 开始扫描系统...")
    
    try:
        # 扫描JetBrains
        print("🔧 扫描 JetBrains IDEs...")
        jetbrains_info = components["jetbrains_handler"].verify_jetbrains_installation()
        if jetbrains_info['installed']:
            print(f"✅ 发现 JetBrains IDEs")
            print(f"   📁 配置目录: {jetbrains_info['config_dir']}")
            print(f"   📄 ID文件: {len(jetbrains_info['existing_files'])}/{len(jetbrains_info['id_files'])}")
        else:
            print("❌ 未发现 JetBrains IDEs")
        
        # 扫描VSCode
        print("📝 扫描 VSCode 系列...")
        vscode_info = components["vscode_handler"].verify_vscode_installation()
        if vscode_info['installed']:
            variants = ', '.join(vscode_info['variants_found'])
            print(f"✅ 发现 VSCode 变体: {variants}")
            print(f"   📁 存储目录: {vscode_info['total_directories']} 个")
        else:
            print("❌ 未发现 VSCode 系列编辑器")
        
        # 扫描数据库
        print("🗃️ 扫描数据库...")
        db_info = components["database_cleaner"].get_database_info()
        print(f"✅ 发现数据库: {db_info['total_databases']} 个")
        print(f"   📊 可访问: {db_info['accessible_databases']} 个")
        
        print("✅ 系统扫描完成！")
        return True
        
    except Exception as e:
        print(f"❌ 扫描失败: {str(e)}")
        traceback.print_exc()
        return False

def clean_system(components, options):
    """清理系统"""
    print("\n🚀 开始清理操作...")
    
    try:
        overall_success = False
        
        # 清理JetBrains
        if options["jetbrains"]:
            print("🔧 正在处理 JetBrains IDEs...")
            result = components["jetbrains_handler"].process_jetbrains_ides(
                create_backups=options["backup"],
                lock_files=options["lock"]
            )
            
            if result['success']:
                print(f"✅ JetBrains 处理成功")
                print(f"   📄 处理文件: {len(result['files_processed'])} 个")
                if result['backups_created']:
                    print(f"   💾 创建备份: {len(result['backups_created'])} 个")
                overall_success = True
            else:
                print("❌ JetBrains 处理失败")
                for error in result['errors'][:3]:
                    print(f"   ❌ {error}")
        
        # 清理VSCode
        if options["vscode"]:
            print("📝 正在处理 VSCode 系列...")
            result = components["vscode_handler"].process_vscode_installations(
                create_backups=options["backup"],
                lock_files=options["lock"],
                clean_workspace=options["workspace"]
            )
            
            if result['success']:
                print(f"✅ VSCode 处理成功")
                print(f"   📁 处理目录: {len(result['directories_processed'])} 个")
                if result['backups_created']:
                    print(f"   💾 创建备份: {len(result['backups_created'])} 个")
                overall_success = True
            else:
                print("❌ VSCode 处理失败")
                for error in result['errors'][:3]:
                    print(f"   ❌ {error}")
        
        # 清理数据库
        if options["database"] and options["vscode"]:
            print("🗃️ 正在清理数据库...")
            result = components["database_cleaner"].clean_all_databases(
                create_backups=options["backup"]
            )
            
            if result['success']:
                print(f"✅ 数据库清理成功")
                print(f"   🗑️ 删除记录: {result['total_records_deleted']} 条")
            else:
                print("❌ 数据库清理失败")
        
        # 完成
        if overall_success:
            print("\n🎉 清理操作完成！")
            print("\n📝 下一步操作:")
            print("   1️⃣ 重启您的IDE")
            print("   2️⃣ 使用新的AugmentCode账户登录")
            print("   3️⃣ 享受无限制的AI编程体验！")
            
            if options["backup"]:
                print(f"\n💾 备份位置: {components['backup_manager'].backup_dir}")
            
            return True
        else:
            print("\n❌ 清理操作失败")
            return False
            
    except Exception as e:
        print(f"❌ 清理过程中发生错误: {str(e)}")
        traceback.print_exc()
        return False

def get_user_options():
    """获取用户选项"""
    options = {
        "jetbrains": True,
        "vscode": True,
        "backup": True,
        "lock": True,
        "database": True,
        "workspace": True
    }
    
    print("\n⚙️ 请选择清理选项 (输入y/n):")
    
    options["jetbrains"] = input("🔧 清理 JetBrains IDEs? [Y/n]: ").lower() != 'n'
    options["vscode"] = input("📝 清理 VSCode 系列? [Y/n]: ").lower() != 'n'
    
    if not options["jetbrains"] and not options["vscode"]:
        print("❌ 错误: 至少需要选择一个IDE类型")
        return None
    
    options["backup"] = input("💾 创建备份 (强烈推荐)? [Y/n]: ").lower() != 'n'
    options["lock"] = input("🔒 锁定文件 (防止IDE重写)? [Y/n]: ").lower() != 'n'
    options["database"] = input("🗃️ 清理数据库记录? [Y/n]: ").lower() != 'n'
    options["workspace"] = input("📁 清理工作区存储? [Y/n]: ").lower() != 'n'
    
    print("\n📋 您选择的选项:")
    print(f"• JetBrains IDEs: {'是' if options['jetbrains'] else '否'}")
    print(f"• VSCode 系列: {'是' if options['vscode'] else '否'}")
    print(f"• 数据库清理: {'是' if options['database'] else '否'}")
    print(f"• 工作区清理: {'是' if options['workspace'] else '否'}")
    print(f"• 创建备份: {'是' if options['backup'] else '否'}")
    print(f"• 锁定文件: {'是' if options['lock'] else '否'}")
    
    confirm = input("\n确认以上选项并开始清理? [Y/n]: ").lower() != 'n'
    if not confirm:
        return None
    
    return options

def show_help():
    """显示帮助信息"""
    help_text = """🚀 AugmentCode Unlimited CLI 使用帮助

📋 功能说明:
• 清理AugmentCode相关的设备标识和认证数据
• 支持JetBrains全系列和VSCode系列编辑器
• 自动备份重要文件，支持一键恢复
• 智能锁定文件，防止IDE自动重写

🔧 使用步骤:
1. 运行扫描功能检测IDE安装情况
2. 选择要清理的IDE和清理选项
3. 执行清理操作
4. 重启IDE并使用新账户登录

⚠️ 注意事项:
• 清理前请关闭所有IDE程序
• 强烈建议保持"创建备份"选项开启
• 如遇问题可通过备份目录手动恢复

💡 命令行参数:
• --scan: 仅扫描系统
• --clean: 直接开始清理 (使用默认选项)
• --help: 显示此帮助信息

💡 技术支持:
• GitHub: https://github.com/wozhenbang2004/augetment-cursor-unlimited
• 问题反馈: 请在GitHub提交Issue"""
    
    print(help_text)

def parse_args():
    """解析命令行参数"""
    args = {
        "scan_only": False,
        "clean_direct": False,
        "show_help": False
    }
    
    if len(sys.argv) > 1:
        if "--scan" in sys.argv:
            args["scan_only"] = True
        if "--clean" in sys.argv:
            args["clean_direct"] = True
        if "--help" in sys.argv or "-h" in sys.argv:
            args["show_help"] = True
    
    return args

def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_args()
        
        # 显示帮助
        if args["show_help"]:
            show_help()
            return 0
        
        # 打印横幅
        print_banner()
        
        # 初始化组件
        components = init_components()
        if not components:
            print("❌ 组件初始化失败，程序无法继续")
            return 1
        
        # 扫描系统
        scan_success = scan_system(components)
        if not scan_success:
            print("❌ 系统扫描失败，程序无法继续")
            return 1
        
        # 如果只是扫描，则退出
        if args["scan_only"]:
            print("\n✅ 扫描完成，使用 --clean 参数执行清理")
            return 0
        
        # 获取用户选项
        if args["clean_direct"]:
            # 使用默认选项
            options = {
                "jetbrains": True,
                "vscode": True,
                "backup": True,
                "lock": True,
                "database": True,
                "workspace": True
            }
            print("\n⚙️ 使用默认选项进行清理")
        else:
            # 交互式获取选项
            options = get_user_options()
            if not options:
                print("❌ 操作已取消")
                return 1
        
        # 清理系统
        clean_success = clean_system(components, options)
        if not clean_success:
            print("❌ 清理失败")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 操作已被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 意外错误: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())