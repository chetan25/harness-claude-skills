# Installation Guide

Choose your installation method based on your workflow.

## Option 1: Local Installation (Recommended for Now)

Install Harness directly into your project folder. This is the primary method until global packages are published.

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
│   ├── generated/          (auto-generated context & diagrams)
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

## Option 2: Global Installation (Coming Soon)

**Status**: Not yet published to npm or PyPI. Will add once CLI is complete.

We're building the CLI tool first (Phase 1). Once complete, we'll publish:
- PyPI package: `pip install harness-claude-skills`
- NPM package: `npm install -g harness-claude-skills`

---

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

---

## Next Steps

- Read [../README.md](../README.md) for quick start
- Check [EXAMPLES.md](./EXAMPLES.md) for real use cases
- See [ARCHITECTURE.md](./ARCHITECTURE.md) for deep dive
