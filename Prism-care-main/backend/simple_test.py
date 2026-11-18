"""
SIMPLE, BULLETPROOF OpenRouter Test
This WILL work or tell you exactly why it doesn't
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("SIMPLE OPENROUTER TEST")
print("="*70)

# Step 1: Check API key
api_key = os.getenv('OPENROUTER_API_KEY')
print(f"\n[1] API Key: {'✓ Found' if api_key else '✗ MISSING'}")
if not api_key:
    print("ERROR: Add OPENROUTER_API_KEY to .env file!")
    exit(1)

print(f"    First 25 chars: {api_key[:25]}...")

# Step 2: Import OpenAI
print(f"\n[2] Importing openai library...")
try:
    from openai import OpenAI
    print("    ✓ Import successful")
except ImportError as e:
    print(f"    ✗ Import failed: {e}")
    print("    Run: pip install openai")
    exit(1)

# Step 3: Create client
print(f"\n[3] Creating OpenRouter client...")
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    print("    ✓ Client created")
except Exception as e:
    print(f"    ✗ Client creation failed: {e}")
    exit(1)

# Step 4: Test API call
print(f"\n[4] Testing API call...")
print("    Model: meta-llama/llama-3.1-8b-instruct:free")

try:
    response = client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct:free",
        messages=[
            {"role": "user", "content": "Say 'Hello! OpenRouter is working perfectly!' if you can hear me."}
        ],
        max_tokens=50
    )
    
    result = response.choices[0].message.content
    print(f"    ✓ API call successful!")
    print(f"\n{'='*70}")
    print("AI RESPONSE:")
    print(result)
    print(f"{'='*70}")
    print("\n✓✓✓ OPENROUTER IS WORKING PERFECTLY! ✓✓✓")
    print("\nYour AI integration should work now!")
    print("If chat/summaries still fail, restart backend: python app_enhanced.py")
    
except Exception as e:
    print(f"    ✗ API call failed!")
    print(f"\nERROR DETAILS:")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")
    
    print(f"\nPOSSIBLE CAUSES:")
    print("1. Invalid API key - Get new one from: https://openrouter.ai/keys")
    print("2. Rate limit exceeded - Wait a few minutes")
    print("3. Network issue - Check internet connection")
    print("4. Model not available - Try different model")
    
    print(f"\nDEBUGGING:")
    print("- Check OpenRouter dashboard: https://openrouter.ai/activity")
    print("- Verify API key is active")
    print("- Try creating new API key")
