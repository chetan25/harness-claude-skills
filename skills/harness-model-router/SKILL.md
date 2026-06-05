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
