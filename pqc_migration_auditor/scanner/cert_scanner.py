"""
Certificate scanner for detecting quantum-vulnerable certificates and keys.
"""

from pathlib import Path
from typing import List, Optional
from ..analysis.recommendations import Finding
from ..analysis.rules import CryptoKnowledgeBase, RiskLevel
from ..utils.logging_utils import get_logger
from ..utils.file_utils import find_scannable_files, is_certificate_file

# Try to import cryptography, but make it optional
try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec
    CRYPTO_AVAILABLE = True
except (ImportError, Exception):
    # Crypto library not available or broken - scanner will be disabled
    CRYPTO_AVAILABLE = False
    x509 = None
    default_backend = None
    serialization = None
    rsa = None
    dsa = None
    ec = None


logger = get_logger(__name__)


class CertificateScanner:
    """
    Scans certificate and key files for quantum-vulnerable algorithms.
    """

    def __init__(self):
        self.knowledge_base = CryptoKnowledgeBase()
        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography library not available - certificate scanning disabled")

    def scan_directory(self, directory_path: Path) -> List[Finding]:
        """
        Scan a directory for certificate/key files.

        Args:
            directory_path: Path to the directory to scan

        Returns:
            List of findings
        """
        if not CRYPTO_AVAILABLE:
            logger.debug("Certificate scanning skipped - cryptography library not available")
            return []

        logger.info(f"Scanning certificates in: {directory_path}")

        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"Invalid directory: {directory_path}")
            return []

        findings: List[Finding] = []

        # Find all certificate/key files
        all_files = find_scannable_files(directory_path, include_certs=True)
        cert_files = [f for f in all_files if is_certificate_file(f)]

        logger.info(f"Found {len(cert_files)} certificate/key files")

        for cert_file in cert_files:
            file_findings = self.scan_certificate_file(cert_file)
            findings.extend(file_findings)

        logger.info(f"Certificate scan complete: {len(findings)} findings")
        return findings

    def scan_certificate_file(self, file_path: Path) -> List[Finding]:
        """
        Scan a certificate or key file.

        Args:
            file_path: Path to the certificate/key file

        Returns:
            List of findings
        """
        if not CRYPTO_AVAILABLE:
            return []

        findings: List[Finding] = []

        try:
            # Read file content
            content = file_path.read_bytes()

            # Try to parse as certificate
            cert_finding = self._scan_certificate(file_path, content)
            if cert_finding:
                findings.append(cert_finding)
                return findings

            # Try to parse as private key
            key_finding = self._scan_private_key(file_path, content)
            if key_finding:
                findings.append(key_finding)

        except Exception as e:
            logger.debug(f"Could not parse {file_path}: {e}")

        return findings

    def _scan_certificate(self, file_path: Path, content: bytes) -> Optional[Finding]:
        """
        Scan a certificate for vulnerable algorithms.

        Args:
            file_path: Path to the certificate file
            content: File content

        Returns:
            Finding if vulnerable algorithm detected, None otherwise
        """
        if not CRYPTO_AVAILABLE:
            return None

        try:
            # Try PEM format
            cert = x509.load_pem_x509_certificate(content, default_backend())
        except Exception:
            try:
                # Try DER format
                cert = x509.load_der_x509_certificate(content, default_backend())
            except Exception:
                return None

        # Get public key
        public_key = cert.public_key()

        # Determine algorithm and key size
        algorithm = None
        key_size = None

        if isinstance(public_key, rsa.RSAPublicKey):
            algorithm = "RSA"
            key_size = public_key.key_size
        elif isinstance(public_key, dsa.DSAPublicKey):
            algorithm = "DSA"
            key_size = public_key.key_size
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            algorithm = "ECDSA"
            key_size = public_key.curve.key_size

        if algorithm:
            algo_info = self.knowledge_base.get_algorithm_info(algorithm)
            risk_level = algo_info.risk_level.value if algo_info else RiskLevel.UNKNOWN.value

            return Finding(
                finding_type="CERT",
                location=str(file_path),
                algorithm=algorithm,
                key_size=key_size,
                risk_level=risk_level,
                details=f"Certificate with {algorithm} {key_size}-bit public key",
                raw_data={
                    "file": str(file_path),
                    "subject": str(cert.subject),
                    "issuer": str(cert.issuer),
                    "not_valid_before": cert.not_valid_before_utc.isoformat(),
                    "not_valid_after": cert.not_valid_after_utc.isoformat()
                }
            )

        return None

    def _scan_private_key(self, file_path: Path, content: bytes) -> Optional[Finding]:
        """
        Scan a private key file for vulnerable algorithms.

        Args:
            file_path: Path to the key file
            content: File content

        Returns:
            Finding if vulnerable algorithm detected, None otherwise
        """
        if not CRYPTO_AVAILABLE:
            return None

        try:
            # Try to load as private key (PEM format, no password)
            private_key = serialization.load_pem_private_key(
                content,
                password=None,
                backend=default_backend()
            )
        except Exception:
            return None

        # Determine algorithm and key size
        algorithm = None
        key_size = None

        if isinstance(private_key, rsa.RSAPrivateKey):
            algorithm = "RSA"
            key_size = private_key.key_size
        elif isinstance(private_key, dsa.DSAPrivateKey):
            algorithm = "DSA"
            key_size = private_key.key_size
        elif isinstance(private_key, ec.EllipticCurvePrivateKey):
            algorithm = "ECDSA"
            key_size = private_key.curve.key_size

        if algorithm:
            algo_info = self.knowledge_base.get_algorithm_info(algorithm)
            risk_level = algo_info.risk_level.value if algo_info else RiskLevel.UNKNOWN.value

            return Finding(
                finding_type="CERT",
                location=str(file_path),
                algorithm=algorithm,
                key_size=key_size,
                risk_level=risk_level,
                details=f"Private key file with {algorithm} {key_size}-bit key",
                raw_data={
                    "file": str(file_path),
                    "key_type": "private"
                }
            )

        return None
