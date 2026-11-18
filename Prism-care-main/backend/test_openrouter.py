"""
Test OpenRouter API and verify it's working
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')

print("="*60)
print("OPENROUTER API TEST")
print("="*60)
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key (first 20 chars): {api_key[:20]}...")
print("")

if not api_key:
    print("ERROR: No API key found!")
    exit(1)

try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
    print("Testing OpenRouter with Llama 3.1...")
    response = client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct:free",
        messages=[
            {"role": "system", "content": "You are a helpful medical AI assistant."},
            {"role": "user", "content": "Provide a detailed medical summary for a patient with diabetes and hypertension. Include key points, risks, and recommendations."}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    print("\nSUCCESS! OpenRouter is working!")
    print("="*60)
    print("AI Response:")
    print(response.choices[0].message.content)
    print("="*60)
    print("\nOpenRouter integration is WORKING PERFECTLY!")
    
except Exception as e:
    print(f"\nERROR: {e}")
    print("\nPossible issues:")
    print("- Invalid API key")
    print("- Network connection problem")
    print("- Rate limit exceeded")
    print("\nCheck: https://openrouter.ai/activity")
