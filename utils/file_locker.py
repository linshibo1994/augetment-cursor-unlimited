"""
File locking utilities for protecting modified files
"""

import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class FileLockManager:
    """Manages file locking operations across different platforms"""
    
    @staticmethod
    def lock_file(file_path: Path) -> bool:
        """
        Lock a file to prevent modification
        
        Args:
            file_path: Path to file to lock
            
        Returns:
            True if file was successfully locked, False otherwise
        """
        if not file_path.exists():
            logger.error(f"Cannot lock file that doesn't exist: {file_path}")
            return False
        
        try:
            logger.info(f"Locking file: {file_path}")
            
            # Use platform-specific locking methods
            success = False
            
            if sys.platform == "win32":
                success = FileLockManager._lock_file_windows(file_path)
            elif sys.platform == "darwin":
                success = FileLockManager._lock_file_macos(file_path)
            else:
                success = FileLockManager._lock_file_linux(file_path)
            
            # Always ensure file is read-only using Python API as fallback
            try:
                perms = file_path.stat().st_mode
                file_path.chmod(perms & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)
                logger.debug(f"Set read-only permissions for: {file_path}")
            except OSError as e:
                logger.warning(f"Failed to set read-only permissions for {file_path}: {e}")
            
            if success:
                logger.info(f"Successfully locked file: {file_path}")
            else:
                logger.warning(f"File locking may not be fully effective for: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to lock file {file_path}: {e}")
            return False
    
    @staticmethod
    def _lock_file_windows(file_path: Path) -> bool:
        """Lock file on Windows using attrib command"""
        try:
            # Use attrib command to set read-only attribute
            result = subprocess.run(
                ["attrib", "+R", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.debug(f"Windows attrib command successful for: {file_path}")
                return True
            else:
                logger.warning(f"Windows attrib command failed for {file_path}: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"Windows file locking command failed for {file_path}: {e}")
            return False
    
    @staticmethod
    def _lock_file_macos(file_path: Path) -> bool:
        """Lock file on macOS using chmod and chflags"""
        success = True
        
        try:
            # Set read-only permissions
            result = subprocess.run(
                ["chmod", "444", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning(f"macOS chmod command failed for {file_path}: {result.stderr}")
                success = False
            else:
                logger.debug(f"macOS chmod command successful for: {file_path}")
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"macOS chmod command failed for {file_path}: {e}")
            success = False
        
        try:
            # Set immutable flag
            result = subprocess.run(
                ["chflags", "uchg", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning(f"macOS chflags command failed for {file_path}: {result.stderr}")
            else:
                logger.debug(f"macOS chflags command successful for: {file_path}")
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"macOS chflags command failed for {file_path}: {e}")
        
        return success
    
    @staticmethod
    def _lock_file_linux(file_path: Path) -> bool:
        """Lock file on Linux using chmod"""
        try:
            # Set read-only permissions
            result = subprocess.run(
                ["chmod", "444", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.debug(f"Linux chmod command successful for: {file_path}")
                return True
            else:
                logger.warning(f"Linux chmod command failed for {file_path}: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"Linux file locking command failed for {file_path}: {e}")
            return False
    
    @staticmethod
    def unlock_file(file_path: Path) -> bool:
        """
        Unlock a file to allow modification
        
        Args:
            file_path: Path to file to unlock
            
        Returns:
            True if file was successfully unlocked, False otherwise
        """
        if not file_path.exists():
            logger.error(f"Cannot unlock file that doesn't exist: {file_path}")
            return False
        
        try:
            logger.info(f"Unlocking file: {file_path}")
            
            # Use platform-specific unlocking methods
            success = False
            
            if sys.platform == "win32":
                success = FileLockManager._unlock_file_windows(file_path)
            elif sys.platform == "darwin":
                success = FileLockManager._unlock_file_macos(file_path)
            else:
                success = FileLockManager._unlock_file_linux(file_path)
            
            # Always restore write permissions using Python API as fallback
            try:
                perms = file_path.stat().st_mode
                file_path.chmod(perms | stat.S_IWUSR)
                logger.debug(f"Restored write permissions for: {file_path}")
            except OSError as e:
                logger.warning(f"Failed to restore write permissions for {file_path}: {e}")
            
            if success:
                logger.info(f"Successfully unlocked file: {file_path}")
            else:
                logger.warning(f"File unlocking may not be fully effective for: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to unlock file {file_path}: {e}")
            return False
    
    @staticmethod
    def _unlock_file_windows(file_path: Path) -> bool:
        """Unlock file on Windows using attrib command"""
        try:
            # Remove read-only attribute
            result = subprocess.run(
                ["attrib", "-R", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.debug(f"Windows attrib unlock successful for: {file_path}")
                return True
            else:
                logger.warning(f"Windows attrib unlock failed for {file_path}: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"Windows file unlocking command failed for {file_path}: {e}")
            return False
    
    @staticmethod
    def _unlock_file_macos(file_path: Path) -> bool:
        """Unlock file on macOS using chmod and chflags"""
        success = True
        
        try:
            # Remove immutable flag
            result = subprocess.run(
                ["chflags", "nouchg", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning(f"macOS chflags unlock failed for {file_path}: {result.stderr}")
            else:
                logger.debug(f"macOS chflags unlock successful for: {file_path}")
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"macOS chflags unlock command failed for {file_path}: {e}")
        
        try:
            # Restore write permissions
            result = subprocess.run(
                ["chmod", "644", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.warning(f"macOS chmod unlock failed for {file_path}: {result.stderr}")
                success = False
            else:
                logger.debug(f"macOS chmod unlock successful for: {file_path}")
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"macOS chmod unlock command failed for {file_path}: {e}")
            success = False
        
        return success
    
    @staticmethod
    def _unlock_file_linux(file_path: Path) -> bool:
        """Unlock file on Linux using chmod"""
        try:
            # Restore write permissions
            result = subprocess.run(
                ["chmod", "644", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.debug(f"Linux chmod unlock successful for: {file_path}")
                return True
            else:
                logger.warning(f"Linux chmod unlock failed for {file_path}: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"Linux file unlocking command failed for {file_path}: {e}")
            return False
    
    @staticmethod
    def is_file_locked(file_path: Path) -> bool:
        """
        Check if a file is locked (read-only)
        
        Args:
            file_path: Path to file to check
            
        Returns:
            True if file is locked, False otherwise
        """
        if not file_path.exists():
            return False
        
        try:
            # Check if file has write permissions
            perms = file_path.stat().st_mode
            is_readonly = not (perms & stat.S_IWUSR)
            
            logger.debug(f"File {file_path} locked status: {is_readonly}")
            return is_readonly
            
        except OSError as e:
            logger.error(f"Failed to check lock status for {file_path}: {e}")
            return False
    
    @staticmethod
    def lock_multiple_files(file_paths: List[Path]) -> Dict[Path, bool]:
        """
        Lock multiple files
        
        Args:
            file_paths: List of file paths to lock
            
        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}
        
        for file_path in file_paths:
            results[file_path] = FileLockManager.lock_file(file_path)
        
        successful_locks = sum(1 for success in results.values() if success)
        logger.info(f"Successfully locked {successful_locks}/{len(file_paths)} files")
        
        return results
