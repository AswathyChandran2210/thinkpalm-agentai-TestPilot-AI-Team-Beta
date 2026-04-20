
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from agents.gherkin_agent import GherkinAgent

def test_gherkin_agent_fallback_structure():
    """Verify that the Gherkin agent fallback produces the correct scenario groupings."""
    agent = GherkinAgent()
    flow = "Fund Transfer"
    description = "Move money between accounts."
    
    # Trigger fallback by using logic (or just testing the method directly)
    output = agent._fallback(flow, description)
    
    assert "Feature: Fund Transfer" in output
    assert "# Positive Scenarios" in output
    assert "# Negative Scenarios" in output
    assert "# Edge Cases" in output
    assert output.count("Scenario:") >= 6

def test_gherkin_agent_scenario_count():
    """Ensure the agent aims for at least 6 scenarios as per strict rules."""
    agent = GherkinAgent()
    # Mocking or direct testing of the _should_continue logic
    assert agent._should_continue("") == True
    assert agent._should_continue("Scenario: 1\nScenario: 2\nScenario: 3\n# Negative\n# Edge") == True
    
    full_text = (
        "# Positive Scenarios\n"
        "Scenario: Successful Fund Transfer between two valid accounts\n"
        "  Given the user is on the transfer page\n"
        "  When the user enters a valid amount and accounts\n"
        "  Then the system confirms transfer success\n\n"
        "Scenario: Verify account balances after success\n"
        "  Given a successful fund transfer completed\n"
        "  Then both account balances are updated correctly\n\n"
        "# Negative Scenarios\n"
        "Scenario: Transfer fails due to insufficient funds\n"
        "  When the user enters an amount exceeding balance\n"
        "  Then an 'Insufficient funds' error is displayed\n\n"
        "Scenario: Transfer fails for identical accounts\n"
        "  When the user selects same account for from/to\n"
        "  Then the system blocks the transfer request\n\n"
        "# Edge Cases\n"
        "Scenario: Handle zero dollar transfer request\n"
        "  When the user enters 0 in the amount field\n"
        "  Then a validation error is displayed\n\n"
        "Scenario: Handle maximum allowable transfer amount\n"
        "  When the user enters the maximum transaction limit\n"
        "  Then the system processes the request securely\n"
    )
    # This should return False (meaning it is complete)
    assert agent._should_continue(full_text) == False
