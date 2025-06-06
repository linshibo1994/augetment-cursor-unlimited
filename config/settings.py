"""
Configuration settings for Augment Unlimited
"""

import os
import sys
from pathlib import Path

# Version information
VERSION = "2.0.0"
APP_NAME = "Augment Unlimited"

# Default settings
DEFAULT_SETTINGS = {
    "create_backups": True,
    "lock_files": True,
    "clean_database": True,
    "clean_workspace": True,
    "verbose": False,
    "force_delete": True,
}

# JetBrains configuration
JETBRAINS_CONFIG = {
    "id_files": [
        "PermanentDeviceId",  # Base64: UGVybWFuZW50RGV2aWNlSWQ=
        "PermanentUserId",    # Base64: UGVybWFuZW50VXNlcklk
    ],
    # Base64编码的文件名 (augment-vip兼容)
    "id_files_encoded": [
        "UGVybWFuZW50RGV2aWNlSWQ=",  # PermanentDeviceId
        "UGVybWFuZW50VXNlcklk",      # PermanentUserId
    ],
    "config_dirs": [
        "JetBrains",
    ],
    "database_files": [
        "app-internal-state.db",
        "updatedBrokenPlugins.db",
        "statistics.db",
        "usage.db",
        "device.db",
    ],
    "database_patterns": [
        "*.db",
        "*.sqlite",
        "*.sqlite3",
    ],
    "augment_patterns": [
        "%augment%",
        "%Augment%",
        "%AUGMENT%",
        "%device%",
        "%user%",
        "%machine%",
        "%telemetry%",
    ],
    "cache_dirs": [
        "caches",
        "logs",
        "system",
        "temp",
    ]
}

# VSCode configuration
VSCODE_CONFIG = {
    "telemetry_keys": [
        "telemetry.machineId",      # Base64: dGVsZW1ldHJ5Lm1hY2hpbmVJZA==
        "telemetry.devDeviceId",    # Base64: dGVsZW1ldHJ5LmRldkRldmljZUlk
        "telemetry.macMachineId",   # Base64: dGVsZW1ldHJ5Lm1hY01hY2hpbmVJZA==
        "telemetry.sqmId",          # Base64: dGVsZW1ldHJ5LnNxbUlk (缺失字段)
    ],
    "storage_patterns": {
        "global": [
            ["User", "globalStorage"],
            ["data", "User", "globalStorage"],
        ],
        "workspace": [
            ["User", "workspaceStorage"],
            ["data", "User", "workspaceStorage"],
        ],
        "machine_id": [
            ["User"],
            ["data"],
        ]
    },
    "vscode_variants": [
        "Code",
        "Code - Insiders",
        "VSCodium",
        "Cursor",
        "code-server",
    ],
    "database_files": [
        "state.vscdb",
        "state.vscdb.backup",
    ],
    "service_worker_patterns": [
        ["User", "CachedExtensions"],
        ["User", "logs"],
        ["User", "CachedData"],
        ["CachedData"],
        ["logs"],
    ],
    "cache_directories": [
        "CachedExtensions",
        "CachedData",
        "logs",
        "GPUCache",
        "Service Worker",
    ]
}

# Database configuration
DATABASE_CONFIG = {
    "augment_patterns": [
        "%augment%",
        "%Augment%",
        "%AUGMENT%",
    ],
    "queries": {
        "count": "SELECT COUNT(*) FROM ItemTable WHERE key LIKE ?",
        "delete": "DELETE FROM ItemTable WHERE key LIKE ?",
    },
    # 精确的augment-vip兼容查询
    "precise_queries": {
        "count_augment": "SELECT COUNT(*) FROM ItemTable WHERE key LIKE '%augment%'",
        "delete_augment": "DELETE FROM ItemTable WHERE key LIKE '%augment%'",
    }
}

# Platform-specific paths
def get_platform_paths():
    """Get platform-specific base directories"""
    if sys.platform == "win32":
        return {
            "config": os.getenv("APPDATA", ""),
            "data": os.getenv("LOCALAPPDATA", ""),
            "home": Path.home(),
        }
    elif sys.platform == "darwin":
        return {
            "config": Path.home() / "Library" / "Application Support",
            "data": Path.home() / "Library" / "Application Support",
            "home": Path.home(),
        }
    else:  # Linux and other Unix-like systems
        return {
            "config": Path.home() / ".config",
            "data": Path.home() / ".local" / "share",
            "home": Path.home(),
        }

# Backup configuration
BACKUP_CONFIG = {
    "timestamp_format": "%Y%m%d_%H%M%S",
    "backup_extension": ".bak",
    "max_backups": 10,  # Keep only the latest 10 backups
}

# Logging configuration
LOGGING_CONFIG = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "level": "INFO",
}

# File operation configuration
FILE_CONFIG = {
    "encoding": "utf-8",
    "chunk_size": 8192,  # For file operations
    "max_retries": 3,
    "retry_delay": 1,  # seconds
}

# Security settings
SECURITY_CONFIG = {
    "verify_paths": True,
    "safe_mode": True,  # Extra checks before destructive operations
    "confirm_destructive": False,  # Ask for confirmation for destructive operations
}

# Export all configurations
__all__ = [
    "VERSION",
    "APP_NAME",
    "DEFAULT_SETTINGS",
    "JETBRAINS_CONFIG",
    "VSCODE_CONFIG",
    "DATABASE_CONFIG",
    "BACKUP_CONFIG",
    "LOGGING_CONFIG",
    "FILE_CONFIG",
    "SECURITY_CONFIG",
    "get_platform_paths",
]
