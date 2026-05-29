---
name: harness-code-orchestrator
category: harness
description: |
  High-level task orchestrator. Breaks requirements into chunks,
  runs harness loop (think → create → verify → test → next).
  Handles multi-task coordination, parallel execution, state tracking.
tags: [harness, orchestration, task-decomposition]
version: 1.0.0
---

# Harness Code Orchestrator

## Purpose
Coordinate the entire harness workflow:

```
User Requirement
    ↓
Decompose into tasks
    ↓
For each task:
    ├─ Load context (via harness-context-loader)
    ├─ Think (plan approach)
    ├─ Create (delegate to Claude Code)
    ├─ Verify (lint, type-check)
    ├─ Test (write + run tests)
    └─ Next task
    ↓
✅ Feature complete
```

## Usage

### Via CLI
```bash
harness orchestrate "Add user authentication with email/password"
```

### Via Hermes Skill + Delegation
```bash
hermes skill harness-code-orchestrator \
  --requirement "Add user authentication with email/password" \
  --project-root ./src \
  --parallel-limit 2
```

### Programmatically
```python
from harness_orchestrator import Orchestrator

orch = Orchestrator(project_root="./")
result = orch.run(
    requirement="Add user authentication with email/password",
    parallel=True,
    verify=True,
    write_tests=True
)
print(result.summary())
```

## How It Works

### Phase 1: Decomposition
```python
tasks = decompose(requirement)
# Input: "Add user authentication with email/password"
# Output: [
#   "Create AuthContext & useAuth hook",
#   "Create LoginForm component",
#   "Create SignupForm component",
#   "Add protected route wrapper",
#   "Write integration tests"
# ]
```

### Phase 2: For Each Task
```
1. THINK: "What's the approach?"
   - Load context (patterns, architecture)
   - Plan code structure
   - Identify dependencies

2. CREATE: "Generate the code"
   - Call Claude Code with context
   - Delegate via harness-context-loader
   - Get back implementation

3. VERIFY: "Is it correct?"
   - Run linter (ESLint, etc.)
   - Type check (TypeScript)
   - Style check (Prettier)
   - If errors → explain to Claude, regenerate

4. TEST: "Does it work?"
   - Generate test file
   - Run test suite
   - Check coverage
   - If fails → explain, regenerate

5. COMMIT: "Save progress"
   - Write files to disk
   - Update project state
   - Log to orchestrator journal
```

### Phase 3: Coordination
- **Serial**: Tasks in order (if dependencies)
- **Parallel**: Independent tasks concurrently (up to limit)
- **Error handling**: Rollback or skip on failure
- **Recovery**: Re-run failed tasks with more context

## Configuration

`.harness/orchestrator-config.yaml`:
```yaml
orchestrator:
  decompose_strategy: claude  # or: rules, hybrid
  parallel_limit: 2
  
  phases:
    think:
      enabled: true
      max_tokens: 500
    
    create:
      enabled: true
      max_retries: 3
      delegate_tool: claude-code  # or: codex, opencode
    
    verify:
      enabled: true
      fail_on_error: true
      checks:
        - lint
        - type-check
        - style
    
    test:
      enabled: true
      coverage_min: 70
      fail_on_low_coverage: false
    
    commit:
      enabled: true
      auto_commit: false  # Manual review first

  logging:
    level: info  # debug, info, warn, error
    journal: .harness/journal.md
```

## Output

After successful run:

```
.harness/
├── journal.md              # Execution log
├── generated/
│   ├── harness-patterns-*.md
│   ├── harness-arch-*.md
│   └── diagrams/
└── state.json              # Task state for recovery
```

**journal.md** (auto-generated):
```markdown
# Harness Execution Journal
Date: 2025-06-05

## Requirement
Add user authentication with email/password

## Tasks Decomposed
1. ✅ Create AuthContext & useAuth hook (12m)
2. ✅ Create LoginForm component (8m)
3. ✅ Create SignupForm component (8m)
4. ✅ Add protected route wrapper (6m)
5. ✅ Write integration tests (15m)

## Summary
- Total time: 49 minutes
- Tasks: 5 completed, 0 failed
- Code generated: 342 lines
- Tests: 18 passing

## Artifacts
- AuthContext.tsx (89 lines)
- useAuth.ts (45 lines)
- LoginForm.tsx (67 lines)
- SignupForm.tsx (72 lines)
- ProtectedRoute.tsx (24 lines)
- auth.test.tsx (118 lines)

## Context Used
- harness-patterns-react.md (loaded)
- harness-arch-components.md (loaded)
- harness-design-tokens.md (loaded)
```

## Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| Tasks decomposed poorly | Use `--decompose-strategy hybrid` to mix Claude + rules |
| Claude loses context mid-run | Each task reloads via context-loader |
| Tests fail after generation | Set `max_retries: 3`, regenerate with error context |
| Parallel tasks have dependency issues | Use `--parallel-limit 1` or manually order |
| Coverage drops | Set `fail_on_low_coverage: true` to block commit |

## Integration with Other Skills

- **harness-codebase-analyzer**: Runs first to generate context
- **harness-context-loader**: Called for each task
- **harness-verifier**: Runs after code generation
- **harness-readme-generator**: Updates README after success

## See Also
- ARCHITECTURE.md — Deep dive on design
- EXAMPLES.md — Real use cases
