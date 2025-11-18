# 🔐 Post-Quantum Cryptography (PQC) Migration Auditor

> A Python tool that scans code and network captures to identify quantum-vulnerable cryptography and suggest NIST/ASD-aligned post-quantum migration options.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: professional](https://img.shields.io/badge/code%20style-professional-brightgreen.svg)](https://github.com/yourusername/pqc-migration-auditor)

---

## 📌 Overview

The **PQC Migration Auditor** is a professional-grade security tool designed to help Australian organisations and security practitioners prepare for the post-quantum era. It automatically identifies quantum-vulnerable cryptographic algorithms in your codebase and network traffic, then provides actionable recommendations aligned with:

- **NIST Post-Quantum Cryptography Standardization** (FIPS 203, 204, 205)
- **Australian Signals Directorate (ASD) PQC Guidance**
- **Industry best practices for crypto-agility**

### The Quantum Threat

Large-scale quantum computers will break widely-used public-key cryptography including:
- **RSA** (all key sizes)
- **ECDSA / ECDH** (all elliptic curves)
- **DSA**
- **Diffie-Hellman**

The threat is not theoretical—adversaries may be conducting "harvest now, decrypt later" attacks, collecting encrypted data today to decrypt with future quantum computers. **ASD recommends organisations begin PQC transition planning immediately.**

---

## ✨ Features

### 🔍 **Dual Scanning Modes**

1. **Code Scanning Mode**
   - Detects vulnerable crypto usage in source code (Python, config files, etc.)
   - Identifies RSA, DSA, ECDSA, ECDH key generation and usage
   - Extracts key sizes and algorithm parameters
   - Scans configuration files (YAML, JSON, OpenSSL configs) for TLS/SSH settings
   - Analyzes certificate files (`.pem`, `.crt`, `.key`) for vulnerable keys

2. **PCAP Scanning Mode**
   - Analyzes network packet captures for TLS handshakes
   - Identifies quantum-vulnerable cipher suites
   - Extracts certificate algorithms and key sizes from TLS sessions
   - Flags RSA key exchange and ECDHE-based sessions

### 💡 **Intelligent Recommendations**

- **NIST-aligned PQC alternatives:**
  - **ML-KEM (CRYSTALS-Kyber)** for key encapsulation
  - **ML-DSA (CRYSTALS-Dilithium)** for digital signatures
  - **SLH-DSA (SPHINCS+)** for hash-based signatures
  - **Falcon** for constrained environments

- **Migration guidance** with actionable next steps
- **Hybrid deployment strategies** for transition periods
- **Risk classification** (QUANTUM_VULNERABLE, TRANSITIONAL, PQC_SAFE)

### 📊 **Multiple Output Formats**

1. **Console Output** - Rich terminal display with color-coded risk levels
2. **JSON Report** - Machine-readable for CI/CD integration
3. **HTML Report** - Professional web-based report for stakeholders

### ✅ **PQC Migration Checklist**

Built-in migration checklist covering:
- Discovery & Inventory
- Risk Assessment
- Planning & Architecture
- Implementation & Testing
- Deployment & Monitoring
- Ongoing Maintenance

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pqc-migration-auditor.git
cd pqc-migration-auditor

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Full Installation (with PCAP support)

```bash
# Install with all optional dependencies
pip install -e ".[all]"
```

**Note:** PCAP scanning requires `scapy`, which may need additional system packages:

- **Ubuntu/Debian:** `sudo apt-get install tcpdump libpcap-dev`
- **macOS:** `brew install libpcap`
- **Windows:** Install [Npcap](https://npcap.com/)

---

## 📖 Usage

### Command-Line Interface

```bash
pqc-auditor --mode {code|pcap} --target TARGET [OPTIONS]
```

### Common Examples

#### 1. Scan a Code Repository

```bash
# Basic code scan
pqc-auditor --mode code --target /path/to/your/project

# Scan with verbose output
pqc-auditor --mode code --target ./my-app --verbose

# Generate JSON and HTML reports
pqc-auditor --mode code --target ./my-app \
    --output-json report.json \
    --output-html report.html
```

#### 2. Scan a PCAP File

```bash
# Analyze network traffic
pqc-auditor --mode pcap --target capture.pcap

# Generate reports for management
pqc-auditor --mode pcap --target tls-traffic.pcap \
    --output-json pcap-findings.json \
    --output-html pcap-report.html
```

#### 3. Scan the Example Dummy Repository

```bash
# Test the tool on our vulnerable example code
pqc-auditor --mode code --target examples/dummy_repo
```

### Python API Usage

```python
from pathlib import Path
from pqc_migration_auditor.scanner.code_scanner import CodeScanner
from pqc_migration_auditor.analysis.recommendations import RecommendationEngine

# Initialize scanner and engine
scanner = CodeScanner()
engine = RecommendationEngine()

# Scan a directory
findings = scanner.scan_directory(Path("./my-project"))

# Generate recommendations
recommendations = [engine.analyze_finding(f) for f in findings]

# Print summary
for rec in recommendations:
    print(f"{rec.vulnerable_algorithm} -> {rec.primary_replacement}")
```

---

## 🏗️ Architecture

### Project Structure

```
pqc-migration-auditor/
├── pqc_migration_auditor/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py                    # Command-line interface
│   ├── scanner/
│   │   ├── code_scanner.py       # Source code analysis
│   │   ├── pcap_scanner.py       # Network traffic analysis
│   │   └── cert_scanner.py       # Certificate file analysis
│   ├── analysis/
│   │   ├── rules.py              # Crypto knowledge base
│   │   └── recommendations.py    # PQC recommendation engine
│   ├── reporting/
│   │   ├── console_reporter.py   # Terminal output
│   │   ├── json_reporter.py      # JSON export
│   │   └── html_reporter.py      # HTML report generation
│   └── utils/
│       ├── logging_utils.py
│       └── file_utils.py
├── examples/
│   ├── dummy_repo/               # Vulnerable test code
│   └── pcaps/                    # Sample PCAP files
├── tests/                        # Unit tests
├── README.md
├── requirements.txt
├── pyproject.toml
└── LICENSE
```

### Design Principles

1. **Separation of Concerns**
   - Scanning logic separate from analysis
   - Analysis separate from reporting
   - Each module has a single, well-defined responsibility

2. **Crypto-Agility**
   - Algorithm definitions centralized in `rules.py`
   - Easy to add new PQC algorithms as standards evolve
   - Extensible pattern matching for new frameworks

3. **Testability**
   - Modular design enables unit testing
   - Includes pytest test suite
   - Example vulnerable code for validation

4. **Professional Quality**
   - Type hints throughout
   - Comprehensive logging
   - Error handling and validation
   - Clean, readable code structure

---

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Or using pytest directly
pytest tests/ -v
pytest tests/ -v --cov=pqc_migration_auditor --cov-report=html
```

### Expected Test Coverage

The test suite covers:
- Code pattern detection (RSA, ECDSA, DSA, etc.)
- Key size extraction
- Recommendation generation
- Knowledge base integrity
- Report summary generation

---

## 📊 Example Output

### Console Output

```
================================================================================
  POST-QUANTUM CRYPTOGRAPHY (PQC) MIGRATION AUDIT REPORT
  Aligned with NIST PQC Standards and ASD Guidance
================================================================================

Scan Information:
  Mode:   code
  Target: examples/dummy_repo

Summary:
  Total Findings:        15
  Quantum Vulnerable:    15
  Transitional:          0

  Findings by Type:
    Code:          13
    Certificates:   2

  Vulnerable Algorithms Detected:
    RSA                  8 occurrence(s)
    ECDSA                5 occurrence(s)
    DSA                  2 occurrence(s)

================================================================================
Detailed Findings:
================================================================================

[1] CODE Finding
  Location:    examples/dummy_repo/webapp.py:12
  Algorithm:   RSA
  Key Size:    2048 bits
  Risk Level:  QUANTUM_VULNERABLE
  Details:     private_key = rsa.generate_private_key(

...

================================================================================
Post-Quantum Migration Recommendations:
================================================================================

• RSA
  Primary Replacement:     ML-KEM (CRYSTALS-Kyber)

  Migration Guidance:
    Migrate to ML-KEM (CRYSTALS-Kyber) for key encapsulation. For TLS, use
    hybrid key exchange combining classical ECDHE with ML-KEM until full PQC
    deployment is mature. This aligns with NIST FIPS 203 and ASD's
    recommendation to begin PQC transition planning immediately.
```

---

## 🎯 What Gets Detected

### Code Patterns

| Algorithm | Detection Examples |
|-----------|-------------------|
| **RSA** | `from cryptography...import rsa`<br>`rsa.generate_private_key()`<br>`key_size=2048` |
| **ECDSA** | `from cryptography...import ec`<br>`ec.generate_private_key()`<br>`SECP256R1` |
| **DSA** | `from cryptography...import dsa`<br>`dsa.generate_private_key()` |
| **Ed25519** | `from cryptography...import ed25519`<br>`Ed25519PrivateKey.generate()` |

### Configuration Files

- TLS cipher suites (e.g., `TLS_RSA_WITH_AES_256_GCM_SHA384`)
- SSH key algorithms (e.g., `ssh-rsa`, `ecdsa-sha2-nistp256`)
- OpenSSL configuration settings
- Key size specifications in YAML/JSON

### Network Traffic (PCAP)

- TLS handshake cipher suites
- Certificate key types (RSA, ECDSA)
- Key exchange methods (RSA, ECDHE, DHE)

---

## 🔬 Technical Details

### Supported Algorithms

#### Quantum-Vulnerable (Detected)

- **RSA** (all key sizes: 1024, 2048, 3072, 4096+)
- **DSA** (Digital Signature Algorithm)
- **ECDSA** (Elliptic Curve Digital Signature Algorithm)
- **ECDH** (Elliptic Curve Diffie-Hellman)
- **DH** (Diffie-Hellman)
- **Ed25519 / EdDSA**

#### Post-Quantum Replacements (Recommended)

| Use Case | NIST Standard | PQC Algorithm | Status |
|----------|---------------|---------------|--------|
| **Key Encapsulation** | FIPS 203 | ML-KEM (CRYSTALS-Kyber) | ✅ Standardized Aug 2024 |
| **Digital Signatures** | FIPS 204 | ML-DSA (CRYSTALS-Dilithium) | ✅ Standardized Aug 2024 |
| **Digital Signatures** | FIPS 205 | SLH-DSA (SPHINCS+) | ✅ Standardized Aug 2024 |
| **Compact Signatures** | Under review | Falcon | 🔄 Standardization in progress |

### Limitations & Future Work

**Current Limitations:**
- Pattern-based detection (may miss obfuscated usage)
- Limited to Python code patterns (extensible to other languages)
- PCAP scanning requires `scapy` library
- No runtime/dynamic analysis

**Planned Enhancements:**
- Support for additional programming languages (Java, C++, Go, Rust)
- Vendor-specific config file parsers (Cisco, F5, etc.)
- Integration with CI/CD pipelines (GitHub Actions, GitLab CI)
- SIEM/SOAR integration
- Full liboqs-python integration for PQC demonstrations
- Automated hybrid key exchange testing

---

## 📚 References & Resources

### Standards & Guidance

- **[NIST Post-Quantum Cryptography Project](https://csrc.nist.gov/projects/post-quantum-cryptography)**
  - FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM)
  - FIPS 204: Module-Lattice-Based Digital Signature Algorithm (ML-DSA)
  - FIPS 205: Stateless Hash-Based Digital Signature Algorithm (SLH-DSA)

- **[ASD Quantum Computing & Post-Quantum Cryptography](https://www.cyber.gov.au/resources-business-and-government/maintaining-devices-and-systems/cryptography/quantum-computing-and-post-quantum-cryptography)**
  - Australian Government guidance on PQC transition planning

- **[ACSC Guidance](https://www.cyber.gov.au/)**
  - Australian Cyber Security Centre resources

### Academic & Technical

- **[PQCrypto Conference Series](https://pqcrypto.org/)**
- **[Open Quantum Safe (OQS) Project](https://openquantumsafe.org/)**
- **[IETF Hybrid Key Exchange Draft](https://datatracker.ietf.org/doc/draft-ietf-tls-hybrid-design/)**

---

## 🎓 Resume-Friendly Project Statement

> **"Developed an automated crypto-agility audit tool aligned with ASD's 2025 Post-Quantum Cryptography Guidelines."**

This project demonstrates:
- ✅ **Security engineering** expertise (cryptography, vulnerability assessment)
- ✅ **Python architecture** skills (modular design, clean code, testing)
- ✅ **Standards compliance** (NIST, ASD alignment)
- ✅ **Professional tooling** (CLI, multiple output formats, documentation)
- ✅ **Australian context** (ASD-aligned, relevant to AU gov/defence/critical infrastructure)

Perfect for portfolios targeting:
- Cybersecurity engineer / architect roles
- Security consultant positions
- Defence and government sector opportunities
- Critical infrastructure security teams

---

## 🤝 Contributing

Contributions are welcome! This is a portfolio project, but improvements are encouraged:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Contribution Ideas

- Add support for additional programming languages
- Improve detection patterns
- Add vendor-specific configuration parsers
- Enhance reporting formats
- Improve test coverage
- Add integration with CI/CD platforms

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is provided for educational and assessment purposes. It:
- Does NOT implement actual post-quantum cryptographic algorithms (use liboqs/OpenSSL for that)
- Is NOT a substitute for professional security assessment
- May produce false positives/negatives
- Should be used as part of a comprehensive PQC migration strategy

Always consult with cryptography and security experts when planning production migrations.

---

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/yourusername/pqc-migration-auditor/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/pqc-migration-auditor/discussions)

---

## 🙏 Acknowledgments

- **NIST PQC Team** for standardization leadership
- **Australian Signals Directorate (ASD)** for Australian PQC guidance
- **Open Quantum Safe (OQS) Project** for PQC implementation reference
- The global cryptography community working to secure the post-quantum future

---

**Built with 🔐 in Australia**

*Preparing today for the quantum future of tomorrow.*
