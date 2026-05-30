# Quick Setup for Laptop Users

If you cloned `.harness` on your **laptop** (not in a container), follow these steps.

## Step 1: Verify Files

Open Terminal and run:

```bash
ls -la ~/D/.harness/cli/
```

Look for:
- `harness` ✅
- `harness-cli.py` ✅

**If you see them:** Skip to Step 3  
**If you DON'T see them:** Do Step 2

## Step 2: Update Your Clone

```bash
cd ~/D/.harness
git pull origin main
cd ..
```

This downloads the latest CLI files from GitHub.

## Step 3: Add to PATH

**Temporary** (this session only):

```bash
export PATH="~/D/.harness/cli:$PATH"
```

**Permanent** (all future sessions):

**For macOS/Linux with bash:**
```bash
echo 'export PATH="~/D/.harness/cli:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**For macOS/Linux with zsh:**
```bash
echo 'export PATH="~/D/.harness/cli:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**For Windows (PowerShell):**
```powershell
# Add to Windows System Environment Variables or run:
$env:Path += ";C:\Users\YourName\D\.harness\cli"
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
