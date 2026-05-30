#!/bin/bash
# Quick setup script for Harness Claude Skills

set -e

PROJECT_ROOT="$(pwd)"
HARNESS_DIR="$PROJECT_ROOT/.harness"

echo "🚀 Harness Claude Skills Setup"
echo ""

# Check if .harness exists
if [ ! -d "$HARNESS_DIR" ]; then
    echo "❌ Error: .harness directory not found"
    echo "   Please run this from your project root where .harness/ exists"
    exit 1
fi

echo "✅ Found .harness at: $HARNESS_DIR"
echo ""

# Check for CLI
if [ ! -f "$HARNESS_DIR/cli/harness" ]; then
    echo "⚠️  CLI not found. Updating..."
    cd "$HARNESS_DIR"
    git pull origin main 2>/dev/null || echo "Could not auto-update. Run 'git pull' manually."
    cd "$PROJECT_ROOT"
fi

# Make scripts executable
chmod +x "$HARNESS_DIR/cli/harness" 2>/dev/null || true
chmod +x "$HARNESS_DIR/cli/harness-cli.py" 2>/dev/null || true

echo ""
echo "✅ Setup Complete!"
echo ""
echo "🎯 Next steps:"
echo ""
echo "1. Add to PATH (temporary):"
echo "   export PATH=\"$HARNESS_DIR/cli:\$PATH\""
echo ""
echo "2. Or add to ~/.bashrc or ~/.zshrc (permanent):"
echo "   echo 'export PATH=\"$HARNESS_DIR/cli:\$PATH\"' >> ~/.bashrc"
echo ""
echo "3. Test:"
echo "   harness --help"
echo ""
echo "4. Analyze your project:"
echo "   harness analyze ./src"
echo ""
