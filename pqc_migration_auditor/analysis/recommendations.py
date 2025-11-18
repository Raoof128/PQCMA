"""
Recommendation engine for PQC migration guidance.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from .rules import CryptoKnowledgeBase, RiskLevel


@dataclass
class Finding:
    """Represents a detected cryptographic vulnerability."""
    finding_type: str  # CODE, PCAP, CERT
    location: str  # File path, line number, or stream ID
    algorithm: str
    key_size: Optional[int] = None
    risk_level: str = RiskLevel.UNKNOWN.value
    details: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class Recommendation:
    """PQC migration recommendation for a finding."""
    finding: Finding
    vulnerable_algorithm: str
    category: str
    risk_level: str
    primary_replacement: str
    alternative_replacements: List[str]
    migration_guidance: str
    references: List[str]


class RecommendationEngine:
    """
    Generates PQC migration recommendations based on detected vulnerabilities.
    """

    def __init__(self):
        self.knowledge_base = CryptoKnowledgeBase()

    def analyze_finding(self, finding: Finding) -> Recommendation:
        """
        Analyze a finding and generate a PQC migration recommendation.

        Args:
            finding: A detected cryptographic vulnerability

        Returns:
            A recommendation with PQC migration guidance
        """
        # Get PQC recommendation from knowledge base
        pqc_rec = self.knowledge_base.get_pqc_recommendation(finding.algorithm)

        return Recommendation(
            finding=finding,
            vulnerable_algorithm=pqc_rec.get("vulnerable_algorithm", finding.algorithm),
            category=pqc_rec.get("category", "UNKNOWN"),
            risk_level=pqc_rec.get("risk_level", RiskLevel.UNKNOWN.value),
            primary_replacement=pqc_rec.get("primary_replacement", "Manual review required"),
            alternative_replacements=pqc_rec.get("alternative_replacements", []),
            migration_guidance=pqc_rec.get("migration_guidance", "Consult ASD PQC guidance"),
            references=pqc_rec.get("references", [])
        )

    def generate_report_summary(
        self,
        findings: List[Finding],
        recommendations: List[Recommendation]
    ) -> Dict[str, Any]:
        """
        Generate a summary report of findings and recommendations.

        Args:
            findings: List of detected vulnerabilities
            recommendations: List of PQC recommendations

        Returns:
            Dictionary containing report summary statistics
        """
        # Count findings by type
        finding_counts = {
            "CODE": 0,
            "PCAP": 0,
            "CERT": 0
        }

        # Count findings by risk level
        risk_counts = {
            RiskLevel.QUANTUM_VULNERABLE.value: 0,
            RiskLevel.TRANSITIONAL.value: 0,
            RiskLevel.PQC_SAFE.value: 0,
            RiskLevel.UNKNOWN.value: 0
        }

        # Count algorithms detected
        algorithm_counts: Dict[str, int] = {}

        for finding in findings:
            finding_counts[finding.finding_type] = finding_counts.get(finding.finding_type, 0) + 1
            risk_counts[finding.risk_level] = risk_counts.get(finding.risk_level, 0) + 1
            algorithm_counts[finding.algorithm] = algorithm_counts.get(finding.algorithm, 0) + 1

        return {
            "total_findings": len(findings),
            "findings_by_type": finding_counts,
            "findings_by_risk": risk_counts,
            "algorithms_detected": algorithm_counts,
            "recommendations_generated": len(recommendations),
            "critical_count": risk_counts.get(RiskLevel.QUANTUM_VULNERABLE.value, 0)
        }

    def get_migration_checklist(self) -> List[Dict[str, Any]]:
        """
        Get the PQC migration checklist from the knowledge base.

        Returns:
            List of migration phases with tasks
        """
        return self.knowledge_base.get_migration_checklist()
