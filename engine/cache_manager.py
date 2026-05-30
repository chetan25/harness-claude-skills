"""
Cache Management System for Harness Claude Skills.

Handles caching of analysis, invalidation on code changes, and cache lifecycle.
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import time


class CacheManager:
    """Manages cache operations for Harness analysis."""

    CACHE_DIR = ".harness/generated"
    CACHE_FILE = "cache.json"
    CACHE_VERSION = "1.0"

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize cache manager.
        
        Args:
            project_root: Project root directory. Auto-detected if not provided.
        """
        self.project_root = project_root or self._find_project_root()
        self.cache_dir = self.project_root / self.CACHE_DIR
        self.cache_file = self.cache_dir / self.CACHE_FILE

    @staticmethod
    def _find_project_root() -> Path:
        """Find .harness folder starting from current directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".harness").exists():
                return current
            current = current.parent
        raise RuntimeError("Could not find .harness folder. Run from project root.")

    def ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cache from disk."""
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def save_cache(self, data: Dict[str, Any]) -> None:
        """Save cache to disk."""
        self.ensure_cache_dir()
        data["version"] = self.CACHE_VERSION
        data["timestamp"] = datetime.now().isoformat()

        with open(self.cache_file, "w") as f:
            json.dump(data, f, indent=2)

    def is_cache_valid(self, ttl_hours: int = 24) -> bool:
        """
        Check if cache is valid (not expired).
        
        Args:
            ttl_hours: Time-to-live in hours
            
        Returns:
            True if cache exists and is not expired
        """
        cache = self.load_cache()
        if not cache or "timestamp" not in cache:
            return False

        try:
            cache_time = datetime.fromisoformat(cache["timestamp"])
            age_hours = (datetime.now() - cache_time).total_seconds() / 3600
            return age_hours < ttl_hours
        except (ValueError, TypeError):
            return False

    def invalidate_cache(self) -> None:
        """Invalidate cache by removing cache file."""
        if self.cache_file.exists():
            self.cache_file.unlink()

    def get_code_hash(self) -> str:
        """
        Compute hash of project code to detect changes.
        
        Returns:
            SHA256 hash of all source files
        """
        hash_obj = hashlib.sha256()

        # Extensions to hash
        extensions = {".py", ".ts", ".tsx", ".jsx", ".js", ".vue", ".svelte"}
        ignore_dirs = {".git", ".harness", "node_modules", ".next", "dist", "build"}

        for root, dirs, files in os.walk(self.project_root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for file in sorted(files):
                if any(file.endswith(ext) for ext in extensions):
                    filepath = Path(root) / file
                    try:
                        with open(filepath, "rb") as f:
                            hash_obj.update(f.read())
                    except (IOError, OSError):
                        pass

        return hash_obj.hexdigest()

    def has_code_changed(self) -> bool:
        """
        Check if project code has changed since last analysis.
        
        Returns:
            True if code changed or cache has no hash
        """
        cache = self.load_cache()
        if not cache or "code_hash" not in cache:
            return True

        current_hash = self.get_code_hash()
        return current_hash != cache["code_hash"]

    def get_cache_status(self) -> Dict[str, Any]:
        """Get current cache status."""
        cache = self.load_cache()

        if not cache:
            return {
                "status": "empty",
                "exists": False,
                "message": "No cache found. Run analysis first.",
            }

        status = {
            "status": "valid" if self.is_cache_valid() else "expired",
            "exists": True,
            "timestamp": cache.get("timestamp"),
            "version": cache.get("version"),
            "code_changed": self.has_code_changed(),
            "files_cached": {
                "patterns": (self.cache_dir / "patterns.json").exists(),
                "architecture": (self.cache_dir / "architecture.md").exists(),
                "diagrams": (self.cache_dir / "diagrams.mermaid").exists(),
                "design_tokens": (self.cache_dir / "design-tokens.json").exists(),
                "skills_summary": (self.cache_dir / "skills-summary.md").exists(),
            },
        }

        if status["code_changed"]:
            status["message"] = "Code changed since last analysis. Consider refresh."
        else:
            status["message"] = "Cache is up-to-date."

        return status

    def clear_cache(self) -> None:
        """Clear all cache files."""
        cache_files = [
            "patterns.json",
            "architecture.md",
            "diagrams.mermaid",
            "design-tokens.json",
            "skills-summary.md",
            "cache.json",
        ]

        for filename in cache_files:
            filepath = self.cache_dir / filename
            if filepath.exists():
                filepath.unlink()

    def refresh_cache(self) -> bool:
        """
        Refresh cache by invalidating and recomputing.
        
        Returns:
            True if refresh needed (code changed or cache invalid)
        """
        needs_refresh = self.has_code_changed() or not self.is_cache_valid()

        if needs_refresh:
            self.invalidate_cache()
            return True

        return False

    def save_analysis_data(self, data: Dict[str, Any]) -> None:
        """
        Save analysis data to cache.
        
        Args:
            data: Analysis data dictionary containing patterns, architecture, etc.
        """
        self.ensure_cache_dir()

        # Save individual files
        if "patterns" in data:
            with open(self.cache_dir / "patterns.json", "w") as f:
                json.dump(data["patterns"], f, indent=2)

        if "architecture" in data:
            with open(self.cache_dir / "architecture.md", "w") as f:
                f.write(data["architecture"])

        if "diagrams" in data:
            with open(self.cache_dir / "diagrams.mermaid", "w") as f:
                f.write(data["diagrams"])

        if "design_tokens" in data:
            with open(self.cache_dir / "design-tokens.json", "w") as f:
                json.dump(data["design_tokens"], f, indent=2)

        if "skills_summary" in data:
            with open(self.cache_dir / "skills-summary.md", "w") as f:
                f.write(data["skills_summary"])

        # Save metadata
        cache_meta = {
            "code_hash": self.get_code_hash(),
            "has_patterns": "patterns" in data,
            "has_architecture": "architecture" in data,
            "has_diagrams": "diagrams" in data,
            "has_design_tokens": "design_tokens" in data,
            "has_skills_summary": "skills_summary" in data,
        }

        self.save_cache(cache_meta)

    def load_analysis_data(self) -> Optional[Dict[str, Any]]:
        """
        Load cached analysis data.
        
        Returns:
            Analysis data or None if not cached
        """
        if not self.cache_file.exists():
            return None

        data = {}

        # Load individual files if they exist
        patterns_file = self.cache_dir / "patterns.json"
        if patterns_file.exists():
            with open(patterns_file) as f:
                data["patterns"] = json.load(f)

        arch_file = self.cache_dir / "architecture.md"
        if arch_file.exists():
            with open(arch_file) as f:
                data["architecture"] = f.read()

        diagrams_file = self.cache_dir / "diagrams.mermaid"
        if diagrams_file.exists():
            with open(diagrams_file) as f:
                data["diagrams"] = f.read()

        tokens_file = self.cache_dir / "design-tokens.json"
        if tokens_file.exists():
            with open(tokens_file) as f:
                data["design_tokens"] = json.load(f)

        summary_file = self.cache_dir / "skills-summary.md"
        if summary_file.exists():
            with open(summary_file) as f:
                data["skills_summary"] = f.read()

        return data if data else None
