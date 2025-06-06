#!/usr/bin/env python3
"""
Augment Cleaner Unified - Main Entry Point

A comprehensive tool that combines the functionality of augment-vip and free-augmentcode
for cleaning AugmentCode-related data and allowing unlimited logins with different accounts.
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Import our modules
from config.settings import VERSION, APP_NAME, DEFAULT_SETTINGS, LOGGING_CONFIG
from utils.paths import PathManager
from utils.backup import BackupManager
from utils.id_generator import IDGenerator
from utils.file_locker import FileLockManager
from core.jetbrains_handler import JetBrainsHandler
from core.vscode_handler import VSCodeHandler
from core.db_cleaner import DatabaseCleaner


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration
    
    Args:
        verbose: Enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format=LOGGING_CONFIG["format"],
        datefmt=LOGGING_CONFIG["date_format"]
    )
    
    # Reduce noise from some modules
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="augment-cleaner-unified",
        description=f"{APP_NAME} v{VERSION} - Clean AugmentCode data for unlimited account switching",
        epilog="For more information, see the README.md file."
    )
    
    # Main operation modes
    parser.add_argument(
        "--jetbrains-only",
        action="store_true",
        help="Process only JetBrains IDEs"
    )
    
    parser.add_argument(
        "--vscode-only", 
        action="store_true",
        help="Process only VSCode variants"
    )
    
    # Backup options
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backups (not recommended)"
    )
    
    # File locking options
    parser.add_argument(
        "--no-lock",
        action="store_true", 
        help="Skip locking files after modification"
    )
    
    # Database cleaning options
    parser.add_argument(
        "--no-database-clean",
        action="store_true",
        help="Skip cleaning SQLite databases"
    )
    
    # Workspace cleaning options
    parser.add_argument(
        "--no-workspace-clean",
        action="store_true",
        help="Skip cleaning workspace storage"
    )
    
    # Information options
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show installation information and exit"
    )
    
    parser.add_argument(
        "--current-ids",
        action="store_true",
        help="Show current ID values and exit"
    )

    parser.add_argument(
        "--paths",
        action="store_true",
        help="Show system paths and exit"
    )

    parser.add_argument(
        "--legacy-output",
        action="store_true",
        help="Use legacy free-augmentcode style output format"
    )
    
    # Output options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress non-error output"
    )
    
    # Version
    parser.add_argument(
        "--version",
        action="version",
        version=f"{APP_NAME} v{VERSION}"
    )
    
    return parser


def print_banner() -> None:
    """Print application banner"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          {APP_NAME}                           ║
║                                 v{VERSION}                                  ║
║                                                                              ║
║  A comprehensive tool for cleaning AugmentCode data and enabling unlimited   ║
║  account switching on the same computer.                                     ║
║                                                                              ║
║  Supports: JetBrains IDEs, VSCode, VSCode Insiders, Cursor, and more        ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


def print_system_paths(path_manager: PathManager) -> None:
    """
    Print system paths information (from free-augmentcode)

    Args:
        path_manager: Path manager instance
    """
    print("\n" + "="*80)
    print("SYSTEM PATHS")
    print("="*80)

    platform_paths = path_manager.platform_paths

    print(f"\n📁 System Directories:")
    print(f"   Home Directory: {platform_paths['home']}")
    print(f"   Config Directory: {platform_paths['config']}")
    print(f"   Data Directory: {platform_paths['data']}")

    # VSCode specific paths
    print(f"\n📝 VSCode Paths:")
    workspace_path = path_manager.get_workspace_storage_path()
    print(f"   Workspace Storage: {workspace_path or 'Not found'}")

    # Show some example storage paths
    vscode_dirs = path_manager.get_vscode_directories()
    if vscode_dirs:
        print(f"   Example Storage Dirs:")
        for i, vscode_dir in enumerate(vscode_dirs[:3]):
            storage_file = path_manager.get_vscode_storage_file(vscode_dir)
            db_file = path_manager.get_vscode_database_file(vscode_dir)
            print(f"     {i+1}. Storage: {storage_file or 'N/A'}")
            print(f"        Database: {db_file or 'N/A'}")
        if len(vscode_dirs) > 3:
            print(f"     ... and {len(vscode_dirs) - 3} more")

    # JetBrains specific paths
    jetbrains_dir = path_manager.get_jetbrains_config_dir()
    print(f"\n🔧 JetBrains Paths:")
    print(f"   Config Directory: {jetbrains_dir or 'Not found'}")
    if jetbrains_dir:
        id_files = path_manager.get_jetbrains_id_files()
        print(f"   ID Files:")
        for id_file in id_files:
            print(f"     • {id_file}")


