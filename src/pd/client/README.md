# PagerDuty Client Module

Lightweight PagerDuty client implementation for MCP servers with singleton pattern support.

## Features

- **Singleton Pattern**: Efficient resource usage in MCP servers
- **Vault Integration**: Automatic token management via general vault
- **Comprehensive API**: Incidents, services, and custom queries
- **Pagination Support**: Automatic handling of API pagination
- **Flexible Filtering**: By status, service, time range, etc.
- **Error Handling**: Robust error handling and logging
- **Health Checks**: Built-in connectivity testing

## Module Structure

```
pagerduty_client/
├── __init__.py       # Public API exports
├── client.py         # Main client implementation
├── examples.py       # Usage examples and tests
└── README.md         # This documentation
```

## Quick Start

### Basic Usage

```python
from src.incident_agent.client import get_pagerduty_client

# Get singleton client (automatic token retrieval from vault)
client = get_pagerduty_client()

# Get this week's resolved incidents
resolved = client.get_this_week_resolved_incidents()
print(f"This week: {len(resolved)} resolved incidents")

# Get open incidents
open_incidents = client.get_open_incidents()
print(f"Currently: {len(open_incidents)} open incidents")
```

### Direct Module Import

```python
from src.incident_agent.client.pagerduty_client import get_pagerduty_client

# Same functionality as above
client = get_pagerduty_client()
```

### Token Management

```python
from src.incident_agent.client import get_default_vault, VaultKeys

# Store token (one-time setup)
vault = get_default_vault()
vault.set(VaultKeys.PAGERDUTY_TOKEN, "your-pagerduty-api-key")

# Client will automatically use the stored token
client = get_pagerduty_client()
```

## API Reference

### PagerDutyClient Methods

#### Core Methods
- `get_incidents(statuses, since, until, service_names, sort_by)` - Generic incident query
- `get_this_week_resolved_incidents(service_names)` - Current week resolved incidents
- `get_open_incidents(service_names)` - Currently open incidents
- `get_services()` - Get all services
- `get_service_id_by_name(service_name)` - Resolve service name to ID
- `health_check()` - Test API connectivity

#### Advanced Queries

```python
# Custom incident query
incidents = client.get_incidents(
    statuses=["triggered", "acknowledged", "resolved"],
    since="2024-01-01T00:00:00Z",
    until="2024-01-31T23:59:59Z",
    service_names=["ML Platform", "Data Pipeline"],
    sort_by="created_at:desc"
)

# High urgency incidents
high_urgency = [i for i in incidents if i['urgency'] == 'high']

# Recent incidents by service
service_incidents = {}
for incident in incidents:
    service = incident['service']['summary']
    if service not in service_incidents:
        service_incidents[service] = []
    service_incidents[service].append(incident)
```

### Configuration

- **API Host**: Fixed to `https://api.pagerduty.com`
- **Token**: Retrieved from vault using `VaultKeys.PAGERDUTY_TOKEN`
- **Default Services**: Configurable via environment variable `PD_SERVICE_NAMES`
- **Timeout**: Configurable via environment variable `PAGERDUTY_TIMEOUT` (default: 30s)
- **Page Limit**: Configurable via environment variable `PAGERDUTY_PAGE_LIMIT` (default: 100)

### Environment Variables

```bash
# Required (or stored in vault)
PAGERDUTY_USER_API_KEY=your-api-key

# Optional
PD_SERVICE_NAMES="Service 1,Service 2,Service 3"
PAGERDUTY_TIMEOUT=30
PAGERDUTY_PAGE_LIMIT=100
```

## Examples

### Basic Incident Retrieval

