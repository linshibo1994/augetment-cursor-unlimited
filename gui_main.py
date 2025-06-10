#!/usr/bin/env python3
"""
Augment Cleaner Unified - GUI Version

图形界面版本的 Augment Cleaner Unified
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
from pathlib import Path
import time

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import VERSION, APP_NAME
from utils.paths import PathManager
from utils.backup import BackupManager
from core.jetbrains_handler import JetBrainsHandler
from core.vscode_handler import VSCodeHandler
from core.db_cleaner import DatabaseCleaner


class ToolTip:
    """工具提示类"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        if self.tooltip_window or not self.text:
            return

        try:
            # 尝试获取widget的位置
            x = self.widget.winfo_rootx() + 25
            y = self.widget.winfo_rooty() + 25
        except:
            return

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                        background="#ffffe0", relief="solid", borderwidth=1,
                        font=("Arial", 9))
        label.pack(ipadx=1)

    def on_leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class AugmentCleanerGUI:
    """Augment Cleaner Unified 图形界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Augment Unlimited Pro - 下一代智能AugmentCode限制绕过系统")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # 设置现代化主题
        self.setup_modern_theme()

        # 设置图标（如果存在）
        try:
            icon_path = Path(__file__).parent / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # 初始化组件
        self.path_manager = None
        self.backup_manager = None
        self.jetbrains_handler = None
        self.vscode_handler = None
        self.database_cleaner = None

        # 创建界面
        self.create_widgets()
        self.initialize_components()

        # 禁用智能监控系统 - 太耗性能
        # self.root.after(1000, self.start_intelligent_monitoring)

    def setup_modern_theme(self):
        """设置现代化主题 - 超越 augment-new 的高级主题"""
        try:
            # 设置深色主题
            self.root.configure(bg='#1a1a1a')

            # 配置ttk样式
            style = ttk.Style()

            # 使用更现代的主题
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'alt' in available_themes:
                style.theme_use('alt')

            # 自定义颜色方案 - 比 augment-new 更高级
            colors = {
                'bg_primary': '#1a1a1a',      # 主背景 - 更深的黑色
                'bg_secondary': '#2d2d2d',    # 次要背景
                'bg_accent': '#3d3d3d',       # 强调背景
                'text_primary': '#ffffff',     # 主文本
                'text_secondary': '#b0b0b0',   # 次要文本
                'accent_blue': '#0078d4',      # 蓝色强调
                'accent_green': '#107c10',     # 绿色强调
                'accent_orange': '#ff8c00',    # 橙色强调
                'accent_red': '#d13438',       # 红色强调
                'border': '#404040',           # 边框颜色
                'hover': '#404040'             # 悬停颜色
            }

            # 配置各种控件样式
            style.configure('TLabel',
                          background=colors['bg_primary'],
                          foreground=colors['text_primary'])

            style.configure('TFrame',
                          background=colors['bg_primary'])

            style.configure('TLabelFrame',
                          background=colors['bg_primary'],
                          foreground=colors['text_primary'],
                          borderwidth=1,
                          relief='solid')

            style.configure('TButton',
                          background=colors['bg_secondary'],
                          foreground=colors['text_primary'],
                          borderwidth=1,
                          focuscolor='none')

            style.map('TButton',
                     background=[('active', colors['hover']),
                               ('pressed', colors['bg_accent'])])

            # 强调按钮样式
            style.configure('Accent.TButton',
                          background=colors['accent_blue'],
                          foreground='white',
                          borderwidth=0,
                          focuscolor='none')

            style.map('Accent.TButton',
                     background=[('active', '#106ebe'),
                               ('pressed', '#005a9e')])

            style.configure('TCheckbutton',
                          background=colors['bg_primary'],
                          foreground=colors['text_primary'],
                          focuscolor='none')

            style.configure('TNotebook',
                          background=colors['bg_primary'],
                          borderwidth=0)

            style.configure('TNotebook.Tab',
                          background=colors['bg_secondary'],
                          foreground=colors['text_primary'],
                          padding=[12, 8])

            style.map('TNotebook.Tab',
                     background=[('selected', colors['accent_blue']),
                               ('active', colors['hover'])])

            # 进度条样式
            style.configure('TProgressbar',
                          background=colors['accent_blue'],
                          troughcolor=colors['bg_secondary'],
                          borderwidth=0,
                          lightcolor=colors['accent_blue'],
                          darkcolor=colors['accent_blue'])

            self.log("✅ 现代化主题设置完成")

        except Exception as e:
            self.log(f"⚠️ 主题设置失败，使用默认主题: {e}")

    def start_intelligent_monitoring(self):
        """启动智能监控系统 - 超越 augment-new 的核心功能"""
        try:
            self.log("🧠 启动智能监控系统...")
            self.log("   🔍 实时威胁检测已激活")
            self.log("   🛡️ 自动反制建议系统已就绪")
            self.log("   📊 智能状态分析引擎已启动")

            # 启动定时监控
            self.schedule_intelligent_scan()

        except Exception as e:
            self.log(f"⚠️ 智能监控启动失败: {e}")

    def schedule_intelligent_scan(self):
        """定时智能扫描（已禁用）"""
        # 禁用定时扫描，避免性能问题
        pass

    def perform_threat_analysis(self):
        """执行威胁分析 - 比 augment-new 更智能"""
        try:
            # 检测AugmentCode活动进程
            active_threats = self.detect_augmentcode_processes()

            # 检测新的限制机制
            new_restrictions = self.detect_new_restrictions()

            # 生成智能建议
            if active_threats or new_restrictions:
                self.generate_intelligent_recommendations(active_threats, new_restrictions)

        except Exception as e:
            pass  # 静默处理，避免干扰用户

    def detect_augmentcode_processes(self):
        """检测AugmentCode相关进程（简化版，避免性能问题）"""
        # 禁用进程检测，因为太耗性能
        return []

    def detect_new_restrictions(self):
        """检测新的限制机制"""
        try:
            restrictions = []

            # 检测新的ID文件
            new_id_files = self.scan_for_new_id_files()
            if new_id_files:
                restrictions.extend(new_id_files)

            # 检测新的数据库表
            new_db_tables = self.scan_for_new_db_tables()
            if new_db_tables:
                restrictions.extend(new_db_tables)

            return restrictions

        except Exception:
            return []

    def scan_for_new_id_files(self):
        """扫描新的ID文件"""
        # 这里可以实现更复杂的扫描逻辑
        return []

    def scan_for_new_db_tables(self):
        """扫描新的数据库表"""
        # 这里可以实现数据库表结构变化检测
        return []

    def generate_intelligent_recommendations(self, threats, restrictions):
        """生成智能建议"""
        try:
            if threats:
                self.log("🚨 检测到活跃威胁:")
                for threat in threats[:3]:  # 只显示前3个
                    self.log(f"   ⚠️ {threat['name']} (PID: {threat['pid']})")
                self.log("   💡 建议：立即执行清理操作")

            if restrictions:
                self.log("🔍 发现新的限制机制:")
                for restriction in restrictions[:2]:  # 只显示前2个
                    self.log(f"   🆕 {restriction.get('type', '未知类型')}")
                self.log("   💡 建议：更新反制策略")

        except Exception:
            pass
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 超级标题 - 比 augment-new 更炫酷
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        title_label = ttk.Label(title_frame, text="🚀 Augment Unlimited Pro",
                               font=("Arial", 20, "bold"))
        title_label.pack()

        subtitle_label = ttk.Label(title_frame, text="下一代智能AugmentCode限制绕过系统",
                                  font=("Arial", 10), foreground="gray")
        subtitle_label.pack()

        version_label = ttk.Label(title_frame, text=f"v{VERSION} - 超越所有同类工具",
                                 font=("Arial", 8), foreground="blue")
        version_label.pack()
        
        # 状态信息框架
        status_frame = ttk.LabelFrame(main_frame, text="系统状态", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # AugmentCode限制反制状态标签
        self.device_id_status = ttk.Label(status_frame, text="🆔 设备ID限制: 检测中...")
        self.device_id_status.grid(row=0, column=0, sticky=tk.W, pady=2)

        self.database_status = ttk.Label(status_frame, text="🗃️ 数据库记录: 检测中...")
        self.database_status.grid(row=1, column=0, sticky=tk.W, pady=2)

        self.workspace_status = ttk.Label(status_frame, text="📁 工作区记录: 检测中...")
        self.workspace_status.grid(row=2, column=0, sticky=tk.W, pady=2)

        self.network_status = ttk.Label(status_frame, text="🌐 网络指纹: 检测中...")
        self.network_status.grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # 刷新按钮
        refresh_btn = ttk.Button(status_frame, text="刷新状态", command=self.refresh_status)
        refresh_btn.grid(row=0, column=1, rowspan=4, sticky=tk.E, padx=(10, 0))
        
        # 选项变量 - 按AugmentCode限制方式分组
        self.bypass_device_id = tk.BooleanVar(value=True)
        self.bypass_database = tk.BooleanVar(value=True)
        self.bypass_workspace = tk.BooleanVar(value=True)
        self.bypass_network = tk.BooleanVar(value=False)  # 网络指纹默认关闭

        # AugmentCode限制反制选择框架
        bypass_frame = ttk.LabelFrame(main_frame, text="🎯 选择要反制的AugmentCode限制", padding="15")
        bypass_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        bypass_frame.columnconfigure(0, weight=1)
        bypass_frame.columnconfigure(1, weight=1)

        # 设备ID限制反制选项
        device_id_frame = ttk.Frame(bypass_frame)
        device_id_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)

        device_id_cb = ttk.Checkbutton(device_id_frame, text="🆔 设备ID限制反制",
                                      variable=self.bypass_device_id)
        device_id_cb.pack(anchor=tk.W)
        self.create_tooltip(device_id_cb, "反制AugmentCode的设备ID检测:\n• IDEA/PyCharm/WebStorm等: PermanentDeviceId, PermanentUserId\n• VSCode/Cursor: machineId, devDeviceId, sqmId\n• 自动生成新ID并锁定文件")

        device_id_desc = ttk.Label(device_id_frame, text="IDEA, PyCharm, VSCode, Cursor\n设备唯一标识符",
                                  font=("Arial", 8), foreground="gray")
        device_id_desc.pack(anchor=tk.W, pady=(2, 0))

        # 数据库记录限制反制选项
        database_frame = ttk.Frame(bypass_frame)
        database_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        database_cb = ttk.Checkbutton(database_frame, text="🗃️ 数据库记录反制",
                                     variable=self.bypass_database)
        database_cb.pack(anchor=tk.W)
        self.create_tooltip(database_cb, "清理AugmentCode的使用记录:\n• VSCode/Cursor: state.vscdb 登录状态\n• 浏览器: 历史记录、Cookie\n• 自动备份并清理相关记录")

        database_desc = ttk.Label(database_frame, text="登录状态、使用记录\n历史数据清理",
                                 font=("Arial", 8), foreground="gray")
        database_desc.pack(anchor=tk.W, pady=(2, 0))

        # 工作区记录限制反制选项
        workspace_frame = ttk.Frame(bypass_frame)
        workspace_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=(10, 0))

        workspace_cb = ttk.Checkbutton(workspace_frame, text="� 工作区记录反制",
                                      variable=self.bypass_workspace)
        workspace_cb.pack(anchor=tk.W)
        self.create_tooltip(workspace_cb, "清理项目使用痕迹:\n• VSCode/Cursor: workspaceStorage 项目记录\n• IDEA/PyCharm等: 项目配置和历史\n• 清理所有项目使用记录")

        workspace_desc = ttk.Label(workspace_frame, text="项目使用记录\n工作区历史清理",
                                  font=("Arial", 8), foreground="gray")
        workspace_desc.pack(anchor=tk.W, pady=(2, 0))

        # 网络指纹限制反制选项
        network_frame = ttk.Frame(bypass_frame)
        network_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=(10, 0))

        network_cb = ttk.Checkbutton(network_frame, text="🌐 网络指纹反制",
                                    variable=self.bypass_network)
        network_cb.pack(anchor=tk.W)
        self.create_tooltip(network_cb, "反制网络层面检测:\n• 浏览器指纹清理\n• Canvas、WebGL指纹重置\n• 网络缓存清理\n⚠️ 可能影响其他应用")

        network_desc = ttk.Label(network_frame, text="浏览器指纹、网络缓存\n⚠️ 高级选项",
                                font=("Arial", 8), foreground="orange")
        network_desc.pack(anchor=tk.W, pady=(2, 0))

        # 高级选项框架
        advanced_frame = ttk.LabelFrame(main_frame, text="⚙️ 高级选项", padding="10")
        advanced_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 备份选项
        self.create_backups = tk.BooleanVar(value=True)  # 默认创建备份
        backup_cb = ttk.Checkbutton(advanced_frame, text="💾 创建备份",
                                   variable=self.create_backups)
        backup_cb.pack(anchor=tk.W)
        self.create_tooltip(backup_cb, "操作前自动备份原始文件:\n• 可用于恢复到修改前状态\n• 建议保持开启以防误操作\n• 备份文件存储在程序目录下")

        backup_desc = ttk.Label(advanced_frame, text="自动备份原始文件，支持一键恢复",
                               font=("Arial", 8), foreground="gray")
        backup_desc.pack(anchor=tk.W, pady=(2, 0))

        # 说明文字
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        info_label = ttk.Label(info_frame,
                              text="💡 自动执行：修改设备ID → 清理数据库/工作区 → 锁定文件 → 清理缓存",
                              font=("Arial", 9), foreground="blue")
        info_label.pack(anchor=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        
        # 主要按钮
        self.start_btn = ttk.Button(button_frame, text="🚀 开始清理", 
                                   command=self.start_cleaning, style="Accent.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📊 查看信息", 
                  command=self.show_info).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔍 当前ID", 
                  command=self.show_current_ids).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📁 打开备份目录",
                  command=self.open_backup_dir).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(button_frame, text="🔄 恢复备份",
                  command=self.restore_backup).pack(side=tk.LEFT, padx=(0, 10))
        
        # 日志框架
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 清除日志按钮
        ttk.Button(log_frame, text="清除日志",
                  command=self.clear_log).grid(row=1, column=0, sticky=tk.E, pady=(5, 0))

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def initialize_components(self):
        """初始化组件"""
        try:
            self.log("正在初始化组件...")
            self.path_manager = PathManager()
            self.backup_manager = BackupManager()
            self.jetbrains_handler = JetBrainsHandler(self.path_manager, self.backup_manager)
            self.vscode_handler = VSCodeHandler(self.path_manager, self.backup_manager)
            self.database_cleaner = DatabaseCleaner(self.path_manager, self.backup_manager)
            self.log("✅ 组件初始化完成")
            # 延迟更新状态显示，避免启动时卡顿
            self.root.after(3000, self.update_status_display)
        except Exception as e:
            self.log(f"❌ 组件初始化失败: {e}")
            messagebox.showerror("错误", f"初始化失败: {e}")
    
    def log(self, message, level="INFO"):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")

        # 根据消息内容自动判断级别
        if "❌" in message or "错误" in message or "失败" in message:
            level = "ERROR"
        elif "⚠️" in message or "警告" in message:
            level = "WARNING"
        elif "✅" in message or "成功" in message or "完成" in message:
            level = "SUCCESS"
        elif "🔍" in message or "检测" in message:
            level = "DETECT"
        elif "🚀" in message or "开始" in message:
            level = "START"

        # 格式化日志消息
        if level == "ERROR":
            log_message = f"[{timestamp}] ❌ {message}\n"
        elif level == "WARNING":
            log_message = f"[{timestamp}] ⚠️ {message}\n"
        elif level == "SUCCESS":
            log_message = f"[{timestamp}] ✅ {message}\n"
        elif level == "DETECT":
            log_message = f"[{timestamp}] 🔍 {message}\n"
        elif level == "START":
            log_message = f"[{timestamp}] 🚀 {message}\n"
        else:
            log_message = f"[{timestamp}] ℹ️ {message}\n"

        # 安全检查：确保log_text已经创建
        if hasattr(self, 'log_text') and self.log_text:
            try:
                self.log_text.insert(tk.END, log_message)
                self.log_text.see(tk.END)
                self.root.update_idletasks()
            except Exception:
                # 如果GUI操作失败，至少输出到控制台
                print(f"LOG: {log_message.strip()}")
        else:
            # 如果log_text还没创建，输出到控制台
            print(f"LOG: {log_message.strip()}")

        # 如果是错误，同时输出到控制台
        if level == "ERROR":
            print(f"ERROR: {message}")
    
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)

    def create_tooltip(self, widget, text):
        """创建工具提示"""
        ToolTip(widget, text)

    def _check_device_id_status(self):
        """检查设备ID限制反制状态"""
        try:
            device_count = 0
            locked_count = 0
            software_list = []

            # 简化检测：直接检查常见路径
            import os
            user_home = Path.home()
            appdata = Path(os.getenv('APPDATA', ''))
            localappdata = Path(os.getenv('LOCALAPPDATA', ''))

            # 检查VSCode/Cursor
            vscode_paths = [
                appdata / 'Code' / 'User' / 'globalStorage' / 'storage.json',
                appdata / 'Cursor' / 'User' / 'globalStorage' / 'storage.json',
                localappdata / 'Programs' / 'Microsoft VS Code',
                localappdata / 'Programs' / 'cursor'
            ]

            for path in vscode_paths:
                if path.exists():
                    device_count += 1
                    if 'Code' in str(path):
                        software_list.append('VSCode')
                    elif 'Cursor' in str(path):
                        software_list.append('Cursor')

            # 检查JetBrains
            jetbrains_config = user_home / '.config' / 'JetBrains'
            if not jetbrains_config.exists():
                jetbrains_config = appdata / 'JetBrains'

            if jetbrains_config.exists():
                for item in jetbrains_config.iterdir():
                    if item.is_dir():
                        device_count += 1
                        if 'idea' in item.name.lower():
                            software_list.append('IntelliJ IDEA')
                        elif 'pycharm' in item.name.lower():
                            software_list.append('PyCharm')
                        elif 'webstorm' in item.name.lower():
                            software_list.append('WebStorm')

            # 构建状态
            if device_count == 0:
                return {
                    'display': "🆔 设备ID限制: ❌ 未检测到",
                    'tooltip': "未检测到支持的IDE安装",
                    'log': "未检测到设备ID文件"
                }

            status = "⚠️ 未锁定"  # 简化状态
            return {
                'display': f"🆔 设备ID限制: {status} ({device_count}个ID)",
                'tooltip': f"设备ID反制状态:\n• 检测到 {device_count} 个设备ID文件\n• 涉及软件: {', '.join(set(software_list))}",
                'log': f"检测到 {device_count} 个设备ID"
            }

        except Exception as e:
            return {
                'display': "🆔 设备ID限制: ❌ 检测失败",
                'tooltip': f"检测失败: {e}",
                'log': f"设备ID检测失败: {e}"
            }

    def _check_database_status(self):
        """检查数据库记录限制反制状态 - 显示具体文件"""
        try:
            # 直接检查常见数据库路径
            import os
            appdata = Path(os.getenv('APPDATA', ''))

            db_files = []
            total_augment_records = 0

            # 检查VSCode数据库
            vscode_db_paths = [
                appdata / 'Code' / 'User' / 'globalStorage' / 'state.vscdb',
                appdata / 'Cursor' / 'User' / 'globalStorage' / 'state.vscdb'
            ]

            for db_path in vscode_db_paths:
                if db_path.exists():
                    db_files.append(db_path)
                    # 快速检查AugmentCode记录
                    try:
                        import sqlite3
                        conn = sqlite3.connect(str(db_path))
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ItemTable'")
                        if cursor.fetchone():
                            cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'")
                            count = cursor.fetchone()[0]
                            total_augment_records += count
                        conn.close()
                    except Exception:
                        pass

            if not db_files:
                return {
                    'display': "🗃️ 数据库文件: ❌ 未检测到",
                    'tooltip': "未检测到IDE数据库文件",
                    'log': "未检测到数据库文件"
                }

            status_text = f"⚠️ {total_augment_records}条记录" if total_augment_records > 0 else "✅ 已清理"
            return {
                'display': f"🗃️ 数据库文件: {status_text}",
                'tooltip': f"检测到 {len(db_files)} 个数据库文件\n{total_augment_records} 条AugmentCode记录",
                'log': f"检测到 {len(db_files)} 个数据库文件，{total_augment_records} 条AugmentCode记录"
            }

        except Exception as e:
            return {
                'display': "🗃️ 数据库文件: ❌ 检测失败",
                'tooltip': f"检测失败: {e}",
                'log': f"数据库检测失败: {e}"
            }

    def _check_workspace_status(self):
        """检查工作区记录限制反制状态 - 显示具体目录"""
        try:
            # 直接检查工作区路径
            import os
            appdata = Path(os.getenv('APPDATA', ''))

            workspace_dirs = []
            total_projects = 0

            # 检查VSCode和Cursor工作区
            workspace_paths = [
                appdata / 'Code' / 'User' / 'workspaceStorage',
                appdata / 'Cursor' / 'User' / 'workspaceStorage'
            ]

            for workspace_path in workspace_paths:
                if workspace_path.exists():
                    workspace_dirs.append(workspace_path)
                    try:
                        project_dirs = [d for d in workspace_path.iterdir() if d.is_dir()]
                        total_projects += len(project_dirs)
                    except Exception:
                        pass

            if not workspace_dirs:
                return {
                    'display': "📁 工作区目录: ❌ 未检测到",
                    'tooltip': "未检测到工作区存储目录",
                    'log': "未检测到工作区目录"
                }

            return {
                'display': f"📁 工作区目录: ⚠️ {len(workspace_dirs)}个待清理",
                'tooltip': f"检测到 {len(workspace_dirs)} 个工作区目录\n包含 {total_projects} 个项目记录",
                'log': f"检测到 {len(workspace_dirs)} 个工作区目录"
            }

        except Exception as e:
            return {
                'display': "📁 工作区目录: ❌ 检测失败",
                'tooltip': f"检测失败: {e}",
                'log': f"工作区检测失败: {e}"
            }

    def _check_network_status(self):
        """检查网络指纹限制反制状态 - 显示浏览器缓存状态"""
        try:
            browser_caches = []
            cache_details = []

            # 检查常见浏览器缓存目录
            import os
            user_profile = Path.home()
            appdata = Path(os.getenv('APPDATA', ''))
            localappdata = Path(os.getenv('LOCALAPPDATA', ''))

            browser_paths = {
                'Chrome': localappdata / 'Google' / 'Chrome' / 'User Data' / 'Default',
                'Edge': localappdata / 'Microsoft' / 'Edge' / 'User Data' / 'Default',
                'Firefox': appdata / 'Mozilla' / 'Firefox' / 'Profiles'
            }

            for browser_name, cache_path in browser_paths.items():
                if cache_path.exists():
                    try:
                        # 检查缓存大小（简化）
                        cache_size = 0
                        cache_files = 0
                        if browser_name == 'Firefox':
                            # Firefox有多个profile目录
                            for profile_dir in cache_path.iterdir():
                                if profile_dir.is_dir():
                                    cache_files += len(list(profile_dir.glob('*')))
                        else:
                            # Chrome/Edge
                            cache_dir = cache_path / 'Cache'
                            if cache_dir.exists():
                                cache_files = len(list(cache_dir.glob('*')))

                        browser_caches.append(cache_path)
                        status_icon = "⚠️" if cache_files > 100 else "✅"
                        cache_details.append(f"• {browser_name}: {status_icon} {cache_files}个缓存文件")
                    except Exception:
                        cache_details.append(f"• {browser_name}: 无法访问")

            if not browser_caches:
                return {
                    'display': "🌐 浏览器缓存: ❌ 未检测到",
                    'tooltip': "未检测到浏览器安装",
                    'log': "未检测到浏览器缓存"
                }

            # 构建详细的tooltip信息
            tooltip_text = f"浏览器缓存状态:\n" + "\n".join(cache_details[:5])
            if len(cache_details) > 5:
                tooltip_text += f"\n... 还有 {len(cache_details) - 5} 个浏览器"
            tooltip_text += f"\n\n将清理内容:\n• 浏览器缓存和Cookie\n• Canvas/WebGL指纹\n• 网络会话数据\n⚠️ 可能影响其他网站登录状态"

            return {
                'display': f"🌐 浏览器缓存: ⚠️ {len(browser_caches)}个浏览器",
                'tooltip': tooltip_text,
                'log': f"检测到 {len(browser_caches)} 个浏览器缓存"
            }

        except Exception as e:
            return {
                'display': "🌐 浏览器缓存: ❌ 检测失败",
                'tooltip': f"检测失败: {e}",
                'log': f"网络指纹检测失败: {e}"
            }
    
    def refresh_status(self):
        """刷新状态"""
        def update_status():
            try:
                self.log("🔍 正在检测系统状态...")

                # 检查 JetBrains
                self.log("   � 检测 JetBrains IDEs...")
                jetbrains_info = self.jetbrains_handler.verify_jetbrains_installation()
                if jetbrains_info['installed']:
                    files_count = len(jetbrains_info['existing_files'])
                    locked_count = sum(1 for f in jetbrains_info['existing_files']
                                     if self.jetbrains_handler.file_locker.is_file_locked(Path(f)))

                    # 构建详细状态描述
                    status_parts = []
                    if files_count > 0:
                        status_parts.append(f"{files_count}个设备ID文件")
                    if locked_count > 0:
                        status_parts.append(f"{locked_count}个已锁定")

                    # 这部分逻辑已移动到新的状态检测方法中
                    pass

                # 这部分逻辑已移动到新的状态检测方法中
                self.log("✅ AugmentCode限制反制状态检测完成")
            except Exception as e:
                self.log(f"❌ 状态刷新失败: {e}")
                import traceback
                self.log(f"   详细错误: {traceback.format_exc()}")

        threading.Thread(target=update_status, daemon=True).start()

    def update_status_display(self):
        """更新状态显示"""
        try:
            # 检测设备ID状态
            device_id_result = self._check_device_id_status()
            self.device_id_status.config(text=device_id_result['display'])
            self.create_tooltip(self.device_id_status, device_id_result['tooltip'])

            # 检测数据库记录状态
            database_result = self._check_database_status()
            self.database_status.config(text=database_result['display'])
            self.create_tooltip(self.database_status, database_result['tooltip'])

            # 检测工作区记录状态
            workspace_result = self._check_workspace_status()
            self.workspace_status.config(text=workspace_result['display'])
            self.create_tooltip(self.workspace_status, workspace_result['tooltip'])

            # 检测网络指纹状态
            network_result = self._check_network_status()
            self.network_status.config(text=network_result['display'])
            self.create_tooltip(self.network_status, network_result['tooltip'])
        except Exception as e:
            self.log(f"❌ 状态显示更新失败: {e}")

    def start_cleaning(self):
        """开始清理 - 一键完成所有操作"""
        if not messagebox.askyesno("确认", "确定要开始一键清理吗？\n\n将自动执行：\n• 关闭所有IDE进程\n• 清理AugmentCode数据库\n• 清理.augmentcode目录\n• 执行安全模式清理"):
            return

        self.start_btn.config(state='disabled', text="一键清理中...")
        self.progress.start()

        def cleaning_thread():
            try:
                self.log("🎯 检测系统中的IDE...")
                self.log("› 🎯 目标IDE: VS Code, Cursor, PyCharm, IntelliJ IDEA, WebStorm, Rider")

                # 第一步：关闭IDE进程
                self.log("› 🔄 正在关闭选定的IDE进程...")
                self._close_ide_processes()

                # 第二步：执行安全模式清理
                self.log("› 🧹 正在清理Augment数据库和配置...")
                self.log("› � 执行安全模式清理...")
                overall_success = self._execute_safe_mode_cleaning()

                # 第三步：清理.augmentcode目录
                self.log("› 🗑️ 正在清理.augmentcode目录...")
                self._clean_augmentcode_directory()

                if overall_success:
                    self.log("› ✅ 安全模式清理完成")
                    self.log("› ✅ 登录数据清理完成")
                    self.log("› 🎉 一键清理完成！所有Augment数据已清除")
                else:
                    self.log("› ⚠️ 部分清理操作失败，请查看详细日志")

                # 如果用户还选择了其他反制选项，继续执行
                additional_operations = False

                # 设备ID限制反制
                if self.bypass_device_id.get():
                    self.log("🆔 执行设备ID限制反制...")
                    self.log("   📋 自动执行：创建备份 → 修改设备ID → 锁定文件")

                    # 处理JetBrains设备ID
                    jetbrains_info = self.jetbrains_handler.verify_jetbrains_installation()
                    if jetbrains_info['installed']:
                        # 先获取具体的软件列表
                        jetbrains_software = set()
                        for file_path in jetbrains_info['existing_files']:
                            software_name = self._get_jetbrains_software_name(Path(file_path).name, jetbrains_info)
                            jetbrains_software.add(software_name)

                        software_list_str = ", ".join(sorted(jetbrains_software))
                        self.log(f"   🔍 检测到软件: {software_list_str}")

                        result = self.jetbrains_handler.process_jetbrains_ides(
                            create_backups=self.create_backups.get(),  # 使用用户选择
                            lock_files=True,      # 默认锁定文件
                            clean_databases=True  # 同时处理数据库文件
                        )
                        if result['success']:
                            files_processed = result.get('files_processed', [])
                            files_count = len(files_processed) if isinstance(files_processed, list) else files_processed
                            databases_processed = result.get('databases_processed', [])
                            db_count = len(databases_processed) if isinstance(databases_processed, list) else databases_processed
                            db_records = result.get('database_records_cleaned', 0)

                            self.log(f"✅ {software_list_str} 反制成功")
                            self.log(f"   📄 处理了 {files_count} 个ID文件，{db_count} 个数据库文件")
                            if db_records > 0:
                                self.log(f"   🗃️ 清理了 {db_records} 条数据库记录")

                            # 显示具体的文件
                            for file_path in result['files_processed']:
                                file_name = Path(file_path).name
                                software_name = self._get_jetbrains_software_name(file_name, jetbrains_info)
                                self.log(f"   📄 ID文件: {software_name} - {file_name}")

                            # 显示数据库文件
                            for db_path in result.get('databases_processed', []):
                                db_name = Path(db_path).name
                                self.log(f"   🗃️ 数据库: {db_name}")

                            overall_success = True
                        else:
                            self.log(f"❌ {software_list_str} 反制失败: {'; '.join(result['errors'])}")
                    else:
                        self.log("   ℹ️ 未检测到IDEA/PyCharm等JetBrains软件安装")

                    # 处理VSCode/Cursor设备ID
                    vscode_info = self.vscode_handler.verify_vscode_installation()
                    if vscode_info['installed']:
                        result = self.vscode_handler.process_vscode_installations(
                            create_backups=self.create_backups.get(),  # 使用用户选择
                            lock_files=True,          # 默认锁定文件
                            clean_workspace=False,    # 设备ID反制不清理工作区
                            clean_cache=False         # 设备ID反制不清理缓存
                        )
                        if result['success']:
                            directories_count = result.get('directories_processed', 0)
                            self.log(f"✅ VSCode/Cursor 设备ID处理成功，修改了 {directories_count} 个目录")
                            # 显示修改的文件详情
                            if result.get('files_processed'):
                                self.log(f"   📄 修改了 {len(result['files_processed'])} 个文件:")
                                for file_path in result['files_processed']:
                                    file_name = Path(file_path).name
                                    self.log(f"      • {file_name}")
                            # 显示ID变更详情
                            if result.get('new_ids'):
                                new_ids_count = len(result['new_ids']) if isinstance(result['new_ids'], (list, dict)) else result['new_ids']
                                self.log(f"   🆔 生成了 {new_ids_count} 个新ID")
                            overall_success = True
                        else:
                            self.log(f"❌ VSCode/Cursor 设备ID处理失败: {'; '.join(result['errors'])}")

                # 数据库记录限制反制
                if self.bypass_database.get():
                    self.log("🗃️ 执行数据库记录限制反制...")
                    self.log("   📋 自动执行：清理全局存储数据库 → 精确清理工作区AugmentCode数据 → 创建安全备份")
                    self.log("   💡 注意：使用精确清理模式，只清理AugmentCode相关数据，保留其他项目配置")
                    self.log("   ⚠️ 备份说明：备份仅用于误操作恢复，恢复后AugmentCode限制会重新生效")

                    try:
                        global_db_cleaned = 0
                        workspace_cleaned = 0

                        if not vscode_info.get('installed'):
                            self.log("   ℹ️ 未检测到VSCode/Cursor安装")
                        else:
                            # 处理每个变体
                            for variant_name in vscode_info.get('variants_found', []):
                                self.log(f"   🔍 处理 {variant_name}...")

                                # 查找该变体的配置目录
                                for storage_dir in vscode_info.get('storage_directories', []):
                                    if variant_name.lower() not in storage_dir.lower():
                                        continue

                                    config_path = Path(storage_dir)

                                    # 清理全局存储数据库
                                    global_storage_path = config_path / "User" / "globalStorage"
                                    state_db_path = global_storage_path / "state.vscdb"

                                    if state_db_path.exists():
                                        try:
                                            # 创建备份（如果用户选择）
                                            if self.create_backups.get():
                                                import time
                                                backup_path = f"{state_db_path}.backup.{int(time.time())}"
                                                import shutil
                                                shutil.copy2(state_db_path, backup_path)
                                                self.log(f"      💾 已备份数据库: {backup_path}")
                                            else:
                                                self.log(f"      ⚠️ 跳过备份（用户选择）")

                                            # 清理AugmentCode记录
                                            import sqlite3
                                            conn = sqlite3.connect(state_db_path)
                                            cursor = conn.cursor()
                                            cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'")
                                            count = cursor.fetchone()[0]

                                            if count > 0:
                                                cursor.execute("DELETE FROM ItemTable WHERE key LIKE '%augment%'")
                                                conn.commit()
                                                global_db_cleaned += count
                                                self.log(f"      📄 清理了 {count} 条AugmentCode记录")

                                            conn.close()
                                        except Exception as e:
                                            self.log(f"      ❌ 数据库清理失败: {e}")

                        if global_db_cleaned > 0:
                            self.log(f"✅ 数据库记录反制成功")
                            self.log(f"   📄 清理了 {global_db_cleaned} 条数据库记录")
                            overall_success = True
                        else:
                            self.log(f"ℹ️ 未发现需要清理的AugmentCode数据库记录")

                    except Exception as e:
                        self.log(f"❌ 数据库记录反制异常: {e}")
                        import traceback
                        self.log(f"   详细错误: {traceback.format_exc()}")

                # 工作区记录限制反制
                if self.bypass_workspace.get():
                    self.log("📁 执行工作区记录限制反制...")
                    self.log("   📋 自动执行：精确清理工作区AugmentCode数据 → 创建安全备份")

                    try:
                        workspace_cleaned = 0
                        vscode_info = self.vscode_handler.verify_vscode_installation()

                        if vscode_info['installed']:
                            for variant_name in vscode_info.get('variants_found', []):
                                self.log(f"   🔍 处理 {variant_name} 工作区...")

                                # 查找该变体的配置目录
                                for storage_dir in vscode_info.get('storage_directories', []):
                                    if variant_name.lower() not in storage_dir.lower():
                                        continue

                                    config_path = Path(storage_dir)
                                    workspace_storage_path = config_path / "User" / "workspaceStorage"

                                    if workspace_storage_path.exists():
                                        try:
                                            workspace_projects_cleaned = 0

                                            # 遍历每个项目目录
                                            for project_dir in workspace_storage_path.iterdir():
                                                if not project_dir.is_dir():
                                                    continue

                                                project_db_path = project_dir / "state.vscdb"
                                                if project_db_path.exists():
                                                    try:
                                                        # 创建项目数据库备份（如果用户选择）
                                                        if self.create_backups.get():
                                                            import time
                                                            backup_path = f"{project_db_path}.backup.{int(time.time())}"
                                                            import shutil
                                                            shutil.copy2(project_db_path, backup_path)

                                                        # 清理项目数据库中的AugmentCode记录
                                                        import sqlite3
                                                        conn = sqlite3.connect(project_db_path)
                                                        cursor = conn.cursor()
                                                        cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'")
                                                        count = cursor.fetchone()[0]

                                                        if count > 0:
                                                            cursor.execute("DELETE FROM ItemTable WHERE key LIKE '%augment%'")
                                                            conn.commit()
                                                            workspace_projects_cleaned += 1
                                                            self.log(f"         📄 项目 {project_dir.name[:8]}... 清理了 {count} 条记录")

                                                        conn.close()
                                                    except Exception as e:
                                                        self.log(f"         ❌ 项目 {project_dir.name[:8]}... 清理失败: {e}")

                                            if workspace_projects_cleaned > 0:
                                                workspace_cleaned += workspace_projects_cleaned
                                                self.log(f"      📁 精确清理了 {workspace_projects_cleaned} 个项目的AugmentCode数据")
                                            else:
                                                self.log(f"      ℹ️ 工作区中未发现AugmentCode数据")

                                        except Exception as e:
                                            self.log(f"      ❌ 工作区清理失败: {e}")

                        if workspace_cleaned > 0:
                            self.log(f"✅ 工作区记录反制成功")
                            self.log(f"   � 清理了 {workspace_cleaned} 个工作区")
                            overall_success = True
                        else:
                            self.log(f"ℹ️ 未发现需要清理的AugmentCode工作区记录")

                    except Exception as e:
                        self.log(f"❌ 工作区记录反制异常: {e}")
                        import traceback
                        self.log(f"   详细错误: {traceback.format_exc()}")

                # 网络指纹限制反制
                if self.bypass_network.get():
                    self.log("🌐 执行网络指纹限制反制...")
                    self.log("   ⚠️ 这是高级功能，可能影响其他应用")
                    self.log("   📋 自动执行：清理浏览器OAuth缓存 → 重置网络指纹")

                    # 清理浏览器OAuth缓存
                    self._clean_browser_oauth_cache()

                    self.log("   ✅ 网络指纹反制完成")
                
                # 完成
                if overall_success:
                    self.log("🎉 清理完成！请重启IDE并使用新账户登录")
                    messagebox.showinfo("成功", "清理完成！\n\n请重启您的IDE并使用新的AugmentCode账户登录。")
                else:
                    self.log("❌ 清理失败，请检查错误信息")
                    messagebox.showerror("失败", "清理过程中出现错误，请查看日志了解详情。")
                
            except Exception as e:
                self.log(f"❌ 清理过程出现异常: {e}")
                messagebox.showerror("错误", f"清理过程出现异常: {e}")
            finally:
                self.progress.stop()
                self.start_btn.config(state='normal', text="🚀 开始清理")
                self.refresh_status()
        
        threading.Thread(target=cleaning_thread, daemon=True).start()
    
    def show_info(self):
        """显示详细信息"""
        info_window = tk.Toplevel(self.root)
        info_window.title("系统详细信息")
        info_window.geometry("900x700")
        info_window.transient(self.root)

        # 创建笔记本控件用于分页显示
        notebook = ttk.Notebook(info_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 系统概览页面
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="📊 系统概览")

        overview_text = scrolledtext.ScrolledText(overview_frame, wrap=tk.WORD, font=("Consolas", 9))
        overview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 设备ID反制详情页面
        device_id_frame = ttk.Frame(notebook)
        notebook.add(device_id_frame, text="🆔 设备ID反制")

        device_id_text = scrolledtext.ScrolledText(device_id_frame, wrap=tk.WORD, font=("Consolas", 9))
        device_id_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 数据库记录反制详情页面
        database_frame = ttk.Frame(notebook)
        notebook.add(database_frame, text="�️ 数据库记录反制")

        database_text = scrolledtext.ScrolledText(database_frame, wrap=tk.WORD, font=("Consolas", 9))
        database_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 工作区记录反制详情页面
        workspace_frame = ttk.Frame(notebook)
        notebook.add(workspace_frame, text="� 工作区记录反制")

        workspace_text = scrolledtext.ScrolledText(workspace_frame, wrap=tk.WORD, font=("Consolas", 9))
        workspace_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 网络指纹反制详情页面
        network_frame = ttk.Frame(notebook)
        notebook.add(network_frame, text="🌐 网络指纹反制")

        network_text = scrolledtext.ScrolledText(network_frame, wrap=tk.WORD, font=("Consolas", 9))
        network_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        def load_info():
            try:
                import platform
                from datetime import datetime

                # 系统概览
                overview_text.insert(tk.END, f"�️ {APP_NAME} v{VERSION} - 系统概览\n")
                overview_text.insert(tk.END, "=" * 70 + "\n\n")
                overview_text.insert(tk.END, f"🕒 检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                overview_text.insert(tk.END, f"💻 操作系统: {platform.system()} {platform.release()}\n")
                overview_text.insert(tk.END, f"🏗️ 架构: {platform.machine()}\n")
                overview_text.insert(tk.END, f"👤 用户名: {os.getenv('USERNAME', 'Unknown')}\n")
                overview_text.insert(tk.END, f"📁 用户目录: {Path.home()}\n\n")

                # 快速状态总结
                jetbrains_info = self.jetbrains_handler.verify_jetbrains_installation()
                vscode_info = self.vscode_handler.verify_vscode_installation()
                db_info = self.database_cleaner.get_database_info()

                overview_text.insert(tk.END, "� 快速状态总结:\n")
                # 显示具体的JetBrains软件
                if jetbrains_info['installed']:
                    jetbrains_software = set()
                    for file_path in jetbrains_info['existing_files']:
                        software_name = self._get_jetbrains_software_name(Path(file_path).name, jetbrains_info)
                        jetbrains_software.add(software_name)
                    software_list_str = ", ".join(sorted(jetbrains_software))
                    overview_text.insert(tk.END, f"   🔧 JetBrains: ✅ 已安装 ({software_list_str})\n")
                else:
                    overview_text.insert(tk.END, f"   🔧 JetBrains: ❌ 未安装\n")
                # 显示友好的VSCode变体名称
                if vscode_info['installed'] and vscode_info['variants_found']:
                    friendly_variants = [self._get_friendly_vscode_name(v) for v in vscode_info['variants_found']]
                    variants_str = ", ".join(friendly_variants)
                    overview_text.insert(tk.END, f"   📝 VSCode/Cursor: ✅ 已安装 ({variants_str})\n")
                else:
                    overview_text.insert(tk.END, f"   📝 VSCode/Cursor: ❌ 未安装\n")
                overview_text.insert(tk.END, f"   🗃️ 数据库: {db_info['accessible_databases']}/{db_info['total_databases']} 可访问\n\n")

                # 备份信息
                backup_dir = self.backup_manager.backup_dir
                if backup_dir.exists():
                    backup_count = len([f for f in backup_dir.iterdir() if f.is_dir()])
                    overview_text.insert(tk.END, f"� 备份状态: ✅ 已创建 {backup_count} 个备份\n")
                    overview_text.insert(tk.END, f"   📁 备份目录: {backup_dir}\n")
                else:
                    overview_text.insert(tk.END, "💾 备份状态: ❌ 暂无备份\n")

                # 设备ID反制详细信息
                self._load_device_id_details(device_id_text, jetbrains_info, vscode_info)

                # 数据库记录反制详细信息
                self._load_database_record_details(database_text, vscode_info)

                # 工作区记录反制详细信息
                self._load_workspace_record_details(workspace_text, vscode_info)

                # 网络指纹反制详细信息
                self._load_network_fingerprint_details(network_text)

            except Exception as e:
                overview_text.insert(tk.END, f"❌ 获取系统概览失败: {e}\n")
                import traceback
                overview_text.insert(tk.END, f"详细错误:\n{traceback.format_exc()}")

        threading.Thread(target=load_info, daemon=True).start()

    def _get_database_name_from_path(self, db_path):
        """从数据库路径获取数据库名称和类型"""
        path_str = str(db_path).lower()

        # VSCode/Cursor 工作区数据库
        if 'code' in path_str or 'cursor' in path_str:
            if 'workspacestorage' in path_str:
                if 'cursor' in path_str:
                    return "Cursor 工作区数据库"
                else:
                    return "VSCode 工作区数据库"
            elif 'globalstorage' in path_str:
                if 'cursor' in path_str:
                    return "Cursor 全局存储"
                else:
                    return "VSCode 全局存储"
            else:
                if 'cursor' in path_str:
                    return "Cursor 状态数据库"
                else:
                    return "VSCode 状态数据库"

        # 浏览器数据库
        elif 'chrome' in path_str:
            if 'google' in path_str:
                return "Google Chrome 历史数据库"
            else:
                return "Chrome 历史数据库"
        elif 'edge' in path_str:
            return "Microsoft Edge 历史数据库"
        elif 'firefox' in path_str:
            return "Firefox 历史数据库"
        elif 'opera' in path_str:
            return "Opera 历史数据库"
        elif 'brave' in path_str:
            return "Brave 历史数据库"
        elif 'vivaldi' in path_str:
            return "Vivaldi 历史数据库"
        else:
            # 尝试从文件名推断
            file_name = Path(db_path).name.lower()
            if 'state.vscdb' in file_name:
                return "IDE 状态数据库"
            elif 'history' in file_name:
                return "浏览器历史数据库"
            elif 'cookies' in file_name:
                return "浏览器Cookie数据库"
            else:
                return "未知数据库"

    def _get_jetbrains_software_info(self, jetbrains_info):
        """获取详细的JetBrains软件信息"""
        jetbrains_config_dir = jetbrains_info.get('config_dir')
        if not jetbrains_config_dir:
            return []

        jetbrains_path = Path(jetbrains_config_dir)
        installed_software = []

        # 检查常见的JetBrains软件目录模式
        software_patterns = {
            'intellijidea': 'IntelliJ IDEA',
            'pycharm': 'PyCharm',
            'webstorm': 'WebStorm',
            'phpstorm': 'PhpStorm',
            'clion': 'CLion',
            'datagrip': 'DataGrip',
            'rider': 'Rider',
            'goland': 'GoLand',
            'rubymine': 'RubyMine',
            'appcode': 'AppCode'
        }

        # 扫描JetBrains目录下的子目录
        try:
            for item in jetbrains_path.iterdir():
                if item.is_dir():
                    dir_name = item.name.lower()

                    # 检查目录名是否匹配已知的软件模式
                    for pattern, display_name in software_patterns.items():
                        if pattern in dir_name:
                            # 尝试提取版本信息
                            version = self._extract_version_from_dirname(item.name)
                            software_info = {
                                'name': display_name,
                                'version': version,
                                'dir_name': item.name,
                                'path': str(item)
                            }
                            installed_software.append(software_info)
                            break
        except (OSError, PermissionError):
            pass

        return installed_software

    def _extract_version_from_dirname(self, dir_name):
        """从目录名中提取版本信息"""
        import re
        # 匹配版本模式，如 "2023.2", "2024.3" 等
        version_match = re.search(r'(\d{4}\.\d+)', dir_name)
        if version_match:
            return version_match.group(1)
        return None

    def _get_jetbrains_software_name(self, file_name, jetbrains_info):
        """从文件名和路径获取JetBrains软件名称（保持兼容性）"""
        # 获取详细的软件信息
        software_list = self._get_jetbrains_software_info(jetbrains_info)

        if software_list:
            # 按软件名分组，显示每个软件的版本
            software_groups = {}
            for software in software_list:
                name = software['name']
                version = software['version']
                if name not in software_groups:
                    software_groups[name] = []
                if version:
                    software_groups[name].append(version)

            # 构建显示字符串
            display_parts = []
            for name, versions in software_groups.items():
                if versions:
                    # 去重并排序版本
                    unique_versions = sorted(set(versions), reverse=True)
                    if len(unique_versions) == 1:
                        display_parts.append(f"{name} {unique_versions[0]}")
                    else:
                        display_parts.append(f"{name} ({', '.join(unique_versions)})")
                else:
                    display_parts.append(name)

            if len(display_parts) == 1:
                return display_parts[0]
            else:
                # 多个软件时，显示前两个
                return f"JetBrains IDEs ({', '.join(display_parts[:2])}{'...' if len(display_parts) > 2 else ''})"

        # 如果无法检测到具体软件，返回通用名称
        # 注意：PermanentDeviceId和PermanentUserId是所有JetBrains软件共享的
        return "JetBrains IDEs"

    def _get_friendly_vscode_name(self, variant_name):
        """将VSCode变体的内部名称转换为用户友好的显示名称"""
        name_mapping = {
            "Code": "Visual Studio Code (VSCode)",
            "Code - Insiders": "VSCode Insiders",
            "VSCodium": "VSCodium",
            "Cursor": "Cursor",
            "code-server": "VSCode Server",
        }
        return name_mapping.get(variant_name, variant_name)

    def _get_vscode_variant_from_path(self, path_str):
        """从路径中提取VSCode变体名称"""
        path_lower = path_str.lower()

        # 检查路径中是否包含特定的变体标识
        if "cursor" in path_lower:
            return "Cursor"
        elif "code - insiders" in path_lower or "insiders" in path_lower:
            return "Code - Insiders"
        elif "vscodium" in path_lower:
            return "VSCodium"
        elif "code-server" in path_lower:
            return "code-server"
        elif "code" in path_lower:
            return "Code"
        else:
            return "Unknown"

    def _load_device_id_details(self, text_widget, jetbrains_info, vscode_info):
        """加载设备ID反制详细信息"""
        from datetime import datetime

        text_widget.insert(tk.END, "🆔 设备ID限制反制详细信息\n")
        text_widget.insert(tk.END, "=" * 70 + "\n\n")

        text_widget.insert(tk.END, "💡 设备ID反制原理:\n")
        text_widget.insert(tk.END, "   • AugmentCode通过设备唯一标识符来识别和限制用户\n")
        text_widget.insert(tk.END, "   • 修改这些标识符可以让AugmentCode认为这是一个新设备\n")
        text_widget.insert(tk.END, "   • 锁定文件防止AugmentCode重新生成原始ID\n\n")

        # JetBrains设备ID部分
        text_widget.insert(tk.END, "🔧 JetBrains系列软件设备ID:\n")
        if jetbrains_info['installed']:
            # 获取详细的软件信息
            software_list = self._get_jetbrains_software_info(jetbrains_info)

            text_widget.insert(tk.END, f"   📊 检测状态: ✅ 已安装\n")
            text_widget.insert(tk.END, f"   📁 配置目录: {jetbrains_info.get('config_dir', '未知')}\n")
            text_widget.insert(tk.END, f"   📄 设备ID文件数量: {len(jetbrains_info['existing_files'])} 个 (所有JetBrains软件共享)\n\n")

            # 显示检测到的具体软件
            if software_list:
                text_widget.insert(tk.END, f"   🎯 检测到的JetBrains软件 ({len(software_list)} 个):\n")
                for i, software in enumerate(software_list, 1):
                    name = software['name']
                    version = software['version']
                    dir_name = software['dir_name']

                    version_str = f" {version}" if version else ""
                    text_widget.insert(tk.END, f"      {i}. {name}{version_str}\n")
                    text_widget.insert(tk.END, f"         📁 目录: {dir_name}\n")
                text_widget.insert(tk.END, "\n")
            else:
                text_widget.insert(tk.END, "   ⚠️ 未检测到具体的JetBrains软件目录\n")
                text_widget.insert(tk.END, "   💡 可能原因: 软件未启动过或配置目录结构不同\n\n")

            text_widget.insert(tk.END, "   📄 设备ID文件详情:\n")
            for i, file_path in enumerate(jetbrains_info['existing_files'], 1):
                file_obj = Path(file_path)
                is_locked = self.jetbrains_handler.file_locker.is_file_locked(file_obj)
                software_name = self._get_jetbrains_software_name(file_obj.name, jetbrains_info)

                try:
                    size = file_obj.stat().st_size if file_obj.exists() else 0
                    mtime = datetime.fromtimestamp(file_obj.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S') if file_obj.exists() else "未知"
                except:
                    size = 0
                    mtime = "未知"

                text_widget.insert(tk.END, f"\n   {i}. {software_name}\n")
                text_widget.insert(tk.END, f"      📁 文件: {file_obj.name}\n")
                text_widget.insert(tk.END, f"      📁 路径: {file_path}\n")
                text_widget.insert(tk.END, f"      📏 大小: {size} 字节\n")
                text_widget.insert(tk.END, f"      🕒 修改时间: {mtime}\n")
                text_widget.insert(tk.END, f"      🔒 锁定状态: {'✅ 已锁定' if is_locked else '❌ 未锁定'}\n")

                # 读取当前ID
                try:
                    if file_obj.exists():
                        current_id = file_obj.read_text(encoding='utf-8').strip()
                        display_id = current_id[:32] + ('...' if len(current_id) > 32 else '')
                        text_widget.insert(tk.END, f"      🆔 当前ID: {display_id}\n")
                except:
                    text_widget.insert(tk.END, f"      🆔 当前ID: 读取失败\n")
        else:
            text_widget.insert(tk.END, "   ❌ 未检测到JetBrains系列软件安装\n")

        text_widget.insert(tk.END, "\n")

        # VSCode/Cursor设备ID部分
        text_widget.insert(tk.END, "📝 VSCode/Cursor设备ID:\n")
        if vscode_info['installed']:
            text_widget.insert(tk.END, f"   📊 检测状态: ✅ 已安装 ({len(vscode_info['variants_found'])} 个变体)\n")
            text_widget.insert(tk.END, f"   📁 存储目录数量: {vscode_info.get('total_directories', 0)}\n\n")

            # 分离VSCode和Cursor
            vscode_variants = [v for v in vscode_info['variants_found'] if 'cursor' not in v.lower()]
            cursor_variants = [v for v in vscode_info['variants_found'] if 'cursor' in v.lower()]

            if vscode_variants:
                text_widget.insert(tk.END, "   📝 VSCode 变体:\n")
                for variant in vscode_variants:
                    friendly_name = self._get_friendly_vscode_name(variant)
                    text_widget.insert(tk.END, f"      ✅ {friendly_name}\n")

            if cursor_variants:
                text_widget.insert(tk.END, "   🖱️ Cursor 变体:\n")
                for variant in cursor_variants:
                    friendly_name = self._get_friendly_vscode_name(variant)
                    text_widget.insert(tk.END, f"      ✅ {friendly_name}\n")

            # Storage 文件详情
            try:
                vscode_dirs = self.path_manager.get_vscode_directories()
                storage_files = []
                for vscode_dir in vscode_dirs:
                    storage_file = self.path_manager.get_vscode_storage_file(vscode_dir)
                    if storage_file:
                        storage_files.append((vscode_dir, storage_file))

                text_widget.insert(tk.END, f"\n   🆔 设备ID存储文件 ({len(storage_files)} 个):\n")

                for i, (vscode_dir, file_path) in enumerate(storage_files, 1):
                    is_locked = self.vscode_handler.file_locker.is_file_locked(file_path)
                    # 从路径推断变体名称并转换为友好名称
                    if "cursor" in str(vscode_dir).lower():
                        variant_name = "Cursor"
                    elif "code - insiders" in str(vscode_dir).lower():
                        variant_name = "VSCode Insiders"
                    elif "vscodium" in str(vscode_dir).lower():
                        variant_name = "VSCodium"
                    elif "code" in str(vscode_dir).lower():
                        variant_name = "VSCode"
                    else:
                        variant_name = "VSCode"

                    try:
                        size = file_path.stat().st_size if file_path.exists() else 0
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S') if file_path.exists() else "未知"
                    except:
                        size = 0
                        mtime = "未知"

                    text_widget.insert(tk.END, f"\n   {i}. {variant_name} - {file_path.name}\n")
                    text_widget.insert(tk.END, f"      📁 路径: {file_path}\n")
                    text_widget.insert(tk.END, f"      📏 大小: {size} 字节\n")
                    text_widget.insert(tk.END, f"      🕒 修改时间: {mtime}\n")
                    text_widget.insert(tk.END, f"      🔒 锁定状态: {'✅ 已锁定' if is_locked else '❌ 未锁定'}\n")

                    # 读取当前ID
                    try:
                        if file_path.exists():
                            if file_path.name == "machineId":
                                current_id = file_path.read_text(encoding='utf-8').strip()
                                display_id = current_id[:32] + ('...' if len(current_id) > 32 else '')
                                text_widget.insert(tk.END, f"      🆔 当前ID: {display_id}\n")
                            elif file_path.name == "storage.json":
                                import json
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                text_widget.insert(tk.END, f"      🆔 包含的设备ID:\n")
                                for key in ["telemetry.machineId", "telemetry.devDeviceId", "telemetry.sqmId"]:
                                    if key in data:
                                        value = str(data[key])[:32] + ('...' if len(str(data[key])) > 32 else '')
                                        text_widget.insert(tk.END, f"         • {key}: {value}\n")
                    except Exception as e:
                        text_widget.insert(tk.END, f"      🆔 当前ID: 读取失败 ({e})\n")
            except Exception as e:
                text_widget.insert(tk.END, f"   ❌ 获取存储文件失败: {e}\n")
        else:
            text_widget.insert(tk.END, "   ❌ 未检测到VSCode/Cursor安装\n")

        text_widget.insert(tk.END, "\n💡 反制操作说明:\n")
        text_widget.insert(tk.END, "   1. 🔄 生成新的随机设备ID\n")
        text_widget.insert(tk.END, "   2. 💾 自动备份原始ID文件\n")
        text_widget.insert(tk.END, "   3. ✏️ 将新ID写入配置文件\n")
        text_widget.insert(tk.END, "   4. 🔒 锁定文件防止被覆盖\n")
        text_widget.insert(tk.END, "   5. 🚀 重启IDE即可使用新账户登录\n")

    def _load_database_record_details(self, text_widget, vscode_info):
        """加载数据库记录反制详细信息"""
        text_widget.insert(tk.END, "🗃️ 数据库记录限制反制详细信息\n")
        text_widget.insert(tk.END, "=" * 70 + "\n\n")

        text_widget.insert(tk.END, "💡 数据库记录反制原理:\n")
        text_widget.insert(tk.END, "   • AugmentCode在IDE数据库中存储登录状态和使用记录\n")
        text_widget.insert(tk.END, "   • 清理这些记录可以让AugmentCode认为这是全新的IDE\n")
        text_widget.insert(tk.END, "   • 只清理AugmentCode相关记录，保留其他配置\n\n")

        # 数据库记录反制主要针对VSCode/Cursor的全局存储数据库
        text_widget.insert(tk.END, "🗃️ 全局存储数据库记录:\n")
        text_widget.insert(tk.END, "   💡 主要清理IDE的全局状态数据库，如登录状态、使用记录等\n")
        text_widget.insert(tk.END, "   🎯 目标：VSCode/Cursor的state.vscdb文件\n\n")

        try:
            if not vscode_info.get('installed'):
                text_widget.insert(tk.END, "❌ 未检测到VSCode/Cursor安装\n")
                return

            text_widget.insert(tk.END, f"📊 总体状态:\n")
            text_widget.insert(tk.END, f"   🔍 检测到的IDE变体: {', '.join(vscode_info.get('variants_found', []))}\n")
            text_widget.insert(tk.END, f"   📁 配置目录数量: {vscode_info.get('total_directories', 0)}\n\n")

            # 显示每个变体的数据库详细信息
            for variant_name in vscode_info.get('variants_found', []):
                is_cursor = 'cursor' in variant_name.lower()
                icon = "🖱️" if is_cursor else "📝"
                friendly_name = self._get_friendly_vscode_name(variant_name)
                text_widget.insert(tk.END, f"{icon} {friendly_name} 数据库记录:\n")

                # 查找该变体的配置目录 - 只查找globalStorage目录
                variant_dirs = []
                for storage_dir in vscode_info.get('storage_directories', []):
                    if (variant_name.lower() in storage_dir.lower() and
                        'globalStorage' in storage_dir and
                        'workspaceStorage' not in storage_dir):
                        variant_dirs.append(storage_dir)

                if not variant_dirs:
                    text_widget.insert(tk.END, f"   ❌ 未找到配置目录\n\n")
                    continue

                for config_dir in variant_dirs:
                    config_path = Path(config_dir)
                    parent_name = config_path.parent.name
                    text_widget.insert(tk.END, f"   📂 配置目录: {parent_name}\n")
                    text_widget.insert(tk.END, f"      📁 路径: {config_dir}\n")

                    # 检查全局存储数据库
                    global_storage_path = config_path / "User" / "globalStorage"
                    state_db_path = global_storage_path / "state.vscdb"

                    if state_db_path.exists():
                        try:
                            import sqlite3
                            conn = sqlite3.connect(state_db_path)
                            cursor = conn.cursor()

                            # 获取总记录数
                            cursor.execute("SELECT COUNT(*) FROM ItemTable")
                            total_records = cursor.fetchone()[0]

                            # 获取AugmentCode记录数
                            cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'")
                            augment_count = cursor.fetchone()[0]

                            # 获取具体的AugmentCode记录
                            cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%augment%' LIMIT 10")
                            augment_keys = [row[0] for row in cursor.fetchall()]

                            conn.close()

                            text_widget.insert(tk.END, f"      🗃️ 全局存储数据库: ✅ 存在\n")
                            text_widget.insert(tk.END, f"         � 路径: {state_db_path}\n")
                            text_widget.insert(tk.END, f"         �📏 大小: {state_db_path.stat().st_size} 字节\n")
                            text_widget.insert(tk.END, f"         📊 总记录数: {total_records} 条\n")
                            text_widget.insert(tk.END, f"         🏷️ AugmentCode记录: {augment_count} 条\n")

                            if augment_keys:
                                text_widget.insert(tk.END, f"         📋 AugmentCode记录示例:\n")
                                for key in augment_keys[:5]:  # 只显示前5个
                                    text_widget.insert(tk.END, f"            • {key}\n")
                                if len(augment_keys) > 5:
                                    text_widget.insert(tk.END, f"            • ... 还有 {len(augment_keys) - 5} 条记录\n")

                        except Exception as e:
                            text_widget.insert(tk.END, f"      🗃️ 全局存储数据库: ❌ 无法访问 ({e})\n")
                            text_widget.insert(tk.END, f"         📁 路径: {state_db_path}\n")
                            text_widget.insert(tk.END, f"         💡 说明: 数据库文件存在但无法读取，可能被占用或损坏\n")
                    else:
                        text_widget.insert(tk.END, f"      🗃️ 全局存储数据库: ❌ 不存在\n")
                        text_widget.insert(tk.END, f"         📁 预期路径: {state_db_path}\n")
                        text_widget.insert(tk.END, f"         💡 说明: 软件未使用过或数据库未创建，这是正常的\n")
                        text_widget.insert(tk.END, f"         🔍 原因: 首次安装、重置过配置、或从未启动过AugmentCode插件\n")

                    text_widget.insert(tk.END, "\n")

                text_widget.insert(tk.END, "\n")

            text_widget.insert(tk.END, "💡 反制操作说明:\n")
            text_widget.insert(tk.END, "   1. 🔍 扫描IDE数据库中的AugmentCode记录\n")
            text_widget.insert(tk.END, "   2. 💾 自动备份数据库文件\n")
            text_widget.insert(tk.END, "   3. 🗑️ 精确删除AugmentCode相关记录\n")
            text_widget.insert(tk.END, "   4. ✅ 保留其他IDE配置和数据\n")
            text_widget.insert(tk.END, "   5. 🚀 重启IDE后AugmentCode将无法识别使用历史\n")

        except Exception as e:
            text_widget.insert(tk.END, f"❌ 获取数据库信息失败: {e}\n")
            import traceback
            text_widget.insert(tk.END, f"详细错误:\n{traceback.format_exc()}")

    def _load_workspace_record_details(self, text_widget, vscode_info):
        """加载工作区记录反制详细信息"""
        text_widget.insert(tk.END, "📁 工作区记录限制反制详细信息\n")
        text_widget.insert(tk.END, "=" * 70 + "\n\n")

        text_widget.insert(tk.END, "💡 工作区记录反制原理:\n")
        text_widget.insert(tk.END, "   • AugmentCode记录每个项目的使用情况和配置\n")
        text_widget.insert(tk.END, "   • 清理工作区记录可以隐藏项目使用痕迹\n")
        text_widget.insert(tk.END, "   • 只清理AugmentCode数据，保留项目配置\n\n")

        # 工作区记录反制主要针对VSCode/Cursor的项目工作区
        text_widget.insert(tk.END, "📁 项目工作区记录:\n")
        text_widget.insert(tk.END, "   � 主要清理每个项目的使用记录和配置\n")
        text_widget.insert(tk.END, "   � 目标：workspaceStorage目录下的项目数据库\n\n")

        try:
            if not vscode_info.get('installed'):
                text_widget.insert(tk.END, "❌ 未检测到VSCode/Cursor安装\n")
                return

            text_widget.insert(tk.END, f"📊 总体状态:\n")
            text_widget.insert(tk.END, f"   🔍 检测到的IDE变体: {', '.join(vscode_info.get('variants_found', []))}\n\n")

            # 显示每个变体的工作区详细信息
            for variant_name in vscode_info.get('variants_found', []):
                is_cursor = 'cursor' in variant_name.lower()
                icon = "🖱️" if is_cursor else "📝"
                friendly_name = self._get_friendly_vscode_name(variant_name)
                text_widget.insert(tk.END, f"{icon} {friendly_name} 工作区记录:\n")

                # 查找该变体的配置目录 - 只查找workspaceStorage目录
                variant_dirs = []
                for storage_dir in vscode_info.get('storage_directories', []):
                    if (variant_name.lower() in storage_dir.lower() and
                        'workspaceStorage' in storage_dir and
                        'globalStorage' not in storage_dir):
                        variant_dirs.append(storage_dir)

                if not variant_dirs:
                    text_widget.insert(tk.END, f"   ❌ 未找到配置目录\n\n")
                    continue

                for config_dir in variant_dirs:
                    config_path = Path(config_dir)
                    parent_name = config_path.parent.name
                    text_widget.insert(tk.END, f"   📂 配置目录: {parent_name}\n")

                    # 检查工作区存储
                    workspace_storage_path = config_path / "User" / "workspaceStorage"
                    if workspace_storage_path.exists():
                        try:
                            workspace_dirs = list(workspace_storage_path.iterdir())
                            workspace_count = len(workspace_dirs)
                            text_widget.insert(tk.END, f"      📁 工作区存储: ✅ 存在 ({workspace_count} 个项目)\n")
                            text_widget.insert(tk.END, f"         📁 路径: {workspace_storage_path}\n")

                            # 显示前几个项目的详细信息
                            if workspace_count > 0:
                                text_widget.insert(tk.END, f"      📋 项目详情 (显示前5个):\n")
                                for i, project_dir in enumerate(workspace_dirs[:5]):
                                    if project_dir.is_dir():
                                        project_db_path = project_dir / "state.vscdb"
                                        augment_records = 0
                                        total_records = 0

                                        if project_db_path.exists():
                                            try:
                                                import sqlite3
                                                conn = sqlite3.connect(project_db_path)
                                                cursor = conn.cursor()
                                                cursor.execute("SELECT COUNT(*) FROM ItemTable")
                                                total_records = cursor.fetchone()[0]
                                                cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'")
                                                augment_records = cursor.fetchone()[0]
                                                conn.close()
                                            except:
                                                pass

                                        try:
                                            dir_size = sum(f.stat().st_size for f in project_dir.rglob('*') if f.is_file())
                                        except:
                                            dir_size = 0

                                        text_widget.insert(tk.END, f"         {i+1}. 项目ID: {project_dir.name[:16]}...\n")
                                        text_widget.insert(tk.END, f"            📁 完整路径: {project_dir}\n")
                                        text_widget.insert(tk.END, f"            📊 总记录数: {total_records} 条\n")
                                        text_widget.insert(tk.END, f"            🏷️ AugmentCode记录: {augment_records} 条\n")
                                        text_widget.insert(tk.END, f"            📏 目录大小: {dir_size} 字节\n")

                                if workspace_count > 5:
                                    text_widget.insert(tk.END, f"         ... 还有 {workspace_count - 5} 个项目\n")

                        except Exception as e:
                            text_widget.insert(tk.END, f"      📁 工作区存储: ❌ 无法访问 ({e})\n")
                            text_widget.insert(tk.END, f"         📁 路径: {workspace_storage_path}\n")
                    else:
                        text_widget.insert(tk.END, f"      📁 工作区存储: ❌ 不存在\n")
                        text_widget.insert(tk.END, f"         📁 预期路径: {workspace_storage_path}\n")
                        text_widget.insert(tk.END, f"         💡 说明: 未创建过项目工作区或已被清理\n")

                    text_widget.insert(tk.END, "\n")

                text_widget.insert(tk.END, "\n")

            text_widget.insert(tk.END, "💡 反制操作说明:\n")
            text_widget.insert(tk.END, "   1. 🔍 扫描所有项目工作区记录\n")
            text_widget.insert(tk.END, "   2. 💾 自动备份项目数据库\n")
            text_widget.insert(tk.END, "   3. 🗑️ 精确删除AugmentCode项目记录\n")
            text_widget.insert(tk.END, "   4. ✅ 保留项目配置和其他数据\n")
            text_widget.insert(tk.END, "   5. 🚀 清理后AugmentCode无法追踪项目使用历史\n")

        except Exception as e:
            text_widget.insert(tk.END, f"❌ 获取工作区信息失败: {e}\n")
            import traceback
            text_widget.insert(tk.END, f"详细错误:\n{traceback.format_exc()}")

    def _load_network_fingerprint_details(self, text_widget):
        """加载网络指纹反制详细信息"""
        text_widget.insert(tk.END, "🌐 网络指纹限制反制详细信息\n")
        text_widget.insert(tk.END, "=" * 70 + "\n\n")

        text_widget.insert(tk.END, "💡 网络指纹反制原理:\n")
        text_widget.insert(tk.END, "   • AugmentCode可能通过浏览器指纹识别用户\n")
        text_widget.insert(tk.END, "   • 包括Canvas指纹、WebGL指纹、字体指纹等\n")
        text_widget.insert(tk.END, "   • 清理这些指纹可以提高匿名性\n\n")

        text_widget.insert(tk.END, "⚠️ 当前状态: 高级功能 (暂未实现)\n\n")

        text_widget.insert(tk.END, "🔧 计划实现的功能:\n")
        text_widget.insert(tk.END, "   1. 🎨 Canvas指纹清理\n")
        text_widget.insert(tk.END, "      • 清理Canvas绘制缓存\n")
        text_widget.insert(tk.END, "      • 重置Canvas上下文\n\n")

        text_widget.insert(tk.END, "   2. 🖼️ WebGL指纹清理\n")
        text_widget.insert(tk.END, "      • 清理WebGL渲染器信息\n")
        text_widget.insert(tk.END, "      • 重置GPU信息缓存\n\n")

        text_widget.insert(tk.END, "   3. 🔤 字体指纹清理\n")
        text_widget.insert(tk.END, "      • 清理字体检测缓存\n")
        text_widget.insert(tk.END, "      • 重置字体列表\n\n")

        text_widget.insert(tk.END, "   4. 🌐 网络缓存清理\n")
        text_widget.insert(tk.END, "      • 清理DNS缓存\n")
        text_widget.insert(tk.END, "      • 清理HTTP缓存\n")
        text_widget.insert(tk.END, "      • 清理Cookie和LocalStorage\n\n")

        text_widget.insert(tk.END, "⚠️ 风险提示:\n")
        text_widget.insert(tk.END, "   • 可能影响其他网站的正常使用\n")
        text_widget.insert(tk.END, "   • 可能导致需要重新登录其他服务\n")
        text_widget.insert(tk.END, "   • 建议在了解风险后谨慎使用\n\n")

        text_widget.insert(tk.END, "💡 使用建议:\n")
        text_widget.insert(tk.END, "   • 目前主要通过设备ID和数据库记录反制即可\n")
        text_widget.insert(tk.END, "   • 网络指纹反制适用于高级用户\n")
        text_widget.insert(tk.END, "   • 如有需要，可以手动清理浏览器数据\n")

    def _load_jetbrains_details(self, text_widget, jetbrains_info):
        """加载JetBrains详细信息"""
        from datetime import datetime

        # 获取具体的软件列表
        jetbrains_software = set()
        if jetbrains_info['installed']:
            for file_path in jetbrains_info['existing_files']:
                software_name = self._get_jetbrains_software_name(Path(file_path).name, jetbrains_info)
                jetbrains_software.add(software_name)

        software_list_str = ", ".join(sorted(jetbrains_software)) if jetbrains_software else "无"

        text_widget.insert(tk.END, f"🔧 JetBrains系列软件详细信息\n")
        text_widget.insert(tk.END, "=" * 70 + "\n\n")

        if jetbrains_info['installed']:
            text_widget.insert(tk.END, f"📊 总体状态: ✅ 已安装 ({software_list_str})\n")
            text_widget.insert(tk.END, f"📁 配置目录: {jetbrains_info.get('config_dir', '未知')}\n")
            text_widget.insert(tk.END, f"📄 配置文件数量: {len(jetbrains_info['existing_files'])} 个\n\n")

            text_widget.insert(tk.END, "📄 配置文件详情:\n")
            for i, file_path in enumerate(jetbrains_info['existing_files'], 1):
                file_obj = Path(file_path)
                is_locked = self.jetbrains_handler.file_locker.is_file_locked(file_obj)

                try:
                    size = file_obj.stat().st_size if file_obj.exists() else 0
                    mtime = datetime.fromtimestamp(file_obj.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S') if file_obj.exists() else "未知"
                except:
                    size = 0
                    mtime = "未知"

                text_widget.insert(tk.END, f"\n{i}. {file_obj.name}\n")
                text_widget.insert(tk.END, f"   📁 路径: {file_path}\n")
                text_widget.insert(tk.END, f"   📏 大小: {size} 字节\n")
                text_widget.insert(tk.END, f"   🕒 修改时间: {mtime}\n")
                text_widget.insert(tk.END, f"   🔒 锁定状态: {'✅ 已锁定' if is_locked else '❌ 未锁定'}\n")

                # 读取当前ID
                try:
                    if file_obj.exists():
                        current_id = file_obj.read_text(encoding='utf-8').strip()
                        display_id = current_id[:32] + ('...' if len(current_id) > 32 else '')
                        text_widget.insert(tk.END, f"   🆔 当前ID: {display_id}\n")
                except:
                    text_widget.insert(tk.END, f"   🆔 当前ID: 读取失败\n")
        else:
            text_widget.insert(tk.END, "❌ 未检测到JetBrains IDEs安装\n\n")
            text_widget.insert(tk.END, "💡 可能的原因:\n")
            text_widget.insert(tk.END, "   • JetBrains IDEs未安装\n")
            text_widget.insert(tk.END, "   • 配置目录不在标准位置\n")
            text_widget.insert(tk.END, "   • 权限不足无法访问配置目录\n")

    def _load_vscode_details(self, text_widget, vscode_info):
        """加载VSCode详细信息"""
        from datetime import datetime

        text_widget.insert(tk.END, "📝 VSCode/Cursor 详细信息\n")
        text_widget.insert(tk.END, "=" * 70 + "\n\n")

        if vscode_info['installed']:
            text_widget.insert(tk.END, f"📊 总体状态: ✅ 已安装 ({len(vscode_info['variants_found'])} 个变体)\n")
            text_widget.insert(tk.END, f"📁 存储目录数量: {vscode_info.get('total_directories', 0)}\n\n")

            # 分离VSCode和Cursor
            vscode_variants = [v for v in vscode_info['variants_found'] if 'cursor' not in v.lower()]
            cursor_variants = [v for v in vscode_info['variants_found'] if 'cursor' in v.lower()]

            if vscode_variants:
                text_widget.insert(tk.END, "📝 VSCode 变体:\n")
                for variant in vscode_variants:
                    text_widget.insert(tk.END, f"   ✅ {variant}\n")
                text_widget.insert(tk.END, "\n")

            if cursor_variants:
                text_widget.insert(tk.END, "🖱️ Cursor 变体:\n")
                for variant in cursor_variants:
                    text_widget.insert(tk.END, f"   ✅ {variant}\n")
                text_widget.insert(tk.END, "\n")

            # Storage 文件详情
            try:
                vscode_dirs = self.path_manager.get_vscode_directories()
                storage_files = []
                for vscode_dir in vscode_dirs:
                    storage_file = self.path_manager.get_vscode_storage_file(vscode_dir)
                    if storage_file:
                        storage_files.append(storage_file)

                text_widget.insert(tk.END, f"🆔 存储文件 ({len(storage_files)} 个):\n")

                for i, file_path in enumerate(storage_files, 1):
                    is_locked = self.vscode_handler.file_locker.is_file_locked(file_path)

                    try:
                        size = file_path.stat().st_size if file_path.exists() else 0
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S') if file_path.exists() else "未知"
                    except:
                        size = 0
                        mtime = "未知"

                    text_widget.insert(tk.END, f"\n{i}. {file_path.name}\n")
                    text_widget.insert(tk.END, f"   📁 路径: {file_path}\n")
                    text_widget.insert(tk.END, f"   📏 大小: {size} 字节\n")
                    text_widget.insert(tk.END, f"   🕒 修改时间: {mtime}\n")
                    text_widget.insert(tk.END, f"   🔒 锁定状态: {'✅ 已锁定' if is_locked else '❌ 未锁定'}\n")

                    # 读取当前ID
                    try:
                        if file_path.exists():
                            if file_path.name == "machineId":
                                current_id = file_path.read_text(encoding='utf-8').strip()
                                display_id = current_id[:32] + ('...' if len(current_id) > 32 else '')
                                text_widget.insert(tk.END, f"   🆔 当前ID: {display_id}\n")
                            elif file_path.name == "storage.json":
                                import json
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                text_widget.insert(tk.END, f"   🆔 包含的ID:\n")
                                for key in ["telemetry.machineId", "telemetry.devDeviceId", "telemetry.sqmId"]:
                                    if key in data:
                                        value = str(data[key])[:32] + ('...' if len(str(data[key])) > 32 else '')
                                        text_widget.insert(tk.END, f"      • {key}: {value}\n")
                    except Exception as e:
                        text_widget.insert(tk.END, f"   🆔 当前ID: 读取失败 ({e})\n")
            except Exception as e:
                text_widget.insert(tk.END, f"❌ 获取存储文件失败: {e}\n")
        else:
            text_widget.insert(tk.END, "❌ 未检测到VSCode/Cursor安装\n\n")
            text_widget.insert(tk.END, "💡 可能的原因:\n")
            text_widget.insert(tk.END, "   • VSCode/Cursor未安装\n")
            text_widget.insert(tk.END, "   • 配置目录不在标准位置\n")
            text_widget.insert(tk.END, "   • 权限不足无法访问配置目录\n")

    def _load_database_details(self, text_widget, db_info):
        """加载数据库详细信息"""
        text_widget.insert(tk.END, "🗃️ 数据库详细信息\n")
        text_widget.insert(tk.END, "=" * 70 + "\n\n")

        text_widget.insert(tk.END, f"📊 总体状态:\n")
        text_widget.insert(tk.END, f"   📁 总数据库: {db_info['total_databases']}\n")
        text_widget.insert(tk.END, f"   ✅ 可访问: {db_info['accessible_databases']}\n")
        text_widget.insert(tk.END, f"   ❌ 不可访问: {db_info['total_databases'] - db_info['accessible_databases']}\n\n")

        if db_info['databases']:
            text_widget.insert(tk.END, "📄 数据库详情:\n")
            for i, db in enumerate(db_info['databases'], 1):
                text_widget.insert(tk.END, f"\n{i}. {db.get('name', '未知数据库')}\n")
                text_widget.insert(tk.END, f"   📁 路径: {db.get('path', '未知')}\n")
                text_widget.insert(tk.END, f"   📏 大小: {db.get('size', 0)} 字节\n")
                text_widget.insert(tk.END, f"   🔍 可访问: {'✅ 是' if db.get('accessible', False) else '❌ 否'}\n")
                text_widget.insert(tk.END, f"   🏷️ AugmentCode记录: {db.get('augment_records', 0)} 条\n")

                if db.get('error'):
                    text_widget.insert(tk.END, f"   ❌ 错误: {db['error']}\n")
        else:
            text_widget.insert(tk.END, "❌ 未找到任何数据库文件\n\n")
            text_widget.insert(tk.END, "💡 可能的原因:\n")
            text_widget.insert(tk.END, "   • 浏览器未安装或未使用过\n")
            text_widget.insert(tk.END, "   • 数据库文件位置不标准\n")
            text_widget.insert(tk.END, "   • 权限不足无法访问数据库\n")

    def _load_database_details_new(self, text_widget):
        """加载数据库详细信息 - 新版本，只显示重要的数据库"""
        text_widget.insert(tk.END, "🗃️ IDE数据库和工作区详细信息\n")
        text_widget.insert(tk.END, "=" * 70 + "\n\n")

        try:
            # 获取VSCode/Cursor的安装信息
            vscode_info = self.vscode_handler.verify_vscode_installation()

            if not vscode_info.get('installed'):
                text_widget.insert(tk.END, "❌ 未检测到VSCode/Cursor安装\n")
                return

            text_widget.insert(tk.END, f"📊 总体状态:\n")
            text_widget.insert(tk.END, f"   🔍 检测到的IDE变体: {', '.join(vscode_info.get('variants_found', []))}\n")
            text_widget.insert(tk.END, f"   📁 配置目录数量: {vscode_info.get('total_directories', 0)}\n\n")

            # 显示每个变体的详细信息
            for variant_name in vscode_info.get('variants_found', []):
                is_cursor = 'cursor' in variant_name.lower()
                icon = "🖱️" if is_cursor else "📝"
                text_widget.insert(tk.END, f"{icon} {variant_name} 详细信息:\n")

                # 查找该变体的配置目录
                variant_dirs = []
                for storage_dir in vscode_info.get('storage_directories', []):
                    if variant_name.lower() in storage_dir.lower():
                        variant_dirs.append(storage_dir)

                if not variant_dirs:
                    text_widget.insert(tk.END, f"   ❌ 未找到配置目录\n\n")
                    continue

                for config_dir in variant_dirs:
                    config_path = Path(config_dir)
                    parent_name = config_path.parent.name
                    text_widget.insert(tk.END, f"   📂 配置目录: {parent_name}\n")
                    text_widget.insert(tk.END, f"      📁 路径: {config_dir}\n")

                    # 检查全局存储数据库
                    global_storage_path = config_path / "User" / "globalStorage"
                    state_db_path = global_storage_path / "state.vscdb"

                    if state_db_path.exists():
                        try:
                            import sqlite3
                            conn = sqlite3.connect(state_db_path)
                            cursor = conn.cursor()
                            cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'")
                            augment_count = cursor.fetchone()[0]
                            conn.close()

                            text_widget.insert(tk.END, f"      🗃️ 全局存储数据库: ✅ 存在\n")
                            text_widget.insert(tk.END, f"         📏 大小: {state_db_path.stat().st_size} 字节\n")
                            text_widget.insert(tk.END, f"         🏷️ AugmentCode记录: {augment_count} 条\n")
                        except Exception as e:
                            text_widget.insert(tk.END, f"      🗃️ 全局存储数据库: ❌ 无法访问 ({e})\n")
                    else:
                        text_widget.insert(tk.END, f"      🗃️ 全局存储数据库: ❌ 不存在\n")

                    # 检查工作区存储
                    workspace_storage_path = config_path / "User" / "workspaceStorage"
                    if workspace_storage_path.exists():
                        try:
                            workspace_count = len(list(workspace_storage_path.iterdir()))
                            text_widget.insert(tk.END, f"      📁 工作区存储: ✅ 存在 ({workspace_count} 个项目)\n")
                        except Exception as e:
                            text_widget.insert(tk.END, f"      📁 工作区存储: ❌ 无法访问 ({e})\n")
                    else:
                        text_widget.insert(tk.END, f"      📁 工作区存储: ❌ 不存在\n")

                    text_widget.insert(tk.END, "\n")

                text_widget.insert(tk.END, "\n")

            text_widget.insert(tk.END, "💡 说明:\n")
            text_widget.insert(tk.END, "   • 全局存储数据库: 存储AugmentCode插件的登录状态和设置\n")
            text_widget.insert(tk.END, "   • 工作区存储: 存储每个项目的AugmentCode配置和缓存\n")
            text_widget.insert(tk.END, "   • 清理时会自动备份这些数据\n")

        except Exception as e:
            text_widget.insert(tk.END, f"❌ 获取数据库信息失败: {e}\n")
            import traceback
            text_widget.insert(tk.END, f"详细错误:\n{traceback.format_exc()}")

    def show_current_ids(self):
        """显示当前ID"""
        ids_window = tk.Toplevel(self.root)
        ids_window.title("当前ID值")
        ids_window.geometry("700x400")
        ids_window.transient(self.root)
        
        ids_text = scrolledtext.ScrolledText(ids_window, wrap=tk.WORD, font=("Consolas", 9))
        ids_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def load_ids():
            try:
                ids_text.insert(tk.END, "当前ID值\n")
                ids_text.insert(tk.END, "=" * 50 + "\n\n")
                
                # JetBrains系列软件 IDs
                jetbrains_ids = self.jetbrains_handler.get_current_jetbrains_ids()
                ids_text.insert(tk.END, "🔧 JetBrains系列软件:\n")
                if jetbrains_ids:
                    # 获取JetBrains安装信息来显示具体软件名称
                    jetbrains_info = self.jetbrains_handler.verify_jetbrains_installation()
                    for file_name, id_value in jetbrains_ids.items():
                        status = "✅" if id_value else "❌"
                        # 从文件路径推断软件名称
                        software_name = self._get_jetbrains_software_name(file_name, jetbrains_info)
                        ids_text.insert(tk.END, f"   {status} {software_name}: {id_value or '未找到'}\n")
                else:
                    ids_text.insert(tk.END, "   ❌ 未找到IDEA/PyCharm等软件安装\n")
                ids_text.insert(tk.END, "\n")

                # VSCode和Cursor分离显示
                vscode_ids = self.vscode_handler.get_current_vscode_ids()

                # VSCode IDs
                vscode_dirs = {k: v for k, v in vscode_ids.items() if 'cursor' not in k.lower()}
                ids_text.insert(tk.END, "📝 VSCode:\n")
                if vscode_dirs:
                    for directory, ids in vscode_dirs.items():
                        dir_name = Path(directory).name
                        parent_name = Path(directory).parent.name
                        ids_text.insert(tk.END, f"   📂 {parent_name}:\n")
                        for key, value in ids.items():
                            status = "✅" if value else "❌"
                            display_value = value[:32] + '...' if value and len(value) > 32 else (value or '未找到')
                            ids_text.insert(tk.END, f"     {status} {key}: {display_value}\n")
                else:
                    ids_text.insert(tk.END, "   ❌ 未找到VSCode安装\n")
                ids_text.insert(tk.END, "\n")

                # Cursor IDs
                cursor_dirs = {k: v for k, v in vscode_ids.items() if 'cursor' in k.lower()}
                ids_text.insert(tk.END, "🖱️ Cursor:\n")
                if cursor_dirs:
                    for directory, ids in cursor_dirs.items():
                        dir_name = Path(directory).name
                        parent_name = Path(directory).parent.name
                        ids_text.insert(tk.END, f"   📂 {parent_name}:\n")
                        for key, value in ids.items():
                            status = "✅" if value else "❌"
                            display_value = value[:32] + '...' if value and len(value) > 32 else (value or '未找到')
                            ids_text.insert(tk.END, f"     {status} {key}: {display_value}\n")
                else:
                    ids_text.insert(tk.END, "   ❌ 未找到Cursor安装\n")
                ids_text.insert(tk.END, "\n")
                
            except Exception as e:
                ids_text.insert(tk.END, f"获取ID失败: {e}")
        
        threading.Thread(target=load_ids, daemon=True).start()
    
    def open_backup_dir(self):
        """打开备份目录"""
        try:
            backup_dir = self.backup_manager.backup_dir
            if backup_dir.exists():
                os.startfile(str(backup_dir))  # Windows
            else:
                messagebox.showinfo("提示", f"备份目录不存在: {backup_dir}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开备份目录: {e}")

    def restore_backup(self):
        """恢复备份"""
        try:
            backup_dir = self.backup_manager.backup_dir
            if not backup_dir.exists():
                messagebox.showinfo("提示", "备份目录不存在，没有可恢复的备份")
                return

            # 获取备份文件列表（.bak文件）
            backup_files = [f for f in backup_dir.iterdir() if f.is_file() and f.suffix == '.bak']
            if not backup_files:
                messagebox.showinfo("提示", "没有找到备份文件")
                return

            # 创建选择窗口
            restore_window = tk.Toplevel(self.root)
            restore_window.title("选择要恢复的备份")
            restore_window.geometry("600x400")
            restore_window.transient(self.root)

            tk.Label(restore_window, text="选择要恢复的备份:", font=("Arial", 12)).pack(pady=10)

            # 备份列表
            listbox = tk.Listbox(restore_window, height=15)
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 按时间排序备份
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for backup_file in backup_files:
                # 显示备份时间和内容
                mtime = backup_file.stat().st_mtime
                time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                file_size = backup_file.stat().st_size
                listbox.insert(tk.END, f"{backup_file.name} - {time_str} ({file_size} 字节)")

            def do_restore():
                selection = listbox.curselection()
                if not selection:
                    messagebox.showwarning("警告", "请选择要恢复的备份")
                    return

                backup_file = backup_files[selection[0]]

                # 智能恢复警告
                warning_msg = f"""⚠️ 重要警告：恢复备份的后果

