"""
Quick test to verify Gemini API is working
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("="*70)
print("GEMINI API TEST")
print("="*70)

api_key = os.getenv('GEMINI_API_KEY')
print(f"\nAPI Key present: {bool(api_key)}")
if api_key:
    print(f"API Key (first 20): {api_key[:20]}...")

if not api_key:
    print("ERROR: No API key found!")
    exit(1)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    print("\nCalling Gemini API...")
    response = model.generate_content("Say 'Hello! Gemini is working perfectly!'")
    
    print(f"\n✅ SUCCESS!")
    print(f"Response: {response.text}")
    print("\n" + "="*70)
    print("GEMINI API IS WORKING!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPossible causes:")
    print("1. Invalid API key")
    print("2. API quota exceeded")
    print("3. Network issue")
    print("\nGet new key: https://aistudio.google.com/app/apikey")
