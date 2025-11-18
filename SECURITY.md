# Security Policy

## Supported Versions

We take security seriously. The following versions of PQC Migration Auditor are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in the PQC Migration Auditor, please report it responsibly:

### Reporting Process

1. **Email:** Send details to the project maintainers (create a private security advisory on GitHub)
2. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)
   - Your contact information

3. **Response Time:**
   - You should receive an acknowledgment within 48 hours
   - We aim to provide a detailed response within 7 days
   - We will keep you informed of progress towards a fix

### What to Report

Please report any vulnerabilities including:

- **Code execution vulnerabilities**
- **Path traversal issues**
- **Injection vulnerabilities** (command injection, code injection)
- **Denial of service** vulnerabilities
- **Information disclosure** issues
- **Cryptographic weaknesses** in the tool itself
- **Dependency vulnerabilities** in critical paths

### Out of Scope

The following are generally **not** considered security vulnerabilities:

- Vulnerabilities in the **cryptographic algorithms** the tool detects (that's the point!)
- Issues in the **example vulnerable code** in `examples/dummy_repo/` (intentionally vulnerable)
- **Performance issues** (unless leading to DoS)
- Issues requiring **physical access** to the system
- **Social engineering** attacks

## Security Best Practices for Users

### Running the Tool Safely

1. **Virtual Environment**
   ```bash
   # Always use a virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. **Scan Untrusted Code Safely**
   - Run in a **sandboxed environment** or container
   - Use **restricted file system permissions**
   - Be cautious with `--output` paths (validates automatically in v1.0.1+)

3. **PCAP Files**
   - Scan PCAP files from **trusted sources only**
   - Large PCAP files may consume significant memory
   - Consider file size limits for production use

4. **Dependencies**
   ```bash
   # Regularly update dependencies
   pip install --upgrade -e ".[all]"

   # Check for known vulnerabilities
   pip install safety
   safety check
   ```

### Secure Configuration

- **Limit scan scope** to necessary directories
- **Validate output paths** before running
- **Use `--quiet` mode** in automated systems to avoid log injection
- **Set file size limits** for large codebases

## Dependency Security

We monitor dependencies for known vulnerabilities:

- **cryptography**: Optional dependency, used for certificate parsing
- **scapy**: Optional dependency, used for PCAP analysis

### Checking Dependencies

```bash
# Install security scanner
pip install safety pip-audit

# Scan for vulnerabilities
safety check
pip-audit

# Update vulnerable packages
pip install --upgrade package-name
```

## Security Features

### Current Security Measures

1. **Input Validation**
   - File path validation and sandboxing
   - File size limits (configurable, default 10MB)
   - Symlink detection and skipping

2. **Output Validation**
   - Output path validation
   - Directory creation with proper permissions
   - No arbitrary file writes

3. **Error Handling**
   - Graceful handling of malformed files
   - No stack traces with sensitive paths in production
   - Proper exception handling throughout

4. **Dependency Management**
   - Optional dependencies (scapy, cryptography) prevent forced installations
   - Minimal required dependencies
   - Regular dependency updates

### Known Limitations

1. **Pattern Matching**
   - Uses regex pattern matching (potential ReDoS if patterns are modified)
   - Current patterns tested and validated

2. **File Processing**
   - Reads files into memory (10MB limit by default)
   - May consume significant resources for large scans

3. **PCAP Parsing**
   - Relies on scapy library security
   - Large PCAP files may cause memory issues

## Disclosure Policy

When we receive a security bug report, we will:

1. **Confirm the vulnerability** and determine affected versions
2. **Develop a fix** and create a security advisory
3. **Release a patch** as soon as possible
4. **Publish a security advisory** on GitHub
5. **Credit the reporter** (unless they prefer to remain anonymous)

### Timeline

- **Day 0**: Vulnerability reported
- **Day 1-2**: Acknowledgment sent
- **Day 1-7**: Investigation and validation
- **Day 7-30**: Fix development and testing
- **Day 30**: Public disclosure and patch release

We follow **responsible disclosure** principles and coordinate with reporters.

## Australian Government & Defence Context

### ASD Compliance

For Australian Government users:

- Follow [ASD's Information Security Manual (ISM)](https://www.cyber.gov.au/ism)
- Apply appropriate **PROTECTED** handling if scanning classified code
- Use in **accredited environments** for sensitive workloads
- Review vendor dependencies against ASD's guidance

### Defence Organizations

If using in defence contexts:

- Conduct **security assessment** before deployment
- Review source code and dependencies
- Use in **air-gapped environments** if required
- Follow DSPF and DISP requirements

## Security Contacts

- **GitHub Security Advisories**: Preferred method (create private advisory)
- **Issue Tracker**: For non-security bugs only
- **Discussions**: For security questions (not vulnerabilities)

## Recognition

We appreciate security researchers who responsibly disclose vulnerabilities. Contributors will be acknowledged in:

- Security advisories
- Release notes
- Hall of Fame (if we create one!)

---

**Thank you for helping keep PQC Migration Auditor and its users safe!** 🔒
