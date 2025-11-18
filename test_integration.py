#!/usr/bin/env python3
"""
Comprehensive integration test for PQC Migration Auditor.
Tests all major functionality including CLI, scanning, and reporting.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

from pqc_migration_auditor.cli import main


def test_cli_code_scan():
    """Test CLI code scanning mode."""
    print("="*80)
    print("Test 1: CLI Code Scan")
    print("="*80)

    # Run code scan with quiet mode (no console output)
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "test_report.json"
        html_path = Path(tmpdir) / "test_report.html"

        args = [
            "--mode", "code",
            "--target", "examples/dummy_repo",
            "--output-json", str(json_path),
            "--output-html", str(html_path),
            "--quiet"
        ]

        print(f"Running: pqc-auditor {' '.join(args)}")
        exit_code = main(args)

        print(f"Exit code: {exit_code}")

        # Should find vulnerabilities (exit code 1)
        assert exit_code == 1, f"Expected exit code 1, got {exit_code}"

        # Check JSON report was created
        assert json_path.exists(), "JSON report not created"
        print(f"✓ JSON report created: {json_path}")

        # Check HTML report was created
        assert html_path.exists(), "HTML report not created"
        print(f"✓ HTML report created: {html_path}")

        # Validate JSON content
        with open(json_path) as f:
            report = json.load(f)

        assert "metadata" in report, "Missing metadata in JSON report"
        assert "findings" in report, "Missing findings in JSON report"
        assert "recommendations" in report, "Missing recommendations in JSON report"
        assert "summary" in report, "Missing summary in JSON report"

        findings_count = len(report["findings"])
        print(f"✓ Found {findings_count} vulnerabilities in JSON report")

        assert findings_count > 0, "No findings in report"

        # Check summary
        summary = report["summary"]
        assert summary["total_findings"] == findings_count
        print(f"✓ Summary correct: {summary['total_findings']} findings")

        # Validate HTML content
        html_content = html_path.read_text()
        assert "<!DOCTYPE html>" in html_content, "Invalid HTML report"
        assert "Post-Quantum" in html_content, "HTML report missing content"
        print("✓ HTML report contains valid content")

    print("\n✓ Test 1 passed!\n")
    return True


def test_cli_with_console_output():
    """Test CLI with console output."""
    print("="*80)
    print("Test 2: CLI with Console Output")
    print("="*80)

    args = [
        "--mode", "code",
        "--target", "examples/dummy_repo"
    ]

    print(f"Running: pqc-auditor {' '.join(args)}")
    exit_code = main(args)

    print(f"\nExit code: {exit_code}")
    assert exit_code == 1, f"Expected exit code 1, got {exit_code}"

    print("\n✓ Test 2 passed!\n")
    return True


def test_cli_empty_directory():
    """Test CLI on empty directory."""
    print("="*80)
    print("Test 3: CLI on Empty Directory")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        args = [
            "--mode", "code",
            "--target", tmpdir,
            "--quiet"
        ]

        print(f"Running scan on empty directory: {tmpdir}")
        exit_code = main(args)

        print(f"Exit code: {exit_code}")
        # Should exit 0 (no vulnerabilities found)
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"

    print("\n✓ Test 3 passed!\n")
    return True


def test_cli_nonexistent_path():
    """Test CLI error handling for nonexistent path."""
    print("="*80)
    print("Test 4: CLI Error Handling - Nonexistent Path")
    print("="*80)

    args = [
        "--mode", "code",
        "--target", "/nonexistent/path/that/does/not/exist",
        "--quiet"
    ]

    print("Running scan on nonexistent path...")
    exit_code = main(args)

    print(f"Exit code: {exit_code}")
    # Should exit with error (1)
    assert exit_code == 1, f"Expected exit code 1, got {exit_code}"

    print("\n✓ Test 4 passed!\n")
    return True


def test_cli_verbose_mode():
    """Test CLI verbose mode."""
    print("="*80)
    print("Test 5: CLI Verbose Mode")
    print("="*80)

    args = [
        "--mode", "code",
        "--target", "examples/dummy_repo",
        "--verbose",
        "--quiet"  # Quiet for console, but verbose logging should still work
    ]

    print("Running with verbose logging...")
    exit_code = main(args)

    print(f"Exit code: {exit_code}")
    assert exit_code == 1, f"Expected exit code 1, got {exit_code}"

    print("\n✓ Test 5 passed!\n")
    return True


def test_json_report_structure():
    """Test detailed JSON report structure."""
    print("="*80)
    print("Test 6: JSON Report Structure Validation")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "detailed_report.json"

        args = [
            "--mode", "code",
            "--target", "examples/dummy_repo",
            "--output-json", str(json_path),
            "--quiet"
        ]

        main(args)

        with open(json_path) as f:
            report = json.load(f)

        # Validate metadata
        metadata = report["metadata"]
        assert metadata["tool"] == "PQC Migration Auditor"
        assert "version" in metadata
        assert "scan_time" in metadata
        print("✓ Metadata valid")

        # Validate findings structure
        if report["findings"]:
            finding = report["findings"][0]
            assert "type" in finding
            assert "location" in finding
            assert "algorithm" in finding
            assert "risk_level" in finding
            print("✓ Finding structure valid")

        # Validate recommendations
        if report["recommendations"]:
            rec = report["recommendations"][0]
            assert "vulnerable_algorithm" in rec
            assert "primary_replacement" in rec
            assert "migration_guidance" in rec
            assert "references" in rec
            print("✓ Recommendation structure valid")

        # Validate migration checklist
        checklist = report["migration_checklist"]
        assert len(checklist) > 0
        assert "phase" in checklist[0]
        assert "tasks" in checklist[0]
        print("✓ Migration checklist valid")

    print("\n✓ Test 6 passed!\n")
    return True


def test_finding_deduplication():
    """Test that findings are properly deduplicated."""
    print("="*80)
    print("Test 7: Finding Deduplication")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "dedup_test.json"

        args = [
            "--mode", "code",
            "--target", "examples/dummy_repo",
            "--output-json", str(json_path),
            "--quiet"
        ]

        main(args)

        with open(json_path) as f:
            report = json.load(f)

        findings = report["findings"]

        # Check for duplicate findings (same location + algorithm)
        seen = set()
        duplicates = []

        for finding in findings:
            key = (finding["location"], finding["algorithm"])
            if key in seen:
                duplicates.append(key)
            seen.add(key)

        assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate findings"
        print(f"✓ No duplicate findings detected (total: {len(findings)})")

    print("\n✓ Test 7 passed!\n")
    return True


def main_test():
    """Run all integration tests."""
    print("\n" + "="*80)
    print("PQC Migration Auditor - Comprehensive Integration Tests")
    print("="*80 + "\n")

    tests = [
        ("CLI Code Scan", test_cli_code_scan),
        ("CLI Console Output", test_cli_with_console_output),
        ("CLI Empty Directory", test_cli_empty_directory),
        ("CLI Error Handling", test_cli_nonexistent_path),
        ("CLI Verbose Mode", test_cli_verbose_mode),
        ("JSON Report Structure", test_json_report_structure),
        ("Finding Deduplication", test_finding_deduplication),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ {test_name} FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"\n✗ {test_name} ERROR: {e}\n")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*80)
    print(f"Integration Test Results: {passed} passed, {failed} failed")
    print("="*80 + "\n")

    if failed == 0:
        print("✓ All integration tests passed!")
        return 0
    else:
        print(f"✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main_test())
