from services.llm_service import generate_response


class CoverageAgent:
    """Agent responsible for generating coverage analysis reports."""

    def analyze(self, feature_description: str, gherkin: str) -> str:
        """Analyze feature coverage and report gaps, risks, and suggested test cases."""
        if not feature_description and not gherkin:
            return "Coverage analysis requires a feature description and generated Gherkin scenarios."

        prompt = (
            "You are a Banking QA Expert. Analyze the feature description and generated Gherkin scenarios below for the Parabank application.\n\n"
            "STRICT REPORT STRUCTURE:\n"
            "1. Coverage Summary\n"
            "2. Covered Areas\n"
            "3. Missing Scenarios (Focus on Parabank specific gaps: overdraws, invalid payees, unauthorized access, etc.)\n"
            "4. Risk Areas (Focus on financial and data integrity risks)\n"
            "5. Suggested Additional Test Cases (Specific scenarios to achieve high-assurance banking coverage)\n\n"
            "QUALITY RULES:\n"
            "- Use logical reasoning to identify gaps based on the feature requirements.\n"
            "- Ensure the report identifies missing edge cases like empty inputs or session timeouts where relevant.\n\n"
            f"Feature Description:\n{feature_description}\n\n"
            f"Generated Gherkin:\n{gherkin}\n"
        )

        response = generate_response(
            prompt,
            temperature=0.2,
            max_output_tokens=1200,
            continue_condition=self._should_continue_coverage,
        )
        if response:
            return response.strip()
        return self._fallback(feature_description, gherkin)

    def _fallback(self, feature_description: str, gherkin: str) -> str:
        lines = [line.strip() for line in gherkin.splitlines() if line.strip()]
        positive = sum(1 for line in lines if line.lower().startswith("scenario:") and ("positive" in line.lower() or "successful" in line.lower() or "valid" in line.lower()))
        negative = sum(1 for line in lines if line.lower().startswith("scenario:") and ("negative" in line.lower() or "invalid" in line.lower() or "error" in line.lower()))
        edge = sum(1 for line in lines if line.lower().startswith("scenario:") and ("edge" in line.lower() or "boundary" in line.lower() or "special" in line.lower()))
        total = positive + negative + edge

        return (
            "1. Coverage Summary:\n"
            f"   - Total scenarios: {total}\n"
            f"   - Count of Positive: {positive} / Negative: {negative} / Edge: {edge}\n\n"
            "2. Covered Areas:\n"
            "   - Core functional requirements identified in the feature description.\n\n"
            "3. Missing Scenarios:\n"
            "   - Specific validation paths not fully detailed in the current scenarios.\n\n"
            "4. Risk Areas:\n"
            "   - Input boundaries and error handling for unexpected system states.\n\n"
            "5. Suggested Additional Test Cases:\n"
            "   - Add scenarios for extremely long inputs and concurrent transaction collisions.\n"
        )

    def _should_continue_coverage(self, text: str) -> bool:
        if not text or len(text.strip()) < 300:
            return True

        lower_text = text.lower()
        if "coverage summary" not in lower_text or "missing scenarios" not in lower_text or "risk areas" not in lower_text:
            return True

        return False
