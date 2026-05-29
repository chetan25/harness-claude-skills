# Harness Claude Skills — Project Status

**Status**: 🟢 Alpha v0.1.0 — Foundation Complete  
**Date**: June 2025  
**Repo**: `/tmp/harness-claude-skills`

---

## ✅ Completed (Phase 0: Foundation)

### Repository Structure
- [x] Core directory layout created
  - `skills/` — Five Hermes skills
  - `cli/` — Command-line interface (placeholder)
  - `docs/` — Documentation
  - `examples/` — Example projects (scaffolding)
  - `tests/` — Test suite (scaffolding)

### Skill Documentation (SKILL.md Files)
- [x] **harness-codebase-analyzer** — Scans project, generates patterns
- [x] **harness-context-loader** — Builds AI-ready context prompts
- [x] **harness-code-orchestrator** — Coordinates decompose→think→create→verify→test loop
- [x] **harness-verifier** — Validates generated code (lint, type-check, test)
- [x] **harness-readme-generator** — Auto-documents with context links

### Main Documentation
- [x] **README.md** — Overview, quick start, features, examples
- [x] **ARCHITECTURE.md** — Deep dive on design, data flow, error handling
- [x] **INSTALL.md** — Local vs global installation instructions

### Configuration & Setup
- [x] **package.json** — npm package metadata
- [x] **setup.py** — Python setup script (local/global modes)
- [x] **LICENSE** — MIT
- [x] **.gitignore** — Standard exclusions
- [x] **Git repo** — Initialized with first commit

---

## 📝 Next Steps (1-5: Implementation)

### Phase 1: CLI Tool (`cli/harness-cli.py`)
**Priority**: 🔴 HIGH — Needed for all user interactions

```
Tasks:
  [ ] Implement command structure: analyze, orchestrate, context, verify, test
  [ ] Add argument parsing (click or argparse)
  [ ] Implement entry point for each command
  [ ] Add help text & examples
  [ ] Test with example project
```

**Artifacts**:
- `cli/harness-cli.py` (main entry point)
- `cli/commands/analyze.py`
- `cli/commands/orchestrate.py`
- `cli/commands/context.py`
- etc.

---

### Phase 2: Codebase Analyzer Skill
**Priority**: 🔴 HIGH — Foundation for context

```
Tasks:
  [ ] Detect project language/framework
  [ ] Build AST parsers (Python, JavaScript, etc.)
  [ ] Extract code patterns (naming, structure)
  [ ] Build dependency graph
  [ ] Generate Mermaid architecture diagrams
  [ ] Create pattern markdown files
  [ ] Cache analysis results
```

**Artifacts**:
- `skills/harness-codebase-analyzer/scripts/analyzer.py`
- `skills/harness-codebase-analyzer/templates/mermaid-templates/*.mermaid`
- Generated: `.harness/generated/harness-patterns-*.md`

---

### Phase 3: Context Loader Skill
**Priority**: 🔴 HIGH — Feeds Claude Code

```
Tasks:
  [ ] Load generated patterns from analyzer
  [ ] Auto-select relevant context (smart algorithm)
  [ ] Build context injection prompts
  [ ] Format for Claude Code consumption
  [ ] Handle token limits (truncate if needed)
  [ ] Test with sample tasks
```

**Artifacts**:
- `skills/harness-context-loader/scripts/loader.py`
- `skills/harness-context-loader/templates/injection-prompt.jinja2`

---

### Phase 4: Orchestrator Skill (Main Loop)
**Priority**: 🔴 CRITICAL — Core workflow

```
Tasks:
  [ ] Implement requirement decomposition
  [ ] Build task dependency graph
  [ ] Implement serial execution
  [ ] Implement parallel execution (with limits)
  [ ] Integrate each phase: think → create → verify → test
  [ ] Add error handling & retry logic
  [ ] Generate execution journal
  [ ] State tracking for recovery
  [ ] Delegate to Claude Code properly
```

**Artifacts**:
- `skills/harness-code-orchestrator/scripts/orchestrator.py`
- `skills/harness-code-orchestrator/templates/decompose-prompt.jinja2`

---

### Phase 5: Verifier Skill
**Priority**: 🟡 MEDIUM — Quality assurance

