# Harness Claude Skills

🎯 **Make Claude Code smarter.** Ground AI code generation in your project's patterns, architecture, and conventions. Reduce context loss, style drift, and hallucination.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Status](https://img.shields.io/badge/Status-Alpha-orange)

---

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

### Local Install (Recommended for Now)

```bash
cd your-project
git clone https://github.com/chetandasauni25/harness-claude-skills.git .harness
cd .harness
python setup.py --local
```

Then:
```bash
# From project root
harness analyze ./src
harness orchestrate "Your feature request"
```

---

## What Gets Generated

After `harness analyze ./src`:

```
.harness/generated/
├── harness-patterns-react.md          # Your code style guide
├── harness-patterns-typescript.md     # Type conventions
├── harness-arch-components.md         # Component architecture
├── harness-design-tokens.md           # Colors, spacing, typography
├── harness-test-patterns.md           # How tests are organized
├── harness-api-auth.md                # API contracts
└── diagrams/
    ├── architecture.mermaid
    └── dependency-graph.mermaid
```

These become **grounding context** that Claude Code uses for better output.

---

## Skills Included

### 1. **harness-codebase-analyzer**
Scans your project, generates grounding materials.

```bash
harness analyze ./src
```

**Outputs:**
- Pattern guides (React, TypeScript, testing)
- Architecture diagrams (mermaid)
- Design token extractions

---

### 2. **harness-context-loader**
Builds AI-ready context prompts from analysis.

```bash
harness context "Add user authentication" --include patterns,design-tokens,test-examples
```

**Outputs:** Injection prompts ready for Claude Code

---

### 3. **harness-code-orchestrator**
The main loop: decompose → think → create → verify → test → next.

```bash
harness orchestrate "Add authentication" --parallel-limit 2
```

**Outputs:** Generated code, tests, execution journal

---

### 4. **harness-verifier**
Lint, type-check, test after generation.

```bash
harness verify ./generated-code
```

**Checks:**
- ESLint / Prettier
- TypeScript / mypy
- Test execution
- Coverage thresholds

---

### 5. **harness-readme-generator**
Auto-updates project README with context links.

```bash
harness readme-generate
```

---

## Workflow

### Manual (Step by Step)

```bash
# 1. Analyze codebase once
harness analyze ./src

# 2. Start a task with context
harness context-loader "Add login modal"
# → Returns prompt injection

# 3. Paste into Claude Code with injection
# → Claude generates code

# 4. Verify result
harness verify ./src/components/LoginModal

# 5. Write tests
harness test ./src/components/LoginModal.test.tsx

# 6. Commit
git add .
```

### Automated (Full Harness)

```bash
# One command: decompose, generate, verify, test, commit
harness orchestrate "Add login modal with email/password"

# Check execution log
cat .harness/journal.md
```

---

## Configuration

Create `.harness/config.yaml`:

```yaml
harness:
  project_root: ./src
  project_name: my-app
  
analyzer:
  scan_depth: 5
  exclude:
    - node_modules
    - dist
    - .git
  
  targets:
    - patterns
    - architecture
    - design-tokens
    - test-structure

orchestrator:
  decompose_strategy: claude  # or: rules, hybrid
  parallel_limit: 2
  
  phases:
    think:
      enabled: true
    create:
      enabled: true
      max_retries: 3
    verify:
      enabled: true
      fail_on_error: true
    test:
      enabled: true
      coverage_min: 70

verifier:
  checks:
    - lint
    - type-check
    - test
  
  lint_config: .eslintrc.json
  test_runner: jest
```

---

## Examples

### React App with TypeScript

```bash
cd examples/react-app
harness analyze ./src

# Try it
harness orchestrate "Add dark mode toggle with persistence"
```

### Node Backend

```bash
cd examples/node-backend
harness analyze ./src

# Try it
harness orchestrate "Add JWT authentication middleware"
```

---

## Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| **"Code doesn't match my style"** | Run `harness analyze` to refresh patterns |
| **"Tests keep failing"** | Check `.harness/journal.md`, increase `max_retries` |
| **"It's too slow"** | Exclude `node_modules`, set `parallel_limit: 3` |
| **"Wrong context loaded"** | Manually specify context with `--include patterns,api` |
| **"Coverage dropped"** | Set `coverage_min: 80`, block commit on failure |

---

## Project Structure

```
harness-claude-skills/
├── skills/                          # Skills & context generators
│   ├── harness-codebase-analyzer/
│   ├── harness-context-loader/
│   ├── harness-code-orchestrator/   # Main loop
│   ├── harness-verifier/
│   └── harness-readme-generator/
├── cli/                             # Command-line tool
│   ├── harness-cli.py               # Entry point
│   └── commands/
├── docs/                            # Deep documentation
├── examples/                        # Example projects
└── tests/                           # Test suite
```

---

## Installation Details

### Local Install (`.harness/` folder) - Recommended

```bash
cd my-project
git clone https://github.com/chetandasauni25/harness-claude-skills.git .harness
cd .harness && python setup.py --local

# Creates:
# - .harness/generated/        (project-specific context)
# - .harness/config.yaml       (project config)
```

**Coming Soon:** Global pip/npm packages for system-wide installation.

---

## Commands Reference

```bash
# Analysis
harness analyze ./src                    # Scan project, generate skills
harness analyze ./src --output custom/   # Custom output directory

# Context
harness context "Add auth" --include patterns,design-tokens
harness context "Add modal" --auto-select                     # Auto-pick context

# Orchestration
harness orchestrate "Add user auth"      # Full harness loop
harness think "Add user auth"            # Decompose only (no code gen)

# Verification
harness verify ./generated                # Lint, type-check, test
harness test ./generated.test.ts          # Run tests

# Status & Logs
harness status                           # Show project state
harness journal                          # View execution log
harness journal --last 5                 # Last 5 entries

# Configuration
harness config show                      # Print current config
harness config set orchestrator.parallel_limit 4
```

---

## For Teams

### Share in Your Repo

```bash
# In project root
git add .harness/
git commit -m "chore: add harness skills for AI-assisted development"
git push
```

### Teammates Install

```bash
git clone <your-repo>
cd <your-repo>
.harness/setup.sh --local

# Now they can run:
harness orchestrate "Feature request"
```

---

## Documentation

- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** — Deep dive into design
- **[INSTALL.md](./docs/INSTALL.md)** — Installation details
- **[INTEGRATION.md](./docs/INTEGRATION.md)** — Integration with CI/CD
- **[EXAMPLES.md](./docs/EXAMPLES.md)** — Real use cases
- **[FAQ.md](./docs/FAQ.md)** — Common questions

---

## Development

```bash
# Clone this repo
git clone https://github.com/chetandasauni25/harness-claude-skills.git
cd harness-claude-skills

# Run tests
python -m pytest tests/

# Try example projects
cd examples/react-app
../../cli/harness-cli.py orchestrate "Add feature"
```

---

## Contributing

Issues, PRs, and ideas welcome! This is alpha — we're iterating fast.

---

## Project Status

**Phase 0: Foundation** ✅ COMPLETE
- ✅ Documentation (README, guides, architecture)
- ✅ CLI structure (command recognition)
- ✅ Skill specifications
- ✅ Setup for all platforms (macOS, Linux, Windows)

**Phase 1: CLI Implementation** ⏳ IN PROGRESS
- ❌ `harness analyze` — Scan repo, generate patterns
- ❌ `harness context` — Build prompt injections
- ❌ `harness orchestrate` — Run full workflow
- ❌ `harness verify` — Lint, type-check, test
- ❌ `harness test` — Run tests

**What Works Now:**
- ✅ `harness --help` shows all commands
- ✅ Full documentation and guides
- ✅ CLI structure ready for implementation

**What Returns "Not Implemented":**
- Running any command (Phase 1 in progress)

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the detailed roadmap and implementation timeline.

---

## License

MIT — Use it, modify it, share it.

---

## Built For

Teams who ❤️ Claude + want AI that understands **their** code.

---

**Questions?** Open an issue or check [FAQ.md](./docs/FAQ.md).
