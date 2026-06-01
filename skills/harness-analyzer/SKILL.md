---
name: harness-analyzer
description: Use at the start of harness work in a new project, or when project grounding is missing or stale, to scan a codebase and GENERATE project-specific grounding skills, Mermaid diagrams, and a relevance index under .claude/skills/, then wire CLAUDE.md so future feature requests automatically follow the harness flow. Run this once before building features.
version: 3.1.0
---

# Harness Analyzer

Scan the current project, then **generate project-specific grounding skills under `.claude/skills/`** and wire `CLAUDE.md` so every later prompt is governed by the harness flow. **You do this directly with your own tools** (`Glob`, `Grep`, `Read`, `Write`) — there is no external program.

The output is **real Claude Code skills**, not data files. Because they live in `.claude/skills/` with proper frontmatter, Claude auto-loads them in this project from then on.

## When to run
- First time setting up the harness in a repo.
- After a major refactor, dependency change, or convention shift (grounding is stale).

## Procedure

Gather evidence with `Glob`/`Grep`/`Read` — **do not guess**. Anything you can't determine from the repo, write as "unknown / not detected" rather than inventing it.

**Diagram self-check:** before writing any `.mmd`, confirm it has a valid header (`graph`, `flowchart`, or `sequenceDiagram`), every arrow connects two declared nodes, and there are no dangling edges. If a diagram can't be built from real evidence, **skip it** — never ship a faked or broken diagram. A minimal project may legitimately get only `components.mmd`.

### 1. Detect the stack
Glob for manifests at the root and one level down: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `pom.xml`, `*.csproj`, `Gemfile`, `composer.json`. Read the primary manifest for language, framework, and scripts. Note the package manager from the lockfile.

### 2. Map the architecture
Glob source dirs (`src/`, `app/`, `lib/`, `packages/*`, `cmd/`, …). Identify module boundaries and how they depend on each other by sampling entry-point files. Capture this as **standalone Mermaid diagram files** under `.claude/skills/project-architecture/diagrams/` (only nodes/edges you have evidence for):
- `components.mmd` — module / dependency graph (`graph` or `flowchart`).
- `data-flow.mmd` — the canonical happy-path of a typical operation (e.g. route → controller → service → repository → DB), if the stack has a clear request/data flow.

Write one diagram per file. Do not embed these in the skill body — the body will reference them (step "Generate the grounding skills").

### 3. Extract code patterns
Read 3–6 representative source files. Record naming conventions (files, components/classes, functions, types), import style (absolute vs relative, path aliases), file/folder organization, and repeated idioms.

Also capture the patterns **visually** as standalone Mermaid files under `.claude/skills/project-patterns-{lang}/diagrams/` (only what the code actually shows):
- `layers.mmd` — allowed-dependency / layering rules (which layer may import which). Use a `graph` with directed edges meaning "may depend on".
- `idiom-<x>.mmd` — a `sequenceDiagram` of a genuinely recurring idiom (e.g. `idiom-form-submit.mmd`: submit → validate → API call → state update). Generate one per standout idiom; **zero is acceptable** if none recur clearly.

One diagram per file. The skill body references these rather than embedding them.

### 4. Detect test conventions
Find test files and identify the runner from the manifest. Read one test to capture the project's test shape and assertion style.

### 5. Detect design tokens (UI projects only)
If a frontend stack is present, look for `tailwind.config.*`, theme files, CSS custom properties, or a tokens file. Extract colors, spacing, typography, radii. Skip this skill entirely if no UI/tokens exist.

## Generate the grounding skills

For each area you found evidence for, **write a skill** at `.claude/skills/<name>/SKILL.md`. `Write` creates the `.claude/skills/` directory if the project doesn't have one yet, so this works in a fresh repo. Use the `project-` prefix so they're distinguishable from the core `harness-*` skills and from hand-written ones:

| Skill folder | Frontmatter `description` (the trigger) | Body |
|--------------|------------------------------------------|------|
| `project-patterns-{lang}` | "Use when creating or editing {lang} files in this project, to follow its real naming, import, and file-structure conventions." | naming, imports, file org, idioms (step 3); **link** diagrams/layers.mmd and any diagrams/idiom-*.mmd |
| `project-architecture` | "Use when adding or moving modules in this project, to respect its real architecture and where things belong." | module map + dependency notes; **link** diagrams/components.mmd and diagrams/data-flow.mmd (step 2) |
| `project-test-patterns` | "Use when writing or running tests in this project, to match its runner and test style." | runner, layout, example assertion style (step 4) |
| `project-design-tokens` | "Use when building or styling UI in this project, to use its real colors, spacing, and typography." | tokens (step 5) — **only if** detected |

Each generated file must be a valid skill:

```markdown
---
name: project-patterns-react
description: <the trigger sentence from the table>
---

# <Title>

<concrete, project-specific guidance pulled from the REAL code — examples over prose>
```

