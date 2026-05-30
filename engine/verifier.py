"""
Harness Verification System - Main coordinator for code quality checks.

Integrates linters, type checkers, test runners, and design verification.
"""

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from .linter import LintChecker
    from .type_checker import TypeChecker
    from .test_runner import TestRunner
    from .design_verifier import DesignVerifier
except ImportError:
    from linter import LintChecker
    from type_checker import TypeChecker
    from test_runner import TestRunner
    from design_verifier import DesignVerifier


@dataclass
class VerificationResult:
    """Result of a verification check."""
    status: str  # "passed", "failed", "warning"
    tool: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "tool": self.tool,
            "errors": self.errors,
            "warnings": self.warnings,
            "details": self.details,
        }


@dataclass
class VerificationReport:
    """Complete verification report."""
    project_path: str
    timestamp: str
    lint_result: Optional[VerificationResult] = None
    type_check_result: Optional[VerificationResult] = None
    test_result: Optional[VerificationResult] = None
    design_result: Optional[VerificationResult] = None
    overall_status: str = "pending"
    
    def to_dict(self) -> Dict:
        return {
            "project_path": self.project_path,
            "timestamp": self.timestamp,
            "lint": self.lint_result.to_dict() if self.lint_result else None,
            "type_check": self.type_check_result.to_dict() if self.type_check_result else None,
            "tests": self.test_result.to_dict() if self.test_result else None,
            "design": self.design_result.to_dict() if self.design_result else None,
            "overall_status": self.overall_status,
        }


class Verifier:
    """Main verification coordinator."""
    
    def __init__(self, project_path: str):
        """Initialize verifier for a project.
        
        Args:
            project_path: Path to project root
        """
        self.project_path = Path(project_path)
        self.linter = LintChecker(project_path)
        self.type_checker = TypeChecker(project_path)
        self.test_runner = TestRunner(project_path)
        self.design_verifier = DesignVerifier(project_path)
    
    def verify_all(self, figma_url: Optional[str] = None) -> VerificationReport:
        """Run all verifications.
        
        Args:
            figma_url: Optional Figma design URL for comparison
            
        Returns:
            Complete verification report
        """
        from datetime import datetime
        report = VerificationReport(
            project_path=str(self.project_path),
            timestamp=datetime.now().isoformat(),
        )
        
        # Run linting
        report.lint_result = self.verify_lint()
        
        # Run type checking
        report.type_check_result = self.verify_types()
        
        # Run tests
        report.test_result = self.verify_tests()
        
        # Run design verification (if Figma URL provided)
        if figma_url:
            report.design_result = self.verify_design(figma_url)
        
        # Determine overall status
        report.overall_status = self._determine_status(report)
        
        return report
    
    def verify_lint(self) -> VerificationResult:
        """Run linting checks."""
        try:
            errors, warnings = self.linter.check()
            status = "failed" if errors else "passed" if not warnings else "warning"
            return VerificationResult(
                status=status,
                tool="linter",
                errors=errors,
                warnings=warnings,
            )
        except Exception as e:
            return VerificationResult(
                status="failed",
                tool="linter",
                errors=[str(e)],
            )
    
    def verify_types(self) -> VerificationResult:
        """Run type checking."""
        try:
            errors, warnings = self.type_checker.check()
            status = "failed" if errors else "passed" if not warnings else "warning"
            return VerificationResult(
                status=status,
                tool="type_checker",
                errors=errors,
                warnings=warnings,
            )
        except Exception as e:
            return VerificationResult(
                status="failed",
                tool="type_checker",
                errors=[str(e)],
            )
    
    def verify_tests(self, path: Optional[str] = None) -> VerificationResult:
        """Run tests.
        
        Args:
            path: Optional specific path to test
        """
        try:
            passed, failed, errors = self.test_runner.run(path)
            status = "passed" if not failed else "failed"
            return VerificationResult(
                status=status,
                tool="test_runner",
                errors=errors,
                details={"passed": passed, "failed": failed},
            )
        except Exception as e:
            return VerificationResult(
                status="failed",
                tool="test_runner",
                errors=[str(e)],
            )
    
    def verify_design(self, figma_url: str) -> VerificationResult:
        """Verify design compliance against Figma.
        
        Args:
            figma_url: Figma design URL
        """
        try:
            issues = self.design_verifier.compare(figma_url)
            status = "failed" if issues else "passed"
            return VerificationResult(
                status=status,
                tool="design_verifier",
                errors=issues,
            )
        except Exception as e:
            return VerificationResult(
                status="failed",
                tool="design_verifier",
                errors=[str(e)],
            )
    
    def verify_file(self, file_path: str) -> VerificationResult:
        """Verify a specific file.
        
        Args:
            file_path: Path to file to verify
        """
        try:
            errors, warnings = self.linter.check_file(file_path)
            status = "failed" if errors else "passed" if not warnings else "warning"
            return VerificationResult(
                status=status,
                tool="linter",
                errors=errors,
                warnings=warnings,
                details={"file": file_path},
            )
        except Exception as e:
            return VerificationResult(
                status="failed",
                tool="linter",
                errors=[str(e)],
            )
    
    def _determine_status(self, report: VerificationReport) -> str:
        """Determine overall verification status.
        
        Args:
            report: Verification report
            
        Returns:
            Overall status: "passed", "warning", or "failed"
        """
        has_failure = False
        has_warning = False
        
        for result in [report.lint_result, report.type_check_result, 
                      report.test_result, report.design_result]:
            if result is None:
                continue
            if result.status == "failed":
                has_failure = True
            elif result.status == "warning":
                has_warning = True
        
        if has_failure:
            return "failed"
        elif has_warning:
            return "warning"
        else:
            return "passed"
    
    def save_report(self, report: VerificationReport, output_path: str) -> None:
        """Save verification report to file.
        
        Args:
            report: Verification report
            output_path: Path to save report
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, "w") as f:
            json.dump(report.to_dict(), f, indent=2)


def verify_changes(project_path: str, changed_files: List[str]) -> VerificationReport:
    """Verify only changed files.
    
    Args:
        project_path: Project root
        changed_files: List of changed file paths
        
    Returns:
        Verification report
    """
    verifier = Verifier(project_path)
    report = VerificationReport(
        project_path=project_path,
        timestamp=__import__("datetime").datetime.now().isoformat(),
    )
    
    # Lint changed files
    lint_errors = []
    for file_path in changed_files:
        result = verifier.verify_file(file_path)
        lint_errors.extend(result.errors)
    
    report.lint_result = VerificationResult(
        status="failed" if lint_errors else "passed",
        tool="linter",
        errors=lint_errors,
    )
    
    report.overall_status = "failed" if lint_errors else "passed"
    
    return report
