# Sample PCAP Files

This directory contains sample PCAP files for testing the PQC Migration Auditor's network traffic analysis capabilities.

## Generating Test PCAP Files

### Option 1: Use the provided script

```bash
python3 generate_sample_pcap.py
```

This will create a `sample-tls-rsa.pcap` file containing TLS handshakes with quantum-vulnerable RSA cipher suites.

### Option 2: Capture real traffic

Use `tcpdump` or `Wireshark` to capture TLS traffic:

```bash
# Capture HTTPS traffic to a file
sudo tcpdump -i any -w sample.pcap 'tcp port 443'

# Then visit some HTTPS websites to generate TLS handshakes
```

### Option 3: Use existing test PCAPs

Download test PCAP files from:
- https://wiki.wireshark.org/SampleCaptures
- Look for files with TLS/SSL traffic

## What the Auditor Detects

The PCAP scanner will identify:

1. **RSA Key Exchange** - TLS cipher suites using static RSA
   - Example: `TLS_RSA_WITH_AES_128_GCM_SHA256`

2. **ECDHE-RSA** - Ephemeral elliptic curve with RSA authentication
   - Example: `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`

3. **ECDHE-ECDSA** - Fully elliptic curve based
   - Example: `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`

4. **Certificate Algorithms** - RSA or ECDSA certificates in the handshake

All of these are vulnerable to quantum attacks via Shor's algorithm.

## Test Without PCAP

If you don't have a PCAP file, you can still test the code scanning functionality:

```bash
# Scan the dummy repository instead
python -m pqc_migration_auditor --mode code --target examples/dummy_repo
```

## Expected PCAP Findings

A typical TLS 1.2 PCAP with RSA certificates should generate findings like:

- **Cipher Suite**: `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
  - Risk: QUANTUM_VULNERABLE
  - Issue: Uses ECDHE (quantum-vulnerable) with RSA authentication

- **Server Certificate**: RSA 2048-bit key
  - Risk: QUANTUM_VULNERABLE
  - Recommendation: Migrate to ML-DSA (Dilithium) or prepare for hybrid certificates

## Scanning a PCAP

```bash
python -m pqc_migration_auditor \\
    --mode pcap \\
    --target examples/pcaps/sample.pcap \\
    --output-json pcap-report.json \\
    --output-html pcap-report.html
```

Note: PCAP scanning requires the `scapy` library. Install with:
```bash
pip install scapy
```
