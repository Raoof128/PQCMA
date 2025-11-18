# Usage Examples for PQC Migration Auditor

This document provides detailed usage examples for the PQC Migration Auditor.

## Quick Start

### 1. Test Installation

```bash
# Run the basic test script
python test_basic.py
```

Expected output: The tool should detect 30+ vulnerable crypto usages in the dummy repository.

### 2. Scan the Example Repository

```bash
# Basic scan with console output
python -m pqc_migration_auditor --mode code --target examples/dummy_repo

# Scan with verbose logging
python -m pqc_migration_auditor --mode code --target examples/dummy_repo --verbose
```

### 3. Generate Reports

```bash
# Generate JSON report
python -m pqc_migration_auditor \
    --mode code \
    --target examples/dummy_repo \
    --output-json findings-report.json

# Generate HTML report for management
python -m pqc_migration_auditor \
    --mode code \
    --target examples/dummy_repo \
    --output-html findings-report.html

# Generate both reports
python -m pqc_migration_auditor \
    --mode code \
    --target examples/dummy_repo \
    --output-json report.json \
    --output-html report.html
```

## Real-World Scenarios

### Scenario 1: Audit a Python Web Application

```bash
# Scan a Django/Flask project
python -m pqc_migration_auditor \
    --mode code \
    --target /path/to/webapp \
    --output-json webapp-audit.json \
    --output-html webapp-audit.html \
    --verbose
```

**What it detects:**
- RSA key generation in authentication modules
- ECDSA usage in JWT signing
- Vulnerable TLS configurations in settings files
- Certificate files with RSA/ECDSA keys

### Scenario 2: Scan Infrastructure-as-Code

```bash
# Scan Terraform/Ansible configurations
python -m pqc_migration_auditor \
    --mode code \
    --target /path/to/infrastructure \
    --output-json infra-audit.json
```

**What it detects:**
- OpenSSL configuration files
- TLS cipher suite specifications
- SSH host key algorithm settings
- Certificate generation scripts

### Scenario 3: Analyze Network Traffic (PCAP)

```bash
# Scan a captured TLS session
python -m pqc_migration_auditor \
    --mode pcap \
    --target network-capture.pcap \
    --output-html tls-analysis.html
```

**What it detects:**
- TLS cipher suites in Server Hello
- RSA vs ECDHE key exchange
- Certificate algorithms in TLS handshakes
- Quantum-vulnerable cryptography in transit

**Note:** PCAP scanning requires `scapy`:
```bash
pip install scapy
```

### Scenario 4: CI/CD Integration

```bash
#!/bin/bash
# Example CI/CD script

# Run audit
python -m pqc_migration_auditor \
    --mode code \
    --target . \
    --output-json pqc-audit.json \
    --quiet

# Check exit code (non-zero if quantum-vulnerable crypto found)
if [ $? -ne 0 ]; then
    echo "❌ Quantum-vulnerable cryptography detected!"
    echo "📊 See pqc-audit.json for details"
    # Optionally fail the build or create a warning
fi
```

## Python API Examples

### Example 1: Basic Scanning

```python
from pathlib import Path
from pqc_migration_auditor.scanner.code_scanner import CodeScanner
from pqc_migration_auditor.analysis.recommendations import RecommendationEngine

# Initialize
scanner = CodeScanner()
engine = RecommendationEngine()

# Scan
findings = scanner.scan_directory(Path("./my-project"))

# Get recommendations
for finding in findings:
    rec = engine.analyze_finding(finding)
    print(f"{rec.vulnerable_algorithm} -> {rec.primary_replacement}")
```

### Example 2: Generate Custom Report

```python
from pathlib import Path
from pqc_migration_auditor.scanner.code_scanner import CodeScanner
from pqc_migration_auditor.analysis.recommendations import RecommendationEngine
from pqc_migration_auditor.reporting.json_reporter import JSONReporter

# Scan
scanner = CodeScanner()
findings = scanner.scan_directory(Path("./my-app"))

# Analyze
engine = RecommendationEngine()
recommendations = [engine.analyze_finding(f) for f in findings]
summary = engine.generate_report_summary(findings, recommendations)

# Generate report
reporter = JSONReporter()
report = reporter.generate_report(
    findings=findings,
    recommendations=recommendations,
    summary=summary,
    scan_metadata={"mode": "code", "target": "./my-app"},
    migration_checklist=engine.get_migration_checklist()
)

# Save
reporter.write_report(report, Path("custom-report.json"))
```

### Example 3: Filter Findings

