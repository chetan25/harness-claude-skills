---
name: harness-context-loader
category: harness
description: |
  Builds AI-ready context prompts from codebase analysis.
  Injects grounding into Claude Code prompts to reduce hallucination.
tags: [harness, ai-grounding, prompt-engineering]
version: 1.0.0
---

# Harness Context Loader

## Purpose
Take outputs from `harness-codebase-analyzer` and transform them into
**injection prompts** that guide Claude Code toward your project's patterns,
style, and conventions.

## How It Works

1. **Loads** generated skills & diagrams from analyzer
2. **Selects** relevant context for the task
   - What architecture diagram matters?
   - What patterns apply?
   - Which test examples?
3. **Builds** a context-injection prompt
4. **Injects** into Claude Code prompt

## Usage

### Via CLI
```bash
harness context "Add user authentication modal"
```

### Programmatically
```python
from harness_loader import ContextLoader

loader = ContextLoader(project_root="./")
context = loader.build_context(
    task="Add user authentication modal",
    include=["patterns", "design-tokens", "test-examples"]
)
print(context.as_prompt())
```

## Output Example

For task "Add user authentication modal":

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLAUDE CODE CONTEXT INJECTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT: my-app (React + TypeScript)
TASK: Add user authentication modal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHITECTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Mermaid diagram of components]
- Modal lives in src/components/Modal/
- Auth logic in src/hooks/useAuth
- Types in src/types/auth.ts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CODE PATTERNS (React)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Naming:
- Components: PascalCase (AuthModal.tsx)
- Hooks: useXxx (useAuth.ts)
- Files: src/components/AuthModal/

Imports (use absolute paths):
  import { useAuth } from '@/hooks/useAuth';
  import { Button } from '@/components/Button';

Structure:
  src/components/AuthModal/
    ├── AuthModal.tsx (component)
    ├── AuthModal.test.tsx (tests)
    ├── AuthModal.module.css (styles)
    └── types.ts (local types)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN TOKENS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Colors:
  --color-primary: #1976d2
  --color-surface: #fff
  --color-error: #d32f2f

Spacing: 8px base unit
  sm: 4px, md: 8px, lg: 16px, xl: 24px

Typography:
  heading-1: 32px, bold
  body: 14px, regular

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST PATTERN (Jest + React Testing Library)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

describe('AuthModal', () => {
  it('should render login form', () => {
    render(<AuthModal isOpen={true} />);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });
});

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACCEPTANCE CRITERIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Component in src/components/AuthModal/
✓ Follows naming pattern: AuthModal.tsx
✓ Uses @/ imports
✓ Includes .test.tsx with >80% coverage
✓ Uses project design tokens (colors, spacing)
✓ Accessible (ARIA labels, keyboard nav)
✓ TypeScript: no 'any' types
```

## Integration with Orchestrator

`harness-code-orchestrator` uses this to:
1. Load context for each task chunk
2. Build prompt injections
3. Pass to Claude Code
4. Verify output matches context

## Configuration

`.harness/context-config.yaml`:
```yaml
loader:
  auto_select: true  # Auto-pick relevant context
  max_tokens: 2000   # Truncate if needed
  
context_sources:
  - patterns
  - architecture
  - design-tokens
  - test-examples
  - api-docs

injection_format: markdown  # or: yaml, json
```

## Pitfalls

- **Context bloat**: Too much context → Claude gets confused
- **Stale context**: Re-run analyzer if patterns change
- **Wrong context**: Manually specify if auto-select fails

## See Also
- `harness-codebase-analyzer` — Generates context
- `harness-code-orchestrator` — Uses context to run tasks
