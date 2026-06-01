# Harness Claude Skills — Quick Start

Harness is **four Claude Code skills**, not a CLI. There's no binary to run and no package to install — Claude reads the skills and does the work. Setup is just making the skills available, then asking Claude to analyze your project once.

## 1. Get the skills

```bash
git clone https://github.com/chetan25/harness-claude-skills.git
```

## 2. Copy them into your project

Copy the four core skill folders into your project's `.claude/skills/`:

```bash
mkdir -p my-project/.claude/skills
cp -r harness-claude-skills/skills/harness-* my-project/.claude/skills/
```

(To get them in **every** repo instead, install as a plugin — see [SETUP.md](SETUP.md#install-as-a-plugin).)

## 3. Analyze the project once

Open the project in Claude Code and say:

```
"Analyze this project."
```

`harness-analyzer` scans the codebase, **generates `project-*` grounding skills** under `.claude/skills/` — including standalone Mermaid diagram files (`.mmd`) under each skill's `diagrams/` folder and a `project-index.md` relevance map — and wires your `CLAUDE.md` so future feature requests automatically follow the harness flow.

## 4. Then just ask for features

```
"Add a dark-mode toggle that persists to localStorage."
```

You don't have to say "use the harness." `CLAUDE.md` + the generated skills route the request through `harness-orchestrator`, which runs the loop:

1. **Decompose** the feature into tasks (`harness-orchestrator`)
2. **Ground** each task with a per-loop context packet — only the grounding skills + diagrams that task needs, plus acceptance criteria (`harness-context-loader`)
3. **Plan** the approach against that packet
4. **Build** following your real patterns and architecture
5. **Verify** with your project's *actual* lint / type-check / test commands (`harness-verifier`)
6. **Test** in your project's style, iterating until green

Every "passing" claim is backed by command output you can see.

## What you end up with

```
my-project/
├── CLAUDE.md
└── .claude/
    ├── harness/
    │   └── state.md                         ← orchestrator run state (resumable)
    └── skills/
        ├── harness-* (the 4 core skills)
        ├── project-index.md                 ← relevance map (area → skills/diagrams)
        ├── project-patterns-<lang>/ { SKILL.md, diagrams/ (layers.mmd, idiom-*.mmd) }
        ├── project-architecture/ { SKILL.md, diagrams/ (components.mmd, data-flow.mmd) }
        ├── project-test-patterns/SKILL.md
        └── project-design-tokens/SKILL.md   (UI only)
```

The generated `project-*` files are **real skills** with `name` + `description` frontmatter, so Claude auto-loads them. They're normal project files — **commit them** so your team shares the same grounding. Re-run the analyzer after a major refactor to refresh them.

## Next steps

- [SETUP.md](SETUP.md) — per-project vs plugin install, refreshing grounding, MCP, troubleshooting
- [CONSUMPTION.md](CONSUMPTION.md) — day-to-day usage and FAQ
- [ARCHITECTURE.md](ARCHITECTURE.md) — how the four skills fit together
