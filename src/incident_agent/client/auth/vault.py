#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General Local Vault Implementation
Secure local storage for sensitive data like tokens, API keys, etc.
"""

import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Configure logging
logger = logging.getLogger('local_vault')

# Default vault location
DEFAULT_VAULT_DIR = Path.home() / ".incident_agent"
DEFAULT_VAULT_FILE = DEFAULT_VAULT_DIR / "vault.json"


class LocalVault:
    """General purpose local vault for storing sensitive data"""
    
    def __init__(self, vault_file: Optional[Path] = None):
        """
        Initialize LocalVault
        
        Args:
            vault_file: Optional custom vault file path
        """
        self.vault_file = vault_file or DEFAULT_VAULT_FILE
        self._ensure_vault_dir()
    
    def _ensure_vault_dir(self):
        """Ensure vault directory exists"""
        self.vault_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _read_vault(self) -> Dict[str, Any]:
        """Read vault data from file"""
        try:
            if self.vault_file.exists():
                with open(self.vault_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read vault file: {e}")
        return {}
    
    def _write_vault(self, data: Dict[str, Any]):
        """Write vault data to file"""
        try:
            self._ensure_vault_dir()
            with open(self.vault_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Set restrictive permissions (read/write for owner only)
            self.vault_file.chmod(0o600)
            
        except Exception as e:
            logger.error(f"Failed to write vault file: {e}")
            raise
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from vault
        
        Args:
            key: The key to retrieve
        
        Returns:
            Value if found, None otherwise
        """
        vault_data = self._read_vault()
        return vault_data.get(key)
    
    def set(self, key: str, value: str):
        """
        Store value in vault
        
        Args:
            key: The key to store
            value: The value to store
        """
        vault_data = self._read_vault()
        vault_data[key] = value
        self._write_vault(vault_data)
        logger.info(f"Stored key '{key}' in vault")
    
    def delete(self, key: str) -> bool:
        """
        Remove key from vault
        
        Args:
            key: The key to remove
        
        Returns:
            True if key was removed, False if key didn't exist
        """
        vault_data = self._read_vault()
        if key in vault_data:
            del vault_data[key]
            self._write_vault(vault_data)
            logger.info(f"Removed key '{key}' from vault")
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in vault
        
        Args:
            key: The key to check
        
        Returns:
            True if key exists, False otherwise
        """
        vault_data = self._read_vault()
        return key in vault_data
    
    def list_keys(self) -> list:
        """
        List all keys in vault
        
        Returns:
            List of keys
        """
        vault_data = self._read_vault()
        return list(vault_data.keys())
    
    def clear(self):
        """Clear all data from vault"""
        self._write_vault({})
        logger.info("Cleared all data from vault")
    
    def get_file_path(self) -> Path:
        """Get vault file path"""
        return self.vault_file


# Global singleton instance for convenience
_default_vault_instance: Optional[LocalVault] = None


def get_default_vault() -> LocalVault:
    """
    Get default LocalVault singleton instance
    
    Returns:
        LocalVault instance
    """
    global _default_vault_instance
    if _default_vault_instance is None:
        _default_vault_instance = LocalVault()
    return _default_vault_instance


# Convenience functions using default vault
def get_token(key: str) -> Optional[str]:
    """Get token from default vault"""
    return get_default_vault().get(key)


def set_token(key: str, value: str):
    """Store token in default vault"""
    get_default_vault().set(key, value)


def delete_token(key: str) -> bool:
    """Remove token from default vault"""
    return get_default_vault().delete(key)


# Specific token keys for common use cases
class VaultKeys:
    """Common vault keys"""
    PROMETHEUS_TOKEN = "prometheus_token"
    GITHUB_TOKEN = "github_token"
    OPENAI_API_KEY = "openai_api_key"
    ANTHROPIC_API_KEY = "anthropic_api_key"
    PAGERDUTY_TOKEN = "pagerduty_token"


# Export
__all__ = [
    "LocalVault",
    "get_default_vault",
    "get_token",
    "set_token", 
    "delete_token",
    "VaultKeys"
]
