---
name: harness-orchestrator
description: Use to drive a multi-step build from a requirement — decompose it into tasks and run each through the harness loop (ground → plan → build → verify → test). Coordinates the other harness skills and tracks progress. Invoke when the user asks to implement a feature "with the harness" or wants grounded, verified, end-to-end generation.
version: 2.1.0
---

# Harness Orchestrator

Drive a requirement from idea to verified, tested code by running a disciplined loop. **You are the orchestrator** — you decompose the work and run each step using your own tools and the other harness skills. There is no external runner.

## The loop

```
Requirement
   ↓
Decompose into ordered tasks
   ↓
For each task:
   ground  → load project context  (harness-context-loader)
   plan    → decide the approach against that context
   build   → implement the change
   verify  → lint / type-check / format / patterns  (harness-verifier)
   test    → add and run tests; fix until green
   ↓
Feature complete
```

## Procedure

### 1. Ensure grounding
If the project has no generated `project-*` grounding skills under `.claude/skills/` (and no wired `CLAUDE.md`), run **`harness-analyzer`** first. It generates those skills and wires `CLAUDE.md` so the flow below is the default for every request. Everything downstream relies on this grounding.

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

### 3. Decompose
Break the requirement into the smallest sensible, independently-verifiable tasks. Order them by dependency. **Track them with a todo list** (`TodoWrite`) so progress is visible and nothing is dropped. Example:

> "Add email/password auth" →
> 1. Auth context + `useAuth` hook
> 2. Login form
> 3. Signup form
> 4. Protected-route wrapper
> 5. Integration tests

Write the decomposed tasks into the `## Tasks` list of `.claude/harness/state.md` (in addition to `TodoWrite`). `state.md` is what survives compaction and restarts; `TodoWrite` is the live in-session view of the same list.

### 4. Run each task through the loop
Mark the task `[>]` in `.claude/harness/state.md` (and in-progress in `TodoWrite`), then:
- **Ground** — invoke **`harness-context-loader`** to produce the task brief + acceptance criteria.
- **Plan** — state the approach and the files you'll touch, consistent with the brief.
- **Build** — implement it, following the project's real patterns.
- **Verify** — invoke **`harness-verifier`**. If it fails, read the errors and fix; re-verify. Do not move on while red.
- **Test** — add tests in the project's style and run them. Iterate until green.

When verify + test both pass, update `.claude/harness/state.md`: set the task to `[x]` with a one-line result, and add a one-line entry to `## Done so far`. Keep `Done so far` to a line or two per task — it is a rolling summary, not a transcript. Then move to the next task. The loader reads this file each loop to build the task's context packet.

### 5. Parallel vs serial
- **Serial** when tasks share state or depend on each other (the common case).
- **Parallel** only for genuinely independent tasks. Before dispatching, invoke **`harness-model-router`** with the parallel task list to get a routing table (task → model tier). Then dispatch subagents with the `Agent` tool (see the `superpowers:dispatching-parallel-agents` skill), passing `model: "<tier>"` from the routing table for each task. Give each a self-contained brief and use worktree isolation if they touch overlapping files.

  ```
  Agent({
    prompt: "<self-contained task brief>",
    model: "haiku" | "sonnet" | "opus"   ← from harness-model-router routing table
  })
  ```

### 6. Recover from failures
If a task can't pass verification after a couple of focused attempts, stop and debug deliberately (`superpowers:systematic-debugging`) rather than thrashing. Surface the blocker to the user instead of forcing a broken result.

## Progress tracking
`.claude/harness/state.md` is the durable source of truth (user-ask summary, task list with status, rolling "done so far"). `TodoWrite` mirrors the task list for live in-session visibility. On re-entry after a restart or compaction, read `state.md` and resume from the first non-`[x]` task — the in-progress task is re-grounded from scratch by `harness-context-loader` (the per-task packet is ephemeral by design).

## Definition of done
- Every decomposed task is complete.
- `harness-verifier` passes on the changed code.
- Tests exist in the project's style and are green.
- You've reported results honestly — including anything skipped or still failing.

## See also
- `harness-analyzer` — generates grounding (run first)
- `harness-context-loader` — builds the per-task brief
- `harness-verifier` — quality gate after each build
- `superpowers:test-driven-development`, `superpowers:dispatching-parallel-agents`, `superpowers:systematic-debugging`
