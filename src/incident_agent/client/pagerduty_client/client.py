#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight PagerDuty Client
For MCP servers with singleton pattern support
"""

import os
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from ..auth.vault import get_default_vault, VaultKeys

# Load environment variables
load_dotenv()

# Constants
PAGERDUTY_API_HOST = "https://api.pagerduty.com"

# Configure logging
logger = logging.getLogger('pagerduty_client')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class PagerDutyConfig:
    """PagerDuty configuration class"""
    api_host: str = PAGERDUTY_API_HOST
    api_key: Optional[str] = None
    default_services: List[str] = field(default_factory=lambda: ["ML Platform", "Model Development Platform"])
    timeout: int = 30
    page_limit: int = 100

    @classmethod
    def from_vault(cls) -> 'PagerDutyConfig':
        """Create configuration from local vault"""
        vault = get_default_vault()
        api_key = vault.get(VaultKeys.PAGERDUTY_TOKEN)
        
        if not api_key:
            # If no token in vault, try to get from environment and store it
            api_key = os.environ.get("PAGERDUTY_USER_API_KEY") or os.environ.get("PAGERDUTY_TOKEN")
            if api_key:
                vault.set(VaultKeys.PAGERDUTY_TOKEN, api_key)
        
        # Parse default services from environment
        service_names_env = os.environ.get("PD_SERVICE_NAMES", "")
        default_services = [name.strip() for name in service_names_env.split(",") if name.strip()]
        if not default_services:
            default_services = ["ML Platform", "Model Development Platform"]
        
        return cls(
            api_host=PAGERDUTY_API_HOST,
            api_key=api_key,
            default_services=default_services,
            timeout=int(os.environ.get("PAGERDUTY_TIMEOUT", "30")),
            page_limit=int(os.environ.get("PAGERDUTY_PAGE_LIMIT", "100"))
        )


class PagerDutyClient:
    """Lightweight PagerDuty client"""
    
    def __init__(self, config: Optional[PagerDutyConfig] = None):
        self.config = config or PagerDutyConfig.from_vault()
        self._validate_config()
        
    def _validate_config(self):
        """Validate configuration"""
        if not self.config.api_host:
            raise ValueError("PagerDuty API host not configured")
        if not self.config.api_key:
            raise ValueError("PagerDuty API key not found. Please set it using: from src.incident_agent.client.auth import get_default_vault, VaultKeys; get_default_vault().set(VaultKeys.PAGERDUTY_TOKEN, 'your_token')")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Token token={self.config.api_key}",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-Type": "application/json"
        }
    
    def _build_url(self, endpoint: str) -> str:
        """Build API URL"""
        return f"{self.config.api_host.rstrip('/')}/{endpoint.lstrip('/')}"
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Send API request"""
        url = self._build_url(endpoint)
        headers = self._get_headers()
        
        try:
            logger.debug(f"Requesting PagerDuty API: {endpoint}")
            
            response = requests.get(
                url, 
                params=params, 
                headers=headers,
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"PagerDuty API request failed: {e}")
            raise
    
    def _paginated_request(self, endpoint: str, params: Optional[Dict] = None) -> List[Any]:
        """Send paginated API request"""
        all_items = []
        offset = 0
        
        while True:
            page_params = dict(params or {})
            page_params.update({
                "offset": offset,
                "limit": self.config.page_limit
            })
            
            response_data = self._request(endpoint, page_params)
            
            # Determine the key for items based on endpoint
            if 'incidents' in endpoint:
                items_key = 'incidents'
            elif 'services' in endpoint:
                items_key = 'services'
            else:
                # Try to find the key automatically
                for key in response_data.keys():
                    if isinstance(response_data[key], list):
                        items_key = key
                        break
                else:
                    items_key = 'data'  # fallback
            
            page_items = response_data.get(items_key, [])
            all_items.extend(page_items)
            
            if not response_data.get("more", False):
                break
                
            offset += len(page_items)
        
        return all_items
    
    def get_service_id_by_name(self, service_name: str) -> Optional[str]:
        """Get service ID by exact service name"""
        try:
            params = {
                "query": service_name,
                "include[]": "teams",
            }
            
            services = self._paginated_request("services", params)
            
            # Prefer exact name match
            for svc in services:
                if svc.get("name") == service_name:
                    return svc.get("id")
            
            # Fallback: case-insensitive match
            for svc in services:
                if svc.get("name", "").lower() == service_name.lower():
                    return svc.get("id")
            
            return None
        except Exception as e:
            logger.error(f"Failed to get service ID for {service_name}: {e}")
            return None
    
    def get_incidents(
        self,
        statuses: Optional[List[str]] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        service_names: Optional[List[str]] = None,
        sort_by: str = "created_at:desc"
    ) -> List[Dict]:
        """Get incidents with filters"""
        params = {
            "sort_by": sort_by
        }
        
        if statuses:
            params["statuses[]"] = statuses
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        
        # Resolve service IDs if service names provided
        if service_names:
            service_ids = []
            for name in service_names:
                sid = self.get_service_id_by_name(name)
                if sid:
                    service_ids.append(sid)
                else:
                    logger.warning(f"Service not found: {name}")
            
            if service_ids:
                params["service_ids[]"] = service_ids
            else:
                logger.warning("No valid service IDs found")
                return []
        
        incidents = self._paginated_request("incidents", params)
        
        # Double-check filtering by service name if provided
        if service_names:
            service_name_set = set(service_names)
            incidents = [
                inc for inc in incidents
                if inc.get("service", {}).get("summary") in service_name_set
            ]
        
        return incidents
    
    def get_this_week_resolved_incidents(self, service_names: Optional[List[str]] = None) -> List[Dict]:
        """Get resolved incidents for current week"""
        # Calculate this week's date range
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        next_monday = monday + timedelta(days=7)
        
        since = monday.isoformat() + "Z"
        until = next_monday.isoformat() + "Z"
        
        logger.info(f"Querying incidents from {since} to {until}")
        
        service_names = service_names or self.config.default_services
        
        return self.get_incidents(
            statuses=["resolved"],
            since=since,
            until=until,
            service_names=service_names,
            sort_by="resolved_at:desc"
        )
    
    def get_open_incidents(self, service_names: Optional[List[str]] = None) -> List[Dict]:
        """Get currently open incidents"""
        service_names = service_names or self.config.default_services
        
        return self.get_incidents(
            statuses=["triggered", "acknowledged"],
            service_names=service_names,
            sort_by="created_at:desc"
        )
    
    def get_services(self) -> List[Dict]:
        """Get all services"""
        return self._paginated_request("services")
    
    def health_check(self) -> bool:
        """Health check - verify API connectivity"""
        try:
            response_data = self._request("services", {"limit": 1})
            return "services" in response_data
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global singleton instance
_pagerduty_client_instance: Optional[PagerDutyClient] = None


def get_pagerduty_client(config: Optional[PagerDutyConfig] = None) -> PagerDutyClient:
    """
    Get PagerDuty client singleton
    
    Args:
        config: Optional configuration, only takes effect on first call
    
    Returns:
        PagerDutyClient instance
    """
    global _pagerduty_client_instance
    
    if _pagerduty_client_instance is None:
        _pagerduty_client_instance = PagerDutyClient(config)
        logger.info("Created new PagerDuty client instance")
    
    return _pagerduty_client_instance


def reset_client():
    """Reset client instance (mainly for testing)"""
    global _pagerduty_client_instance
    _pagerduty_client_instance = None


# Export
__all__ = [
    "PagerDutyConfig",
    "PagerDutyClient", 
    "get_pagerduty_client",
    "reset_client"
]