**Reference diagrams, don't embed them.** A generated skill body must point at its diagram files by path relative to the skill folder, e.g.:

> **Data flow** — read `diagrams/data-flow.mmd` before adding or moving a service.
> **Layering rules** — `diagrams/layers.mmd`; do not introduce a dependency it forbids.

This keeps each skill light and lets the context-loader pull a diagram only when a task touches that area. Do **not** paste Mermaid blocks into the skill body.

Keep each under ~150 lines. Favor real snippets from the codebase over generic advice. These are grounding for an LLM that will auto-load them, so the `description` must accurately say *when* to use the skill.

## Generate the relevance index

Write `.claude/skills/project-index.md` — a compact map from **area → grounding to pull**. This is what lets the loop load only what a task needs instead of re-guessing each time. Build rows only for areas you have evidence for; omit any you can't classify.

```markdown
<!-- harness:index -->
| Area            | Skills                                    | Diagrams                  |
|-----------------|-------------------------------------------|---------------------------|
| api / services  | project-patterns-<lang>, project-architecture | data-flow.mmd, layers.mmd |
| ui / components | project-patterns-<lang>, project-design-tokens | idiom-form-submit.mmd     |
| data / db       | project-architecture                      | data-flow.mmd             |
| tests           | project-test-patterns                     | —                         |
<!-- harness:index -->
```

Rules:
- Areas come from the architecture map you built in step 2.
- Diagram cells are bare filenames; the owning skill folder is implied (architecture diagrams live under `project-architecture/diagrams/`, pattern diagrams under `project-patterns-<lang>/diagrams/`).
- Only list diagrams/skills you actually generated. Use `—` when none apply.
- On re-analyze, regenerate this file from current evidence (overwrite).

## Wire CLAUDE.md (governs the next prompt)

`CLAUDE.md` at the project root is what makes future prompts follow the harness flow. The harness section is delimited by stable markers so it can be updated idempotently on re-analyze:

```markdown
<!-- harness:start -->
## Working in this repo (harness)

- **Stack:** <detected stack>
- **Grounding skills** (auto-loaded, under `.claude/skills/`; each links its diagrams under `diagrams/`):
  - `project-patterns-<lang>` — naming, imports, file structure (+ `layers.mmd`, `idiom-*.mmd`)
  - `project-architecture` — module map / where things belong (+ `components.mmd`, `data-flow.mmd`)
  - `project-test-patterns` — test runner and style
  - `project-design-tokens` — colors, spacing, typography (UI only)
- **Relevance map:** `.claude/skills/project-index.md` — area → which skills/diagrams to load for a task.
- **Loop state:** `harness-orchestrator` tracks progress in `.claude/harness/state.md` (resumable across sessions).

**For any non-trivial feature or change, use `harness-orchestrator`:**
decompose into tasks → for each: ground (harness-context-loader) → build following the
`project-*` conventions → verify (harness-verifier runs this repo's real lint/type/test
commands) → add tests until green. Only claim a check passed after seeing its output.
If the `project-*` skills are missing or stale, run `harness-analyzer` first.

**Quality gates (this repo's real commands):** lint: `<cmd>` · type-check: `<cmd>` · test: `<cmd>`
<!-- harness:end -->
```

Apply it based on the current state (Read the file first if it exists):

1. **No `CLAUDE.md`** → create it containing the block above (fill in real values; drop sections that don't apply).
2. **`CLAUDE.md` exists, no `<!-- harness:start -->` marker** → **append** the block to the end. Leave every existing line untouched.
3. **`CLAUDE.md` exists with the markers** (a prior run) → **replace only the text between `<!-- harness:start -->` and `<!-- harness:end -->`**. Never duplicate the section, and never touch content outside the markers.

This makes the wiring create-if-absent, append-if-present-but-unwired, and update-in-place on re-analyze — always preserving the user's own content. (The repo's `templates/claude.md.template` has a fuller reference version, but write the block directly — don't depend on that file existing in the target project.)

## Works from any starting state
This runs whether or not the project already has a `.claude/` folder or a `CLAUDE.md`:
- **No `.claude/`** → `Write` creates `.claude/skills/` for the generated skills.
- **No `CLAUDE.md`** → create it.
- **Existing `CLAUDE.md`** → **merge** the harness section in; never clobber the user's content.

## After running
Report which `project-*` skills you created and confirm `CLAUDE.md` is wired. Tell the user to **start a new Claude Code session** so the freshly generated `project-*` skills auto-load and the wired `CLAUDE.md` governs by itself. (In *this* session the flow still works without a reload, because `harness-orchestrator` and `harness-context-loader` read the generated files directly.)

## See also
- `harness-context-loader` — assembles the per-task brief from the generated skills
- `harness-orchestrator` — drives the build loop the wired CLAUDE.md points to
- `harness-verifier` — checks output against `project-patterns-*` and the project's gates
