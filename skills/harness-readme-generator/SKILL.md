---
name: harness-readme-generator
category: harness
description: |
  Auto-generates project README with links to context skills.
  Keeps documentation in sync with codebase analysis.
tags: [harness, documentation, readme]
version: 1.0.0
---

# Harness README Generator

## Purpose
Automatically generate or update project README with:
- Links to generated context skills
- How-to for using harness
- Architecture overview
- Codebase structure

Keeps docs in sync with your actual codebase.

## Usage

### Via CLI
```bash
harness readme-generate
```

### Via Hermes Skill
```bash
hermes skill harness-readme-generator \
  --project-root ./src \
  --output ./README-harness.md
```

### Programmatically
```python
from harness_readme_gen import ReadmeGenerator

gen = ReadmeGenerator(project_root="./")
readme = gen.generate()
gen.write(output_file="./README.md")
```

## Generated Content

Auto-generates:

```markdown
# Project README

## How to Use Harness

This project uses Harness for AI-assisted development.

### Quick Start
\`\`\`bash
harness analyze ./src
harness orchestrate "Your feature request"
\`\`\`

## Codebase Context (for AI)

When using Claude Code, reference:
- [Code Patterns](./docs/harness-patterns-*.md) — Naming, structure, imports
- [Architecture](./docs/harness-arch-*.md) — Component relationships
- [Design Tokens](./docs/harness-design-tokens.md) — Colors, spacing, typography
- [Test Patterns](./docs/harness-test-patterns.md) — How tests are written

## Project Structure

[Auto-generated tree of main directories]

## Technologies

[Auto-detected from package.json, tsconfig.json, etc.]
```

## Configuration

`.harness/readme-config.yaml`:
```yaml
generator:
  include_sections:
    - overview
    - quickstart
    - architecture
    - context_links
    - project_structure
    - technologies
    - commands
    - examples

  style: minimal  # or: detailed, comprehensive
  
  output:
    file: ./README-HARNESS.md
    replace_existing: false  # Set true to overwrite README.md
```

## Integration

After `harness-code-orchestrator` completes:
1. Calls `harness-readme-generator`
2. Updates README with new context links
3. Commits to version control

## Pitfalls

- **Long README**: Use `style: minimal` for summaries
- **Outdated content**: Re-run after major refactors
- **Lost customizations**: Use `replace_existing: false`, manually merge

## See Also
- `harness-codebase-analyzer` — Generates content
- `harness-code-orchestrator` — Runs generator after tasks
