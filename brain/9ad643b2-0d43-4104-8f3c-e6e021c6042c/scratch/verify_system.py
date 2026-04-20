
import sys
import os
sys.path.append(os.getcwd())

from agents.orchestrator import OrchestratorAgent

def verify_system_upgrade():
    orchestrator = OrchestratorAgent()
    
    flow_name = "Fund Transfer"
    feature_description = (
        "Transfer 100 from checking account 12345 to savings account 67890. "
        "The user must see 'Transfer Complete!' on success. "
        "If balance is below 100, show 'Insufficient funds'."
    )
    
    print(f"--- RUNNING ORCHESTRATOR FOR FLOW: {flow_name} ---")
    result = orchestrator.orchestrate(flow_name, feature_description)
    
    gherkin = result["gherkin"]
    script = result["script"]
    coverage = result["coverage"]
    
    print("\n[VERIFICATION: GHERKIN]")
    print(f"Feature Title in Gherkin: {'Feature: ' + flow_name in gherkin}")
    print(f"Group # Positive Scenarios: {'# Positive Scenarios' in gherkin}")
    print(f"Group # Negative Scenarios: {'# Negative Scenarios' in gherkin}")
    print(f"Group # Edge Cases: {'# Edge Cases' in gherkin}")
    scenario_count = gherkin.count("Scenario:")
    print(f"Scenario Count: {scenario_count} (Expected >= 6)")
    
    print("\n[VERIFICATION: SCRIPT]")
    print(f"Playwright Sync Fixure: {'@pytest.fixture' in script}")
    print(f"Edge Launch: {'channel=\"msedge\"' in script}")
    test_count = script.count("def test_")
    print(f"Test Function Count: {test_count} (Should match Gherkin scenario count)")
    print(f"Traceability Comments: {'# Scenario:' in script}")
    
    print("\n[VERIFICATION: COVERAGE]")
    sections = [
        "1. Coverage Summary:",
        "2. Covered Areas:",
        "3. Missing Scenarios:",
        "4. Risk Areas:",
        "5. Suggested Additional Test Cases:"
    ]
    all_sections = all(s in coverage for s in sections)
    print(f"All 5 required sections present: {all_sections}")
    
    print("\n--- FULL OUTPUT SNAPSHOT ---")
    print("GHERKIN:\n", gherkin[:300], "...")
    print("\nSCRIPT:\n", script[:300], "...")
    print("\nCOVERAGE:\n", coverage[:300], "...")

if __name__ == "__main__":
    verify_system_upgrade()
