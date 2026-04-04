**Hackathon MVP Goal**: Deliver a working, installable ACP agent that demonstrates end-to-end protocol compliance and prepares the foundation for deep graph-native portfolio management.

---

## Build & Test

- **Virtual Environment**: Always use the `.venv` located in the project root. Activate with `source .venv/bin/activate` (Unix/macOS) or `.venv\Scripts\activate` (Windows).
- **Dependencies**:
  - Python dependencies (ACP SDK, MCP client libraries, etc.) must be added to `requirements.txt`.
  - Jac/Jaseci dependencies and toolchain commands must be documented in `docs/context/jac-setup.md`.
  - Update both `requirements.txt` and `pyproject.toml` (if used) when adding or changing dependencies.
- **Testing & Verification**:
  - Test all scripts using `if __name__ == "__main__":` blocks for quick local verification before committing.
  - Validate ACP compliance by launching the agent manually via terminal and simulating stdio communication.
  - Once installed in DataSpell, test via the AI Chat tool window with simple prompts.
  - Ensure all file paths are relative to the project root. Use `pathlib.Path(__file__).parent` or `os.path.abspath(os.path.dirname(__file__))` patterns.
- **Data Paths**: Use `data/raw/` for input files (e.g., sample MCP responses, test payloads) and `data/processed/` for generated outputs (e.g., serialized graph snapshots, visualization JSON). Never hardcode absolute user-specific directories.

---

## Core Rules

- **Primitives & Graph Entities**: All data structures (session state, MCP config wrappers, primitives) in Python must use immutable dataclasses. Graph entities (Asset, Position, TradeEvent, RiskNode, etc.) live in pure Jac and follow Jaseci node/edge conventions.
- **Strict Separation of Concerns**:
  - **IO/Transport Layer**: Responsible only for stdio handling, JSON-RPC plumbing, and SDK wiring. Must remain thin and delegate immediately to core logic.
  - **Core Domain Layer**: Contains handler implementations, session management, MCP client glue, and hooks for Jac walkers/`by llm()`.
  - **Jac Graph Layer**: All agentic reasoning, portfolio state, decision making, and functional traversals live here.
- **Metadata & Config Handling**: When parsing ACP messages or the injected MCP configuration from DataSpell, use safe access patterns such as `getattr(obj, "AttributeName", "Default")` to prevent `AttributeError`.
- **Alignment**: Identifiers and structures must remain compatible with the official ACP schema (via the Python SDK) and Alpaca MCP tool signatures.

---

## Code Style (Cython/Nuitka-Friendly + Jac-Compatible)

To support future single-binary packaging (PyInstaller), Cython optimization, or Nuitka compilation for performance and IP protection, while maintaining clean Jac interop, follow these mandatory practices:

- **Strict Type Hinting**: Every Python function must include complete type annotations for all arguments and return values.  
  *Example*: `async def handle_prompt(request: PromptRequest) -> PromptResponse:`
- **Pure Functions**: Heavy logic, graph traversal wrappers, and reasoning steps should be implemented as standalone pure functions that do not depend on `self` where feasible. This aligns naturally with pure Jac walkers.
- **Fixed Variable Types**: Do not reuse a variable name for a different type within the same function or scope.
- **Immutable State**: Use `@dataclasses.dataclass(frozen=True)` for all Python primitives and session state objects. In Jac, prefer functional updates via new nodes/edges rather than mutation.
- **NumPy Usage**: Use `numpy.ndarray` only when necessary (e.g., for risk calculations or visualization data). Prefer native Jaseci graph operations for portfolio state.
- **Jac Style Alignment**: Keep Python code minimal and protocol-focused. All intelligent decision-making and graph operations must route through `.jac` files using walkers and `by llm()`.

---

## Naming Conventions (Strictly Enforced)

- **Classes**: `PascalCase` (e.g., `JacTradingAgent`, `AcpSessionState`, `PortfolioGraphService`).
- **Functions / Variables**: `snake_case` with clear verb/adjective/noun format (e.g., `handle_initialize`, `parse_mcp_config`, `traverse_portfolio_graph`).
- **Private Members**: Use a leading underscore for internal state, maps, or helper methods (e.g., `self._sessions`, `_send_notification`).
- **CONSTANTS**: `SCREAMING_SNAKE_CASE` (e.g., `DEFAULT_CAPABILITIES`, `ACP_PROTOCOL_VERSION`).
- **Jac-Specific Naming**: Follow Jaseci conventions — nodes (`AssetNode`), edges (`HAS_POSITION`), walkers (`PortfolioQueryWalker`).

---

## Architecture

