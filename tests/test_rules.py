"""
Tests for the cryptographic rules and knowledge base.
"""

import pytest
from pqc_migration_auditor.analysis.rules import (
    CryptoKnowledgeBase,
    RiskLevel,
    AlgorithmCategory,
)


class TestCryptoKnowledgeBase:
    """Test cases for the CryptoKnowledgeBase class."""

    def test_vulnerable_algorithms_defined(self):
        """Test that vulnerable algorithms are defined."""
        kb = CryptoKnowledgeBase()

        assert "RSA" in kb.VULNERABLE_ALGORITHMS
        assert "DSA" in kb.VULNERABLE_ALGORITHMS
        assert "ECDSA" in kb.VULNERABLE_ALGORITHMS
        assert "ECDH" in kb.VULNERABLE_ALGORITHMS

    def test_pqc_algorithms_defined(self):
        """Test that PQC algorithms are defined."""
        kb = CryptoKnowledgeBase()

        assert "CRYSTALS-Kyber" in kb.PQC_ALGORITHMS
        assert "CRYSTALS-Dilithium" in kb.PQC_ALGORITHMS
        assert "SPHINCS+" in kb.PQC_ALGORITHMS

    def test_get_algorithm_info_rsa(self):
        """Test getting information about RSA."""
        kb = CryptoKnowledgeBase()
        info = kb.get_algorithm_info("RSA")

        assert info is not None
        assert info.name == "RSA"
        assert info.risk_level == RiskLevel.QUANTUM_VULNERABLE
        assert info.category == AlgorithmCategory.KEY_EXCHANGE

    def test_get_algorithm_info_ecdsa(self):
        """Test getting information about ECDSA."""
        kb = CryptoKnowledgeBase()
        info = kb.get_algorithm_info("ECDSA")

        assert info is not None
        assert info.risk_level == RiskLevel.QUANTUM_VULNERABLE
        assert info.category == AlgorithmCategory.DIGITAL_SIGNATURE

    def test_get_pqc_recommendation_rsa(self):
        """Test getting PQC recommendation for RSA."""
        kb = CryptoKnowledgeBase()
        rec = kb.get_pqc_recommendation("RSA")

        assert rec is not None
        assert "vulnerable_algorithm" in rec
        assert rec["vulnerable_algorithm"] == "RSA"
        assert "primary_replacement" in rec
        assert "ML-KEM" in rec["primary_replacement"] or "Kyber" in rec["primary_replacement"]
        assert "migration_guidance" in rec
        assert len(rec["migration_guidance"]) > 0

    def test_get_pqc_recommendation_ecdsa(self):
        """Test getting PQC recommendation for ECDSA."""
        kb = CryptoKnowledgeBase()
        rec = kb.get_pqc_recommendation("ECDSA")

        assert rec is not None
        assert "ML-DSA" in rec["primary_replacement"] or "Dilithium" in rec["primary_replacement"]

    def test_code_patterns_defined(self):
        """Test that code patterns are defined."""
        kb = CryptoKnowledgeBase()

        assert len(kb.CODE_PATTERNS) > 0
        assert any("rsa" in pattern.lower() for pattern in kb.CODE_PATTERNS.keys())
        assert any("ecdsa" in pattern.lower() or "ec" in pattern.lower() for pattern in kb.CODE_PATTERNS.keys())

    def test_migration_checklist(self):
        """Test migration checklist."""
        kb = CryptoKnowledgeBase()
        checklist = kb.get_migration_checklist()

        assert len(checklist) > 0

        # Each phase should have a name and tasks
        for phase in checklist:
            assert "phase" in phase
            assert "tasks" in phase
            assert len(phase["tasks"]) > 0
            assert all(isinstance(task, str) for task in phase["tasks"])

    def test_unknown_algorithm(self):
        """Test handling of unknown algorithm."""
        kb = CryptoKnowledgeBase()

        info = kb.get_algorithm_info("NONEXISTENT_ALGO")
        assert info is None

        rec = kb.get_pqc_recommendation("NONEXISTENT_ALGO")
        assert "algorithm" in rec or "vulnerable_algorithm" in rec
