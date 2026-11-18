"""
Quick test to verify Groq API is actually working
"""
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')

print("Testing Groq API...")
print(f"API Key loaded: {bool(api_key)}")
print(f"API Key (first 20 chars): {api_key[:20] if api_key else 'NONE'}...")

if not api_key:
    print("ERROR: No API key!")
    exit(1)

try:
    client = Groq(api_key=api_key)
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "user", "content": "Say 'Hello! I am working!' if you can hear me."}
        ],
        temperature=0.7,
        max_tokens=50,
    )
    
    print("\nSUCCESS!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    print(f"Error type: {type(e).__name__}")
