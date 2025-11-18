"""
Example vulnerable web application using quantum-vulnerable cryptography.
This is a DUMMY application for testing the PQC Migration Auditor.
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import json


class VulnerableAuthService:
    """
    Authentication service using RSA for key exchange and signatures.
    QUANTUM VULNERABLE - needs migration to PQC algorithms.
    """

    def __init__(self):
        # Generate RSA-2048 key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,  # Vulnerable to quantum attacks
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def encrypt_session_key(self, session_key: bytes) -> bytes:
        """Encrypt session key using RSA-OAEP."""
        ciphertext = self.public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    def decrypt_session_key(self, ciphertext: bytes) -> bytes:
        """Decrypt session key using RSA-OAEP."""
        plaintext = self.private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

    def sign_token(self, token_data: bytes) -> bytes:
        """Sign authentication token using RSA-PSS."""
        signature = self.private_key.sign(
            token_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, token_data: bytes, signature: bytes) -> bool:
        """Verify token signature."""
        try:
            self.public_key.verify(
                signature,
                token_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def export_public_key(self) -> bytes:
        """Export public key in PEM format."""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem


class APIClient:
    """
    API client using RSA-4096 for secure communications.
    QUANTUM VULNERABLE - should migrate to ML-KEM for key exchange.
    """

    def __init__(self):
        # Even RSA-4096 is vulnerable to quantum attacks
        self.rsa_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )

    def create_secure_channel(self) -> dict:
        """Establish secure channel using RSA key exchange."""
        return {
            "algorithm": "RSA-4096",
            "key": self.rsa_key,
            "status": "VULNERABLE_TO_QUANTUM_ATTACKS"
        }


def main():
    """Demo of vulnerable cryptographic usage."""
    print("Initializing vulnerable authentication service...")

    auth_service = VulnerableAuthService()
    print(f"Using RSA-2048 encryption - QUANTUM VULNERABLE")

    # Generate session key
    session_key = b"my_secret_session_key_12345"

    # Encrypt with RSA
    encrypted = auth_service.encrypt_session_key(session_key)
    print(f"Encrypted session key length: {len(encrypted)} bytes")

    # Create API client with RSA-4096
    api_client = APIClient()
    channel = api_client.create_secure_channel()
    print(f"API Channel: {channel['algorithm']}")

    print("\nWARNING: This code uses quantum-vulnerable cryptography!")
    print("Recommendation: Migrate to ML-KEM (CRYSTALS-Kyber) and ML-DSA (Dilithium)")


if __name__ == "__main__":
    main()
