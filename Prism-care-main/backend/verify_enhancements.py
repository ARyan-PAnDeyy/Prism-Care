import requests
import json
import time

BASE_URL = "http://localhost:5000/api"
ABHA_ID = "P12345"  # Using a known test ID

def test_health_check():
    print("\n--- Testing Health Check ---")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health Check Passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_chat_endpoint():
    print("\n--- Testing Chat Endpoint ---")
    payload = {
        "abha_id": ABHA_ID,
        "query": "Is it safe to take Aspirin given my history?",
        "history": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            print("✅ Chat Endpoint Passed")
            print("Response:", response.json().get("response"))
        else:
            print(f"❌ Chat Endpoint Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_lab_upload_json():
    print("\n--- Testing Lab Upload (JSON) ---")
    payload = {
        "test_name": "Lipid Profile",
        "results": {
            "cholesterol": {"value": 240, "unit": "mg/dL", "reference_range": "<200", "status": "high"},
            "hdl": {"value": 35, "unit": "mg/dL", "reference_range": ">40", "status": "low"}
        },
        "patient_age": 45,
        "patient_gender": "Male"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/patient/{ABHA_ID}/upload-lab", json=payload)
        if response.status_code == 200:
            print("✅ Lab Upload via JSON Passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Lab Upload Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def main():
    print("Wait for server startup...")
    time.sleep(3)
    test_health_check()
    test_chat_endpoint()
    test_lab_upload_json()

if __name__ == "__main__":
    main()
