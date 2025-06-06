"""
Backup management utilities for safe file operations
"""

import os
import shutil
import time
import zipfile
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

from config.settings import BACKUP_CONFIG

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages backup operations for files and directories"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize backup manager

        Args:
            backup_dir: Custom backup directory (optional)
        """
        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            # Default backup directory in project directory to avoid permission issues
            try:
                # Try user's home directory first
                self.backup_dir = Path.home() / ".augment_cleaner_backups"
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                # Test write permission
                test_file = self.backup_dir / "test_write.tmp"
                test_file.write_text("test")
                test_file.unlink()
            except (PermissionError, OSError):
                # Fallback to project directory if home directory has permission issues
                project_root = Path(__file__).parent.parent
                self.backup_dir = project_root / "backups"
                logger.warning("Using project directory for backups due to permission issues")

        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Backup directory: {self.backup_dir}")
    
    def create_file_backup(self, file_path: Path, backup_name: Optional[str] = None) -> Optional[Path]:
        """
        Create a backup of a single file
        
        Args:
            file_path: Path to file to backup
            backup_name: Custom backup name (optional)
            
        Returns:
            Path to backup file or None if backup failed
        """
        if not file_path.exists():
            logger.warning(f"File does not exist, cannot backup: {file_path}")
            return None
        
        try:
            # Generate backup filename
            timestamp = time.strftime(BACKUP_CONFIG["timestamp_format"])
            if backup_name:
                backup_filename = f"{backup_name}_{timestamp}{BACKUP_CONFIG['backup_extension']}"
            else:
                backup_filename = f"{file_path.name}_{timestamp}{BACKUP_CONFIG['backup_extension']}"
            
            backup_path = self.backup_dir / backup_filename
            
            # Copy file to backup location
            shutil.copy2(file_path, backup_path)
            
            logger.info(f"Created backup: {file_path} -> {backup_path}")
            return backup_path
            
        except (OSError, IOError) as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return None
    
    def create_directory_backup(self, dir_path: Path, backup_name: Optional[str] = None) -> Optional[Path]:
        """
        Create a compressed backup of a directory
        
        Args:
            dir_path: Path to directory to backup
            backup_name: Custom backup name (optional)
            
        Returns:
            Path to backup zip file or None if backup failed
        """
        if not dir_path.exists() or not dir_path.is_dir():
            logger.warning(f"Directory does not exist, cannot backup: {dir_path}")
            return None
        
        try:
            # Generate backup filename
            timestamp = time.strftime(BACKUP_CONFIG["timestamp_format"])
            if backup_name:
                backup_filename = f"{backup_name}_{timestamp}.zip"
            else:
                backup_filename = f"{dir_path.name}_{timestamp}.zip"
            
            backup_path = self.backup_dir / backup_filename
            
            # Create zip backup
            failed_files = []
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file():
                        try:
                            # Calculate relative path for archive
                            arcname = file_path.relative_to(dir_path)
                            zipf.write(file_path, str(arcname))
                        except (OSError, PermissionError, zipfile.BadZipFile) as e:
                            failed_files.append({
                                'file': str(file_path),
                                'error': str(e)
                            })
                            logger.warning(f"Failed to backup file {file_path}: {e}")
            
            if failed_files:
                # Save failed files list
                failed_files_path = backup_path.with_suffix('.failed.json')
                with open(failed_files_path, 'w', encoding='utf-8') as f:
                    json.dump(failed_files, f, indent=2)
                logger.warning(f"Some files failed to backup, see: {failed_files_path}")
            
            logger.info(f"Created directory backup: {dir_path} -> {backup_path}")
            return backup_path
            
        except (OSError, IOError, zipfile.BadZipFile) as e:
            logger.error(f"Failed to create directory backup for {dir_path}: {e}")
            return None
    
    def create_json_backup(self, data: Dict[str, Any], backup_name: str) -> Optional[Path]:
        """
        Create a backup of JSON data
        
        Args:
            data: Data to backup
            backup_name: Name for the backup file
            
        Returns:
            Path to backup file or None if backup failed
        """
        try:
            timestamp = time.strftime(BACKUP_CONFIG["timestamp_format"])
            backup_filename = f"{backup_name}_{timestamp}.json"
            backup_path = self.backup_dir / backup_filename
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created JSON backup: {backup_path}")
            return backup_path
            
        except (OSError, IOError, json.JSONEncodeError) as e:
            logger.error(f"Failed to create JSON backup '{backup_name}': {e}")
            return None
    
    def restore_file_backup(self, backup_path: Path, target_path: Path) -> bool:
        """
        Restore a file from backup

        Args:
            backup_path: Path to backup file
            target_path: Path where to restore the file

        Returns:
            True if restore was successful, False otherwise
        """
        if not backup_path.exists():
            logger.error(f"Backup file does not exist: {backup_path}")
            return False

        try:
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy backup to target location
            shutil.copy2(backup_path, target_path)

            logger.info(f"Restored backup: {backup_path} -> {target_path}")
            return True

        except (OSError, IOError) as e:
            logger.error(f"Failed to restore backup {backup_path} to {target_path}: {e}")
            return False

    def auto_restore_backup(self, backup_name_pattern: str) -> Dict[str, Any]:
        """
        Automatically restore the most recent backup matching a pattern

        Args:
            backup_name_pattern: Pattern to match backup files

        Returns:
            Dictionary with restore results
        """
        result = {
            "success": False,
            "restored_files": [],
            "failed_files": [],
            "error": None
        }

        try:
            # Find matching backups
            matching_backups = self.list_backups(backup_name_pattern)
            if not matching_backups:
                result["error"] = f"No backups found matching pattern: {backup_name_pattern}"
                return result

            # Get the most recent backup
            latest_backup = matching_backups[0]  # Already sorted by modification time

            # Try to determine original file path from backup name
            original_path = self._get_original_path_from_backup(latest_backup)
            if not original_path:
                result["error"] = f"Cannot determine original path for backup: {latest_backup.name}"
                return result

            # Restore the backup
            if self.restore_file_backup(latest_backup, original_path):
                result["success"] = True
                result["restored_files"].append({
                    "backup": str(latest_backup),
                    "target": str(original_path)
                })
                logger.info(f"Auto-restored backup: {latest_backup.name} -> {original_path}")
            else:
                result["failed_files"].append({
                    "backup": str(latest_backup),
                    "target": str(original_path),
                    "error": "Restore operation failed"
                })

        except Exception as e:
            result["error"] = f"Auto-restore failed: {str(e)}"
            logger.error(f"Auto-restore error: {e}")

        return result

    def _get_original_path_from_backup(self, backup_path: Path) -> Optional[Path]:
        """
        Try to determine the original file path from backup filename

        Args:
            backup_path: Path to backup file

        Returns:
            Original file path or None if cannot be determined
        """
        try:
            # Parse backup filename to extract original info
            # Format: {prefix}_{timestamp}.bak
            backup_name = backup_path.stem  # Remove .bak extension

            # Remove timestamp (format: YYYYMMDD_HHMMSS)
            import re
            timestamp_pattern = r'_\d{8}_\d{6}$'
            original_name = re.sub(timestamp_pattern, '', backup_name)

            # Map common backup prefixes to original paths
            from config.settings import get_platform_paths
            platform_paths = get_platform_paths()

            if original_name.startswith('jetbrains_'):
                # JetBrains ID files
                file_name = original_name.replace('jetbrains_', '')
                jetbrains_dir = Path(platform_paths["config"]) / "JetBrains"
                return jetbrains_dir / file_name

            elif original_name.startswith('vscode_storage_'):
                # VSCode storage files
                variant_name = original_name.replace('vscode_storage_', '')
                # This is more complex as we need to find the right VSCode variant
                # For now, return None to indicate manual restore needed
                return None

            elif original_name.startswith('vscode_machine_'):
                # VSCode machine ID files
                return None  # Complex path resolution needed

            else:
                # Unknown backup type
                return None

        except Exception as e:
            logger.warning(f"Could not determine original path for {backup_path}: {e}")
            return None
    
    def list_backups(self, pattern: Optional[str] = None) -> List[Path]:
        """
        List available backup files
        
        Args:
            pattern: Optional pattern to filter backups
            
        Returns:
            List of backup file paths
        """
        try:
            if pattern:
                backups = list(self.backup_dir.glob(f"*{pattern}*"))
            else:
                backups = list(self.backup_dir.glob("*"))
            
            # Filter only files and sort by modification time (newest first)
            backups = [b for b in backups if b.is_file()]
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return backups
            
        except OSError as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def cleanup_old_backups(self, max_backups: Optional[int] = None) -> int:
        """
        Clean up old backup files, keeping only the most recent ones
        
        Args:
            max_backups: Maximum number of backups to keep (uses config default if None)
            
        Returns:
            Number of backups deleted
        """
        if max_backups is None:
            max_backups = BACKUP_CONFIG["max_backups"]
        
        backups = self.list_backups()
        
        if len(backups) <= max_backups:
            return 0
        
        # Delete oldest backups
        backups_to_delete = backups[max_backups:]
        deleted_count = 0
        
        for backup_path in backups_to_delete:
            try:
                backup_path.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old backup: {backup_path}")
            except OSError as e:
                logger.warning(f"Failed to delete old backup {backup_path}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old backup files")
        
        return deleted_count
    
    def get_backup_info(self, backup_path: Path) -> Dict[str, Any]:
        """
        Get information about a backup file
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Dictionary with backup information
        """
        if not backup_path.exists():
            return {}
        
        try:
            stat = backup_path.stat()
            return {
                "path": str(backup_path),
                "size": stat.st_size,
                "created": time.ctime(stat.st_ctime),
                "modified": time.ctime(stat.st_mtime),
                "is_compressed": backup_path.suffix.lower() == '.zip',
            }
        except OSError as e:
            logger.error(f"Failed to get backup info for {backup_path}: {e}")
            return {}
    
    def verify_backup_integrity(self, backup_path: Path) -> bool:
        """
        Verify the integrity of a backup file
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if backup is valid, False otherwise
        """
        if not backup_path.exists():
            return False
        
        try:
            if backup_path.suffix.lower() == '.zip':
                # Verify zip file integrity
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    # Test the zip file
                    zipf.testzip()
                return True
            elif backup_path.suffix.lower() == '.json':
                # Verify JSON file integrity
                with open(backup_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                return True
            else:
                # For other files, just check if readable
                with open(backup_path, 'rb') as f:
                    f.read(1024)  # Read first 1KB to test
                return True
                
        except (OSError, IOError, zipfile.BadZipFile, json.JSONDecodeError) as e:
            logger.error(f"Backup integrity check failed for {backup_path}: {e}")
            return False
