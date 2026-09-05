"""
Test runner for the edge-case matrix. Loads tests/matrix.yaml and runs each
scenario as a pytest test.

Usage:
  pytest tests/test_matrix.py -v
  pytest tests/test_matrix.py -k "INGEST" -v  # run only ingest tests
"""
import pytest
import yaml
from pathlib import Path

MATRIX_FILE = Path(__file__).parent / "matrix.yaml"


def load_matrix():
    with open(MATRIX_FILE) as f:
        data = yaml.safe_load(f)
    return data["scenarios"]


def pytest_generate_tests(metafunc):
    """Generate one test per scenario."""
    if "scenario" in metafunc.fixturenames:
        scenarios = load_matrix()
        metafunc.parametrize(
            "scenario",
            scenarios,
            ids=[s["id"] for s in scenarios],
        )


def test_scenario(scenario):
    """Run a single scenario from the test matrix.

    Each scenario has:
      - id, name
      - input: dict describing the action or inputs
      - expected: dict describing expected outcomes
      - severity: critical/warning/info
    """
    # Placeholder: in production, route to appropriate test runner
    # based on scenario id prefix (INGEST-*, STORAGE-*, etc.)
    print(f"\n[{scenario['severity'].upper()}] {scenario['id']}: {scenario['name']}")
    print(f"  Input:    {scenario.get('input', {})}")
    print(f"  Expected: {scenario.get('expected', {})}")
    # Mark as xfail for now — actual assertions go here
    pytest.xfail(f"Implementation pending for {scenario['id']}")
