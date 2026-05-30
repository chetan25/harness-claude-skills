"""Lint integration for multiple linters."""

import json
import subprocess
from pathlib import Path
from typing import List, Tuple


class LintChecker:
    """Handles linting checks for various linters."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
    
    def check(self) -> Tuple[List[str], List[str]]:
        """Run appropriate linter for project.
        
        Returns:
            (errors, warnings)
        """
        # Detect linter
        if (self.project_path / ".eslintrc.json").exists() or \
           (self.project_path / ".eslintrc.js").exists() or \
           (self.project_path / ".eslintrc.yaml").exists():
            return self._check_eslint()
        
        if (self.project_path / "pylintrc").exists() or \
           (self.project_path / ".pylintrc").exists():
            return self._check_pylint()
        
        if (self.project_path / "pyproject.toml").exists():
            return self._check_ruff()
        
        return [], []
    
    def check_file(self, file_path: str) -> Tuple[List[str], List[str]]:
        """Check specific file.
        
        Args:
            file_path: Path to file
            
        Returns:
            (errors, warnings)
        """
        full_path = self.project_path / file_path
        if not full_path.exists():
            return [f"File not found: {file_path}"], []
        
        if file_path.endswith(".js") or file_path.endswith(".tsx") or \
           file_path.endswith(".ts") or file_path.endswith(".jsx"):
            return self._check_eslint_file(file_path)
        
        if file_path.endswith(".py"):
            return self._check_pylint_file(file_path)
        
        return [], []
    
    def _check_eslint(self) -> Tuple[List[str], List[str]]:
        """Check with ESLint."""
        try:
            result = subprocess.run(
                ["npx", "eslint", ".", "--format", "json"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if not result.stdout:
                return [], []
            
            data = json.loads(result.stdout)
            errors = []
            warnings = []
            
            for file_report in data:
                for message in file_report.get("messages", []):
                    msg = f"{file_report['filePath']}: {message['message']}"
                    if message["severity"] == 2:
                        errors.append(msg)
                    else:
                        warnings.append(msg)
            
            return errors, warnings
        except Exception as e:
            return [str(e)], []
    
    def _check_eslint_file(self, file_path: str) -> Tuple[List[str], List[str]]:
        """Check single file with ESLint."""
        try:
            result = subprocess.run(
                ["npx", "eslint", str(file_path), "--format", "json"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if not result.stdout:
                return [], []
            
            data = json.loads(result.stdout)
            errors = []
            warnings = []
            
            for message in data[0].get("messages", []):
                msg = f"{message['message']}"
                if message["severity"] == 2:
                    errors.append(msg)
                else:
                    warnings.append(msg)
            
            return errors, warnings
        except Exception as e:
            return [str(e)], []
    
    def _check_pylint(self) -> Tuple[List[str], List[str]]:
        """Check with Pylint."""
        try:
            result = subprocess.run(
                ["pylint", ".", "--exit-zero"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            lines = result.stdout.split("\n")
            errors = []
            warnings = []
            
            for line in lines:
                if "error" in line.lower():
                    errors.append(line)
                elif "warning" in line.lower():
                    warnings.append(line)
            
            return errors, warnings
        except Exception as e:
            return [str(e)], []
    
    def _check_pylint_file(self, file_path: str) -> Tuple[List[str], List[str]]:
        """Check single file with Pylint."""
        try:
            result = subprocess.run(
                ["pylint", str(file_path), "--exit-zero"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            lines = result.stdout.split("\n")
            errors = []
            warnings = []
            
            for line in lines:
                if "error" in line.lower():
                    errors.append(line)
                elif "warning" in line.lower():
                    warnings.append(line)
            
            return errors, warnings
        except Exception as e:
            return [str(e)], []
    
    def _check_ruff(self) -> Tuple[List[str], List[str]]:
        """Check with Ruff."""
        try:
            result = subprocess.run(
                ["ruff", "check", "."],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            return result.stdout.split("\n"), []
        except Exception as e:
            return [str(e)], []
