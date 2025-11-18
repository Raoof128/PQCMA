"""
File utility functions for the PQC Migration Auditor.
"""

from pathlib import Path
from typing import List, Optional
import mimetypes


def is_text_file(file_path: Path) -> bool:
    """
    Check if a file is likely a text file.

    Args:
        file_path: Path to the file

    Returns:
        True if file appears to be text, False otherwise
    """
    # Check by extension first
    text_extensions = {
        '.py', '.js', '.java', '.c', '.cpp', '.h', '.hpp',
        '.go', '.rs', '.rb', '.php', '.sh', '.bash',
        '.yml', '.yaml', '.json', '.xml', '.toml', '.ini',
        '.txt', '.md', '.rst', '.conf', '.cfg', '.config',
        '.sql', '.cs', '.ts', '.tsx', '.jsx', '.vue',
        '.html', '.css', '.scss', '.sass', '.less'
    }

    if file_path.suffix.lower() in text_extensions:
        return True

    # Try MIME type detection
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and mime_type.startswith('text/'):
        return True

    return False


def is_certificate_file(file_path: Path) -> bool:
    """
    Check if a file is a certificate or key file.

    Args:
        file_path: Path to the file

    Returns:
        True if file is a certificate/key file
    """
    cert_extensions = {'.pem', '.crt', '.cer', '.der', '.key', '.p12', '.pfx'}
    return file_path.suffix.lower() in cert_extensions


def find_scannable_files(
    directory: Path,
    include_certs: bool = True
) -> List[Path]:
    """
    Find all files that should be scanned in a directory.

    Args:
        directory: Root directory to search
        include_certs: Whether to include certificate files

    Returns:
        List of file paths to scan
    """
    scannable_files = []

    # Directories to skip
    skip_dirs = {
        '.git', '.svn', '.hg', 'node_modules', '__pycache__',
        '.venv', 'venv', 'env', '.tox', 'build', 'dist',
        '.idea', '.vscode', '.pytest_cache'
    }

    for file_path in directory.rglob('*'):
        # Skip if not a file
        if not file_path.is_file():
            continue

        # Skip if in an excluded directory
        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
            continue

        # Check if file should be scanned
        if is_text_file(file_path):
            scannable_files.append(file_path)
        elif include_certs and is_certificate_file(file_path):
            scannable_files.append(file_path)

    return scannable_files


def safe_read_file(file_path: Path, max_size_mb: int = 10) -> Optional[str]:
    """
    Safely read a text file with size limits.

    Args:
        file_path: Path to the file
        max_size_mb: Maximum file size in MB

    Returns:
        File contents as string, or None if file too large or unreadable
    """
    try:
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return None

        # Try to read as text
        return file_path.read_text(encoding='utf-8', errors='ignore')

    except Exception:
        return None
