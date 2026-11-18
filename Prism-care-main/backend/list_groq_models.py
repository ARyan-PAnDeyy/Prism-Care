"""
List all available Groq models
"""
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')

if not api_key:
    print("No API key!")
    exit(1)

try:
    client = Groq(api_key=api_key)
    
    # List available models
    models = client.models.list()
    
    print("="*60)
    print("AVAILABLE GROQ MODELS")
    print("="*60)
    
    for model in models.data:
        print(f"\nModel ID: {model.id}")
        print(f"  Created: {model.created}")
        print(f"  Owned by: {model.owned_by}")
    
    print("\n" + "="*60)
    print("RECOMMENDED MODELS FOR MEDICAL USE:")
    print("="*60)
    
    # Test a few common models
    test_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "llama3-70b-8192",
        "llama3-8b-8192"
    ]
    
    for model_name in test_models:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=10
            )
            print(f"✓ {model_name} - WORKING")
        except Exception as e:
            print(f"✗ {model_name} - {str(e)[:50]}")
    
except Exception as e:
    print(f"Error: {e}")
