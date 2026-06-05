# Harness Model Router — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `harness-model-router` skill that classifies parallel tasks by complexity and routes each to the cheapest model tier (haiku/sonnet/opus) when `harness-orchestrator` dispatches parallel subagents.

**Architecture:** Two-file change. A new standalone skill encapsulates all classification logic; the orchestrator gets a single additive edit at step 5 (parallel path only) to invoke the router and pass `model:` to each `Agent` call. No new dependencies, no external tooling.

**Tech Stack:** Markdown skill files (`.md` with YAML frontmatter). No build step. Verified by reading file content and checking frontmatter validity.

**Spec:** `docs/superpowers/specs/2026-06-04-model-router-design.md`

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `skills/harness-model-router/SKILL.md` | Full classification logic + routing table emission |
| Modify | `skills/harness-orchestrator/SKILL.md` | Step 5 parallel path — invoke router, pass `model:` to Agent |

---

## Task 1: Create `skills/harness-model-router/SKILL.md`

**Files:**
- Create: `skills/harness-model-router/SKILL.md`

- [ ] **Step 1: Verify the target directory does not already exist**

```bash
ls skills/
```

Expected: no `harness-model-router` folder listed.

- [ ] **Step 2: Write the skill file**

Create `skills/harness-model-router/SKILL.md` with this exact content:

```markdown
---
name: harness-model-router
description: Use when harness-orchestrator is about to dispatch parallel subagents, to classify each task by complexity and annotate it with the right model tier (haiku/sonnet/opus) so cheaper models handle trivial work automatically.
version: 1.0.0
---

# Harness Model Router

Classify a list of parallel task descriptions by complexity and emit a routing table that maps each task to a model tier. **You do this yourself** — read each task description and apply the classification procedure below.

## When to run
- Called by `harness-orchestrator` at step 5, immediately before building the `Agent()` call list for independent parallel tasks.
- No-op for serial tasks — only invoke when tasks are genuinely parallel.

## Procedure

### 1. Receive the parallel task list
Take the list of parallel task descriptions from `harness-orchestrator`. Each entry is a short description of independent work.

### 2. Classify each task

Apply both signals in order. Keywords can only **upgrade** a tier, never downgrade.

#### Step 1 — Task type (primary signal)

| Task type | Tier |
|---|---|
| Read-only / explanation | haiku |
| Trivial mutation (rename, typo, constant, comment) | haiku |
| Code generation (component, endpoint, hook, service) | sonnet |
| Standard feature addition | sonnet |
| Cross-cutting reasoning (debug across layers, investigate) | opus |
| Architecture / design / migration | opus |

#### Step 2 — Keyword scan (confirms or upgrades)

| Keywords present | Tier signal |
|---|---|
| `rename`, `typo`, `comment`, `explain`, `describe`, `list`, `show`, `format` | haiku |
| `add`, `create`, `write`, `implement`, `update`, `build`, `generate`, `test`, `endpoint`, `component`, `hook` | sonnet |
| `refactor`, `debug`, `design`, `architect`, `analyze`, `migrate`, `restructure`, `investigate`, `across`, `system-wide` | opus |

#### Tie-breaking rules

- **Ambiguous → sonnet.** Never silently under-allocate.
- **Multiple modules or layers mentioned → minimum sonnet.** Upgrade to opus if opus keywords are also present.
- **Keywords only upgrade.** A haiku-type task with sonnet keywords becomes sonnet. Never the reverse.

### 3. Emit the routing table

Output the table in context (do **not** write to a file — it is ephemeral per dispatch):

```
ROUTING TABLE
  [1] "<task description>"   → haiku
  [2] "<task description>"   → sonnet
  [3] "<task description>"   → opus
```

`harness-orchestrator` reads this table and passes `model: "<tier>"` to each `Agent` call.

## Model tier reference

| Tier | Model ID | Best for |
|---|---|---|
| haiku | `claude-haiku-4-5-20251001` | Trivial mutations, read-only, explanations |
| sonnet | `claude-sonnet-4-6` | Code generation, standard feature work, tests |
| opus | `claude-opus-4-8` | Architecture, cross-cutting refactors, debugging across layers |

## See also
- `harness-orchestrator` — invokes this skill before parallel dispatch
- `superpowers:dispatching-parallel-agents` — the dispatch mechanism this routing feeds into
```

