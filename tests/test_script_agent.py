
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from agents.script_agent import ScriptAgent

def test_script_agent_fallback_structure():
    """Verify that the script agent fallback produces correct 1:1 mapping structure."""
    agent = ScriptAgent()
    gherkin = """
    # Positive Scenarios
    Scenario: Happy Path
      Given something
    # Negative Scenarios
    Scenario: Sad Path
      When error
    # Edge Cases
    Scenario: Boundary Path
      Then limit
    """
    
    output = agent._fallback(gherkin)
    
    assert "import pytest" in output
    assert "from playwright.sync_api" in output
    assert "channel=\"msedge\"" in output
    # Check for 1:1 mapping (3 scenarios -> 3 tests)
    assert output.count("def test_") == 3
    # Check for traceability comments
    assert "# Positive" in output
    assert "# Scenario: Happy Path" in output

def test_script_agent_sanitization():
    """Verify that the agent correctly sanitizes scenario titles for python functions."""
    agent = ScriptAgent()
    assert agent._sanitize_test_name("Login Successfully!") == "login_successfully"
    assert agent._sanitize_test_name("Transfer $100.00") == "transfer_10000"
