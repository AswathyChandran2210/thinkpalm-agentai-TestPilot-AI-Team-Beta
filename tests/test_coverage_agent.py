
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from agents.coverage_agent import CoverageAgent

def test_coverage_agent_report_structure():
    """Verify that the coverage agent fallback produces the structured 5-section report."""
    agent = CoverageAgent()
    gherkin = """
    Scenario: Positive 1
    Scenario: Positive 2
    Scenario: Negative 1
    Scenario: Edge 1
    """
    
    output = agent._fallback("Some description", gherkin)
    
    # Check for all 5 required sections
    assert "1. Coverage Summary" in output
    assert "2. Covered Areas" in output
    assert "3. Missing Scenarios" in output
    assert "4. Risk Areas" in output
    assert "5. Suggested Additional Test Cases" in output
    
    # Check for summary stats
    assert "Total scenarios: 4" in output

def test_coverage_agent_continuation_logic():
    """Verify the logic that determines if a coverage report is complete."""
    agent = CoverageAgent()
    assert agent._should_continue_coverage("") == True
    assert agent._should_continue_coverage("1. Coverage Summary\n3. Missing Scenarios") == True
    
    complete_report = (
        "1. Coverage Summary: All scenarios identified. "
        "2. Covered Areas: Functional testing of login and accounts. "
        "3. Missing Scenarios: No gaps detected in core flows. "
        "4. Risk Areas: Session management and data parity. "
        "5. Suggested Additional Test Cases: Add concurrent login tests. "
        "This is a long enough string to satisfy the 300 character length heuristic used by the agent "
        "to determine if a generation is complete or needs continuation. Adding more text here to "
        "ensure the test passes reliably across different environments."
    )
    assert agent._should_continue_coverage(complete_report) == False
