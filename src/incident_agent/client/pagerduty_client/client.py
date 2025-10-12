#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PagerDuty Client Implementation using Abstract Base Classes
For MCP servers with singleton pattern support
"""

import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from ..base import BaseClientConfig, BaseAPIClient, ClientSingleton
from ..auth.vault import VaultKeys

# Constants
PAGERDUTY_API_HOST = "https://api.pagerduty.com"


@dataclass
class PagerDutyConfig(BaseClientConfig):
    """PagerDuty configuration class"""
    
    api_host: str = PAGERDUTY_API_HOST
    api_key: Optional[str] = None
    default_services: List[str] = field(default_factory=lambda: ["ML Platform", "Model Development Platform"])
    page_limit: int = 100
    
    @property
    def service_name(self) -> str:
        return "PagerDuty"
    
    @property
    def vault_token_key(self) -> str:
        return VaultKeys.PAGERDUTY_TOKEN
    
    @property
    def env_token_keys(self) -> List[str]:
        return ["PAGERDUTY_USER_API_KEY", "PAGERDUTY_TOKEN"]
    
    def _set_token(self, token: Optional[str]):
        self.api_key = token
    
    def _load_env_config(self):
        super()._load_env_config()
        
        # Parse default services from environment
        service_names_env = os.environ.get("PD_SERVICE_NAMES", "")
        default_services = [name.strip() for name in service_names_env.split(",") if name.strip()]
        if default_services:
            self.default_services = default_services
        
        self.page_limit = int(os.environ.get("PAGERDUTY_PAGE_LIMIT", str(self.page_limit)))


class PagerDutyClient(BaseAPIClient):
    """PagerDuty client implementation using abstract base class"""
    
    def _get_default_config(self) -> PagerDutyConfig:
        return PagerDutyConfig.from_vault()
    
    def _validate_config(self):
        if not self.config.api_host:
            raise ValueError("PagerDuty API host not configured")
        if not self.config.api_key:
            raise ValueError("PagerDuty API key not found. Please set it using: from src.incident_agent.client.auth import get_default_vault, VaultKeys; get_default_vault().set(VaultKeys.PAGERDUTY_TOKEN, 'your_token')")
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Token token={self.config.api_key}",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-Type": "application/json"
        }
    
    def _build_url(self, endpoint: str) -> str:
        return f"{self.config.api_host.rstrip('/')}/{endpoint.lstrip('/')}"
    
    def health_check(self) -> bool:
        """Health check - verify API connectivity"""
        try:
            response_data = self._request("services", {"limit": 1})
            return "services" in response_data
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    # PagerDuty-specific helper methods
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
    
    # PagerDuty-specific methods
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
            self.logger.error(f"Failed to get service ID for {service_name}: {e}")
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
                    self.logger.warning(f"Service not found: {name}")
            
            if service_ids:
                params["service_ids[]"] = service_ids
            else:
                self.logger.warning("No valid service IDs found")
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
        
        self.logger.info(f"Querying incidents from {since} to {until}")
        
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


# Singleton functions using generic factory  
def get_pagerduty_client(config: Optional[PagerDutyConfig] = None) -> PagerDutyClient:
    """
    Get PagerDuty client singleton using factory pattern
    
    Args:
        config: Optional configuration, only takes effect on first call
    
    Returns:
        PagerDutyClient instance
    """
    return ClientSingleton.get_client(PagerDutyClient, config)


def reset_client():
    """Reset client instance (mainly for testing)"""
    ClientSingleton.reset_client(PagerDutyClient)


# Export
__all__ = [
    "PagerDutyConfig",
    "PagerDutyClient", 
    "get_pagerduty_client",
    "reset_client"
]