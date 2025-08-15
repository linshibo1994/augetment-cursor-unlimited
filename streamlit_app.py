#!/usr/bin/env python3
"""
AugmentCode Unlimited - Streamlit版本
使用Streamlit框架实现的GUI界面，提供与原GUI相同的功能
"""

try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    import psutil
except ImportError:
    print("错误: 缺少必要的依赖包。请运行: pip install streamlit>=1.28.0 plotly>=5.15.0 pandas>=1.5.0 numpy>=1.24.0 psutil>=5.9.0")
    import sys
    sys.exit(1)
import sys
import os
import time
import threading
import traceback
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 全局变量
APP_NAME = "AugmentCode Unlimited"
VERSION = "2.0.0"

try:
    from config.settings import VERSION, APP_NAME
except ImportError:
    st.warning("无法导入配置，使用默认值")

# 初始化会话状态
if 'backend_ready' not in st.session_state:
    st.session_state.backend_ready = False
if 'components' not in st.session_state:
    st.session_state.components = None
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None
if 'clean_results' not in st.session_state:
    st.session_state.clean_results = None
if 'is_cleaning' not in st.session_state:
    st.session_state.is_cleaning = False

def log_message(message, level="info"):
    """添加日志消息到会话状态"""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.log_messages.append({
        "timestamp": timestamp,
        "message": message,
        "level": level
    })

def check_permissions():
    """检查并请求必要的权限"""
    try:
        log_message("🔒 检查文件权限...")
        
        # 检查备份目录权限
        backup_dir = os.path.expanduser("~/.augment_cleaner_backups")
        if not os.path.exists(backup_dir):
            try:
                os.makedirs(backup_dir, exist_ok=True)
                log_message(f"✅ 创建备份目录: {backup_dir}")
            except PermissionError:
                log_message(f"⚠️ 无法创建备份目录: {backup_dir}", "warning")
                return False
        
        # 检查JetBrains目录权限
        jetbrains_dir = os.path.expanduser("~/Library/Application Support/JetBrains")
        if os.path.exists(jetbrains_dir):
            try:
                # 尝试创建测试文件
                test_file = os.path.join(jetbrains_dir, ".permission_test")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                log_message("✅ JetBrains目录权限正常")
            except PermissionError:
                log_message("⚠️ JetBrains目录需要更高权限", "warning")
                log_message("💡 提示: 请尝试以管理员/sudo权限运行", "warning")
                log_message("💡 macOS用户: 请尝试以下命令:", "warning")
                log_message("   sudo chmod -R 755 ~/Library/Application\\ Support/JetBrains", "warning")
                log_message("   sudo chown -R $(whoami) ~/Library/Application\\ Support/JetBrains", "warning")
                return False
        
        # 检查VSCode目录权限
        vscode_dir = os.path.expanduser("~/Library/Application Support/Code")
        if os.path.exists(vscode_dir):
            try:
                # 尝试创建测试文件
                test_file = os.path.join(vscode_dir, ".permission_test")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                log_message("✅ VSCode目录权限正常")
            except PermissionError:
                log_message("⚠️ VSCode目录需要更高权限", "warning")
                log_message("💡 提示: 请尝试以管理员/sudo权限运行", "warning")
                log_message("💡 macOS用户: 请尝试以下命令:", "warning")
                log_message("   sudo chmod -R 755 ~/Library/Application\\ Support/Code", "warning")
                log_message("   sudo chown -R $(whoami) ~/Library/Application\\ Support/Code", "warning")
                return False
        
        return True
    except Exception as e:
        log_message(f"❌ 权限检查失败: {str(e)}", "error")
        return False

