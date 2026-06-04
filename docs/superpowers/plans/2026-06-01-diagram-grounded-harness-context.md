# Diagram-grounded Harness Context Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the four `harness-*` skills so the analyzer emits standalone Mermaid diagrams + a relevance index, and the orchestrator/loader drive each loop from a compact, file-backed, freshly-assembled context packet.

**Architecture:** Additive edits to four existing `SKILL.md` files — no new skill, no scripts. Analyzer generates `.mmd` diagram files, a `project-index.md` relevance map, and diagram-referencing `project-*` skills. Orchestrator owns `.claude/harness/state.md`; context-loader assembles an ephemeral per-loop packet from state + index + selected diagrams; verifier adds a diagram-conformance check.

**Tech Stack:** Claude Code skills (Markdown + YAML frontmatter), Mermaid diagrams. No build system. Verification is by exercising the flow on a sample repo.

**Spec:** `docs/superpowers/specs/2026-06-01-diagram-grounded-harness-context-design.md`

---

## File structure

All edits are to existing files:

- `skills/harness-analyzer/SKILL.md` — diagram generation, `project-index.md`, diagram-referencing skill bodies, CLAUDE.md wiring (Tasks 1–4). Frontmatter `version` 3.0.0 → 3.1.0.
- `skills/harness-orchestrator/SKILL.md` — `state.md` ownership + loop (Task 5). `version` 2.0.0 → 2.1.0.
- `skills/harness-context-loader/SKILL.md` — per-loop packet from state + index (Task 6). `version` 3.0.0 → 3.1.0.
- `skills/harness-verifier/SKILL.md` — diagram-conformance gate (Task 7). `version` 2.0.0 → 2.1.0.
- Task 8 is end-to-end verification on a throwaway sample repo (no file in this repo changes except the plan checkboxes).

Convention note: diagrams the analyzer GENERATES live under the *consuming* project's `.claude/skills/project-*/diagrams/`. Nothing in THIS repo gains a `diagrams/` folder.

---

## Task 1: Analyzer — generate standalone diagram artifacts

**Files:**
- Modify: `skills/harness-analyzer/SKILL.md` (steps 2 "Map the architecture" and 3 "Extract code patterns")

- [ ] **Step 1: Replace the "Map the architecture" step to emit diagram files**

In `skills/harness-analyzer/SKILL.md`, replace the `### 2. Map the architecture` section with:

