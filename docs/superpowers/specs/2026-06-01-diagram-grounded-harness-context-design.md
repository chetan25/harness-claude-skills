# Diagram-grounded harness with precise per-loop context

**Date:** 2026-06-01
**Status:** Approved (design)
**Scope:** Extends the four existing `harness-*` skills. No new skill, no external scripts.

## Problem

The harness loop loads project grounding as prose-heavy `project-*` skills with a single
inline Mermaid block. Two weaknesses follow:

1. **Weak visual grounding.** Architecture gets one inline diagram; coding patterns, data
   flow, and idioms are described only in prose, which the agent grounds on less reliably.
2. **Context drifts as the loop runs.** Across a multi-task build, "what's been done" and
   "what this task needs" live only in the conversation. They degrade under context growth,
   compaction, and session restarts — the opposite of "precise context every loop."

## Goal

- The analyzer generates a **set of standalone Mermaid diagrams** (architecture + patterns:
  data flow, layering, common idioms) as referenceable `.mmd` artifacts.
- The generated `project-*` skills **reference** those diagrams instead of embedding them.
- The orchestrator drives each loop iteration from a **compact, freshly-assembled context
  packet** that carries: a short summary of the user ask, what's done so far, the current
  task, and pointers to exactly the grounding (skills + diagrams) that task needs.
- Running state is **file-backed** so the loop is resumable and survives compaction.
- Loading stays **selective** — each loop pulls only the grounding relevant to its task.

Non-goals: adding a fifth skill, external runner programs, generating diagrams without
codebase evidence, or persisting the per-loop packet (it is rebuilt each loop by design).

## Architecture overview

```
harness-analyzer   ──generates──▶  .claude/skills/project-*/diagrams/*.mmd
                                    .claude/skills/project-index.md   (relevance map)
                                    .claude/skills/project-*/SKILL.md (link diagrams)
                                    CLAUDE.md  (wiring + pointers)

harness-orchestrator ──owns──▶  .claude/harness/state.md  (user ask, tasks, done-so-far)
        │  each loop:
        │    mark current task → call context-loader → build → verify → test
        │    on green: update state.md
        ▼
harness-context-loader ──reads──▶  state.md + project-index.md + selected *.mmd
        └─emits──▶  ephemeral per-loop context packet (held in context, not written)

harness-verifier ──gates──▶  also checks change respects the diagrams it was grounded on
```

## Components

### 1. Generated diagram artifacts (analyzer)

The analyzer writes one diagram per file, only where it has real evidence:

```
.claude/skills/
  project-architecture/
    SKILL.md
    diagrams/
      components.mmd      # module / dependency graph
      data-flow.mmd       # canonical happy-path: route → service → repo → DB
  project-patterns-<lang>/
    SKILL.md
    diagrams/
      layers.mmd          # allowed-dependency / layering rules
      idiom-<x>.mmd        # sequenceDiagram of a recurring idiom (0..n)
  project-design-tokens/   # UI only, unchanged in scope
  project-test-patterns/
  project-index.md         # relevance map (see §3)
```

Rules:
- Each `.mmd` contains exactly one diagram and is generated only from evidence in the repo
  (no invented nodes/edges). A minimal project may get only `components.mmd`.
- Before writing a `.mmd`, the analyzer does a light syntax self-check: a valid diagram
  header (`graph`/`flowchart`/`sequenceDiagram`), balanced node/arrow usage, no dangling
  arrows. If a diagram can't be built from evidence, it is skipped, not faked.
- `idiom-<x>.mmd` files are zero-or-more: generate one per genuinely recurring idiom found
  (e.g. `idiom-form-submit.mmd`), skip if none stand out.

### 2. Skills reference diagrams (analyzer output shape)

`project-*` SKILL.md bodies stop embedding Mermaid. Instead they reference the files:

> **Data flow** — read `diagrams/data-flow.mmd` before adding or moving a service.
> **Layering rules** — `diagrams/layers.mmd`; do not introduce dependencies it forbids.

Diagram paths in skill bodies are relative to the skill's own folder.

### 3. Relevance index (`project-index.md`)

A compact analyzer-generated table mapping **area → grounding to pull**. This makes
selective loading deterministic instead of re-guessed each loop.

```markdown
<!-- harness:index -->
| Area              | Skills                                   | Diagrams                       |
|-------------------|------------------------------------------|--------------------------------|
| api / services    | project-patterns-ts, project-architecture | data-flow.mmd, layers.mmd      |
| ui / components    | project-patterns-ts, project-design-tokens | idiom-form-submit.mmd         |
| data / db         | project-architecture                      | data-flow.mmd                  |
| tests             | project-test-patterns                     | —                              |
```

- Areas are derived from the architecture map the analyzer already builds.
- Diagram entries are bare filenames; the owning skill folder is implied by which skill
  lists the diagram (architecture diagrams under `project-architecture/diagrams/`, etc.).
- If the analyzer can't classify an area, it omits the row rather than guessing.

### 4. Running state (`.claude/harness/state.md`, orchestrator-owned)

Created at decompose time, updated after each task. Small and stable:

