"""Test specific Groq models"""
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Test these models
models_to_test = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "llama-3.1-8b-instant"
]

print("Testing Groq Models...")
print("="*60)

working_model = None

for model in models_to_test:
    try:
        print(f"\nTesting: {model}...", end=" ")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'Working!' if you hear me."}],
            max_tokens=20
        )
        print(f"SUCCESS!")
        print(f"  Response: {response.choices[0].message.content}")
        if not working_model:
            working_model = model
    except Exception as e:
        print(f"FAILED - {str(e)[:60]}")

print("\n" + "="*60)
if working_model:
    print(f"RECOMMENDED MODEL: {working_model}")
else:
    print("No working models found!")
print("="*60)
