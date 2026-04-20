import os
import logging
import time
from typing import Callable, Optional, List, Dict
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

client = None
if API_KEY:
    client = Groq(api_key=API_KEY)

def generate_response(
    prompt: str,
    temperature: float = 0.2,
    max_output_tokens: int = 1600,
    continue_condition: Optional[Callable[[str], bool]] = None,
) -> str:
    """Send a prompt to the Groq model and return the plain text response."""
    if not client:
        logging.warning("GROQ_API_KEY is not configured. Groq requests will not be executed.")
        return ""

    retries = 2
    delay = 2  # Initial delay in seconds

    # Initial message for the chat
    messages = [{"role": "user", "content": prompt}]

    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
            )
            
            result = response.choices[0].message.content or ""
            
            # Check if we need to continue (long output handling)
            if continue_condition and continue_condition(result):
                logging.info("Continuation condition met. Requesting completion...")
                # Add the assistant's partial response to history
                messages.append({"role": "assistant", "content": result})
                # Add the continuation prompt
                messages.append({"role": "user", "content": "Continue the previous output and complete the response without repeating text."})
                
                continuation = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_output_tokens,
                )
                
                continuation_text = continuation.choices[0].message.content or ""
                if continuation_text:
                    result = f"{result}\n{continuation_text}".strip()
            
            return result.strip()

        except Exception as e:
            error_str = str(e).lower()
            # Handle rate limits (429) specifically for Groq
            if "rate limit" in error_str or "429" in error_str:
                if attempt < retries:
                    logging.warning(f"Groq API rate limit hit. Retrying in {delay} seconds (Attempt {attempt+1}/{retries})...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    logging.error("Groq API rate limit exceeded after retries.")
                    return ""
            else:
                logging.exception("Groq API call failed")
                return ""
                
    return ""
