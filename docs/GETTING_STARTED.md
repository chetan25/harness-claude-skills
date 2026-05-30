# Getting Started with Harness

**Harness is an AI dev orchestration system designed for Claude Code.**

## What You'll Do

```
@harness orchestrate "Add dark mode feature"
    ↓
Harness analyzes your project
    ↓
Generates skills (if missing)
    ↓
Injects into Claude's context
    ↓
Coordinates multi-agent workflow
    ↓
7-phase verification & completion
```

## Installation

### 1. Clone Harness into Your Project

```bash
cd your-project
git clone https://github.com/chetan25/harness-claude-skills.git .harness
```

### 2. Enable Harness in Claude Code

Claude Code will auto-detect `.harness/` folder in your project.

### 3. Start Using

In Claude Code, ask:

```
@harness orchestrate "Add user authentication"
```

## The Flow

**Your project:**
```
your-project/
├── src/
├── tests/
├── .harness/                  ← Harness installation
│   ├── skills/
│   ├── generated/             ← Auto-generated (skills + diagrams + cache)
│   └── config.yaml
└── package.json
```

**What Harness Does:**

1. **Detects** your `.harness/` folder
2. **Analyzes** your project (first time only)
3. **Generates** skills with Mermaid diagrams (if missing)
4. **Caches** results (.harness/generated/)
5. **Injects** skills into Claude's prompt
6. **Orchestrates** work through 7 phases
7. **Verifies** everything (code, UI, design, tests, lint/types)

## Your First Command

```
@harness orchestrate "Add dark mode toggle with localStorage"
```

Harness will:

✅ Break task into subtasks  
✅ Load project patterns & architecture diagrams  
✅ Spawn sub-agents for components, tests, styles  
✅ Verify each piece in the UI  
✅ Compare against Figma (if you provide design)  
✅ Write & run tests  
✅ Check lint/TypeScript errors  
✅ Ship when ready  

## Questions?

See:
- **How Claude Commands work:** `docs/CLAUDE_COMMANDS.md`
- **Architecture deep dive:** `docs/ARCHITECTURE.md`
- **Full workflow guide:** `docs/USAGE_GUIDE.md`
