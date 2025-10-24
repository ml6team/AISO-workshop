<p align="center">
  <img src="assets/logo.svg" alt="Project Logo" height="144">
</p>

# GDG Hackathon - ML6 Agent Challenge

Welcome! This repository contains everything you need to build and evaluate an AI agent using Google's Agent Development Kit (ADK).

<p align="center">
  <img src="assets/agent.webp" alt="Agent Illustration" height="144">
</p>


## What You'll Be Working On

**Your main workspace: `my_agent/` folder**

This is where you'll spend most of your time:
- `my_agent/agent.py` - Define your agent's configuration and capabilities
- `my_agent/tools/` - Add custom tools/functions for your agent to use

**Other folders (scaffolding - no need to modify):**
- `scripts/` - Infrastructure code for running and evaluating agents
- `data/` - Test and validation datasets
- `evaluate.py` - Evaluation script (feel free to read and understand it!)

## Quick Start

### 1. Prerequisites

You'll need:
- Python 3.9 or higher
- A Google API key (We will provide one)

### 2. Install uv (Python package manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or via Homebrew (macOS):
```bash
brew install uv
```

### 3. Setup the Project

**Step 1: Copy the environment file**
```bash
# From the project root, navigate to my_agent folder
cd my_agent

# Copy the example environment file
# macOS/Linux
cp .local_env .env

# Windows
copy .local_env .env
```

**Step 2: Add your API key**

Open `my_agent/.env` and replace the placeholder with your actual Google API key:
```
GOOGLE_API_KEY="your_actual_api_key_here"
```

**Step 3: Install dependencies**
```bash
# Go back to project root
cd ..

# Install all dependencies
uv sync
```

That's it! You're ready to start developing.

## Development Workflow

### Option 1: Interactive Development (Recommended)

Use the ADK web interface to test and debug your agent interactively:

```bash
adk web
```

Then open http://127.0.0.1:8000 in your browser. This gives you:
- Live chat interface to test your agent
- Session history to review conversations
- Real-time debugging

**Note:** Session history is lost when you stop the server! To view previous evaluation sessions, see the [Advanced: Viewing Evaluations in the Web UI](#advanced-viewing-evaluations-in-the-web-ui) section below.

### Option 2: Run Evaluations

Test your agent against the validation dataset:

**Evaluate all questions:**
```bash
uv run python evaluate.py
```

**Evaluate a specific question:**
```bash
uv run python evaluate.py --question 0
```
(Replace `0` with any question index)

**Save results to a custom file:**
```bash
uv run python evaluate.py --output my_results.json
```

Results include:
- Total accuracy percentage
- Detailed breakdown per question
- Agent responses and expected answers
- Evaluation method used (string match or LLM judge)

## How to Build Your Agent

### 1. Basic Agent Configuration

Open `my_agent/agent.py`:

```python
from google.adk.agents import llm_agent
from my_agent.tools import web_search

root_agent = llm_agent.Agent(
    model='gemini-2.5-flash-lite',  # or other options such as 'gemini-2.0-flash'
    name='agent',
    description="A helpful assistant that can answer questions.",
    instruction="You are a helpful assistant...",  # Customize this!
    tools=[web_search.web_search],  # Add your tools here
)
```

**Key things to customize:**
- `instruction`: This is your agent's system prompt - be specific about how it should behave
- `tools`: Add custom tools to extend your agent's capabilities
- `model`: Choose the best model for your use case

### 2. Adding Custom Tools

Create new tools in `my_agent/tools/`:

**Example: `my_agent/tools/calculator.py`**
```python
def calculator(operation: str, a: float, b: float) -> float:
    """
    Performs basic arithmetic operations.

    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number

    Returns:
        The result of the operation
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    # ... etc
```

Then import and add it to your agent in `agent.py`:
```python
from google.adk.agents import llm_agent
from my_agent.tools import web_search
from my_agent.tools import calculator

root_agent = llm_agent.Agent(
    # ...
    tools=[web_search.web_search, calculator.calculator],
)
```

### 3. Import Style Guidelines

This project follows Google's Python import style guide:

**Import modules, not individual classes or functions:**

```python
# Good
from google.adk.agents import llm_agent
from my_agent.tools import web_search

agent = llm_agent.Agent(...)
result = web_search.web_search(query)

# Bad
from google.adk.agents.llm_agent import Agent  # Don't import classes
from my_agent.tools.web_search import web_search  # Don't import functions
```

**Exception:** You can directly import from `typing`, `collections.abc`, and `typing_extensions`:
```python
from typing import Optional, List  # This is OK
```

**No relative imports:**
```python
# Good
from my_agent.tools import web_search

# Bad
from .tools import web_search  # Don't use relative imports
```

### 4. Tips for Success

- **Start simple**: Get a basic agent working first, then add complexity
- **Test frequently**: Use `adk web` to interactively test changes
- **Read the docs**: Everything you need to know about using the ADK can be found in the [official ADK documentation](https://google.github.io/adk-docs/)
- **Check out examples**: Browse the [ADK samples repository](https://github.com/google/adk-samples) for inspiration and working examples
- **Understand the dataset**: Look at questions in `benchmark/validation.json` to understand what your agent needs to handle (some have attachments)
- **Iterate**: Run evaluations, analyze failures, improve prompts/tools, repeat!

## Advanced: Viewing Evaluations in the Web UI

If you want to see your evaluation runs in the web interface:

1. **First, start the web UI:**
   ```bash
   adk web
   ```

2. **Then run evaluations in a separate terminal:**
   ```bash
   uv run python evaluate.py
   ```

   or

   ```bash
   uv run python evaluate.py --question 0
   ```

   (Replace `0` with any question index)

This way, all evaluation sessions will appear in the web UI's history (using the same `dev_user` ID).

## Project Structure

```
gdg-hackathon-prep/
├── my_agent/              # ← YOUR WORKSPACE
│   ├── agent.py          # ← Define your agent here
│   ├── tools/            # ← Add custom tools here
│   │   ├── web_search.py # Example tool
│   │   └── __init__.py
│   ├── .local_env        # Example environment file
│   └── .env              # Your API key (create this!)
├── scripts/              # Scaffolding (don't modify)
│   └── agent.py          # Agent runner infrastructure
├── data/                 # Datasets (read-only)
│   ├── validation_sets/  # For testing
│   └── test_set/         # For final evaluation
├── evaluate.py           # Evaluation script
├── pyproject.toml        # Project dependencies
└── README.md             # This file
```

## Troubleshooting

**"Module not found" errors:**
```bash
uv sync
```

**API key issues:**
- Make sure you copied `.local_env` to `.env` in the `my_agent/` folder
- Verify the key is valid at https://aistudio.google.com/app/apikey

**Port already in use:**
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

## Resources

### Official Documentation & Examples

- **ADK Documentation**: https://google.github.io/adk-docs/ - Complete guide on how to use the ADK
- **ADK Samples**: https://github.com/google/adk-samples - Working examples for inspiration
- **Gemini API Docs**: https://ai.google.dev/docs - Reference for Gemini models

### Getting Help

- **Documentation**: Almost everyrthing you need can be found in the official ADK docs linked above
- **Other Issues**: Feel free to reach out to on of our colleagues walking around

Good luck building your agent!