def print_installation_info(jetbrains_handler: JetBrainsHandler, vscode_handler: VSCodeHandler, database_cleaner: DatabaseCleaner) -> None:
    """
    Print installation information
    
    Args:
        jetbrains_handler: JetBrains handler instance
        vscode_handler: VSCode handler instance
        database_cleaner: Database cleaner instance
    """
    print("\n" + "="*80)
    print("INSTALLATION INFORMATION")
    print("="*80)
    
    # JetBrains info
    jetbrains_info = jetbrains_handler.verify_jetbrains_installation()
    print(f"\n🔧 JetBrains IDEs:")
    print(f"   Installed: {'Yes' if jetbrains_info['installed'] else 'No'}")
    if jetbrains_info['installed']:
        print(f"   Config Directory: {jetbrains_info['config_dir']}")
        print(f"   ID Files Found: {len(jetbrains_info['existing_files'])}/{len(jetbrains_info['id_files'])}")
        for file_path in jetbrains_info['existing_files']:
            print(f"     ✓ {file_path}")
        for file_path in jetbrains_info['missing_files']:
            print(f"     ✗ {file_path}")
    
    # VSCode info
    vscode_info = vscode_handler.verify_vscode_installation()
    print(f"\n📝 VSCode Variants:")
    print(f"   Installed: {'Yes' if vscode_info['installed'] else 'No'}")
    if vscode_info['installed']:
        print(f"   Variants Found: {', '.join(vscode_info['variants_found'])}")
        print(f"   Storage Directories: {vscode_info['total_directories']}")
        for directory in vscode_info['storage_directories'][:5]:  # Show first 5
            print(f"     • {directory}")
        if vscode_info['total_directories'] > 5:
            print(f"     ... and {vscode_info['total_directories'] - 5} more")
    
    # Database info
    db_info = database_cleaner.get_database_info()
    print(f"\n🗃️ Databases:")
    print(f"   Total Found: {db_info['total_databases']}")
    print(f"   Accessible: {db_info['accessible_databases']}")
    
    total_augment_records = sum(db['augment_records'] for db in db_info['databases'] if db.get('augment_records'))
    print(f"   AugmentCode Records: {total_augment_records}")


def print_current_ids(jetbrains_handler: JetBrainsHandler, vscode_handler: VSCodeHandler) -> None:
    """
    Print current ID values
    
    Args:
        jetbrains_handler: JetBrains handler instance
        vscode_handler: VSCode handler instance
    """
    print("\n" + "="*80)
    print("CURRENT ID VALUES")
    print("="*80)
    
    # JetBrains IDs
    jetbrains_ids = jetbrains_handler.get_current_jetbrains_ids()
    print(f"\n🔧 JetBrains IDs:")
    if jetbrains_ids:
        for file_name, id_value in jetbrains_ids.items():
            status = "✓" if id_value else "✗"
            print(f"   {status} {file_name}: {id_value or 'Not found'}")
    else:
        print("   No JetBrains IDs found")
    
    # VSCode IDs
    vscode_ids = vscode_handler.get_current_vscode_ids()
    print(f"\n📝 VSCode IDs:")
    if vscode_ids:
        for directory, ids in vscode_ids.items():
            print(f"   Directory: {Path(directory).name}")
            for key, value in ids.items():
                status = "✓" if value else "✗"
                print(f"     {status} {key}: {value or 'Not found'}")
    else:
        print("   No VSCode IDs found")


