"""
Phase 1.3 - Claude Commands Integration: Usage Examples

This module demonstrates how to use the command system, auto-detection,
cache management, and command routing.
"""

import sys
sys.path.insert(0, '/tmp/harness-claude-skills/engine')

from pathlib import Path
import tempfile

from commands import CommandType, CommandArgs
from command_router import CommandParser, CommandRouter
from auto_detector import AutoDetector
from cache_manager import CacheManager


def example_1_basic_command_parsing():
    """Example: Parse various @harness commands."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Command Parsing")
    print("="*70)
    
    commands = [
        '@harness orchestrate "Add user authentication with email/password"',
        '@harness orchestrate "Build dark mode" --figma-url https://figma.com/design/123',
        '@harness orchestrate "Add feature" --cache refresh',
        '@harness analyze',
        '@harness context',
        '@harness verify ./src/components/Button',
        '@harness cache status',
        '@harness cache refresh',
        '@harness cache clear',
    ]
    
    parser = CommandParser()
    
    for cmd_str in commands:
        result = parser.parse(cmd_str)
        if result:
            print(f"\n✓ Parsed: {cmd_str}")
            print(f"  Command: {result.command.value}")
            if result.task:
                print(f"  Task: {result.task}")
            if result.figma_url:
                print(f"  Figma: {result.figma_url}")
            if result.path:
                print(f"  Path: {result.path}")
            if result.cache_action:
                print(f"  Cache Action: {result.cache_action}")
            if result.flags:
                print(f"  Flags: {result.flags}")
        else:
            print(f"\n✗ Failed to parse: {cmd_str}")


def example_2_command_execution():
    """Example: Execute commands and see formatted output."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Command Execution & Formatting")
    print("="*70)
    
    router = CommandRouter()
    
    test_commands = [
        '@harness orchestrate "Add dark mode toggle to settings"',
        '@harness analyze',
        '@harness cache status',
    ]
    
    for cmd_str in test_commands:
        print(f"\n>>> {cmd_str}")
        result = router.execute(cmd_str)
        output = router.format_output(cmd_str, result)
        print(output)


def example_3_auto_detection():
    """Example: Auto-detect .harness folder and first-run."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Auto-Detection & First-Run")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Initialize .harness structure
        harness_dir = tmpdir / ".harness"
        harness_dir.mkdir()
        (harness_dir / "skills").mkdir()
        (harness_dir / "generated").mkdir()
        
        # Create detector
        detector = AutoDetector(tmpdir)
        
        # Check status
        status = detector.get_status()
        print("\nInitial Status:")
        print(f"  Detected: {status['detected']}")
        print(f"  First-run: {status['is_first_run']}")
        print(f"  Message: {status['message']}")
        
        # List contents
        contents = detector.list_harness_contents()
        print(f"\n.harness contents:")
        print(f"  Subdirs: {contents['subdirs']}")
        
        # Verify structure
        is_valid, issues = detector.verify_structure()
        print(f"\nStructure valid: {is_valid}")
        if issues:
            for issue in issues:
                print(f"  ⚠ {issue}")
        
        # Mark as initialized
        detector.mark_initialized()
        status = detector.get_status()
        print(f"\nAfter initialization:")
        print(f"  First-run: {status['is_first_run']}")
        print(f"  Message: {status['message']}")


def example_4_cache_management():
    """Example: Cache operations and code change detection."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Cache Management")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        harness_dir = tmpdir / ".harness"
        harness_dir.mkdir()
        
        # Create source files
        (tmpdir / "app.py").write_text("print('hello')")
        (tmpdir / "config.ts").write_text("export const config = {}")
        
        cache_mgr = CacheManager(tmpdir)
        
        # Initial state
        print("\n1. Initial Cache State:")
        status = cache_mgr.get_cache_status()
        print(f"   Status: {status['status']}")
        print(f"   Message: {status['message']}")
        
        # Compute code hash
        print("\n2. Computing Code Hash:")
        hash1 = cache_mgr.get_code_hash()
        print(f"   Hash: {hash1[:16]}...")
        
        # Save analysis
        print("\n3. Saving Analysis Data:")
        data = {
            "patterns": {"framework": "React", "language": "TypeScript"},
            "architecture": "# Component Architecture\n- Header\n- Main\n- Footer",
            "diagrams": "graph TD; A-->B; B-->C",
            "design_tokens": {"primary": "#3B82F6", "secondary": "#6B7280"},
            "skills_summary": "# Detected Skills\n- React Hooks\n- TypeScript\n- Jest Testing",
        }
        cache_mgr.save_analysis_data(data)
        
        # Check files
        print("   Files created:")
        for fname in ["patterns.json", "architecture.md", "diagrams.mermaid", 
                      "design-tokens.json", "skills-summary.md", "cache.json"]:
            exists = (cache_mgr.cache_dir / fname).exists()
            print(f"   ✓ {fname}" if exists else f"   ✗ {fname}")
        
        # Check validity
        print("\n4. Cache Validity:")
        print(f"   Valid: {cache_mgr.is_cache_valid()}")
        print(f"   Code changed: {cache_mgr.has_code_changed()}")
        
        # Modify code
        print("\n5. Modifying Code:")
        (tmpdir / "app.py").write_text("print('modified')")
        print(f"   Code changed: {cache_mgr.has_code_changed()}")
        
        # Refresh cache
        print("\n6. Refresh Status:")
        needs_refresh = cache_mgr.refresh_cache()
        print(f"   Needs refresh: {needs_refresh}")
        
        # Load data
        print("\n7. Loading Cached Data:")
        loaded = cache_mgr.load_analysis_data()
        if loaded:
            print(f"   ✓ Loaded {len(loaded)} sections:")
            for section in loaded.keys():
                print(f"     - {section}")
        
        # Clear cache
        print("\n8. Clearing Cache:")
        cache_mgr.clear_cache()
        status = cache_mgr.get_cache_status()
        print(f"   Status: {status['status']}")


