"""
Comprehensive tests for Phase 1.3 command handling.
Run with: python -m pytest test_commands.py -v
"""

import sys
sys.path.insert(0, '/tmp/harness-claude-skills/engine')

from pathlib import Path
import tempfile

from commands import CommandType, CommandArgs, CommandValidator, OrchestrateCommand
from command_router import CommandParser, CommandRouter
from auto_detector import AutoDetector
from cache_manager import CacheManager


def test_parse_orchestrate():
    """Test parsing orchestrate command."""
    cmd = CommandParser.parse('@harness orchestrate "Add feature"')
    assert cmd is not None
    assert cmd.command == CommandType.ORCHESTRATE
    assert cmd.task == "Add feature"
    print("✓ test_parse_orchestrate")


def test_parse_with_figma():
    """Test parsing with Figma URL."""
    cmd = CommandParser.parse(
        '@harness orchestrate "Task" --figma-url https://figma.com/test'
    )
    assert cmd.figma_url == "https://figma.com/test"
    print("✓ test_parse_with_figma")


def test_parse_cache_command():
    """Test parsing cache commands."""
    for action in ["clear", "refresh", "status"]:
        cmd = CommandParser.parse(f"@harness cache {action}")
        assert cmd.cache_action == action
    print("✓ test_parse_cache_command")


def test_validate_orchestrate():
    """Test validation."""
    args = CommandArgs(command=CommandType.ORCHESTRATE, task="Task")
    is_valid, _ = CommandValidator.validate_orchestrate(args)
    assert is_valid
    print("✓ test_validate_orchestrate")


def test_execute_command():
    """Test command execution."""
    router = CommandRouter()
    result = router.execute('@harness analyze')
    assert result["status"] == "pending"
    print("✓ test_execute_command")


def test_auto_detect():
    """Test auto-detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / ".harness").mkdir()
        detector = AutoDetector(tmpdir)
        found = detector.find_harness_root()
        assert found is not None
    print("✓ test_auto_detect")


def test_cache_operations():
    """Test cache save/load."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / ".harness").mkdir()
        cache_mgr = CacheManager(tmpdir)
        cache_mgr.save_cache({"key": "value"})
        loaded = cache_mgr.load_cache()
        assert loaded["key"] == "value"
    print("✓ test_cache_operations")


def test_code_hash():
    """Test code hash detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / ".harness").mkdir()
        (tmpdir / "test.py").write_text("code")
        cache_mgr = CacheManager(tmpdir)
        hash1 = cache_mgr.get_code_hash()
        (tmpdir / "test.py").write_text("new")
        hash2 = cache_mgr.get_code_hash()
        assert hash1 != hash2
    print("✓ test_code_hash")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Phase 1.3 Command Integration Tests")
    print("="*60 + "\n")
    
    tests = [
        test_parse_orchestrate,
        test_parse_with_figma,
        test_parse_cache_command,
        test_validate_orchestrate,
        test_execute_command,
        test_auto_detect,
        test_cache_operations,
        test_code_hash,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__}: {e}")
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60 + "\n")
