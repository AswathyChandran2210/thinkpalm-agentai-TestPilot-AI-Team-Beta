
import sys
import os
sys.path.append(os.getcwd())

from agents.gherkin_agent import GherkinAgent

def demo_banking_gherkin():
    agent = GherkinAgent()
    flow = "Fund Transfer"
    description = (
        "User should be able to transfer funds from a checking account to a savings account. "
        "The system must validate the balance, ensure account selection is valid, "
        "and handle zero or negative amounts with specific error messages. "
        "A successful transfer should display a confirmation ID and the new balance."
    )
    
    print(f"--- GENERATING BANKING GHERKIN FOR: {flow} ---")
    output = agent.generate(flow, description)
    print(output)

if __name__ == "__main__":
    demo_banking_gherkin()
