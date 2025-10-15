#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstract Client Base Classes
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

from .config import BaseClientConfig

# Load environment variables
load_dotenv()


class BaseAPIClient(ABC):
    """Abstract base class for API clients"""
    
    def __init__(self, config: Optional[BaseClientConfig] = None):
        self.config = config or self._get_default_config()
        self._setup_logger()
        self._validate_config()
    
    @abstractmethod
    def _get_default_config(self) -> BaseClientConfig:
        """Get default configuration instance"""
        pass
    
    def _setup_logger(self):
        """Setup logging for the client"""
        logger_name = f"{self.config.service_name.lower()}_client"
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    @abstractmethod
    def _validate_config(self):
        """Validate configuration - service specific"""
        pass
    
    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers - service specific"""
        pass
    
    @abstractmethod
    def _build_url(self, endpoint: str) -> str:
        """Build API URL - service specific"""
        pass
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Send API request - common implementation with hooks"""
        url = self._build_url(endpoint)
        headers = self._get_headers()
        auth = self._get_auth()
        
        try:
            self.logger.debug(f"Requesting {self.config.service_name} API: {endpoint}")
            
            response = requests.get(
                url, 
                params=params, 
                headers=headers, 
                auth=auth,
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            
            # Allow subclasses to process the response
            return self._process_response(response)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"{self.config.service_name} API request failed: {e}")
            raise
    
    def _get_auth(self):
        """Get authentication info - default implementation"""
        # Can be overridden by subclasses if needed
        return None
    
    def _process_response(self, response) -> Any:
        """Process response - can be overridden by subclasses"""
        result = response.json()
        
        # Common response validation - can be overridden
        return self._validate_response(result)
    
    def _validate_response(self, result: Any) -> Any:
        """Validate API response - default implementation"""
        return result
    
    @abstractmethod
    def health_check(self) -> bool:
        """Health check - service specific implementation"""
        pass
