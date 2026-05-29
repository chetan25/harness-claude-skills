# Quick Start — Harness Claude Skills

## What Is This?

A system of 5 Hermes skills that ground Claude Code in your project's patterns and conventions.

**Problem**: Claude Code loses context, generates inconsistent code, doesn't match your design  
**Solution**: Analyze your project → inject context → verify output

## Try It Locally

```bash
cd /tmp/harness-claude-skills

# Read the overview
cat README.md

# Understand the design
cat docs/ARCHITECTURE.md

# Check the roadmap
cat PROJECT_STATUS.md
```

## File Guide

| File | Purpose |
|------|---------|
| `README.md` | Feature overview, quick start |
| `docs/ARCHITECTURE.md` | Deep dive on design & components |
| `docs/INSTALL.md` | Installation instructions |
| `PROJECT_STATUS.md` | Roadmap for Phases 1-5 |
| `skills/*/SKILL.md` | Individual skill documentation |

## Next Steps

**Option A: Push to GitHub**
```bash
# Tell me your GitHub username & desired repo name
# I'll create the repo and push for you
```

**Option B: Build Phase 1 (CLI Tool)**
```bash
# Implement harness-cli.py with commands:
# - harness analyze ./src
# - harness orchestrate "Feature request"
# - harness context "Description"
# - harness verify ./output
# - harness test ./output.test.ts
```

**Option C: Build Phase 2 (Analyzer)**
```bash
# Implement codebase scanning:
# - Language detection
# - AST parsing
# - Pattern extraction
# - Dependency graphs
# - Mermaid diagrams
```

## The 5 Skills

1. **harness-codebase-analyzer** — Scan → Extract patterns → Generate diagrams
2. **harness-context-loader** — Load patterns → Build AI-ready prompts
3. **harness-code-orchestrator** — Main loop (decompose → think → create → verify → test)
4. **harness-verifier** — Lint, type-check, test, validate
5. **harness-readme-generator** — Auto-update docs

See `skills/*/SKILL.md` for details on each.

## Git

```bash
# Current state
git log --oneline
# 6278de2 docs: add project status and implementation roadmap
# ebe488d chore: initial harness-claude-skills repo

# View files
git ls-files

# Add to GitHub
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin master
```

## Questions?

- **Architecture?** → See `docs/ARCHITECTURE.md`
- **Installation?** → See `docs/INSTALL.md`
- **Roadmap?** → See `PROJECT_STATUS.md`
- **How do I contribute?** → Pick Phase 1-5, follow the tasks in `PROJECT_STATUS.md`

---

**Ready?** Let me know your next move!
