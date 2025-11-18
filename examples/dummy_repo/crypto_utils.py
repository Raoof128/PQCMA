"""
Cryptographic utilities module.
Contains various quantum-vulnerable algorithms.
"""

from cryptography.hazmat.primitives.asymmetric import ec, dsa, ed25519
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def generate_ecdsa_keypair():
    """
    Generate ECDSA key pair using secp256r1 curve.
    QUANTUM VULNERABLE - ECDSA is broken by Shor's algorithm.
    """
    private_key = ec.generate_private_key(
        ec.SECP256R1(),  # NIST P-256 curve - quantum vulnerable
        backend=default_backend()
    )
    return private_key


def generate_dsa_keypair():
    """
    Generate DSA key pair.
    QUANTUM VULNERABLE - DSA is broken by Shor's algorithm.
    """
    private_key = dsa.generate_private_key(
        key_size=2048,
        backend=default_backend()
    )
    return private_key


def generate_ed25519_keypair():
    """
    Generate Ed25519 key pair.
    QUANTUM VULNERABLE - EdDSA is vulnerable to quantum attacks.
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    return private_key


class ECDHKeyExchange:
    """
    Elliptic Curve Diffie-Hellman key exchange.
    QUANTUM VULNERABLE - should migrate to ML-KEM.
    """

    def __init__(self):
        # Using SECP384R1 curve (P-384)
        self.private_key = ec.generate_private_key(
            ec.SECP384R1(),
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def derive_shared_key(self, peer_public_key):
        """Derive shared secret using ECDH."""
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF

        shared_key = self.private_key.exchange(
            ec.ECDH(),
            peer_public_key
        )

        # Derive a key from the shared secret
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
            backend=default_backend()
        ).derive(shared_key)

        return derived_key


class SignatureVerifier:
    """
    Digital signature verification using ECDSA.
    QUANTUM VULNERABLE.
    """

    @staticmethod
    def verify_ecdsa_signature(public_key, signature, message):
        """Verify ECDSA signature."""
        try:
            public_key.verify(
                signature,
                message,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False

    @staticmethod
    def verify_dsa_signature(public_key, signature, message):
        """Verify DSA signature."""
        try:
            public_key.verify(
                signature,
                message,
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