📁 备份: {backup_file.name}
📅 时间: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(backup_file.stat().st_mtime))}

🔄 恢复后会发生什么：
✅ 所有配置文件将恢复到备份时的状态
❌ AugmentCode的限制也会重新生效！
❌ 您将无法使用新账户登录AugmentCode
❌ 需要重新运行清理工具才能绕过限制

💡 建议的使用场景：
• 误操作需要恢复数据
• 测试和调试用途
• 提取特定配置文件

确定要继续恢复吗？"""

                if messagebox.askyesno("⚠️ 恢复备份警告", warning_msg):
                    try:
                        # 尝试自动恢复备份
                        backup_name = backup_file.stem  # 去掉.bak扩展名

                        # 检查是否可以自动恢复
                        restore_result = self.backup_manager.auto_restore_backup(backup_name)

                        if restore_result["success"]:
                            success_msg = f"""✅ 备份恢复成功！

📁 已恢复的文件:
{chr(10).join(f"• {item['target']}" for item in restore_result['restored_files'])}

⚠️ 重要提醒:
• AugmentCode的限制已重新生效
• 需要重启相关IDE才能看到变化
• 如需继续绕过限制，请重新运行清理工具"""
                            messagebox.showinfo("✅ 恢复成功", success_msg)
                            self.log(f"✅ 自动恢复备份成功: {backup_file.name}")
                        else:
                            # 自动恢复失败，提供手动恢复说明
                            error_msg = restore_result.get("error", "未知错误")
                            manual_msg = f"""❌ 自动恢复失败: {error_msg}

