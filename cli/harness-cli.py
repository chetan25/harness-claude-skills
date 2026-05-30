#!/usr/bin/env python3
"""
Harness CLI - Temporary Placeholder
This will be replaced by Phase 1 implementation.
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        prog='harness',
        description='Claude Code Skills - Ground AI in your project patterns'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze = subparsers.add_parser('analyze', help='Scan project for patterns')
    analyze.add_argument('path', nargs='?', default='./src', help='Path to scan')
    analyze.add_argument('--output', help='Output directory')
    
    # Context command
    context = subparsers.add_parser('context', help='Get prompt injection for Claude Code')
    context.add_argument('description', help='Feature description')
    context.add_argument('--include', help='Comma-separated: patterns,api,design-tokens')
    
    # Orchestrate command
    orchestrate = subparsers.add_parser('orchestrate', help='Run full workflow')
    orchestrate.add_argument('description', help='Feature description')
    
    # Think command
    think = subparsers.add_parser('think', help='Decompose task only')
    think.add_argument('description', help='Feature description')
    
    # Verify command
    verify = subparsers.add_parser('verify', help='Lint, type-check, test')
    verify.add_argument('path', help='Path to verify')
    
    # Test command
    test = subparsers.add_parser('test', help='Run tests')
    test.add_argument('path', help='Test file or directory')
    
    # Status command
    status = subparsers.add_parser('status', help='Show project state')
    
    # Journal command
    journal = subparsers.add_parser('journal', help='View execution log')
    journal.add_argument('--last', type=int, help='Show last N entries')
    
    # Config command
    config = subparsers.add_parser('config', help='Manage configuration')
    config.add_argument('action', choices=['show', 'set'], help='Action')
    config.add_argument('key', nargs='?', help='Config key (for set)')
    config.add_argument('value', nargs='?', help='Config value (for set)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Phase 1 TODO: Implement these commands
    print(f"❌ Command '{args.command}' not yet implemented")
    print()
    print("📋 This is a placeholder for Phase 1 of Harness Claude Skills")
    print()
    print("✅ Phase 0: Documentation & skill definitions (DONE)")
    print("📋 Phase 1: CLI Tool Implementation (IN PROGRESS)")
    print("   - harness analyze ./src")
    print("   - harness context 'description'")
    print("   - harness orchestrate 'feature'")
    print("   - harness verify ./output")
    print("   - harness test ./output.test.ts")
    print()
    print("See docs/USAGE_GUIDE.md for the intended workflow")
    print("See PROJECT_STATUS.md for the roadmap")

if __name__ == '__main__':
    main()
