# How to Use Harness Claude Skills in Your Project

## The Goal

You want to use Claude Code to build features in your project, but Claude needs context about your codebase to generate better code. This guide shows how to install Harness and use it.

---

## Installation

### Step 1: Clone Harness into Your Project

```bash
cd your-project
git clone https://github.com/chetan25/harness-claude-skills.git .harness
cd .harness
python setup.py --local
cd ..
```

This creates:
- `.harness/` — The Harness installation
- `.harness/generated/` — Project-specific context files (auto-generated)
- `.harness/config/default.yaml` — Configuration

### Step 2: Make `harness` Command Available

Add to your `.bashrc`, `.zshrc`, or shell config:

```bash
export PATH="$PATH:$(pwd)/.harness/cli"
```

Or use it directly:
```bash
python .harness/cli/harness-cli.py
```

---

## Usage: 3-Step Workflow

### Step 1: Analyze Your Project

```bash
harness analyze ./src
```

This scans your codebase and generates:
- Pattern files (React, TypeScript, testing conventions)
- Architecture diagrams (Mermaid format)
- Design tokens (colors, spacing, typography)
- API contracts
- Test structure guides

All go into `.harness/generated/`

### Step 2: Get Context for Your Task

```bash
harness context "Add user authentication modal"
```

This outputs a prompt injection you can copy-paste into Claude Code. It includes:
- Your project's React patterns
- Your testing conventions
- Similar code examples
- Design token guidance

### Step 3: Generate + Verify

Paste the context into Claude Code, describe your feature, and Claude generates code.

Then verify it:
```bash
harness verify ./src/components/LoginModal
```

This checks:
- ESLint (code style)
- TypeScript (types are correct)
- Tests pass
- Coverage meets threshold

---

## Full Example: Add Dark Mode

```bash
# 1. Analyze project (do this once)
harness analyze ./src

# 2. Get context for dark mode
harness context "Add dark mode toggle with localStorage persistence"
# Output: Prompt injection mentioning your theme context, localStorage patterns, etc.

# 3. Copy that prompt into Claude Code
# → Paste in: "Here's your project's pattern context: [prompt from harness context]"
# → Then ask: "Add dark mode toggle with localStorage persistence"
# → Claude generates code

# 4. Verify the generated code
harness verify ./src/features/DarkMode

# 5. Write tests (Claude can generate these too)
harness test ./src/features/DarkMode.test.tsx

# 6. Commit
git add .
git commit -m "feat: add dark mode toggle"
```

---

## Commands Reference

```bash
# Analysis
harness analyze ./src                           # Scan project once
harness analyze ./src --output .harness/gen2    # Custom output dir

# Context
harness context "Feature description"           # Get prompt injection
harness context "Feature" --include patterns,design-tokens,api  # Specific context

# Orchestration (automated)
harness orchestrate "Feature description"       # Full loop: decompose → create → verify → test
harness think "Feature description"             # Just decomposition (no code generation)

# Verification
harness verify ./path/to/generated-code         # Lint + type + test
harness test ./file.test.ts                     # Run tests only

# Status
harness status                                  # Show project state
harness journal                                 # View execution log
harness journal --last 5                        # Last 5 entries

# Configuration
harness config show                             # Print current config
harness config set analyzer.depth 4             # Change setting
```

---

## File Structure After Installation

```
your-project/
├── .harness/                                   # Harness installation
│   ├── cli/
│   │   ├── harness-cli.py                     # Main command
│   │   └── commands/                          # Command implementations
│   ├── skills/                                 # 5 skills
│   │   ├── harness-codebase-analyzer/
│   │   ├── harness-context-loader/
│   │   ├── harness-code-orchestrator/
│   │   ├── harness-verifier/
│   │   └── harness-readme-generator/
│   ├── config/
│   │   └── default.yaml                       # Harness config
│   ├── generated/                             # AUTO-GENERATED
│   │   ├── patterns-react.md
│   │   ├── patterns-typescript.md
│   │   ├── architecture.md
│   │   ├── design-tokens.md
│   │   ├── test-patterns.md
│   │   └── diagrams/
│   │       ├── architecture.mermaid
│   │       └── dependency-graph.mermaid
│   └── journal.md                             # Execution log
│
├── .harness-config.yaml                       # Project-specific config (gitignored)
├── src/                                        # Your code
└── ...
```

---

## Configuration

Create `.harness-config.yaml` in your project root to customize:

```yaml
harness:
  project_name: my-app
  project_root: ./src
  
analyzer:
  scan_depth: 5
  exclude:
    - node_modules
    - dist
    - .git
  languages:
    - javascript
    - typescript
    - jsx
    - tsx
  
context:
  include:
    - patterns
    - architecture
    - design-tokens
    - test-examples
  
verifier:
  lint: true
  lint_config: .eslintrc.json
  type_check: true
  test: true
  coverage_min: 70
```

---

## Sharing with Teammates

### Option 1: Commit .harness/ to Git

```bash
# Let teammates get the same setup
git add .harness/
git commit -m "chore: add harness claude skills"
git push

# Teammates:
git pull
.harness/setup.py --local
```

### Option 2: Document in README

Add to your project's README:

```markdown
## Using Claude Code with Harness

1. Install Harness:
   ```bash
   git clone https://github.com/chetan25/harness-claude-skills.git .harness
   cd .harness && python setup.py --local
   ```

2. Analyze your project:
   ```bash
   harness analyze ./src
   ```

3. When using Claude Code, get context:
   ```bash
   harness context "Your feature"
   ```

4. Verify generated code:
   ```bash
   harness verify ./path/to/generated
   ```
```

---

## Troubleshooting

### "harness: command not found"

**Solution 1:** Use full path
```bash
python .harness/cli/harness-cli.py analyze ./src
```

**Solution 2:** Add to PATH
```bash
export PATH="$PATH:$(pwd)/.harness/cli"
harness analyze ./src
```

### ".harness/generated/ is empty"

**Solution:** Run analyze first
```bash
harness analyze ./src
```

### "My patterns aren't matching"

**Solution:** Refresh analysis
```bash
rm -rf .harness/generated/*
harness analyze ./src
```

### "Claude isn't following my style"

**Solution 1:** Check the context
```bash
harness context "Your feature" | head -100
# Are your patterns in there? If not, adjust .harness-config.yaml
```

**Solution 2:** Be explicit in Claude Code
Paste context AND describe your style: "Use React hooks, prefer functional components, use Tailwind for styling"

---

## Next: Automate Everything (Optional)

Once you're comfortable with manual workflow, try:

```bash
harness orchestrate "Add dark mode toggle"
```

This runs the full loop automatically:
1. Decompose the feature into tasks
2. Generate code for each task (with context)
3. Verify (lint, type, test)
4. Write tests
5. Show execution journal

See `docs/ARCHITECTURE.md` for how this works.

---

**Questions?** Check:
- `docs/INSTALL.md` — Detailed installation
- `docs/ARCHITECTURE.md` — How Harness works
- `PROJECT_STATUS.md` — Roadmap & phases
- `skills/*/SKILL.md` — Individual skill docs
