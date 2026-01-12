# tests/conftest.py
"""
Pytest configuration and fixtures for Essen Sales Agent tests.
"""

import sys
import pytest
from pathlib import Path

# Add src to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


@pytest.fixture
def project_root():
    """Return the project root directory"""
    return PROJECT_ROOT


@pytest.fixture
def data_dir(project_root):
    """Return the data directory path"""
    return project_root / "data"


@pytest.fixture
def prompts_dir(project_root):
    """Return the prompts directory path"""
    return project_root / "src" / "agents" / "prompts"


@pytest.fixture
def sample_product():
    """Return a sample product for testing"""
    return {
        "id": "TEST001",
        "description": "Test Product"
    }


@pytest.fixture
def sample_price():
    """Return a sample price record for testing"""
    return {
        "id": "TEST001",
        "base_price": "100000",
        "cash_price": "95000",
        "installments_12": "10000",
        "installments_9": "12500",
        "installments_6": "17500"
    }


@pytest.fixture
def sample_promotion():
    """Return a sample promotion for testing"""
    return {
        "id": "TEST001",
        "name": "Test Promotion",
        "banks": ["GALICIA", "MACRO"],
        "credit_cards": ["VISA", "MASTERCARD"],
        "installments": [3, 6, 12],
        "availability": {"type": "always"},
        "wallets": [],
        "reimbursement": None
    }
