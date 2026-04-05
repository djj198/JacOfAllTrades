## Documentation Model

- **Engineering Source (Repo):** Documentation is authored in real-time in Markdown. The repository is the single source of truth for architecture, design, and verification protocols.
- **Regulatory Records (Greenlight Guru):** On release or at major milestones, approved snapshots of repository documentation are transferred to Greenlight Guru for formal baseline and DHF/RMF inclusion.

## Categorized Structure

| Category | Location | Primary Documents |
|----------|----------|-------------------|
| **1. Context** | [`docs/context/`](docs/context/) | Software Requirements, Build Instructions |
| **2. Architecture** | [`docs/architecture/`](docs/architecture/) | Consolidated Architecture Design Document (AsciiDoc) |

### 1. Context Documents (`docs/context/`)
Defines the environment, requirements, and constraints.
- [Software Requirements](context/software-requirements.md): Lifecycle, SBOM, and Cybersecurity.
- [Build Instructions](context/build-instructions.md): Toolchain and packaging.

### 2. Architecture Documents (`docs/architecture/`)
Contains consolidated system architecture and detailed product design.
- [Architecture Design Document](architecture/ocusciences-architecture.adoc): Consolidated system architecture, Node B architecture, and detailed specification.``

### 3. Traceability Documents (`docs/traceability/`)
Demonstrates compliance and verification.
- [Architectural Decision Record](traceability/architectural-decision-record.md): Consolidated ADR log.
- [CyberSecurity Report](traceability/cybersecurity-report.adoc): Security analysis.
- [Software Integration & Test Protocols](traceability/software-integration-system-test-protocols.md): Risk/Design/Verification Crosswalk.

## Agent Guidance

- **PR Rule:** Documentation must be updated in the same PR as the corresponding code/design changes, adhering to the category-based triggers.
- **Traceability:** Maintain links between categories (e.g., Context → Architecture → Traceability).
- **Style:** Use lowercase hyphenated filenames. Keep content concise and professional.
- **Reference:** See [agents.md](../agents.md) for detailed documentation governance rules.

---

COMPANY CONFIDENTIAL	SOP-03-1; Project Plan Form (SaMD) Page i of n
