"""
Path management utilities for cross-platform support
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from config.settings import get_platform_paths, VSCODE_CONFIG, JETBRAINS_CONFIG

logger = logging.getLogger(__name__)


class PathManager:
    """Manages paths for different IDEs and platforms"""
    
    def __init__(self):
        self.platform_paths = get_platform_paths()
        self._jetbrains_dirs = None
        self._vscode_dirs = None
        self._vscode_variant_map = {}  # 存储路径到变体名称的映射
        self._vscode_variant_map = {}  # 存储路径到变体名称的映射
    
    def get_jetbrains_config_dir(self) -> Optional[Path]:
        """
        Find JetBrains configuration directory across different platforms
        
        Returns:
            Path to JetBrains config directory or None if not found
        """
        if self._jetbrains_dirs is not None:
            return self._jetbrains_dirs
            
        base_dirs = [
            self.platform_paths["config"],
            self.platform_paths["data"], 
            self.platform_paths["home"],
        ]
        
        for base_dir in base_dirs:
            if not base_dir:
                continue
                
            base_path = Path(base_dir)
            jetbrains_path = base_path / "JetBrains"
            
            if jetbrains_path.exists() and jetbrains_path.is_dir():
                logger.info(f"Found JetBrains config directory: {jetbrains_path}")
                self._jetbrains_dirs = jetbrains_path
                return jetbrains_path
        
        logger.warning("JetBrains configuration directory not found")
        return None
    
    def get_jetbrains_id_files(self) -> List[Path]:
        """
        Get list of JetBrains ID files to modify
        
        Returns:
            List of Path objects for JetBrains ID files
        """
        jetbrains_dir = self.get_jetbrains_config_dir()
        if not jetbrains_dir:
            return []
        
        id_files = []
        for file_name in JETBRAINS_CONFIG["id_files"]:
            file_path = jetbrains_dir / file_name
            id_files.append(file_path)
            logger.debug(f"JetBrains ID file: {file_path}")
        
        return id_files

    def get_jetbrains_database_files(self) -> List[Path]:
        """
        Get list of JetBrains database files

        Returns:
            List of Path objects for JetBrains database files
        """
        db_files = []

        jetbrains_dir = self.get_jetbrains_config_dir()
        if jetbrains_dir and jetbrains_dir.exists():
            # 扫描所有子目录中的数据库文件
            for pattern in JETBRAINS_CONFIG["database_patterns"]:
                db_files.extend(jetbrains_dir.rglob(pattern))

            # 过滤出实际存在的文件
            db_files = [f for f in db_files if f.is_file()]
            logger.info(f"Found {len(db_files)} JetBrains database files")
            for db_file in db_files:
                logger.debug(f"JetBrains database file: {db_file}")

        return db_files

    def get_jetbrains_cache_dirs(self) -> List[Path]:
        """
        Get list of JetBrains cache directories

        Returns:
            List of Path objects for JetBrains cache directories
        """
        cache_dirs = []

        jetbrains_dir = self.get_jetbrains_config_dir()
        if jetbrains_dir and jetbrains_dir.exists():
            # 扫描缓存目录
            for cache_name in JETBRAINS_CONFIG["cache_dirs"]:
                cache_dirs.extend(jetbrains_dir.rglob(cache_name))

            # 过滤出实际存在的目录
            cache_dirs = [d for d in cache_dirs if d.is_dir()]
            logger.info(f"Found {len(cache_dirs)} JetBrains cache directories")
            for cache_dir in cache_dirs:
                logger.debug(f"JetBrains cache directory: {cache_dir}")

        return cache_dirs

    def get_vscode_directories(self) -> List[Path]:
        """
        Find all VSCode variant directories and their storage paths

        Returns:
            List of Path objects for VSCode storage directories
        """
        if self._vscode_dirs is not None:
            return self._vscode_dirs

        vscode_dirs = []

        # 直接查找已知的VSCode变体目录
        base_path = Path(self.platform_paths["config"])

        if not base_path.exists():
            logger.warning(f"Config directory does not exist: {base_path}")
            self._vscode_dirs = []
            return []

        # 检查每个VSCode变体
        for variant in VSCODE_CONFIG["vscode_variants"]:
            variant_path = base_path / variant

            if variant_path.exists() and variant_path.is_dir():
                logger.info(f"Found VSCode variant: {variant} at {variant_path}")

                # 查找存储目录
                storage_dirs = self._find_vscode_storage_dirs(variant_path)
                # 为每个存储目录记录变体信息
                for storage_dir in storage_dirs:
                    self._vscode_variant_map[str(storage_dir)] = variant
                vscode_dirs.extend(storage_dirs)

        # Remove duplicates while preserving mapping
        seen = set()
        unique_dirs = []
        for vscode_dir in vscode_dirs:
            dir_str = str(vscode_dir)
            if dir_str not in seen:
                seen.add(dir_str)
                unique_dirs.append(vscode_dir)

        vscode_dirs = sorted(unique_dirs, key=str)

        logger.info(f"Found {len(vscode_dirs)} VSCode storage directories")
        for vscode_dir in vscode_dirs:
            logger.debug(f"VSCode storage directory: {vscode_dir}")

        self._vscode_dirs = vscode_dirs
        return vscode_dirs

    def _find_vscode_storage_dirs(self, vscode_base: Path) -> List[Path]:
        """
        Find storage directories within a VSCode installation

        Args:
            vscode_base: Base VSCode directory

        Returns:
            List of storage directory paths
        """
        storage_dirs = []

        # Global storage patterns
        for pattern in VSCODE_CONFIG["storage_patterns"]["global"]:
            storage_path = vscode_base
            for segment in pattern:
                storage_path = storage_path / segment

            if storage_path.exists() and storage_path.is_dir():
                storage_dirs.append(storage_path)

        # Workspace storage patterns - enumerate subdirectories
        for pattern in VSCODE_CONFIG["storage_patterns"]["workspace"]:
            workspace_base = vscode_base
            for segment in pattern:
                workspace_base = workspace_base / segment

            if workspace_base.exists() and workspace_base.is_dir():
                try:
                    for workspace_dir in workspace_base.iterdir():
                        if workspace_dir.is_dir():
                            storage_dirs.append(workspace_dir)
                except (PermissionError, OSError) as e:
                    logger.warning(f"Cannot access workspace directory {workspace_base}: {e}")

        # Machine ID file patterns
        for pattern in VSCODE_CONFIG["storage_patterns"]["machine_id"]:
            machine_id_base = vscode_base
            for segment in pattern:
                machine_id_base = machine_id_base / segment

            machine_id_file = machine_id_base / "machineId"
            if machine_id_file.exists():
                storage_dirs.append(machine_id_file)

        return storage_dirs

    def get_vscode_variant_name(self, storage_dir: Path) -> str:
        """
        获取VSCode存储目录对应的变体名称

        Args:
            storage_dir: VSCode存储目录

        Returns:
            变体名称 (Code, Cursor等)
        """
        return self._vscode_variant_map.get(str(storage_dir), 'Unknown')

    def get_vscode_storage_file(self, storage_dir: Path) -> Optional[Path]:
        """
        Get storage.json file path for a VSCode storage directory

        Args:
            storage_dir: VSCode storage directory

        Returns:
            Path to storage.json file or None if not found
        """
        if storage_dir.is_file():
            # This is likely a machineId file
            return storage_dir

        storage_file = storage_dir / "storage.json"
        if storage_file.exists():
            return storage_file

        return None

    def get_vscode_database_file(self, storage_dir: Path) -> Optional[Path]:
        """
        Get database file path for a VSCode storage directory

        Args:
            storage_dir: VSCode storage directory

        Returns:
            Path to database file or None if not found
        """
        if storage_dir.is_file():
            # This is not a directory, skip database check
            return None

        for db_file in VSCODE_CONFIG["database_files"]:
            db_path = storage_dir / db_file
            if db_path.exists():
                return db_path

        return None

    def get_workspace_storage_path(self) -> Optional[Path]:
        """
        Get the main workspace storage path for cleaning

        Returns:
            Path to workspace storage directory or None if not found
        """
        base_path = Path(self.platform_paths["config"])

        for variant in VSCODE_CONFIG["vscode_variants"]:
            for pattern in VSCODE_CONFIG["storage_patterns"]["workspace"]:
                workspace_path = base_path / variant
                for segment in pattern:
                    workspace_path = workspace_path / segment

                if workspace_path.exists() and workspace_path.is_dir():
                    logger.info(f"Found workspace storage: {workspace_path}")
                    return workspace_path

        logger.warning("Workspace storage directory not found")
        return None

    @staticmethod
    def ensure_long_path_support(path: Path) -> str:
        """
        Ensure long path support on Windows

        Args:
            path: Path object

        Returns:
            String path with long path prefix if needed
        """
        if sys.platform == "win32":
            path_str = str(path.resolve())
            if len(path_str) > 260 and not path_str.startswith("\\\\?\\"):
                return f"\\\\?\\{path_str}"
            return path_str
        return str(path)

    def validate_path(self, path: Path) -> bool:
        """
        Validate that a path is safe to operate on

        Args:
            path: Path to validate

        Returns:
            True if path is safe, False otherwise
        """
        try:
            # Convert to absolute path
            abs_path = path.resolve()

            # Check if path exists
            if not abs_path.exists():
                return False

            # Check if path is within expected directories
            platform_paths = self.platform_paths
            safe_bases = [
                Path(platform_paths["config"]),
                Path(platform_paths["data"]),
                Path(platform_paths["home"]),
            ]

            for safe_base in safe_bases:
                try:
                    abs_path.relative_to(safe_base.resolve())
                    return True
                except ValueError:
                    continue

            logger.warning(f"Path {abs_path} is not within safe directories")
            return False

        except (OSError, ValueError) as e:
            logger.error(f"Error validating path {path}: {e}")
            return False
