# Harness Claude Skills

**Teach Claude Code your project once, then build features through a disciplined, verified loop — entirely as skills. No CLI, no separate program. Claude *is* the harness.**

`harness-analyzer` scans your codebase and **generates project-specific grounding skills** under `.claude/skills/` — including standalone Mermaid diagram files (`diagrams/`) and a relevance index (`project-index.md`) — then wires your `CLAUDE.md` so every following prompt is automatically governed by the harness flow: decompose → ground → build → verify → test.

---

## The problem

Claude Code is powerful but has blind spots:

- **Context decay** — each prompt starts fresh, losing project knowledge
- **Style drift** — generated code doesn't match your conventions
- **Hallucination** — wrong APIs, missing types, inconsistent naming
- **Complex features** — multi-step work needs coordination
- **No verification** — code ships without lint, types, or tests

## The model

Harness is **four Claude Code skills**. There is no binary to run and no Python package to install — each is a `SKILL.md` that Claude executes with its own tools (`Glob`, `Grep`, `Read`, `Write`, `Bash`, `Agent`).

| Skill | What Claude does when it runs |
|-------|-------------------------------|
| **harness-analyzer** | Scans the project, **generates `project-*` grounding skills** into `.claude/skills/`, and wires `CLAUDE.md` so future prompts follow the flow. |
| **harness-context-loader** | Assembles a compact per-loop **context packet** — user-ask summary, what's done so far, the current task, only the needed `project-*` skills/diagrams, and acceptance criteria. |
| **harness-orchestrator** | Decomposes a requirement and drives each task through the loop, tracking progress in resumable `.claude/harness/state.md`. |
| **harness-verifier** | Runs the project's *real* lint / type-check / format / test commands, checks pattern conformance, and verifies the change respects its grounding diagrams. |

### What makes it self-governing

The analyzer's output is **real skills**, not data files. Because the generated `project-*` skills live in `.claude/skills/` with proper frontmatter, Claude auto-loads them — and the `CLAUDE.md` it wires says "route any feature request through `harness-orchestrator`." So once you've analyzed a project, **your next prompt just follows the harness flow** without you asking for it.

### The loop

```
Requirement
   ↓
Decompose into ordered tasks   (harness-orchestrator)
   ↓
For each task:
   ground  → per-loop context packet (only the needed project-* skills/diagrams)   (harness-context-loader)
   plan    → approach against that packet
   build   → implement, following project-patterns / project-architecture
   verify  → lint / types / format / patterns / diagrams   (harness-verifier)
   test    → add + run tests until green
   ↓
Feature complete
```

---

## Quick start

### 1. Get the skills

```bash
git clone https://github.com/chetan25/harness-claude-skills.git
```

### 2. Make them available in your project

**Per project** — copy the four core skill folders in:

```bash
cp -r harness-claude-skills/skills/harness-* my-project/.claude/skills/
```

**Across all projects** — install as a plugin so they auto-load everywhere. See [docs/SETUP.md](docs/SETUP.md#install-as-a-plugin).

### 3. Analyze once, then just build

```
"Analyze this project."
```

`harness-analyzer` generates the `project-*` grounding skills and wires `CLAUDE.md`. After that, ask for work normally:

```
"Add dark mode with persistence."
```

CLAUDE.md + the generated skills route it through the harness flow automatically — no need to say "use the harness."

---

## What gets generated

`harness-analyzer` writes **skills** (not data) into `.claude/skills/`, and updates `CLAUDE.md`:

```
my-project/
├── CLAUDE.md                                ← wired so feature requests follow the flow
└── .claude/
    ├── harness/
    │   └── state.md                         ← orchestrator run state (resumable)
    └── skills/
        ├── harness-analyzer/ … harness-verifier/   (the 4 core skills you installed)
        ├── project-index.md                 ← relevance map (area → skills/diagrams)
        ├── project-patterns-<lang>/
        │   ├── SKILL.md
        │   └── diagrams/  (layers.mmd, idiom-*.mmd)
        ├── project-architecture/
        │   ├── SKILL.md
        │   └── diagrams/  (components.mmd, data-flow.mmd)
        ├── project-test-patterns/SKILL.md
        └── project-design-tokens/SKILL.md   (UI projects only)
```

The generated `project-*` skills are normal project files — commit them so your team shares the same grounding. Re-run the analyzer after major refactors to refresh them.

---

## Example: "Add user authentication"

After analysis, you say:

```
"Add email/password auth with a remember-me checkbox and JWT storage."
```

CLAUDE.md routes it through `harness-orchestrator`, which:

- **Decomposes** → auth context + `useAuth` hook · login form · token storage · route guard · tests
- **Grounds** each task from the `project-*` skills (your component structure, design tokens, test style)
- **Builds** following your real conventions
- **Verifies** with *your* `lint` / `typecheck` / `test` scripts — not assumed commands
- **Tests** in your project's style, iterating until green

Every claim of "passing" is backed by command output you can see.

---

## Skills included

1. **harness-analyzer** — scans the project, generates `project-*` grounding skills, wires `CLAUDE.md`
2. **harness-context-loader** — assembles the per-loop context packet (user-ask summary + done-so-far + current task + only the needed skills/diagrams) from the generated skills and `project-index.md`
3. **harness-orchestrator** — runs the decompose → ground → build → verify → test loop, tracking progress in resumable `.claude/harness/state.md`
4. **harness-verifier** — runs the project's real quality gates and checks patterns + grounding diagrams

Each is a `SKILL.md`. Claude reads it and acts. Nothing to execute.

---

## Optional: MCP integration (e.g. Figma)

Harness has no MCP config of its own. To give Claude design context, configure an MCP server the normal Claude Code way — a `.mcp.json` in your project (see the `plugin-dev:mcp-integration` guidance). With a Figma MCP connected, the verifier can compare generated UI against the design as part of its checks.

---

## Works with any stack

The skills detect the stack from real manifests (`package.json`, `pyproject.toml`, `go.mod`, …) and read the project's own scripts — so React/TS, Vue, Node, Python, Go, etc. all work without per-stack config.

---

## Project structure (this repo)

This repo is itself a **Claude Code plugin** (so it can auto-load in any repo):

```
harness-claude-skills/
├── .claude-plugin/
│   ├── plugin.json             ← plugin manifest
│   └── marketplace.json        ← single-plugin marketplace (for install/testing)
├── skills/                     ← the 4 core harness skills (this is the product)
│   ├── harness-analyzer/
│   ├── harness-context-loader/
│   ├── harness-orchestrator/
│   ├── harness-verifier/
│   └── README.md
├── templates/                  ← claude.md / orchestrator / domain-skill templates + example outputs
├── docs/
│   ├── QUICKSTART.md
│   ├── SETUP.md
│   ├── CONSUMPTION.md
│   └── ARCHITECTURE.md
└── README.md
```

---

## Documentation

| Guide | Use case |
|-------|----------|
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | Running in a few minutes |
| [docs/SETUP.md](docs/SETUP.md) | Install per-project or as a plugin |
| [docs/CONSUMPTION.md](docs/CONSUMPTION.md) | How to use it day to day + FAQ |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How the skills fit together |

---

## License

MIT — use it, modify it, share it.
