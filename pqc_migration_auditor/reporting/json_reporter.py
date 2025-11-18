"""
JSON reporter for generating machine-readable audit reports.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from ..analysis.recommendations import Finding, Recommendation
from ..utils.logging_utils import get_logger


logger = get_logger(__name__)


class JSONReporter:
    """
    Generates JSON-format audit reports.
    """

    def __init__(self, tool_version: str = "1.0.0"):
        self.tool_version = tool_version

    def generate_report(
        self,
        findings: List[Finding],
        recommendations: List[Recommendation],
        summary: Dict[str, Any],
        scan_metadata: Dict[str, Any],
        migration_checklist: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a JSON report.

        Args:
            findings: List of detected vulnerabilities
            recommendations: List of PQC recommendations
            summary: Summary statistics
            scan_metadata: Metadata about the scan
            migration_checklist: PQC migration checklist

        Returns:
            Dictionary suitable for JSON serialization
        """
        report = {
            "metadata": {
                "tool": "PQC Migration Auditor",
                "version": self.tool_version,
                "scan_time": datetime.now().isoformat(),
                "mode": scan_metadata.get("mode", "unknown"),
                "target": scan_metadata.get("target", "unknown")
            },
            "summary": summary,
            "findings": [self._serialize_finding(f) for f in findings],
            "recommendations": [self._serialize_recommendation(r) for r in recommendations],
            "migration_checklist": migration_checklist
        }

        return report

    def write_report(
        self,
        report: Dict[str, Any],
        output_path: Path
    ) -> None:
        """
        Write JSON report to file.

        Args:
            report: Report dictionary
            output_path: Path to output file
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"JSON report written to: {output_path}")
        except Exception as e:
            logger.error(f"Error writing JSON report: {e}")

    def _serialize_finding(self, finding: Finding) -> Dict[str, Any]:
        """Serialize a Finding to a dictionary."""
        return {
            "type": finding.finding_type,
            "location": finding.location,
            "algorithm": finding.algorithm,
            "key_size": finding.key_size,
            "risk_level": finding.risk_level,
            "details": finding.details,
            "raw_data": finding.raw_data
        }

    def _serialize_recommendation(self, rec: Recommendation) -> Dict[str, Any]:
        """Serialize a Recommendation to a dictionary."""
        return {
            "finding": self._serialize_finding(rec.finding),
            "vulnerable_algorithm": rec.vulnerable_algorithm,
            "category": rec.category,
            "risk_level": rec.risk_level,
            "primary_replacement": rec.primary_replacement,
            "alternative_replacements": rec.alternative_replacements,
            "migration_guidance": rec.migration_guidance,
            "references": rec.references
        }