- **IO vs. Core Split** (Mandatory):
  - `src/io/` or `src/transport/`: Contains **only** stdio JSON-RPC handling, `AgentSideConnection`, and low-level ACP SDK wiring. This layer must delegate immediately to core.
  - `src/agent/` or `src/core/`: Contains domain logic, protocol handlers (`initialize`, `session/new`, `session/prompt`), session state, MCP client wrapper, and Jac bridge.
  - `jac/`: Pure Jac files defining nodes, edges, walkers, and agentic reasoning.
- **Primitive-Service Split**:
  - Primitives and dataclasses live in `src/core/primitives/` (data structures only).
  - All logic, processing, and graph operations belong in services (`src/core/services/`) or dedicated Jac walkers.
- **Context Managers**: Use `@contextmanager` for resource-heavy operations (e.g., loading Jac graph state or establishing MCP connections).
- **Session Management**: Maintain per-`sessionId` state (MCP config, graph reference) in memory. Prefer immutable structures.
- **Recommended Project Structure**:
jac-acp-agent/
├── .venv/
├── jac/                          # Pure Jac graph brain (nodes, edges, walkers, by llm())
├── src/
│   ├── agent/                    # Core domain logic & handlers
│   │   ├── core.py
│   │   ├── handlers.py
│   │   └── models.py
│   ├── io/                       # Transport & protocol plumbing only
│   │   ├── transport.py
│   │   └── connection.py
│   └── core/
│       ├── primitives/
│       └── services/
├── main.py                       # Thin entry point for stdio launch
├── requirements.txt
├── pyproject.toml
├── config/
│   └── example_acp.json
├── data/
│   ├── raw/
│   └── processed/
└── docs/                         # Auto-documentation


---

## Gotchas

- **Immutable State**: Because primitives and session state are frozen, use `dataclasses.replace()` in Python or create new edges/nodes in Jac for updates.
- **MCP Config Injection**: The Alpaca MCP configuration (including tokens) is automatically injected by DataSpell into the `session/new` handshake. Never prompt the user for tokens inside the agent.
- **Jac Interop**: Keep the Python layer strictly protocol and transport focused. All reasoning must be delegated to Jac walkers.
- **No Runtime Imports**: List all imports at the top of every Python file.
- **Hackathon Constraints**: Prioritize a working `initialize` + `session/new` + basic `session/prompt` (with streaming notifications) before adding full graph logic or trading features.

---

## Techniques

- **Safe Parsing**: Always handle optional or injected fields gracefully in ACP and MCP messages.
- **Streaming UX**: Liberally use `session/update` notifications to provide responsive, real-time feedback inside DataSpell (e.g., "Thinking…", tool call progress, partial results).
- **Pure Functional Design**: Align Python wrappers with the project’s strictly functional, graph-native philosophy.

---

## Auto-Documentation Paradigm (24hr Hackathon Edition)

**Core Mindset**  
Treat documentation as **code**. Update documentation in the **same commit** as the related code changes. No deferred updates — this is especially critical during the fast-paced 24-hour hackathon.

### What Must Be Updated (Minimal Set)

| Change Type                          | Document to Update                                              | When |
|--------------------------------------|-----------------------------------------------------------------|------|
| Architectural / design change        | `docs/architecture/project-architecture.adoc`                   | Component boundaries, IO-Core split, Jac interop, new subsystems |
| Significant decision                 | `docs/traceability/architectural-decision-record.md`            | New tech choice, major pattern, deployment or security decision |
| Dependency added/updated/removed     | `requirements.txt` + `pyproject.toml` + `docs/context/dependencies.md` | Always |
| Version bump                         | `pyproject.toml` + `docs/context/release-notes.md`              | For any working demo or release |
| Risk-relevant code changes           | `docs/traceability/software-integration-system-test-protocols.md` | ACP protocol, MCP client, graph updates, permission handling |
| New Jac graph feature                | `docs/architecture/jac-graph-model.adoc`                        | New nodes, edges, walkers, or `by llm()` usage |

### Documentation Locations

- **Context**: `docs/context/` — software requirements, build instructions, DataSpell installation guide, Alpaca MCP setup.
- **Architecture**: `docs/architecture/` — consolidated design document (`project-architecture.adoc`), Jac graph reference, IO-Core split.
- **Traceability**: `docs/traceability/` — architectural decision records (ADRs), test protocols, deployment notes, token handling security.
- **Templates**: `docs/templates/`
- **Overview**: `docs/README.md`

**Dependency Management**:
- Update `requirements.txt` when adding Python packages (e.g., `agent-client-protocol`).
- Document Jac toolchain setup and versions in `docs/context/jac-setup.md`.
- Keep version pins consistent across files.
