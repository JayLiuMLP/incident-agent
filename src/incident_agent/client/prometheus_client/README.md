# Prometheus Client Module

Lightweight Prometheus client implementation for MCP servers with singleton pattern support.

## Features

- **Singleton Pattern**: Efficient resource usage in MCP servers
- **Fixed Chronosphere URL**: Hardcoded endpoint configuration  
- **Vault Integration**: Automatic token management via general vault
- **Health Checks**: Built-in connectivity testing
- **Comprehensive API**: Instant queries, range queries, metrics listing
- **Error Handling**: Robust error handling and logging

## Module Structure

```
prometheus_client/
├── __init__.py       # Public API exports
├── client.py         # Main client implementation
├── examples.py       # Usage examples and tests
└── README.md         # This documentation
```

## Quick Start

### Basic Usage

```python
from src.incident_agent.client import get_prometheus_client

# Get singleton client (automatic token retrieval from vault)
client = get_prometheus_client()

# Execute instant query
result = client.query("vector(1)")
print(f"Result: {result}")

# Health check
if client.health_check():
    print("Connection OK")
```

### Direct Module Import

```python
from src.incident_agent.client.prometheus_client import get_prometheus_client

# Same functionality as above
client = get_prometheus_client()
```

### Token Management

```python
from src.incident_agent.client import get_default_vault, VaultKeys

# Store token (one-time setup)
vault = get_default_vault()
vault.set(VaultKeys.PROMETHEUS_TOKEN, "your-token-here")

# Client will automatically use the stored token
client = get_prometheus_client()
```

## API Reference

### PrometheusClient Methods

- `query(query: str, time: Optional[str] = None)` - Execute instant query
- `query_range(query: str, start: str, end: str, step: str)` - Execute range query
- `get_metrics()` - Get list of available metrics
- `get_targets()` - Get scrape target information  
- `health_check()` - Test API connectivity

### Configuration

- **URL**: Fixed to `https://doordash.chronosphere.io/data/metrics/api/v1`
- **Token**: Retrieved from vault using `VaultKeys.PROMETHEUS_TOKEN`
- **Timeout**: Configurable via environment variable `PROMETHEUS_TIMEOUT` (default: 30s)

## Examples

Run the examples module to see various usage patterns:

```bash
uv run python -m src.incident_agent.client.prometheus_client.examples
```

## Error Handling

The client includes comprehensive error handling:

- **Connection errors**: HTTP request failures
- **API errors**: Prometheus API error responses  
- **Configuration errors**: Missing URL or token
- **Timeout errors**: Request timeout handling

## Integration

This module integrates seamlessly with:

- **General Vault**: Automatic token storage and retrieval
- **MCP Servers**: Singleton pattern for resource efficiency
- **FastMCP**: Compatible with FastMCP tool decorators
- **Logging**: Structured logging with configurable levels

## Security

- Tokens stored securely in local vault with 600 permissions
- No sensitive data in code or logs
- HTTPS-only communication
- Timeout protection against hanging requests
