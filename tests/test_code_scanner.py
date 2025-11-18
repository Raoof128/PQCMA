"""
Tests for the code scanner module.
"""

import pytest
from pathlib import Path
from pqc_migration_auditor.scanner.code_scanner import CodeScanner
from pqc_migration_auditor.analysis.rules import RiskLevel


class TestCodeScanner:
    """Test cases for the CodeScanner class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scanner = CodeScanner()

    def test_scanner_initialization(self):
        """Test that scanner initializes correctly."""
        assert self.scanner is not None
        assert self.scanner.knowledge_base is not None
        assert len(self.scanner.patterns) > 0

    def test_scan_line_rsa(self):
        """Test detection of RSA usage in code."""
        test_line = "from cryptography.hazmat.primitives.asymmetric import rsa"
        findings = self.scanner.scan_line(Path("test.py"), 1, test_line)

        assert len(findings) > 0
        assert findings[0].algorithm == "RSA"
        assert findings[0].risk_level == RiskLevel.QUANTUM_VULNERABLE.value

    def test_scan_line_ecdsa(self):
        """Test detection of ECDSA usage."""
        test_line = "from cryptography.hazmat.primitives.asymmetric import ec"
        findings = self.scanner.scan_line(Path("test.py"), 1, test_line)

        assert len(findings) > 0
        assert findings[0].algorithm == "ECDSA"

    def test_scan_line_key_size_extraction(self):
        """Test extraction of key size from code."""
        test_line = "private_key = rsa.generate_private_key(key_size=2048)"
        findings = self.scanner.scan_line(Path("test.py"), 1, test_line)

        assert len(findings) > 0
        assert findings[0].key_size == 2048

    def test_scan_line_no_match(self):
        """Test that non-crypto code produces no findings."""
        test_line = "print('Hello, world!')"
        findings = self.scanner.scan_line(Path("test.py"), 1, test_line)

        assert len(findings) == 0

    def test_scan_directory_dummy_repo(self):
        """Test scanning the dummy repository."""
        dummy_repo_path = Path(__file__).parent.parent / "examples" / "dummy_repo"

        if dummy_repo_path.exists():
            findings = self.scanner.scan_directory(dummy_repo_path)

            # Should find multiple vulnerable crypto uses
            assert len(findings) > 0

            # Should detect RSA
            rsa_findings = [f for f in findings if f.algorithm == "RSA"]
            assert len(rsa_findings) > 0

            # Should detect ECDSA
            ecdsa_findings = [f for f in findings if f.algorithm == "ECDSA"]
            assert len(ecdsa_findings) > 0

    def test_scan_nonexistent_directory(self):
        """Test scanning a directory that doesn't exist."""
        findings = self.scanner.scan_directory(Path("/nonexistent/path"))
        assert findings == []

    def test_extract_key_size_various_formats(self):
        """Test key size extraction from various formats."""
        # Direct key_size parameter
        assert self.scanner._extract_key_size("key_size=2048") == 2048

        # Bit notation
        assert self.scanner._extract_key_size("2048-bit RSA key") == 2048

        # RSA notation
        assert self.scanner._extract_key_size("RSA-4096") == 4096

        # No key size
        assert self.scanner._extract_key_size("just some text") is None
