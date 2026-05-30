"""Type checker integration for TypeScript, MyPy, Pyright."""

import subprocess
from pathlib import Path
from typing import List, Tuple


class TypeChecker:
    """Handles type checking for various type checkers."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
    
    def check(self) -> Tuple[List[str], List[str]]:
        """Run appropriate type checker for project.
        
        Returns:
            (errors, warnings)
        """
        # Detect type checker
        if (self.project_path / "tsconfig.json").exists():
            return self._check_typescript()
        
        if (self.project_path / "pyproject.toml").exists() or \
           (self.project_path / "setup.py").exists():
            return self._check_mypy()
        
        return [], []
    
    def _check_typescript(self) -> Tuple[List[str], List[str]]:
        """Check with TypeScript compiler."""
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            errors = []
            warnings = []
            
            for line in result.stderr.split("\n"):
                if "error" in line.lower():
                    errors.append(line)
                elif "warning" in line.lower():
                    warnings.append(line)
            
            return errors, warnings
        except Exception as e:
            return [str(e)], []
    
    def _check_mypy(self) -> Tuple[List[str], List[str]]:
        """Check with MyPy."""
        try:
            result = subprocess.run(
                ["mypy", "."],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            errors = []
            for line in result.stdout.split("\n"):
                if "error:" in line:
                    errors.append(line)
            
            return errors, []
        except Exception as e:
            return [str(e)], []
    
    def _check_pyright(self) -> Tuple[List[str], List[str]]:
        """Check with Pyright."""
        try:
            result = subprocess.run(
                ["pyright"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            errors = []
            for line in result.stdout.split("\n"):
                if "error" in line.lower():
                    errors.append(line)
            
            return errors, []
        except Exception as e:
            return [str(e)], []
