from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')

print("="*60)
print("GROQ API TEST")
print("="*60)
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key (first 15 chars): {api_key[:15]}...")
print("")

if not api_key:
    print("ERROR: No API key found in .env file")
    exit(1)

try:
    client = Groq(api_key=api_key)
    
    print("Testing Groq API with Llama 3.1 70B...")
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful medical AI assistant."},
            {"role": "user", "content": "Say 'Hello! Groq is working perfectly!' if you can hear me."}
        ],
        temperature=0.7,
        max_tokens=100,
    )
    
    print("SUCCESS!")
    print("")
    print("AI Response:")
    print(response.choices[0].message.content)
    print("")
    print("="*60)
    print("Groq integration is working perfectly!")
    print("="*60)
    
except Exception as e:
    print(f"ERROR: {e}")
    print("")
    print("Possible issues:")
    print("- Invalid API key")
    print("- Network connection problem")
    print("- Quota exceeded")
