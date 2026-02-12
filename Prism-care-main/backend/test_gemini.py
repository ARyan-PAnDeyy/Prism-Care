import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
model_name = os.getenv('LLM_MODEL')

print(f"Key present: {bool(api_key)}")
print(f"Model: {model_name}")

if not api_key:
    print("No API key found.")
    exit(1)

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, can you hear me?")
    print("Success!")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
