# Authentication & Vault Module

This module provides secure local storage for sensitive data like API tokens and keys.

## Features

- **Secure Local Storage**: Stores sensitive data in `~/.incident_agent/vault.json` with restrictive file permissions (600)
- **Multiple Token Support**: Supports various token types (Prometheus, GitHub, OpenAI, etc.)
- **Easy API**: Simple get/set/delete operations
- **Singleton Pattern**: Default vault instance for convenience
- **Thread-Safe**: Safe for concurrent access

## Usage

### Basic Operations

```python
from src.incident_agent.client.auth import get_default_vault, VaultKeys

# Get default vault instance
vault = get_default_vault()

# Store tokens
vault.set(VaultKeys.PROMETHEUS_TOKEN, "your-prometheus-token")
vault.set(VaultKeys.GITHUB_TOKEN, "your-github-token")
vault.set(VaultKeys.OPENAI_API_KEY, "your-openai-key")

# Retrieve tokens
prometheus_token = vault.get(VaultKeys.PROMETHEUS_TOKEN)
github_token = vault.get(VaultKeys.GITHUB_TOKEN)

# List all stored keys
keys = vault.list_keys()
print(f"Stored keys: {keys}")

# Check if key exists
if vault.exists(VaultKeys.PROMETHEUS_TOKEN):
    print("Prometheus token found")

# Delete specific token
vault.delete(VaultKeys.GITHUB_TOKEN)

# Clear all tokens
vault.clear()
```

### Convenience Functions

```python
from src.incident_agent.client.auth import get_token, set_token, delete_token, VaultKeys

# Shorthand operations using default vault
set_token(VaultKeys.PROMETHEUS_TOKEN, "your-token")
token = get_token(VaultKeys.PROMETHEUS_TOKEN)
delete_token(VaultKeys.PROMETHEUS_TOKEN)
```

### Custom Vault Location

```python
from src.incident_agent.client.auth.vault import LocalVault
from pathlib import Path

# Create vault in custom location
custom_vault = LocalVault(Path("/custom/path/vault.json"))
custom_vault.set("custom_key", "custom_value")
```

## Supported Token Types

The `VaultKeys` class provides constants for common token types:

- `VaultKeys.PROMETHEUS_TOKEN` - Prometheus/Chronosphere API token
- `VaultKeys.GITHUB_TOKEN` - GitHub API token
- `VaultKeys.OPENAI_API_KEY` - OpenAI API key
- `VaultKeys.ANTHROPIC_API_KEY` - Anthropic API key

## Security

- Vault file is created with 600 permissions (readable/writable by owner only)
- JSON format for human readability
- No encryption (relies on filesystem permissions)
- Automatic directory creation

## Integration with Prometheus Client

The Prometheus client automatically uses the vault for token storage:

```python
from src.incident_agent.client import get_prometheus_client
from src.incident_agent.client.auth import get_default_vault, VaultKeys

# Store token first
vault = get_default_vault()
vault.set(VaultKeys.PROMETHEUS_TOKEN, "your-prometheus-token")

# Client will automatically use the stored token
client = get_prometheus_client()
result = client.query("vector(1)")
```
