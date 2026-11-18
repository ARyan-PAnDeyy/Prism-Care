"""
COMPREHENSIVE DIAGNOSTIC SCRIPT
Tests everything and provides detailed report
"""
import os
import sys
from dotenv import load_dotenv

print("="*70)
print("PRISMCARE AI SYSTEM DIAGNOSTIC")
print("="*70)

load_dotenv()

# 1. Check Environment Variables
print("\n[1] ENVIRONMENT VARIABLES")
print("-"*70)
openrouter_key = os.getenv('OPENROUTER_API_KEY')
use_llm = os.getenv('USE_LLM')
model = os.getenv('LLM_MODEL')

print(f"OPENROUTER_API_KEY: {'✓ Present' if openrouter_key else '✗ MISSING'}")
if openrouter_key:
    print(f"  First 20 chars: {openrouter_key[:20]}...")
print(f"USE_LLM: {use_llm}")
print(f"LLM_MODEL: {model}")

# 2. Test OpenRouter API
print("\n[2] OPENROUTER API TEST")
print("-"*70)
if not openrouter_key:
    print("✗ Cannot test - no API key!")
else:
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key
        )
        
        print(f"Testing model: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'API Working!'"}],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        print(f"✓ API WORKING!")
        print(f"  Response: {result}")
        
    except Exception as e:
        print(f"✗ API FAILED!")
        print(f"  Error: {str(e)[:100]}")

# 3. Check AI Modules
print("\n[3] AI MODULES CHECK")
print("-"*70)
try:
    from ai_summarizer import MedicalSummarizer
    summarizer = MedicalSummarizer()
    print(f"✓ ai_summarizer.py loaded")
    print(f"  Client initialized: {summarizer.client is not None}")
    print(f"  Model: {summarizer.model}")
except Exception as e:
    print(f"✗ ai_summarizer.py FAILED: {e}")

try:
    from ai_engine_enhanced import chat_with_context
    print(f"✓ ai_engine_enhanced.py loaded")
except Exception as e:
    print(f"✗ ai_engine_enhanced.py FAILED: {e}")

try:
    from lab_analyzer import analyze_lab_report
    print(f"✓ lab_analyzer.py loaded")
except Exception as e:
    print(f"✗ lab_analyzer.py FAILED: {e}")

# 4. Test Chat Function
print("\n[4] CHAT FUNCTION TEST")
print("-"*70)
try:
    from ai_engine_enhanced import chat_with_context
    
    test_context = {
        "age": 45,
        "gender": "Male",
        "allergies": ["Penicillin"],
        "conditions": ["Diabetes"],
        "medications": ["Metformin"]
    }
    
    response = chat_with_context([], "Hello, can you help me?", test_context)
    
    if "apologize" in response.lower() or "trouble" in response.lower():
        print(f"✗ CHAT FAILED - Error response")
        print(f"  Response: {response[:100]}...")
    else:
        print(f"✓ CHAT WORKING!")
        print(f"  Response length: {len(response)} chars")
        print(f"  First 100 chars: {response[:100]}...")
        
except Exception as e:
    print(f"✗ CHAT TEST FAILED: {e}")

# 5. Summary
print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)
print("\nIf any tests failed, check:")
print("1. OpenRouter API key is correct")
print("2. All dependencies installed (pip install openai)")
print("3. Backend restarted after .env changes")
print("4. Check terminal for detailed error messages")
