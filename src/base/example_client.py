#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example Client Implementation using Abstract Base Classes
Demonstrates how easy it is to create new clients with the base architecture
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass

from .config import BaseClientConfig
from .client import BaseAPIClient
from .singleton import ClientSingleton


@dataclass
class ExampleConfig(BaseClientConfig):
    """Example configuration class - demonstrates the pattern"""
    
    api_url: str = "https://api.example.com/v1"
    api_key: Optional[str] = None
    
    @property
    def service_name(self) -> str:
        return "Example"
    
    @property
    def vault_token_key(self) -> str:
        # Would need to add to VaultKeys: EXAMPLE_TOKEN = "example_token"
        return "example_token"
    
    @property
    def env_token_keys(self) -> List[str]:
        return ["EXAMPLE_API_KEY", "EXAMPLE_TOKEN"]
    
    def _set_token(self, token: Optional[str]):
        self.api_key = token


class ExampleClient(BaseAPIClient):
    """Example client implementation - demonstrates the pattern"""
    
    def _get_default_config(self) -> ExampleConfig:
        return ExampleConfig.from_vault()
    
    def _validate_config(self):
        if not self.config.api_url:
            raise ValueError("Example API URL not configured")
        if not self.config.api_key:
            raise ValueError("Example API key not found")
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "incident-agent-example-client"
        }
    
    def _build_url(self, endpoint: str) -> str:
        return f"{self.config.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    def health_check(self) -> bool:
        """Example health check implementation"""
        try:
            # In a real implementation, this would call an actual health endpoint
            result = {"status": "ok", "service": "example"}
            return result.get("status") == "ok"
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    # Example-specific methods
    def get_example_data(self) -> Dict[str, Any]:
        """Example method - would call actual API"""
        # In a real implementation: return self._request("data")
        return {
            "message": "This is example data",
            "service": self.config.service_name,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    def create_example_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Example POST method"""
        # In a real implementation: return self._request("items", method="POST", data=data)
        return {
            "id": "example-123",
            "created": True,
            "data": data
        }


# Singleton functions using generic factory
def get_example_client(config: Optional[ExampleConfig] = None) -> ExampleClient:
    """Get Example client singleton"""
    return ClientSingleton.get_client(ExampleClient, config)


def reset_example_client():
    """Reset Example client instance"""
    ClientSingleton.reset_client(ExampleClient)


# Export
__all__ = [
    "ExampleConfig",
    "ExampleClient",
    "get_example_client",
    "reset_example_client"
]
