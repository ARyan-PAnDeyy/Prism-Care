import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("ERROR: No API key found.")
    exit(1)

genai.configure(api_key=api_key)

# List of models to try
models_to_try = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash-latest",
]

print("Testing available Gemini models...")
print("")

working_models = []

for model_name in models_to_try:
    try:
        print(f"Testing: {model_name}...", end=" ")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK' if you can hear me.")
        print(f"SUCCESS")
        working_models.append(model_name)
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"NOT FOUND (404)")
        elif "quota" in error_msg.lower():
            print(f"QUOTA EXCEEDED")
        else:
            print(f"❌ ERROR: {error_msg[:50]}")

print("\n" + "="*60)
if working_models:
    print(f"Working models found: {len(working_models)}")
    for model in working_models:
        print(f"   - {model}")
    print(f"\nRecommended: Use '{working_models[0]}' in .env file")
else:
    print("No working models found!")
    print("   Check your API key or quota limits")
print("="*60)
