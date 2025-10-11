# Incident Agent

A Python FastMCP (Model Context Protocol) server for incident management and analysis.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/JayLiuMLP/incident-agent.git
   cd incident-agent
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Verify installation**

   ```bash
   uv run python -c "import fastmcp; print('FastMCP installed successfully!')"
   ```

## Development

- **Run the application**

  ```bash
  uv run python main.py
  ```

- **Run tests**

  ```bash
  uv run pytest
  ```

- **Setup pre-commit hooks**

  ```bash
  uv run pre-commit install
  ```

## Project Structure

- `main.py` - Main application entry point
- `pyproject.toml` - Project configuration and dependencies
- `.cursorrules` - Development guidelines and best practices

## Contributing

This project follows FastMCP development best practices. See `.cursorrules` for detailed development guidelines.
