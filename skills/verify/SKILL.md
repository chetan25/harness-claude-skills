**Verification is runtime observation.** You build the app, run it,
drive it to where the changed code executes, and capture what you
see. That capture is your evidence. Nothing else is.

**Don't run tests. Don't typecheck.** Running them here proves you
can run CI — not that the change works. Not as a warm-up,
not "just to be sure," not as a regression sweep after. The time
goes to running the app instead.

**Don't import-and-call.** `import { foo } from './src/...'` then
`console.log(foo(x))` is a unit test you wrote. The function did what
the function does — you knew that from reading it. The app never ran.
Whatever calls `foo` in the real codebase ends at a CLI, a socket, or
a window. Go there.

## Find the change

The scope is what you're verifying — usually a diff, sometimes just
"does X work." In a git repo, establish the full range (a branch may
be many commits, or the change may still be uncommitted):

```bash
git log --oneline @{u}..              # count commits (if upstream set)
git diff @{u}.. --stat                # full range, not HEAD~1
git diff origin/HEAD... --stat        # no upstream: committed vs base
git diff HEAD --stat                  # uncommitted: working tree vs HEAD
gh pr diff                            # if in a PR context
```

State the commit count. Large diff truncating? Redirect to a file
then Read it. Repo but no diff from any of these → say so, stop.
**No repo → the scope is whatever the user named; ask if they
didn't.**

**The diff is ground truth. Any description is a claim about it.**
Read both. If they disagree, that's a finding.

## Surface

The surface is where a user — human or programmatic — meets the
change. That's where you observe.

| Change reaches | Surface | You |
|---|---|---|
| CLI / TUI | terminal | type the command, capture the pane |
| Server / API | socket | send the request, capture the response |
| GUI / UI | browser pixels | **use Chrome DevTools MCP** — navigate, snapshot, interact, screenshot |
| Library | package boundary | sample code through the public export — `import pkg`, not `import ./src/...` |
| Prompt / agent config | the agent | run the agent, capture its behavior |
| CI workflow | Actions | dispatch it, read the run |

**For any GUI or UI change, Chrome DevTools MCP is the mandatory
tool.** Do not screenshot manually, do not describe what "should"
appear — navigate to the page, interact with it via the MCP tools,
and capture screenshot evidence.

**Internal function? Not a surface.** Something in the repo calls it
and that caller ends at one of the rows above. Follow it there.

**No runtime surface at all** — docs-only, type declarations with no
emit, build config that produces no behavioral diff — report
**SKIP — no runtime surface: (reason).** Don't run tests to fill
the space.

**Tests in the diff are the author's evidence, not a surface.** CI
runs them. Tests-only PR → SKIP, one line. Mixed src+tests → verify
the src, ignore the test files.

## Get a handle

**Check `.claude/skills/` first — even if you already know how to
build and run.** A matching `verifier-*` skill is the repo's
evidence-capture protocol.

```bash
ls .claude/skills/
```

- **`verifier-*` matching your surface** → invoke it with the Skill
  tool and follow its setup.
- **`run-*` but no matching verifier** → use its build/launch
  primitives as your handle.
- **Neither** → cold start from README/package.json/Makefile.
  Timebox ~15min. Stuck → BLOCKED with exactly where.

## UI Verification with Chrome DevTools MCP

**Required for all GUI/browser/frontend changes.** This is not
optional — screenshots from the live running app are the evidence.

### Standard workflow

```
1. Start the dev server (npm run dev / next dev / vite / etc.)
2. navigate_page → the URL where the change appears
3. wait_for → a selector or condition confirming the page loaded
4. take_snapshot → get page structure and element UIDs
5. Interact using UIDs (click, fill, hover, press_key)
6. take_screenshot → capture what the user sees
```

### Tool reference

