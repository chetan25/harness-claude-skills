# Quick Setup for Laptop Users

If you cloned `.harness` on your **laptop** (not in a container), follow these steps.

## Step 1: How Did You Clone It?

**Option A: Clone as `.harness` (Recommended)**

```bash
git clone https://github.com/chetan25/harness-claude-skills.git .harness
```

Creates: `~/D/.harness/cli/`

**Option B: Clone with Repo Name**

```bash
git clone https://github.com/chetan25/harness-claude-skills.git
```

Creates: `~/D/harness-claude-skills/cli/`

---

## Step 2: Verify Files

Based on your clone method:

**If you did Option A (`.harness`):**
```bash
ls -la ~/D/.harness/cli/
```

**If you did Option B (`harness-claude-skills`):**
```bash
ls -la ~/D/harness-claude-skills/cli/
```

Look for:
- `harness` ✅
- `harness-cli.py` ✅

**If you DON'T see them:** Skip to Step 3

## Step 3: Update Your Clone

```bash
# If you have .harness:
cd ~/D/.harness && git pull origin main && cd ..

# If you have harness-claude-skills:
cd ~/D/harness-claude-skills && git pull origin main && cd ..
```

## Step 4: Add to PATH

**Important:** Use the correct path for YOUR clone!

**If you have `.harness`:**
```bash
export PATH="~/D/.harness/cli:$PATH"
```

**If you have `harness-claude-skills`:**
```bash
export PATH="~/D/harness-claude-skills/cli:$PATH"
```

**To make it permanent:**

**For macOS/Linux with bash:**
```bash
# If .harness:
echo 'export PATH="~/D/.harness/cli:$PATH"' >> ~/.bashrc

# If harness-claude-skills:
echo 'export PATH="~/D/harness-claude-skills/cli:$PATH"' >> ~/.bashrc

source ~/.bashrc
```

**For macOS/Linux with zsh:**
```bash
# If .harness:
echo 'export PATH="~/D/.harness/cli:$PATH"' >> ~/.zshrc

# If harness-claude-skills:
echo 'export PATH="~/D/harness-claude-skills/cli:$PATH"' >> ~/.zshrc

source ~/.zshrc
```

## Step 4: Test

```bash
harness --help
```

Should show:
```
usage: harness [-h]
               {analyze,context,orchestrate,think,verify,test,status,journal,config}
```

If you see this, ✅ **You're all set!**

## Now Use It

```bash
# In your project folder
cd ~/D
harness analyze ./src
harness context "Add dark mode"
```

## Troubleshooting

**"harness: command not found"**
- Check: `ls -la ~/D/.harness/cli/harness` 
- If missing: Run `cd ~/D/.harness && git pull`
- Check PATH: `echo $PATH`

**"Permission denied"**
```bash
chmod +x ~/D/.harness/cli/harness
chmod +x ~/D/.harness/cli/harness-cli.py
```

**Still not working?**
Use the full path:
```bash
python3 ~/D/.harness/cli/harness-cli.py --help
```

Or create an alias:
```bash
alias harness='python3 ~/D/.harness/cli/harness-cli.py'
harness --help
```
