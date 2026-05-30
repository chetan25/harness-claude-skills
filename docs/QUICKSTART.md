# Harness Claude Skills — Quick Start (5 Minutes)

## 3-Step Setup

### Step 1: Clone Harness Skills
```bash
git clone https://github.com/chetan25/harness-claude-skills.git
```

### Step 2: Copy to Your Project
```bash
cp -r harness-claude-skills/.claude/skills/ my-project/.claude/
```

### Step 3: Open in Claude Code
```bash
cd my-project
# Open in Claude Code
```

---

## That's It! Now Use It

**Just ask Claude naturally:**

```
"Analyze this project and help me add dark mode feature"
```

or

```
"Add user authentication with email and password"
```

Claude will:
1. ✅ Read your project structure
2. ✅ Generate domain skills for your code
3. ✅ Create a `claude.md` with orchestrator instructions
4. ✅ Break your feature into tasks
5. ✅ Write code with your patterns
6. ✅ Run tests and verify
7. ✅ Ship when ready

**No CLI. No commands. Just natural language.**

---

## What Gets Generated

After analysis, you'll have:
```
my-project/
├── claude.md                           ← Instructions for Claude
├── .claude/
│   ├── skills/
│   │   ├── patterns-react.md          ← Your React patterns
│   │   ├── architecture.md            ← Your project structure
│   │   ├── design-tokens.md           ← UI tokens (if found)
│   │   └── test-patterns.md           ← How you test
│   ├── orchestrator.md                ← Task tracking
│   └── mcp-config.yaml                ← Figma + MCPs
```

---

## Next Steps

- Check `docs/SETUP.md` for detailed installation
- Read `docs/CONSUMPTION.md` for usage patterns
- See `examples/react-app/` for a working example
