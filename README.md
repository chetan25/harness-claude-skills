# Harness Claude Skills

**AI Dev Team Coordinator** — Orchestrate Claude to build complete features with verification, testing, and design compliance.

Instead of asking Claude to "add dark mode," you ask Harness to orchestrate it. Harness coordinates sub-agents, verifies everything (code, UI, tests, lint/types, design), and ships when ready.

## The Problem

Claude Code is powerful but struggles with:
- **Context decay**: Each invocation starts fresh
- **Style drift**: Generated code doesn't match existing patterns
- **Hallucination**: Wrong APIs, missing types, inconsistent conventions
- **Multi-step coordination**: No guidance for complex features
- **No verification**: Code ships without design/lint/test validation

## The Solution

**Harness** is an AI dev team coordinator with three layers:

### 1. **Skill Builder** (Auto-Generate if Missing)
Scans your project and auto-generates skills:
- React/Vue/Angular patterns
- TypeScript conventions
- Test framework patterns
- Design tokens & color systems
- API integration examples

### 2. **Harness Context** (Ground Claude)
Injects generated skills into Claude's context:
- Claude now understands YOUR conventions
- Fewer hallucinations
- Consistent code style

### 3. **Orchestrator** (Multi-Layer Process)
Coordinates Claude agents through 7 phases:

```
User: "Add dark mode toggle"
    ↓
[1] Problem Analysis: Break into subtasks
[2] Context Loading: Gather skills + Figma design
[3] Code Generation: Multi-agent team writes code
[4] Visual Verification: Verify in UI + against Figma
[5] Testing: Write/run tests
[6] Re-Verification: Final lint/type/design checks
[7] Completion: Ship when ready
```

### Example: Add User Authentication

```
@harness orchestrate "Add user authentication with email/password"
```

Harness will:
- ✅ Analyze the task (hook + form + routes + tests)
- ✅ Load skills (React patterns, auth APIs, test examples)
- ✅ Spawn sub-agents for each component
- ✅ Verify each piece matches your conventions
- ✅ Verify UI against Figma design (if provided)
- ✅ Run full test suite
- ✅ Check lint/types
- ✅ Ship with confidence

---

## Quick Start

### 1. Clone into Your Project

```bash
cd your-project
git clone https://github.com/chetan25/harness-claude-skills.git .harness
```

### 2. Use in Claude Code

```
@harness orchestrate "Add dark mode toggle"
```

Claude auto-detects `.harness/` and runs the full workflow.

---

## Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** — 2-minute setup, first command
- **[Claude Commands](docs/CLAUDE_COMMANDS.md)** — All available commands & examples
- **[Architecture](docs/ARCHITECTURE.md)** — How it works, deep dive with Mermaid diagrams
- **[Usage Guide](docs/USAGE_GUIDE.md)** — Full workflow, advanced tips
- **[Installation](docs/INSTALL.md)** — Detailed setup for all platforms

---

## How It Works

**Behind the scenes:**

```
Claude Code IDE
    ↓
@harness command triggered
    ↓
Auto-detect `.harness/` folder
    ↓
Analyze project (first time) or load cache
    ↓
Generate Mermaid diagrams for architecture
    ↓
Extract code patterns & conventions
    ↓
Inject everything into Claude's system prompt
    ↓
Claude executes (fully grounded)
    ↓
Coordinate sub-agents for each subtask
    ↓
Verify code + UI + tests + lint/types + design
    ↓
Ship when everything passes
```

---

## Skills Included

Harness includes 5 core skills that work together:

1. **harness-codebase-analyzer** — Scans your project, extracts patterns, generates Mermaid diagrams
2. **harness-context-loader** — Builds AI-ready context prompts from analysis
3. **harness-code-orchestrator** — Coordinates multi-agent workflow (7 phases)
4. **harness-verifier** — Lint, type-check, test verification
5. **harness-readme-generator** — Keeps documentation in sync

---

## Project Structure

```
.harness/
├── skills/                          # 5 core skill definitions
│   ├── harness-codebase-analyzer/
│   ├── harness-context-loader/
│   ├── harness-code-orchestrator/
│   ├── harness-verifier/
│   └── harness-readme-generator/
│
├── generated/                       # Auto-generated on first run
│   ├── patterns.json               # Extracted code patterns
│   ├── architecture.md             # Component structure
│   ├── diagrams.mermaid            # Visual architecture
│   ├── design-tokens.json          # Colors, spacing, etc.
│   ├── cache.json                  # Analysis metadata
│   └── skills-summary.md
│
├── config.yaml                      # Project config (generated)
├── cli/
│   ├── harness-cli.py              # Legacy fallback (CLI)
│   └── ... 
└── docs/
    ├── ARCHITECTURE.md
    ├── CLAUDE_COMMANDS.md
    ├── GETTING_STARTED.md
    └── ...
```

---

## What Gets Cached

After first analysis, Harness caches:

```
.harness/generated/
├── patterns.json              # React/TypeScript/testing patterns
├── architecture.md            # Component relationships
├── diagrams.mermaid           # Mermaid diagrams for architecture
├── design-tokens.json         # Colors, spacing, typography
├── cache.json                 # Metadata & timestamps
└── skills-summary.md          # What was detected
```

Cache automatically updates when you edit code. Clear with `@harness cache refresh`.

---

## Project Status

**Phase 0: Foundation** ✅ COMPLETE
- ✅ Architecture designed
- ✅ Documentation with Mermaid diagrams
- ✅ 5 skills defined and documented
- ✅ Claude Command structure ready
- ✅ Installation tested

**Phase 1: Implementation** ⏳ IN PROGRESS
- Skill Builder (analyze + diagram generation)
- Claude Command integration
- Cache management
- Orchestrator (7-phase workflow)
- Verification engine

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for timeline and details.

---

## Contributing

Issues, PRs, and ideas welcome! This is alpha — we're iterating fast.

---

## License

MIT — Use it, modify it, share it.

---

## Built For

Teams who ❤️ Claude + want AI that understands **their** code.

---

**Get started:** [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
