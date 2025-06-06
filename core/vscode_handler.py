#!/usr/bin/env python3
"""
VSCode Handler - VSCode/Cursor 处理模块

处理 VSCode 系列编辑器的设备ID、工作区存储和数据库清理
"""

import json
import logging
import sqlite3
import shutil
import stat
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid
import hashlib
import secrets

from config.settings import VSCODE_CONFIG
from utils.id_generator import IDGenerator
from utils.file_locker import FileLockManager

logger = logging.getLogger(__name__)


class VSCodeHandler:
    """VSCode 系列编辑器处理器"""
    
    def __init__(self, path_manager, backup_manager):
        """
        初始化 VSCode 处理器
        
        Args:
            path_manager: 路径管理器实例
            backup_manager: 备份管理器实例
        """
        self.path_manager = path_manager
        self.backup_manager = backup_manager
        self.id_generator = IDGenerator()
        self.file_locker = FileLockManager()
        
    def process_vscode_installations(self, create_backups: bool = True, 
                                   lock_files: bool = True,
                                   clean_workspace: bool = False,
                                   clean_cache: bool = False) -> Dict[str, Any]:
        """
        处理所有 VSCode 安装
        
        Args:
            create_backups: 是否创建备份
            lock_files: 是否锁定文件
            clean_workspace: 是否清理工作区
            clean_cache: 是否清理缓存
            
        Returns:
            处理结果字典
        """
        logger.info("Starting VSCode processing")
        
        results = {
            "success": False,
            "vscode_found": False,
            "variants_found": [],
            "total_directories": 0,
            "directories_processed": 0,
            "directories_failed": 0,
            "files_processed": [],
            "files_failed": [],
            "backups_created": [],
            "old_ids": {},
            "new_ids": {},
            "workspace_cleaned": 0,
            "cache_cleaned": 0,
            "errors": []
        }
        
        try:
            # 获取 VSCode 目录
            vscode_dirs = self.path_manager.get_vscode_directories()
            if not vscode_dirs:
                results["errors"].append("No VSCode installations found")
                return results
            
            results["vscode_found"] = True
            results["total_directories"] = len(vscode_dirs)
            
            # 处理每个 VSCode 目录
            for vscode_dir in vscode_dirs:
                try:
                    # 获取变体名称
                    variant_name = self.path_manager.get_vscode_variant_name(vscode_dir)
                    if variant_name not in results["variants_found"]:
                        results["variants_found"].append(variant_name)
                    
                    # 处理设备ID文件
                    storage_result = self._process_storage_files(
                        vscode_dir, create_backups, lock_files
                    )
                    
                    if storage_result["success"]:
                        results["directories_processed"] += 1
                        results["files_processed"].extend(storage_result["files_processed"])
                        results["backups_created"].extend(storage_result["backups_created"])
                        results["old_ids"].update(storage_result["old_ids"])
                        results["new_ids"].update(storage_result["new_ids"])
                    else:
                        results["directories_failed"] += 1
                        results["files_failed"].extend(storage_result["files_failed"])
                        results["errors"].extend(storage_result["errors"])
                    
                    # 清理工作区（如果需要）
                    if clean_workspace:
                        workspace_result = self._clean_workspace_storage(vscode_dir, create_backups)
                        results["workspace_cleaned"] += workspace_result["cleaned_count"]
                    
                    # 清理缓存（如果需要）
                    if clean_cache:
                        cache_result = self._clean_cache_directories(vscode_dir.parent, create_backups)
                        results["cache_cleaned"] += cache_result["cleaned_count"]
                        
                except Exception as e:
                    error_msg = f"Error processing {vscode_dir}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    results["directories_failed"] += 1
            
            # 判断整体成功
            if results["directories_processed"] > 0:
                results["success"] = True
                logger.info(f"Successfully processed {results['directories_processed']} VSCode directories")
            
        except Exception as e:
            error_msg = f"VSCode processing failed: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    def _process_storage_files(self, vscode_dir: Path, create_backups: bool, 
                              lock_files: bool) -> Dict[str, Any]:
        """
        处理存储文件（storage.json 和 state.vscdb）
        
        Args:
            vscode_dir: VSCode 目录路径
            create_backups: 是否创建备份
            lock_files: 是否锁定文件
            
        Returns:
            处理结果字典
        """
        result = {
            "success": False,
            "files_processed": [],
            "files_failed": [],
            "backups_created": [],
            "old_ids": {},
            "new_ids": {},
            "errors": []
        }
        
        try:
            # 处理 storage.json
            storage_file = vscode_dir / "storage.json"
            if storage_file.exists():
                storage_result = self._process_storage_json(storage_file, create_backups, lock_files)
                if storage_result["success"]:
                    result["files_processed"].append(str(storage_file))
                    result["old_ids"].update(storage_result["old_ids"])
                    result["new_ids"].update(storage_result["new_ids"])
                    if storage_result["backup_path"]:
                        result["backups_created"].append(storage_result["backup_path"])
                else:
                    result["files_failed"].append(str(storage_file))
                    result["errors"].extend(storage_result["errors"])
            
            # 处理 state.vscdb
            db_file = vscode_dir / "state.vscdb"
            if db_file.exists():
                db_result = self._process_state_database(db_file, create_backups, lock_files)
                if db_result["success"]:
                    result["files_processed"].append(str(db_file))
                    result["old_ids"].update(db_result["old_ids"])
                    result["new_ids"].update(db_result["new_ids"])
                    if db_result["backup_path"]:
                        result["backups_created"].append(db_result["backup_path"])
                else:
                    result["files_failed"].append(str(db_file))
                    result["errors"].extend(db_result["errors"])
            
            # 判断成功
            if result["files_processed"]:
                result["success"] = True
                
        except Exception as e:
            error_msg = f"Storage processing failed: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        return result
    
    def _process_storage_json(self, storage_file: Path, create_backups: bool, 
                             lock_files: bool) -> Dict[str, Any]:
        """
        处理 storage.json 文件
        
        Args:
            storage_file: storage.json 文件路径
            create_backups: 是否创建备份
            lock_files: 是否锁定文件
            
        Returns:
            处理结果字典
        """
        result = {
            "success": False,
            "backup_path": None,
            "old_ids": {},
            "new_ids": {},
            "errors": []
        }
        
        try:
            # 创建备份
            if create_backups:
                backup_path = self.backup_manager.create_file_backup(storage_file)
                if backup_path:
                    result["backup_path"] = str(backup_path)
                    logger.info(f"Created backup: {backup_path}")
            
            # 读取现有数据
            with open(storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理设备ID
            modified = False
            for key in VSCODE_CONFIG["telemetry_keys"]:
                if key in data:
                    old_value = data[key]
                    new_value = self.id_generator.generate_device_id()
                    data[key] = new_value
                    result["old_ids"][key] = old_value
                    result["new_ids"][key] = new_value
                    modified = True
                    logger.info(f"Updated {key}: {old_value} -> {new_value}")
            
            # 写入修改后的数据
            if modified:
                # 移除只读属性
                if storage_file.exists():
                    storage_file.chmod(stat.S_IWRITE | stat.S_IREAD)
                
                with open(storage_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # 锁定文件（如果需要）
                if lock_files:
                    storage_file.chmod(stat.S_IREAD)
                    logger.info(f"Locked file: {storage_file}")
                
                result["success"] = True
                logger.info(f"Successfully processed storage.json: {storage_file}")
            else:
                logger.info(f"No telemetry keys found in {storage_file}")
                result["success"] = True
                
        except Exception as e:
            error_msg = f"Failed to process storage.json: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        return result

    def _process_state_database(self, db_file: Path, create_backups: bool,
                               lock_files: bool) -> Dict[str, Any]:
        """
        处理 state.vscdb 数据库文件

        Args:
            db_file: 数据库文件路径
            create_backups: 是否创建备份
            lock_files: 是否锁定文件

        Returns:
            处理结果字典
        """
        result = {
            "success": False,
            "backup_path": None,
            "old_ids": {},
            "new_ids": {},
            "errors": []
        }

        try:
            # 创建备份
            if create_backups:
                backup_path = self.backup_manager.create_file_backup(db_file)
                if backup_path:
                    result["backup_path"] = str(backup_path)
                    logger.info(f"Created backup: {backup_path}")

            # 移除只读属性
            if db_file.exists():
                db_file.chmod(stat.S_IWRITE | stat.S_IREAD)

            # 连接数据库
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()

            try:
                # 查找包含设备ID的记录
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                modified = False
                for table_name, in tables:
                    try:
                        # 获取表结构
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()

                        # 查找文本列
                        text_columns = [col[1] for col in columns if col[2].upper() in ['TEXT', 'VARCHAR', 'CHAR']]

                        for column in text_columns:
                            for key in VSCODE_CONFIG["telemetry_keys"]:
                                # 查找包含设备ID的记录
                                cursor.execute(f"SELECT rowid, {column} FROM {table_name} WHERE {column} LIKE ?", (f'%{key}%',))
                                rows = cursor.fetchall()

                                for rowid, value in rows:
                                    if key in str(value):
                                        # 生成新的设备ID
                                        new_id = self.id_generator.generate_device_id()
                                        new_value = str(value).replace(str(value), new_id)

                                        # 更新记录
                                        cursor.execute(f"UPDATE {table_name} SET {column} = ? WHERE rowid = ?", (new_value, rowid))

                                        result["old_ids"][f"{table_name}.{column}"] = value
                                        result["new_ids"][f"{table_name}.{column}"] = new_value
                                        modified = True

                                        logger.info(f"Updated {table_name}.{column}: {value} -> {new_value}")

                    except sqlite3.Error as e:
                        logger.warning(f"Could not process table {table_name}: {e}")
                        continue

                # 提交更改
                if modified:
                    conn.commit()
                    logger.info(f"Successfully updated database: {db_file}")

                result["success"] = True

            finally:
                cursor.close()
                conn.close()

            # 锁定文件（如果需要）
            if lock_files:
                db_file.chmod(stat.S_IREAD)
                logger.info(f"Locked file: {db_file}")

        except Exception as e:
            error_msg = f"Failed to process state database: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    def _clean_workspace_storage(self, vscode_dir: Path, create_backups: bool) -> Dict[str, Any]:
        """
        精确清理工作区存储 - 只清理AugmentCode相关记录，保护其他插件配置

        Args:
            vscode_dir: VSCode 目录路径
            create_backups: 是否创建备份

        Returns:
            清理结果字典
        """
        result = {
            "success": False,
            "cleaned_count": 0,
            "projects_processed": 0,
            "records_deleted": 0,
            "errors": []
        }

        try:
            workspace_dir = vscode_dir.parent / "workspaceStorage"
            if not workspace_dir.exists():
                logger.info(f"Workspace storage directory does not exist: {workspace_dir}")
                result["success"] = True
                return result

            logger.info(f"Starting precise workspace cleaning: {workspace_dir}")

            # 遍历每个项目目录
            for project_dir in workspace_dir.iterdir():
                if not project_dir.is_dir():
                    continue

                try:
                    result["projects_processed"] += 1
                    project_cleaned = False

                    # 1. 清理项目数据库中的AugmentCode记录
                    project_db = project_dir / "state.vscdb"
                    if project_db.exists():
                        if create_backups:
                            backup_path = self.backup_manager.create_file_backup(project_db, f"workspace_{project_dir.name}")
                            if backup_path:
                                logger.debug(f"Created project DB backup: {backup_path}")

                        records_deleted = self._clean_project_database(project_db)
                        if records_deleted > 0:
                            result["records_deleted"] += records_deleted
                            project_cleaned = True
                            logger.info(f"Cleaned {records_deleted} AugmentCode records from project {project_dir.name}")

                    # 2. 清理AugmentCode插件专用目录（如果存在）
                    augment_dirs = [
                        project_dir / "augmentcode.augment",
                        project_dir / "augmentcode",
                        project_dir / "augment"
                    ]

                    for augment_dir in augment_dirs:
                        if augment_dir.exists() and augment_dir.is_dir():
                            try:
                                if create_backups:
                                    backup_path = self.backup_manager.create_directory_backup(augment_dir)
                                    if backup_path:
                                        logger.debug(f"Created AugmentCode dir backup: {backup_path}")

                                shutil.rmtree(augment_dir)
                                project_cleaned = True
                                logger.info(f"Removed AugmentCode directory: {augment_dir}")
                            except Exception as e:
                                logger.warning(f"Could not remove AugmentCode directory {augment_dir}: {e}")

                    # 3. 清理AugmentCode相关的配置文件
                    augment_files = [
                        project_dir / "augment.json",
                        project_dir / "augmentcode.json",
                        project_dir / ".augment"
                    ]

                    for augment_file in augment_files:
                        if augment_file.exists():
                            try:
                                if create_backups:
                                    backup_path = self.backup_manager.create_file_backup(augment_file)
                                    if backup_path:
                                        logger.debug(f"Created AugmentCode file backup: {backup_path}")

                                augment_file.unlink()
                                project_cleaned = True
                                logger.info(f"Removed AugmentCode file: {augment_file}")
                            except Exception as e:
                                logger.warning(f"Could not remove AugmentCode file {augment_file}: {e}")

                    if project_cleaned:
                        result["cleaned_count"] += 1

                except Exception as e:
                    logger.warning(f"Error processing project directory {project_dir}: {e}")
                    result["errors"].append(f"Project {project_dir.name}: {str(e)}")

            logger.info(f"Workspace cleaning completed: {result['cleaned_count']} projects cleaned, "
                       f"{result['records_deleted']} records deleted from {result['projects_processed']} projects")
            result["success"] = True

        except Exception as e:
            error_msg = f"Workspace cleaning failed: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    def _clean_project_database(self, project_db: Path) -> int:
        """
        精确清理项目数据库中的AugmentCode记录

        Args:
            project_db: 项目数据库文件路径

        Returns:
            删除的记录数量
        """
        records_deleted = 0

        try:
            # 检查是否为有效的SQLite数据库
            if not self._is_valid_sqlite_database(project_db):
                logger.debug(f"Skipping non-SQLite file: {project_db}")
                return 0

            conn = sqlite3.connect(str(project_db))
            cursor = conn.cursor()

            try:
                # 检查ItemTable是否存在
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ItemTable'")
                if not cursor.fetchone():
                    logger.debug(f"No ItemTable found in {project_db}")
                    return 0

                # AugmentCode相关的清理模式
                augment_patterns = [
                    '%augment%',           # AugmentCode相关
                    '%Augment%',           # 大写变体
                    '%AUGMENT%',           # 全大写
                    '%cursor.com%',        # Cursor域名相关
                    '%workos%',            # WorkOS认证服务
                    '%oauth%',             # OAuth状态
                    '%auth%',              # 认证状态
                    '%session%',           # 会话状态
                    '%token%',             # 令牌
                    '%login%'              # 登录状态
                ]

                # 精确删除匹配的记录
                for pattern in augment_patterns:
                    cursor.execute("SELECT COUNT(*) FROM ItemTable WHERE key LIKE ?", (pattern,))
                    count = cursor.fetchone()[0]

                    if count > 0:
                        cursor.execute("DELETE FROM ItemTable WHERE key LIKE ?", (pattern,))
                        records_deleted += count
                        logger.debug(f"Deleted {count} records matching pattern {pattern}")

                # 提交更改
                if records_deleted > 0:
                    conn.commit()
                    logger.debug(f"Successfully deleted {records_deleted} AugmentCode records from {project_db}")

            finally:
                cursor.close()
                conn.close()

        except sqlite3.Error as e:
            logger.warning(f"SQLite error cleaning project database {project_db}: {e}")
        except Exception as e:
            logger.warning(f"Error cleaning project database {project_db}: {e}")

        return records_deleted

    def _is_valid_sqlite_database(self, db_file: Path) -> bool:
        """
        检查文件是否为有效的SQLite数据库

        Args:
            db_file: 数据库文件路径

        Returns:
            True if valid SQLite database, False otherwise
        """
        try:
            # SQLite文件以"SQLite format 3\000"开头
            with open(db_file, 'rb') as f:
                header = f.read(16)
                return header.startswith(b'SQLite format 3\x00')
        except (OSError, IOError):
            return False

    def _clean_cache_directories(self, vscode_root: Path, create_backups: bool) -> Dict[str, Any]:
        """
        清理缓存目录

        Args:
            vscode_root: VSCode 根目录路径
            create_backups: 是否创建备份

        Returns:
            清理结果字典
        """
        result = {
            "success": False,
            "cleaned_count": 0,
            "errors": []
        }

        try:
            cache_dirs = ["CachedExtensions", "CachedData", "logs", "GPUCache", "Service Worker"]

            for cache_dir_name in cache_dirs:
                cache_dir = vscode_root / cache_dir_name
                if cache_dir.exists():
                    try:
                        if create_backups:
                            backup_path = self.backup_manager.create_directory_backup(cache_dir)
                            if backup_path:
                                logger.info(f"Created cache backup: {backup_path}")

                        # 清理缓存目录
                        if cache_dir.is_dir():
                            shutil.rmtree(cache_dir)
                            result["cleaned_count"] += 1
                            logger.info(f"Cleaned cache directory: {cache_dir}")

                    except Exception as e:
                        logger.warning(f"Could not clean cache {cache_dir}: {e}")
                        result["errors"].append(f"Cache {cache_dir_name}: {str(e)}")

            result["success"] = True

        except Exception as e:
            error_msg = f"Cache cleaning failed: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    def verify_vscode_installation(self) -> Dict[str, Any]:
        """
        验证 VSCode 安装并返回信息

        Returns:
            安装信息字典
        """
        info = {
            "installed": False,
            "variants_found": [],
            "total_directories": 0,
            "storage_files": [],
            "database_files": [],
            "missing_files": [],
            "storage_directories": []
        }

        try:
            # 获取 VSCode 目录
            vscode_dirs = self.path_manager.get_vscode_directories()
            if vscode_dirs:
                info["installed"] = True
                info["total_directories"] = len(vscode_dirs)
                info["storage_directories"] = [str(vscode_dir) for vscode_dir in vscode_dirs]

                # 检查每个目录
                for vscode_dir in vscode_dirs:
                    variant_name = self.path_manager.get_vscode_variant_name(vscode_dir)
                    if variant_name not in info["variants_found"]:
                        info["variants_found"].append(variant_name)

                    # 检查存储文件
                    storage_file = vscode_dir / "storage.json"
                    if storage_file.exists():
                        info["storage_files"].append(str(storage_file))
                    else:
                        info["missing_files"].append(str(storage_file))

                    # 检查数据库文件
                    db_file = vscode_dir / "state.vscdb"
                    if db_file.exists():
                        info["database_files"].append(str(db_file))
                    else:
                        info["missing_files"].append(str(db_file))

        except Exception as e:
            logger.error(f"Error verifying VSCode installation: {e}")
            info["error"] = str(e)

        return info

    def get_current_device_ids(self) -> Dict[str, Any]:
        """
        获取当前的设备ID

        Returns:
            设备ID信息字典
        """
        ids = {
            "storage_ids": {},
            "database_ids": {},
            "errors": []
        }

        try:
            vscode_dirs = self.path_manager.get_vscode_directories()

            for vscode_dir in vscode_dirs:
                variant_name = vscode_dir.parent.name

                # 读取 storage.json 中的ID
                storage_file = vscode_dir / "storage.json"
                if storage_file.exists():
                    try:
                        with open(storage_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        storage_ids = {}
                        for key in VSCODE_CONFIG["telemetry_keys"]:
                            if key in data:
                                storage_ids[key] = data[key]

                        if storage_ids:
                            ids["storage_ids"][variant_name] = storage_ids

                    except Exception as e:
                        ids["errors"].append(f"Error reading {storage_file}: {str(e)}")

                # 读取数据库中的ID（简化版本）
                db_file = vscode_dir / "state.vscdb"
                if db_file.exists():
                    try:
                        conn = sqlite3.connect(str(db_file))
                        cursor = conn.cursor()

                        # 查找包含设备ID的记录（简化查询）
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = cursor.fetchall()

                        db_ids = {}
                        for table_name, in tables[:3]:  # 限制查询表数量
                            try:
                                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                                rows = cursor.fetchall()
                                for row in rows:
                                    for value in row:
                                        if isinstance(value, str):
                                            for key in VSCODE_CONFIG["telemetry_keys"]:
                                                if key in value:
                                                    db_ids[f"{table_name}"] = value[:100]  # 截断长值
                                                    break
                            except:
                                continue

                        if db_ids:
                            ids["database_ids"][variant_name] = db_ids

                        cursor.close()
                        conn.close()

                    except Exception as e:
                        ids["errors"].append(f"Error reading {db_file}: {str(e)}")

        except Exception as e:
            ids["errors"].append(f"Error getting device IDs: {str(e)}")

        return ids

    def get_current_vscode_ids(self):
        """
        获取当前VSCode/Cursor的设备ID信息

        Returns:
            Dict[str, Dict]: 包含各个VSCode变体的ID信息
        """
        result = {}

        try:
            # 获取所有VSCode目录
            vscode_dirs = self.path_manager.get_vscode_directories()

            for vscode_dir in vscode_dirs:
                variant_name = self._get_variant_name_from_path(str(vscode_dir))

                # 只处理globalStorage目录
                if 'globalStorage' in str(vscode_dir):
                    variant_ids = {}

                    # 检查storage.json文件
                    storage_file = vscode_dir / "storage.json"
                    if storage_file.exists():
                        try:
                            with open(storage_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)

                            # 提取遥测ID
                            telemetry_keys = [
                                'telemetry.machineId',
                                'telemetry.devDeviceId',
                                'telemetry.macMachineId',
                                'telemetry.sqmId'
                            ]

                            for key in telemetry_keys:
                                if key in data:
                                    variant_ids[key] = data[key]

                        except Exception as e:
                            logger.warning(f"Could not read storage.json for {variant_name}: {e}")

                    # 检查machineId文件
                    machine_id_file = vscode_dir.parent / "machineId"
                    if machine_id_file.exists():
                        try:
                            with open(machine_id_file, 'r', encoding='utf-8') as f:
                                machine_id = f.read().strip()
                            variant_ids['machineId'] = machine_id
                        except Exception as e:
                            logger.warning(f"Could not read machineId for {variant_name}: {e}")

                    if variant_ids:
                        result[variant_name] = variant_ids

        except Exception as e:
            logger.error(f"Failed to get VSCode IDs: {e}")

        return result

    def _get_variant_name_from_path(self, path_str):
        """从路径获取VSCode变体名称"""
        if 'Cursor' in path_str:
            return 'Cursor'
        elif 'Code - Insiders' in path_str:
            return 'VSCode Insiders'
        elif 'Code' in path_str:
            return 'VSCode'
        elif 'VSCodium' in path_str:
            return 'VSCodium'
        else:
            return 'Unknown VSCode Variant'
