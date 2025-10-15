#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstract Configuration Base Classes
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass

from .auth.vault import get_default_vault


@dataclass
class BaseClientConfig(ABC):
    """Abstract base class for client configurations"""
    
    # Common fields that all configs should have
    timeout: int = 30
    
    # Abstract properties that subclasses must define
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Service name for logging and identification"""
        pass
    
    @property
    @abstractmethod
    def vault_token_key(self) -> str:
        """Vault key for storing the token"""
        pass
    
    @property
    @abstractmethod
    def env_token_keys(self) -> List[str]:
        """Environment variable names to check for token"""
        pass
    
    @classmethod
    def from_vault(cls):
        """Create configuration from local vault - common implementation"""
        vault = get_default_vault()
        instance = cls()
        
        # Get token from vault
        token = vault.get(instance.vault_token_key)
        
        if not token:
            # Try environment variables
            for env_key in instance.env_token_keys:
                token = os.environ.get(env_key)
                if token:
                    # Store in vault for future use
                    vault.set(instance.vault_token_key, token)
                    break
        
        # Set token in instance
        instance._set_token(token)
        
        # Load other environment-specific configs
        instance._load_env_config()
        
        return instance
    
    @abstractmethod
    def _set_token(self, token: Optional[str]):
        """Set the token in the config instance"""
        pass
    
    def _load_env_config(self):
        """Load additional config from environment variables"""
        timeout_env = f"{self.service_name.upper()}_TIMEOUT"
        self.timeout = int(os.environ.get(timeout_env, str(self.timeout)))
    
    def get_token(self) -> Optional[str]:
        """Get the token value - implemented by subclasses"""
        return getattr(self, '_token', None)
