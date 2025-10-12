#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generic Singleton Factory for API Clients
"""

from typing import TypeVar, Type, Optional, Dict, Any
from .client import BaseAPIClient
from .config import BaseClientConfig

ClientType = TypeVar('ClientType', bound=BaseAPIClient)
ConfigType = TypeVar('ConfigType', bound=BaseClientConfig)


class ClientSingleton:
    """Generic singleton factory for API clients"""
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def get_client(
        cls, 
        client_class: Type[ClientType], 
        config: Optional[BaseClientConfig] = None
    ) -> ClientType:
        """Get or create singleton client instance"""
        service_name = client_class.__name__
        
        if service_name not in cls._instances:
            instance = client_class(config)
            cls._instances[service_name] = instance
            instance.logger.info(f"Created new {service_name} instance")
        
        return cls._instances[service_name]
    
    @classmethod
    def reset_client(cls, client_class: Type[ClientType]):
        """Reset specific client instance"""
        service_name = client_class.__name__
        if service_name in cls._instances:
            del cls._instances[service_name]
    
    @classmethod
    def reset_all_clients(cls):
        """Reset all client instances"""
        cls._instances.clear()
    
    @classmethod
    def get_active_clients(cls) -> Dict[str, Any]:
        """Get all active client instances"""
        return cls._instances.copy()
