
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from agents.gherkin_agent import GherkinAgent

def test_repro():
    load_dotenv()
    agent = GherkinAgent()
    
    # Example flow where it might fail: Bill Payment
    flow = "Bill Payment"
    description = "User wants to pay their electricity bill of $50 to Spark Energy."
    
    print(f"--- Testing Flow: {flow} ---")
    print(f"Description: {description}\n")
    
    result = agent.generate(flow, description)
    print("--- GENERATED OUTPUT ---")
    print(result)
    print("------------------------")

if __name__ == "__main__":
    test_repro()
