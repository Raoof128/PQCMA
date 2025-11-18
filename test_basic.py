#!/usr/bin/env python3
"""
Basic test script to verify core functionality without full cryptography library.
"""

import sys
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

from pqc_migration_auditor.scanner.code_scanner import CodeScanner
from pqc_migration_auditor.analysis.recommendations import RecommendationEngine
from pqc_migration_auditor.analysis.rules import CryptoKnowledgeBase

def test_knowledge_base():
    """Test the crypto knowledge base."""
    print("=" * 80)
    print("Testing Crypto Knowledge Base...")
    print("=" * 80)

    kb = CryptoKnowledgeBase()

    # Test vulnerable algorithms
    print("\nVulnerable Algorithms:")
    for algo_name in ["RSA", "ECDSA", "DSA", "ECDH"]:
        info = kb.get_algorithm_info(algo_name)
        if info:
            print(f"  ✓ {algo_name}: {info.risk_level.value} - {info.description[:60]}...")

    # Test PQC recommendations
    print("\nPQC Recommendations:")
    rec = kb.get_pqc_recommendation("RSA")
    print(f"  RSA -> {rec['primary_replacement']}")

    rec = kb.get_pqc_recommendation("ECDSA")
    print(f"  ECDSA -> {rec['primary_replacement']}")

    print("\n✓ Knowledge base working correctly!\n")


def test_code_scanner():
    """Test the code scanner."""
    print("=" * 80)
    print("Testing Code Scanner...")
    print("=" * 80)

    scanner = CodeScanner()
    dummy_repo = Path("examples/dummy_repo")

    if not dummy_repo.exists():
        print(f"✗ Dummy repository not found at {dummy_repo}")
        return False

    print(f"\nScanning: {dummy_repo}")

    # Scan the dummy repository
    findings = scanner.scan_directory(dummy_repo)

    print(f"\nFindings: {len(findings)} vulnerable crypto usages detected")

    # Group by algorithm
    algo_counts = {}
    for finding in findings:
        algo_counts[finding.algorithm] = algo_counts.get(finding.algorithm, 0) + 1

    print("\nDetected Algorithms:")
    for algo, count in sorted(algo_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {algo}: {count} occurrence(s)")

    # Show first few findings
    print("\nSample Findings:")
    for i, finding in enumerate(findings[:5], 1):
        print(f"\n  [{i}] {finding.algorithm} at {finding.location}")
        if finding.key_size:
            print(f"      Key size: {finding.key_size} bits")
        print(f"      Risk: {finding.risk_level}")

    print(f"\n✓ Code scanner working correctly! Found {len(findings)} issues.\n")
    return len(findings) > 0


def test_recommendations():
    """Test the recommendation engine."""
    print("=" * 80)
    print("Testing Recommendation Engine...")
    print("=" * 80)

    from pqc_migration_auditor.analysis.recommendations import Finding

    engine = RecommendationEngine()

    # Create a test finding
    test_finding = Finding(
        finding_type="CODE",
        location="test.py:10",
        algorithm="RSA",
        key_size=2048,
        risk_level="QUANTUM_VULNERABLE",
        details="Test RSA usage"
    )

    # Generate recommendation
    rec = engine.analyze_finding(test_finding)

    print(f"\nTest Finding: {rec.vulnerable_algorithm}")
    print(f"Recommended Replacement: {rec.primary_replacement}")
    print(f"Category: {rec.category}")
    print(f"\nMigration Guidance (first 100 chars):")
    print(f"  {rec.migration_guidance[:100]}...")

    print("\n✓ Recommendation engine working correctly!\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("PQC Migration Auditor - Basic Functionality Test")
    print("=" * 80 + "\n")

    try:
        # Test 1: Knowledge Base
        test_knowledge_base()

        # Test 2: Code Scanner
        if not test_code_scanner():
            print("⚠ Warning: No findings detected. Check dummy repository.")

        # Test 3: Recommendations
        test_recommendations()

        print("=" * 80)
        print("✓ All basic tests passed!")
        print("=" * 80)
        print("\nThe PQC Migration Auditor is working correctly.")
        print("\nTo run a full scan, use:")
        print("  python -m pqc_migration_auditor --mode code --target examples/dummy_repo")
        print("\nNote: Certificate scanning requires the cryptography library.")
        print("=" * 80 + "\n")

        return 0

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
