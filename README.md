# Harness Claude Skills

**Ground Claude Code in your project's patterns. Zero friction. Just ask.**

Instead of guessing, Claude now understands your code. Ask for features naturally, and Harness orchestrates the full development loop: decompose → context → code → verify → test → ship.

---

## The Problem

Claude Code is powerful but has blind spots:

- **Context decay** — Each prompt starts from scratch, losing project knowledge
- **Style drift** — Generated code doesn't match your patterns & conventions
- **Hallucination** — Wrong APIs, missing types, inconsistent naming
- **Complex features** — Multi-step tasks need coordination
- **No verification** — Code ships without tests, linting, or design validation

---

## The Solution: Harness

**Harness** automates the entire development workflow:

### 1️⃣ **Analyze** (One Time)
```
Claude scans your project:
  ✓ Detects tech stack (React, Node, Python, etc.)
  ✓ Extracts code patterns & conventions
  ✓ Maps architecture
  ✓ Finds design tokens
  ✓ Understands test structure
```

### 2️⃣ **Generate Context** (Automatic)
Creates `.claude/skills/` — Your project's codebook:
- `patterns-react.md` — React style guide
- `architecture.md` — Component structure
- `design-tokens.md` — Colors, spacing, fonts
- `test-patterns.md` — How you test
- `orchestrator.md` — Multi-task coordination template

### 3️⃣ **Orchestrate** (On Every Prompt)
When you ask Claude for a feature:
```
User: "Add dark mode with persistence"
    ↓
Claude reads .claude/skills/ (your context)
    ↓
Orchestrator runs 7-phase loop:
  1. DECOMPOSE → Break into tasks
  2. CONTEXT → Load patterns + architecture
  3. CODE → Generate with your conventions
  4. TEST → Write & run tests
  5. VERIFY → Lint, types, coverage checks
  6. UI CHECK → Compare with Figma (if available)
  7. ITERATE → Loop until quality gates pass
    ↓
Feature shipped ✓
```

---

## Quick Start (3 Steps)

### Step 1: Clone Harness

```bash
git clone https://github.com/chetan25/harness-claude-skills.git
```

### Step 2: Copy to Your Project

```bash
cp -r harness-claude-skills/.claude/skills/ my-project/.claude/
```

### Step 3: Open Claude Code & Ask

```
"Analyze this project and help me build features"
```

or just start with:

```
"Add dark mode feature"
```

**That's it.** No CLI. No configuration. Claude handles everything.

---

## What You Get

After analysis, your project has:

```
my-project/
├── claude.md                           ← Auto-generated instructions
├── .claude/
│   ├── skills/
│   │   ├── patterns-react.md          ← Your code style
│   │   ├── architecture.md            ← Project structure
│   │   ├── design-tokens.md           ← UI tokens
│   │   ├── test-patterns.md           ← Testing approach
│   │   └── README.md
│   ├── orchestrator.md                ← Task tracking
│   └── mcp-config.yaml                ← Figma + custom MCPs
├── src/
└── ...
```

Next time you ask Claude for anything, it:
- ✅ Reads your skills automatically
- ✅ Generates code matching your patterns
- ✅ Writes & runs tests
- ✅ Validates against Figma (if configured)
- ✅ Iterates until quality gates pass

---

## Example: Real Workflow

### You say:
```
"Add user authentication with email/password login, 
remember me checkbox, and JWT token storage"
```

### Orchestrator does:

**DECOMPOSE**
- Create auth context + hooks
- Build login form component
- Add JWT token management
- Protect routes
- Write integration tests

**CONTEXT**
- Loads patterns-react.md (your component structure)
- Loads design-tokens.md (your color palette)
- Loads test-patterns.md (your test setup)

**CODE**
- Generates AuthContext.tsx (matches your patterns)
- Generates LoginForm.tsx (uses your design tokens)
- Generates useAuth.ts hook (follows your conventions)
- Generates route guards

**TEST**
- Writes unit tests (90% coverage)
- Writes integration tests
- Runs full suite ✓

**VERIFY**
- ESLint: ✓ Pass
- TypeScript: ✓ Pass
- Tests: ✓ 92% coverage
- Design: ✓ Matches Figma

**SHIP**
- Everything ready
- Tests passing
- Code follows patterns
- Ship it! 🚀

---

## Documentation

| Guide | Use Case |
|-------|----------|
| **[QUICKSTART.md](docs/QUICKSTART.md)** | Get running in 5 minutes |
| **[SETUP.md](docs/SETUP.md)** | Detailed installation & configuration |
| **[CONSUMPTION.md](docs/CONSUMPTION.md)** | How to use Harness + FAQ |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Deep dive: how it works |
| **[GETTING_STARTED.md](docs/GETTING_STARTED.md)** | First commands & examples |

---

## How It Works

### The Skills System

Each `.md` file in `.claude/skills/` is a **guide Claude uses automatically**:

- Before generating code, Claude reads patterns-react.md
- Before writing tests, Claude reads test-patterns.md
- Before creating UI, Claude reads design-tokens.md

