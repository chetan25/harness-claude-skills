# Quick Start — Harness Claude Skills

## What Is This?

A system of 5 skills that ground Claude Code in your project's patterns and conventions.

**Problem**: Claude Code loses context, generates inconsistent code, doesn't match your design  
**Solution**: Analyze your project → inject context → verify output

---

## Installation (2 Minutes)

### Clone Harness into Your Project

```bash
cd your-project
git clone https://github.com/chetan25/harness-claude-skills.git .harness
cd .harness && python setup.py --local
cd ..
```

### Make Command Available (Optional)

```bash
export PATH="$PATH:$(pwd)/.harness/cli"
```

---

## Your First Task

### 1. Analyze Your Project

```bash
harness analyze ./src
```

Generates context files in `.harness/generated/`

### 2. Ask Claude for Context

```bash
harness context "Add user authentication modal"
```

Copy the output into Claude Code.

### 3. Verify Generated Code

```bash
harness verify ./src/components/LoginModal
```

Checks: lint, types, tests, coverage.

---

## Full Workflow Example

```bash
# 1. Analyze (once per project)
harness analyze ./src

# 2. Get context for a feature
harness context "Add dark mode toggle with persistence"

# 3. In Claude Code:
#    - Paste the context from step 2
#    - Ask: "Add dark mode toggle with persistence"
#    - Claude generates code

# 4. Verify
harness verify ./src/features/DarkMode

# 5. Commit
git add . && git commit -m "feat: add dark mode"
```

---

## Commands

```bash
harness analyze ./src                    # Scan project once
harness context "Feature description"    # Get prompt injection
harness orchestrate "Feature"            # Full automated workflow
harness verify ./generated-code          # Lint + type + test
harness status                           # Show project state
harness journal                          # View execution log
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| **[USAGE_GUIDE.md](./USAGE_GUIDE.md)** | Complete how-to guide (READ THIS FIRST) |
| **[INSTALL.md](./INSTALL.md)** | Installation troubleshooting |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | How Harness works (deep dive) |
| **[../README.md](../README.md)** | Feature overview |
| **[../PROJECT_STATUS.md](../PROJECT_STATUS.md)** | Roadmap for Phases 1-5 |

---

## Next Steps

**→ [Read USAGE_GUIDE.md](./USAGE_GUIDE.md) for the full guide**

Or jump to:
- **[Installation Issues?](./INSTALL.md)** 
- **[How Does It Work?](./ARCHITECTURE.md)**
- **[Roadmap & Phases](../PROJECT_STATUS.md)**

---

## The 5 Skills

1. **harness-codebase-analyzer** — Scans your project, extracts patterns
2. **harness-context-loader** — Builds AI-ready prompt injections
3. **harness-code-orchestrator** — Automates the full workflow
4. **harness-verifier** — Validates generated code (lint, type, test)
5. **harness-readme-generator** — Auto-generates documentation

See `skills/*/SKILL.md` for details.

---

**Questions?** Open an issue on GitHub or check the docs above.
