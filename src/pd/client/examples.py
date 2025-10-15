#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PagerDuty Client Usage Examples
"""

from typing import Dict, Any, List
from .client import get_pagerduty_client, PagerDutyConfig
from ..auth.vault import get_default_vault, VaultKeys


def example_basic_usage():
    """Basic usage example"""
    print("=== PagerDuty Client Basic Usage ===")
    
    try:
        # Get singleton client (automatic token retrieval from vault)
        client = get_pagerduty_client()
        
        # Health check
        if not client.health_check():
            print("❌ PagerDuty connection failed")
            return
        
        print("✅ Connection successful")
        
        # Get this week's resolved incidents
        resolved_incidents = client.get_this_week_resolved_incidents()
        print(f"This week resolved incidents: {len(resolved_incidents)}")
        
        # Get open incidents
        open_incidents = client.get_open_incidents()
        print(f"Currently open incidents: {len(open_incidents)}")
        
        # Display some details
        if resolved_incidents:
            incident = resolved_incidents[0]
            print(f"\nLatest resolved incident:")
            print(f"  #{incident['incident_number']}: {incident['title']}")
            print(f"  Service: {incident['service']['summary']}")
            print(f"  Resolved at: {incident.get('resolved_at')}")
            print(f"  URL: {incident['html_url']}")
        
        if open_incidents:
            incident = open_incidents[0]
            print(f"\nLatest open incident:")
            print(f"  #{incident['incident_number']}: {incident['title']}")
            print(f"  Service: {incident['service']['summary']}")
            print(f"  Status: {incident['status']}")
            print(f"  Urgency: {incident['urgency']}")
            print(f"  Created at: {incident['created_at']}")
            print(f"  URL: {incident['html_url']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_vault_management():
    """Vault management example"""
    print("=== Vault Management ===")
    
    vault = get_default_vault()
    
    # Check current token
    current_token = vault.get(VaultKeys.PAGERDUTY_TOKEN)
    if current_token:
        print(f"Current token: {current_token[:20]}...")
    else:
        print("No token found in vault")
        print("To set token: vault.set(VaultKeys.PAGERDUTY_TOKEN, 'your-pagerduty-token')")
    
    # List all keys
    keys = vault.list_keys()
    print(f"Keys in vault: {keys}")


def example_custom_queries():
    """Custom query examples"""
    print("=== Custom Queries ===")
    
    client = get_pagerduty_client()
    
    try:
        # Get incidents from specific services
        incidents = client.get_incidents(
            statuses=["resolved"],
            service_names=["ML Platform"],
            sort_by="resolved_at:desc"
        )
        print(f"ML Platform resolved incidents: {len(incidents)}")
        
        # Get high urgency open incidents
        incidents = client.get_incidents(
            statuses=["triggered", "acknowledged"]
        )
        high_urgency = [i for i in incidents if i['urgency'] == 'high']
        print(f"High urgency open incidents: {len(high_urgency)}")
        
        # Display incident summary
        if incidents:
            display_incident_summary(incidents)
        
    except Exception as e:
        print(f"❌ Query error: {e}")


def example_service_management():
    """Service management examples"""
    print("=== Service Management ===")
    
    client = get_pagerduty_client()
    
    try:
        # Get all services
        services = client.get_services()
        print(f"Total services: {len(services)}")
        
        # Display first few services
        print("\nSample services:")
        for service in services[:5]:
            print(f"  - {service['name']} (ID: {service['id']})")
        
        # Test service ID resolution
        service_name = "ML Platform"
        service_id = client.get_service_id_by_name(service_name)
        if service_id:
            print(f"\nService '{service_name}' ID: {service_id}")
        else:
            print(f"\nService '{service_name}' not found")
        
    except Exception as e:
        print(f"❌ Service query error: {e}")


def display_incident_summary(incidents: List[Dict]):
    """Display incident summary statistics"""
    if not incidents:
        print("No incidents to display")
        return
    
    print(f"\n📊 Incident Summary ({len(incidents)} total)")
    print("=" * 50)
    
    # Group by urgency
    urgency_counts = {}
    for incident in incidents:
        urgency = incident['urgency']
        urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
    
    print("By urgency:")
    for urgency, count in urgency_counts.items():
        print(f"  {urgency}: {count}")
    
    # Group by service  
    service_counts = {}
    for incident in incidents:
        service = incident['service']['summary']
        service_counts[service] = service_counts.get(service, 0) + 1
    
    print("\nBy service:")
    for service, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {service}: {count}")
    
    # Group by status
    status_counts = {}
    for incident in incidents:
        status = incident['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\nBy status:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")


def example_mcp_server_usage():
    """MCP server usage example"""
    def pagerduty_tool_function(query_type: str = "this_week_resolved") -> Dict[str, Any]:
        """
        Use PagerDuty client in MCP tool
        """
        # Get singleton client
        client = get_pagerduty_client()
        
        try:
            if query_type == "this_week_resolved":
                incidents = client.get_this_week_resolved_incidents()
            elif query_type == "open":
                incidents = client.get_open_incidents()
            else:
                return {
                    "success": False,
                    "error": f"Unknown query type: {query_type}",
                    "query_type": query_type
                }
            
            return {
                "success": True,
                "data": {
                    "incident_count": len(incidents),
                    "incidents": incidents[:5] if incidents else [],  # Return first 5 for brevity
                    "query_type": query_type
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_type": query_type
            }
    
    # Usage example
    print("=== MCP Server Usage Example ===")
    
    result = pagerduty_tool_function("this_week_resolved")
    print(f"This week resolved incidents result: {result['success']}")
    if result['success']:
        print(f"Count: {result['data']['incident_count']}")
    
    result = pagerduty_tool_function("open")
    print(f"Open incidents result: {result['success']}")
    if result['success']:
        print(f"Count: {result['data']['incident_count']}")


if __name__ == "__main__":
    print("=== PagerDuty Client Examples ===\n")
    
    example_basic_usage()
    print("\n" + "="*60 + "\n")
    
    example_vault_management()  
    print("\n" + "="*60 + "\n")
    
    example_custom_queries()
    print("\n" + "="*60 + "\n")
    
    example_service_management()
    print("\n" + "="*60 + "\n")
    
    example_mcp_server_usage()
