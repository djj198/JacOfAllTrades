# Jac ACP Trading Agent MVP

Minimal viable ACP (Agent Client Protocol) agent for JacHacks 2026. This agent provides a base for building graph-native portfolio management tools in DataSpell.

## MVP Features
- Protocol-compliant `initialize` handshake.
- Support for `session/new` with automatic MCP config injection.
- Streaming feedback via `session/update` notifications.
- Static `session/prompt` response (Graph brain integration coming soon).

## Project Structure
- `main.py`: Entry point for stdio transport.
- `src/agent/`: Core domain logic and protocol handlers.
- `src/io/`: Thin transport layer using the ACP SDK.
- `config/`: Configuration templates for DataSpell installation.

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure DataSpell:
   Add the following snippet to your `~/.jetbrains/acp.json` (create the file if it doesn't exist):
   ```json
   {
     "agents": [
       {
         "id": "jac-trading-agent-mvp",
         "name": "Jac Trading Agent MVP",
         "transport": "stdio",
         "command": "/path/to/project/.venv/bin/python",
         "args": ["/path/to/project/main.py"],
         "env": {
           "PYTHONPATH": "/path/to/project"
         }
       }
     ]
   }
   ```
   *Note: Replace `/path/to/project` with the absolute path to this directory.*

4. Restart DataSpell and use the AI Chat tool window to interact with the agent.
