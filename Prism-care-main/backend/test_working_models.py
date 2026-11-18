"""
Test currently working Groq models (Feb 2026)
"""
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    print("ERROR: No API key!")
    exit(1)

client = Groq(api_key=api_key)

# Models to test (in order of preference)
models_to_test = [
    "llama-3.1-8b-instant",      # Fastest, most reliable
    "llama3-70b-8192",            # Better quality
    "llama3-8b-8192",             # Backup
    "mixtral-8x7b-32768",         # Alternative
]

print("="*60)
print("TESTING WORKING GROQ MODELS")
print("="*60)

working_model = None

for model in models_to_test:
    try:
        print(f"\nTesting: {model}...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful medical AI."},
                {"role": "user", "content": "Say 'I am working!' if you can hear me."}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✓ SUCCESS!")
        print(f"  Response: {result}")
        
        if not working_model:
            working_model = model
            
    except Exception as e:
        error_msg = str(e)
        print(f"✗ FAILED: {error_msg[:80]}")

print("\n" + "="*60)
if working_model:
    print(f"RECOMMENDED MODEL: {working_model}")
    print(f"\nUpdate .env file with:")
    print(f"LLM_MODEL={working_model}")
else:
    print("ERROR: No working models found!")
    print("Consider switching to OpenRouter instead.")
print("="*60)
