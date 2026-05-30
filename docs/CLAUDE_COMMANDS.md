# Claude Commands Guide

**Harness is integrated as Claude Commands** — no CLI needed!

## Available Commands

### @harness orchestrate

**Runs the full 7-phase workflow**

```
@harness orchestrate "Add dark mode toggle"
```

**What it does:**
1. Analyzes the requirement
2. Generates skills (if missing)
3. Breaks into subtasks
4. Spawns sub-agents for each piece
5. Verifies in UI + against Figma
6. Writes & runs tests
7. Final lint/type/design checks
8. Ships when complete

**Optional parameters:**
```
@harness orchestrate "feature description" --figma-url "design-url" --cache refresh
```

### @harness analyze

**Scans project & generates skills (one-time)**

```
@harness analyze
```

**Output:**
- Project structure analysis
- Component/module diagrams (Mermaid)
- Code pattern extraction
- Stored in `.harness/generated/`
- Cached for future use

**Usually runs automatically**, but you can trigger manually.

### @harness context

**Shows loaded context & patterns**

```
@harness context
```

**Displays:**
- Loaded skills
- Generated diagrams
- Cached patterns
- Architecture overview

Useful for debugging or understanding what Claude sees.

### @harness verify

**Runs verification suite on existing code**

```
@harness verify ./src/components
```

**Checks:**
- Lint (ESLint/Prettier)
- Types (TypeScript)
- Tests
- Design consistency (if Figma provided)

### @harness cache

**Manage cached analysis**

```
@harness cache clear          # Clear all cache
@harness cache refresh        # Re-analyze project
@harness cache status         # Show what's cached
```

## How It Works Behind the Scenes

```
Claude Code IDE
    ↓
@harness command triggered
    ↓
Auto-detect `.harness/` folder
    ↓
Load cache (or run analysis if missing)
    ↓
Generate Mermaid diagrams for architecture
    ↓
Inject patterns into Claude's system prompt
    ↓
Claude executes (grounded by skills)
    ↓
Return results + cache for next time
```

## Auto-Detection

Harness **automatically detects** your project:

```
When you use @harness in Claude Code:
  1. Looks for `.harness/` folder
  2. If found: Loads cached skills
  3. If cache stale: Re-analyzes
  4. If missing: Asks before analyzing
  5. Injects into prompt
```

## Examples

### Example 1: Add Authentication

```
@harness orchestrate "Add email/password authentication with JWT tokens"
```

Harness will:
- Detect your React patterns
- Load auth skill examples
- Coordinate auth hook + form + API + tests
- Verify against your routing patterns
- Ship complete feature

### Example 2: Add Design System Component

```
@harness orchestrate "Create Button component following design system" --figma-url "https://figma.com/..."
```

Harness will:
- Analyze Figma design
- Extract colors, typography, spacing
- Generate component with tests
- Verify rendered output matches Figma
- Ship when design-compliant

### Example 3: Refactor Existing Code

```
@harness orchestrate "Refactor UserService to use repository pattern"
```

Harness will:
- Analyze current code
- Plan refactoring strategy
- Decompose into steps
- Implement + test each step
- Verify no regressions
- Ship refactored code

## Tips & Tricks

**First time setup:**
```
@harness analyze
# Then: @harness context
# See what was detected
```

**Refresh if patterns changed:**
```
@harness cache refresh
# Re-scans project
```

**Debug what Claude sees:**
```
@harness context
# Shows loaded skills + diagrams
```

**Force full re-analysis:**
```
@harness cache clear
@harness orchestrate "your feature"
# Fresh analysis
```

## What Gets Cached?

```
.harness/generated/
├── patterns.json              # Extracted conventions
├── architecture.md            # Component structure
├── diagrams.mermaid           # Visual architecture
├── design-tokens.json         # Colors, spacing, etc.
├── cache.json                 # Metadata
└── skills-summary.md          # What was detected
```

Cache stays until:
- You run `@harness cache refresh`
- You manually edit project
- Cache expires (configurable)

## Troubleshooting

**"Project not detected"**
- Check `.harness/` folder exists
- Run `@harness analyze` manually

**"Cache seems stale"**
- Run `@harness cache refresh`
- Or `@harness cache clear` then try again

**"Generated code doesn't match my style"**
- Patterns might be incomplete
- Run `@harness analyze` to re-scan
- Check `@harness context` to see detected patterns

**"Figma comparison failed"**
- Ensure Figma URL is valid
- Check design system is documented

---

**Questions?** See GETTING_STARTED.md or ARCHITECTURE.md
