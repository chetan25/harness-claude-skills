"""Test runner integration for Jest, pytest, Vitest."""

import json
import subprocess
from pathlib import Path
from typing import List, Tuple


class TestRunner:
    """Handles test execution for various test frameworks."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
    
    def run(self, path: str = None) -> Tuple[int, int, List[str]]:
        """Run tests for project.
        
        Args:
            path: Optional specific path to test
            
        Returns:
            (passed_count, failed_count, errors)
        """
        # Detect test framework
        if (self.project_path / "jest.config.js").exists() or \
           (self.project_path / "package.json").exists():
            return self._run_jest(path)
        
        if (self.project_path / "pytest.ini").exists() or \
           (self.project_path / "pyproject.toml").exists():
            return self._run_pytest(path)
        
        return 0, 0, []
    
    def _run_jest(self, path: str = None) -> Tuple[int, int, List[str]]:
        """Run tests with Jest."""
        try:
            cmd = ["npx", "jest", "--json"]
            if path:
                cmd.append(path)
            
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if not result.stdout:
                return 0, 0, []
            
            data = json.loads(result.stdout)
            passed = data.get("numPassedTests", 0)
            failed = data.get("numFailedTests", 0)
            
            errors = []
            for test_result in data.get("testResults", []):
                for failure in test_result.get("assertionResults", []):
                    if failure["status"] == "failed":
                        errors.append(failure.get("failureMessages", ["Unknown error"])[0])
            
            return passed, failed, errors
        except Exception as e:
            return 0, 0, [str(e)]
    
    def _run_pytest(self, path: str = None) -> Tuple[int, int, List[str]]:
        """Run tests with pytest."""
        try:
            cmd = ["pytest", "--json-report"]
            if path:
                cmd.append(path)
            
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            # Parse output
            lines = result.stdout.split("\n")
            passed = 0
            failed = 0
            errors = []
            
            for line in lines:
                if " passed" in line:
                    passed = int(line.split()[0]) if line.split()[0].isdigit() else 0
                if " failed" in line:
                    failed = int(line.split()[0]) if line.split()[0].isdigit() else 0
                if "FAILED" in line:
                    errors.append(line)
            
            return passed, failed, errors
        except Exception as e:
            return 0, 0, [str(e)]
