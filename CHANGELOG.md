# Changelog

All notable changes to the PQC Migration Auditor will be documented in this file.

## [1.0.1] - 2025-Extensive Polish & Debug - CURRENT

### Enhanced
- **Code Scanner Improvements**
  - Added finding deduplication to prevent multiple detections of the same algorithm on a single line
  - Improved progress logging for large codebases (logs every 100 files)
  - Enhanced error handling with try-except blocks for regex and file processing
  - Added validation for key size extraction (128-16384 bits)
  - Truncated long lines in findings to 200 characters for better readability
  - Added better type hints (Set[str] for deduplication tracking)
  - Graceful handling of file scanning errors (continues scan instead of failing)

- **CLI Interface Improvements**
  - Fixed logger initialization order (now set up before use)
  - Added comprehensive path validation for output files
  - Improved error messages with stderr output
  - Added "no findings" success message when no vulnerabilities detected
  - Better exception handling with specific error types (FileNotFoundError, NotADirectoryError)
  - Added exit code 0 for clean scans (previously always returned 1)
  - Enhanced user feedback for report generation
  - Improved verbose mode integration

- **File Utilities Enhancements**
  - Added symlink detection and skipping to avoid infinite loops
  - Expanded list of excluded directories (added .mypy_cache, virtualenv, .terraform, vendor, etc.)
  - Added more file extensions (.pl, .swift, .kt, .scala, .groovy, .r, .p7b, .p7c)
  - Improved error handling with specific exception types (OSError, PermissionError)
  - Added `validate_output_path()` function for safer file writing
  - Better path validation in `safe_read_file()`
  - Graceful handling of directory traversal failures

- **Certificate Scanner Robustness**
  - Made cryptography library fully optional
  - Graceful degradation when cryptography is not available
  - Better error handling for import failures
  - Clear warning messages when library is missing
  - Prevents crashes when cryptography has dependency issues

- **PCAP Scanner Robustness**
  - Made scapy library fully optional
  - Graceful degradation when scapy is not available
  - Better error handling for import failures
  - Clear warning messages with install instructions
  - Prevents crashes when scapy or cryptography unavailable

- **General Code Quality**
  - Consistent error handling across all modules
  - Better logging throughout
  - More robust type annotations
  - Improved documentation strings
  - Better separation of concerns

### Fixed
- Logger not initialized before use in main() - now properly initialized in CLI constructor
- Duplicate findings from multiple pattern matches on same line - added deduplication
- Silent failures in file_utils - now logs warnings/errors appropriately
- Crashes when cryptography library unavailable - now optional with graceful fallback
- Crashes when scapy library unavailable - now optional with graceful fallback
- No feedback when scanning empty directories - now provides clear message
- Exit code always 1 even for clean scans - now returns 0 when no vulnerabilities found
- Output path validation missing - now validates and creates directories as needed
- Symlink handling could cause infinite loops - now skips symlinks
- Long lines in findings causing display issues - now truncated to 200 chars

### Testing
- Created comprehensive integration test suite (test_integration.py)
- All basic functionality tests passing
- Verified finding deduplication (reduced from 33 to 28 findings in dummy repo)
- Tested graceful handling of missing dependencies
- Validated JSON and HTML report generation
- Tested error handling for nonexistent paths
- Verified verbose and quiet modes

## [1.0.0] - 2025 - Initial Release

### Added
- Initial implementation of PQC Migration Auditor
- Code scanning for quantum-vulnerable crypto patterns
- PCAP scanning for TLS handshake analysis
- Certificate file scanning
- Comprehensive crypto vulnerability knowledge base
- PQC migration recommendations (ML-KEM, ML-DSA, SLH-DSA)
- Multiple output formats (Console, JSON, HTML)
- CLI interface with argparse
- Unit tests with pytest
- Dummy vulnerable repository for testing
- Comprehensive documentation (README, USAGE_EXAMPLES)
- NIST and ASD standards alignment
- Migration checklist with 6-phase implementation guidance
- Professional HTML reports with styling
- Color-coded console output
- Progress tracking and logging
- Modular, extensible architecture

### Standards Support
- NIST FIPS 203 (ML-KEM / CRYSTALS-Kyber)
- NIST FIPS 204 (ML-DSA / CRYSTALS-Dilithium)
- NIST FIPS 205 (SLH-DSA / SPHINCS+)
- Australian Signals Directorate (ASD) PQC Guidance

### Detected Algorithms
- RSA (all key sizes)
- ECDSA / ECDH
- DSA
- Ed25519
- Various elliptic curves (secp256r1, secp384r1, prime256v1)

---

## Version History

- **1.0.1** - Extensive Polish & Debug (CURRENT)
- **1.0.0** - Initial Release
