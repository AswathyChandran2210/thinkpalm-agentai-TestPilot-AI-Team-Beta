
import sys
import os
sys.path.append(os.getcwd())

from agents.orchestrator import OrchestratorAgent

def run_real_world_test():
    orchestrator = OrchestratorAgent()
    
    flow_name = "Fund Transfer"
    feature_description = "Transfer 100 from account 12345 to 67890. Ensure valid balance check."
    
    print(f"--- GENERATING TEST FOR: {flow_name} ---")
    result = orchestrator.orchestrate(flow_name, feature_description)
    
    script_content = result["script"]
    test_file = "test_parabank_generated.py"
    
    with open(test_file, "w") as f:
        f.write(script_content)
    
    print(f"Test script saved to {test_file}")
    print("\n--- RUNNING PYTEST ---")
    
    # Note: Running with --headless=no might not work in some environments, 
    # but the script is configured for msedge.
    # We will try to run it in headless mode if possible or just check for syntax.
    os.system(f"pytest {test_file}")

if __name__ == "__main__":
    run_real_world_test()
