# 🚀 Full Guide to Using Claude Code

Everything you need to know to crush building anything with Claude Code! This guide takes you from installation through advanced context engineering, subagents, hooks, and parallel agent workflows.

## 📋 Prerequisites

- Terminal/Command line access
- Node.js installed (for Claude Code installation)
- GitHub account (for GitHub CLI integration)
- Text editor (VS Code recommended)

## 🔧 Installation

**macOS/Linux:**
```bash
npm install -g @anthropic-ai/claude-code
```

**Windows (WSL recommended):**
See detailed instructions in [install_claude_code_windows.md](./install_claude_code_windows.md)

**Verify installation:**
```bash
claude --version
```

---

## ✅ TIP 1: CREATE AND OPTIMIZE CLAUDE.md FILES

Claude Code reads `CLAUDE.md` files to understand your project rules, conventions, and patterns.

**Essential CLAUDE.md Structure:**
```markdown
### 🔄 Project Awareness & Context
- Always read PLANNING.md at conversation start
- Check TASK.md before starting new tasks
- Use consistent naming conventions and patterns

### 🧱 Code Structure & Modularity  
- Never create files longer than 500 lines
- Organize code into clearly separated modules
- Use clear, consistent imports

### 🧪 Testing & Reliability
- Always create unit tests for new features
- Tests should live in /tests folder
- Include happy path, edge case, and failure tests

### 📎 Style & Conventions
- Use Python as primary language
- Follow PEP8, use type hints, format with black
- Use pydantic for data validation
- Write docstrings for every function
```

**Pro Tips:**
- ✅ Be specific about your conventions (import style, error handling patterns)
- ✅ Include gotchas and common mistakes to avoid
- ✅ Reference example files for patterns to follow
- ✅ Update CLAUDE.md as your project evolves

---

## ✅ TIP 2: LEVERAGE EXAMPLES/ FOLDER

The examples/ folder is your secret weapon. Claude performs 10x better when it can see patterns to follow.

**Essential Examples Structure:**
```
examples/
├── README.md           # Explains what each demonstrates
├── agents/
│   ├── basic_agent.py  # Simple agent pattern
│   ├── tool_agent.py   # Agent with tools
│   └── multi_agent.py  # Multi-agent coordination
├── tools/
│   ├── api_tool.py     # External API integration
│   └── database_tool.py # Database operations
└── tests/
    ├── test_agent.py   # Unit test patterns
    └── conftest.py     # Pytest configuration
```

**What to Include:**
- Code structure patterns
- Testing approaches
- Integration examples
- Error handling patterns
- Configuration management

---

## ✅ TIP 3: MASTER THE PRP WORKFLOW

PRPs (Product Requirements Prompts) are the core of context engineering:

**1. Create INITIAL.md:**
```markdown
## FEATURE:
Build an async web scraper using BeautifulSoup that extracts product data, handles rate limiting, and stores results in PostgreSQL

## EXAMPLES:
- examples/scraper_basic.py - Basic scraping pattern
- examples/rate_limiter.py - Rate limiting implementation

## DOCUMENTATION:
- https://docs.python-requests.org/en/master/
- https://www.postgresql.org/docs/current/

## OTHER CONSIDERATIONS:
- Handle 429 rate limit responses
- Use connection pooling for database
- Include retry logic with exponential backoff
```

**2. Generate PRP:**
```bash
/generate-prp INITIAL.md
```

**3. Execute PRP:**
```bash
/execute-prp PRPs/your-feature-name.md
```

---

## ✅ TIP 4: CONTEXT ENGINEERING BEST PRACTICES

**1. Be Information Dense:**
- Include specific API endpoints, methods, parameters
- Reference exact file paths and line numbers
- Provide complete error messages and stack traces

**2. Use Validation Loops:**
```markdown
### Level 1: Syntax
- ruff check . --fix
- mypy .

### Level 2: Tests  
- pytest tests/ -v
- Coverage should be >80%

### Level 3: Integration
- Start service: uv run python main.py
- Test endpoint: curl -X POST localhost:8000/api
```

**3. Include Anti-Patterns:**
```markdown
## Don't Do This:
- ❌ Don't hardcode API keys
- ❌ Don't use sync functions in async context  
- ❌ Don't ignore rate limits
```

---

## ✅ TIP 5: EFFECTIVE TOOL USAGE

**Custom Commands in .claude/commands/:**

Create powerful slash commands:

**.claude/commands/test-feature.md:**
```markdown
# Test Feature Command

Run comprehensive tests for a specific feature.

## Usage
/test-feature [feature_name]

## Implementation
```bash
# Run unit tests
uv run pytest tests/test_$ARGUMENTS.py -v

# Run integration tests  
uv run pytest tests/integration/test_$ARGUMENTS.py -v

# Check coverage
uv run pytest --cov=$ARGUMENTS --cov-report=term-missing
```
```

---

## 🔥 ADVANCED PATTERNS

### Multi-Agent Workflows
- Use agent-as-tool pattern for complex tasks
- Pass context between agents efficiently
- Handle token limits with smart context pruning

### Context Management
- Keep context files under 50KB for best performance
- Use hierarchical context (project → module → function)
- Implement context refresh patterns for long sessions

### Quality Gates
- Automated linting and formatting
- Comprehensive test coverage
- Integration test suites
- Performance benchmarks

---

## 📚 Resources

- [Context Engineering Principles](../README.md)
- [PRP Templates](../PRPs/templates/)
- [Example Projects](../use-cases/)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)

---

**Remember**: Context Engineering is about providing Claude with ALL the information it needs to succeed. The more comprehensive your context, the better your results!
