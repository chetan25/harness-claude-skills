---
name: harness-verifier
category: harness
description: |
  Post-generation verification: lint, type-check, test, style check.
  Ensures generated code meets quality gates before shipping.
tags: [harness, verification, quality-gates]
version: 1.0.0
---

# Harness Verifier

## Purpose
Verify generated code meets quality standards:
- **Lint**: ESLint, Pylint, etc.
- **Type-check**: TypeScript, mypy, etc.
- **Test**: Run test suite, check coverage
- **Style**: Prettier, Black, etc.
- **Pattern**: Does code match project conventions?

## Usage

### Via CLI
```bash
harness verify ./src/components/LoginModal
```

### Via Hermes Skill
```bash
hermes skill harness-verifier \
  --path ./src/components/LoginModal \
  --checks lint,type-check,test
```

### Programmatically
```python
from harness_verifier import Verifier

verifier = Verifier(config_file=".harness/verifier-config.yaml")
results = verifier.verify(
    code_path="./src/components/LoginModal",
    checks=["lint", "type-check", "test"]
)
print(results.summary())
```

## Configuration

`.harness/verifier-config.yaml`:
```yaml
verifier:
  checks:
    - lint
    - type-check
    - style
    - test
    - coverage
    - patterns

  lint:
    enabled: true
    config: .eslintrc.json
    fail_on_warning: false

  type_check:
    enabled: true
    language: typescript
    fail_on_error: true

  style:
    enabled: true
    formatter: prettier
    config: .prettierrc

  test:
    enabled: true
    runner: jest
    pattern: "*.test.ts{,x}"
    fail_on_failure: true

  coverage:
    enabled: true
    min_percent: 70
    fail_on_low: false

  patterns:
    enabled: true
    check_naming: true
    check_structure: true
    check_imports: true
```

## Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERIFICATION RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Path: ./src/components/LoginModal

✅ LINT (ESLint)
   - No errors

❌ TYPE-CHECK (TypeScript)
   - Error: Property 'children' has no initializer
   - File: LoginModal.tsx:12

✅ STYLE (Prettier)
   - No issues

✅ TEST (Jest)
   - 8 passing
   - 0 failing

✅ COVERAGE
   - Statements: 82%
   - Branches: 75%
   - Functions: 88%

✅ PATTERNS
   - Naming: OK (PascalCase)
   - Structure: OK (component/ folder)
   - Imports: OK (absolute paths)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY: 5/6 checks passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Integration with Orchestrator

When orchestrator runs, it:
1. Generates code via Claude Code
2. Calls `harness-verifier`
3. If failures → Explains errors to Claude, regenerates
4. If passing → Commits to project

## Error Recovery

When verification fails:

```python
errors = verifier.verify(code_path)
if errors:
    # Explain errors to Claude
    context = f"""
Previous code failed verification:
{errors.summary()}

Please fix:
{errors.explanation()}
"""
    # Claude regenerates with error context
```

## Pitfalls

- **Too strict**: Set `fail_on_warning: false` to allow minor issues
- **Slow tests**: Use `--timeout 30` to skip slow tests during iteration
- **Coverage too high**: Adjust `coverage_min` based on project reality

## See Also
- `harness-code-orchestrator` — Uses verifier in loop
- `harness-context-loader` — Provides pattern context for verification