```
Tasks:
  [ ] Implement ESLint runner
  [ ] Implement TypeScript type-check
  [ ] Implement Jest test runner
  [ ] Implement coverage checker
  [ ] Implement style check (Prettier)
  [ ] Implement pattern validation
  [ ] Add error explanation for Claude
  [ ] Test with generated code
```

**Artifacts**:
- `skills/harness-verifier/scripts/verifier.py`
- `skills/harness-verifier/config/eslint-rules.json`
- `skills/harness-verifier/scripts/checkers/*.py`

---

## 🧪 Testing & Examples

After Phase 1-5:
- [ ] Create example React app with `.harness/` integration
- [ ] Create example Node.js backend
- [ ] Write integration tests (pytest)
- [ ] Document expected vs actual outputs

---

## 🚀 Deployment & Sharing

After features are working:
- [ ] Create GitHub repo (public)
- [ ] Setup CI/CD (GitHub Actions)
- [ ] Create PyPI package
- [ ] NPM package (optional)
- [ ] Write installation guide
- [ ] Create tutorial video

---

## 📊 File Tree (Current State)

```
harness-claude-skills/
├── README.md                                           ✅
├── LICENSE                                             ✅
├── .gitignore                                          ✅
├── setup.py                                            ✅
├── package.json                                        ✅
├── .git/                                               ✅
│
├── skills/
│   ├── harness-codebase-analyzer/
│   │   ├── SKILL.md                                    ✅
│   │   ├── scripts/                                    📋
│   │   └── templates/mermaid-templates/                📋
│   │
│   ├── harness-context-loader/
│   │   ├── SKILL.md                                    ✅
│   │   ├── scripts/                                    📋
│   │   └── templates/                                  📋
│   │
│   ├── harness-code-orchestrator/
│   │   ├── SKILL.md                                    ✅
│   │   ├── scripts/                                    📋
│   │   └── templates/                                  📋
│   │
│   ├── harness-verifier/
│   │   ├── SKILL.md                                    ✅
│   │   ├── scripts/                                    📋
│   │   └── config/                                     📋
│   │
│   └── harness-readme-generator/
│       ├── SKILL.md                                    ✅
│       ├── scripts/                                    📋
│       └── templates/                                  📋
│
├── cli/
│   ├── commands/                                       📋
│   └── config/                                         📋
│
├── examples/
│   ├── react-app/.harness/                             📋
│   └── node-backend/.harness/                          📋
│
├── tests/
│   └── fixtures/sample-repos/                          📋
│
└── docs/
    ├── README.md                                       ✅
    ├── ARCHITECTURE.md                                 ✅
    ├── INSTALL.md                                      ✅
    ├── EXAMPLES.md                                     📋
    └── FAQ.md                                          📋

✅ = Done     📋 = Placeholder/TODO
```

---

## 🎯 Key Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| SKILL.md files | 5 | 5 ✅ | Complete |
| Documentation pages | 5+ | 3 ✅ | Complete |
| Published to registries | npm, PyPI | 0 ⏳ | Coming after Phase 1 |
| CLI commands | 6 | 0 📋 | Phase 1 |
| Local install method | ✅ | ✅ | Ready to use |
| Unit tests | 20+ | 0 📋 | Phase 2+ |
| Example projects | 2 | 0 📋 | Phase 2+ |

---

## 🔄 How to Use This Repo

### For Contributors
```bash
git clone https://github.com/chetandasauni25/harness-claude-skills.git
cd harness-claude-skills

# Check current status
cat PROJECT_STATUS.md

# Pick a phase (1-5) and contribute
# Example: Implement Phase 1 CLI
python setup.py --local
cd cli/commands
# Create analyze.py, orchestrate.py, etc.
```

### For Early Adopters
```bash
# Local install (after Phase 1-3 are done)
cd your-project
git clone https://github.com/chetandasauni25/harness-claude-skills.git .harness
cd .harness && python setup.py --local

# Try it
harness analyze ./src
```

---

## 📚 References

- **Harness.pdf** — Original reference document (used for architecture)
- **Hermes Agent** — Underlying skill system (hermes-agent.nousresearch.com)
- **Claude Code** — AI code generation tool being grounded
- **Mermaid** — Diagram format for architecture visualization

---

## 💬 Questions?

See [docs/FAQ.md](./docs/FAQ.md) or open an issue.

---

**Last Updated**: June 5, 2025  
**Next Review**: After Phase 1 completion
