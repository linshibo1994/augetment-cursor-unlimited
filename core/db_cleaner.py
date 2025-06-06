#!/usr/bin/env python3
"""
Database Cleaner - 数据库清理模块

专门处理 VSCode 和 JetBrains 数据库中的 AugmentCode 相关记录清理
"""

import logging
import sqlite3
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

from config.settings import VSCODE_CONFIG, JETBRAINS_CONFIG

logger = logging.getLogger(__name__)


class DatabaseCleaner:
    """数据库清理器"""
    
    def __init__(self, path_manager, backup_manager):
        """
        初始化数据库清理器
        
        Args:
            path_manager: 路径管理器实例
            backup_manager: 备份管理器实例
        """
        self.path_manager = path_manager
        self.backup_manager = backup_manager
    
    def clean_vscode_databases(self, create_backups: bool = True) -> Dict[str, Any]:
        """
        清理 VSCode 数据库中的 AugmentCode 记录
        
        Args:
            create_backups: 是否创建备份
            
        Returns:
            清理结果字典
        """
        logger.info("Starting VSCode database cleaning")
        
        results = {
            "success": False,
            "databases_found": 0,
            "databases_cleaned": 0,
            "databases_failed": 0,
            "total_records_deleted": 0,
            "backups_created": [],
            "errors": []
        }
        
        try:
            # Find VSCode directories
            vscode_dirs = self.path_manager.get_vscode_directories()
            if not vscode_dirs:
                results["errors"].append("No VSCode installations found")
                return results
            
            # Process each VSCode directory
            for vscode_dir in vscode_dirs:
                db_file = self.path_manager.get_vscode_database_file(vscode_dir)
                if db_file:
                    results["databases_found"] += 1
                    
                    db_result = self._clean_database_file(db_file, create_backups)
                    if db_result["success"]:
                        results["databases_cleaned"] += 1
                        results["total_records_deleted"] += db_result["records_deleted"]
                        if db_result["backup_path"]:
                            results["backups_created"].append(db_result["backup_path"])
                    else:
                        results["databases_failed"] += 1
                        if db_result["error"]:
                            results["errors"].append(f"{db_file.name}: {db_result['error']}")
            
            # 判断整体成功
            if results["databases_cleaned"] > 0:
                results["success"] = True
                logger.info(f"Successfully cleaned {results['databases_cleaned']} VSCode databases")
            
        except Exception as e:
            error_msg = f"VSCode database cleaning failed: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    def clean_jetbrains_databases(self, create_backups: bool = True) -> Dict[str, Any]:
        """
        清理 JetBrains 数据库中的 AugmentCode 记录
        
        Args:
            create_backups: 是否创建备份
            
        Returns:
            清理结果字典
        """
        logger.info("Starting JetBrains database cleaning")
        
        results = {
            "success": False,
            "databases_found": 0,
            "databases_cleaned": 0,
            "databases_failed": 0,
            "total_records_deleted": 0,
            "backups_created": [],
            "errors": []
        }
        
        try:
            # Find JetBrains database files
            jetbrains_dbs = self.path_manager.get_jetbrains_database_files()
            if not jetbrains_dbs:
                results["errors"].append("No JetBrains database files found")
                return results
            
            results["databases_found"] = len(jetbrains_dbs)
            
            # Process each database file
            for db_file in jetbrains_dbs:
                db_result = self._clean_database_file(db_file, create_backups, use_jetbrains_patterns=True)
                if db_result["success"]:
                    results["databases_cleaned"] += 1
                    results["total_records_deleted"] += db_result["records_deleted"]
                    if db_result["backup_path"]:
                        results["backups_created"].append(db_result["backup_path"])
                else:
                    results["databases_failed"] += 1
                    if db_result["error"]:
                        results["errors"].append(f"{db_file.name}: {db_result['error']}")
            
            # 判断整体成功
            if results["databases_cleaned"] > 0:
                results["success"] = True
                logger.info(f"Successfully cleaned {results['databases_cleaned']} JetBrains databases")
            
        except Exception as e:
            error_msg = f"JetBrains database cleaning failed: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    def _clean_database_file(self, db_file: Path, create_backups: bool, 
                            use_jetbrains_patterns: bool = False) -> Dict[str, Any]:
        """
        清理单个数据库文件
        
        Args:
            db_file: 数据库文件路径
            create_backups: 是否创建备份
            use_jetbrains_patterns: 是否使用 JetBrains 模式
            
        Returns:
            清理结果字典
        """
        result = {
            "success": False,
            "backup_path": None,
            "records_deleted": 0,
            "error": None
        }
        
        try:
            # 检查文件是否为有效的 SQLite 数据库
            if not self._is_valid_sqlite_database(db_file):
                logger.warning(f"Skipping non-SQLite file: {db_file}")
                result["success"] = True  # 不是错误，只是跳过
                return result
            
            # 创建备份
            if create_backups:
                backup_path = self.backup_manager.create_file_backup(db_file)
                if backup_path:
                    result["backup_path"] = str(backup_path)
                    logger.info(f"Created backup: {backup_path}")
            
            # 清理数据库
            records_deleted = self._execute_database_cleaning(db_file, use_jetbrains_patterns)
            result["records_deleted"] = records_deleted
            
            logger.info(f"Successfully deleted {records_deleted} records from {db_file}")
            result["success"] = True
            
        except Exception as e:
            error_msg = f"Database cleaning failed: {str(e)}"
            logger.error(f"Error cleaning database {db_file}: {error_msg}")
            result["error"] = error_msg
        
        return result
    
    def _is_valid_sqlite_database(self, db_file: Path) -> bool:
        """
        检查文件是否为有效的 SQLite 数据库
        
        Args:
            db_file: 数据库文件路径
            
        Returns:
            是否为有效的 SQLite 数据库
        """
        try:
            # 检查文件头
            with open(db_file, 'rb') as f:
                header = f.read(16)
                if not header.startswith(b'SQLite format 3\x00'):
                    return False
            
            # 尝试连接数据库
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            cursor.close()
            conn.close()
            return True
            
        except Exception:
            return False

    def _execute_database_cleaning(self, db_file: Path, use_jetbrains_patterns: bool = False) -> int:
        """
        执行实际的数据库清理操作

        Args:
            db_file: 数据库文件路径
            use_jetbrains_patterns: 是否使用 JetBrains 模式

        Returns:
            删除的记录数量
        """
        total_deleted = 0

        try:
            # 连接数据库
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()

            try:
                # 获取所有表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                # 选择清理模式
                patterns = JETBRAINS_CONFIG["augment_patterns"] if use_jetbrains_patterns else [
                    "%augment%", "%Augment%", "%AUGMENT%", "%device%", "%machine%", "%telemetry%"
                ]

                # 清理每个表
                for table_name, in tables:
                    table_deleted = self._clean_table_records(cursor, table_name, patterns)
                    total_deleted += table_deleted

                # 提交所有更改
                conn.commit()

                # 清理备份数据库（如果存在）
                backup_db_file = db_file.with_suffix(db_file.suffix + ".backup")
                if backup_db_file.exists():
                    logger.info(f"Cleaning backup database: {backup_db_file}")
                    backup_deleted = self._execute_database_cleaning(backup_db_file, use_jetbrains_patterns)
                    logger.info(f"Deleted {backup_deleted} records from backup database")

            finally:
                cursor.close()
                conn.close()

        except sqlite3.Error as e:
            logger.error(f"SQLite error while cleaning {db_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while cleaning {db_file}: {e}")
            raise

        return total_deleted

    def _clean_table_records(self, cursor, table_name: str, patterns: List[str]) -> int:
        """
        清理表中的记录

        Args:
            cursor: 数据库游标
            table_name: 表名
            patterns: 匹配模式列表

        Returns:
            删除的记录数量
        """
        deleted_count = 0

        try:
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # 查找文本列
            text_columns = [col[1] for col in columns if col[2].upper() in ['TEXT', 'VARCHAR', 'CHAR', 'BLOB']]

            for column in text_columns:
                for pattern in patterns:
                    try:
                        # 计算要删除的记录数
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column} LIKE ?", (pattern,))
                        count = cursor.fetchone()[0]

                        if count > 0:
                            # 删除记录
                            cursor.execute(f"DELETE FROM {table_name} WHERE {column} LIKE ?", (pattern,))
                            deleted_count += count
                            logger.info(f"Cleaned {count} records from {table_name}.{column} matching {pattern}")

                    except sqlite3.Error as e:
                        logger.warning(f"Could not clean {table_name}.{column} with pattern {pattern}: {e}")
                        continue

        except sqlite3.Error as e:
            logger.warning(f"Could not process table {table_name}: {e}")

        return deleted_count

    def get_database_info(self) -> Dict[str, Any]:
        """
        获取数据库信息

        Returns:
            数据库信息字典
        """
        info = {
            "vscode_databases": [],
            "jetbrains_databases": [],
            "total_databases": 0,
            "accessible_databases": 0,
            "errors": []
        }

        try:
            # VSCode 数据库
            vscode_dirs = self.path_manager.get_vscode_directories()
            for vscode_dir in vscode_dirs:
                db_file = self.path_manager.get_vscode_database_file(vscode_dir)
                if db_file:
                    db_info = {
                        "path": str(db_file),
                        "variant": vscode_dir.parent.name,
                        "exists": db_file.exists(),
                        "accessible": False,
                        "size": 0
                    }

                    if db_file.exists():
                        try:
                            db_info["size"] = db_file.stat().st_size
                            if self._is_valid_sqlite_database(db_file):
                                db_info["accessible"] = True
                                info["accessible_databases"] += 1
                        except Exception as e:
                            info["errors"].append(f"Error accessing {db_file}: {str(e)}")

                    info["vscode_databases"].append(db_info)
                    info["total_databases"] += 1

            # JetBrains 数据库
            jetbrains_dbs = self.path_manager.get_jetbrains_database_files()
            for db_file in jetbrains_dbs:
                db_info = {
                    "path": str(db_file),
                    "exists": db_file.exists(),
                    "accessible": False,
                    "size": 0
                }

                if db_file.exists():
                    try:
                        db_info["size"] = db_file.stat().st_size
                        if self._is_valid_sqlite_database(db_file):
                            db_info["accessible"] = True
                            info["accessible_databases"] += 1
                    except Exception as e:
                        info["errors"].append(f"Error accessing {db_file}: {str(e)}")

                info["jetbrains_databases"].append(db_info)
                info["total_databases"] += 1

        except Exception as e:
            info["errors"].append(f"Error getting database info: {str(e)}")

        return info
