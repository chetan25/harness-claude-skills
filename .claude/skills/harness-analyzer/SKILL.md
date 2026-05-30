---
name: harness-codebase-analyzer
category: harness
description: |
  Scans a project, analyzes code patterns, architecture, and test structure.
  Auto-generates grounding skills with Mermaid diagrams for the LLM.
  
  Outputs:
  - harness-patterns-{lang}.md (code style, conventions)
  - harness-arch-{domain}.md (component structure)
  - harness-design-tokens.md (UI tokens if found)
  - harness-test-patterns.md (testing approach)
  - mermaid diagrams (architecture visualization)
tags: [harness, ai-grounding, codebase-analysis]
version: 1.0.0
---

# Harness Codebase Analyzer

## Purpose
Before Claude Code generates anything, ground it with your project's:
- **Patterns**: How you name things, structure files, write tests
- **Architecture**: Component relationships, dependencies, module boundaries
- **Design tokens**: Typography, colors, spacing (if UI project)
- **APIs**: Public interfaces, types, contracts

## How It Works

1. **Scans** your project root (configurable depth)
2. **Analyzes**:
   - File structure (detect React, Node, Python, etc.)
   - Code imports & dependencies
   - Test structure (Jest, pytest, etc.)
   - Package.json / pyproject.toml / go.mod
   - Design files (if Figma tokens, tailwind.config, etc.)
3. **Generates**:
   - Hermes skills (one per domain)
   - Mermaid diagrams (architecture, dependency graph)
   - Pattern examples (code snippets)
4. **Updates** your project's `.harness/generated/` folder

## Usage

### Via CLI
```bash
harness analyze ./src --output .harness/generated
```

### Via CLI
```bash
harness analyze ./src
```

### Programmatically
```python
from harness_analyzer import CodebaseAnalyzer

analyzer = CodebaseAnalyzer(project_root="./")
report = analyzer.analyze()
analyzer.generate_skills(output_dir=".harness/generated")
print(report.summary())
```

## Configuration

Create `.harness/analyzer-config.yaml`:
```yaml
scan:
  root: ./src
  exclude:
    - node_modules
    - dist
    - .git
  depth: 5

analysis:
  detect_language: true
  extract_patterns: true
  build_dependency_graph: true

output:
  generate_skills: true
  generate_diagrams: true
  format: markdown

targets:
  - patterns
  - architecture
  - design-tokens
  - test-structure
  - api-contracts
```

## Output Example

For a React project, generates:

**harness-patterns-react.md**
```markdown
# React Patterns in This Project

## File Structure
\`\`\`
src/
  components/
    Button/
      Button.tsx
      Button.test.tsx
      Button.stories.tsx
    Card/
      ...
  hooks/
  utils/
  types/
\`\`\`

## Naming Conventions
- Components: PascalCase (Button.tsx)
- Hooks: camelCase, prefix with 'use' (useAuth.ts)
- Utils: camelCase (formatDate.ts)
- Types: PascalCase, suffix with 'Props' (ButtonProps)

## Imports Style
\`\`\`typescript
// Absolute imports
import { Button } from '@/components/Button';
import { useAuth } from '@/hooks/useAuth';

// Avoid relative imports in src/
\`\`\`

## Testing Pattern
\`\`\`typescript
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('should render with label', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
});
\`\`\`
```

## Integration with Harness Loop

When `harness-code-orchestrator` runs, it:
1. Calls this skill to load/refresh patterns
2. Embeds outputs into context prompts
3. Ensures Claude Code stays aligned with project

## Pitfalls

- **Slow on large repos**: Exclude node_modules, dist, etc.
- **Language misdetection**: Manually set in config if needed
- **Stale artifacts**: Re-run after major refactors

## See Also
- `harness-context-loader` — Uses outputs to inject context
- `harness-code-orchestrator` — Runs before each task