- [ ] **Step 3: Verify frontmatter is valid**

Read `skills/harness-model-router/SKILL.md` and confirm:
- First line is `---`
- `name:` is `harness-model-router`
- `description:` is present and non-empty
- `version:` is `1.0.0`
- Closing `---` is on its own line before the `# Harness Model Router` heading

- [ ] **Step 4: Verify content completeness**

Confirm the file contains all four required sections:
- `## When to run`
- `## Procedure` with sub-sections `### 1`, `### 2`, `### 3`
- Both classification tables (task type + keyword scan)
- All three tie-breaking rules
- `## Model tier reference` table with all three model IDs
- `## See also`

- [ ] **Step 5: Commit**

```bash
git add skills/harness-model-router/SKILL.md
git commit -m "feat: add harness-model-router skill for parallel subagent model routing"
```

---

## Task 2: Update `harness-orchestrator` step 5

**Files:**
- Modify: `skills/harness-orchestrator/SKILL.md` (step 5 only — lines 72–74)

- [ ] **Step 1: Read the current step 5 text**

Read `skills/harness-orchestrator/SKILL.md` and locate the `### 5. Parallel vs serial` section. Confirm it currently reads:

```
### 5. Parallel vs serial
- **Serial** when tasks share state or depend on each other (the common case).
- **Parallel** only for genuinely independent tasks. To run independent tasks concurrently, dispatch subagents with the `Agent` tool (see the `superpowers:dispatching-parallel-agents` skill). Give each a self-contained brief and use worktree isolation if they touch overlapping files.
```

- [ ] **Step 2: Replace step 5 with the model-routing version**

Replace the `### 5. Parallel vs serial` block with:

```markdown
### 5. Parallel vs serial
- **Serial** when tasks share state or depend on each other (the common case).
- **Parallel** only for genuinely independent tasks. Before dispatching, invoke **`harness-model-router`** with the parallel task list to get a routing table (task → model tier). Then dispatch subagents with the `Agent` tool (see the `superpowers:dispatching-parallel-agents` skill), passing `model: "<tier>"` from the routing table for each task. Give each a self-contained brief and use worktree isolation if they touch overlapping files.

  ```
  Agent({
    prompt: "<self-contained task brief>",
    model: "haiku" | "sonnet" | "opus"   ← from harness-model-router routing table
  })
  ```
```

- [ ] **Step 3: Verify no other lines in the file were changed**

Run:

```bash
git diff skills/harness-orchestrator/SKILL.md
```

Confirm the diff shows only the step 5 block replaced — no other hunks.

- [ ] **Step 4: Verify the updated file still has all original sections**

Read `skills/harness-orchestrator/SKILL.md` and confirm these headings are all still present and unchanged:
- `## The loop`
- `### 1. Ensure grounding`
- `### 2. Initialize loop state`
- `### 3. Decompose`
- `### 4. Run each task through the loop`
- `### 5. Parallel vs serial` (updated)
- `### 6. Recover from failures`
- `## Progress tracking`
- `## Definition of done`
- `## See also`

- [ ] **Step 5: Commit**

```bash
git add skills/harness-orchestrator/SKILL.md
git commit -m "feat: invoke harness-model-router in orchestrator parallel dispatch"
```

---

## Self-Review Checklist

After both tasks are complete, verify:

- [ ] `harness-model-router/SKILL.md` exists with valid frontmatter
- [ ] All three model IDs in the tier reference table are correct (`claude-haiku-4-5-20251001`, `claude-sonnet-4-6`, `claude-opus-4-8`)
- [ ] Tie-breaking rules state ambiguous → sonnet (not haiku)
- [ ] Orchestrator step 5 references `harness-model-router` by name
- [ ] Orchestrator step 5 shows `model:` param in the Agent call example
- [ ] No other sections of `harness-orchestrator/SKILL.md` were modified
- [ ] Both commits are on the main branch and `git log --oneline -3` shows them