```markdown
### 2. Map the architecture
Glob source dirs (`src/`, `app/`, `lib/`, `packages/*`, `cmd/`, …). Identify module boundaries and how they depend on each other by sampling entry-point files. Capture this as **standalone Mermaid diagram files** under `.claude/skills/project-architecture/diagrams/` (only nodes/edges you have evidence for):
- `components.mmd` — module / dependency graph (`graph` or `flowchart`).
- `data-flow.mmd` — the canonical happy-path of a typical operation (e.g. route → controller → service → repository → DB), if the stack has a clear request/data flow.

Write one diagram per file. Do not embed these in the skill body — the body will reference them (step "Generate the grounding skills").
```

- [ ] **Step 2: Replace the "Extract code patterns" step to emit pattern diagrams**

Replace the `### 3. Extract code patterns` section with:

```markdown
### 3. Extract code patterns
Read 3–6 representative source files. Record naming conventions (files, components/classes, functions, types), import style (absolute vs relative, path aliases), file/folder organization, and repeated idioms.

Also capture the patterns **visually** as standalone Mermaid files under `.claude/skills/project-patterns-{lang}/diagrams/` (only what the code actually shows):
- `layers.mmd` — allowed-dependency / layering rules (which layer may import which). Use a `graph` with directed edges meaning "may depend on".
- `idiom-<x>.mmd` — a `sequenceDiagram` of a genuinely recurring idiom (e.g. `idiom-form-submit.mmd`: submit → validate → API call → state update). Generate one per standout idiom; **zero is acceptable** if none recur clearly.

One diagram per file. The skill body references these rather than embedding them.
```

- [ ] **Step 3: Add a Mermaid self-check note**

Immediately after the `## Procedure` intro paragraph (the "Gather evidence…" line) in `skills/harness-analyzer/SKILL.md`, add:

```markdown

**Diagram self-check:** before writing any `.mmd`, confirm it has a valid header (`graph`, `flowchart`, or `sequenceDiagram`), every arrow connects two declared nodes, and there are no dangling edges. If a diagram can't be built from real evidence, **skip it** — never ship a faked or broken diagram. A minimal project may legitimately get only `components.mmd`.
```

- [ ] **Step 4: Verify the edits are coherent**

Read: `skills/harness-analyzer/SKILL.md` sections 2 and 3.
Expected: both sections instruct writing `.mmd` files (not inline blocks); the self-check note is present; no remaining instruction to embed Mermaid inline in step 2.

- [ ] **Step 5: Commit**

```bash
git add skills/harness-analyzer/SKILL.md
git commit -m "feat(analyzer): emit standalone architecture + pattern Mermaid diagrams"
```

---

## Task 2: Analyzer — skills reference diagrams instead of embedding

**Files:**
- Modify: `skills/harness-analyzer/SKILL.md` ("Generate the grounding skills" section)

- [ ] **Step 1: Update the grounding-skills table Body column to reference diagrams**

In the `## Generate the grounding skills` table, replace the `project-architecture` and `project-patterns-{lang}` rows' Body cells so they reference diagram files:

- `project-architecture` Body: `module map + dependency notes; **link** diagrams/components.mmd and diagrams/data-flow.mmd (step 2)`
- `project-patterns-{lang}` Body: `naming, imports, file org, idioms (step 3); **link** diagrams/layers.mmd and any diagrams/idiom-*.mmd`

- [ ] **Step 2: Add an explicit "reference, don't embed" rule under the table**

Immediately after the example skill markdown block in `## Generate the grounding skills`, add:

```markdown
**Reference diagrams, don't embed them.** A generated skill body must point at its diagram files by path relative to the skill folder, e.g.:

> **Data flow** — read `diagrams/data-flow.mmd` before adding or moving a service.
> **Layering rules** — `diagrams/layers.mmd`; do not introduce a dependency it forbids.

This keeps each skill light and lets the context-loader pull a diagram only when a task touches that area. Do **not** paste Mermaid blocks into the skill body.
```

- [ ] **Step 3: Verify**

Read: `skills/harness-analyzer/SKILL.md` `## Generate the grounding skills`.
Expected: table Body cells reference `diagrams/*.mmd`; the "Reference diagrams, don't embed them" rule is present.

- [ ] **Step 4: Commit**

```bash
git add skills/harness-analyzer/SKILL.md
git commit -m "feat(analyzer): generated skills reference diagram files instead of embedding"
```

---

## Task 3: Analyzer — generate the relevance index (project-index.md)

**Files:**
- Modify: `skills/harness-analyzer/SKILL.md` (new subsection after "Generate the grounding skills")

- [ ] **Step 1: Add the index-generation subsection**

After the `## Generate the grounding skills` section (before `## Wire CLAUDE.md`), insert:

````markdown
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
````

- [ ] **Step 2: Verify**

Read: `skills/harness-analyzer/SKILL.md`.
Expected: a `## Generate the relevance index` section exists between grounding-skills generation and CLAUDE.md wiring; it writes `.claude/skills/project-index.md` with a `<!-- harness:index -->`-delimited table.

- [ ] **Step 3: Commit**

```bash
git add skills/harness-analyzer/SKILL.md
git commit -m "feat(analyzer): generate project-index.md relevance map for selective loading"
```

---

## Task 4: Analyzer — wire CLAUDE.md to index + state, bump version

**Files:**
- Modify: `skills/harness-analyzer/SKILL.md` (CLAUDE.md block + frontmatter)

- [ ] **Step 1: Add index + state pointers to the CLAUDE.md harness block**

In the `## Wire CLAUDE.md` fenced `markdown` block, update the grounding-skills bullet list and add two lines. Replace the grounding-skills sub-list so each entry notes diagrams, and add the index + state pointers right after the list:

```markdown
- **Grounding skills** (auto-loaded, under `.claude/skills/`; each links its diagrams under `diagrams/`):
  - `project-patterns-<lang>` — naming, imports, file structure (+ `layers.mmd`, `idiom-*.mmd`)
  - `project-architecture` — module map / where things belong (+ `components.mmd`, `data-flow.mmd`)
  - `project-test-patterns` — test runner and style
  - `project-design-tokens` — colors, spacing, typography (UI only)
- **Relevance map:** `.claude/skills/project-index.md` — area → which skills/diagrams to load for a task.
- **Loop state:** `harness-orchestrator` tracks progress in `.claude/harness/state.md` (resumable across sessions).
```

- [ ] **Step 2: Bump the analyzer version**

In `skills/harness-analyzer/SKILL.md` frontmatter, change `version: 3.0.0` to `version: 3.1.0`.

- [ ] **Step 3: Update the analyzer's frontmatter description to mention diagrams + index**

Change the frontmatter `description` to:

```
description: Use at the start of harness work in a new project, or when project grounding is missing or stale, to scan a codebase and GENERATE project-specific grounding skills, Mermaid diagrams, and a relevance index under .claude/skills/, then wire CLAUDE.md so future feature requests automatically follow the harness flow. Run this once before building features.
```

- [ ] **Step 4: Verify**

Read: `skills/harness-analyzer/SKILL.md` frontmatter + `## Wire CLAUDE.md`.
Expected: `version: 3.1.0`; description mentions diagrams + relevance index; CLAUDE.md block lists the relevance map and loop-state pointers.

- [ ] **Step 5: Commit**

```bash
git add skills/harness-analyzer/SKILL.md
git commit -m "feat(analyzer): wire CLAUDE.md to relevance index + loop state, bump to 3.1.0"
```

---

## Task 5: Orchestrator — own `.claude/harness/state.md` and drive the loop from it

**Files:**
- Modify: `skills/harness-orchestrator/SKILL.md` (procedure steps 2–3, "Progress tracking", frontmatter)

- [ ] **Step 1: Add a state-file definition after "Ensure grounding"**

In `skills/harness-orchestrator/SKILL.md`, immediately after `### 1. Ensure grounding`, insert a new subsection:

````markdown
### 2. Initialize loop state
Create `.claude/harness/state.md` — the resumable source of truth for this run. Write the user-ask summary and the (about-to-be-decomposed) task list. Keep it small:

```markdown
## User ask
<2-3 line summary of the original request>

## Tasks
- [ ] 1. <task>
- [ ] 2. <task>

## Done so far
- (nothing yet)
```

Task markers: `[ ]` pending, `[>]` in-progress, `[x]` done (with a one-line result). If `state.md` already exists (resuming a run), **read it instead of overwriting** and continue from the first non-`[x]` task.
````

Then renumber the existing `### 2. Decompose` → `### 3. Decompose`, `### 3. Run each task…` → `### 4. Run each task…`, `### 4. Parallel vs serial` → `### 5.`, `### 5. Recover from failures` → `### 6.`.

- [ ] **Step 2: Update the decompose step to write tasks into state.md**

In the renamed `### 3. Decompose`, append after the existing example:

```markdown

Write the decomposed tasks into the `## Tasks` list of `.claude/harness/state.md` (in addition to `TodoWrite`). `state.md` is what survives compaction and restarts; `TodoWrite` is the live in-session view of the same list.
```

- [ ] **Step 3: Update the per-task loop to read/update state each iteration**

In the renamed `### 4. Run each task through the loop`, replace its intro line ("Mark the task in-progress, then:") with:

```markdown
Mark the task `[>]` in `.claude/harness/state.md` (and in-progress in `TodoWrite`), then:
```

And replace the final paragraph ("Mark the task complete only when verify + test both pass. Then move to the next.") with:

```markdown
When verify + test both pass, update `.claude/harness/state.md`: set the task to `[x]` with a one-line result, and add a one-line entry to `## Done so far`. Keep `Done so far` to a line or two per task — it is a rolling summary, not a transcript. Then move to the next task. The loader reads this file each loop to build the task's context packet.
```

- [ ] **Step 4: Replace "Progress tracking" to point at state.md**

Replace the `## Progress tracking` section with:

```markdown
## Progress tracking
`.claude/harness/state.md` is the durable source of truth (user-ask summary, task list with status, rolling "done so far"). `TodoWrite` mirrors the task list for live in-session visibility. On re-entry after a restart or compaction, read `state.md` and resume from the first non-`[x]` task — the in-progress task is re-grounded from scratch by `harness-context-loader` (the per-task packet is ephemeral by design).
```

- [ ] **Step 5: Bump version**

In frontmatter, change `version: 2.0.0` to `version: 2.1.0`.

- [ ] **Step 6: Verify**

Read: `skills/harness-orchestrator/SKILL.md`.
Expected: numbered procedure is 1–6 with "Initialize loop state" as step 2; decompose writes to `state.md`; the loop marks `[>]`/`[x]` and updates "Done so far"; Progress tracking points at `state.md`; `version: 2.1.0`.

- [ ] **Step 7: Commit**

```bash
git add skills/harness-orchestrator/SKILL.md
git commit -m "feat(orchestrator): drive loop from resumable .claude/harness/state.md"
```

---

## Task 6: Context-loader — assemble the ephemeral per-loop packet

**Files:**
- Modify: `skills/harness-context-loader/SKILL.md` (procedure + frontmatter)

- [ ] **Step 1: Replace step "Select what's relevant" to use the index**

In `skills/harness-context-loader/SKILL.md`, replace the `### 2. Select what's relevant to THIS task` section with:

```markdown
### 2. Read the loop state and resolve the task's grounding
Read `.claude/harness/state.md` to get the user-ask summary, the "done so far" log, and the current (`[>]`) task. Then read `.claude/skills/project-index.md` and match the current task to its area row(s) to get the exact skills + diagrams to pull. Don't load everything — context bloat degrades output. Read only the selected `project-*` skill bodies and only the `.mmd` files those rows name.

If `project-index.md` is missing, fall back to inferring relevance from the task text and `project-architecture` (and suggest re-running `harness-analyzer` to regenerate the index).
```

- [ ] **Step 2: Replace step "Produce the brief" with the per-loop packet**

Replace the `### 3. Produce the brief` section with:

````markdown
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
````

- [ ] **Step 3: Update frontmatter description + bump version**

Change the `description` to:

```
description: Use before generating or modifying code in a harness-grounded project to assemble a compact per-loop context packet — pull the loop state (.claude/harness/state.md) plus only the project-* skills and diagrams the current task needs (via project-index.md) into a focused brief with acceptance criteria. Keeps each loop's context precise.
```

Change `version: 3.0.0` to `version: 3.1.0`.

- [ ] **Step 4: Verify**

Read: `skills/harness-context-loader/SKILL.md`.
Expected: step 2 reads `state.md` + `project-index.md`; step 3 emits the packet (USER ASK / DONE SO FAR / CURRENT TASK / CONTEXT / ACCEPTANCE) and says it is ephemeral; `version: 3.1.0`.

- [ ] **Step 5: Commit**

```bash
git add skills/harness-context-loader/SKILL.md
git commit -m "feat(context-loader): assemble ephemeral per-loop packet from state + index"
```

---

## Task 7: Verifier — add diagram-conformance check

**Files:**
- Modify: `skills/harness-verifier/SKILL.md` ("Check pattern conformance" step, report block, frontmatter)

- [ ] **Step 1: Extend the pattern-conformance step to cover diagrams**

In `skills/harness-verifier/SKILL.md`, replace the `### 3. Check pattern conformance` section with:

```markdown
### 3. Check pattern + diagram conformance
Compare the changed files against the generated `project-patterns-*` skill (if present, under `.claude/skills/`) and the surrounding code:
- Naming (files, symbols) matches conventions.
- Imports follow the project's style (aliases vs relative).
- New files live in the right place; structure matches siblings.

Also check the change respects the **diagrams it was grounded on** (named in the task's context packet):
- `diagrams/layers.mmd` — the change introduces no dependency the layering rules forbid.
- `diagrams/data-flow.mmd` — new flow follows the canonical path (e.g. doesn't have a route reach the DB directly if the flow goes through a service).

Only check diagrams that were loaded for this task; if none were, skip this sub-check.
```

- [ ] **Step 2: Add a diagrams line to the report block**

In the `### 4. Report` fenced block, add a `diagrams` row after `patterns`:

```
  patterns    ✅  naming / imports / location OK
  diagrams    ✅  respects layers.mmd / data-flow.mmd
```

- [ ] **Step 3: Bump version**

Change `version: 2.0.0` to `version: 2.1.0`.

- [ ] **Step 4: Verify**

Read: `skills/harness-verifier/SKILL.md`.
Expected: step 3 includes the diagram-conformance sub-check (with skip-if-none clause); report block has a `diagrams` row; `version: 2.1.0`.

- [ ] **Step 5: Commit**

```bash
git add skills/harness-verifier/SKILL.md
git commit -m "feat(verifier): add diagram-conformance check (layers/data-flow)"
```

---

## Task 8: End-to-end verification on a sample repo

No files in this repo change (except checking off this task). This exercises the flow per the spec's Verification section.

- [ ] **Step 1: Create a throwaway sample project**

```bash
mkdir -p /tmp/harness-sample/src/services /tmp/harness-sample/src/ui
cd /tmp/harness-sample
printf '{\n  "name":"sample","scripts":{"lint":"echo lint","test":"echo test"}\n}\n' > package.json
printf 'export function getUser(id){ return db.find(id) }\n' > src/services/user.js
printf 'export function LoginForm(){ return null }\n' > src/ui/LoginForm.js
git init -q && git add -A && git commit -qm "sample"
```

- [ ] **Step 2: Run the analyzer against the sample (in a Claude Code session opened on /tmp/harness-sample)**

Invoke `harness-analyzer`.
Expected artifacts:
- `.claude/skills/project-architecture/diagrams/components.mmd` (and `data-flow.mmd` if a flow was detected)
- `.claude/skills/project-patterns-js/diagrams/layers.mmd` (and any `idiom-*.mmd`)
- `.claude/skills/project-index.md` containing a `<!-- harness:index -->` table
- `project-*` SKILL.md bodies that **reference** the `.mmd` files (no inline Mermaid)
- `CLAUDE.md` with the harness block listing the relevance map + loop-state pointers

- [ ] **Step 3: Validate the diagrams parse**

For each generated `.mmd`, confirm it has a valid header and connects declared nodes. Quick check:

```bash
grep -lE '^(graph|flowchart|sequenceDiagram)' /tmp/harness-sample/.claude/skills/**/diagrams/*.mmd
```
Expected: every `.mmd` path is listed (each has a valid header). Optionally render one at https://mermaid.live to confirm it's not broken.

- [ ] **Step 4: Run the orchestrator on a small 2-task requirement**

Invoke `harness-orchestrator` with e.g. "add a logout function and a Logout button".
Expected:
- `.claude/harness/state.md` is created with `## User ask`, a `## Tasks` list, `## Done so far`.
- After task 1 passes, its line flips to `[x]` with a one-line result and `Done so far` gains an entry.
- The loader's packet for each task pulls only the indexed grounding (services-area task does not load UI design tokens, and vice versa).

- [ ] **Step 5: Confirm resumability**

Inspect `.claude/harness/state.md` mid-run; confirm it alone is enough to know the user ask, what's done, and the current task (i.e. a fresh session could resume from it).

- [ ] **Step 6: Confirm idempotent re-analyze**

Run `harness-analyzer` again on the sample. Expected: diagrams + `project-index.md` regenerated; `CLAUDE.md` harness block replaced in place (not duplicated); `state.md` left untouched.

- [ ] **Step 7: Mark complete**

```bash
git add docs/superpowers/plans/2026-06-01-diagram-grounded-harness-context.md
git commit -m "docs: check off end-to-end verification of diagram-grounded harness"
```
```bash
rm -rf /tmp/harness-sample
```

---

## Self-review notes

- **Spec coverage:** standalone diagrams (T1), reference-don't-embed (T2), `project-index.md` (T3), CLAUDE.md wiring (T4), file-backed `state.md` + loop (T5), ephemeral per-loop packet (T6), verifier diagram-conformance (T7), end-to-end + resumability + idempotent re-analyze (T8). All spec sections map to a task.
- **Naming consistency:** files are `state.md`, `project-index.md`, `components.mmd`, `data-flow.mmd`, `layers.mmd`, `idiom-<x>.mmd` throughout; index marker `<!-- harness:index -->`; task markers `[ ]`/`[>]`/`[x]` used identically in T5 and T6.
- **No placeholders:** every edit step shows the exact replacement markdown.
