#!/usr/bin/env python3
"""
Generate test RSA certificates for demonstration purposes.
These certificates are QUANTUM VULNERABLE and for testing only.
"""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import datetime


def generate_rsa_cert(key_size=2048, filename_prefix="test-rsa"):
    """Generate a self-signed RSA certificate."""

    # Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )

    # Generate certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "AU"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Queensland"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Brisbane"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PQC Test Corp"),
        x509.NameAttribute(NameOID.COMMON_NAME, "example.com"),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("example.com"),
            x509.DNSName("www.example.com"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())

    # Write private key
    with open(f"{filename_prefix}-{key_size}.key", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Write certificate
    with open(f"{filename_prefix}-{key_size}.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"Generated {filename_prefix}-{key_size}.key and {filename_prefix}-{key_size}.crt")


if __name__ == "__main__":
    print("Generating quantum-vulnerable RSA certificates for testing...")
    print("WARNING: These are for testing only!\n")

    # Generate RSA-2048 cert
    generate_rsa_cert(2048, "server-rsa")

    # Generate RSA-4096 cert
    generate_rsa_cert(4096, "ca-rsa")

    print("\nCertificates generated successfully.")
    print("These certificates use RSA and are QUANTUM VULNERABLE.")
