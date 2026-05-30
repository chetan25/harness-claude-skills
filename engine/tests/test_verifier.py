"""Tests for verification system."""

import json
import tempfile
from pathlib import Path
from verifier import Verifier, VerificationResult, VerificationReport, verify_changes


def test_verification_result():
    """Test VerificationResult dataclass."""
    result = VerificationResult(
        status="passed",
        tool="linter",
        errors=[],
        warnings=["unused variable"],
    )
    
    assert result.status == "passed"
    assert result.tool == "linter"
    assert len(result.warnings) == 1
    
    result_dict = result.to_dict()
    assert result_dict["status"] == "passed"
    assert result_dict["tool"] == "linter"


def test_verification_report():
    """Test VerificationReport dataclass."""
    result = VerificationResult(status="passed", tool="linter")
    report = VerificationReport(
        project_path="/tmp/project",
        timestamp="2025-05-30T00:00:00",
        lint_result=result,
    )
    
    assert report.lint_result.status == "passed"
    
    report_dict = report.to_dict()
    assert report_dict["project_path"] == "/tmp/project"
    assert report_dict["lint"]["status"] == "passed"


def test_verifier_initialization():
    """Test Verifier initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        verifier = Verifier(tmpdir)
        assert verifier.project_path == Path(tmpdir)
        assert verifier.linter is not None
        assert verifier.type_checker is not None
        assert verifier.test_runner is not None


def test_determine_status_passed():
    """Test status determination when all checks pass."""
    with tempfile.TemporaryDirectory() as tmpdir:
        verifier = Verifier(tmpdir)
        
        report = VerificationReport(
            project_path=tmpdir,
            timestamp="2025-05-30T00:00:00",
            lint_result=VerificationResult(status="passed", tool="linter"),
            type_check_result=VerificationResult(status="passed", tool="type_checker"),
        )
        
        status = verifier._determine_status(report)
        assert status == "passed"


def test_determine_status_warning():
    """Test status determination with warnings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        verifier = Verifier(tmpdir)
        
        report = VerificationReport(
            project_path=tmpdir,
            timestamp="2025-05-30T00:00:00",
            lint_result=VerificationResult(status="warning", tool="linter"),
            type_check_result=VerificationResult(status="passed", tool="type_checker"),
        )
        
        status = verifier._determine_status(report)
        assert status == "warning"


def test_determine_status_failed():
    """Test status determination when checks fail."""
    with tempfile.TemporaryDirectory() as tmpdir:
        verifier = Verifier(tmpdir)
        
        report = VerificationReport(
            project_path=tmpdir,
            timestamp="2025-05-30T00:00:00",
            lint_result=VerificationResult(status="failed", tool="linter"),
            type_check_result=VerificationResult(status="passed", tool="type_checker"),
        )
        
        status = verifier._determine_status(report)
        assert status == "failed"


def test_save_report():
    """Test saving verification report."""
    with tempfile.TemporaryDirectory() as tmpdir:
        verifier = Verifier(tmpdir)
        
        report = VerificationReport(
            project_path=tmpdir,
            timestamp="2025-05-30T00:00:00",
            lint_result=VerificationResult(status="passed", tool="linter"),
        )
        
        output_path = Path(tmpdir) / "verification_report.json"
        verifier.save_report(report, str(output_path))
        
        assert output_path.exists()
        
        with open(output_path) as f:
            saved = json.load(f)
        
        assert saved["project_path"] == tmpdir


def test_verify_changes():
    """Test verification of changed files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        report = verify_changes(tmpdir, ["test.js"])
        
        assert report.project_path == tmpdir
        assert report.lint_result is not None


if __name__ == "__main__":
    # Run tests
    tests = [
        test_verification_result,
        test_verification_report,
        test_verifier_initialization,
        test_determine_status_passed,
        test_determine_status_warning,
        test_determine_status_failed,
        test_save_report,
        test_verify_changes,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
