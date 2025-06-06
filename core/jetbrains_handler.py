"""
JetBrains IDE handler for modifying telemetry IDs
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from utils.paths import PathManager
from utils.backup import BackupManager
from utils.id_generator import IDGenerator
from utils.file_locker import FileLockManager
from config.settings import JETBRAINS_CONFIG

logger = logging.getLogger(__name__)


class JetBrainsHandler:
    """Handles JetBrains IDE telemetry ID modification"""
    
    def __init__(self, path_manager: PathManager, backup_manager: BackupManager):
        """
        Initialize JetBrains handler
        
        Args:
            path_manager: Path management instance
            backup_manager: Backup management instance
        """
        self.path_manager = path_manager
        self.backup_manager = backup_manager
        self.id_generator = IDGenerator()
        self.file_locker = FileLockManager()
    
    def process_jetbrains_ides(self, create_backups: bool = True, lock_files: bool = True, clean_databases: bool = True) -> Dict[str, Any]:
        """
        Process all JetBrains IDE installations

        Args:
            create_backups: Whether to create backups before modification
            lock_files: Whether to lock files after modification
            clean_databases: Whether to clean database files

        Returns:
            Dictionary with processing results
        """
        logger.info("Starting JetBrains IDE processing")

        results = {
            "success": False,
            "jetbrains_found": False,
            "files_processed": [],
            "databases_processed": [],
            "files_failed": [],
            "databases_failed": [],
            "backups_created": [],
            "old_ids": {},
            "new_ids": {},
            "database_records_cleaned": 0,
            "errors": []
        }
        
        try:
            # Find JetBrains configuration directory
            jetbrains_dir = self.path_manager.get_jetbrains_config_dir()
            if not jetbrains_dir:
                results["errors"].append("JetBrains configuration directory not found")
                return results
            
            results["jetbrains_found"] = True
            logger.info(f"Found JetBrains directory: {jetbrains_dir}")
            
            # Get ID files to process
            id_files = self.path_manager.get_jetbrains_id_files()
            if not id_files:
                results["errors"].append("No JetBrains ID files found")
                return results
            
            # Process each ID file
            for file_path in id_files:
                file_result = self._process_jetbrains_id_file(
                    file_path, 
                    create_backups=create_backups,
                    lock_files=lock_files
                )
                
                if file_result["success"]:
                    results["files_processed"].append(str(file_path))
                    if file_result["backup_path"]:
                        results["backups_created"].append(file_result["backup_path"])
                    if file_result["old_id"]:
                        results["old_ids"][file_path.name] = file_result["old_id"]
                    if file_result["new_id"]:
                        results["new_ids"][file_path.name] = file_result["new_id"]
                else:
                    results["files_failed"].append(str(file_path))
                    if file_result["error"]:
                        results["errors"].append(f"{file_path.name}: {file_result['error']}")
            
            # Process database files if requested
            if clean_databases:
                logger.info("Processing JetBrains database files...")
                db_files = self.path_manager.get_jetbrains_database_files()

                for db_file in db_files:
                    db_result = self._process_jetbrains_database_file(
                        db_file,
                        create_backups=create_backups
                    )

                    if db_result["success"]:
                        results["databases_processed"].append(str(db_file))
                        if db_result["backup_path"]:
                            results["backups_created"].append(db_result["backup_path"])
                        results["database_records_cleaned"] += db_result.get("records_cleaned", 0)
                    else:
                        results["databases_failed"].append(str(db_file))
                        if db_result["error"]:
                            results["errors"].append(f"{db_file.name}: {db_result['error']}")

            # Overall success if at least one file was processed
            results["success"] = (len(results["files_processed"]) > 0 or
                                len(results["databases_processed"]) > 0)

            if results["success"]:
                logger.info(f"Successfully processed {len(results['files_processed'])} ID files and {len(results['databases_processed'])} database files")
            else:
                logger.error("Failed to process any JetBrains files")

        except Exception as e:
            logger.error(f"Unexpected error in JetBrains processing: {e}")
            results["errors"].append(f"Unexpected error: {str(e)}")

        return results
    
    def _process_jetbrains_id_file(self, file_path: Path, create_backups: bool = True, lock_files: bool = True) -> Dict[str, Any]:
        """
        Process a single JetBrains ID file
        
        Args:
            file_path: Path to ID file
            create_backups: Whether to create backup
            lock_files: Whether to lock file after modification
            
        Returns:
            Dictionary with processing results
        """
        result = {
            "success": False,
            "backup_path": None,
            "old_id": None,
            "new_id": None,
            "error": None
        }
        
        try:
            logger.info(f"Processing JetBrains ID file: {file_path}")
            
            # Validate path
            if not self.path_manager.validate_path(file_path.parent):
                result["error"] = "Invalid or unsafe file path"
                return result
            
            # Read old ID if file exists
            old_id = None
            if file_path.exists():
                try:
                    old_id = file_path.read_text(encoding='utf-8').strip()
                    result["old_id"] = old_id
                    logger.info(f"Old ID: {old_id}")
                except (OSError, UnicodeDecodeError) as e:
                    logger.warning(f"Could not read old ID from {file_path}: {e}")
            
            # Create backup if requested and file exists
            if create_backups and file_path.exists():
                backup_path = self.backup_manager.create_file_backup(file_path, f"jetbrains_{file_path.name}")
                if backup_path:
                    result["backup_path"] = str(backup_path)
                    logger.info(f"Created backup: {backup_path}")
                else:
                    logger.warning(f"Failed to create backup for {file_path}")
            
            # Generate new ID
            new_id = self.id_generator.generate_uuid()
            result["new_id"] = new_id
            logger.info(f"New ID: {new_id}")
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Unlock file if it's locked
            if file_path.exists() and self.file_locker.is_file_locked(file_path):
                self.file_locker.unlock_file(file_path)
            
            # Write new ID to file
            file_path.write_text(new_id, encoding='utf-8')
            logger.info(f"Successfully wrote new ID to {file_path}")
            
            # Lock file if requested
            if lock_files:
                if self.file_locker.lock_file(file_path):
                    logger.info(f"Successfully locked file: {file_path}")
                else:
                    logger.warning(f"Failed to lock file: {file_path}")
            
            result["success"] = True
            
        except (OSError, IOError) as e:
            error_msg = f"File operation failed: {str(e)}"
            logger.error(f"Error processing {file_path}: {error_msg}")
            result["error"] = error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error processing {file_path}: {error_msg}")
            result["error"] = error_msg
        
        return result

    def _process_jetbrains_database_file(self, db_path: Path, create_backups: bool = True) -> Dict[str, Any]:
        """
        Process a single JetBrains database file

        Args:
            db_path: Path to database file
            create_backups: Whether to create backup

        Returns:
            Dictionary with processing results
        """
        result = {
            "success": False,
            "backup_path": None,
            "records_cleaned": 0,
            "error": None
        }

        try:
            logger.info(f"Processing JetBrains database file: {db_path}")

            # Validate path
            if not self.path_manager.validate_path(db_path):
                result["error"] = "Invalid or unsafe database path"
                return result

            if not db_path.exists():
                result["error"] = "Database file does not exist"
                return result

            # Create backup if requested
            if create_backups:
                backup_path = self.backup_manager.create_file_backup(db_path, f"jetbrains_db_{db_path.name}")
                if backup_path:
                    result["backup_path"] = str(backup_path)
                    logger.info(f"Created database backup: {backup_path}")
                else:
                    logger.warning(f"Failed to create backup for {db_path}")

            # Process database based on file type
            if db_path.suffix.lower() in ['.db', '.sqlite', '.sqlite3']:
                records_cleaned = self._clean_sqlite_database(db_path)
                result["records_cleaned"] = records_cleaned
                logger.info(f"Cleaned {records_cleaned} records from {db_path}")
            else:
                logger.info(f"Skipping non-SQLite database: {db_path}")

            result["success"] = True

        except Exception as e:
            error_msg = f"Database processing failed: {str(e)}"
            logger.error(f"Error processing {db_path}: {error_msg}")
            result["error"] = error_msg

        return result

    def _clean_sqlite_database(self, db_path: Path) -> int:
        """
        Clean AugmentCode-related records from SQLite database

        Args:
            db_path: Path to SQLite database

        Returns:
            Number of records cleaned
        """
        import sqlite3

        records_cleaned = 0

        try:
            # First check if this is actually a SQLite database
            if not self._is_sqlite_database(db_path):
                logger.debug(f"Skipping non-SQLite file: {db_path}")
                return 0

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table_name, in tables:
                # Try to find and clean AugmentCode-related records
                try:
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()

                    # Look for text columns that might contain AugmentCode data
                    text_columns = [col[1] for col in columns if col[2].upper() in ['TEXT', 'VARCHAR', 'CHAR']]

                    for column in text_columns:
                        for pattern in JETBRAINS_CONFIG["augment_patterns"]:
                            # Count records to be deleted
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column} LIKE ?", (pattern,))
                            count = cursor.fetchone()[0]

                            if count > 0:
                                # Delete records
                                cursor.execute(f"DELETE FROM {table_name} WHERE {column} LIKE ?", (pattern,))
                                records_cleaned += count
                                logger.info(f"Cleaned {count} records from {table_name}.{column} matching {pattern}")

                except sqlite3.Error as e:
                    logger.warning(f"Could not clean table {table_name}: {e}")
                    continue

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            logger.error(f"SQLite error cleaning {db_path}: {e}")

        return records_cleaned

    def _is_sqlite_database(self, file_path: Path) -> bool:
        """
        Check if a file is actually a SQLite database

        Args:
            file_path: Path to file to check

        Returns:
            True if file is a SQLite database, False otherwise
        """
        try:
            # SQLite files start with "SQLite format 3\000"
            with open(file_path, 'rb') as f:
                header = f.read(16)
                return header.startswith(b'SQLite format 3\x00')
        except (OSError, IOError):
            return False

    def verify_jetbrains_installation(self) -> Dict[str, Any]:
        """
        Verify JetBrains installation and return information
        
        Returns:
            Dictionary with installation information
        """
        info = {
            "installed": False,
            "config_dir": None,
            "id_files": [],
            "existing_files": [],
            "missing_files": []
        }
        
        try:
            # Check for JetBrains directory
            jetbrains_dir = self.path_manager.get_jetbrains_config_dir()
            if jetbrains_dir:
                info["installed"] = True
                info["config_dir"] = str(jetbrains_dir)
                
                # Check ID files
                id_files = self.path_manager.get_jetbrains_id_files()
                info["id_files"] = [str(f) for f in id_files]
                
                for file_path in id_files:
                    if file_path.exists():
                        info["existing_files"].append(str(file_path))
                    else:
                        info["missing_files"].append(str(file_path))
            
        except Exception as e:
            logger.error(f"Error verifying JetBrains installation: {e}")
        
        return info
    
    def get_current_jetbrains_ids(self) -> Dict[str, str]:
        """
        Get current JetBrains ID values
        
        Returns:
            Dictionary mapping file names to current ID values
        """
        current_ids = {}
        
        try:
            id_files = self.path_manager.get_jetbrains_id_files()
            
            for file_path in id_files:
                if file_path.exists():
                    try:
                        current_id = file_path.read_text(encoding='utf-8').strip()
                        current_ids[file_path.name] = current_id
                    except (OSError, UnicodeDecodeError) as e:
                        logger.warning(f"Could not read ID from {file_path}: {e}")
                        current_ids[file_path.name] = None
                else:
                    current_ids[file_path.name] = None
        
        except Exception as e:
            logger.error(f"Error getting current JetBrains IDs: {e}")
        
        return current_ids
