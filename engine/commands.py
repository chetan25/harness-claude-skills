"""
Command definitions and handlers for Harness Claude Skills.

Defines all available commands:
- orchestrate: Run full 7-phase workflow
- analyze: Analyze project and generate skills
- context: Show context information
- verify: Verify code/tests/lint
- cache: Manage cache (clear/refresh/status)
"""

from enum import Enum
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from pathlib import Path
import sys


class CommandType(Enum):
    """Available command types."""

    ORCHESTRATE = "orchestrate"
    ANALYZE = "analyze"
    CONTEXT = "context"
    VERIFY = "verify"
    CACHE = "cache"


@dataclass
class CommandArgs:
    """Parsed command arguments."""

    command: CommandType
    task: Optional[str] = None
    figma_url: Optional[str] = None
    cache_action: Optional[str] = None  # clear, refresh, status
    path: Optional[str] = None
    flags: Dict[str, Any] = None

    def __post_init__(self):
        if self.flags is None:
            self.flags = {}


class CommandValidator:
    """Validates command arguments."""

    @staticmethod
    def validate_orchestrate(args: CommandArgs) -> tuple[bool, str]:
        """Validate orchestrate command."""
        if not args.task or not args.task.strip():
            return False, "Task description required: @harness orchestrate \"task description\""

        if args.figma_url and not args.figma_url.startswith(("http://", "https://")):
            return False, "Invalid Figma URL format"

        return True, ""

    @staticmethod
    def validate_analyze(args: CommandArgs) -> tuple[bool, str]:
        """Validate analyze command."""
        return True, ""

    @staticmethod
    def validate_context(args: CommandArgs) -> tuple[bool, str]:
        """Validate context command."""
        return True, ""

    @staticmethod
    def validate_verify(args: CommandArgs) -> tuple[bool, str]:
        """Validate verify command."""
        if not args.path:
            return False, "Path required: @harness verify ./path/to/verify"

        return True, ""

    @staticmethod
    def validate_cache(args: CommandArgs) -> tuple[bool, str]:
        """Validate cache command."""
        valid_actions = {"clear", "refresh", "status"}

        if not args.cache_action or args.cache_action not in valid_actions:
            return False, f"Cache action must be: {', '.join(valid_actions)}"

        return True, ""

    @staticmethod
    def validate(args: CommandArgs) -> tuple[bool, str]:
        """
        Validate command arguments.

        Returns:
            Tuple of (is_valid, error_message)
        """
        validators = {
            CommandType.ORCHESTRATE: CommandValidator.validate_orchestrate,
            CommandType.ANALYZE: CommandValidator.validate_analyze,
            CommandType.CONTEXT: CommandValidator.validate_context,
            CommandType.VERIFY: CommandValidator.validate_verify,
            CommandType.CACHE: CommandValidator.validate_cache,
        }

        validator = validators.get(args.command)
        if validator:
            return validator(args)

        return False, f"Unknown command: {args.command}"


class CommandFormatter:
    """Formats command output for Claude."""

    @staticmethod
    def format_header(title: str) -> str:
        """Format section header."""
        return f"\n{'=' * 60}\n{title}\n{'=' * 60}\n"

    @staticmethod
    def format_section(title: str, content: str) -> str:
        """Format a section with title and content."""
        return f"\n### {title}\n{content}\n"

    @staticmethod
    def format_list(items: List[str]) -> str:
        """Format a list of items."""
        return "\n".join(f"• {item}" for item in items)

    @staticmethod
    def format_key_value(data: Dict[str, Any]) -> str:
        """Format key-value pairs."""
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                value_str = str(value)
            else:
                value_str = str(value)
            lines.append(f"**{key}:** {value_str}")
        return "\n".join(lines)

    @staticmethod
    def format_status(status: str, message: str, details: Optional[Dict] = None) -> str:
        """Format status output."""
        output = f"\n**Status:** {status}\n**Message:** {message}"

        if details:
            output += "\n\n**Details:**\n"
            output += CommandFormatter.format_key_value(details)

        return output

    @staticmethod
    def format_error(error: str) -> str:
        """Format error message."""
        return f"\n❌ **Error:** {error}\n"

    @staticmethod
    def format_success(message: str, details: Optional[str] = None) -> str:
        """Format success message."""
        output = f"\n✅ **Success:** {message}\n"
        if details:
            output += f"\n{details}"
        return output


