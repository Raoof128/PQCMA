# Vulnerable Demo Application

This is a **dummy repository** for testing the PQC Migration Auditor.

## ⚠️ WARNING: Quantum-Vulnerable Cryptography

This application intentionally uses quantum-vulnerable cryptographic algorithms for demonstration purposes:

- **RSA-2048 and RSA-4096**: Used for key exchange and digital signatures
- **ECDSA with NIST curves**: Used for authentication
- **ECDH**: Used for key agreement
- **DSA**: Used in legacy components

All of these algorithms are vulnerable to Shor's algorithm running on a cryptographically-relevant quantum computer (CRQC).

## Files

- `webapp.py` - Web application using RSA encryption and signatures
- `crypto_utils.py` - Cryptographic utilities using ECDSA, DSA, Ed25519
- `config.yaml` - Configuration file with TLS and SSH settings
- `openssl.conf` - OpenSSL configuration with RSA settings

## Scan This Repository

To test the PQC Migration Auditor:

```bash
python -m pqc_migration_auditor --mode code --target examples/dummy_repo
```

## Expected Findings

The auditor should detect:
1. Multiple uses of RSA (2048-bit and 4096-bit)
2. ECDSA usage with various curves (P-256, P-384)
3. DSA usage
4. Ed25519 usage
5. ECDH key exchange
6. Quantum-vulnerable TLS cipher suites in configuration

## Recommended Migration

- RSA → **ML-KEM (CRYSTALS-Kyber)** for key encapsulation
- ECDSA/DSA → **ML-DSA (CRYSTALS-Dilithium)** for digital signatures
- ECDH → **ML-KEM** or hybrid approach
- TLS cipher suites → Hybrid PQC/classical suites
