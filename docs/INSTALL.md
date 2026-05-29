# Installation Guide

Choose your installation method based on your workflow.

## Option 1: Local Installation (Recommended for Getting Started)

Install Harness directly into your project folder. Great for teams, testing, and keeping configs close to the codebase.

### Steps

```bash
cd your-project
git clone https://github.com/chetandasauni25/harness-claude-skills.git .harness
cd .harness
python setup.py --local
```

### What Gets Created

```
your-project/
├── .harness/
│   ├── config/
│   │   └── default.yaml
│   ├── generated/          (auto-generated skills & diagrams)
│   └── journal.md          (execution log)
├── .harness-config.yaml    (gitignored, project-specific)
└── ...
```

### Usage

From your project root:

```bash
harness analyze ./src
harness orchestrate "Add login page"
```

### Benefits
✅ Project-specific configuration  
✅ Easy to share with teammates (commit `.harness/`)  
✅ No global state pollution  
✅ Easy to try without permanent install  

---

## Option 2: Global Installation (For Power Users)

Install Harness system-wide. Works across multiple projects.

### Steps

```bash
# Install via pip
pip install harness-claude-skills

# Or from source
git clone https://github.com/chetandasauni25/harness-claude-skills.git
cd harness-claude-skills
pip install -e .

# Setup global config
harness init my-project
```

### What Gets Created

```
~/.harness/
├── config.yaml             (global settings)
├── cache/                  (analysis cache)
└── ...

my-project/
├── .harness-config.yaml    (project overrides)
└── ...

~/.hermes/skills/harness-*/ (installed skills)
```

### Usage

From any directory:

```bash
harness analyze ./src
harness orchestrate "Add login page"
```

### Benefits
✅ Works across projects  
✅ Shared cache & config  
✅ One install, use everywhere  
✅ CLI available globally  

---

## Hermes Integration

Harness uses Hermes skills. Make sure Hermes Agent is installed:

```bash
hermes --version
```

If not installed:
```bash
pip install hermes-agent
hermes setup
```

---

## First Run Checklist

After installation:

- [ ] Run `harness --version` (should show version)
- [ ] Run `harness analyze ./src` (should generate context files)
- [ ] Check `.harness/generated/` (should have pattern files)
- [ ] Try `harness orchestrate "small task"` (should work)

---

## Troubleshooting

### "harness: command not found"

**Local install**: Use `python cli/harness-cli.py` or add to PATH:
```bash
export PATH="$PATH:$(pwd)/.harness/cli"
```

**Global install**: Reinstall:
```bash
pip install --upgrade harness-claude-skills
```

### "No such file or directory: .harness/config"

Run `python setup.py --local` from project root.

### "Hermes skill not found"

Make sure Hermes is installed and configured:
```bash
hermes config show
hermes tools list harness-*
```

---

## Next Steps

- Read [../README.md](../README.md) for quick start
- Check [EXAMPLES.md](./EXAMPLES.md) for real use cases
- See [ARCHITECTURE.md](./ARCHITECTURE.md) for deep dive