```python
client = get_pagerduty_client()

# This week's resolved incidents
resolved = client.get_this_week_resolved_incidents()
for incident in resolved:
    print(f"#{incident['incident_number']}: {incident['title']}")
    print(f"  Service: {incident['service']['summary']}")
    print(f"  Resolved: {incident.get('resolved_at')}")

# Open incidents  
open_incidents = client.get_open_incidents()
for incident in open_incidents:
    print(f"#{incident['incident_number']}: {incident['title']}")
    print(f"  Status: {incident['status']}")
    print(f"  Urgency: {incident['urgency']}")
```

### Service Management

```python
# Get all services
services = client.get_services()
for service in services:
    print(f"- {service['name']} (ID: {service['id']})")

# Resolve service name to ID
service_id = client.get_service_id_by_name("ML Platform")
if service_id:
    print(f"ML Platform ID: {service_id}")
```

### Custom Filtering

```python
from datetime import datetime, timedelta

# Last month's incidents
end = datetime.now()
start = end - timedelta(days=30)

incidents = client.get_incidents(
    statuses=["resolved"],
    since=start.isoformat() + "Z", 
    until=end.isoformat() + "Z",
    service_names=["Critical Service"]
)

print(f"Last 30 days: {len(incidents)} incidents")
```

### Statistics and Analysis

```python
incidents = client.get_this_week_resolved_incidents()

# Group by urgency
urgency_counts = {}
for incident in incidents:
    urgency = incident['urgency']
    urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1

print("This week by urgency:")
for urgency, count in urgency_counts.items():
    print(f"  {urgency}: {count}")

# Average resolution time
from datetime import datetime
total_resolution_time = 0
resolved_count = 0

for incident in incidents:
    if incident.get('resolved_at') and incident.get('created_at'):
        created = datetime.fromisoformat(incident['created_at'].replace('Z', '+00:00'))
        resolved = datetime.fromisoformat(incident['resolved_at'].replace('Z', '+00:00'))
        resolution_time = (resolved - created).total_seconds() / 3600  # hours
        total_resolution_time += resolution_time
        resolved_count += 1

if resolved_count > 0:
    avg_resolution = total_resolution_time / resolved_count
    print(f"Average resolution time: {avg_resolution:.2f} hours")
```

## Running Examples

Run the examples module to see various usage patterns:

```bash
uv run python -m src.incident_agent.client.pagerduty_client.examples
```

## Error Handling

The client includes comprehensive error handling:

- **Connection errors**: HTTP request failures
- **API errors**: PagerDuty API error responses  
- **Configuration errors**: Missing API host or key
- **Timeout errors**: Request timeout handling
- **Service resolution**: Graceful handling of unknown services

## Integration

This module integrates seamlessly with:

- **General Vault**: Automatic token storage and retrieval
- **MCP Servers**: Singleton pattern for resource efficiency
- **FastMCP**: Compatible with FastMCP tool decorators
- **Logging**: Structured logging with configurable levels

## MCP Tool Example

```python
from src.incident_agent.client import get_pagerduty_client

@mcp.tool()
async def get_current_incidents(ctx: Context) -> str:
    """Get currently open incidents"""
    try:
        client = get_pagerduty_client()
        incidents = client.get_open_incidents()
        
        if not incidents:
            return "No open incidents found."
        
        result = f"Found {len(incidents)} open incidents:\n\n"
        for incident in incidents[:5]:  # Show first 5
            result += f"#{incident['incident_number']}: {incident['title']}\n"
            result += f"  Service: {incident['service']['summary']}\n"
            result += f"  Status: {incident['status']} | Urgency: {incident['urgency']}\n"
            result += f"  Created: {incident['created_at']}\n\n"
        
        if len(incidents) > 5:
            result += f"... and {len(incidents) - 5} more incidents"
        
        return result
        
    except Exception as e:
        await ctx.error(f"Failed to get incidents: {e}")
        return f"Error retrieving incidents: {str(e)}"
```

## Security

- Tokens stored securely in local vault with 600 permissions
- No sensitive data in code or logs
- HTTPS-only communication
- Timeout protection against hanging requests
- Environment variable fallback for configuration
