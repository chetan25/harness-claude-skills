# Using Harness Claude Skills

Harness is **four Claude Code skills** — `harness-analyzer`, `harness-context-loader`, `harness-orchestrator`, `harness-verifier`. There's no CLI and no separate program. Claude reads the `SKILL.md` files and acts. **Claude is the runtime.**

## The flow

```
Copy the harness-* skills into your project's .claude/skills/   (or install the plugin)
        ↓
Open the project in Claude Code
        ↓
"Analyze this project"
   → harness-analyzer GENERATES project-* grounding skills under .claude/skills/
   → and wires CLAUDE.md so future requests follow the harness flow
        ↓
"Add a feature."                 ← just ask normally; no "use the harness" needed
        ↓
CLAUDE.md + the generated skills route it through harness-orchestrator:
  1. Decompose the feature into ordered tasks
  2. Ground each task with a per-loop context packet   (harness-context-loader)
       → pulls only the grounding skills + diagrams the task actually needs (selective)
  3. Plan the approach against that packet
  4. Build it following your real patterns
  5. Verify with your project's own lint / type / format / test commands   (harness-verifier)
  6. Add tests and iterate until green
```

The first prompt sets up grounding. After that, the wired `CLAUDE.md` and the auto-loaded `project-*` skills mean **your next feature request just follows the flow** — you don't have to invoke anything by name.

---

## What you don't have to do

❌ Learn or run any CLI (there is no `harness` command and no slash command)
❌ Install a Python or JS package or runtime
❌ Maintain a harness config by hand — the orchestrator keeps a small auto-managed run-state file (`.claude/harness/state.md`) for you; there's no config to edit
❌ Say "use the harness" — once analyzed, `CLAUDE.md` routes feature requests for you

## What you get

✅ **Grounded generation** — code matches *your* project, not generic defaults
✅ **Self-governing** — generated `project-*` skills auto-load; `CLAUDE.md` routes requests
✅ **Real verification** — the verifier runs your actual scripts and shows the output
✅ **Decomposition** — large features broken into independently verifiable tasks
✅ **Honest iteration** — it loops on real failures and reports what's still red

---

## Example: "Add dark mode"

After analysis, you say:

```
"Add dark mode with persistence to localStorage."
```

`CLAUDE.md` routes it through `harness-orchestrator`:

```
1. DECOMPOSE
   ├─ theme context + provider
   ├─ theme toggle
   ├─ apply dark styles
   ├─ persist to localStorage
   └─ tests for each

2. GROUND  (per task, via harness-context-loader)
   ├─ reads .claude/harness/state.md      (user-ask summary + done-so-far + current task)
   ├─ reads project-index.md              (which skills/diagrams this task needs)
   ├─ pulls only the relevant grounding   (e.g. project-design-tokens + diagrams/idiom-*.mmd for UI work)
   └─ emits a compact per-loop context packet + acceptance-criteria checklist

3. BUILD
   ├─ ThemeContext following your patterns
   ├─ ThemeToggle using your design tokens
   └─ wires it into the app

4. VERIFY  (harness-verifier)
   ├─ runs your lint script
   ├─ runs your type-check
   ├─ runs your tests
   ├─ checks naming / imports / file location against project-patterns-*
   └─ checks the change respects the grounding diagrams (a `diagrams` gate)

5. DONE
   └─ green gates + tests passing, reported with real command output
```

Every "passing" claim is backed by command output you can see.

---

## Behind the scenes

### `project-*` are generated *skills* that auto-load

`harness-analyzer` writes real `SKILL.md` files into `.claude/skills/`, each with `name` + `description` frontmatter:

- `project-patterns-{lang}/SKILL.md` — naming, imports, file organization; references standalone diagrams in `project-patterns-{lang}/diagrams/` (`layers.mmd`, plus zero-or-more `idiom-*.mmd`)
- `project-architecture/SKILL.md` — module map; references standalone diagrams in `project-architecture/diagrams/` (`components.mmd`, `data-flow.mmd`)
- `project-test-patterns/SKILL.md` — runner + test shape
- `project-design-tokens/SKILL.md` — colors, spacing, typography (UI only)
- `project-index.md` — a relevance map (area → which skills + diagrams to load for a task) that powers selective per-loop loading

