# Design: harness-model-router

**Date:** 2026-06-04  
**Status:** Approved  
**Scope:** Automatic model-tier routing for parallel subagents in the harness loop

---

## Problem

The harness orchestrator spawns parallel subagents for independent tasks using the `Agent` tool, which accepts a `model` parameter. Today every subagent inherits the session model regardless of task complexity, wasting tokens on expensive models for trivial work.

The session model cannot be switched mid-run without user intervention, so automatic routing is only feasible for parallel subagents.

---

## Goal

A standalone skill (`harness-model-router`) that:

1. Receives the list of parallel task descriptions from `harness-orchestrator`
2. Classifies each task by complexity (keywords + task type)
3. Emits a routing table (task → model tier)
4. `harness-orchestrator` reads the table and passes `model: "<tier>"` to each `Agent` call

---

## Out of scope

- Session-level model recommendation (advisory-only, not automatic — excluded)
- Serial task routing (main loop always runs on session model — excluded)
- File-count or diagram-complexity signals (keywords + task type are sufficient)

---

## Skill: harness-model-router

**File:** `skills/harness-model-router/SKILL.md`  
**Version:** 1.0.0

**Frontmatter description (auto-load trigger):**
> "Use when harness-orchestrator is about to dispatch parallel subagents, to classify each task by complexity and annotate it with the right model tier (haiku/sonnet/opus) so cheaper models handle trivial work automatically."

### Classification procedure

Apply in order. Keywords can only **upgrade** a tier, never downgrade.

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

| Keywords | Tier signal |
|---|---|
| `rename`, `typo`, `comment`, `explain`, `describe`, `list`, `show`, `format` | haiku |
| `add`, `create`, `write`, `implement`, `update`, `build`, `generate`, `test`, `endpoint`, `component`, `hook` | sonnet |
| `refactor`, `debug`, `design`, `architect`, `analyze`, `migrate`, `restructure`, `investigate`, `across`, `system-wide` | opus |

#### Tie-breaking rules

- Ambiguous → **sonnet** (never silently under-allocate)
- Task mentions multiple modules or layers → minimum **sonnet**; upgrade to opus if opus keywords present
- Keywords upgrade only — a haiku-type task with sonnet keywords becomes sonnet; never the reverse

### Output format

Emitted in context (not written to disk — ephemeral per dispatch):

```
ROUTING TABLE — <run identifier>
  [1] "<task description>"   → haiku
  [2] "<task description>"   → sonnet
  [3] "<task description>"   → opus
```

---

## Integration: harness-orchestrator (step 5 change)

The only change to `harness-orchestrator` is at **step 5 — Parallel vs serial**, parallel path.

**Before:**
> Dispatch subagents with the `Agent` tool. Give each a self-contained brief.

**After:**
```
1. Invoke harness-model-router with the parallel task list
2. Read the ROUTING TABLE it emits
3. For each task, include model: "<tier>" in the Agent call

Agent({
  prompt: "<self-contained task brief>",
  model: "haiku" | "sonnet" | "opus"   ← from routing table
})
```

No other part of the orchestrator loop changes. Serial tasks are unaffected.

---

## Model tier reference

| Tier | Model ID | Best for |
|---|---|---|
| haiku | `claude-haiku-4-5-20251001` | Trivial mutations, read-only, explanations |
| sonnet | `claude-sonnet-4-6` | Code generation, standard feature work, tests |
| opus | `claude-opus-4-8` | Architecture, cross-cutting refactors, debugging across layers |

---

## Files to create / modify

| Action | File |
|---|---|
| Create | `skills/harness-model-router/SKILL.md` |
| Modify (step 5 only) | `skills/harness-orchestrator/SKILL.md` |

---

## Success criteria

- `harness-model-router` classifies a list of task descriptions and emits a valid routing table
- `harness-orchestrator` passes the correct `model` param to each parallel `Agent` call
- Ambiguous tasks default to sonnet, never silently downgrade to haiku
- Serial tasks are unaffected by this change
