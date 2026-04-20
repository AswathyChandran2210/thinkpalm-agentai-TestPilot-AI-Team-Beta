from services.llm_service import generate_response


class ScriptAgent:
    """Agent responsible for converting Gherkin into Playwright Python test scripts."""

    def generate(self, gherkin: str) -> str:
        """Generate a Playwright Python script for the provided Gherkin scenarios."""
        prompt = (
            "You are a Banking QA Expert specialized in the Parabank application (https://parabank.parasoft.com/parabank/index.htm).\n\n"
            "STRICT RULES:\n"
            "1. Generate scripts ONLY from the provided Gherkin scenarios. Do not create extra cases.\n"
            "2. Use real Parabank UI selectors. Mapping:\n"
            "   - Login Page: input[name='username'], input[name='password'], input[value='Log In']\n"
            "   - Sidebar Links: text='Transfer Funds', text='Bill Pay', text='Accounts Overview'\n"
            "   - Transfer Funds: input[name='amount'], select[name='fromAccountId'], select[name='toAccountId'], input[value='Transfer']\n"
            "   - Bill Pay: input[name='payee.name'], input[name='payee.address.street'], input[name='payee.accountNumber'], input[name='amount'], input[value='Send Payment']\n"
            "3. Use real assertion messages. Example:\n"
            "   - Success Transfer: expect(page.locator('text=Transfer Complete!')).to_be_visible()\n"
            "   - Bill Pay Complete: expect(page.locator('text=Bill Payment Complete')).to_be_visible()\n"
            "4. Format: Python + pytest with the sync API.\n"
            "5. Launch Edge: browser = p.chromium.launch(channel=\"msedge\")\n"
            "6. Traceability: Add '# <Type>' and '# Scenario: <name>' comments above each test.\n\n"
            f"Gherkin:\n{gherkin}\n\n"
            "Return ONLY the Python code. No conversational text."
        )

        response = generate_response(
            prompt,
            temperature=0.2,
            max_output_tokens=1800,
            continue_condition=self._should_continue_script,
        )
        if response:
            return response.strip()
        return self._fallback(gherkin)

    def _fallback(self, gherkin: str) -> str:
        lines = [line.strip() for line in gherkin.splitlines() if line.strip()]
        scenarios = []
        current = None
        current_category = "Positive"

        for line in lines:
            if line.startswith("#"):
                lowered_line = line.lower()
                if "negative" in lowered_line:
                    current_category = "Negative"
                elif "edge" in lowered_line:
                    current_category = "Edge"
                elif "positive" in lowered_line:
                    current_category = "Positive"

            if line.startswith("Scenario:"):
                if current is not None:
                    scenarios.append(current)
                current = {
                    "title": line.replace("Scenario:", "", 1).strip(),
                    "category": current_category,
                    "steps": [],
                }
            elif current is not None:
                current["steps"].append(line)

        if current is not None:
            scenarios.append(current)

        output = [
            "import pytest",
            "from playwright.sync_api import sync_playwright, Page, expect",
            "",
            "@pytest.fixture(scope=\"function\")",
            "def page():",
            "    with sync_playwright() as p:",
            "        browser = p.chromium.launch(channel=\"msedge\", headless=False)",
            "        context = browser.new_context()",
            "        page = context.new_page()",
            "        yield page",
            "        browser.close()",
            "",
        ]

        if not scenarios:
            output.append("def test_parabank_placeholder(page: Page):")
            output.append("    # Launch Edge browser: browser = p.chromium.launch(channel=\"msedge\")")
            output.append("    page.goto(\"https://parabank.parasoft.com/parabank/index.htm\")")
            output.append("    # No scenarios detected in Gherkin input.")
        else:
            for scenario in scenarios:
                name = self._sanitize_test_name(scenario["title"])
                output.append(f"# {scenario['category']}")
                output.append(f"# Scenario: {scenario['title']}")
                output.append(f"def test_{name}(page: Page):")
                output.append("    page.goto(\"https://parabank.parasoft.com/parabank/index.htm\")")
                output.append("    # TODO: Login logic if required (input[name='username'], input[name='password'])")
                for step in scenario["steps"]:
                    output.append(f"    # {step}")
                output.append("    # REAL PARABANK SELECTORS:")
                output.append("    # page.fill(\"input[name='amount']\", \"100\")")
                output.append("    # page.select_option(\"select[name='fromAccountId']\", label=\"<account_id>\")")
                output.append("    # page.click(\"input[value='Transfer']\")")
                output.append("    # expect(page.locator(\"text=Transfer Complete!\")).to_be_visible()")
                output.append("    # TODO: Implement additional actions and assertions")
                output.append("")

        return "\n".join(output)

    def _sanitize_test_name(self, title: str) -> str:
        """Convert scenario title to snake_case."""
        sanitized = "".join(c if c.isalnum() or c.isspace() else "" for c in title)
        return sanitized.lower().strip().replace(" ", "_")


    def _should_continue_script(self, text: str) -> bool:
        if not text or len(text.strip()) < 250:
            return True

        if "def test_" not in text:
            return True

        test_count = text.count("def test_")
        if test_count < 3 and text.count("Scenario:") >= 3:
            return True

        return False
