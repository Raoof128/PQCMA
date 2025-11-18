"""
PCAP scanner for detecting quantum-vulnerable cryptography in network traffic.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from ..analysis.recommendations import Finding
from ..analysis.rules import CryptoKnowledgeBase, RiskLevel
from ..utils.logging_utils import get_logger

# Try to import scapy, but make it optional
try:
    from scapy.all import rdpcap, TLS, TLSClientHello, TLSServerHello, TLSCertificate
    from scapy.layers.tls.handshake import TLSClientKeyExchange, TLSServerKeyExchange
    from scapy.layers.x509 import X509_Cert
    SCAPY_AVAILABLE = True
except (ImportError, Exception):
    SCAPY_AVAILABLE = False
    rdpcap = None
    TLS = None
    TLSClientHello = None
    TLSServerHello = None
    TLSCertificate = None

# Try to import cryptography for certificate parsing
try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec
    CRYPTO_AVAILABLE = True
except (ImportError, Exception):
    CRYPTO_AVAILABLE = False
    x509 = None
    default_backend = None
    rsa = None
    dsa = None
    ec = None


logger = get_logger(__name__)


class PCAPScanner:
    """
    Scans PCAP files for quantum-vulnerable TLS handshakes and certificates.
    """

    def __init__(self):
        self.knowledge_base = CryptoKnowledgeBase()
        if not SCAPY_AVAILABLE:
            logger.warning("Scapy library not available - PCAP scanning disabled")

    def scan_pcap(self, pcap_path: Path) -> List[Finding]:
        """
        Scan a PCAP file for vulnerable cryptographic usage.

        Args:
            pcap_path: Path to the PCAP file

        Returns:
            List of findings
        """
        if not SCAPY_AVAILABLE:
            logger.warning("Scapy library not available - skipping PCAP scanning")
            logger.warning("Install with: pip install scapy")
            return []

        logger.info(f"Scanning PCAP file: {pcap_path}")

        if not pcap_path.exists():
            logger.error(f"PCAP file does not exist: {pcap_path}")
            return []

        findings: List[Finding] = []

        try:
            # Read PCAP file
            packets = rdpcap(str(pcap_path))
            logger.info(f"Loaded {len(packets)} packets from PCAP")

            # Track TLS sessions
            tls_sessions: Dict[str, Dict[str, Any]] = {}

            # Analyze packets
            for idx, packet in enumerate(packets):
                # Look for TLS handshake messages
                if packet.haslayer(TLS):
                    session_findings = self._analyze_tls_packet(
                        packet,
                        idx,
                        tls_sessions,
                        pcap_path
                    )
                    findings.extend(session_findings)

            logger.info(f"PCAP scan complete: {len(findings)} findings")

        except Exception as e:
            logger.error(f"Error scanning PCAP: {e}")

        return findings

    def _analyze_tls_packet(
        self,
        packet: Any,
        packet_idx: int,
        tls_sessions: Dict[str, Dict[str, Any]],
        pcap_path: Path
    ) -> List[Finding]:
        """
        Analyze a TLS packet for vulnerable cryptography.

        Args:
            packet: Scapy packet
            packet_idx: Packet index in PCAP
            tls_sessions: Dictionary tracking TLS session information
            pcap_path: Path to the PCAP file

        Returns:
            List of findings from this packet
        """
        findings: List[Finding] = []

        try:
            # Get session identifier (src:sport -> dst:dport)
            if hasattr(packet, 'ip') and hasattr(packet.ip, 'src'):
                src_ip = packet.ip.src
                dst_ip = packet.ip.dst
            else:
                src_ip = "unknown"
                dst_ip = "unknown"

            if hasattr(packet, 'sport') and hasattr(packet, 'dport'):
                src_port = packet.sport
                dst_port = packet.dport
            else:
                src_port = 0
                dst_port = 0

            session_id = f"{src_ip}:{src_port}->{dst_ip}:{dst_port}"

            if session_id not in tls_sessions:
                tls_sessions[session_id] = {
                    "client_hello": None,
                    "server_hello": None,
                    "certificates": [],
                    "key_exchange": None
                }

            # Check for Client Hello
            if packet.haslayer(TLSClientHello):
                client_hello = packet[TLSClientHello]
                tls_sessions[session_id]["client_hello"] = {
                    "packet_idx": packet_idx,
                    "cipher_suites": self._extract_cipher_suites(client_hello)
                }

            # Check for Server Hello
            if packet.haslayer(TLSServerHello):
                server_hello = packet[TLSServerHello]
                cipher_suite = self._get_cipher_suite_name(server_hello.cipher)
                tls_sessions[session_id]["server_hello"] = {
                    "packet_idx": packet_idx,
                    "cipher_suite": cipher_suite
                }

                # Analyze cipher suite for vulnerabilities
                finding = self._analyze_cipher_suite(
                    cipher_suite,
                    session_id,
                    packet_idx,
                    pcap_path
                )
                if finding:
                    findings.append(finding)

            # Check for Certificate
            if packet.haslayer(TLSCertificate) and CRYPTO_AVAILABLE:
                cert_findings = self._analyze_tls_certificate(
                    packet[TLSCertificate],
                    session_id,
                    packet_idx,
                    pcap_path
                )
                findings.extend(cert_findings)

        except Exception as e:
            logger.debug(f"Error analyzing TLS packet {packet_idx}: {e}")

        return findings

    def _extract_cipher_suites(self, client_hello: Any) -> List[str]:
        """Extract cipher suite names from Client Hello."""
        cipher_suites = []
        try:
            if hasattr(client_hello, 'ciphers'):
                for cipher in client_hello.ciphers:
                    cipher_name = self._get_cipher_suite_name(cipher)
                    if cipher_name:
                        cipher_suites.append(cipher_name)
        except Exception:
            pass
        return cipher_suites

    def _get_cipher_suite_name(self, cipher_code: Any) -> str:
        """Get cipher suite name from code."""
        # This is a simplified mapping - real implementation would be more comprehensive
        cipher_map = {
            0x002F: "TLS_RSA_WITH_AES_128_CBC_SHA",
            0x0035: "TLS_RSA_WITH_AES_256_CBC_SHA",
            0xC013: "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
            0xC014: "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
            0xC009: "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
            0xC00A: "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
            0x009C: "TLS_RSA_WITH_AES_128_GCM_SHA256",
            0x009D: "TLS_RSA_WITH_AES_256_GCM_SHA384",
            0xC02F: "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
            0xC030: "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
        }

        try:
            if isinstance(cipher_code, int):
                return cipher_map.get(cipher_code, f"UNKNOWN_0x{cipher_code:04X}")
            else:
                return str(cipher_code)
        except Exception:
            return "UNKNOWN"

    def _analyze_cipher_suite(
        self,
        cipher_suite: str,
        session_id: str,
        packet_idx: int,
        pcap_path: Path
    ) -> Optional[Finding]:
        """
        Analyze a cipher suite for quantum vulnerabilities.

        Args:
            cipher_suite: Cipher suite name
            session_id: TLS session identifier
            packet_idx: Packet index
            pcap_path: Path to PCAP file

        Returns:
            Finding if vulnerable, None otherwise
        """
        # Check for RSA key exchange
        if "RSA" in cipher_suite and "ECDHE" not in cipher_suite:
            return Finding(
                finding_type="PCAP",
                location=f"{pcap_path}:packet_{packet_idx}",
                algorithm="RSA",
                risk_level=RiskLevel.QUANTUM_VULNERABLE.value,
                details=f"TLS session using RSA key exchange: {cipher_suite}",
                raw_data={
                    "pcap_file": str(pcap_path),
                    "packet_index": packet_idx,
                    "session_id": session_id,
                    "cipher_suite": cipher_suite,
                    "vulnerability": "RSA key exchange vulnerable to quantum attacks"
                }
            )

        # Check for ECDHE (vulnerable but better than static RSA)
        elif "ECDHE" in cipher_suite:
            if "RSA" in cipher_suite:
                algorithm = "ECDH+RSA"
            elif "ECDSA" in cipher_suite:
                algorithm = "ECDSA"
            else:
                algorithm = "ECDH"

            return Finding(
                finding_type="PCAP",
                location=f"{pcap_path}:packet_{packet_idx}",
                algorithm=algorithm,
                risk_level=RiskLevel.QUANTUM_VULNERABLE.value,
                details=f"TLS session using quantum-vulnerable ephemeral key exchange: {cipher_suite}",
                raw_data={
                    "pcap_file": str(pcap_path),
                    "packet_index": packet_idx,
                    "session_id": session_id,
                    "cipher_suite": cipher_suite,
                    "vulnerability": "ECDHE provides forward secrecy but is quantum-vulnerable"
                }
            )

        return None

    def _analyze_tls_certificate(
        self,
        tls_cert_layer: Any,
        session_id: str,
        packet_idx: int,
        pcap_path: Path
    ) -> List[Finding]:
        """
        Analyze TLS certificates from handshake.

        Args:
            tls_cert_layer: Scapy TLS Certificate layer
            session_id: TLS session identifier
            packet_idx: Packet index
            pcap_path: Path to PCAP file

        Returns:
            List of findings from certificates
        """
        findings: List[Finding] = []

        if not CRYPTO_AVAILABLE:
            return findings

        try:
            # Extract certificates
            if hasattr(tls_cert_layer, 'certs'):
                for cert_data in tls_cert_layer.certs:
                    try:
                        # Parse certificate
                        if hasattr(cert_data, 'der'):
                            cert_bytes = cert_data.der
                        else:
                            cert_bytes = bytes(cert_data)

                        cert = x509.load_der_x509_certificate(cert_bytes, default_backend())

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
                            finding = Finding(
                                finding_type="PCAP",
                                location=f"{pcap_path}:packet_{packet_idx}",
                                algorithm=algorithm,
                                key_size=key_size,
                                risk_level=RiskLevel.QUANTUM_VULNERABLE.value,
                                details=f"TLS certificate with {algorithm} {key_size}-bit key",
                                raw_data={
                                    "pcap_file": str(pcap_path),
                                    "packet_index": packet_idx,
                                    "session_id": session_id,
                                    "subject": str(cert.subject),
                                    "issuer": str(cert.issuer)
                                }
                            )
                            findings.append(finding)

                    except Exception as e:
                        logger.debug(f"Error parsing certificate in packet {packet_idx}: {e}")

        except Exception as e:
            logger.debug(f"Error analyzing TLS certificates: {e}")

        return findings