| Goal | Tool |
|---|---|
| Open a URL | `navigate_page` |
| Open a new tab | `new_page` |
| Get page structure + UIDs | `take_snapshot` |
| Visual evidence | `take_screenshot` |
| Click an element | `click` (use UID from snapshot) |
| Type into a field | `fill` or `type_text` |
| Fill multiple fields | `fill_form` |
| Hover | `hover` |
| Keyboard input | `press_key` |
| Wait for element/state | `wait_for` |
| Run JS | `evaluate_script` |
| Check console errors | `list_console_messages` |
| Check network calls | `list_network_requests` |
| Responsive/mobile | `resize_page` or `emulate` |
| Performance | `lighthouse_audit` |
| Manage tabs | `list_pages`, `select_page`, `close_page` |

### What to capture

For every UI change, take at minimum:

1. **Before state** screenshot (if testing a change from a known state)
2. **After interaction** screenshot showing the feature working
3. **Console messages** — any errors or warnings from `list_console_messages`
4. **Probe state** — at least one edge case screenshot (empty state,
   error state, mobile viewport, etc.)

### UI probes

After confirming the happy path:

- **Responsive**: `resize_page` to 375px wide — does layout hold?
- **Empty state**: trigger the zero-content case — what does the user see?
- **Error state**: trigger validation or network error — is messaging clear?
- **Keyboard nav**: `press_key` Tab through interactive elements
- **Console clean**: `list_console_messages` — any unexpected errors?
- **Network**: `list_network_requests` — are API calls correct?

Pick the probes the change points at, not all of them.

## Drive it

Smallest path that makes the changed code execute:

- Changed a component? Navigate to the page that renders it.
- Changed a form? Fill and submit it.
- Changed error handling? Trigger the error state.
- Changed a route/handler? Navigate to that route.
- Changed an internal function? Find the UI surface that calls it.

**Read your plan back before running.** If every step is build /
typecheck / run test file — you've planned a CI rerun, not a
verification.

**End-to-end, through the real interface.** For UI: click buttons,
not curl the API underneath. The seam between frontend and backend
is where bugs hide.

**Destructive path?** If the change touches code that deletes,
publishes, sends, or writes outside the workspace and there's no
dry-run or safe target, verify what you can around it and note
which path you didn't exercise and why.

## Capture

For CLI/API: stdout, response bodies, pane captures.
For GUI: screenshots from `take_screenshot`, console output from
`list_console_messages`. Captured output is evidence; your memory
isn't.

Something unexpected? Don't route around it — capture, note, decide
if it's the change or the environment.

## Report

Inline, final message:

```
## Verification: <one-line what changed>

**Verdict:** PASS | FAIL | BLOCKED | SKIP

**Claim:** <what it's supposed to do — your read of the diff and/or
the stated claim; note any mismatch>

**Method:** <how you got a handle — which verifier/run-skill, or
cold start; what you launched; which MCP tools used for UI>

### Steps

Each step is one thing you did to the **running app** and what it
showed. Build/install/checkout are setup, not steps.

1. ✅/❌/⚠️/🔍 <what you did to the running app> → <what you observed>
   <evidence: screenshot path, console output, response body>

🔍 marks a probe — a step off the claim's happy path. At least one.

**Screenshot:** <screenshot path from take_screenshot — required for
all UI/GUI changes>

### Findings
<Things you noticed. Not just bugs — friction, surprises, console
errors, layout issues, anything a first-time user would trip on.
Each probe gets a line even when it held.

Lead with ⚠️ for lines worth interrupting the reviewer for.>
```

**Verdicts:**
- **PASS** — you ran the app, the change did what it should at its
  surface. For UI: you have screenshots proving it.
- **FAIL** — you ran it and it doesn't. Or it breaks something else.
  Or claim and diff disagree materially.
- **BLOCKED** — couldn't reach a state where the change is observable.
  Say exactly where it stopped.
- **SKIP** — no runtime surface exists. Docs-only, types-only,
  tests-only. One line why.

No partial pass. "3 of 4 passed" is FAIL until 4 passes or is
explained away.

**When in doubt, FAIL.** False PASS ships broken code; false FAIL
costs one more human look.
