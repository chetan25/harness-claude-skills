#!/usr/bin/env python3
"""
CLI entry point for Skill Builder Engine.

Usage:
    python3 cli.py <project_path> [--output-dir <dir>] [--verbose]
    python3 cli.py analyze <project_path>
    python3 cli.py generate-artifacts <project_path> --output-dir <dir>
"""

import argparse
import sys
import json
from pathlib import Path

from analyzer import ProjectAnalyzer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Skill Builder Engine - Analyze projects and generate architecture diagrams"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a project")
    analyze_parser.add_argument(
        "project_path",
        help="Path to project root"
    )
    analyze_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    # generate-artifacts command
    artifacts_parser = subparsers.add_parser(
        "generate-artifacts",
        help="Generate and save artifacts"
    )
    artifacts_parser.add_argument(
        "project_path",
        help="Path to project root"
    )
    artifacts_parser.add_argument(
        "--output-dir", "-o",
        default=".harness/generated",
        help="Output directory (default: .harness/generated)"
    )
    artifacts_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    # Default command (shorthand)
    parser.add_argument(
        "project_path",
        nargs="?",
        help="Path to project (shorthand: same as 'analyze' command)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for artifacts"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Handle shorthand usage
    if args.command is None and args.project_path:
        args.command = "analyze"
        if args.output_dir:
            args.command = "generate-artifacts"

    if not args.command or not args.project_path:
        parser.print_help()
        return 1

    try:
        analyzer = ProjectAnalyzer(verbose=args.verbose)

        if args.command == "analyze":
            return cmd_analyze(analyzer, args.project_path)

        elif args.command == "generate-artifacts":
            output_dir = args.output_dir or ".harness/generated"
            return cmd_generate_artifacts(analyzer, args.project_path, output_dir)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_analyze(analyzer: ProjectAnalyzer, project_path: str) -> int:
    """Run analysis command."""
    print(f"Analyzing project: {project_path}")
    print("-" * 60)

    results = analyzer.analyze(project_path)

    print("\n" + analyzer.get_analysis_summary())

    print("\n" + "-" * 60)
    print("Full results (JSON):")
    print(json.dumps(results, indent=2, default=str))

    return 0


def cmd_generate_artifacts(analyzer: ProjectAnalyzer, project_path: str, output_dir: str) -> int:
    """Run artifact generation command."""
    print(f"Analyzing project: {project_path}")
    print(f"Output directory: {output_dir}")
    print("-" * 60)

    # Run analysis
    analyzer.analyze(project_path)

    # Generate artifacts
    artifacts = analyzer.generate_artifacts(output_dir)

    print("\n" + analyzer.get_analysis_summary())

    print("\n" + "-" * 60)
    print(f"Generated {len(artifacts)} artifacts:")
    for name, path in artifacts.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"  ✓ {name:20} -> {path} ({size:,} bytes)")

    print("\nArtifacts saved to:", output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
