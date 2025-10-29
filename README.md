<p align="center">
  <img src="assets/logo.svg" alt="Project Logo" height="144">
</p>

# GDG Hackathon - ML6 Agent Challenge

Welcome! This repository contains everything you need to build and evaluate an AI agent using Google's Agent Development Kit (ADK).

<p align="center">
  <img src="assets/agent.webp" alt="Agent Illustration" height="144">
</p>

## 🎯 The Challenge

*"In the era of ChatGPT, clients have ever growing expectations of AI systems. They expect every question to be answered — instantly, flawlessly, and magically. From "Which came first — the chicken or the egg?" to "ChatGPT, can you solve my project?" — they want answers, now.*

*Unfortunately, although modern AI models can already generate impressive outputs, they still lack the **tools and capabilities to solve the most complex questions** some of our clients have.*

*Throughout the years, we have compiled these difficult questions into a dataset to evaluate our internal AI systems. But after years of development, we still have not been able to create a system that satisfies our most critical customers. So today, we are asking for your help!*

*Your challenge is to leverage an AI agent, augmenting their capabilities through the right design, tool use, prompting, and coordination — to find the correct answers to a wide range of complex questions that require multi-step reasoning and digging through files. From history to science, from video interpretation to riddles — **your system should think, not just predict**."*

### What You Need to Build

**An AI agent that can interpret questions (and possibly files) and return accurate answers.**

The questions require your agent to:

- Autonomously extract information from files
- Search the web for relevant information
- Reason about information step-by-step
- Handle multiple topics and modalities (text, images, PDFs, etc.)

**What is an Agent?**

An [agent](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) is an LLM in a loop with the ability to invoke tools (Python functions - which in turn can invoke APIs) and use the output of these tools in the next loop iteration.

This challenge will help you get hands-on experience with building agents and custom tools. Throughout the day, questions of increasing difficulty will be released sequentially - covering different topics, modalities, and durations to test your agent's **accuracy** and **speed**.

### Deliverables

**1. Technical Deliverable**

- Working AI agent code in this repository
- Code must be readable and well-structured
- The agent code MUST be the same as the one used in your demo

**2. Presentation (Short & Functional)**

Your presentation should have two sections:

**Section One: Demo & Insights**

- Show your agent in action
- Share key learnings and insights from development
- Discuss interesting technical challenges you solved

**Section Two: Real-World Application**

- Demonstrate a potential business application
- Showcase ROI and measurable business value
- Present how the agent delivers impact in a realistic context

⚠️ **Important**: Keep the presentation clear and accessible. **Points will be deducted if it is too technical**.

### Judging Criteria

| **Criteria** | **Weight** | **Guiding Questions** |
|-------------|-----------|----------------------|
| Agent Answer Accuracy | 40% | Was the answer given by your agent the same as the ground truth answer in our **hidden test set**? |
| Agent Answer Speed | 10% | What was the average time required to generate correct answers for all questions? |
| Presentation Section One | 20% | Did we clearly see the agent in action? Did we receive interesting insights and learnings? |
| Presentation Section Two | 30% | Did we clearly see the potential and value of the agent for an original use case? |

We will clone your repository and also evaluate the authenticity of your agent.
To allow a smooth evaluation, make sure to properly update the python requirements if you are adding novel packages.

⚠️ **Important Note on Accuracy**: Your final accuracy score will be evaluated on a **hidden test set** that you don't have access to. This test set contains the same types of questions as your training set, but ensures fair evaluation. Use the training set (`benchmark/train.json`) to develop your agent, but avoid overfitting to it!

**Scoring System:**

We use a **100-point system** divided across these criteria and teams.

The **weight** represents the total points available for that criterion. Points are distributed among teams based on performance:

- **Highest-performing team**: 25% of the category's points
- **Second team**: 15%
- **Third team**: 10%
- **Fourth team**: 8%
- **Fifth team**: 6%
- **All other teams**: Equally share the remaining points

**The team with the most total points wins!**

### Submission Format

**Code Submission:**