The analyzer writes Mermaid diagrams as standalone `.mmd` files under each grounding skill's `diagrams/` folder, and the `project-*` skills reference them by path rather than embedding the diagram inline.

Because they're proper skills, Claude **auto-loads them by description** in this project from then on. The analyzer also creates or updates the project's root `CLAUDE.md` so feature requests automatically route through `harness-orchestrator`.

`harness-context-loader` reads `.claude/harness/state.md` + `project-index.md`, selects only the grounding skills + diagrams relevant to the current task, and emits a compact ephemeral packet — short user-ask summary, done-so-far, current task, exact context to use, and acceptance criteria — which is exactly what the verifier checks the result against.

**Precise per-loop context.** The loader rebuilds that packet fresh on every loop (user-ask summary + done-so-far + current task + only the needed skills/diagrams via `project-index.md`), so context stays tight instead of dragging in everything. Because the orchestrator keeps its progress in `.claude/harness/state.md`, a long build is **resumable** across compaction and restarts.

These are **normal committable project files** — commit them so your team shares the same grounding. (They are *not* gitignored.) The orchestrator keeps resumable run state in `.claude/harness/state.md`.

### The verifier uses *your* commands

It reads `package.json` scripts, `pyproject.toml`, `Makefile`, or CI config to find the real `lint` / `typecheck` / `format` / `test` commands and runs those. If a gate isn't configured in your project, it reports it as "not configured" instead of inventing one. It also adds a `diagrams` gate — confirming the change respects the diagrams it was grounded on (layering in `layers.mmd`, the canonical `data-flow.mmd`).

### MCP is optional and standard

To add design context, connect a Figma (or other) MCP server the normal Claude Code way via a project `.mcp.json`. The harness ships no MCP config of its own. With a Figma MCP connected, the verifier can compare generated UI against the design.

---

## FAQ

**Q: Do I need to learn new commands?**
A: No. Ask Claude naturally. There's no CLI and no slash command. Once you've analyzed the project, `CLAUDE.md` routes feature requests for you.

**Q: Is there a Python tool or CLI to install?**
A: No. Harness is four `SKILL.md` files. Claude is the runtime — nothing to `pip install` or execute.

**Q: What if I have a legacy codebase?**
A: Run "analyze this project" — the analyzer learns the patterns that actually exist and writes grounding skills from real code.

**Q: Do I have to say "use the harness" every time?**
A: No. The analyzer wires `CLAUDE.md`, so a normal feature request routes through the flow. (It's a soft, idiomatic instruction in `CLAUDE.md`, not a hard hook — you can always invoke a skill by name if you want.)

**Q: Non-React projects?**
A: Supported. The skills detect the stack from real manifests (`package.json`, `pyproject.toml`, `go.mod`, …) and use the project's own scripts. `project-design-tokens` is generated only for UI projects.

**Q: How do I refresh after a refactor?**
A: "Re-analyze this project" — the analyzer regenerates the `project-*` skills and merges `CLAUDE.md`.

**Q: Can I resume a long build if it gets interrupted?**
A: Yes. The orchestrator tracks the user ask, the task list with status, and a done-so-far log in `.claude/harness/state.md`, so it can pick up where it left off after a compaction or restart.

**Q: How do I get the skills in all my repos?**
A: Install them as a plugin instead of copying per project (see [SETUP.md](SETUP.md#install-as-a-plugin)). Then they auto-load everywhere.

---

## Troubleshooting

**Claude doesn't trigger the skills**
- Confirm `.claude/skills/harness-*/SKILL.md` exist (or the plugin is installed).
- Invoke one explicitly by name (e.g. "use harness-analyzer").

**Generated code doesn't match your style**
- Grounding is likely stale — "re-analyze this project", or edit the relevant `.claude/skills/project-patterns-*/SKILL.md` directly.

**Feature requests aren't following the flow**
- Make sure the analyzer ran and `CLAUDE.md` exists at the project root with the harness routing. Re-run "analyze this project" if it's missing.

**Tests fail after generation**
- The orchestrator loops on real failures. If it stays red, it switches to deliberate debugging and surfaces the blocker rather than forcing a broken result.

---

## Next steps

- [QUICKSTART.md](QUICKSTART.md) — fastest path
- [SETUP.md](SETUP.md) — per-project and plugin install
- [ARCHITECTURE.md](ARCHITECTURE.md) — how the four skills fit together