def main() -> int:
    """
    Main entry point
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup logging
    verbose = args.verbose and not args.quiet
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    # Print banner unless quiet
    if not args.quiet:
        print_banner()
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        path_manager = PathManager()
        backup_manager = BackupManager()
        jetbrains_handler = JetBrainsHandler(path_manager, backup_manager)
        vscode_handler = VSCodeHandler(path_manager, backup_manager)
        database_cleaner = DatabaseCleaner(path_manager, backup_manager)
        
        # Handle information requests
        if args.info:
            print_installation_info(jetbrains_handler, vscode_handler, database_cleaner)
            return 0

        if args.current_ids:
            print_current_ids(jetbrains_handler, vscode_handler)
            return 0

        if args.paths:
            print_system_paths(path_manager)
            return 0
        
        # Validate arguments
        if args.jetbrains_only and args.vscode_only:
            logger.error("Cannot specify both --jetbrains-only and --vscode-only")
            return 1
        
        # Determine what to process
        process_jetbrains = not args.vscode_only
        process_vscode = not args.jetbrains_only
        create_backups = not args.no_backup
        lock_files = not args.no_lock
        clean_database = not args.no_database_clean
        clean_workspace = not args.no_workspace_clean
        
        logger.info(f"Starting {APP_NAME} v{VERSION}")
        logger.info(f"Process JetBrains: {process_jetbrains}")
        logger.info(f"Process VSCode: {process_vscode}")
        logger.info(f"Create backups: {create_backups}")
        logger.info(f"Lock files: {lock_files}")
        logger.info(f"Clean database: {clean_database}")
        logger.info(f"Clean workspace: {clean_workspace}")
        
        # Track overall results
        overall_success = False
        results = {}
        
        # Process JetBrains IDEs
        if process_jetbrains:
            if not args.quiet:
                print("\n🔧 Processing JetBrains IDEs...")
            
            jetbrains_result = jetbrains_handler.process_jetbrains_ides(
                create_backups=create_backups,
                lock_files=lock_files
            )
            results["jetbrains"] = jetbrains_result
            
            if jetbrains_result["success"]:
                overall_success = True
                if not args.quiet:
                    print(f"   ✓ Processed {len(jetbrains_result['files_processed'])} JetBrains ID files")

                    # Show detailed results like free-augmentcode
                    if jetbrains_result["old_ids"] and jetbrains_result["new_ids"]:
                        print(f"   📋 ID Changes:")
                        for file_name in jetbrains_result["old_ids"]:
                            old_id = jetbrains_result["old_ids"].get(file_name, "N/A")
                            new_id = jetbrains_result["new_ids"].get(file_name, "N/A")
                            print(f"     {file_name}:")
                            print(f"       Old: {old_id}")
                            print(f"       New: {new_id}")

                    if jetbrains_result["backups_created"]:
                        print(f"   💾 Backups created:")
                        for backup in jetbrains_result["backups_created"]:
                            print(f"     • {backup}")
            else:
                if not args.quiet:
                    print(f"   ✗ JetBrains processing failed")
                    for error in jetbrains_result["errors"]:
                        print(f"     Error: {error}")
        
        # Process VSCode variants
        if process_vscode:
            if not args.quiet:
                print("\n📝 Processing VSCode variants...")
            
            vscode_result = vscode_handler.process_vscode_installations(
                create_backups=create_backups,
                lock_files=lock_files,
                clean_workspace=clean_workspace
            )
            results["vscode"] = vscode_result
            
            if vscode_result["success"]:
                overall_success = True
                if not args.quiet:
                    print(f"   ✓ Processed {len(vscode_result['directories_processed'])} VSCode directories")

                    # Show detailed results like free-augmentcode
                    if vscode_result["old_ids"] and vscode_result["new_ids"]:
                        print(f"   📋 ID Changes:")
                        for key in vscode_result["old_ids"]:
                            old_id = vscode_result["old_ids"].get(key, "N/A")
                            new_id = vscode_result["new_ids"].get(key, "N/A")
                            print(f"     {key}:")
                            print(f"       Old: {old_id}")
                            print(f"       New: {new_id}")

                    if vscode_result["backups_created"]:
                        print(f"   💾 Backups created: {len(vscode_result['backups_created'])} files")

                    if vscode_result["workspace_cleaned"]:
                        print(f"   ✓ Cleaned workspace storage")
                        if vscode_result["workspace_backup"]:
                            print(f"     Workspace backup: {vscode_result['workspace_backup']}")
            else:
                if not args.quiet:
                    print(f"   ✗ VSCode processing failed")
                    for error in vscode_result["errors"]:
                        print(f"     Error: {error}")
        
        # Clean databases
        if clean_database and (process_vscode or not process_jetbrains):
            if not args.quiet:
                print("\n🗃️ Cleaning databases...")
            
            db_result = database_cleaner.clean_all_databases(create_backups=create_backups)
            results["database"] = db_result
            
            if db_result["success"]:
                if not args.quiet:
                    print(f"   ✓ Cleaned {db_result['databases_cleaned']} databases")
                    print(f"   ✓ Deleted {db_result['total_records_deleted']} AugmentCode records")

                    # Show detailed results like free-augmentcode
                    if db_result["backups_created"]:
                        print(f"   💾 Database backups created: {len(db_result['backups_created'])} files")

                    print(f"   📊 Database Summary:")
                    print(f"     Total found: {db_result['databases_found']}")
                    print(f"     Successfully cleaned: {db_result['databases_cleaned']}")
                    print(f"     Failed: {db_result['databases_failed']}")
            else:
                if not args.quiet:
                    print(f"   ✗ Database cleaning failed")
                    for error in db_result["errors"]:
                        print(f"     Error: {error}")
        
        # Print summary
        if not args.quiet:
            print("\n" + "="*80)
            if overall_success:
                print("✅ OPERATION COMPLETED SUCCESSFULLY")
                print("\nNext steps:")
                print("1. Restart your IDE(s)")
                print("2. Log in with a new AugmentCode account")
                print("3. Enjoy unlimited account switching!")
                
                if create_backups:
                    print(f"\n💾 Backups created in: {backup_manager.backup_dir}")
            else:
                print("❌ OPERATION FAILED")
                print("\nSome operations failed. Check the errors above.")
                print("You may need to run the tool with elevated permissions.")
            print("="*80)
        
        return 0 if overall_success else 1
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        if not args.quiet:
            print("\n\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        if not args.quiet:
            print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
