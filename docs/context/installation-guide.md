# ACP Agent Installation Guide

Detailed instructions for installing and testing the Jac ACP Trading Agent MVP in DataSpell.

## Prerequisites
- DataSpell 2024.1+ (with ACP support)
- Python 3.10+
- `.venv` virtual environment (recommended)

## Step 1: Prepare the Environment
Ensure you have installed the required dependencies as outlined in the `README.md`.

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install ACP SDK and other dependencies
pip install -r requirements.txt
```

## Step 2: Configure DataSpell
DataSpell reads agent configurations from `~/.jetbrains/acp.json`.

1. Open or create `~/.jetbrains/acp.json`.
2. Append the agent configuration (ensure it's valid JSON):
   ```json
   {
     "agents": [
       {
         "id": "jac-trading-agent-mvp",
         "name": "Jac Trading Agent MVP",
         "transport": "stdio",
         "command": "/absolute/path/to/project/.venv/bin/python",
         "args": ["/absolute/path/to/project/main.py"],
         "env": {
           "PYTHONPATH": "/absolute/path/to/project"
         }
       }
     ]
   }
   ```
3. Ensure all paths are absolute and point correctly to your local environment.

## Step 3: Interaction in AI Chat
1. Launch DataSpell.
2. Open the **AI Chat** tool window.
3. Select "Jac Trading Agent MVP" from the agent selector.
4. DataSpell will automatically call `initialize` and `session/new` (injecting your configured Alpaca MCP tokens if applicable).
5. Send a message (e.g., "Show me my current portfolio risk.").
6. You should see a notification "Analyzing portfolio graph state..." followed by "Hello from Jac ACP Trading Agent MVP. Graph brain coming soon."

## Verification & Troubleshooting
- **No Agent in Selector**: Check the format of `~/.jetbrains/acp.json` and ensure the `id` is unique.
- **Agent Crashes**: Check the DataSpell logs (`Help -> Show Log in Explorer`).
- **Manual Test**: Run `.venv/bin/python main.py` manually in a terminal. The agent should stay alive and wait for stdio input.
- **Python Path**: Ensure `PYTHONPATH` includes the project root so `import src` works.