```markdown
## User ask
<2-3 line summary of the original request>

## Tasks
- [x] 1. Auth context + useAuth hook — done: added src/auth/, hook returns {user,login,logout}
- [>] 2. Login form
- [ ] 3. Protected-route wrapper

## Done so far
- Auth context wired; verifier green (lint/type/test). Tokens reused from project-design-tokens.
```

- Task markers: `[ ]` pending, `[>]` in-progress, `[x]` done (with a one-line result).
- `Done so far` is a short rolling log (a line or two per finished task), not a transcript.
- `state.md` is the resumable source of truth; on re-entry the orchestrator reads it rather
  than re-deriving progress from conversation.

### 5. Per-loop context packet (context-loader, ephemeral)

Each loop, the context-loader reads `state.md` + `project-index.md`, resolves the current
task to its area(s), and emits the packet below — held in context for that one task only,
never written to disk:

```
USER ASK (summary): ...
DONE SO FAR: ...
CURRENT TASK: 2. Login form
CONTEXT FOR THIS TASK:
  - project-patterns-ts (naming/imports)
  - project-design-tokens
  - diagrams/idiom-form-submit.mmd
ACCEPTANCE CRITERIA:
  - [ ] lives in the right place per project-architecture
  - [ ] follows naming + import conventions
  - [ ] (UI) uses project design tokens, accessible
  - [ ] tests added in the project's style, passing
```

The loader reads the `.mmd` files for the selected areas only. The packet never accumulates
prior tasks' detail beyond the short `DONE SO FAR` line — that is what keeps every loop tight.

## Data flow (one loop iteration)

1. Orchestrator marks the current task `[>]` in `state.md`.
2. Orchestrator calls context-loader.
3. Context-loader: read `state.md` → current task; read `project-index.md` → area → skills +
   diagrams; read the selected `project-*` skills and `.mmd` files; emit the packet.
4. Orchestrator builds the change against the packet.
5. Verifier runs the project's real gates **and** checks the change respects the diagrams it
   was grounded on (notably the layering rules in `layers.mmd`).
6. On green: orchestrator sets the task `[x]` with a one-line result and refreshes
   `Done so far` in `state.md`. Move to the next task.

## Responsibilities by skill (what changes)

- **harness-analyzer** — emit standalone `.mmd` diagrams (architecture + patterns), the
  `project-index.md` relevance map, and `project-*` bodies that reference diagrams by path.
  Add a CLAUDE.md wiring line pointing at `project-index.md` and `.claude/harness/state.md`.
  Light Mermaid syntax self-check before writing.
- **harness-orchestrator** — create and maintain `.claude/harness/state.md`; drive each loop
  from it; resumable re-entry reads it. Replaces the optional ad-hoc journal with this
  structured state file.
- **harness-context-loader** — assemble the per-loop packet from `state.md` + index +
  selected skills/diagrams; read only the selected `.mmd` files.
- **harness-verifier** — additionally verify the change respects the diagrams it was grounded
  on (layering/data-flow), reported as a pattern-conformance check.

## CLAUDE.md wiring (additions)

The existing `<!-- harness:start -->` … `<!-- harness:end -->` block gains:
- A pointer to `project-index.md` as the relevance map.
- A note that the orchestrator tracks progress in `.claude/harness/state.md` (resumable).
- Grounding-skills list notes that each `project-*` skill links diagrams under its
  `diagrams/` folder.

Idempotent merge behavior is unchanged (create-if-absent, append-if-unwired,
replace-between-markers on re-analyze).

## Error handling & edge cases

- **No evidence for a diagram** → skip that `.mmd`; do not fake it. A project may legitimately
  have only `components.mmd`.
- **Re-analyze** → diagrams and `project-index.md` are regenerated; `state.md` is left
  untouched (it belongs to the orchestrator's run, not the analyzer).
- **Resume after restart/compaction** → orchestrator reads `state.md`; the in-progress `[>]`
  task is re-grounded by the loader from scratch (packet is ephemeral by design).
- **Stale grounding** → if `project-*` skills or `project-index.md` are missing, orchestrator
  runs the analyzer first (unchanged precondition, now also covers the index).
- **Mermaid that won't parse** → caught by the analyzer's self-check; the diagram is rewritten
  or skipped rather than shipped broken.

## Verification

Because this is a set of skills (markdown), verification is by exercising the flow on a real
repo, not unit tests:

- Run `harness-analyzer` on a sample project → confirm `.mmd` files, `project-index.md`, and
  diagram-referencing `project-*` skills are generated, and diagrams render.
- Run `harness-orchestrator` on a 2–3 task requirement → confirm `state.md` is created and
  updated per task, and that each loop's packet pulls only the indexed grounding.
- Restart mid-run → confirm the orchestrator resumes from `state.md`.
- Confirm CLAUDE.md wiring is idempotent across two analyzer runs.

## Open questions

None blocking. Two defaults locked during design:
- The per-loop packet is **ephemeral** (rebuilt from `state.md` each loop), not persisted.
- `project-index.md` is a **new generated file** the loader depends on for selective loading.