This is **automatic** — you don't mention skills. Claude just uses them.

### The Orchestrator Loop

When you ask for a feature, `orchestrator.md` tells Claude exactly what to do:

1. Break feature into tasks
2. Load context for each task
3. Generate code
4. Verify with tests
5. Check against Figma
6. Iterate if needed
7. Mark complete

### The Magic

`claude.md` at your project root says:

```markdown
# Project Instructions

**For ANY feature request:**
1. Load context from .claude/skills/
2. Follow the 7-phase orchestrator loop in .claude/orchestrator.md
3. Always run tests before shipping
4. If Figma MCP is configured, validate UI against designs
```

So Claude just... does it. Automatically.

---

## Skills Included

Harness comes with 4 core skills:

1. **harness-analyzer** — Scans projects, generates `.claude/skills/`
2. **harness-orchestrator** — Coordinates 7-phase feature workflow
3. **harness-context-loader** — Loads context for each task
4. **harness-verifier** — Tests, linting, type-checking, coverage

Each is a `.md` file with clear instructions. Claude reads them. Done.

---

## No CLI. No Commands.

This isn't another tool. It's **skills for Claude Code**.

- ❌ No CLI commands to learn
- ❌ No configuration files to edit
- ❌ No "how do I run this?" complexity

Just:
1. Clone
2. Copy
3. Ask Claude naturally

---

## MCP Integration (Optional)

If you add Figma to `.claude/mcp-config.yaml`:

```yaml
mcps:
  figma:
    enabled: true
    token: ${FIGMA_API_TOKEN}
    project_id: your-figma-id
```

Claude will:
- Fetch Figma designs
- Validate generated UI against specs
- Suggest fixes if misaligned
- Compare colors, spacing, fonts

---

## Works With Everything

Harness adapts to your tech stack:

| Stack | Supported |
|-------|-----------|
| React + TypeScript + Jest | ✅ Out-of-box |
| Vue + Vitest | ✅ Auto-detected |
| Node + Express | ✅ Auto-detected |
| Python + pytest | ✅ Auto-detected |
| Any combo | ✅ Patterns adapt |

Run `/harness analyze` once, and Claude understands your entire codebase.

---

## Project Structure

```
harness-claude-skills/
├── .claude/
│   ├── templates/              ← Templates for generating skills
│   │   ├── claude.md.template
│   │   ├── orchestrator.md.template
│   │   └── ...
│   └── skills/
│       └── README.md           ← Guide for domain skills
├── skills/                     ← 4 core Hermes skills
│   ├── harness-analyzer/
│   ├── harness-orchestrator/
│   ├── harness-context-loader/
│   └── harness-verifier/
├── docs/                       ← Complete documentation
├── examples/                   ← Working examples
│   ├── react-app/
│   └── node-backend/
└── README.md (this file)
```

---

## Examples

Check `examples/` for working projects:

- **react-app/** — React 18 + TypeScript + Tailwind
- **node-backend/** — Node.js + Express + PostgreSQL

Each has its own `.claude/skills/` showing what Claude generates.

---

## FAQ

**Q: Do I need to learn new syntax?**  
A: No. Just ask Claude naturally. Everything happens automatically.

**Q: What if my project is not React?**  
A: Harness auto-detects Python, Node, Go, etc. Skills adapt automatically.

**Q: Do I need to install the CLI?**  
A: No CLI needed. Just copy `.claude/skills/` to your project.

**Q: Can I customize the skills?**  
A: Yes! Edit `.claude/skills/patterns-*.md` to guide Claude your way.

**Q: What about Figma integration?**  
A: Optional. Add Figma token to `.claude/mcp-config.yaml` if you want design validation.

**Q: How often should I re-analyze?**  
A: Once at the start. Run `Analyze this project` if major refactors happen.

See [docs/CONSUMPTION.md](docs/CONSUMPTION.md) for complete FAQ.

---

## Next Steps

1. **Start here:** [docs/QUICKSTART.md](docs/QUICKSTART.md) (5 minutes)
2. **Deep dive:** [docs/SETUP.md](docs/SETUP.md)
3. **Learn the workflow:** [docs/CONSUMPTION.md](docs/CONSUMPTION.md)
4. **See examples:** [examples/](examples/)

---

## Status

**Phase 0: Complete** ✅
- ✅ 4 core skills (analyzer, orchestrator, context-loader, verifier)
- ✅ Templates for code generation
- ✅ Full documentation
- ✅ Examples included
- ✅ Ready to use

**Phase 1: Coming Soon**
- Figma MCP integration enhancements
- Design token extraction
- Automated skill generation improvements

---

## Contributing

Issues, PRs, ideas welcome! This is alpha — we're moving fast.

---

## License

MIT — Use it, modify it, share it.

---

## Built For

Teams who ❤️ Claude and want AI that understands **their** code.

**Get started:** [docs/QUICKSTART.md](docs/QUICKSTART.md)