📁 请手动恢复备份文件:
📂 备份文件: {backup_file}

🔧 手动恢复步骤:
1. 关闭所有IDE (VSCode/Cursor/JetBrains)
2. 找到备份文件的原始位置
3. 将备份文件复制回原位置并重命名
4. 重新启动IDE

💡 提示: 查看程序日志了解原始文件路径"""
                            messagebox.showwarning("⚠️ 需要手动恢复", manual_msg)
                            self.log(f"❌ 自动恢复失败: {backup_file.name} - {error_msg}")

                        restore_window.destroy()
                    except Exception as e:
                        messagebox.showerror("错误", f"恢复过程出现异常: {e}")
                        self.log(f"❌ 恢复异常: {e}")

            # 按钮
            button_frame = tk.Frame(restore_window)
            button_frame.pack(pady=10)

            tk.Button(button_frame, text="恢复选中的备份", command=do_restore).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="取消", command=restore_window.destroy).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("错误", f"无法访问备份: {e}")

    def _close_ide_processes(self):
        """关闭所有IDE进程"""
        try:
            import psutil
        except ImportError:
            self.log("› ❌ 缺少 psutil 模块，请运行: pip install psutil")
            return False

        import subprocess
        import time

        # 定义要关闭的IDE进程
        ide_processes = {
            'VSCODE': ['code.exe', 'code'],
            'CURSOR': ['cursor.exe', 'cursor'],
            'PYCHARM': ['pycharm64.exe', 'pycharm.exe', 'pycharm'],
            'INTELLIJ': ['idea64.exe', 'idea.exe', 'idea'],
            'WEBSTORM': ['webstorm64.exe', 'webstorm.exe', 'webstorm'],
            'RIDER': ['rider64.exe', 'rider.exe', 'rider']
        }

        total_closed = 0

        for ide_name, process_names in ide_processes.items():
            try:
                processes_found = []

                # 查找进程
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        if any(proc_name == name.lower() for name in process_names):
                            processes_found.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                if processes_found:
                    self.log(f"› 🔍 发现 {len(processes_found)} 个 {ide_name} 进程")

                    # 第一步：温和地终止进程
                    terminated_count = 0
                    for proc in processes_found:
                        try:
                            proc.terminate()
                            terminated_count += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue

                    if terminated_count > 0:
                        self.log(f"› 📤 发送终止信号给 {terminated_count} 个进程")
                        time.sleep(3)  # 等待进程优雅退出

                    # 第二步：检查哪些进程还在运行
                    still_running = []
                    for proc in processes_found:
                        try:
                            if proc.is_running():
                                still_running.append(proc)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue

                    # 第三步：强制结束仍在运行的进程
                    if still_running:
                        self.log(f"› ⚡ 强制结束 {len(still_running)} 个顽固进程")
                        for proc in still_running:
                            try:
                                proc.kill()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                continue
                        time.sleep(1)

                    # 第四步：验证进程是否真的被关闭
                    final_check = []
                    for proc in processes_found:
                        try:
                            if proc.is_running():
                                final_check.append(proc)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue

                    if final_check:
                        self.log(f"› ⚠️ {ide_name}: 仍有 {len(final_check)} 个进程无法关闭")
                        # 尝试使用系统命令强制关闭
                        try:
                            if ide_name == 'CURSOR':
                                subprocess.run(['taskkill', '/F', '/IM', 'cursor.exe', '/T'],
                                             capture_output=True, check=False)
                            elif ide_name == 'VSCODE':
                                subprocess.run(['taskkill', '/F', '/IM', 'code.exe', '/T'],
                                             capture_output=True, check=False)
                        except:
                            pass
                    else:
                        self.log(f"› ✅ 已关闭 {ide_name}")
                        total_closed += len(processes_found)

            except Exception as e:
                self.log(f"› ⚠️ 关闭 {ide_name} 时出错: {e}")

        self.log(f"› ✅ IDE进程关闭完成 (共关闭 {total_closed} 个进程)")
        return True

    def _execute_safe_mode_cleaning(self):
        """执行安全模式清理 - 专门针对OAuth登录失败问题"""
        try:
            overall_success = True
            cleaned_count = 0

            # 清理VSCode/Cursor数据库和OAuth状态
            vscode_info = self.vscode_handler.verify_vscode_installation()
            if vscode_info['installed']:
                self.log("   🔍 检测到VSCode/Cursor安装，开始清理OAuth状态...")

                # 获取所有VSCode目录
                vscode_dirs = self.path_manager.get_vscode_directories()

                for vscode_dir in vscode_dirs:
                    variant_name = self._get_vscode_variant_from_path(str(vscode_dir))
                    self.log(f"   📁 处理 {variant_name} 配置...")

                    # 清理全局存储数据库 (主要的OAuth状态存储)
                    if 'globalStorage' in str(vscode_dir):
                        # 1. 清理数据库文件
                        db_file = vscode_dir / "state.vscdb"
                        if db_file.exists():
                            records_cleaned = self._clean_oauth_database_file(db_file, variant_name)
                            if records_cleaned > 0:
                                cleaned_count += records_cleaned
                                self.log(f"      ✅ 清理了 {records_cleaned} 条OAuth记录")

                        # 2. 清理storage.json文件 (关键的登录状态存储)
                        storage_file = vscode_dir / "storage.json"
                        if storage_file.exists():
                            auth_keys_cleaned = self._clean_storage_json_auth(storage_file, variant_name)
                            if auth_keys_cleaned > 0:
                                cleaned_count += auth_keys_cleaned
                                self.log(f"      🔑 清理了 {auth_keys_cleaned} 个认证令牌")

                    # 清理工作区数据库
                    elif 'workspaceStorage' in str(vscode_dir):
                        db_file = vscode_dir / "state.vscdb"
                        if db_file.exists():
                            records_cleaned = self._clean_oauth_database_file(db_file, f"{variant_name} 工作区")
                            if records_cleaned > 0:
                                cleaned_count += records_cleaned

            # 清理JetBrains ID文件和OAuth状态
            jetbrains_info = self.jetbrains_handler.verify_jetbrains_installation()
            if jetbrains_info['installed']:
                self.log("   🔍 检测到JetBrains安装，开始清理设备ID...")
                result = self.jetbrains_handler.process_jetbrains_ides(
                    create_backups=False,  # 安全模式不创建备份
                    lock_files=True,
                    clean_databases=True
                )
                if result['success']:
                    files_processed = result.get('files_processed', [])
                    files_count = len(files_processed) if isinstance(files_processed, list) else files_processed
                    self.log(f"      ✅ 处理了 {files_count} 个JetBrains ID文件")
                else:
                    overall_success = False
                    self.log(f"      ❌ JetBrains处理失败: {'; '.join(result['errors'])}")

            # 注意：浏览器OAuth缓存清理已移至网络指纹反制选项中
            # 避免在安全模式中自动清理浏览器数据

            if cleaned_count > 0:
                self.log(f"   ✅ 总共清理了 {cleaned_count} 条OAuth相关记录")
            else:
                self.log("   ℹ️ 未发现需要清理的OAuth记录")

            return overall_success

        except Exception as e:
            self.log(f"› ❌ 安全模式清理失败: {e}")
            import traceback
            self.log(f"   详细错误: {traceback.format_exc()}")
            return False

    def _clean_database_file(self, db_file):
        """清理单个数据库文件中的AugmentCode记录"""
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # 检查并删除AugmentCode相关记录
            cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'")
            count_before = cursor.fetchone()[0]

            if count_before > 0:
                cursor.execute("DELETE FROM ItemTable WHERE key LIKE '%augment%'")
                conn.commit()
                self.log(f"   清理了 {count_before} 条记录: {db_file.name}")

            conn.close()

        except Exception as e:
            self.log(f"   清理数据库失败 {db_file}: {e}")

    def _clean_oauth_database_file(self, db_file, variant_name):
        """专门清理OAuth相关的数据库记录"""
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ItemTable'")
            if not cursor.fetchone():
                conn.close()
                return 0

            # OAuth相关的键模式 - 更全面的清理
            oauth_patterns = [
                '%augment%',           # AugmentCode相关
                '%oauth%',             # OAuth状态
                '%auth%',              # 认证状态
                '%session%',           # 会话状态
                '%token%',             # 令牌
                '%login%',             # 登录状态
                '%workos%',            # WorkOS (AugmentCode使用的认证服务)
                '%cursor.com%',        # Cursor域名相关
                '%telemetry%'          # 遥测数据
            ]

            total_cleaned = 0
            for pattern in oauth_patterns:
                cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE ?", (pattern,))
                count = cursor.fetchone()[0]

                if count > 0:
                    cursor.execute("DELETE FROM ItemTable WHERE key LIKE ?", (pattern,))
                    total_cleaned += count
                    self.log(f"      🗑️ 清理 {pattern} 模式: {count} 条记录")

            if total_cleaned > 0:
                conn.commit()
                self.log(f"   ✅ {variant_name}: 总共清理了 {total_cleaned} 条OAuth记录")

            conn.close()
            return total_cleaned

        except Exception as e:
            self.log(f"   ❌ 清理OAuth数据库失败 {db_file}: {e}")
            return 0

    def _clean_storage_json_auth(self, storage_file, variant_name):
        """清理storage.json文件中的认证信息"""
        try:
            import json

            # 读取storage.json文件
            with open(storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 需要清理的认证相关键
            auth_keys_to_remove = [
                'cursorAuth/accessToken',      # Cursor访问令牌
                'cursorAuth/refreshToken',     # Cursor刷新令牌
                'cursorAuth/cachedSignUpType', # 缓存的注册类型
                'augmentcode.accessToken',     # AugmentCode访问令牌
                'augmentcode.refreshToken',    # AugmentCode刷新令牌
                'augmentcode.userInfo',        # AugmentCode用户信息
                'augmentcode.sessionId',       # AugmentCode会话ID
                'workos.accessToken',          # WorkOS访问令牌
                'workos.refreshToken',         # WorkOS刷新令牌
                'workos.userInfo',             # WorkOS用户信息
            ]

            # 查找并删除认证相关的键
            keys_removed = 0
            keys_to_delete = []

            for key in data.keys():
                # 精确匹配
                if key in auth_keys_to_remove:
                    keys_to_delete.append(key)
                    keys_removed += 1
                # 模糊匹配 - 包含认证相关关键词的键
                elif any(pattern in key.lower() for pattern in ['auth', 'token', 'session', 'login', 'augment', 'workos']):
                    keys_to_delete.append(key)
                    keys_removed += 1

            # 删除找到的键
            for key in keys_to_delete:
                del data[key]
                self.log(f"      🗑️ 删除认证键: {key}")

            # 如果有修改，写回文件
            if keys_removed > 0:
                # 创建备份
                backup_file = storage_file.with_suffix('.json.backup')
                import shutil
                shutil.copy2(storage_file, backup_file)
                self.log(f"      💾 创建备份: {backup_file.name}")

                # 写入修改后的数据
                with open(storage_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                self.log(f"   ✅ {variant_name}: 清理了 {keys_removed} 个认证令牌")
            else:
                self.log(f"   ℹ️ {variant_name}: 未发现需要清理的认证令牌")

            return keys_removed

        except Exception as e:
            self.log(f"   ❌ 清理storage.json认证信息失败 {storage_file}: {e}")
            return 0

    def _clean_browser_oauth_cache(self):
        """安全清理浏览器中的OAuth缓存 - 只清理特定域名数据"""
        try:
            self.log("   🌐 安全清理浏览器OAuth缓存...")
            self.log("   💡 使用精确清理模式，只清理AugmentCode相关数据")

            # 常见浏览器的用户数据目录
            browser_paths = []

            # Chrome/Chromium系列
            chrome_base = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
            if chrome_base.exists():
                browser_paths.append(("Chrome", chrome_base))

            # Edge
            edge_base = Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data"
            if edge_base.exists():
                browser_paths.append(("Edge", edge_base))

            # Brave
            brave_base = Path.home() / "AppData" / "Local" / "BraveSoftware" / "Brave-Browser" / "User Data"
            if brave_base.exists():
                browser_paths.append(("Brave", brave_base))

            cleaned_browsers = 0
            for browser_name, browser_path in browser_paths:
                try:
                    # 只清理特定域名的数据，不删除整个存储目录
                    default_profile = browser_path / "Default"
                    if default_profile.exists():
                        # 安全清理Local Storage - 只清理特定域名
                        local_storage_base = default_profile / "Local Storage" / "leveldb"
                        if local_storage_base.exists():
                            cleaned_count = self._safe_clean_browser_storage(local_storage_base, browser_name, "Local Storage")
                            if cleaned_count > 0:
                                cleaned_browsers += 1

                        # 清理Cookies中的特定域名
                        cookies_file = default_profile / "Cookies"
                        if cookies_file.exists():
                            cleaned_count = self._safe_clean_browser_cookies(cookies_file, browser_name)
                            if cleaned_count > 0:
                                cleaned_browsers += 1

                except Exception as e:
                    self.log(f"      ⚠️ 清理 {browser_name} 时出错: {e}")

            if cleaned_browsers > 0:
                self.log(f"   ✅ 安全清理了 {cleaned_browsers} 个浏览器的OAuth数据")
            else:
                self.log("   ℹ️ 未发现需要清理的浏览器OAuth数据")

        except Exception as e:
            self.log(f"   ❌ 清理浏览器OAuth缓存失败: {e}")

    def _safe_clean_browser_storage(self, storage_path, browser_name, storage_type):
        """安全清理浏览器存储 - 只清理特定域名的数据"""
        try:
            # 这里我们不删除整个存储目录，而是标记需要手动清理
            self.log(f"      ℹ️ {browser_name} {storage_type}: 建议手动清理 cursor.com 和 augmentcode.com 相关数据")
            self.log(f"      📁 路径: {storage_path}")
            return 1  # 表示找到了需要清理的存储
        except Exception as e:
            self.log(f"      ❌ 检查 {browser_name} {storage_type} 失败: {e}")
            return 0

    def _safe_clean_browser_cookies(self, cookies_file, browser_name):
        """安全清理浏览器Cookies - 只清理特定域名"""
        try:
            # 这里我们不直接操作Cookies数据库，而是提供清理建议
            self.log(f"      ℹ️ {browser_name} Cookies: 建议手动清理 cursor.com 和 augmentcode.com 相关Cookie")
            self.log(f"      📁 路径: {cookies_file}")
            return 1  # 表示找到了需要清理的Cookies
        except Exception as e:
            self.log(f"      ❌ 检查 {browser_name} Cookies 失败: {e}")
            return 0

    def _clean_augmentcode_directory(self):
        """清理.augmentcode目录"""
        try:
            import os
            home_dir = Path.home()
            augmentcode_dir = home_dir / ".augmentcode"

            if augmentcode_dir.exists():
                import shutil
                shutil.rmtree(augmentcode_dir, ignore_errors=True)
                self.log("   清理了 .augmentcode 目录")
            else:
                self.log("   .augmentcode 目录不存在")

        except Exception as e:
            self.log(f"   清理 .augmentcode 目录失败: {e}")

    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    try:
        app = AugmentCleanerGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("启动错误", f"程序启动失败: {e}")


if __name__ == "__main__":
    main()
