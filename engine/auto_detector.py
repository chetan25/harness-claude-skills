"""
Auto-detection system for .harness folder and first-run detection.

Handles project root detection, first-run analysis triggering, and initialization.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List


class AutoDetector:
    """Auto-detects .harness folder and first-run conditions."""

    HARNESS_DIR_NAME = ".harness"
    MARKER_FILE = ".harness_initialized"

    def __init__(self, start_path: Optional[Path] = None):
        """
        Initialize auto-detector.
        
        Args:
            start_path: Starting directory for search. Defaults to current working directory.
        """
        self.start_path = start_path or Path.cwd()
        self.harness_root = None
        self.project_root = None

    def find_harness_root(self) -> Optional[Path]:
        """
        Find .harness directory by traversing up from start_path.
        
        Returns:
            Path to .harness directory or None if not found
        """
        current = self.start_path.resolve()

        while current != current.parent:
            harness_dir = current / self.HARNESS_DIR_NAME
            if harness_dir.exists() and harness_dir.is_dir():
                self.harness_root = harness_dir
                self.project_root = current
                return harness_dir

            current = current.parent

        return None

    def is_first_run(self) -> bool:
        """
        Check if this is a first-run scenario.
        
        Returns:
            True if .harness/ exists but is not initialized
        """
        if not self.harness_root:
            self.find_harness_root()

        if not self.harness_root:
            return False

        marker = self.harness_root / self.MARKER_FILE
        return not marker.exists()

    def mark_initialized(self) -> None:
        """Mark .harness as initialized."""
        if not self.harness_root:
            self.find_harness_root()

        if self.harness_root:
            marker = self.harness_root / self.MARKER_FILE
            marker.touch()

    def get_status(self) -> Dict[str, Any]:
        """
        Get detection status.
        
        Returns:
            Dictionary with detection info
        """
        harness = self.find_harness_root()

        if not harness:
            return {
                "detected": False,
                "harness_root": None,
                "project_root": None,
                "is_first_run": False,
                "message": "No .harness folder found. Initialize with: git clone ... .harness",
            }

        first_run = self.is_first_run()

        return {
            "detected": True,
            "harness_root": str(harness),
            "project_root": str(self.project_root),
            "is_first_run": first_run,
            "message": "First-run: analysis required"
            if first_run
            else "Already initialized",
        }

    def list_harness_contents(self) -> Dict[str, Any]:
        """
        List contents of .harness directory.
        
        Returns:
            Dictionary with directory structure
        """
        if not self.harness_root:
            self.find_harness_root()

        if not self.harness_root:
            return {}

        contents = {
            "root": str(self.harness_root),
            "subdirs": [],
            "files": [],
        }

        try:
            for item in self.harness_root.iterdir():
                if item.is_dir():
                    contents["subdirs"].append(item.name)
                elif item.is_file():
                    contents["files"].append(item.name)
        except OSError:
            pass

        return contents

    def verify_structure(self) -> Tuple[bool, List[str]]:
        """
        Verify .harness directory structure is valid.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        if not self.harness_root:
            self.find_harness_root()

        if not self.harness_root:
            return False, ["No .harness folder found"]

        issues = []

        # Check required directories
        required_dirs = ["skills", "cli", "docs"]
        for dirname in required_dirs:
            dirpath = self.harness_root / dirname
            if not dirpath.exists():
                issues.append(f"Missing directory: {dirname}")

        # Check generated directory
        generated_dir = self.harness_root / "generated"
        if not generated_dir.exists():
            # This is ok, it gets created on first run
            pass

        return len(issues) == 0, issues

    @staticmethod
    def init_harness_structure(project_root: Path) -> Dict[str, Any]:
        """
        Initialize .harness directory structure.
        
        Args:
            project_root: Root of the project
            
        Returns:
            Dictionary with initialization status
        """
        harness_root = project_root / AutoDetector.HARNESS_DIR_NAME

        if harness_root.exists():
            return {
                "status": "exists",
                "message": ".harness already exists",
                "path": str(harness_root),
            }

        # Create structure
        harness_root.mkdir(exist_ok=True)

        directories = [
            "skills",
            "generated",
            "cli",
            "docs",
        ]

        for dirname in directories:
            (harness_root / dirname).mkdir(exist_ok=True)

        # Create marker
        (harness_root / AutoDetector.MARKER_FILE).touch()

        return {
            "status": "created",
            "message": ".harness directory initialized",
            "path": str(harness_root),
            "directories_created": directories,
        }
