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
- **No verification**: Code ships without linting, testing, type-checking

## The Solution

**Harness** is a system of Hermes skills that:

1. **Scan** your codebase (structure, patterns, tests, design tokens)
2. **Ground** Claude with explicit context (mermaid diagrams, pattern examples)
3. **Orchestrate** multi-task workflows with verification loops
4. **Verify** generated code (lint → type-check → test → ship)

### Example: Add User Authentication

```bash
harness orchestrate "Add user authentication with email/password"
```

Harness will:
- ✅ Break down into tasks (hook, form components, routes, tests)
- ✅ Load context (your React patterns, auth APIs, design tokens)
- ✅ Generate each component (Claude Code with grounding)
- ✅ Verify (ESLint, TypeScript, tests)
- ✅ Ship with confidence

---

## Quick Start

### Option 1: Local Install (Try It First)

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

### Option 2: Global Install (After You Love It)

```bash
pip install harness-claude-skills
harness init my-project
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

These become **Hermes skills** that Claude uses as context.

---

## Skills Included

### 1. **harness-codebase-analyzer**
Scans your project, generates grounding materials.

```bash
hermes skill harness-codebase-analyzer --scan-root ./src
```

**Outputs:**
- Pattern skills (React, TypeScript, testing)
- Architecture diagrams (mermaid)
- Design token extractions

---

### 2. **harness-context-loader**
Builds AI-ready context prompts from analysis.

```bash
hermes skill harness-context-loader \
  --task "Add user authentication" \
  --include patterns,design-tokens,test-examples
```

**Outputs:** Injection prompts ready for Claude Code

---

### 3. **harness-code-orchestrator**
The main loop: decompose → think → create → verify → test → next.

```bash
hermes skill harness-code-orchestrator \
  --requirement "Add authentication" \
  --parallel-limit 2
```

**Outputs:** Generated code, tests, execution journal

---

### 4. **harness-verifier**
Lint, type-check, test after generation.

```bash
hermes skill harness-verifier ./generated-code
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
hermes skill harness-readme-generator
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
├── skills/                          # Hermes skills
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

### Local Install (`.harness/` folder)

```bash
cd my-project
git clone https://github.com/chetandasauni25/harness-claude-skills.git .harness
cd .harness && python setup.py --local

# Creates:
# - .harness/generated/        (project-specific skills)
# - .harness/config.yaml       (project config)
# - ~/.hermes/skills/harness-* (symlinks)
```

### Global Install (System-wide)

```bash
pip install harness-claude-skills
# or: npm install -g harness-claude-skills

harness init my-project

# Creates:
# - ~/.harness/config.yaml          (global settings)
# - ~/.hermes/skills/harness-*      (installed globally)
# - my-project/.harness-config.yaml (project overrides)
```

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

## License

MIT — Use it, modify it, share it.

---

## Built For

Teams who ❤️ Claude + want AI that understands **their** code.

---

**Questions?** Open an issue or check [FAQ.md](./docs/FAQ.md).
