#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight Prometheus Client
For MCP servers with singleton pattern support
"""

import os
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

from .auth.vault import get_default_vault, VaultKeys

# Load environment variables
load_dotenv()

# Constants
PROMETHEUS_URL = "https://doordash.chronosphere.io/data/metrics/api/v1"

# Configure logging
logger = logging.getLogger('prometheus_client')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)




@dataclass
class PrometheusConfig:
    """Prometheus configuration class"""
    url: str = PROMETHEUS_URL
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    org_id: Optional[str] = None
    timeout: int = 30

    @classmethod
    def from_vault(cls) -> 'PrometheusConfig':
        """Create configuration from local vault"""
        vault = get_default_vault()
        token = vault.get(VaultKeys.PROMETHEUS_TOKEN)
        
        if not token:
            # If no token in vault, try to get from environment and store it
            token = os.environ.get("PROMETHEUS_TOKEN") or os.environ.get("CHRONOSPHERE_TOKEN")
            if token:
                vault.set(VaultKeys.PROMETHEUS_TOKEN, token)
        
        return cls(
            url=PROMETHEUS_URL,
            token=token,
            org_id=os.environ.get("ORG_ID", ""),
            timeout=int(os.environ.get("PROMETHEUS_TIMEOUT", "30"))
        )


class PrometheusClient:
    """Lightweight Prometheus client"""
    
    def __init__(self, config: Optional[PrometheusConfig] = None):
        self.config = config or PrometheusConfig.from_vault()
        self._validate_config()
        
    def _validate_config(self):
        """Validate configuration"""
        if not self.config.url:
            raise ValueError("Prometheus URL not configured")
        if not self.config.token:
            raise ValueError("Prometheus token not found. Please set it using: from src.incident_agent.client.auth import get_default_vault, VaultKeys; get_default_vault().set(VaultKeys.PROMETHEUS_TOKEN, 'your_token')")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        
        if self.config.org_id:
            headers["X-Scope-OrgID"] = self.config.org_id
            
        return headers
    
    def _get_auth(self):
        """Get authentication info"""
        if self.config.username and self.config.password:
            return requests.auth.HTTPBasicAuth(self.config.username, self.config.password)
        return None
    
    def _build_url(self, endpoint: str) -> str:
        """Build API URL"""
        base_url = self.config.url.rstrip('/')
        
        # If URL already contains api/v1, don't add it again
        if base_url.endswith('/api/v1') or '/api/v1' in base_url:
            return f"{base_url}/{endpoint}"
        else:
            return f"{base_url}/api/v1/{endpoint}"
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Send API request"""
        url = self._build_url(endpoint)
        headers = self._get_headers()
        auth = self._get_auth()
        
        try:
            logger.debug(f"Requesting Prometheus API: {endpoint}")
            
            response = requests.get(
                url, 
                params=params, 
                headers=headers, 
                auth=auth,
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status") != "success":
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Prometheus API error: {error_msg}")
                raise ValueError(f"Prometheus API error: {error_msg}")
            
            return result["data"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Prometheus API request failed: {e}")
            raise
    
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
    
    def health_check(self) -> bool:
        """Health check"""
        try:
            # Use simple health check, only test API connectivity
            url = self._build_url("query")
            headers = self._get_headers()
            auth = self._get_auth()
            
            # Use a simple query to test connection
            response = requests.get(
                url,
                params={"query": "vector(1)"},  # Simple constant query
                headers=headers,
                auth=auth,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("status") == "success"
            
            return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global singleton instance
_prometheus_client_instance: Optional[PrometheusClient] = None


def get_prometheus_client(config: Optional[PrometheusConfig] = None) -> PrometheusClient:
    """
    Get Prometheus client singleton
    
    Args:
        config: Optional configuration, only takes effect on first call
    
    Returns:
        PrometheusClient instance
    """
    global _prometheus_client_instance
    
    if _prometheus_client_instance is None:
        _prometheus_client_instance = PrometheusClient(config)
        logger.info("Created new Prometheus client instance")
    
    return _prometheus_client_instance


def reset_client():
    """Reset client instance (mainly for testing)"""
    global _prometheus_client_instance
    _prometheus_client_instance = None


# Export
__all__ = [
    "PrometheusConfig",
    "PrometheusClient", 
    "get_prometheus_client",
    "reset_client"
]
