# Windows Setup Guide (Git Bash / MINGW64)

If you're on Windows using **Git Bash** or **MINGW64**, follow these steps.

## The Problem

The bash wrapper script (`harness`) doesn't work on Windows. You need to use Python directly.

## Solution 1: Use Python Directly (Quick)

```bash
python3 /d/Programming/harness-claude-skills/cli/harness-cli.py --help
python3 /d/Programming/harness-claude-skills/cli/harness-cli.py analyze ./src
```

## Solution 2: Create an Alias (Recommended)

### Step 1: Open Git Bash Config

```bash
# Open your Git Bash profile
nano ~/.bashrc
```

### Step 2: Add This Line

At the end of the file, add:

```bash
# Harness Claude Skills
alias harness='python3 /d/Programming/harness-claude-skills/cli/harness-cli.py'
```

**Save:** Ctrl+O → Enter → Ctrl+X

### Step 3: Reload This Session

```bash
source ~/.bashrc
```

### Step 4: Test in a NEW Git Bash Window

Close Git Bash completely, then open a fresh window and try:

```bash
harness --help
```

If it works, the alias is now persistent! ✅

### Step 5: Verify It's Permanent

In any Git Bash window (now or later), check:

```bash
cat ~/.bashrc | grep harness
```

Should show your alias line.

## Understanding Persistence

**One-Time Alias (This Session Only):**

```bash
alias harness='python3 /d/Programming/harness-claude-skills/cli/harness-cli.py'
```

This works **only in this Git Bash window**. If you close it or open a new one, the alias disappears.

**Permanent Alias (All Sessions):**

Add the same line to `~/.bashrc`. Now it loads automatically every time you open Git Bash.

---

## File Locations on Windows

Your config files live in your **home directory**. Find it:

```bash
# Show home directory
echo $HOME

# List config files
ls -la ~/ | grep bash
```

Common locations:
- `C:\Users\YourUsername\.bashrc`
- `C:\Users\YourUsername\.bash_profile`
- Or use: `~/.bashrc` in Git Bash (it resolves automatically)

---

## Multiple Config Files?

Git Bash reads config files in this order:

1. `~/.bash_profile` (if exists)
2. `~/.bashrc` (if exists)

**Best practice:** Add your alias to `~/.bashrc` — it's loaded by both login and non-login shells.

---

If you want to use Command Prompt (cmd.exe) or PowerShell instead of Git Bash:

### Step 1: Create a Batch File

Create: `C:\Users\YourUsername\harness.bat`

```batch
@echo off
python3 "d:\Programming\harness-claude-skills\cli\harness-cli.py" %*
```

**Replace:**
- `YourUsername` with your Windows username
- `d:\Programming\` with your actual path

### Step 2: Add to Windows PATH

1. Open **Environment Variables** (search in Start menu)
2. Click "Edit environment variables for your account"
3. Edit `PATH`
4. Add: `C:\Users\YourUsername`
5. Click OK

### Step 3: Test in Command Prompt

```cmd
harness --help
harness analyze ./src
```

---

## Solution 4: PowerShell Profile (Alternative)

### Step 1: Open PowerShell Profile

```powershell
notepad $PROFILE
```

### Step 2: Add Function

```powershell
function harness {
    python3 "d:\Programming\harness-claude-skills\cli\harness-cli.py" @args
}
```

### Step 3: Reload

```powershell
. $PROFILE
```

### Step 4: Test

```powershell
harness --help
```

---

## Full Workflow on Windows

```bash
# 1. Navigate to your project
cd /d/Programming/your-project

# 2. Use harness (pick your method)
# Method A: Python directly
python3 /d/Programming/harness-claude-skills/cli/harness-cli.py analyze ./src

# Method B: With alias (after setup)
harness analyze ./src

# 3. Get context
harness context "Add dark mode"

# 4. Verify
harness verify ./src/features
```

---

## Troubleshooting

**"python3: command not found"**

Install Python from https://python.org or use:
```bash
python --version  # Use 'python' instead of 'python3'
alias harness='python /d/Programming/harness-claude-skills/cli/harness-cli.py'
```

**Alias not persisting?**

Make sure you edited the right config file:
```bash
# Check which files exist:
ls -la ~/ | grep bash
# Edit the one that exists:
nano ~/.bashrc    # Most common
# or
nano ~/.bash_profile
```

**Path issues?**

Use full absolute path, not tilde:
```bash
# Good:
/d/Programming/harness-claude-skills/cli/harness-cli.py

# May not work:
~/d/Programming/harness-claude-skills/cli/harness-cli.py
```

---

## Recommended: Solution 2 (Alias)

It's the easiest and most portable. Takes 2 minutes to set up once, then `harness` works everywhere! 🚀