class Command:
    """Base command class."""

    def __init__(self, name: str, description: str):
        """Initialize command."""
        self.name = name
        self.description = description

    def execute(self, args: CommandArgs) -> Dict[str, Any]:
        """
        Execute command.

        Returns:
            Dictionary with command result
        """
        raise NotImplementedError

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format command output for Claude."""
        raise NotImplementedError


class OrchestrateCommand(Command):
    """Orchestrate command: run full 7-phase workflow."""

    def __init__(self):
        super().__init__(
            "orchestrate",
            "Orchestrate full workflow for a task",
        )

    def execute(self, args: CommandArgs) -> Dict[str, Any]:
        """Execute orchestrate command."""
        is_valid, error = CommandValidator.validate_orchestrate(args)
        if not is_valid:
            return {"status": "error", "message": error}

        return {
            "status": "pending",
            "command": "orchestrate",
            "task": args.task,
            "figma_url": args.figma_url,
            "cache_action": args.flags.get("cache", "use"),
            "phases": [
                "1. Problem Analysis",
                "2. Context Loading",
                "3. Code Generation",
                "4. Visual Verification",
                "5. Testing",
                "6. Re-Verification",
                "7. Completion",
            ],
        }

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format orchestrate output."""
        if result["status"] == "error":
            return CommandFormatter.format_error(result["message"])

        output = CommandFormatter.format_header("🎯 Orchestration Started")
        output += CommandFormatter.format_section(
            "Task",
            f"```\n{result['task']}\n```",
        )

        if result.get("figma_url"):
            output += CommandFormatter.format_section("Figma Design", result["figma_url"])

        output += CommandFormatter.format_section("Phases", CommandFormatter.format_list(result["phases"]))

        output += "\n📋 **Next Step:** Running Phase 1 - Problem Analysis..."

        return output


class AnalyzeCommand(Command):
    """Analyze command: analyze project and generate skills."""

    def __init__(self):
        super().__init__(
            "analyze",
            "Analyze project and generate skills",
        )

    def execute(self, args: CommandArgs) -> Dict[str, Any]:
        """Execute analyze command."""
        is_valid, error = CommandValidator.validate_analyze(args)
        if not is_valid:
            return {"status": "error", "message": error}

        return {
            "status": "pending",
            "command": "analyze",
            "steps": [
                "Scanning project structure",
                "Extracting code patterns",
                "Analyzing framework/libraries",
                "Detecting design system",
                "Generating Mermaid diagrams",
                "Caching results",
            ],
        }

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format analyze output."""
        if result["status"] == "error":
            return CommandFormatter.format_error(result["message"])

        output = CommandFormatter.format_header("🔍 Project Analysis")
        output += CommandFormatter.format_section(
            "Running Steps",
            CommandFormatter.format_list(result["steps"]),
        )

        return output


class ContextCommand(Command):
    """Context command: show context information."""

    def __init__(self):
        super().__init__(
            "context",
            "Show current context information",
        )

    def execute(self, args: CommandArgs) -> Dict[str, Any]:
        """Execute context command."""
        is_valid, error = CommandValidator.validate_context(args)
        if not is_valid:
            return {"status": "error", "message": error}

        return {
            "status": "pending",
            "command": "context",
            "info_types": [
                "Project root",
                "Detected frameworks",
                "Code patterns",
                "Design tokens",
                "Architecture overview",
                "Cache status",
            ],
        }

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format context output."""
        if result["status"] == "error":
            return CommandFormatter.format_error(result["message"])

        output = CommandFormatter.format_header("📚 Context Information")
        output += CommandFormatter.format_section(
            "Available Info",
            CommandFormatter.format_list(result["info_types"]),
        )

        return output


class VerifyCommand(Command):
    """Verify command: verify code/tests/lint."""

    def __init__(self):
        super().__init__(
            "verify",
            "Verify code, tests, and linting",
        )

    def execute(self, args: CommandArgs) -> Dict[str, Any]:
        """Execute verify command."""
        is_valid, error = CommandValidator.validate_verify(args)
        if not is_valid:
            return {"status": "error", "message": error}

        return {
            "status": "pending",
            "command": "verify",
            "path": args.path,
            "checks": [
                "Type checking",
                "Linting",
                "Tests",
                "Coverage",
                "Build",
            ],
        }

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format verify output."""
        if result["status"] == "error":
            return CommandFormatter.format_error(result["message"])

        output = CommandFormatter.format_header("✓ Verification")
        output += CommandFormatter.format_section("Path", f"```\n{result['path']}\n```")
        output += CommandFormatter.format_section(
            "Checks",
            CommandFormatter.format_list(result["checks"]),
        )

        return output


class CacheCommand(Command):
    """Cache command: manage cache."""

    def __init__(self):
        super().__init__(
            "cache",
            "Manage cache (clear/refresh/status)",
        )

    def execute(self, args: CommandArgs) -> Dict[str, Any]:
        """Execute cache command."""
        is_valid, error = CommandValidator.validate_cache(args)
        if not is_valid:
            return {"status": "error", "message": error}

        action = args.cache_action.lower()

        return {
            "status": "pending",
            "command": "cache",
            "action": action,
            "message": f"Cache {action} initiated",
        }

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format cache output."""
        if result["status"] == "error":
            return CommandFormatter.format_error(result["message"])

        action = result["action"].upper()
        output = CommandFormatter.format_header(f"💾 Cache {action}")
        output += result["message"]

        return output


# Registry of all available commands
COMMAND_REGISTRY: Dict[CommandType, Command] = {
    CommandType.ORCHESTRATE: OrchestrateCommand(),
    CommandType.ANALYZE: AnalyzeCommand(),
    CommandType.CONTEXT: ContextCommand(),
    CommandType.VERIFY: VerifyCommand(),
    CommandType.CACHE: CacheCommand(),
}


def get_command(command_type: CommandType) -> Optional[Command]:
    """Get command instance by type."""
    return COMMAND_REGISTRY.get(command_type)
