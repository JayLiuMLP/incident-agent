#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prometheus Client Usage Examples
"""

import os
from typing import Dict, Any

from .prometheus_client import get_prometheus_client, PrometheusConfig
from .auth.vault import get_default_vault, VaultKeys


def example_basic_usage():
    """Basic usage example"""
    # Method 1: Use configuration from local vault (recommended)
    client = get_prometheus_client()
    
    try:
        # Health check
        if not client.health_check():
            print("Prometheus connection failed")
            return
        
        # Execute simple query (limit result count)
        result = client.query("up{job=\"prometheus\"}")
        print(f"Query result: {len(result.get('result', []))} time series")
        
        # If above query fails, try simpler one
        if not result.get('result'):
            result = client.query("prometheus_build_info")
            print(f"Fallback query result: {len(result.get('result', []))} time series")
        
        # Get metrics list (first 10)
        metrics = client.get_metrics()[:10]
        print(f"Available metrics: {metrics}")
        
    except Exception as e:
        print(f"Query failed: {e}")


def example_custom_config():
    """Custom configuration example"""
    # Method 2: Manually create configuration (not recommended since URL is now constant)
    config = PrometheusConfig(
        token="your-token-here",
        org_id="your-org-id",
        timeout=60
    )
    
    client = get_prometheus_client(config)
    
    try:
        # Execute range query
        result = client.query_range(
            query="up",
            start="2024-01-01T00:00:00Z",
            end="2024-01-01T01:00:00Z",
            step="5m"
        )
        print(f"Range query result: {len(result.get('result', []))} time series")
        
    except Exception as e:
        print(f"Range query failed: {e}")


def example_vault_management():
    """Local vault management example"""
    print("=== Vault Management ===")
    
    vault = get_default_vault()
    
    # Check current token
    current_token = vault.get(VaultKeys.PROMETHEUS_TOKEN)
    if current_token:
        print(f"Current token: {current_token[:20]}...")
    else:
        print("No token found in vault")
    
    # List all keys in vault
    keys = vault.list_keys()
    print(f"Keys in vault: {keys}")
    
    # Set new token (if needed)
    # vault.set(VaultKeys.PROMETHEUS_TOKEN, "new-token-here")
    
    # Delete specific token (if needed)  
    # vault.delete(VaultKeys.PROMETHEUS_TOKEN)
    
    # Clear entire vault (if needed)
    # vault.clear()


def example_mcp_server_usage():
    """MCP server usage example"""
    def prometheus_tool_function(query: str) -> Dict[str, Any]:
        """
        Use Prometheus client in MCP tool
        """
        # Get singleton client
        client = get_prometheus_client()
        
        try:
            # Execute query
            result = client.query(query)
            
            return {
                "success": True,
                "data": result,
                "query": query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    # Usage example
    result = prometheus_tool_function("vector(1)")
    print(f"MCP tool result: {result}")


if __name__ == "__main__":
    print("=== Prometheus Client Basic Usage ===")
    example_basic_usage()
    
    print("\n=== Custom Configuration Usage ===")
    example_custom_config()
    
    print("\n=== Vault Management ===")
    example_vault_management()
    
    print("\n=== MCP Server Usage Example ===")
    example_mcp_server_usage()
