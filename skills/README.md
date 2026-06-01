# Harness Skills

These are **Claude Code skills** — each is a `SKILL.md` of instructions Claude reads and executes with its own tools (`Glob`, `Grep`, `Read`, `Write`, `Bash`, `Agent`). There is no Python package, no CLI, and no skills API to call. Claude is the runtime.

This folder holds the **four core skills** (the reusable product). When you run the analyzer in a target project, it *generates* additional `project-*` grounding skills alongside them.

## The four core skills

### harness-analyzer
Scans the project, **generates `project-*` grounding skills** into `.claude/skills/` (project-patterns, project-architecture, project-test-patterns, project-design-tokens) with standalone Mermaid diagrams under each skill's own `diagrams/` folder (`components.mmd`, `data-flow.mmd`, `layers.mmd`, `idiom-*.mmd`), generates a `project-index.md` relevance map, and wires the project's `CLAUDE.md` so future feature requests follow the harness flow. Run it first, and after major refactors.

### harness-context-loader
Each loop, reads `state.md` + `project-index.md` and assembles a compact per-loop **context packet** — carrying the user-ask summary, what's done so far, the current task, only the relevant `project-*` skills/diagrams, and acceptance criteria. The packet is ephemeral (rebuilt each loop) so context stays precise. Keeps generated code aligned with real project conventions.

### harness-orchestrator
Decomposes a requirement and drives each task through the loop — ground → plan → build → verify → test — tracking progress with a todo list and a resumable `.claude/harness/state.md` (user-ask summary, task list with `[ ]`/`[>]`/`[x]` markers, and a rolling done-so-far log) that survives compaction and session restarts.

### harness-verifier
Runs the project's *real* lint / type-check / format / test commands, checks the changed code for pattern conformance against `project-patterns-*`, and verifies the change respects its grounding diagrams (e.g. layering rules in `layers.mmd`, the canonical `data-flow.mmd`) — reported as a `diagrams` gate. Reports pass/fail with evidence and drives fixes until green.

## How they relate

```
harness-orchestrator  (tracks progress in .claude/harness/state.md)
  ├─ runs harness-analyzer first if no project-* skills / CLAUDE.md exist
  │    └─ analyzer writes project-* skills, diagrams/, and project-index.md
  ├─ per task: harness-context-loader reads state.md + project-index.md → context packet
  │              (only the needed project-* skills + diagrams)
  ├─ build
  └─ harness-verifier → gate: lint / types / format / tests / patterns / diagrams (fix + retry on red)
```

## Skill anatomy

Each skill folder contains one `SKILL.md` with YAML frontmatter and a Markdown body:

```markdown
---
name: harness-analyzer
description: Use at the start of harness work ... (this is what triggers the skill)
version: 3.1.0
---

# Harness Analyzer

<direct, imperative instructions Claude follows with its own tools>
```

The `description` is the trigger — write it so Claude knows exactly when to invoke the skill. The body is instructions for Claude to *do*, not documentation of an external tool: it says "use Glob to find manifests, Read them, Write a generated skill to `.claude/skills/project-*/SKILL.md`", never "run some command" against a program that doesn't exist.

## Generated `project-*` skills

These are written by `harness-analyzer` into `.claude/skills/` in the *target* project, each alongside its own `diagrams/` folder of standalone `.mmd` files (the skills reference these diagrams by path rather than embedding Mermaid inline). The analyzer also writes a `project-index.md` relevance map (area → which `project-*` skills + diagrams to load). They're real skills (with `name` + `description`), so Claude auto-loads them — and they're normal committable project files, so a team shares the same grounding. They are grounding, generated from the real codebase; re-running the analyzer refreshes them.

## Adding a domain skill (by hand)

1. Create the skill folder: `skills/harness-<domain>/SKILL.md` in this plugin (or, for a one-off in a single project, that project's `.claude/skills/harness-<domain>/SKILL.md`).
2. Start from `templates/domain-skill.template`.
3. Write Claude-native instructions in the same style as the four core skills.
4. Reference the generated `project-*` skills it should consult and which sibling skills it composes with.

## Conventions

- **Folder:** kebab-case; the folder name is the skill's invocation name. Core skills use `harness-`; generated grounding uses `project-`.
- **Frontmatter `name`** should match the folder name.
- **Instructions, not implementation:** describe what Claude should do with its tools — no Python/JS code purporting to be the skill's runtime.
- **Evidence over assertion:** skills that verify must run real commands and report real output (see `harness-verifier`).

## See also

- `templates/` — domain-skill template, the CLAUDE.md/orchestrator reference templates, and example generated outputs
- `docs/ARCHITECTURE.md` — how the skills fit together
- `docs/CONSUMPTION.md` — day-to-day usage