def init_backend():
    """初始化后端组件"""
    if st.session_state.backend_ready:
        return True
    
    # 检查权限
    check_permissions()
    
    try:
        log_message("🔧 正在加载核心模块...")
        
        # 导入基础模块
        try:
            from utils.paths import PathManager
            from utils.backup import BackupManager
            log_message("✅ 基础模块加载成功")
            
            # 初始化基础组件
            path_manager = PathManager()
            backup_manager = BackupManager()
            log_message("✅ 基础组件初始化成功")
            
            # 导入核心处理模块
            try:
                from core.jetbrains_handler import JetBrainsHandler
                from core.vscode_handler import VSCodeHandler
                from core.db_cleaner import DatabaseCleaner
                log_message("✅ 核心模块加载成功")
                
                # 初始化核心组件
                jetbrains_handler = JetBrainsHandler(path_manager, backup_manager)
                vscode_handler = VSCodeHandler(path_manager, backup_manager)
                database_cleaner = DatabaseCleaner(path_manager, backup_manager)
                log_message("✅ 核心组件初始化成功")
                
                # 保存组件到会话状态
                st.session_state.components = {
                    "path_manager": path_manager,
                    "backup_manager": backup_manager,
                    "jetbrains_handler": jetbrains_handler,
                    "vscode_handler": vscode_handler,
                    "database_cleaner": database_cleaner
                }
                
                st.session_state.backend_ready = True
                log_message("✅ 后端组件初始化完成")
                log_message("💡 点击 '扫描系统' 开始检测您的IDE安装情况")
                log_message("⚠️  建议在清理前关闭所有IDE程序")
                
                return True
                
            except Exception as e:
                log_message(f"❌ 核心模块加载失败: {str(e)}", "error")
                log_message("⚠️ 部分功能可能不可用", "warning")
                return False
                
        except Exception as e:
            log_message(f"❌ 基础模块加载失败: {str(e)}", "error")
            log_message("⚠️ 程序无法正常工作", "error")
            return False
            
    except Exception as e:
        log_message(f"❌ 后端初始化失败: {str(e)}", "error")
        log_message("⚠️ 部分功能可能不可用", "warning")
        traceback.print_exc()
        return False

