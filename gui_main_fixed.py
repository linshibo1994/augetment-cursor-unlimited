#!/usr/bin/env python3
"""
Augment Cleaner Unified - 修复版GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
from pathlib import Path
import time
import traceback

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 全局变量用于存储组件
APP_NAME = "AugmentCode Unlimited"
VERSION = "1.0.0"

try:
    from config.settings import VERSION, APP_NAME
except ImportError:
    print("警告: 无法导入配置，使用默认值")

class AugmentCleanerGUI:
    """AugmentCode Unlimited GUI主类"""
    
    def __init__(self):
        print("初始化GUI...")
        self.root = tk.Tk()
        self.backend_ready = False
        
        # 先设置窗口和基本组件
        self.setup_window()
        self.setup_components()
        self.setup_layout()
        
        # 在后台初始化后端组件
        self.init_backend()
        
        self.is_cleaning = False
        print("GUI初始化完成")
        
    def setup_window(self):
        """设置主窗口"""
        print("设置主窗口...")
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 强制窗口显示在前台
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        # 居中显示
        self.center_window()
        
        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """居中显示窗口"""
        self.root.update_idletasks()
        width = 800
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_components(self):
        """设置GUI组件"""
        print("设置GUI组件...")
        
        # 主框架
        self.main_frame = ttk.Frame(self.root, padding="15")
        
        # 标题区域
        self.header_frame = ttk.Frame(self.main_frame)
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text=f"{APP_NAME} v{VERSION}",
            font=("Arial", 18, "bold")
        )
        
        self.subtitle_label = ttk.Label(
            self.header_frame,
            text="🚀 解除AugmentCode设备限制，实现无限账户切换",
            font=("Arial", 11)
        )
        
        # 状态显示区域
        self.status_frame = ttk.LabelFrame(self.main_frame, text="📊 系统状态与日志", padding="10")
        self.status_text = scrolledtext.ScrolledText(
            self.status_frame,
            height=15,
            width=70,
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg="#f8f9fa",
            fg="#212529"
        )
        
        # 选项框架
        self.options_frame = ttk.LabelFrame(self.main_frame, text="⚙️ 清理选项", padding="15")
        
        # 复选框变量
        self.jetbrains_var = tk.BooleanVar(value=True)
        self.vscode_var = tk.BooleanVar(value=True)
        self.backup_var = tk.BooleanVar(value=True)
        self.lock_var = tk.BooleanVar(value=True)
        self.database_var = tk.BooleanVar(value=True)
        self.workspace_var = tk.BooleanVar(value=True)
        
        # IDE选项组
        self.ide_frame = ttk.LabelFrame(self.options_frame, text="IDE 选择", padding="10")
        
        self.jetbrains_check = ttk.Checkbutton(
            self.ide_frame,
            text="🔧 JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm 等)",
            variable=self.jetbrains_var
        )
        
        self.vscode_check = ttk.Checkbutton(
            self.ide_frame,
            text="📝 VSCode 系列 (VSCode, Cursor, VSCodium 等)",
            variable=self.vscode_var
        )
        
        # 清理选项组
        self.clean_frame = ttk.LabelFrame(self.options_frame, text="清理选项", padding="10")
        
        self.database_check = ttk.Checkbutton(
            self.clean_frame,
            text="🗃️ 清理数据库记录",
            variable=self.database_var
        )
        
        self.workspace_check = ttk.Checkbutton(
            self.clean_frame,
            text="📁 清理工作区存储",
            variable=self.workspace_var
        )
        
        # 安全选项组
        self.safety_frame = ttk.LabelFrame(self.options_frame, text="安全选项", padding="10")
        
        self.backup_check = ttk.Checkbutton(
            self.safety_frame,
            text="💾 创建备份 (强烈推荐)",
            variable=self.backup_var
        )
        
        self.lock_check = ttk.Checkbutton(
            self.safety_frame,
            text="🔒 锁定文件 (防止IDE重写)",
            variable=self.lock_var
        )
        
        # 按钮框架
        self.button_frame = ttk.Frame(self.main_frame)
        
        # 按钮
        self.scan_button = ttk.Button(
            self.button_frame,
            text="🔍 扫描系统",
            command=self.scan_system,
            width=15
        )
        
        self.clean_button = ttk.Button(
            self.button_frame,
            text="🚀 开始清理",
            command=self.start_cleaning,
            width=15
        )
        
        self.help_button = ttk.Button(
            self.button_frame,
            text="❓ 帮助",
            command=self.show_help,
            width=15
        )
        
        # 进度条
        self.progress = ttk.Progressbar(
            self.main_frame,
            mode='indeterminate'
        )
        
        # 状态栏
        self.status_bar = ttk.Label(
            self.main_frame,
            text="正在初始化...",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding="5"
        )
        
    def setup_layout(self):
        """设置布局"""
        print("设置布局...")
        
        # 主框架
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题区域
        self.header_frame.pack(fill=tk.X, pady=(0, 15))
        self.title_label.pack()
        self.subtitle_label.pack(pady=(5, 0))
        
        # 状态区域
        self.status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # 选项区域
        self.options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # IDE选项
        self.ide_frame.pack(fill=tk.X, pady=(0, 10))
        self.jetbrains_check.pack(anchor=tk.W, pady=2)
        self.vscode_check.pack(anchor=tk.W, pady=2)
        
        # 清理选项
        self.clean_frame.pack(fill=tk.X, pady=(0, 10))
        self.database_check.pack(anchor=tk.W, pady=2)
        self.workspace_check.pack(anchor=tk.W, pady=2)
        
        # 安全选项
        self.safety_frame.pack(fill=tk.X, pady=(0, 10))
        self.backup_check.pack(anchor=tk.W, pady=2)
        self.lock_check.pack(anchor=tk.W, pady=2)
        
        # 按钮区域
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        self.scan_button.pack(side=tk.LEFT, padx=(0, 10))
        self.clean_button.pack(side=tk.LEFT, padx=(0, 10))
        self.help_button.pack(side=tk.RIGHT)
        
        # 进度条
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # 状态栏
        self.status_bar.pack(fill=tk.X)
        
        # 初始化消息
        self.log_message("🎉 AugmentCode Unlimited 已启动")
        self.log_message("💡 正在初始化后端组件...")
        
        # 强制刷新界面
        self.root.update()
        
    def init_backend(self):
        """初始化后端组件"""
        def init_thread():
            try:
                self.log_message("🔧 正在加载核心模块...")
                
                # 导入后端模块
                from utils.paths import PathManager
                from utils.backup import BackupManager
                from core.jetbrains_handler import JetBrainsHandler
                from core.vscode_handler import VSCodeHandler
                from core.db_cleaner import DatabaseCleaner
                
                self.log_message("✅ 核心模块加载成功")
                
                # 初始化组件
                self.log_message("🔧 正在初始化组件...")
                self.path_manager = PathManager()
                self.backup_manager = BackupManager()
                self.jetbrains_handler = JetBrainsHandler(self.path_manager, self.backup_manager)
                self.vscode_handler = VSCodeHandler(self.path_manager, self.backup_manager)
                self.database_cleaner = DatabaseCleaner(self.path_manager, self.backup_manager)
                
                self.backend_ready = True
                self.log_message("✅ 后端组件初始化完成")
                self.log_message("💡 点击 '扫描系统' 开始检测您的IDE安装情况")
                self.log_message("⚠️  建议在清理前关闭所有IDE程序")
                
                self.status_bar.config(text="就绪 - 可以开始使用")
                
            except Exception as e:
                error_msg = f"后端初始化失败: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                self.log_message("⚠️  部分功能可能不可用")
                self.status_bar.config(text="初始化失败 - 部分功能不可用")
                print(f"后端初始化错误: {e}")
                traceback.print_exc()
        
        # 在后台线程中初始化
        threading.Thread(target=init_thread, daemon=True).start()
        
    def log_message(self, message):
        """在状态区域显示消息"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def scan_system(self):
        """扫描系统"""
        if not self.backend_ready:
            messagebox.showwarning("警告", "后端组件尚未初始化完成，请稍候...")
            return
            
        self.log_message("🔍 开始扫描系统...")
        self.status_bar.config(text="正在扫描系统...")
        
        def scan_thread():
            try:
                # 扫描JetBrains
                self.log_message("🔧 扫描 JetBrains IDEs...")
                jetbrains_info = self.jetbrains_handler.verify_jetbrains_installation()
                if jetbrains_info['installed']:
                    self.log_message(f"✅ 发现 JetBrains IDEs")
                    self.log_message(f"   📁 配置目录: {jetbrains_info['config_dir']}")
                    self.log_message(f"   📄 ID文件: {len(jetbrains_info['existing_files'])}/{len(jetbrains_info['id_files'])}")
                else:
                    self.log_message("❌ 未发现 JetBrains IDEs")
                
                # 扫描VSCode
                self.log_message("📝 扫描 VSCode 系列...")
                vscode_info = self.vscode_handler.verify_vscode_installation()
                if vscode_info['installed']:
                    variants = ', '.join(vscode_info['variants_found'])
                    self.log_message(f"✅ 发现 VSCode 变体: {variants}")
                    self.log_message(f"   📁 存储目录: {vscode_info['total_directories']} 个")
                else:
                    self.log_message("❌ 未发现 VSCode 系列编辑器")
                
                # 扫描数据库
                self.log_message("🗃️ 扫描数据库...")
                db_info = self.database_cleaner.get_database_info()
                self.log_message(f"✅ 发现数据库: {db_info['total_databases']} 个")
                self.log_message(f"   📊 可访问: {db_info['accessible_databases']} 个")
                
                self.log_message("✅ 系统扫描完成！")
                self.status_bar.config(text="扫描完成")
                
            except Exception as e:
                self.log_message(f"❌ 扫描失败: {str(e)}")
                self.status_bar.config(text="扫描失败")
                print(f"扫描错误: {e}")
        
        threading.Thread(target=scan_thread, daemon=True).start()
        
    def start_cleaning(self):
        """开始清理"""
        if not self.backend_ready:
            messagebox.showwarning("警告", "后端组件尚未初始化完成，请稍候...")
            return
            
        if self.is_cleaning:
            messagebox.showwarning("警告", "清理正在进行中，请稍候...")
            return
            
        if not (self.jetbrains_var.get() or self.vscode_var.get()):
            messagebox.showwarning("警告", "请至少选择一个IDE清理选项！")
            return
            
        # 确认对话框
        result = messagebox.askyesno(
            "确认清理",
            "⚠️ 即将开始清理AugmentCode相关数据\n\n"
            "📋 清理内容:\n"
            f"• JetBrains IDEs: {'是' if self.jetbrains_var.get() else '否'}\n"
            f"• VSCode 系列: {'是' if self.vscode_var.get() else '否'}\n"
            f"• 数据库清理: {'是' if self.database_var.get() else '否'}\n"
            f"• 工作区清理: {'是' if self.workspace_var.get() else '否'}\n"
            f"• 创建备份: {'是' if self.backup_var.get() else '否'}\n\n"
            "🔔 建议在清理前关闭所有IDE\n\n"
            "是否继续？"
        )
        
        if not result:
            return
            
        self.is_cleaning = True
        self.progress.start()
        self.clean_button.config(state='disabled')
        self.status_bar.config(text="正在清理...")
        
        def clean_thread():
            try:
                self.log_message("🚀 开始清理操作...")
                
                overall_success = False
                
                # 清理JetBrains
                if self.jetbrains_var.get():
                    self.log_message("🔧 正在处理 JetBrains IDEs...")
                    result = self.jetbrains_handler.process_jetbrains_ides(
                        create_backups=self.backup_var.get(),
                        lock_files=self.lock_var.get()
                    )
                    
                    if result['success']:
                        self.log_message(f"✅ JetBrains 处理成功")
                        self.log_message(f"   📄 处理文件: {len(result['files_processed'])} 个")
                        if result['backups_created']:
                            self.log_message(f"   💾 创建备份: {len(result['backups_created'])} 个")
                        overall_success = True
                    else:
                        self.log_message("❌ JetBrains 处理失败")
                        for error in result['errors'][:3]:
                            self.log_message(f"   ❌ {error}")
                
                # 清理VSCode
                if self.vscode_var.get():
                    self.log_message("📝 正在处理 VSCode 系列...")
                    result = self.vscode_handler.process_vscode_installations(
                        create_backups=self.backup_var.get(),
                        lock_files=self.lock_var.get(),
                        clean_workspace=self.workspace_var.get()
                    )
                    
                    if result['success']:
                        self.log_message(f"✅ VSCode 处理成功")
                        self.log_message(f"   📁 处理目录: {len(result['directories_processed'])} 个")
                        if result['backups_created']:
                            self.log_message(f"   💾 创建备份: {len(result['backups_created'])} 个")
                        overall_success = True
                    else:
                        self.log_message("❌ VSCode 处理失败")
                        for error in result['errors'][:3]:
                            self.log_message(f"   ❌ {error}")
                
                # 清理数据库
                if self.database_var.get() and self.vscode_var.get():
                    self.log_message("🗃️ 正在清理数据库...")
                    result = self.database_cleaner.clean_all_databases(
                        create_backups=self.backup_var.get()
                    )
                    
                    if result['success']:
                        self.log_message(f"✅ 数据库清理成功")
                        self.log_message(f"   🗑️ 删除记录: {result['total_records_deleted']} 条")
                    else:
                        self.log_message("❌ 数据库清理失败")
                
                # 完成
                if overall_success:
                    self.log_message("🎉 清理操作完成！")
                    self.log_message("")
                    self.log_message("📝 下一步操作:")
                    self.log_message("   1️⃣ 重启您的IDE")
                    self.log_message("   2️⃣ 使用新的AugmentCode账户登录")
                    self.log_message("   3️⃣ 享受无限制的AI编程体验！")
                    
                    self.status_bar.config(text="清理完成")
                    
                    messagebox.showinfo(
                        "清理完成",
                        "🎉 AugmentCode数据清理完成！\n\n"
                        "📋 下一步:\n"
                        "1. 重启您的IDE\n"
                        "2. 使用新账户登录AugmentCode\n"
                        "3. 开始使用！\n\n"
                        f"💾 备份位置: {self.backup_manager.backup_dir if self.backup_var.get() else '未创建备份'}"
                    )
                else:
                    self.log_message("❌ 清理操作失败")
                    self.status_bar.config(text="清理失败")
                    messagebox.showerror("清理失败", "清理操作未能成功完成，请查看日志了解详情。")
                
            except Exception as e:
                self.log_message(f"❌ 清理过程中发生错误: {str(e)}")
                self.status_bar.config(text="清理出错")
                messagebox.showerror("错误", f"清理过程中发生错误:\n{str(e)}")
                print(f"清理错误: {e}")
                traceback.print_exc()
            
            finally:
                self.is_cleaning = False
                self.progress.stop()
                self.clean_button.config(state='normal')
        
        threading.Thread(target=clean_thread, daemon=True).start()
        
    def show_help(self):
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
        
        messagebox.showinfo("帮助", help_text)
        
    def on_closing(self):
        """窗口关闭事件"""
        if self.is_cleaning:
            result = messagebox.askyesno(
                "确认退出",
                "清理操作正在进行中，确定要退出吗？\n\n"
                "强制退出可能导致数据不一致。"
            )
            if not result:
                return
                
        self.root.destroy()
        
    def run(self):
        """运行GUI"""
        try:
            print("启动GUI主循环...")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_message("程序被用户中断")
        except Exception as e:
            print(f"GUI运行错误: {e}")
            messagebox.showerror("严重错误", f"程序运行时发生严重错误:\n{str(e)}")


def main():
    """主函数"""
    try:
        # 设置环境变量消除macOS警告
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        
        print("正在启动 AugmentCode Unlimited GUI...")
        
        # 创建并运行GUI
        app = AugmentCleanerGUI()
        app.run()
        
    except ImportError as e:
        error_msg = f"模块导入失败: {e}\n\n请确保已安装所有依赖:\npip install -r requirements.txt"
        print(error_msg)
        try:
            messagebox.showerror("导入错误", error_msg)
        except:
            pass
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"程序启动失败: {e}"
        print(error_msg)
        try:
            messagebox.showerror("启动错误", error_msg)
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()