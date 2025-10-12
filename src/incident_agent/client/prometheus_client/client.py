#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prometheus Client Implementation using Abstract Base Classes
For MCP servers with singleton pattern support
"""

import os
from typing import Any, Dict, Optional, List
from dataclasses import dataclass

import requests

from ..base import BaseClientConfig, BaseAPIClient, ClientSingleton
from ..auth.vault import VaultKeys

# Constants
PROMETHEUS_URL = "https://doordash.chronosphere.io/data/metrics/api/v1"


@dataclass
class PrometheusConfig(BaseClientConfig):
    """Prometheus configuration class"""
    
    url: str = PROMETHEUS_URL
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    org_id: Optional[str] = None
    
    @property
    def service_name(self) -> str:
        return "Prometheus"
    
    @property
    def vault_token_key(self) -> str:
        return VaultKeys.PROMETHEUS_TOKEN
    
    @property
    def env_token_keys(self) -> List[str]:
        return ["PROMETHEUS_TOKEN", "CHRONOSPHERE_TOKEN"]
    
    def _set_token(self, token: Optional[str]):
        self.token = token
    
    def _load_env_config(self):
        super()._load_env_config()
        self.org_id = os.environ.get("ORG_ID", "")


class PrometheusClient(BaseAPIClient):
    """Prometheus client implementation using abstract base class"""
    
    def _get_default_config(self) -> PrometheusConfig:
        return PrometheusConfig.from_vault()
    
    def _validate_config(self):
        if not self.config.url:
            raise ValueError("Prometheus URL not configured")
        if not self.config.token:
            raise ValueError("Prometheus token not found. Please set it using: from src.incident_agent.client.auth import get_default_vault, VaultKeys; get_default_vault().set(VaultKeys.PROMETHEUS_TOKEN, 'your_token')")
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        
        if hasattr(self.config, 'org_id') and self.config.org_id:
            headers["X-Scope-OrgID"] = self.config.org_id
            
        return headers
    
    def _get_auth(self):
        """Get authentication info"""
        if self.config.username and self.config.password:
            return requests.auth.HTTPBasicAuth(self.config.username, self.config.password)
        return None
    
    def _build_url(self, endpoint: str) -> str:
        base_url = self.config.url.rstrip('/')
        
        # If URL already contains api/v1, don't add it again
        if base_url.endswith('/api/v1') or '/api/v1' in base_url:
            return f"{base_url}/{endpoint}"
        else:
            return f"{base_url}/api/v1/{endpoint}"
    
    def _validate_response(self, result: Any) -> Any:
        """Validate Prometheus API response"""
        if isinstance(result, dict) and result.get("status") != "success":
            error_msg = result.get('error', 'Unknown error')
            self.logger.error(f"Prometheus API error: {error_msg}")
            raise ValueError(f"Prometheus API error: {error_msg}")
        
        return result.get("data") if isinstance(result, dict) and "data" in result else result
    
    def health_check(self) -> bool:
        """Health check - test API connectivity"""
        try:
            result = self.query("vector(1)")
            return result.get("resultType") == "vector"
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    # Prometheus-specific methods
    def query(self, query: str, time: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute instant query
        
        Args:
            query: PromQL query string
            time: Optional timestamp (RFC3339 or Unix timestamp)
        
        Returns:
            Query result
        """
        params = {"query": query}
        if time:
            params["time"] = time
        
        return self._request("query", params=params)
    
    def query_range(
        self,
        query: str,
        start: str,
        end: str,
        step: str
    ) -> Dict[str, Any]:
        """
        Execute range query
        
        Args:
            query: PromQL query string
            start: Start time
            end: End time  
            step: Step interval
        
        Returns:
            Range query result
        """
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step
        }
        
        return self._request("query_range", params=params)
    
    def get_metrics(self) -> list:
        """Get all available metrics"""
        return self._request("label/__name__/values")
    
    def get_targets(self) -> Dict[str, Any]:
        """Get scrape target information"""
        return self._request("targets")


# Singleton functions using generic factory
def get_prometheus_client(config: Optional[PrometheusConfig] = None) -> PrometheusClient:
    """
    Get Prometheus client singleton using factory pattern
    
    Args:
        config: Optional configuration, only takes effect on first call
    
    Returns:
        PrometheusClient instance
    """
    return ClientSingleton.get_client(PrometheusClient, config)


def reset_client():
    """Reset client instance (mainly for testing)"""
    ClientSingleton.reset_client(PrometheusClient)


# Export
__all__ = [
    "PrometheusConfig",
    "PrometheusClient", 
    "get_prometheus_client",
    "reset_client"
]