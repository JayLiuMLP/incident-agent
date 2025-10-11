## FEATURE

Doordash internal MCP to help the software engineer collect the incident signals from the metric, log and traces and troubleshooting the incidents.

## EXAMPLES

The `examples/fastmcp/` folder contains comprehensive FastMCP service implementation patterns:

### Basic Service Patterns

- `examples/fastmcp/examples/simple_echo.py` - Minimal FastMCP server with single tool definition, perfect starting point
- `examples/fastmcp/examples/echo.py` - Complete service example showing all four MCP components:
  - Tools: `@mcp.tool` for executable functions
  - Static Resources: `@mcp.resource("echo://static")` for fixed data
  - Dynamic Resource Templates: `@mcp.resource("echo://{text}")` for parameterized data access
  - Prompts: `@mcp.prompt("echo")` for LLM prompt templates

### Real-World Service Examples

- `examples/fastmcp/examples/desktop.py` - File system resource access with `dir://desktop` protocol
- `examples/fastmcp/examples/config_server.py` - Command-line configurable server with argument parsing
- `examples/fastmcp/examples/mount_example.py` - Service composition and mounting patterns

### Advanced Multi-Service Architecture

- `examples/fastmcp/examples/smart_home/` - Complete smart home automation system demonstrating:
  - **Service Composition**: `hub.py` mounting `lights_mcp` under "hue" prefix
  - **Modular Design**: Separate services for different device types (lights, future thermostat, etc.)
  - **Enterprise Integration**: Philips Hue bridge integration with proper error handling
  - **Type Safety**: Using `HueAttributes` TypedDict for parameter validation
  - **Configuration Management**: Environment-based settings for device connections

### Key Implementation Patterns to Follow

- **Decorator-based API**: Use `@mcp.tool`, `@mcp.resource()`, `@mcp.prompt()` decorators
- **Type Annotations**: Full type safety with Pydantic models and TypedDict
- **Error Handling**: Return structured success/error responses instead of raising exceptions
- **Resource URI Design**: Follow hierarchical naming like `protocol://category/item/{param}`
- **Service Mounting**: Use `mcp.mount("prefix", sub_service)` for modular architecture
- **Configuration**: Use `pyproject.toml` dependencies and `.fastmcp.json` for deployment config

## DOCUMENTATION

[List out any documentation (web pages, sources for an MCP server like Crawl4AI RAG, etc.) that will need to be referenced during development]

## OTHER CONSIDERATIONS

[Any other considerations or specific requirements - great place to include gotchas that you see AI coding assistants miss with your projects a lot]