def scan_system():
    """扫描系统"""
    if not st.session_state.backend_ready:
        st.warning("后端组件尚未初始化完成，请稍候...")
        return
    
    components = st.session_state.components
    
    with st.spinner("正在扫描系统..."):
        try:
            log_message("🔍 开始扫描系统...")
            
            # 扫描JetBrains
            log_message("🔧 扫描 JetBrains IDEs...")
            jetbrains_info = components["jetbrains_handler"].verify_jetbrains_installation()
            
            # 扫描VSCode
            log_message("📝 扫描 VSCode 系列...")
            vscode_info = components["vscode_handler"].verify_vscode_installation()
            
            # 扫描数据库
            log_message("🗃️ 扫描数据库...")
            db_info = components["database_cleaner"].get_database_info()
            
            # 保存扫描结果
            st.session_state.scan_results = {
                "jetbrains": jetbrains_info,
                "vscode": vscode_info,
                "database": db_info,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 显示扫描结果
            if jetbrains_info['installed']:
                log_message(f"✅ 发现 JetBrains IDEs")
                log_message(f"   📁 配置目录: {jetbrains_info['config_dir']}")
                log_message(f"   📄 ID文件: {len(jetbrains_info['existing_files'])}/{len(jetbrains_info['id_files'])}")
            else:
                log_message("❌ 未发现 JetBrains IDEs")
            
            if vscode_info['installed']:
                variants = ', '.join(vscode_info['variants_found'])
                log_message(f"✅ 发现 VSCode 变体: {variants}")
                log_message(f"   📁 存储目录: {vscode_info['total_directories']} 个")
            else:
                log_message("❌ 未发现 VSCode 系列编辑器")
            
            log_message(f"✅ 发现数据库: {db_info['total_databases']} 个")
            log_message(f"   📊 可访问: {db_info['accessible_databases']} 个")
            
            log_message("✅ 系统扫描完成！")
            
            return True
            
        except Exception as e:
            log_message(f"❌ 扫描失败: {str(e)}", "error")
            traceback.print_exc()
            return False

def start_cleaning():
    """开始清理"""
    if not st.session_state.backend_ready:
        st.warning("后端组件尚未初始化完成，请稍候...")
        return
        
    if st.session_state.is_cleaning:
        st.warning("清理正在进行中，请稍候...")
        return
    
    components = st.session_state.components
    
    # 获取选项
    options = {
        "jetbrains": st.session_state.jetbrains,
        "vscode": st.session_state.vscode,
        "backup": st.session_state.backup,
        "lock": st.session_state.lock,
        "database": st.session_state.database,
        "workspace": st.session_state.workspace
    }
    
    if not (options["jetbrains"] or options["vscode"]):
        st.warning("请至少选择一个IDE清理选项！")
        return
    
    # 检查权限
    if not check_permissions():
        st.warning("⚠️ 权限不足，部分文件可能无法清理。请尝试以管理员/sudo权限运行。")
        log_message("⚠️ 权限不足，部分文件可能无法清理", "warning")
        log_message("💡 提示: 在macOS上，请尝试使用 'sudo ./start_streamlit.sh'", "warning")
        log_message("💡 提示: 在Windows上，请右键点击批处理文件并选择'以管理员身份运行'", "warning")
        
        # 询问用户是否继续
        if not st.session_state.get("continue_without_permissions", False):
            st.session_state.continue_without_permissions = True
            return
    
    st.session_state.is_cleaning = True
    
    with st.spinner("正在清理..."):
        try:
            log_message("🚀 开始清理操作...")
            
            overall_success = False
            clean_results = {
                "jetbrains": None,
                "vscode": None,
                "database": None,
                "success": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 清理JetBrains
            if options["jetbrains"]:
                log_message("🔧 正在处理 JetBrains IDEs...")
                result = components["jetbrains_handler"].process_jetbrains_ides(
                    create_backups=options["backup"],
                    lock_files=options["lock"]
                )
                
                clean_results["jetbrains"] = result
                
                if result['success']:
                    log_message(f"✅ JetBrains 处理成功")
                    log_message(f"   📄 处理文件: {len(result['files_processed']) if result['files_processed'] else 0} 个")
                    if result['backups_created'] and isinstance(result['backups_created'], list):
                        log_message(f"   💾 创建备份: {len(result['backups_created'])} 个")
                    overall_success = True
                else:
                    log_message("❌ JetBrains 处理失败", "error")
                    for error in result['errors'][:3]:
                        log_message(f"   ❌ {error}", "error")
            
            # 清理VSCode
            if options["vscode"]:
                log_message("📝 正在处理 VSCode 系列...")
                result = components["vscode_handler"].process_vscode_installations(
                    create_backups=options["backup"],
                    lock_files=options["lock"],
                    clean_workspace=options["workspace"]
                )
                
                clean_results["vscode"] = result
                
                if result['success']:
                    log_message(f"✅ VSCode 处理成功")
                    if isinstance(result['directories_processed'], list):
                        log_message(f"   📁 处理目录: {len(result['directories_processed'])} 个")
                    elif isinstance(result['directories_processed'], int):
                        log_message(f"   📁 处理目录: {result['directories_processed']} 个")
                    else:
                        log_message(f"   📁 处理目录: 0 个")
                    
                    if result['backups_created'] and isinstance(result['backups_created'], list):
                        log_message(f"   💾 创建备份: {len(result['backups_created'])} 个")
                    elif result['backups_created'] and isinstance(result['backups_created'], int):
                        log_message(f"   💾 创建备份: {result['backups_created']} 个")
                    overall_success = True
                else:
                    log_message("❌ VSCode 处理失败", "error")
                    for error in result['errors'][:3]:
                        log_message(f"   ❌ {error}", "error")
            
                # 清理数据库
                if options["database"] and options["vscode"]:
                    log_message("🗃️ 正在清理数据库...")
                    try:
                        # 清理VSCode数据库
                        vscode_result = components["database_cleaner"].clean_vscode_databases(
                            create_backups=options["backup"]
                        )
                        
                        # 清理JetBrains数据库
                        jetbrains_result = components["database_cleaner"].clean_jetbrains_databases(
                            create_backups=options["backup"]
                        )
                        
                        # 合并结果
                        result = {
                            "success": vscode_result["success"] or jetbrains_result["success"],
                            "databases_cleaned": vscode_result["databases_cleaned"] + jetbrains_result["databases_cleaned"],
                            "databases_failed": vscode_result["databases_failed"] + jetbrains_result["databases_failed"],
                            "total_records_deleted": vscode_result["total_records_deleted"] + jetbrains_result["total_records_deleted"],
                            "backups_created": vscode_result["backups_created"] + jetbrains_result["backups_created"],
                            "errors": vscode_result["errors"] + jetbrains_result["errors"]
                        }
                    except Exception as e:
                        log_message(f"⚠️ 数据库清理过程中发生错误: {str(e)}", "warning")
                        result = {
                            "success": False,
                            "errors": [str(e)],
                            "databases_cleaned": 0,
                            "databases_failed": 0,
                            "total_records_deleted": 0,
                            "backups_created": []
                        }
                
                clean_results["database"] = result
                
                if result['success']:
                    log_message(f"✅ 数据库清理成功")
                    log_message(f"   🗑️ 删除记录: {result['total_records_deleted']} 条")
                else:
                    log_message("❌ 数据库清理失败", "error")
            
            # 完成
            clean_results["success"] = overall_success
            st.session_state.clean_results = clean_results
            
            if overall_success:
                log_message("🎉 清理操作完成！")
                log_message("")
                log_message("📝 下一步操作:")
                log_message("   1️⃣ 重启您的IDE")
                log_message("   2️⃣ 使用新的AugmentCode账户登录")
                log_message("   3️⃣ 享受无限制的AI编程体验！")
                
                if options["backup"]:
                    backup_dir = components["backup_manager"].backup_dir
                    log_message(f"💾 备份位置: {backup_dir}")
                
                st.success("🎉 AugmentCode数据清理完成！")
            else:
                log_message("❌ 清理操作失败", "error")
                st.error("清理操作未能成功完成，请查看日志了解详情。")
            
            return overall_success
            
        except Exception as e:
            log_message(f"❌ 清理过程中发生错误: {str(e)}", "error")
            traceback.print_exc()
            st.error(f"清理过程中发生错误: {str(e)}")
            return False
        finally:
            st.session_state.is_cleaning = False

def show_help():
    """显示帮助信息"""
    help_text = """🚀 AugmentCode Unlimited 使用帮助

📋 功能说明:
• 清理AugmentCode相关的设备标识和认证数据
• 支持JetBrains全系列和VSCode系列编辑器
• 自动备份重要文件，支持一键恢复
• 智能锁定文件，防止IDE自动重写

🔧 使用步骤:
1. 点击"扫描系统"检测IDE安装情况
2. 选择要清理的IDE和清理选项
3. 点击"开始清理"执行清理操作
4. 重启IDE并使用新账户登录

⚠️ 注意事项:
• 清理前请关闭所有IDE程序
• 强烈建议保持"创建备份"选项开启
• 如遇问题可通过备份目录手动恢复

💡 技术支持:
• GitHub: https://github.com/wozhenbang2004/augetment-cursor-unlimited
• 问题反馈: 请在GitHub提交Issue"""
    
    st.info(help_text)

def render_log_messages():
    """渲染日志消息"""
    if not st.session_state.log_messages:
        st.text("暂无日志消息")
        return
    
    log_df = pd.DataFrame(st.session_state.log_messages)
    
    # 创建HTML表格
    html = '<div class="log-container" style="height: 300px; overflow-y: auto; background-color: #f8f9fa; border-radius: 5px; padding: 10px; font-family: monospace;">'
    
    for _, log in log_df.iterrows():
        timestamp = log["timestamp"]
        message = log["message"]
        level = log["level"]
        
        # 根据级别设置颜色
        if level == "error":
            color = "red"
        elif level == "warning":
            color = "orange"
        else:
            color = "black"
        
        html += f'<div style="margin-bottom: 5px;"><span style="color: #666;">[{timestamp}]</span> <span style="color: {color};">{message}</span></div>'
    
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)

def render_scan_results():
    """渲染扫描结果"""
    if not st.session_state.scan_results:
        return
    
    scan_results = st.session_state.scan_results
    
    # 创建JetBrains图表
    if scan_results["jetbrains"]["installed"]:
        st.subheader("🔧 JetBrains IDEs")
        
        # 创建饼图
        jetbrains_data = {
            "状态": ["已找到", "未找到"],
            "数量": [
                len(scan_results["jetbrains"]["existing_files"]),
                len(scan_results["jetbrains"]["missing_files"])
            ]
        }
        
        fig = px.pie(
            jetbrains_data,
            values="数量",
            names="状态",
            title="JetBrains ID文件状态",
            color="状态",
            color_discrete_map={"已找到": "#4CAF50", "未找到": "#F44336"}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示文件列表
        if scan_results["jetbrains"]["existing_files"]:
            with st.expander("查看已找到的文件"):
                for file_path in scan_results["jetbrains"]["existing_files"]:
                    st.text(f"✓ {file_path}")
        
        if scan_results["jetbrains"]["missing_files"]:
            with st.expander("查看未找到的文件"):
                for file_path in scan_results["jetbrains"]["missing_files"]:
                    st.text(f"✗ {file_path}")
    
    # 创建VSCode图表
    if scan_results["vscode"]["installed"]:
        st.subheader("📝 VSCode 变体")
        
        # 创建条形图
        vscode_data = pd.DataFrame({
            "变体": scan_results["vscode"]["variants_found"],
            "目录数量": [scan_results["vscode"]["total_directories"]] * len(scan_results["vscode"]["variants_found"])
        })
        
        fig = px.bar(
            vscode_data,
            x="变体",
            y="目录数量",
            title="VSCode变体分布",
            color="变体"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示存储目录
        with st.expander("查看存储目录"):
            for directory in scan_results["vscode"]["storage_directories"][:10]:
                st.text(f"• {directory}")
            
            if len(scan_results["vscode"]["storage_directories"]) > 10:
                st.text(f"... 以及 {len(scan_results['vscode']['storage_directories']) - 10} 个更多目录")
    
    # 创建数据库图表
    if scan_results["database"]["total_databases"] > 0:
        st.subheader("🗃️ 数据库")
        
        # 创建条形图
        db_data = {
            "类型": ["可访问", "不可访问"],
            "数量": [
                scan_results["database"]["accessible_databases"],
                scan_results["database"]["total_databases"] - scan_results["database"]["accessible_databases"]
            ]
        }
        
        fig = px.bar(
            db_data,
            x="类型",
            y="数量",
            title="数据库可访问性",
            color="类型",
            color_discrete_map={"可访问": "#4CAF50", "不可访问": "#F44336"}
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_clean_results():
    """渲染清理结果"""
    if not st.session_state.clean_results:
        return
    
    clean_results = st.session_state.clean_results
    
    if clean_results["success"]:
        st.subheader("🎉 清理结果")
        
        # 创建清理结果图表
        results_data = {
            "类型": [],
            "成功": [],
            "失败": []
        }
        
        if clean_results["jetbrains"]:
            results_data["类型"].append("JetBrains")
            if isinstance(clean_results["jetbrains"]["files_processed"], list):
                results_data["成功"].append(len(clean_results["jetbrains"]["files_processed"]))
            else:
                results_data["成功"].append(0)
            
            if isinstance(clean_results["jetbrains"]["errors"], list):
                results_data["失败"].append(len(clean_results["jetbrains"]["errors"]))
            else:
                results_data["失败"].append(0)
        
        if clean_results["vscode"]:
            results_data["类型"].append("VSCode")
            results_data["成功"].append(len(clean_results["vscode"]["directories_processed"]) if isinstance(clean_results["vscode"]["directories_processed"], list) else 0)
            results_data["失败"].append(len(clean_results["vscode"]["errors"]) if isinstance(clean_results["vscode"]["errors"], list) else 0)
        
        if clean_results["database"]:
            results_data["类型"].append("数据库")
            results_data["成功"].append(clean_results["database"]["databases_cleaned"] if isinstance(clean_results["database"]["databases_cleaned"], int) else 0)
            results_data["失败"].append(clean_results["database"]["databases_failed"] if isinstance(clean_results["database"]["databases_failed"], int) else 0)
        
        if results_data["类型"]:
            results_df = pd.DataFrame(results_data)
            
            fig = px.bar(
                results_df,
                x="类型",
                y=["成功", "失败"],
                title="清理结果统计",
                barmode="group",
                color_discrete_map={"成功": "#4CAF50", "失败": "#F44336"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # 显示备份信息
        has_backups = False
        backup_count = 0
        
        if clean_results["jetbrains"] and clean_results["jetbrains"].get("backups_created") and isinstance(clean_results["jetbrains"]["backups_created"], list):
            has_backups = True
            backup_count += len(clean_results["jetbrains"]["backups_created"])
        
        if clean_results["vscode"] and clean_results["vscode"].get("backups_created") and isinstance(clean_results["vscode"]["backups_created"], list):
            has_backups = True
            backup_count += len(clean_results["vscode"]["backups_created"])
        
        if clean_results["database"] and clean_results["database"].get("backups_created") and isinstance(clean_results["database"]["backups_created"], list):
            has_backups = True
            backup_count += len(clean_results["database"]["backups_created"])
            
        if has_backups:
            st.subheader("💾 备份信息")
            
            st.info(f"共创建了 {backup_count} 个备份文件")
            
            with st.expander("查看备份详情"):
                if clean_results["jetbrains"] and clean_results["jetbrains"].get("backups_created") and isinstance(clean_results["jetbrains"]["backups_created"], list):
                    st.write("JetBrains备份:")
                    for backup in clean_results["jetbrains"]["backups_created"]:
                        st.text(f"• {backup}")
                
                if clean_results["vscode"] and clean_results["vscode"].get("backups_created") and isinstance(clean_results["vscode"]["backups_created"], list):
                    st.write("VSCode备份:")
                    for backup in clean_results["vscode"]["backups_created"]:
                        st.text(f"• {backup}")
                
                if clean_results["database"] and clean_results["database"].get("backups_created") and isinstance(clean_results["database"]["backups_created"], list):
                    st.write("数据库备份:")
                    for backup in clean_results["database"]["backups_created"]:
                        st.text(f"• {backup}")

def main():
    """主函数"""
    # 设置页面配置
    st.set_page_config(
        page_title=f"{APP_NAME} v{VERSION}",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 自定义CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #424242;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .log-container {
        height: 300px;
        overflow-y: auto;
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 10px;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 标题
    st.markdown(f'<h1 class="main-header">{APP_NAME} v{VERSION}</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">🚀 解除AugmentCode设备限制，实现无限账户切换</p>', unsafe_allow_html=True)
    
    # 初始化后端
    if not st.session_state.backend_ready:
        init_backend()
    
    # 创建三列布局
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # 左侧列 - 选项
    with col1:
        st.subheader("⚙️ 清理选项")
        
        # IDE选项
        st.write("**IDE 选择**")
        if 'jetbrains' not in st.session_state:
            st.session_state.jetbrains = True
        if 'vscode' not in st.session_state:
            st.session_state.vscode = True
            
        st.checkbox("🔧 JetBrains IDEs", key="jetbrains", help="清理JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm等)")
        st.checkbox("📝 VSCode 系列", key="vscode", help="清理VSCode系列 (VSCode, Cursor, VSCodium等)")
        
        # 清理选项
        st.write("**清理选项**")
        if 'database' not in st.session_state:
            st.session_state.database = True
        if 'workspace' not in st.session_state:
            st.session_state.workspace = True
            
        st.checkbox("🗃️ 清理数据库记录", key="database", help="清理存储在SQLite数据库中的AugmentCode相关记录")
        st.checkbox("📁 清理工作区存储", key="workspace", help="清理VSCode工作区存储中的AugmentCode相关数据")
        
        # 安全选项
        st.write("**安全选项**")
        if 'backup' not in st.session_state:
            st.session_state.backup = True
        if 'lock' not in st.session_state:
            st.session_state.lock = True
            
        st.checkbox("💾 创建备份 (强烈推荐)", key="backup", help="在修改文件前创建备份，以便在出现问题时恢复")
        st.checkbox("🔒 锁定文件 (防止IDE重写)", key="lock", help="修改文件权限，防止IDE自动重写")
        
        # 操作按钮
        st.button("🔍 扫描系统", on_click=scan_system, disabled=not st.session_state.backend_ready)
        st.button("🚀 开始清理", on_click=start_cleaning, disabled=not st.session_state.backend_ready or st.session_state.is_cleaning)
        st.button("❓ 帮助", on_click=show_help)
        
        # 系统信息
        st.subheader("💻 系统信息")
        system_info = {
            "操作系统": os.name,
            "Python版本": sys.version.split()[0],
            "CPU使用率": f"{psutil.cpu_percent()}%",
            "内存使用率": f"{psutil.virtual_memory().percent}%"
        }
        
        for key, value in system_info.items():
            st.text(f"{key}: {value}")
    
    # 中间列 - 日志和结果
    with col2:
        st.subheader("📊 系统状态与日志")
        
        # 日志区域
        render_log_messages()
        
        # 扫描结果
        if st.session_state.scan_results:
            st.subheader("🔍 扫描结果")
            render_scan_results()
        
        # 清理结果
        if st.session_state.clean_results:
            render_clean_results()
    
    # 右侧列 - 帮助和信息
    with col3:
        st.subheader("📋 快速指南")
        st.info("""
        **使用步骤:**
        1. 点击"扫描系统"检测IDE安装情况
        2. 选择要清理的IDE和清理选项
        3. 点击"开始清理"执行清理操作
        4. 重启IDE并使用新账户登录
        
        **注意事项:**
        • 清理前请关闭所有IDE程序
        • 强烈建议保持"创建备份"选项开启
        """)
        
        # 显示进度
        if st.session_state.is_cleaning:
            st.subheader("⏳ 清理进度")
            st.progress(100)
            st.text("清理操作正在进行中...")
        
        # 显示备份位置
        if st.session_state.backend_ready and 'components' in st.session_state and st.session_state.components:
            backup_dir = st.session_state.components["backup_manager"].backup_dir
            st.subheader("💾 备份位置")
            st.code(backup_dir)
        
        # 显示关于信息
        st.subheader("ℹ️ 关于")
        st.markdown("""
        **AugmentCode Unlimited** 是一个开源工具，用于解除AugmentCode设备限制，实现无限账户切换。
        
        [GitHub仓库](https://github.com/wozhenbang2004/augetment-cursor-unlimited) | [报告问题](https://github.com/wozhenbang2004/augetment-cursor-unlimited/issues)
        
        版本: {0} | 更新日期: 2023-08-15
        """.format(VERSION))

if __name__ == "__main__":
    main()