```python
from pathlib import Path
from pqc_migration_auditor.scanner.code_scanner import CodeScanner
from pqc_migration_auditor.analysis.rules import RiskLevel

# Scan
scanner = CodeScanner()
findings = scanner.scan_directory(Path("./my-project"))

# Filter only critical findings
critical_findings = [
    f for f in findings
    if f.risk_level == RiskLevel.QUANTUM_VULNERABLE.value
]

# Group by algorithm
from collections import defaultdict
by_algorithm = defaultdict(list)
for finding in critical_findings:
    by_algorithm[finding.algorithm].append(finding)

# Print summary
for algo, findings_list in by_algorithm.items():
    print(f"{algo}: {len(findings_list)} occurrences")
    for f in findings_list[:3]:  # Show first 3
        print(f"  - {f.location}")
```

## Expected Output Formats

### Console Output (Summary)

```
================================================================================
  POST-QUANTUM CRYPTOGRAPHY (PQC) MIGRATION AUDIT REPORT
  Aligned with NIST PQC Standards and ASD Guidance
================================================================================

Summary:
  Total Findings:        33
  Quantum Vulnerable:    33

  Vulnerable Algorithms Detected:
    RSA                  17 occurrence(s)
    ECDSA                6 occurrence(s)
    secp256r1            4 occurrence(s)
```

### JSON Output (Structure)

```json
{
  "metadata": {
    "tool": "PQC Migration Auditor",
    "version": "1.0.0",
    "scan_time": "2025-01-15T10:30:00",
    "mode": "code",
    "target": "examples/dummy_repo"
  },
  "summary": {
    "total_findings": 33,
    "critical_count": 33,
    "findings_by_type": {
      "CODE": 33
    },
    "algorithms_detected": {
      "RSA": 17,
      "ECDSA": 6
    }
  },
  "findings": [
    {
      "type": "CODE",
      "location": "webapp.py:12",
      "algorithm": "RSA",
      "key_size": 2048,
      "risk_level": "QUANTUM_VULNERABLE",
      "details": "rsa.generate_private_key(...)"
    }
  ],
  "recommendations": [...]
}
```

### HTML Output

Opens in browser with:
- Executive summary with statistics
- Detailed findings table
- Migration recommendations
- Interactive PQC migration checklist
- Professional styling for stakeholder presentations

## Troubleshooting

### Issue: "cryptography library not available"

**Solution:** The code scanner works without the cryptography library. Only certificate file scanning requires it.

```bash
# Install if needed
pip install cryptography
```

### Issue: "scapy library not available"

**Solution:** PCAP scanning requires scapy.

```bash
# Install scapy
pip install scapy

# On Linux, may also need:
sudo apt-get install tcpdump libpcap-dev
```

### Issue: No findings detected

**Possible causes:**
1. The code doesn't use the cryptography library patterns we detect
2. Crypto usage is obfuscated or in a different language
3. The scan target path is incorrect

**Solution:** Check that the target path is correct and contains source code files.

## Performance Tips

### Large Codebases

For large repositories (10,000+ files):

```bash
# Scan with quiet mode, save to JSON
python -m pqc_migration_auditor \
    --mode code \
    --target /large/repo \
    --output-json findings.json \
    --quiet

# Then analyze the JSON separately
```

### Selective Scanning

If you only want to scan specific directories:

```bash
# Scan only the application source (not dependencies)
python -m pqc_migration_auditor \
    --mode code \
    --target /project/src \
    --output-json src-audit.json
```

## Integration Examples

### GitHub Actions

```yaml
name: PQC Crypto Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install PQC Auditor
        run: |
          pip install -e .

      - name: Run PQC Audit
        run: |
          python -m pqc_migration_auditor \
            --mode code \
            --target . \
            --output-json pqc-audit.json

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: pqc-audit-report
          path: pqc-audit.json
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python -m pqc_migration_auditor \
    --mode code \
    --target . \
    --quiet \
    --output-json .pqc-audit.json

# Don't fail the commit, just warn
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Quantum-vulnerable cryptography detected"
    echo "   See .pqc-audit.json for details"
fi

exit 0
```

## Next Steps

After running the audit:

1. **Review the findings** - Understand which algorithms are used where
2. **Prioritize** - Focus on high-value systems and sensitive data
3. **Plan migration** - Use the migration checklist provided
4. **Engage vendors** - Ask about their PQC roadmaps
5. **Test hybrid approaches** - Combine classical and PQC during transition
6. **Monitor standards** - Stay updated on NIST PQC developments

## Getting Help

- **Documentation:** See README.md
- **Issues:** Report bugs or ask questions on GitHub Issues
- **ASD Guidance:** https://www.cyber.gov.au/
- **NIST PQC:** https://csrc.nist.gov/projects/post-quantum-cryptography
