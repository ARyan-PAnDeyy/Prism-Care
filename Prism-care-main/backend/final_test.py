from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

print("Testing llama-3.3-70b-versatile...")

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful medical AI assistant."},
            {"role": "user", "content": "Hello! Can you help me understand my medications?"}
        ],
        temperature=0.7,
        max_tokens=150
    )
    
    print("\nSUCCESS! Groq is working!")
    print("="*60)
    print("AI Response:")
    print(response.choices[0].message.content)
    print("="*60)
    
except Exception as e:
    print(f"\nERROR: {e}")
