# Architecture Documentation

## Overview

The PQC Migration Auditor is a modular Python application designed to identify quantum-vulnerable cryptographic implementations across codebases, network traffic, and certificate infrastructure. This document provides a comprehensive overview of the system architecture, design decisions, and data flow.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Module Structure](#module-structure)
3. [Data Flow](#data-flow)
4. [Key Components](#key-components)
5. [Design Patterns](#design-patterns)
6. [Extension Points](#extension-points)
7. [Security Considerations](#security-considerations)
8. [Performance Characteristics](#performance-characteristics)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│                    (pqc_migration_auditor/cli.py)            │
└───────────────┬──────────────────────────────────────────────┘
                │
                ├──── Scanners ─────────────────────────────────┐
                │                                               │
        ┌───────┴────────┐  ┌────────────┐  ┌──────────────┐  │
        │ Code Scanner   │  │   PCAP     │  │ Certificate  │  │
        │                │  │  Scanner   │  │   Scanner    │  │
        └───────┬────────┘  └─────┬──────┘  └──────┬───────┘  │
                │                  │                 │          │
                └──────────────────┴─────────────────┴──────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                │      Analysis & Rules Engine        │
                │  - CryptoKnowledgeBase              │
                │  - RecommendationEngine             │
                │  - Pattern Matching                 │
                └──────────────────┬──────────────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                │         Reporting Layer             │
                │  - Console Reporter                 │
                │  - JSON Reporter                    │
                │  - HTML Reporter                    │
                └─────────────────────────────────────┘
```

## Module Structure

### Core Modules

#### 1. `pqc_migration_auditor/cli.py`
**Purpose:** Command-line interface and application orchestration

**Responsibilities:**
- Argument parsing and validation
- Scanner coordination
- Error handling and logging setup
- Output formatting delegation
- Exit code management

**Key Classes:**
- `PQCAuditorCLI`: Main application controller

**Design Notes:**
- Initializes logging before any other operations (critical bug fix in v1.0.1)
- Uses composition to manage scanner instances
- Validates all paths before processing
- Gracefully handles missing optional dependencies

---

#### 2. `pqc_migration_auditor/scanner/`

##### a. `code_scanner.py`
**Purpose:** Static analysis of source code for cryptographic API usage

**Responsibilities:**
- Recursive directory traversal
- Text file detection and reading
- Pattern matching against code patterns
- Finding deduplication (v1.0.1 enhancement)
- Progress tracking for large repositories

**Key Classes:**
- `CodeScanner`: Main scanning engine

**Algorithm:**
```python
for file in find_scannable_files(directory):
    for line_num, line in enumerate(file):
        seen_algorithms = set()  # Deduplication per line
        for pattern, algorithm in patterns:
            if matches(pattern, line) and algorithm not in seen_algorithms:
                create_finding(file, line_num, algorithm)
                seen_algorithms.add(algorithm)
```

**Performance:**
- O(n * m * p) where n=files, m=lines, p=patterns
- Optimized with early termination on match
- File size limit: 10MB default
- Progress logging every 100 files

##### b. `pcap_scanner.py`
**Purpose:** Network traffic analysis for TLS handshakes

**Dependencies:** scapy (optional)

**Responsibilities:**
- PCAP file parsing
- TLS session reconstruction
- Cipher suite analysis
- Certificate extraction from handshakes

**Key Classes:**
- `PCAPScanner`: PCAP analysis engine

**TLS Session Tracking:**
```python
sessions = {
    "src:sport->dst:dport": {
        "client_hello": {...},
        "server_hello": {...},
        "certificates": [...],
        "key_exchange": {...}
    }
}
```

**Graceful Degradation:**
- If scapy unavailable: warns user and returns empty findings
- If cryptography unavailable: skips certificate parsing

##### c. `cert_scanner.py`
**Purpose:** X.509 certificate and private key analysis

**Dependencies:** cryptography (optional)

**Responsibilities:**
- Certificate file discovery (.pem, .crt, .cer, .key)
- Public key extraction
- Algorithm and key size detection
- Validity period analysis

**Key Classes:**
- `CertificateScanner`: Certificate analysis engine

**Supported Formats:**
- PEM encoded certificates and keys
- DER encoded certificates
- Unencrypted private keys

**Detected Algorithms:**
- RSA (key size extraction)
- DSA (key size extraction)
- ECDSA (curve and key size extraction)

---

#### 3. `pqc_migration_auditor/analysis/`

##### a. `rules.py`
**Purpose:** Cryptographic knowledge base and pattern definitions

**Key Data Structures:**

```python
VULNERABLE_ALGORITHMS = {
    "RSA": VulnerableAlgorithm(
        name="RSA",
        category=AlgorithmCategory.KEY_EXCHANGE,
        risk_level=RiskLevel.QUANTUM_VULNERABLE,
        description="...",
        quantum_threat="Shor's algorithm",
        recommended_alternatives=["ML-KEM-768", "ML-KEM-1024"]
    ),
    # ... ECDSA, DSA, ECDH, etc.
}

CODE_PATTERNS = {
    r'\bRSA\.generate\(': "RSA",
    r'\becdsa\.': "ECDSA",
    # ... 50+ patterns
}
```

**Design Pattern:** Registry Pattern
- Centralized knowledge base
- Easy extension with new algorithms
- Version-controlled algorithm metadata

##### b. `recommendations.py`
**Purpose:** Finding generation and recommendation engine

**Key Classes:**
- `Finding`: Data class for vulnerability findings
- `RecommendationEngine`: Generates PQC recommendations

**Finding Structure:**
```python
@dataclass
class Finding:
    finding_type: str      # CODE, PCAP, CERT
    location: str          # file:line or packet index
    algorithm: str         # RSA, ECDSA, etc.
    key_size: Optional[int]
    risk_level: str        # QUANTUM_VULNERABLE, etc.
    details: str
    raw_data: dict
```

**Recommendation Logic:**
```python
def get_pqc_recommendation(algorithm: str) -> dict:
    if algorithm in ["RSA", "DH"]:
        return ML-KEM family  # Key encapsulation
    elif algorithm in ["ECDSA", "DSA"]:
        return ML-DSA family  # Digital signatures
    # ... hash-based signatures for some cases
```

---

#### 4. `pqc_migration_auditor/reporting/`

##### a. `console_reporter.py`
**Purpose:** Human-readable terminal output

**Features:**
- Color-coded risk levels
- Grouped findings by algorithm
- Summary statistics
- Recommendation sections

##### b. `json_reporter.py`
**Purpose:** Machine-readable JSON output

**Schema:**
```json
{
  "scan_metadata": {
    "tool_version": "1.0.0",
    "scan_timestamp": "ISO-8601",
    "target_path": "...",
    "scan_types": ["code", "pcap", "cert"]
  },
  "findings": [
    {
      "finding_type": "CODE",
      "location": "file.py:42",
      "algorithm": "RSA",
      "key_size": 2048,
      "risk_level": "QUANTUM_VULNERABLE",
      "details": "...",
      "raw_data": {...}
    }
  ],
  "summary": {
    "total_findings": 28,
    "by_algorithm": {...},
    "by_risk_level": {...}
  }
}
```

##### c. `html_reporter.py`
**Purpose:** Interactive HTML report with visualizations

**Features:**
- Responsive design
- Sortable/filterable tables
- Risk level charts
- Collapsible sections
- Copy-to-clipboard for code snippets

---

#### 5. `pqc_migration_auditor/utils/`

##### a. `file_utils.py`
**Purpose:** Safe file system operations

**Key Functions:**
```python
find_scannable_files(directory: Path) -> List[Path]
    # Recursive file discovery with safety checks

is_text_file(file_path: Path) -> bool
    # Extension-based text file detection

validate_output_path(output_path: str) -> Optional[Path]
    # Path validation and directory creation

is_symlink_safe(file_path: Path) -> bool
    # Symlink protection (v1.0.1)
```

**Safety Features:**
- Symlink loop prevention
- File size limits (configurable, default 10MB)
- Path traversal protection
- Proper exception handling

##### b. `logging_utils.py`
**Purpose:** Centralized logging configuration

**Features:**
- Colored output for terminal
- Configurable verbosity levels
- Module-specific loggers
- Proper initialization order (critical fix v1.0.1)

---

## Data Flow

### Code Scanning Flow

```
User Input (directory path)
    │
    ├─> Path Validation (cli.py)
    │
    ├─> File Discovery (file_utils.py)
    │       ├─> Recursive traversal
    │       ├─> Symlink checks
    │       └─> Extension filtering
    │
    ├─> Code Scanning (code_scanner.py)
    │       ├─> For each file:
    │       │   ├─> Read file (respecting size limits)
    │       │   ├─> For each line:
    │       │   │   ├─> Pattern matching
    │       │   │   └─> Deduplication
    │       │   └─> Create findings
    │       └─> Progress logging
    │
    ├─> Analysis (recommendations.py)
    │       ├─> Enrich with algorithm info
    │       ├─> Generate recommendations
    │       └─> Calculate risk levels
    │
    └─> Reporting (console/json/html)
            ├─> Format findings
            ├─> Generate summary
            └─> Output to file/console
```

### PCAP Scanning Flow

```
PCAP File Input
    │
    ├─> PCAP Parsing (scapy)
    │       └─> Load all packets into memory
    │
    ├─> TLS Session Tracking (pcap_scanner.py)
    │       ├─> For each packet:
    │       │   ├─> Extract session ID
    │       │   ├─> Check for TLS layers:
    │       │   │   ├─> Client Hello → store cipher suites
    │       │   │   ├─> Server Hello → analyze selected cipher
    │       │   │   └─> Certificate → parse public key
    │       │   └─> Create findings
    │       └─> Session state management
    │
    ├─> Certificate Analysis (cryptography)
    │       ├─> Parse DER-encoded certs
    │       ├─> Extract public key
    │       └─> Determine algorithm/key size
    │
    └─> Reporting
```

---

## Key Components

### 1. CryptoKnowledgeBase

**Purpose:** Centralized source of truth for cryptographic algorithms

**Design Pattern:** Singleton-like registry

**Contents:**
- 10+ vulnerable algorithms with metadata
- 6+ post-quantum algorithms (NIST standards)
- Quantum threat models
- Migration recommendations

**Usage:**
```python
kb = CryptoKnowledgeBase()
algo_info = kb.get_algorithm_info("RSA")
pqc_alternatives = kb.get_pqc_alternatives("RSA")
```

### 2. Finding Deduplication Engine

**Problem:** Same algorithm detected multiple times per line
**Solution:** Per-line Set-based tracking

**Implementation:**
```python
seen_algorithms: Set[str] = set()
for pattern, algorithm in patterns:
    if matches and algorithm not in seen_algorithms:
        create_finding()
        seen_algorithms.add(algorithm)
```

**Impact:** 15% reduction in false positives (33 → 28 findings in tests)

### 3. Optional Dependency Management

**Problem:** Hard dependencies on scapy/cryptography caused crashes
**Solution:** Try/except import with feature flags

**Pattern:**
```python
try:
    from scapy.all import rdpcap
    SCAPY_AVAILABLE = True
except (ImportError, Exception):
    SCAPY_AVAILABLE = False
    rdpcap = None

# Later:
if not SCAPY_AVAILABLE:
    logger.warning("Scapy not available - PCAP scanning disabled")
    return []
```

**Benefits:**
- Core functionality works without optional dependencies
- Clear user feedback about missing features
- No crashes on import errors

---

## Design Patterns

### 1. **Strategy Pattern** (Scanners)
- Multiple scanner implementations (Code, PCAP, Cert)
- Common interface: `scan() -> List[Finding]`
- CLI orchestrates scanner selection

### 2. **Registry Pattern** (Algorithm Knowledge)
- Central registration of algorithms and patterns
- Easy extension without code changes
- Version-controlled metadata

### 3. **Factory Pattern** (Reporters)
- Reporter selection based on output format
- Common interface: `generate_report(findings) -> str/file`

### 4. **Singleton Pattern** (Logger)
- Single logger instance per module
- Centralized configuration
- Prevents duplicate handlers

### 5. **Decorator Pattern** (Error Handling)
- Graceful degradation wrappers
- Optional dependency checks
- Progress tracking decorators

---

## Extension Points

### Adding New Algorithm Detection

**Step 1:** Update `analysis/rules.py`
```python
VULNERABLE_ALGORITHMS["NEW_ALGO"] = VulnerableAlgorithm(...)
CODE_PATTERNS[r'\bnew_algo_pattern'] = "NEW_ALGO"
```

**Step 2:** Add test case
```python
# tests/test_code_scanner.py
def test_detects_new_algorithm():
    scanner = CodeScanner()
    findings = scanner.scan_line("new_algo.generate()")
    assert any(f.algorithm == "NEW_ALGO" for f in findings)
```

**Step 3:** Update documentation
- README.md algorithm list
- CHANGELOG.md

### Adding New Programming Language

**Step 1:** Update `utils/file_utils.py`
```python
text_extensions = {'.py', '.java', '.go', '.new_lang'}
```

**Step 2:** Add language-specific patterns to `rules.py`
```python
CODE_PATTERNS[r'newlang_crypto_api'] = "ALGORITHM"
```

**Step 3:** Test with sample code
```bash
# examples/sample.newlang
# Scan and verify detection
```

### Adding New Output Format

**Step 1:** Create reporter in `reporting/`
```python
class XMLReporter:
    def generate_report(self, findings: List[Finding]) -> str:
        # XML generation logic
        pass
```

**Step 2:** Register in CLI
```python
if output_format == "xml":
    reporter = XMLReporter()
```

---

## Security Considerations

### Input Validation
- **Path Traversal:** All paths normalized and validated
- **Symlinks:** Detected and skipped to prevent loops
- **File Size:** 10MB default limit prevents DoS
- **File Extensions:** Whitelist-based text file detection

### Output Safety
- **Directory Creation:** Proper permissions, parent directory validation
- **No Arbitrary Writes:** Output paths validated before writing
- **Error Messages:** No sensitive path leakage in production

### Dependency Security
- **Optional Dependencies:** Failures don't crash the tool
- **Version Pinning:** Minimum versions specified in pyproject.toml
- **Regular Updates:** Dependabot integration recommended

### Code Execution Prevention
- **No Dynamic Imports:** All imports static
- **No eval/exec:** Pure pattern matching, no code execution
- **Regex Safety:** Patterns tested for ReDoS vulnerabilities

---

## Performance Characteristics

### Time Complexity

**Code Scanning:**
- **Best Case:** O(n) - single pattern match per file
- **Average Case:** O(n * m * p) where:
  - n = number of files
  - m = average lines per file
  - p = number of patterns (~50)
- **Worst Case:** O(n * m * p) - all patterns checked per line

**Optimizations:**
- Early termination on match
- Deduplication reduces redundant processing
- File size limits prevent extreme cases

**PCAP Scanning:**
- **Complexity:** O(k) where k = number of packets
- **Memory:** Entire PCAP loaded into RAM
- **Limitation:** Large PCAPs (>1GB) may cause memory issues

**Certificate Scanning:**
- **Complexity:** O(c) where c = number of cert files
- **I/O Bound:** DER parsing is fast, disk reads dominate

### Space Complexity

**Memory Usage:**
- **Code Scanning:** O(1) - streaming line-by-line
- **PCAP Scanning:** O(k) - all packets in memory
- **Findings Storage:** O(f) where f = number of findings

**Disk Usage:**
- **Reports:** JSON ~1KB per finding, HTML ~5KB per finding

### Scalability

**Small Projects (<1,000 files):**
- Scan time: <10 seconds
- Memory: <100MB

**Medium Projects (1,000-10,000 files):**
- Scan time: 1-5 minutes
- Memory: <500MB

**Large Projects (>10,000 files):**
- Scan time: 5-30 minutes
- Memory: <1GB
- Progress logging every 100 files

**PCAP Files:**
- Small (<10MB): <1 second
- Medium (10-100MB): 1-10 seconds
- Large (>100MB): 10+ seconds, high memory usage

---

## Threading and Concurrency

**Current Implementation:**
- Single-threaded sequential processing
- No race conditions
- Simple debugging and error handling

**Future Enhancements:**
- Parallel file scanning with `multiprocessing`
- Thread pool for I/O operations
- Async I/O for network operations

---

## Error Handling Strategy

### Levels of Resilience

**1. File-Level Errors (Non-Fatal):**
```python
try:
    scan_file(file_path)
except Exception as e:
    logger.warning(f"Skipping {file_path}: {e}")
    continue  # Don't stop entire scan
```

**2. Scanner-Level Errors (Graceful Degradation):**
```python
if not SCAPY_AVAILABLE:
    logger.warning("PCAP scanning disabled")
    return []  # Continue with other scanners
```

**3. Critical Errors (Fatal):**
```python
if not target_path.exists():
    logger.error("Target path does not exist")
    sys.exit(1)  # Cannot proceed
```

### Logging Strategy

- **DEBUG:** Detailed trace for development
- **INFO:** Progress updates, file counts
- **WARNING:** Non-fatal issues, missing dependencies
- **ERROR:** Fatal errors requiring user action

---

## Testing Architecture

### Test Levels

**1. Unit Tests** (`tests/test_*.py`)
- Individual function testing
- Mocked dependencies
- Fast execution (<1 second)

**2. Integration Tests** (`test_integration.py`)
- End-to-end CLI testing
- Real file I/O
- Multiple output formats
- Medium execution (~10 seconds)

**3. Regression Tests** (`test_basic.py`)
- Known vulnerable code samples
- Expected finding counts
- Backwards compatibility

### Test Coverage Goals

- **Target:** >80% code coverage
- **Critical Paths:** 100% (scanners, pattern matching)
- **Error Handling:** All exception paths tested

---

## Deployment Considerations

### Installation Methods

**1. Pip Install (Recommended):**
```bash
pip install pqc-migration-auditor
```

**2. Development Install:**
```bash
git clone https://github.com/user/PQCMA
cd PQCMA
pip install -e ".[all,dev]"
```

**3. Docker (Future):**
```bash
docker run pqc-auditor scan /target
```

### Environment Requirements

- **Python:** 3.9+ (tested on 3.9, 3.10, 3.11, 3.12)
- **OS:** Linux, macOS, Windows
- **Disk:** 50MB for package
- **RAM:** 100MB-1GB depending on scan size

### CI/CD Integration

**GitHub Actions Example:**
```yaml
- name: Scan for quantum-vulnerable crypto
  run: |
    pip install pqc-migration-auditor
    pqc-audit scan . --output report.json
    # Fail build if critical vulnerabilities found
```

---

## Future Architecture Enhancements

### Planned Improvements

1. **Database Backend:**
   - SQLite for historical scan tracking
   - Trend analysis over time
   - Finding persistence

2. **Plugin System:**
   - Custom scanner plugins
   - Custom reporter plugins
   - Language-specific analyzers

3. **Web Dashboard:**
   - Real-time scanning
   - Multi-project management
   - Team collaboration features

4. **Machine Learning:**
   - False positive reduction
   - Context-aware detection
   - Automatic pattern learning

5. **Integration APIs:**
   - REST API for scan triggers
   - Webhook notifications
   - SIEM integration (Splunk, ELK)

---

## References

- **NIST PQC Standards:** FIPS 203, 204, 205
- **ASD Guidelines:** [Australian Signals Directorate PQC Guidance](https://www.cyber.gov.au/)
- **Python Best Practices:** PEP 8, Type Hints (PEP 484)
- **Security Standards:** OWASP Top 10, CWE

---

**Last Updated:** 2025-11-18
**Version:** 1.0.1
**Maintainer:** Australian Cybersecurity Engineer
