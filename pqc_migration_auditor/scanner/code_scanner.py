"""
Code scanner for detecting quantum-vulnerable cryptographic usage in source files.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..analysis.recommendations import Finding
from ..analysis.rules import CryptoKnowledgeBase, RiskLevel
from ..utils.logging_utils import get_logger
from ..utils.file_utils import find_scannable_files, safe_read_file, is_certificate_file


logger = get_logger(__name__)


class CodeScanner:
    """
    Scans source code files for quantum-vulnerable cryptographic usage.
    """

    def __init__(self):
        self.knowledge_base = CryptoKnowledgeBase()
        self.patterns = self.knowledge_base.CODE_PATTERNS

    def scan_directory(self, directory_path: Path) -> List[Finding]:
        """
        Scan a directory for vulnerable cryptographic usage.

        Args:
            directory_path: Path to the directory to scan

        Returns:
            List of findings
        """
        logger.info(f"Scanning directory: {directory_path}")

        if not directory_path.exists():
            logger.error(f"Directory does not exist: {directory_path}")
            return []

        if not directory_path.is_dir():
            logger.error(f"Path is not a directory: {directory_path}")
            return []

        findings: List[Finding] = []

        # Find all scannable files
        scannable_files = find_scannable_files(directory_path, include_certs=False)
        logger.info(f"Found {len(scannable_files)} files to scan")

        for file_path in scannable_files:
            file_findings = self.scan_file(file_path)
            findings.extend(file_findings)

        logger.info(f"Code scan complete: {len(findings)} findings")
        return findings

    def scan_file(self, file_path: Path) -> List[Finding]:
        """
        Scan a single file for vulnerable cryptographic usage.

        Args:
            file_path: Path to the file to scan

        Returns:
            List of findings in this file
        """
        findings: List[Finding] = []

        # Skip certificate files (handled by cert_scanner)
        if is_certificate_file(file_path):
            return findings

        # Read file contents
        content = safe_read_file(file_path)
        if content is None:
            logger.debug(f"Skipping file (too large or unreadable): {file_path}")
            return findings

        # Scan line by line
        lines = content.split('\n')
        for line_num, line in enumerate(lines, start=1):
            line_findings = self.scan_line(file_path, line_num, line)
            findings.extend(line_findings)

        return findings

    def scan_line(self, file_path: Path, line_num: int, line: str) -> List[Finding]:
        """
        Scan a single line for vulnerable cryptographic patterns.

        Args:
            file_path: Path to the file being scanned
            line_num: Line number
            line: Line content

        Returns:
            List of findings in this line
        """
        findings: List[Finding] = []

        for pattern, algorithm in self.patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                # Determine risk level
                algo_info = self.knowledge_base.get_algorithm_info(algorithm)
                risk_level = algo_info.risk_level.value if algo_info else RiskLevel.UNKNOWN.value

                # Extract key size if present
                key_size = self._extract_key_size(line)

                finding = Finding(
                    finding_type="CODE",
                    location=f"{file_path}:{line_num}",
                    algorithm=algorithm,
                    key_size=key_size,
                    risk_level=risk_level,
                    details=line.strip(),
                    raw_data={
                        "file": str(file_path),
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "pattern_matched": pattern
                    }
                )

                findings.append(finding)
                logger.debug(f"Found {algorithm} at {file_path}:{line_num}")

        return findings

    def _extract_key_size(self, line: str) -> Optional[int]:
        """
        Extract key size from a line if present.

        Args:
            line: Line content

        Returns:
            Key size in bits, or None if not found
        """
        # Common key size patterns
        key_size_patterns = [
            r'key_size\s*=\s*(\d+)',
            r'(\d+)[-\s]?bit',
            r'rsa[-_]?(\d+)',
        ]

        for pattern in key_size_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue

        return None
