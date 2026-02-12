import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_context_safety_check():
    print("\n--- Testing Context-Aware Safety Check ---")
    
    # Test 1: ABHA003 has 'Ibuprofen' allergy (simulated in app_enhanced.py)
    print("\nTest 1: Allergies (ABHA003 + Ibuprofen)")
    payload = {
        "abha_id": "ABHA003",
        "medicine": "Ibuprofen"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/check-safety", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result.get('status')}")
            print(f"Risk Level: {result.get('risk_level')}")
            print(f"Explanation: {result.get('patient_explanation')}")
            
            if "Allergy" in result.get('patient_explanation', '') or "Critical" in result.get('risk_level', ''):
                print("✅ Allergy Check Passed")
            else:
                print("❌ Allergy Check Failed - Expected Warning")
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

    # Test 2: Drug-Condition (Hypertension + NSAID)
    # We need a patient with Hypertension. Let's assume ABHA002 has it (from previous context, usually does).
    print("\nTest 2: Condition (Hypertension + Naproxen)")
    payload_cond = {
        "abha_id": "ABHA002", # Assuming ABHA002 has Hypertension
        "medicine": "Naproxen"
    }
    try:
        response = requests.post(f"{BASE_URL}/check-safety", json=payload_cond)
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result.get('status')}")
            print(f"Explanation: {result.get('patient_explanation')}")
        else:
            print(f"❌ API Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_context_safety_check()
