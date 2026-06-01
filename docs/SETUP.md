# Setup Guide

Harness is a set of **Claude Code skills**. There's nothing to compile or install with a package manager and no external program to run — you just make the four `harness-*` skill folders discoverable, then ask Claude to analyze your project. Claude *is* the runtime.

## Prerequisites

- Claude Code installed and working
- Git

---

## Option A — Per-project install

### 1. Clone this repo

```bash
git clone https://github.com/chetan25/harness-claude-skills.git
```

### 2. Copy the skills into your project

```bash
mkdir -p your-project/.claude/skills
cp -r harness-claude-skills/skills/harness-* your-project/.claude/skills/
```

Your project now has the four core skills:

```
your-project/
└── .claude/
    └── skills/
        ├── harness-analyzer/SKILL.md
        ├── harness-context-loader/SKILL.md
        ├── harness-orchestrator/SKILL.md
        └── harness-verifier/SKILL.md
```

Project-local skills are auto-discovered by Claude Code in that project.

---

## Install as a plugin

To make the harness skills available in **every** repo (this is what fixes "they don't show up in my other project"), install them as a Claude Code plugin instead of copying per project. The four `harness-*` skills then load on every session, in any repo.

This repo is already a plugin: `.claude-plugin/plugin.json` (the manifest) plus `.claude-plugin/marketplace.json` (a single-plugin marketplace named `harness-marketplace`). The `skills/` directory at the repo root is what the plugin ships.

### Test it from a local clone (no publishing needed)

You already have this repo cloned. In **any other local repo** you want to try it in, open Claude Code and run:

```
/plugin marketplace add D:/Programming/harness-claude-skills
/plugin install harness@harness-marketplace
```

- The first command registers this local folder as a marketplace (it reads `.claude-plugin/marketplace.json`).
- The second installs the `harness` plugin from it. (You can also run `/plugin`, pick **harness-marketplace → harness → Install**.)

Then **start a new Claude Code session** in that repo and confirm the four skills are loaded — ask "list available skills" or just say "use harness-analyzer". Now run:

```
"Analyze this project."
```

The analyzer generates the `project-*` grounding skills into **that** repo's `.claude/skills/` and wires its `CLAUDE.md`. From then on, feature requests there follow the harness flow.

After you edit the plugin's skills here, run `/plugin marketplace update harness-marketplace` (or reinstall) and restart the session to pick up changes.

### Publish for others

Push this repo to GitHub and others install with:

```
/plugin marketplace add chetan25/harness-claude-skills
/plugin install harness@harness-marketplace
```

(See the `plugin-dev:plugin-structure` guidance for marketplace details.)

The generated `project-*` grounding skills are always written per project (under that project's `.claude/skills/`) when you analyze it — the plugin only carries the four reusable core skills.

---

## First run — analyze the project

In Claude Code, say:

```
"Analyze this project."
```

`harness-analyzer` will:

1. Detect the stack from real manifests (`package.json`, `pyproject.toml`, `go.mod`, …)
2. Map the architecture as standalone Mermaid diagram files under `diagrams/` (and write the `project-index.md` relevance map)
3. Extract naming / import / structure patterns from real files
4. Capture the test conventions
5. Capture design tokens (UI projects only)

Then it **generates grounding skills** under `.claude/skills/` and **wires `CLAUDE.md`**:

```
your-project/
├── CLAUDE.md                                     ← wired so feature requests follow the flow
└── .claude/
    ├── harness/
    │   └── state.md                              ← orchestrator run state (resumable)
    └── skills/
        ├── project-index.md                      ← relevance map (area → skills/diagrams)
        ├── project-patterns-{lang}/ { SKILL.md, diagrams/ (layers.mmd, idiom-*.mmd) }
        ├── project-architecture/   { SKILL.md, diagrams/ (components.mmd, data-flow.mmd) }
        ├── project-test-patterns/SKILL.md
        └── project-design-tokens/SKILL.md        (UI projects only)
```

Each generated `SKILL.md` is a **real skill** with `name` + `description` frontmatter, so Claude auto-loads it; the `project-*` skills reference their diagrams by path instead of embedding Mermaid. They're normal project files — **commit them** so your whole team shares the same grounding. The diagram files (`.mmd`) and `project-index.md` are committable too. (They are not gitignored.) `.claude/harness/state.md` is transient run state — you don't need to commit it.

The `CLAUDE.md` the analyzer writes summarizes the project, lists the generated `project-*` skills, and instructs that any non-trivial feature request runs through `harness-orchestrator`. So after analysis, your **next prompt is governed automatically** — no need to say "use the harness."

---

## Using it

Ask for features naturally:

```
"Add user authentication with email/password and JWT."
```

`CLAUDE.md` routes it through `harness-orchestrator`, which runs the loop: decompose → (per task) ground → plan → build → verify → test, tracked with `TodoWrite`. Each loop, `harness-context-loader` assembles a compact per-loop **context packet** — a user-ask summary + done-so-far + the current task + only the needed skills/diagrams (selected via `project-index.md`) + acceptance criteria. `harness-verifier` runs your project's *own* scripts — it discovers them from `package.json` scripts / `pyproject.toml` / `Makefile` rather than assuming commands — and also checks the change respects the diagrams it was grounded on (`layers.mmd`, `data-flow.mmd`).

The orchestrator tracks progress in `.claude/harness/state.md`, which makes longer builds resumable across restarts.

---

## Refreshing grounding

Re-run the analyzer when the project changes shape:

```
"Re-analyze this project — the architecture changed."
```

It regenerates the `project-*` skills under `.claude/skills/` and updates `CLAUDE.md` to match. Commit the refreshed skills so the team stays in sync.

---

## Optional — design context via MCP

Harness ships no MCP config of its own. To give Claude Figma/design context, add an MCP server the standard Claude Code way — a project `.mcp.json` (see `plugin-dev:mcp-integration`). With a Figma MCP connected, the verifier can compare generated UI against the design as one of its checks.

---

## Troubleshooting

**Skills don't trigger**
- Confirm `.claude/skills/harness-*/SKILL.md` exist in the project (Option A) or that the plugin is installed (Install as a plugin).
- If feature requests aren't following the flow, make sure you ran "Analyze this project" — the generated `project-*` skills and the wired `CLAUDE.md` are what route later prompts. You can also invoke a skill explicitly, e.g. "use the harness-analyzer skill."

**Generated code doesn't match style (stale grounding)**
- The `project-*` skills may be out of date after a refactor. Say "re-analyze this project" to regenerate them, or edit the relevant `.claude/skills/project-patterns-*/SKILL.md` by hand.

**Verifier reports a gate as "not configured"**
- That gate has no script in your project. `harness-verifier` only runs commands the project actually defines — it won't invent one. Add a `lint` / `typecheck` / `test` script (or the equivalent in `pyproject.toml` / `Makefile`) and re-run; the verifier will pick it up.

---

## Next steps

- [QUICKSTART.md](QUICKSTART.md) — the fastest path end to end
- [CONSUMPTION.md](CONSUMPTION.md) — day-to-day usage and FAQ
- [ARCHITECTURE.md](ARCHITECTURE.md) — how the four skills fit together
