
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from services.llm_service import generate_response

def test_groq_connectivity():
    load_dotenv()
    prompt = "Hello Groq! Respond with 'Connected' if you can read this."
    print("Testing Groq Connectivity...")
    result = generate_response(prompt)
    print(f"Result: {result}")
    
    if "Connected" in result:
        print("SUCCESS: Groq migration verified.")
    else:
        print("WARNING: Groq response received but content mismatch.")

if __name__ == "__main__":
    test_groq_connectivity()
