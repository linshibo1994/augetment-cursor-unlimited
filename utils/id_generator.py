"""
ID generation utilities for creating new device and machine IDs
"""

import uuid
import secrets
import hashlib
import base64
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class IDGenerator:
    """Generates various types of IDs for telemetry replacement"""

    @staticmethod
    def decode_base64_string(encoded_str: str) -> str:
        """
        Decode Base64 encoded string (for security/obfuscation)

        Args:
            encoded_str: Base64 encoded string

        Returns:
            Decoded string
        """
        try:
            decoded_bytes = base64.b64decode(encoded_str)
            decoded_str = decoded_bytes.decode('utf-8')
            logger.debug(f"Decoded Base64: {encoded_str} -> {decoded_str}")
            return decoded_str
        except Exception as e:
            logger.error(f"Failed to decode Base64 string {encoded_str}: {e}")
            return encoded_str  # Return original if decoding fails
    
    @staticmethod
    def generate_uuid() -> str:
        """
        Generate a random UUID v4
        
        Returns:
            Lowercase UUID v4 string
        """
        new_uuid = str(uuid.uuid4()).lower()
        logger.debug(f"Generated UUID: {new_uuid}")
        return new_uuid
    
    @staticmethod
    def generate_machine_id() -> str:
        """
        Generate a random 64-character hex string for machine ID
        Similar to using /dev/urandom but using Python's cryptographic functions
        
        Returns:
            64-character hexadecimal string
        """
        # Generate 32 random bytes (which will become 64 hex characters)
        random_bytes = secrets.token_bytes(32)
        machine_id = random_bytes.hex()
        logger.debug(f"Generated machine ID: {machine_id}")
        return machine_id
    
    @staticmethod
    def generate_device_id() -> str:
        """
        Generate a random UUID v4 for device ID
        
        Returns:
            Lowercase UUID v4 string
        """
        device_id = IDGenerator.generate_uuid()
        logger.debug(f"Generated device ID: {device_id}")
        return device_id
    
    @staticmethod
    def generate_sha256_hash() -> str:
        """
        Generate a SHA-256 hash from a random UUID
        Some telemetry fields require SHA-256 hashes instead of plain UUIDs
        
        Returns:
            64-character SHA-256 hash string
        """
        # Generate a random UUID and hash it
        random_uuid = uuid.uuid4()
        sha256_hash = hashlib.sha256(random_uuid.bytes).hexdigest()
        logger.debug(f"Generated SHA-256 hash: {sha256_hash}")
        return sha256_hash
    
    @staticmethod
    def generate_telemetry_ids() -> Dict[str, str]:
        """
        Generate a complete set of telemetry IDs
        
        Returns:
            Dictionary containing all generated IDs
        """
        ids = {
            "machine_id": IDGenerator.generate_machine_id(),
            "device_id": IDGenerator.generate_device_id(),
            "mac_machine_id": IDGenerator.generate_sha256_hash(),
            "permanent_device_id": IDGenerator.generate_uuid(),
            "permanent_user_id": IDGenerator.generate_uuid(),
        }
        
        logger.info("Generated complete telemetry ID set")
        for key, value in ids.items():
            logger.debug(f"{key}: {value}")
        
        return ids
    
    @staticmethod
    def get_id_for_key(key: str) -> str:
        """
        Generate appropriate ID based on the telemetry key
        
        Args:
            key: Telemetry key name
            
        Returns:
            Generated ID string
        """
        # Map telemetry keys to appropriate ID generation methods
        key_lower = key.lower()
        
        # Handle specific telemetry keys
        if key == "telemetry.devDeviceId":
            # VSCode/Cursor device ID - uses UUID format
            return IDGenerator.generate_device_id()
        elif key == "telemetry.macMachineId":
            # VSCode/Cursor Mac machine ID - uses SHA-256 hash
            return IDGenerator.generate_sha256_hash()
        elif "machineId" in key or "machine_id" in key_lower:
            if "mac" in key_lower:
                # macMachineId uses SHA-256 hash
                return IDGenerator.generate_sha256_hash()
            else:
                # Regular machineId uses 64-char hex
                return IDGenerator.generate_machine_id()
        elif "deviceId" in key or "device_id" in key_lower:
            # Device IDs use UUID
            return IDGenerator.generate_device_id()
        elif "userId" in key or "user_id" in key_lower:
            # User IDs use UUID
            return IDGenerator.generate_uuid()
        elif "sqmId" in key:
            # sqmId uses SHA-256 hash (based on augment-vip pattern)
            return IDGenerator.generate_sha256_hash()
        else:
            # Default to UUID for unknown keys
            logger.debug(f"Using UUID for key '{key}' (not in known patterns)")
            return IDGenerator.generate_uuid()
    
    @staticmethod
    def validate_id_format(id_value: str, id_type: str) -> bool:
        """
        Validate that an ID matches the expected format
        
        Args:
            id_value: ID value to validate
            id_type: Type of ID (uuid, machine_id, sha256)
            
        Returns:
            True if ID format is valid, False otherwise
        """
        if not id_value:
            return False
        
        try:
            if id_type == "uuid":
                # Validate UUID format
                uuid.UUID(id_value)
                return True
            elif id_type == "machine_id":
                # Validate 64-character hex string
                return len(id_value) == 64 and all(c in "0123456789abcdef" for c in id_value.lower())
            elif id_type == "sha256":
                # Validate SHA-256 hash format
                return len(id_value) == 64 and all(c in "0123456789abcdef" for c in id_value.lower())
            else:
                logger.warning(f"Unknown ID type: {id_type}")
                return False
        except (ValueError, TypeError) as e:
            logger.debug(f"ID validation failed for '{id_value}' (type: {id_type}): {e}")
            return False
    
    @staticmethod
    def backup_old_ids(old_ids: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a backup record of old IDs with metadata
        
        Args:
            old_ids: Dictionary of old ID values
            
        Returns:
            Backup record with metadata
        """
        import time
        
        backup_record = {
            "timestamp": int(time.time()),
            "old_ids": old_ids.copy(),
            "backup_format_version": "1.0",
        }
        
        logger.info(f"Created backup record for {len(old_ids)} IDs")
        return backup_record
