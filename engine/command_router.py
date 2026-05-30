"""
Command router: parses and routes commands to handlers.

Handles:
- String → command parsing
- Argument extraction
- Command type detection
- Handler invocation
"""

import re
import shlex
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path

from commands import CommandType, CommandArgs, Command, get_command, CommandValidator


class CommandParser:
    """Parses @harness command strings."""

    # Pattern: @harness <command> [args...]
    COMMAND_PATTERN = r"@harness\s+(\w+)(?:\s+(.*))?$"

    @staticmethod
    def parse(command_string: str) -> Optional[CommandArgs]:
        """
        Parse command string into CommandArgs.

        Example inputs:
        - @harness orchestrate "Add dark mode toggle" --figma-url https://... --cache refresh
        - @harness analyze
        - @harness context
        - @harness verify ./src/components/Button
        - @harness cache clear

        Returns:
            CommandArgs if valid, None otherwise
        """
        command_string = command_string.strip()

        # Check if it starts with @harness
        if not command_string.startswith("@harness"):
            return None

        match = re.match(CommandParser.COMMAND_PATTERN, command_string)
        if not match:
            return None

        command_name = match.group(1).lower()
        args_str = match.group(2) or ""

        # Try to get command type
        try:
            command_type = CommandType[command_name.upper()]
        except KeyError:
            return None

        # Parse arguments based on command type
        if command_type == CommandType.ORCHESTRATE:
            return CommandParser._parse_orchestrate(args_str)
        elif command_type == CommandType.ANALYZE:
            return CommandArgs(command=command_type)
        elif command_type == CommandType.CONTEXT:
            return CommandArgs(command=command_type)
        elif command_type == CommandType.VERIFY:
            return CommandParser._parse_verify(args_str)
        elif command_type == CommandType.CACHE:
            return CommandParser._parse_cache(args_str)

        return None

    @staticmethod
    def _parse_orchestrate(args_str: str) -> Optional[CommandArgs]:
        """Parse orchestrate command: orchestrate \"task\" [--figma-url URL] [--cache action]"""
        if not args_str.strip():
            return None

        try:
            parts = shlex.split(args_str)
        except ValueError:
            return None

        if not parts:
            return None

        # First argument should be the task
        task = parts[0]
        flags = {}

        # Parse flags
        i = 1
        figma_url = None

        while i < len(parts):
            if parts[i] == "--figma-url" and i + 1 < len(parts):
                figma_url = parts[i + 1]
                i += 2
            elif parts[i] == "--cache" and i + 1 < len(parts):
                flags["cache"] = parts[i + 1]
                i += 2
            else:
                i += 1

        return CommandArgs(
            command=CommandType.ORCHESTRATE,
            task=task,
            figma_url=figma_url,
            flags=flags,
        )

    @staticmethod
    def _parse_verify(args_str: str) -> Optional[CommandArgs]:
        """Parse verify command: verify ./path"""
        args_str = args_str.strip()
        if not args_str:
            return None

        # Path is the first argument
        parts = args_str.split()
        path = parts[0] if parts else None

        if not path:
            return None

        return CommandArgs(
            command=CommandType.VERIFY,
            path=path,
        )

    @staticmethod
    def _parse_cache(args_str: str) -> Optional[CommandArgs]:
        """Parse cache command: cache clear/refresh/status"""
        args_str = args_str.strip().lower()

        valid_actions = {"clear", "refresh", "status"}
        if args_str not in valid_actions:
            return None

        return CommandArgs(
            command=CommandType.CACHE,
            cache_action=args_str,
        )


class CommandRouter:
    """Routes parsed commands to handlers."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize router.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()

    def parse(self, command_string: str) -> Optional[CommandArgs]:
        """Parse command string."""
        return CommandParser.parse(command_string)

    def validate(self, args: CommandArgs) -> Tuple[bool, str]:
        """
        Validate command arguments.

        Returns:
            Tuple of (is_valid, error_message)
        """
        return CommandValidator.validate(args)

    def route(self, args: CommandArgs) -> Tuple[Optional[Command], str]:
        """
        Route to appropriate command handler.

        Returns:
            Tuple of (command_instance, error_message)
        """
        is_valid, error = self.validate(args)
        if not is_valid:
            return None, error

        command = get_command(args.command)
        if not command:
            return None, f"No handler for command: {args.command.value}"

        return command, ""

    def execute(self, command_string: str) -> Dict[str, Any]:
        """
        Parse, validate, and execute command.

        Returns:
            Dictionary with execution result
        """
        # Parse
        args = self.parse(command_string)
        if not args:
            return {
                "status": "error",
                "message": "Invalid command format",
                "example": "@harness orchestrate \"Add dark mode\"",
            }

        # Validate
        is_valid, error = self.validate(args)
        if not is_valid:
            return {
                "status": "error",
                "message": error,
            }

        # Route
        command, error = self.route(args)
        if not command:
            return {
                "status": "error",
                "message": error,
            }

        # Execute
        try:
            result = command.execute(args)
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Execution failed: {str(e)}",
            }

    def format_output(self, command_string: str, result: Dict[str, Any]) -> str:
        """
        Format command output for Claude.

        Args:
            command_string: Original command string
            result: Command execution result

        Returns:
            Formatted output string
        """
        args = self.parse(command_string)
        if not args:
            from commands import CommandFormatter
            return CommandFormatter.format_error("Failed to parse command")

        command = get_command(args.command)
        if not command:
            from commands import CommandFormatter
            return CommandFormatter.format_error("No handler for command")

        return command.format_output(result)


# Convenience function for typical usage
def route_and_execute(command_string: str, project_root: Optional[Path] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Parse, validate, execute, and format command in one call.

    Args:
        command_string: @harness command string
        project_root: Project root directory

    Returns:
        Tuple of (formatted_output, result_dict)
    """
    router = CommandRouter(project_root)
    result = router.execute(command_string)
    output = router.format_output(command_string, result)
    return output, result
