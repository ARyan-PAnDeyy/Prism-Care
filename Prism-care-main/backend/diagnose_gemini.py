import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

print("="*60)
print("GEMINI API DIAGNOSTIC")
print("="*60)
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key (first 10 chars): {api_key[:10]}...")
    print(f"API Key length: {len(api_key)}")
print("")

if not api_key:
    print("ERROR: No API key found in .env file")
    exit(1)

genai.configure(api_key=api_key)

# Try to list available models
print("Attempting to list available models...")
try:
    models = genai.list_models()
    print("Available models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
except Exception as e:
    print(f"ERROR listing models: {e}")
    print("")

# Try specific models
print("")
print("Testing specific models:")
print("-"*60)

test_models = [
    "gemini-1.5-flash",
    "gemini-1.5-pro", 
    "gemini-pro",
]

for model_name in test_models:
    try:
        print(f"Testing {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say OK")
        print(f"SUCCESS - Response: {response.text.strip()}")
    except Exception as e:
        error_str = str(e)
        if "404" in error_str:
            print(f"FAILED - Model not found (404)")
        elif "API" in error_str or "key" in error_str.lower():
            print(f"FAILED - API key issue: {error_str[:80]}")
        else:
            print(f"FAILED - {error_str[:80]}")

print("="*60)
