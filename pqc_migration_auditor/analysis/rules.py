"""
Cryptographic vulnerability rules and PQC knowledge base.

This module contains the detection rules for quantum-vulnerable algorithms
and mappings to NIST/ASD-aligned post-quantum replacements.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class RiskLevel(Enum):
    """Risk classification for cryptographic algorithms."""
    QUANTUM_VULNERABLE = "QUANTUM_VULNERABLE"
    TRANSITIONAL = "TRANSITIONAL"
    PQC_SAFE = "PQC_SAFE"
    UNKNOWN = "UNKNOWN"


class AlgorithmCategory(Enum):
    """Categories of cryptographic algorithms."""
    KEY_EXCHANGE = "KEY_EXCHANGE"
    DIGITAL_SIGNATURE = "DIGITAL_SIGNATURE"
    ENCRYPTION = "ENCRYPTION"
    HASH = "HASH"


@dataclass
class VulnerableAlgorithm:
    """Definition of a quantum-vulnerable algorithm."""
    name: str
    category: AlgorithmCategory
    risk_level: RiskLevel
    description: str
    key_sizes: Optional[List[int]] = None


@dataclass
class PQCAlgorithm:
    """Definition of a post-quantum cryptographic algorithm."""
    name: str
    category: AlgorithmCategory
    nist_status: str
    description: str
    security_level: str


class CryptoKnowledgeBase:
    """
    Knowledge base of cryptographic algorithms and PQC recommendations.

    Aligned with:
    - NIST PQC Standardization (FIPS 203, 204, 205)
    - ASD's Quantum Computing and Post-Quantum Cryptography guidance
    """

    # Quantum-vulnerable algorithms
    VULNERABLE_ALGORITHMS = {
        # Public key encryption / Key Exchange
        "RSA": VulnerableAlgorithm(
            name="RSA",
            category=AlgorithmCategory.KEY_EXCHANGE,
            risk_level=RiskLevel.QUANTUM_VULNERABLE,
            description="RSA is vulnerable to Shor's algorithm on quantum computers",
            key_sizes=[1024, 2048, 3072, 4096]
        ),
        "DSA": VulnerableAlgorithm(
            name="DSA",
            category=AlgorithmCategory.DIGITAL_SIGNATURE,
            risk_level=RiskLevel.QUANTUM_VULNERABLE,
            description="DSA is vulnerable to Shor's algorithm on quantum computers"
        ),
        "ECDSA": VulnerableAlgorithm(
            name="ECDSA",
            category=AlgorithmCategory.DIGITAL_SIGNATURE,
            risk_level=RiskLevel.QUANTUM_VULNERABLE,
            description="ECDSA is vulnerable to Shor's algorithm on quantum computers"
        ),
        "ECDH": VulnerableAlgorithm(
            name="ECDH",
            category=AlgorithmCategory.KEY_EXCHANGE,
            risk_level=RiskLevel.QUANTUM_VULNERABLE,
            description="ECDH is vulnerable to Shor's algorithm on quantum computers"
        ),
        "DH": VulnerableAlgorithm(
            name="DH",
            category=AlgorithmCategory.KEY_EXCHANGE,
            risk_level=RiskLevel.QUANTUM_VULNERABLE,
            description="Diffie-Hellman is vulnerable to Shor's algorithm on quantum computers"
        ),
        "Ed25519": VulnerableAlgorithm(
            name="Ed25519",
            category=AlgorithmCategory.DIGITAL_SIGNATURE,
            risk_level=RiskLevel.QUANTUM_VULNERABLE,
            description="EdDSA/Ed25519 is vulnerable to Shor's algorithm on quantum computers"
        ),
        "secp256r1": VulnerableAlgorithm(
            name="secp256r1",
            category=AlgorithmCategory.KEY_EXCHANGE,
            risk_level=RiskLevel.QUANTUM_VULNERABLE,
            description="NIST P-256 curve is vulnerable to Shor's algorithm"
        ),
        "secp384r1": VulnerableAlgorithm(
            name="secp384r1",
            category=AlgorithmCategory.KEY_EXCHANGE,
            risk_level=RiskLevel.QUANTUM_VULNERABLE,
            description="NIST P-384 curve is vulnerable to Shor's algorithm"
        ),
        "prime256v1": VulnerableAlgorithm(
            name="prime256v1",
            category=AlgorithmCategory.KEY_EXCHANGE,
            risk_level=RiskLevel.QUANTUM_VULNERABLE,
            description="P-256 curve is vulnerable to Shor's algorithm"
        ),
    }

    # NIST-standardized PQC algorithms
    PQC_ALGORITHMS = {
        "CRYSTALS-Kyber": PQCAlgorithm(
            name="ML-KEM (CRYSTALS-Kyber)",
            category=AlgorithmCategory.KEY_EXCHANGE,
            nist_status="FIPS 203 - Standardized August 2024",
            description="Module-Lattice-Based Key Encapsulation Mechanism",
            security_level="NIST levels 1, 3, 5"
        ),
        "CRYSTALS-Dilithium": PQCAlgorithm(
            name="ML-DSA (CRYSTALS-Dilithium)",
            category=AlgorithmCategory.DIGITAL_SIGNATURE,
            nist_status="FIPS 204 - Standardized August 2024",
            description="Module-Lattice-Based Digital Signature Algorithm",
            security_level="NIST levels 2, 3, 5"
        ),
        "SPHINCS+": PQCAlgorithm(
            name="SLH-DSA (SPHINCS+)",
            category=AlgorithmCategory.DIGITAL_SIGNATURE,
            nist_status="FIPS 205 - Standardized August 2024",
            description="Stateless Hash-Based Signature Scheme",
            security_level="NIST levels 1, 3, 5"
        ),
        "Falcon": PQCAlgorithm(
            name="Falcon",
            category=AlgorithmCategory.DIGITAL_SIGNATURE,
            nist_status="Under standardization for compact signatures",
            description="Fast Fourier Lattice-based Compact Signatures",
            security_level="NIST levels 1, 5"
        ),
    }

    # Code patterns that indicate vulnerable crypto usage
    CODE_PATTERNS = {
        # Python cryptography library patterns
        r"from\s+cryptography\.hazmat\.primitives\.asymmetric\s+import\s+rsa": "RSA",
        r"from\s+cryptography\.hazmat\.primitives\.asymmetric\s+import\s+dsa": "DSA",
        r"from\s+cryptography\.hazmat\.primitives\.asymmetric\s+import\s+ec": "ECDSA",
        r"from\s+cryptography\.hazmat\.primitives\.asymmetric\s+import\s+ed25519": "Ed25519",
        r"rsa\.generate_private_key": "RSA",
        r"dsa\.generate_private_key": "DSA",
        r"ec\.generate_private_key": "ECDSA",
        r"RSAPrivateKey": "RSA",
        r"DSAPrivateKey": "DSA",
        r"EllipticCurvePrivateKey": "ECDSA",
        r"ECDSA\(": "ECDSA",
        r"ECDH\(": "ECDH",

        # OpenSSL / general patterns
        r"RSA_generate_key": "RSA",
        r"EC_KEY_new": "ECDSA",
        r"EVP_PKEY_RSA": "RSA",
        r"EVP_PKEY_EC": "ECDSA",

        # TLS cipher suites
        r"TLS_RSA_": "RSA",
        r"TLS_ECDHE_RSA_": "RSA",
        r"TLS_ECDHE_ECDSA_": "ECDSA",
        r"ECDHE-RSA-": "RSA",
        r"ECDHE-ECDSA-": "ECDSA",

        # Key size specifications
        r"key_size\s*=\s*2048": "RSA",
        r"key_size\s*=\s*4096": "RSA",
        r"2048-bit": "RSA",
        r"4096-bit": "RSA",

        # Certificate/signature algorithms
        r"sha256WithRSAEncryption": "RSA",
        r"sha384WithRSAEncryption": "RSA",
        r"sha512WithRSAEncryption": "RSA",
        r"ecdsa-with-SHA256": "ECDSA",
        r"ecdsa-with-SHA384": "ECDSA",

        # Common curve names
        r"secp256r1": "secp256r1",
        r"secp384r1": "secp384r1",
        r"prime256v1": "prime256v1",
        r"SECP256R1": "secp256r1",
        r"SECP384R1": "secp384r1",
    }

    @classmethod
    def get_algorithm_info(cls, algorithm_name: str) -> Optional[VulnerableAlgorithm]:
        """Get information about a vulnerable algorithm."""
        return cls.VULNERABLE_ALGORITHMS.get(algorithm_name)

    @classmethod
    def get_pqc_recommendation(cls, algorithm_name: str) -> Dict[str, any]:
        """
        Get PQC migration recommendation for a vulnerable algorithm.

        Returns a dict with recommended PQC alternatives and migration guidance.
        """
        algo_info = cls.VULNERABLE_ALGORITHMS.get(algorithm_name)

        if not algo_info:
            return {
                "algorithm": algorithm_name,
                "alternatives": [],
                "recommendation": "Unknown algorithm - manual review required"
            }

        recommendations = {
            AlgorithmCategory.KEY_EXCHANGE: {
                "primary": "ML-KEM (CRYSTALS-Kyber)",
                "alternatives": ["Hybrid: X25519 + ML-KEM"],
                "guidance": (
                    "Migrate to ML-KEM (CRYSTALS-Kyber) for key encapsulation. "
                    "For TLS, use hybrid key exchange combining classical ECDHE with ML-KEM "
                    "until full PQC deployment is mature. This aligns with NIST FIPS 203 and "
                    "ASD's recommendation to begin PQC transition planning immediately."
                )
            },
            AlgorithmCategory.DIGITAL_SIGNATURE: {
                "primary": "ML-DSA (CRYSTALS-Dilithium)",
                "alternatives": ["SLH-DSA (SPHINCS+)", "Falcon (for constrained environments)"],
                "guidance": (
                    "Migrate to ML-DSA (CRYSTALS-Dilithium) for general digital signatures. "
                    "For scenarios requiring smaller signatures, consider Falcon. "
                    "SLH-DSA (SPHINCS+) provides stateless hash-based signatures with conservative "
                    "security assumptions. This aligns with NIST FIPS 204/205 and ASD's "
                    "post-quantum cryptography guidance."
                )
            },
            AlgorithmCategory.ENCRYPTION: {
                "primary": "AES-256 (quantum-resistant for symmetric encryption)",
                "alternatives": [],
                "guidance": (
                    "Symmetric encryption like AES-256 remains quantum-resistant with doubled key sizes. "
                    "Focus PQC migration efforts on asymmetric cryptography (key exchange and signatures)."
                )
            }
        }

        category_rec = recommendations.get(algo_info.category, {
            "primary": "Manual review required",
            "alternatives": [],
            "guidance": "Consult ASD's PQC guidance for specific recommendations"
        })

        return {
            "vulnerable_algorithm": algorithm_name,
            "category": algo_info.category.value,
            "risk_level": algo_info.risk_level.value,
            "primary_replacement": category_rec["primary"],
            "alternative_replacements": category_rec["alternatives"],
            "migration_guidance": category_rec["guidance"],
            "references": [
                "NIST PQC Project: https://csrc.nist.gov/projects/post-quantum-cryptography",
                "ASD Quantum Computing & PQC: https://www.cyber.gov.au/resources-business-and-government/maintaining-devices-and-systems/cryptography/quantum-computing-and-post-quantum-cryptography"
            ]
        }

    @classmethod
    def get_migration_checklist(cls) -> List[Dict[str, str]]:
        """
        Get a generic PQC migration checklist aligned with ASD guidance.
        """
        return [
            {
                "phase": "Discovery & Inventory",
                "tasks": [
                    "Conduct comprehensive cryptographic inventory across all systems",
                    "Identify all uses of public-key cryptography (RSA, ECDSA, ECDH, etc.)",
                    "Map certificate chains and PKI dependencies",
                    "Document third-party dependencies and their crypto usage",
                    "Prioritize systems by criticality and exposure to quantum threat"
                ]
            },
            {
                "phase": "Risk Assessment",
                "tasks": [
                    "Assess 'harvest now, decrypt later' risk for sensitive data",
                    "Determine timeline for quantum threat based on data sensitivity lifetime",
                    "Evaluate business impact of cryptographic failures",
                    "Review compliance requirements (government, defense, critical infrastructure)"
                ]
            },
            {
                "phase": "Planning & Architecture",
                "tasks": [
                    "Design crypto-agile architecture to support algorithm transitions",
                    "Plan for hybrid classical/PQC deployments during transition",
                    "Engage vendors for PQC roadmaps and support timelines",
                    "Budget for infrastructure upgrades (CPU, bandwidth, storage for larger PQC keys/signatures)",
                    "Establish PQC governance and update policies"
                ]
            },
            {
                "phase": "Implementation & Testing",
                "tasks": [
                    "Deploy hybrid TLS configurations (e.g., X25519 + ML-KEM)",
                    "Update PKI infrastructure to support PQC certificates",
                    "Implement ML-KEM for key encapsulation",
                    "Implement ML-DSA for digital signatures",
                    "Conduct interoperability testing",
                    "Performance test PQC implementations under load"
                ]
            },
            {
                "phase": "Deployment & Monitoring",
                "tasks": [
                    "Pilot PQC in non-production environments",
                    "Gradual rollout to production systems",
                    "Monitor performance and compatibility issues",
                    "Maintain classical crypto fallback options during transition",
                    "Document lessons learned and update procedures"
                ]
            },
            {
                "phase": "Ongoing Maintenance",
                "tasks": [
                    "Stay updated on NIST PQC standardization developments",
                    "Monitor ASD and ACSC guidance updates",
                    "Plan for future algorithm updates as standards mature",
                    "Conduct regular crypto-agility assessments",
                    "Train security and development teams on PQC best practices"
                ]
            }
        ]
