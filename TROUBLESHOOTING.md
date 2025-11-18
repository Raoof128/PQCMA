# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the PQC Migration Auditor.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [Scanning Issues](#scanning-issues)
4. [Performance Problems](#performance-problems)
5. [Output and Reporting](#output-and-reporting)
6. [Platform-Specific Issues](#platform-specific-issues)
7. [Getting Help](#getting-help)

---

## Installation Issues

### Problem: `pip install` fails with "No module named 'cryptography'"`

**Symptoms:**
```
ModuleNotFoundError: No module named '_cffi_backend'
```

**Solution:**
The cryptography library requires system dependencies.

**On Ubuntu/Debian:**
```bash
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
pip install --upgrade pip
pip install pqc-migration-auditor
```

**On macOS:**
```bash
brew install openssl
env LDFLAGS="-L$(brew --prefix openssl)/lib" \
    CFLAGS="-I$(brew --prefix openssl)/include" \
    pip install cryptography
pip install pqc-migration-auditor
```

**On Windows:**
```powershell
# Install Visual C++ Build Tools from Microsoft
# Then:
pip install --upgrade pip
pip install pqc-migration-auditor
```

---

### Problem: Scapy installation fails

**Symptoms:**
```
ERROR: Could not build wheels for scapy
```

**Solution:**
Scapy is optional. Install without it:

```bash
pip install pqc-migration-auditor
# Skip scapy - PCAP scanning will be disabled
```

To install scapy separately:
```bash
# Linux/macOS
pip install scapy

# Windows (requires npcap or winpcap)
# Download npcap: https://npcap.com/
pip install scapy
```

---

### Problem: Command `pqc-audit` not found after installation

**Symptoms:**
```bash
pqc-audit: command not found
```

**Solution:**

1. Verify installation:
   ```bash
   pip show pqc-migration-auditor
   ```

2. Check if scripts directory is in PATH:
   ```bash
   # Find installation path
   python -m site --user-base

   # Add to PATH (Linux/macOS)
   export PATH="$PATH:$(python -m site --user-base)/bin"

   # Add to PATH (Windows)
   # Add %APPDATA%\Python\Python311\Scripts to PATH
   ```

3. Alternative: Run as module
   ```bash
   python -m pqc_migration_auditor.cli scan /path/to/code
   ```

---

## Runtime Errors

### Problem: Logger initialization error

**Symptoms:**
```
AttributeError: 'NoneType' object has no attribute 'info'
```

**Solution:**
This was fixed in v1.0.1. Update to the latest version:

```bash
pip install --upgrade pqc-migration-auditor
```

---

### Problem: "PCAP scanning disabled" warning

**Symptoms:**
```
WARNING: Scapy library not available - PCAP scanning disabled
```

**Solution:**
This is normal if scapy is not installed. To enable PCAP scanning:

```bash
pip install scapy
# On Linux, may need libpcap-dev:
sudo apt-get install libpcap-dev
```

---

### Problem: "Certificate scanning disabled" warning

**Symptoms:**
```
WARNING: Cryptography library not available - certificate scanning disabled
```

**Solution:**
Install the cryptography library:

```bash
pip install cryptography
# If fails, see "Installation Issues" above
```

---

### Problem: PermissionError when scanning

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/some/path'
```

**Solutions:**

1. **Check file permissions:**
   ```bash
   ls -la /path/to/scan
   ```

2. **Run with appropriate permissions:**
   ```bash
   # If needed (use with caution):
   sudo pqc-audit scan /protected/path
   ```

3. **Scan a different directory:**
   ```bash
   # Copy to accessible location first
   cp -r /protected/path ~/temp-scan
   pqc-audit scan ~/temp-scan
   ```

---

## Scanning Issues

### Problem: No findings detected in obviously vulnerable code

**Symptoms:**
Scanning code with RSA/ECDSA usage returns 0 findings.

**Diagnostics:**

1. **Check file is being scanned:**
   ```bash
   pqc-audit scan /path --verbose
   # Look for "Scanning file: yourfile.py" messages
   ```

2. **Verify file extension is supported:**
   ```bash
   # Supported: .py, .java, .go, .js, .c, .cpp, etc.
   # Check file extension
   ls -la /path/to/file
   ```

3. **Test with example vulnerable code:**
   ```bash
   pqc-audit scan examples/dummy_repo --verbose
   # Should detect 28+ findings
   ```

4. **Check if patterns match your code:**
   ```python
   # This WILL be detected:
   from cryptography.hazmat.primitives.asymmetric import rsa
   rsa.generate_private_key(65537, 2048)

   # This might NOT be detected (obfuscated):
   algo = getattr(__import__('cryptography'), 'rsa')
   ```

**Solution:**
If using non-standard crypto APIs, consider:
- Opening an issue with code sample
- Contributing pattern additions to `analysis/rules.py`

---

### Problem: Too many false positives

**Symptoms:**
Findings reported for non-vulnerable code (e.g., comments, variable names).

**Examples of False Positives:**
```python
# This comment mentions RSA but doesn't use it
variable_rsa = "just a string"  # False positive
```

**Solutions:**

1. **Use --quiet mode to reduce noise:**
   ```bash
   pqc-audit scan /path --quiet
   ```

2. **Review findings manually:**
   ```bash
   pqc-audit scan /path --output report.json
   # Review JSON report for context
   ```

3. **Report false positive patterns:**
   - Open an issue with code sample
   - We'll improve detection accuracy

---

### Problem: Symlink infinite loop warning

**Symptoms:**
```
WARNING: Skipping symlink: /path/to/link
```

**Solution:**
This is expected behavior. Symlinks are skipped to prevent infinite loops.

To scan symlinked content:
```bash
# Resolve symlink first
REAL_PATH=$(readlink -f /path/to/link)
pqc-audit scan "$REAL_PATH"
```

---

### Problem: File size limit exceeded

**Symptoms:**
```
WARNING: File exceeds size limit (10MB): skipping /path/to/large_file
```

**Solution:**
The default 10MB limit prevents memory issues. Large files are skipped.

**Workarounds:**
1. Split large files manually
2. Scan specific subdirectories
3. Modify scanner code to increase limit (advanced)

---

## Performance Problems

### Problem: Scan is very slow

**Symptoms:**
Scanning takes >10 minutes for medium-sized projects.

**Diagnostics:**

1. **Check project size:**
   ```bash
   find /path/to/scan -type f | wc -l
   # How many files?

   du -sh /path/to/scan
   # How large is the project?
   ```

2. **Use verbose mode to see progress:**
   ```bash
   pqc-audit scan /path --verbose
   # Shows "Scanned 100 files..." every 100 files
   ```

**Solutions:**

1. **Exclude unnecessary directories:**
   ```bash
   # Manually exclude node_modules, vendor, etc.
   find /path -name "*.py" -not -path "*/node_modules/*" > files.txt
   # Then scan specific files
   ```

2. **Scan subdirectories separately:**
   ```bash
   pqc-audit scan /path/src --output src-report.json
   pqc-audit scan /path/lib --output lib-report.json
   ```

3. **Run benchmarks:**
   ```bash
   python benchmark.py
   # Compare your system performance
   ```

**Expected Performance:**
- Small projects (<1,000 files): <10 seconds
- Medium projects (1,000-10,000 files): 1-5 minutes
- Large projects (>10,000 files): 5-30 minutes

---

### Problem: High memory usage

**Symptoms:**
System runs out of memory during large scans.

**Solutions:**

1. **Scan in smaller chunks**
2. **Close other applications**
3. **Use Docker with memory limits:**
   ```bash
   docker run -m 1g pqc-auditor scan /scan
   ```

---

## Output and Reporting

### Problem: Cannot write output file

**Symptoms:**
```
ERROR: Cannot write to output path: /path/to/report.json
```

**Solutions:**

1. **Check directory exists:**
   ```bash
   mkdir -p /path/to/reports
   pqc-audit scan /code --output /path/to/reports/scan.json
   ```

2. **Check write permissions:**
   ```bash
   ls -la /path/to/reports
   # Verify you have write access
   ```

3. **Use relative path:**
   ```bash
   pqc-audit scan /code --output ./report.json
   ```

---

### Problem: HTML report doesn't open correctly

**Symptoms:**
HTML report shows blank page or formatting issues.

**Solutions:**

1. **Check file size:**
   ```bash
   ls -lh report.html
   # Very large reports (>10MB) may be slow to load
   ```

2. **Try different browser:**
   - Chrome/Chromium (recommended)
   - Firefox
   - Safari

3. **Check file encoding:**
   ```bash
   file report.html
   # Should be UTF-8
   ```

---

### Problem: JSON output is not valid

**Symptoms:**
```
json.decoder.JSONDecodeError: Expecting value
```

**Solution:**
This indicates a bug in report generation.

**Workaround:**
```bash
# Use console output instead
pqc-audit scan /path

# Or try verbose mode
pqc-audit scan /path --output report.json --verbose
```

**Report the issue:**
- Include the command you ran
- Attach (sanitized) output if possible

---

## Platform-Specific Issues

### Windows Issues

#### Problem: File path errors

**Symptoms:**
```
FileNotFoundError: [WinError 3] The system cannot find the path specified
```

**Solution:**
Use forward slashes or raw strings:

```powershell
# Instead of:
pqc-audit scan C:\Users\Name\Code

# Use:
pqc-audit scan "C:/Users/Name/Code"

# Or:
pqc-audit scan C:\\Users\\Name\\Code
```

#### Problem: ColoredFormatter errors

**Symptoms:**
Weird characters in console output.

**Solution:**
Enable ANSI color support:

```powershell
# Windows 10+
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1

# Or disable colors:
pqc-audit scan /path --no-color
# (Note: --no-color not implemented yet, use --quiet)
```

---

### macOS Issues

#### Problem: SSL errors during installation

**Symptoms:**
```
[SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solution:**
```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command

# Or:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pqc-migration-auditor
```

---

### Linux Issues

#### Problem: Missing libpcap

**Symptoms:**
```
OSError: libpcap.so.1: cannot open shared object file
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install libpcap0.8

# Fedora/RHEL
sudo dnf install libpcap

# Arch
sudo pacman -S libpcap
```

---

## Docker Issues

### Problem: Permission denied in Docker container

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/scan'
```

**Solution:**
Check volume mount permissions:

```bash
# Ensure local directory is readable
chmod -R +r /path/to/scan

# Run Docker with proper user
docker run --user $(id -u):$(id -g) \
    -v /path/to/scan:/scan:ro \
    pqc-auditor scan /scan
```

---

### Problem: Docker build fails

**Symptoms:**
```
ERROR: failed to solve: process "/bin/sh -c pip install ..." did not complete successfully
```

**Solution:**

1. **Check Docker version:**
   ```bash
   docker --version
   # Should be 20.10+
   ```

2. **Clean Docker cache:**
   ```bash
   docker build --no-cache -t pqc-auditor .
   ```

3. **Check network connectivity:**
   ```bash
   docker run --rm alpine ping -c 3 pypi.org
   ```

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Search existing issues:** https://github.com/Raoof128/PQCMA/issues
3. **Try with verbose output:**
   ```bash
   pqc-audit scan /path --verbose > debug.log 2>&1
   ```
4. **Test with example code:**
   ```bash
   pqc-audit scan examples/dummy_repo --verbose
   ```

### How to Report Issues

When creating an issue, include:

1. **System Information:**
   ```bash
   pqc-audit --version
   python --version
   uname -a  # or "systeminfo" on Windows
   ```

2. **Full command run:**
   ```bash
   pqc-audit scan /path --verbose --output report.json
   ```

3. **Complete error message:**
   ```
   [Paste full error output here]
   ```

4. **Minimal reproduction:**
   - Smallest code sample that reproduces the issue
   - Or use `examples/dummy_repo` if applicable

5. **Expected vs actual behavior:**
   - What you expected to happen
   - What actually happened

### Community Support

- **GitHub Issues:** https://github.com/Raoof128/PQCMA/issues
- **GitHub Discussions:** https://github.com/Raoof128/PQCMA/discussions
- **Documentation:** https://github.com/Raoof128/PQCMA#readme

### Commercial Support

For Australian Government and Defence organizations requiring dedicated support:
- Contact via GitHub Issues with `[ASD]` or `[Defence]` tag
- Indicate classification level and urgency

---

## Debug Mode

For advanced debugging, you can modify the code to enable more verbose logging:

```python
# In pqc_migration_auditor/utils/logging_utils.py
# Change:
logging.DEBUG  # to maximum verbosity
```

Or run Python with debug flags:
```bash
PYTHONVERBOSE=1 pqc-audit scan /path --verbose
```

---

## Known Issues

### Issue: Deduplication reduces findings (v1.0.1)

**Status:** Resolved in v1.0.1

Duplicate findings on the same line are now filtered. This is expected behavior and improves accuracy.

### Issue: Exit code always 1 (v1.0.0)

**Status:** Fixed in v1.0.1

Update to v1.0.1 or later:
```bash
pip install --upgrade pqc-migration-auditor
```

---

**Last Updated:** 2025-11-18
**Version:** 1.0.1

For the latest troubleshooting tips, see: https://github.com/Raoof128/PQCMA/issues
