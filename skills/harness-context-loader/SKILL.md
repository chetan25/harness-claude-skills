---
name: harness-context-loader
description: Use before generating or modifying code in a harness-grounded project to assemble a compact per-loop context packet — pull the loop state (.claude/harness/state.md) plus only the project-* skills and diagrams the current task needs (via project-index.md) into a focused brief with acceptance criteria. Keeps each loop's context precise.
version: 3.1.0
---

# Harness Context Loader

Before writing code for a task, consult the project's generated grounding skills and distill them into a **focused brief** with acceptance criteria. **You do this yourself** — there is no external loader program.

The grounding lives in the `project-*` skills that `harness-analyzer` generated under `.claude/skills/`. Those auto-load by description, but this skill makes the grounding *task-specific*: it picks what's relevant and turns it into a concrete checklist.

## When to run
- At the start of any implementation task in a harness-grounded repo.
- Called by `harness-orchestrator` once per decomposed task.

## Procedure

### 1. Ensure grounding exists
Check for `project-*` skills under `.claude/skills/` (e.g. `project-patterns-*`, `project-architecture`, `project-test-patterns`, `project-design-tokens`). If none exist, run **`harness-analyzer`** first — it generates them.

### 2. Read the loop state and resolve the task's grounding
Read `.claude/harness/state.md` to get the user-ask summary, the "done so far" log, and the current (`[>]`) task. Then read `.claude/skills/project-index.md` and match the current task to its area row(s) to get the exact skills + diagrams to pull. Don't load everything — context bloat degrades output. Read only the selected `project-*` skill bodies and only the `.mmd` files those rows name.

If `project-index.md` is missing, fall back to inferring relevance from the task text and `project-architecture` (and suggest re-running `harness-analyzer` to regenerate the index).

### 3. Emit the per-loop context packet
Assemble a compact packet for THIS task only and hold it in context (do **not** write it to a file — it is rebuilt each loop from `state.md`, so it never goes stale):

```
USER ASK (summary): <from state.md>
DONE SO FAR: <from state.md, the rolling summary>
CURRENT TASK: <the [>] task>
CONTEXT FOR THIS TASK:
  - <selected project-* skills, e.g. project-patterns-ts (naming/imports)>
  - <selected diagrams, e.g. diagrams/idiom-form-submit.mmd>
ACCEPTANCE CRITERIA:
  - [ ] lives in the right place per project-architecture
  - [ ] follows naming + import conventions
  - [ ] respects layering in diagrams/layers.mmd (if loaded)
  - [ ] (UI) uses project design tokens, accessible
  - [ ] tests added in the project's style, passing
```

The packet carries only the short "done so far" line from prior work — it never accumulates earlier tasks' detail. That is what keeps every loop's context tight. This packet is what the build step works against and what `harness-verifier` checks the result against.

## Guidance
- **Keep it lean.** A few hundred words of sharp, project-specific guidance beats dumping every generated skill.
- **Stay grounded.** Every constraint should trace to a `project-*` skill or the actual repo — not to generic best practice.

## See also
- `harness-analyzer` — generates the `project-*` skills this consults
- `harness-orchestrator` — calls this per task, then builds against the brief
- `harness-verifier` — checks output against the acceptance criteria
