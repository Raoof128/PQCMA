"""
Pytest configuration and shared fixtures.
"""

import pytest
from pathlib import Path


@pytest.fixture
def examples_dir():
    """Get path to examples directory."""
    return Path(__file__).parent.parent / "examples"


@pytest.fixture
def dummy_repo_dir(examples_dir):
    """Get path to dummy repository."""
    return examples_dir / "dummy_repo"


@pytest.fixture
def sample_code_with_rsa():
    """Sample code containing RSA usage."""
    return """
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def generate_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return private_key
"""


@pytest.fixture
def sample_code_with_ecdsa():
    """Sample code containing ECDSA usage."""
    return """
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

def generate_ecdsa_key():
    private_key = ec.generate_private_key(
        ec.SECP256R1(),
        backend=default_backend()
    )
    return private_key
"""
