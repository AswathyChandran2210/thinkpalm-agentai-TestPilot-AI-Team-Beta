import sys
import os
sys.path.append(os.getcwd())
from agents.script_agent import ScriptAgent

# Sample Gherkin mimicking orchestrator output
gherkin_input = """
Feature: Fund Transfer

  # Positive Scenarios
  Scenario: Successful transfer
    Given the user is on transfer page
    When the user transfers $100
    Then the transfer should be complete

  # Negative Scenarios
  Scenario: Insufficient funds
    Given the user has $10
    When the user transfers $100
    Then an error message should appear

  # Edge Cases
  Scenario: Zero amount transfer
    Given the user is on transfer page
    When the user enters $0
    Then a validation message should appear
"""

agent = ScriptAgent()
print("--- GENERATING SCRIPT ---")
output = agent.generate(gherkin_input)
print(output)
print("--- END OF SCRIPT ---")
