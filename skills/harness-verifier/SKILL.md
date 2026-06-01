---
name: harness-verifier
description: Use after generating or changing code in a harness task to verify it against quality gates — run the project's real lint, type-check, format, and test commands, and check the code matches the project's naming/structure/import conventions. Reports pass/fail and drives fixes until green before the work is considered done.
version: 2.1.0
---

# Harness Verifier

Verify changed code against the project's real quality gates. **You run the project's actual tooling** with `Bash` and read the results — there is no external verifier program. Never claim a check passed without running it and seeing the output (`superpowers:verification-before-completion`).

## When to run
- After each build step in the harness loop, before marking a task done.
- Called by `harness-orchestrator` as the gate between "build" and "test".

## Procedure

### 1. Discover the project's commands
Don't assume — read them from the repo:
- **Node/TS:** read `package.json` `scripts` (e.g. `lint`, `typecheck`, `test`, `format`). Use the project's package manager (`npm`/`pnpm`/`yarn` per lockfile).
- **Python:** check `pyproject.toml` / `tox.ini` / `Makefile` for `ruff`/`flake8`/`pylint`, `mypy`/`pyright`, `pytest`, `black`/`ruff format`.
- **Go:** `go vet`, `golangci-lint`, `gofmt -l`, `go test ./...`.
- **Other stacks:** find the equivalent from the manifest/Makefile/CI config.

If a gate has no configured command in the project, note it as "not configured" — don't invent one or run a global tool the project doesn't use.

### 2. Run the gates
Run each available gate with `Bash` and capture real output. Scope to the changed code where the tooling allows (faster, clearer signal):
- **Lint**
- **Type-check**
- **Format check** (check mode, e.g. `prettier --check`, `black --check` — don't auto-reformat the whole repo)
- **Tests** (the suite, or the relevant subset)

### 3. Check pattern + diagram conformance
Compare the changed files against the generated `project-patterns-*` skill (if present, under `.claude/skills/`) and the surrounding code:
- Naming (files, symbols) matches conventions.
- Imports follow the project's style (aliases vs relative).
- New files live in the right place; structure matches siblings.

Also check the change respects the **diagrams it was grounded on** (named in the task's context packet):
- `diagrams/layers.mmd` — the change introduces no dependency the layering rules forbid.
- `diagrams/data-flow.mmd` — new flow follows the canonical path (e.g. doesn't have a route reach the DB directly if the flow goes through a service).

Only check diagrams that were loaded for this task; if none were, skip this sub-check.

### 4. Report
Summarize each gate as pass / fail / not-configured with the key evidence:

```
VERIFICATION — <path or "changed files">
  lint        ✅
  type-check  ❌  LoginModal.tsx:12  Property 'children' has no initializer
  format      ✅
  tests       ✅  8 passed
  patterns    ✅  naming / imports / location OK
  diagrams    ✅  respects layers.mmd / data-flow.mmd
RESULT: 1 gate failing
```

### 5. Drive fixes
If anything is red: read the actual error, fix the cause (debug deliberately with `superpowers:systematic-debugging` if it's not obvious), and **re-run that gate**. Repeat until all configured gates pass. Only then is the task verified.

## Guardrails
- **Evidence before claims.** "Tests pass" requires a test run you can point to.
- **Don't paper over failures.** Don't loosen configs, skip tests, or add blanket ignores to make a gate green unless the user explicitly asks.
- **Honest reporting.** If a gate can't run (missing dep, broken script), say so plainly rather than marking it passed.

## See also
- `harness-orchestrator` — runs this as the gate after each build step
- `harness-context-loader` — supplies the acceptance criteria this checks against
- `superpowers:verification-before-completion`, `superpowers:systematic-debugging`
