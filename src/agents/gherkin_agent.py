from typing import Dict

from services.llm_service import generate_response


class GherkinAgent:
    """Agent responsible for generating BDD Gherkin scenarios."""

    def generate(self, flow: str, feature_description: str) -> str:
        """Generate Gherkin scenarios from the selected flow and feature description."""
        prompt = (
            "You are a Senior QA Automation Architect and specialized Banking QA Expert for the Parabank application (https://parabank.parasoft.com/parabank/index.htm).\n\n"
            "GOAL: Generate high-fidelity, detailed Gherkin BDD scenarios based on the feature description and the selected flow.\n\n"
            "STRICT GENERATION RULES:\n"
            "1. NO GENERIC STEPS: Avoid 'enter details' or 'process request'. Use specific actions like 'clicks the Transfer Funds link' or 'enters 500.00 into the Amount field'.\n"
            "2. FIELD-LEVEL SPECIFICITY: Use actual Parabank field names and realistic test values.\n"
            "3. DATA TABLES: Use Gherkin tables (Step + Data) for input forms wherever multiple fields are involved.\n"
            "4. ERROR MESSAGES: Include exact expected error messages (e.g., 'Insufficient Funds', 'Passwords did not match').\n"
            "5. COVERAGE GROUPS: You must provide scenarios for:\n"
            "   - # Positive Scenarios: Successful end-to-end paths.\n"
            "   - # Negative Scenarios: Validation failures and error paths.\n"
            "   - # Edge Cases: Boundary values, session timeouts, or unexpected input types.\n"
            "   - # Field-Level Validations: Required fields, format checks, and character limits.\n"
            "6. EXECUTABILITY: Ensure steps are clearly mapped to UI actions suitable for Playwright automation.\n\n"
            "FLOW-SPECIFIC REQUIREMENTS FOR: " + flow + "\n"
            "   - If Login: Validate username/password, invalid credentials, empty fields, and session handling.\n"
            "   - If User Registration: Validate First Name, Last Name, Address, Phone, SSN, Username, Password, Confirm Password. Check required fields, password mismatch, and duplicate usernames.\n"
            "   - If Fund Transfer: Validate From Account, To Account, Amount. Check insufficient balance, same account restriction, and invalid amount formats.\n"
            "   - If Bill Payment: Validate Payee Name, Address, Account Number, Amount, From Account. Check invalid payee details and insufficient balance.\n"
            "   - If Account Overview: Validate data visibility, session validation, and correct balance display.\n\n"
            "SYSTEM CONSTRAINTS:\n"
            "- Generate Exactly ONE 'Feature:' block.\n"
            "- The feature name MUST exactly match: " + flow + "\n"
            "- Return ONLY raw Gherkin text. No markdown fences. No preamble.\n\n"
            f"FEATURE DESCRIPTION INPUT:\n{feature_description}\n\n"
            "Produce the complete Gherkin suite following the rules above."
        )

        response = generate_response(
            prompt,
            temperature=0.0,
            max_output_tokens=1800,
            continue_condition=self._should_continue,
        )
        if response:
            return response.strip()
        return self._fallback(flow, feature_description)

    def _fallback(self, flow: str, feature_description: str) -> str:
        import re
        
        # Extract potential keywords (quoted strings, capitalized words, amounts)
        keywords = re.findall(r'"([^"]+)"|([A-Z][a-z]+)|(\$\d+(?:\.\d+)?)|(\d+)', feature_description)
        flat_keywords = [item for sublist in keywords for item in sublist if item]
        
        # Heuristic for the "Primary Subject"
        subject = flat_keywords[0] if flat_keywords else flow
        context = f" involving {subject}" if flat_keywords else ""

        return (
            f"Feature: {flow}\n\n"
            "  # [DRAFT - Fallback Mode] These scenarios were generated via local keyword extraction because the AI service is busy. \n"
            "  # Positive Scenarios\n"
            f"  Scenario: Successful {flow}{context}\n"
            "    Given the user is logged into Parabank and navigates to the proper section\n"
            f"    When the user enters the details described: \"{feature_description[:100]}...\"\n"
            "    And the user confirms the transaction or action\n"
            "    Then the system should process the request successfully as per requirements\n\n"
            "  Scenario: Data persistence and balance check\n"
            "    Given the previous action was initiated\n"
            "    When the user verifies the current state or account summary\n"
            f"    Then the changes related to {subject} should be reflected correctly\n\n"
            "  # Negative Scenarios\n"
            f"  Scenario: Error handling for invalid {subject} data\n"
            "    Given the user provides malformed or incomplete input\n"
            "    When the submission is attempted\n"
            "    Then the application should display a validation error message\n\n"
            f"  Scenario: Authorization or limit failure for {flow}\n"
            "    Given the user does not meet the necessary criteria (e.g. balance or credentials)\n"
            "    When the action is triggered\n"
            "    Then the system should safely decline the request\n\n"
            "  # Edge Cases\n"
            f"  Scenario: Boundary validation for {subject} parameters\n"
            "    Given the user enters values at the minimum or maximum allowed limits\n"
            "    When the request is processed\n"
            "    Then the system should handle the boundary case without crashing\n\n"
            f"  Scenario: Special character and empty field security check for {flow}\n"
            "    Given the user attempts to inject special characters into the input\n"
            "    When the request is submitted\n"
            "    Then the application should treat the input as a potential security risk or invalid format\n"
        )

    def _should_continue(self, text: str) -> bool:
        if not text or len(text.strip()) < 250:
            return True

        lower_text = text.lower()
        if "# negative scenarios" not in lower_text or "# edge cases" not in lower_text:
            return True

        scenario_count = text.count("Scenario:")
        if scenario_count < 6:
            return True

        return False
