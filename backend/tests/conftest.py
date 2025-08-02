#!/usr/bin/env python3
"""
pytest configuration and fixtures for backend tests
"""

import pytest
import sys
import os

# Ensure backend is in Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


@pytest.fixture(scope="session")
def sample_player_names():
    """Common player names for testing"""
    return [
        "Salah",
        "Haaland", 
        "Son",
        "Kane",
        "De Bruyne"
    ]


@pytest.fixture(scope="session") 
def sample_team_names():
    """Common team names for testing"""
    return [
        "Arsenal",
        "Liverpool", 
        "Man City",
        "Chelsea",
        "Tottenham"
    ]


@pytest.fixture(scope="session")
def test_positions():
    """Valid position names for testing"""
    return [
        "goalkeeper",
        "defender", 
        "midfielder",
        "forward"
    ]


@pytest.fixture(scope="session")
def test_price_ranges():
    """Common price ranges for testing"""
    return [
        (4.0, 6.0),   # Budget players
        (6.0, 8.0),   # Mid-range
        (8.0, 12.0),  # Premium
        (12.0, 15.0)  # Super premium
    ]


def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location/name"""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Mark unit tests (everything else)
        else:
            item.add_marker(pytest.mark.unit)
        
        # Mark potentially slow tests
        if any(keyword in item.name.lower() for keyword in ["large", "complex", "workflow"]):
            item.add_marker(pytest.mark.slow)