- Push your code to this GitHub repository
- Keep code readable and well-documented
- **Deadline**: Last commit before the specified deadline will be evaluated

**Presentation Submission:**

- Share a link to your Google Slides presentation
- Presentation must include: Intro, Section One (demo), and Section Two (business case)
- **Grant access** to `cas.coopman@ml6.eu` for the slide deck AND any referenced files (videos, etc.)

## What You'll Be Working On

**Your main workspace: `my_agent/` folder**

This is where you'll spend most of your time:

- `my_agent/agent.py` - Define your agent's configuration and capabilities
- `my_agent/tools/` - Add custom tools/functions for your agent to use

**Other folders (scaffolding - do not modify):**

- `utils/` - Infrastructure code for running and evaluating agents
- `benchmark/` - Train benchmark
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
uv run adk web
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. This gives you:

- Live chat interface to test your agent
- Session history to review conversations
- Real-time debugging

**Note:** Session history is lost when you stop the server! To view previous evaluation sessions, see the [Advanced: Viewing Evaluations in the Web UI](#advanced-viewing-evaluations-in-the-web-ui) section below.

### Option 2: Run Evaluations

Test your agent against the train dataset:

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
- **Timing metrics** - Response time for each question and overall averages

The evaluation tracks response times and provides:

- **Average Response Time (All)**: Average time across all questions
- **Average Response Time (Correct Only)**: Average time for correctly answered questions only

💡 **Tip**: This evaluation runs on the **training set** (`benchmark/train.json`). Your final score will be based on a hidden test set with similar questions, so focus on building a robust, generalizable agent rather than memorizing answers!

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

### 3. Tips for Success

- **Start simple**: Get a basic agent working first, then add complexity
- **Test frequently**: Use `uv run adk web` to interactively test changes
- **Read the docs**: Everything you need to know about using the ADK can be found in the [official ADK documentation](https://google.github.io/adk-docs/)
- **Check out examples**: Browse the [ADK samples repository](https://github.com/google/adk-samples) for inspiration and working examples
- **Understand the dataset**: Look at questions in `benchmark/train.json` to understand what your agent needs to handle (some have attachments)
- **Iterate**: Run evaluations, analyze failures, improve prompts/tools, repeat!

## Advanced: Viewing Evaluations in the Web UI

If you want to see your evaluation runs in the web interface:

1. **First, start the web UI:**

   ```bash
   uv run adk web
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
│   ├── .local_env        # Example environment file
│   └── .env              # Your API key (create this!)
├── scripts/              # Scaffolding (don't modify)
│   └── server.py         # Agent runner infrastructure
├── benchmark/            # Train dataset (read-only)
│   ├── attachments/      # Files to answer some questions
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
- Verify the API key variable has been set

**Port already in use:**

```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

## Resources

### Official Documentation & Examples

- **ADK Documentation**: [https://google.github.io/adk-docs/](https://google.github.io/adk-docs/) - Complete guide on how to use the ADK
- **ADK Samples**: [https://github.com/google/adk-samples](https://github.com/google/adk-samples) - Working examples for inspiration
- **Gemini API Docs**: [https://ai.google.dev/docs](https://ai.google.dev/docs) - Reference for Gemini models

### Agent Design & Best Practices

- **Building Effective Agents**: [https://www.anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents) - Anthropic's guide on agent design patterns and workflows
- **Writing Tools for Agents**: [https://www.anthropic.com/engineering/writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents) - Best practices for creating effective agent tools

### Getting Help

- **Documentation**: Almost everything you need can be found in the official ADK docs linked above
- **Other Issues**: Feel free to reach out to one of the ML6 ML Engineers walking around

Good luck building your agent! 🚀

### About ML6

ML6 is a frontier, international AI engineering company, constantly pushing the boundaries of what's possible with AI. We partner with bold leaders to turn cutting-edge AI into lasting business impact. With over a decade of proven expertise, we deliver AI that reshapes business models. AI that is reliable and secure, ensuring a lasting impact. From strategy to delivery, we don't just follow the hype—we build the future.
