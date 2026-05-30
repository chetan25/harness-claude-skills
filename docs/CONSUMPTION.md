# How to Consume Harness Claude Skills

## The Workflow

```
User clones harness-claude-skills
        ↓
Copies .claude/skills/ to their project
        ↓
Opens Claude Code
        ↓
Says: "Add a feature" (just ask naturally)
        ↓
Claude reads claude.md → auto-invokes orchestrator
        ↓
Orchestrator runs:
  1. Breaks feature into tasks
  2. Loads context (your patterns, architecture)
  3. Writes code (with your conventions)
  4. Verifies (tests, lint, types)
  5. Flags UI for manual check (if needed)
  6. Compares with Figma (if available)
  7. Ships when ready ✓
```

---

## What Users Don't Need to Do

❌ Learn CLI commands  
❌ Mention skills explicitly  
❌ Configure anything  
❌ Run build steps  

---

## What Users Get Automatically

✅ **Smart Code Generation** — Claude generates code that matches YOUR project  
✅ **Verified Output** — Tests, linting, type-checking built-in  
✅ **Design Validation** — Compares UI against Figma (if configured)  
✅ **Feature Decomposition** — Large features break into manageable tasks  
✅ **Iterative Refinement** — Loops if tests fail, until quality gates pass  

---

## Example: "Add Dark Mode"

### User Says:
```
"Add dark mode feature with persistence to localStorage"
```

### Orchestrator Does:
```
1. DECOMPOSE
   ├─ Create theme context + provider
   ├─ Add theme toggle button
   ├─ Apply dark CSS classes
   ├─ Persist to localStorage
   └─ Write tests for each

2. CONTEXT
   ├─ Loads patterns-react.md (your React patterns)
   ├─ Loads design-tokens.md (your colors)
   ├─ Loads test-patterns.md (your test setup)

3. CODE
   ├─ Creates ThemeContext.tsx (matches your patterns)
   ├─ Creates ThemeToggle.tsx (uses your design tokens)
   ├─ Updates main App.tsx

4. VERIFY
   ├─ Runs ESLint ✓
   ├─ TypeScript check ✓
   ├─ Tests pass ✓
   ├─ Coverage threshold met ✓

5. UI CHECK (if needed)
   ├─ Flags: "Review UI in Figma"
   ├─ User checks, confirms ✓

6. SHIP
   ├─ All tests pass
   ├─ Code matches patterns
   ├─ Docs updated
   └─ Ready to commit
```

### Claude Returns:
- ✅ Dark mode fully working
- ✅ All tests passing
- ✅ Persistence working
- ✅ Matches your design tokens
- ✅ Follows your coding patterns
- ✅ Ready to merge

---

## Behind the Scenes

### 1. `.claude/skills/` Are Your Codebook

Each skill is a guide Claude uses:
- `patterns-react.md` — Your React conventions
- `architecture.md` — Project structure
- `design-tokens.md` — Colors, spacing, fonts
- `test-patterns.md` — How you test

Claude reads these **automatically** before writing code.

### 2. `claude.md` Is The Orchestrator Blueprint

When user opens Claude Code in their project, Claude reads `claude.md` which says:

```markdown
# For ANY feature request:
1. Always use harness-orchestrator SKILL
2. Load context from .claude/skills/
3. Follow the 7-phase loop (decompose → context → code → verify → UI check → test → ship)
4. Use Figma MCP if available
```

### 3. MCPs Extend Capabilities

If user configured Figma MCP:
- Claude can fetch design specs
- Compare generated UI against design
- Request changes if misaligned

---

## FAQ

### Q: Do I need to learn new commands?
**A:** No. Just ask Claude naturally. The orchestrator handles everything.

### Q: What if I have a legacy codebase?
**A:** Run "Analyze this project" and Harness learns your patterns automatically.

### Q: Can I use this without `.claude/skills/`?
**A:** Yes, but Claude won't have project context. It works best WITH skills.

### Q: What if my project has no tests?
**A:** Harness generates tests as part of the orchestrator loop.

### Q: Can I use this with non-React projects?
**A:** Yes! Harness works with any tech. Skills adapt to your stack (Python, Node, Go, etc.).

### Q: What about Figma integration?
**A:** If you configure Figma MCP in `.claude/mcp-config.yaml`, Claude can fetch designs and validate UI.

### Q: How do I add custom MCPs?
**A:** Edit `.claude/mcp-config.yaml` and add your MCP server configs. Claude will use them.

### Q: Is this only for Claude Code?
**A:** Phase 0 targets Claude Code. Future phases may support other IDEs.

---

## Troubleshooting

### Claude doesn't use the skills
- **Check:** `claude.md` exists at project root
- **Check:** `.claude/skills/` folder exists
- **Check:** Skills have readable .md files

### Tests fail after generation
- Orchestrator re-runs, fixes issues, retries
- Check `.claude/orchestrator.md` for failure details

### Code doesn't match my style
- Run "Analyze this project" to refresh patterns
- Update `.claude/skills/patterns-*.md` manually if needed

### Claude mentions skills explicitly
- That's okay! It means skills are loaded
- User doesn't need to mention them though

---

## Next Steps

1. **Clone & copy:** See QUICKSTART.md
2. **Detailed setup:** See SETUP.md
3. **Advanced:** See ARCHITECTURE.md for how it works
