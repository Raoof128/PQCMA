"""
Tests for the recommendation engine.
"""

import pytest
from pqc_migration_auditor.analysis.recommendations import (
    RecommendationEngine,
    Finding,
)
from pqc_migration_auditor.analysis.rules import RiskLevel


class TestRecommendationEngine:
    """Test cases for the RecommendationEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = RecommendationEngine()

    def test_engine_initialization(self):
        """Test that engine initializes correctly."""
        assert self.engine is not None
        assert self.engine.knowledge_base is not None

    def test_analyze_rsa_finding(self):
        """Test recommendation for RSA finding."""
        finding = Finding(
            finding_type="CODE",
            location="test.py:10",
            algorithm="RSA",
            key_size=2048,
            risk_level=RiskLevel.QUANTUM_VULNERABLE.value,
            details="RSA key generation"
        )

        recommendation = self.engine.analyze_finding(finding)

        assert recommendation is not None
        assert recommendation.vulnerable_algorithm == "RSA"
        assert "ML-KEM" in recommendation.primary_replacement or "Kyber" in recommendation.primary_replacement
        assert recommendation.risk_level == RiskLevel.QUANTUM_VULNERABLE.value
        assert len(recommendation.migration_guidance) > 0

    def test_analyze_ecdsa_finding(self):
        """Test recommendation for ECDSA finding."""
        finding = Finding(
            finding_type="CODE",
            location="test.py:20",
            algorithm="ECDSA",
            risk_level=RiskLevel.QUANTUM_VULNERABLE.value,
        )

        recommendation = self.engine.analyze_finding(finding)

        assert recommendation is not None
        assert "ML-DSA" in recommendation.primary_replacement or "Dilithium" in recommendation.primary_replacement

    def test_generate_report_summary(self):
        """Test report summary generation."""
        findings = [
            Finding(
                finding_type="CODE",
                location="file1.py:10",
                algorithm="RSA",
                risk_level=RiskLevel.QUANTUM_VULNERABLE.value
            ),
            Finding(
                finding_type="CODE",
                location="file2.py:20",
                algorithm="ECDSA",
                risk_level=RiskLevel.QUANTUM_VULNERABLE.value
            ),
            Finding(
                finding_type="PCAP",
                location="capture.pcap:100",
                algorithm="RSA",
                risk_level=RiskLevel.QUANTUM_VULNERABLE.value
            ),
        ]

        recommendations = [self.engine.analyze_finding(f) for f in findings]
        summary = self.engine.generate_report_summary(findings, recommendations)

        assert summary["total_findings"] == 3
        assert summary["findings_by_type"]["CODE"] == 2
        assert summary["findings_by_type"]["PCAP"] == 1
        assert summary["critical_count"] == 3
        assert "RSA" in summary["algorithms_detected"]
        assert "ECDSA" in summary["algorithms_detected"]

    def test_get_migration_checklist(self):
        """Test migration checklist retrieval."""
        checklist = self.engine.get_migration_checklist()

        assert len(checklist) > 0
        assert all("phase" in item for item in checklist)
        assert all("tasks" in item for item in checklist)

        # Check for expected phases
        phases = [item["phase"] for item in checklist]
        assert any("Discovery" in phase or "Inventory" in phase for phase in phases)
        assert any("Risk" in phase for phase in phases)
        assert any("Planning" in phase or "Architecture" in phase for phase in phases)

    def test_unknown_algorithm(self):
        """Test handling of unknown algorithm."""
        finding = Finding(
            finding_type="CODE",
            location="test.py:30",
            algorithm="UNKNOWN_ALGO",
            risk_level=RiskLevel.UNKNOWN.value
        )

        recommendation = self.engine.analyze_finding(finding)

        assert recommendation is not None
        assert "Manual review" in recommendation.primary_replacement or "Unknown" in recommendation.vulnerable_algorithm