def example_5_validation():
    """Example: Command validation and error handling."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Validation & Error Handling")
    print("="*70)
    
    router = CommandRouter()
    
    test_cases = [
        ('@harness orchestrate "Valid task"', "✓ Valid"),
        ('@harness orchestrate', "✗ Missing task"),
        ('@harness orchestrate "Task" --figma-url invalid-url', "✗ Bad URL"),
        ('@harness verify', "✗ Missing path"),
        ('@harness cache invalid-action', "✗ Bad action"),
        ('not a valid command', "✗ Bad format"),
    ]
    
    for cmd_str, expected in test_cases:
        result = router.execute(cmd_str)
        status = "✓" if result["status"] == "pending" else "✗"
        print(f"\n{status} {cmd_str}")
        print(f"  Result: {result['status']}")
        if "message" in result:
            print(f"  Message: {result['message']}")


def example_6_full_workflow():
    """Example: Complete workflow from detection to caching."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Full Workflow")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        print("\n1. Initialize Project Structure")
        result = AutoDetector.init_harness_structure(tmpdir)
        print(f"   Status: {result['status']}")
        print(f"   Path: {result['path']}")
        
        print("\n2. Create Source Code")
        (tmpdir / "main.py").write_text("def main(): pass")
        (tmpdir / "test.py").write_text("def test(): pass")
        
        print("\n3. Auto-detect .harness")
        detector = AutoDetector(tmpdir)
        status = detector.get_status()
        print(f"   Detected: {status['detected']}")
        print(f"   Is first-run: {status['is_first_run']}")
        
        print("\n4. Run Analysis")
        router = CommandRouter()
        result = router.execute('@harness analyze')
        output = router.format_output('@harness analyze', result)
        print(output[:200] + "...")
        
        print("\n5. Cache Analysis Results")
        cache_mgr = CacheManager(tmpdir)
        cache_mgr.save_analysis_data({
            "patterns": {"python": "standard_library"},
            "architecture": "# Main\n- functions",
        })
        status = cache_mgr.get_cache_status()
        print(f"   Cache valid: {cache_mgr.is_cache_valid()}")
        print(f"   Files cached: {sum(1 for v in status['files_cached'].values() if v)}")
        
        print("\n6. Check Cache")
        result = router.execute('@harness cache status')
        output = router.format_output('@harness cache status', result)
        print(output[:200] + "...")
        
        print("\n7. Code Change Detection")
        (tmpdir / "main.py").write_text("def main(args): pass  # Modified")
        print(f"   Code changed: {cache_mgr.has_code_changed()}")
        
        print("\n8. Refresh Cache")
        cache_mgr.refresh_cache()
        print(f"   Cache invalidated and ready for refresh")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 1.3: CLAUDE COMMANDS INTEGRATION - USAGE EXAMPLES")
    print("="*70)
    
    try:
        example_1_basic_command_parsing()
        example_2_command_execution()
        example_3_auto_detection()
        example_4_cache_management()
        example_5_validation()
        example_6_full_workflow()
        
        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*70)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
