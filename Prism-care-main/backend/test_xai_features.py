"""
XAI Feature Testing Script
Tests the Explainable AI features in PrismCare
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_drug_interaction_xai():
    """Test drug interaction analysis with XAI explanations"""
    print("\n" + "="*60)
    print("Testing Drug Interaction XAI Features")
    print("="*60)
    
    test_cases = [
        {
            "name": "Critical Risk: Aspirin + Warfarin",
            "abha_id": "ABHA001",
            "medicine": "Warfarin"
        },
        {
            "name": "Moderate Risk: Ibuprofen + Aspirin",
            "abha_id": "ABHA001",
            "medicine": "Ibuprofen"
        },
        {
            "name": "Safe: Paracetamol",
            "abha_id": "ABHA001",
            "medicine": "Paracetamol"
        }
    ]
    
    for test in test_cases:
        print(f"\n📋 Test Case: {test['name']}")
        print("-" * 60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/check-safety",
                json={
                    "abha_id": test['abha_id'],
                    "medicine": test['medicine']
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Status: {result.get('status')}")
                print(f"⚠️  Risk Level: {result.get('risk_level', 'N/A')}")
                print(f"🎯 Confidence: {result.get('confidence', 0) * 100:.0f}%")
                print(f"\n📖 Patient Explanation:")
                print(f"   {result.get('patient_explanation', 'N/A')[:150]}...")
                print(f"\n🏥 Doctor Explanation:")
                print(f"   {result.get('doctor_explanation', 'N/A')[:150]}...")
                
                if result.get('mechanism'):
                    print(f"\n🔬 Mechanism:")
                    print(f"   {result['mechanism'][:150]}...")
                
                if result.get('source'):
                    print(f"\n📚 Evidence Source:")
                    print(f"   {result['source']}")
                
                if result.get('recommendation'):
                    print(f"\n💡 Recommendation:")
                    print(f"   {result['recommendation'][:150]}...")
                
                # Verify XAI completeness
                xai_score = 0
                if result.get('patient_explanation'): xai_score += 1
                if result.get('doctor_explanation'): xai_score += 1
                if result.get('mechanism'): xai_score += 1
                if result.get('source'): xai_score += 1
                if result.get('recommendation'): xai_score += 1
                if result.get('confidence'): xai_score += 1
                
                print(f"\n📊 XAI Completeness: {xai_score}/6 components present")
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def test_test_recommendations_xai():
    """Test AI test recommendations with rationale"""
    print("\n" + "="*60)
    print("Testing Test Recommendations XAI")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/patient/ABHA001/test-recommendations")
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            
            print(f"\n✅ Found {len(recommendations)} test recommendations")
            
            for idx, rec in enumerate(recommendations[:3], 1):  # Show first 3
                print(f"\n📋 Recommendation {idx}:")
                print(f"   Test: {rec.get('test')}")
                print(f"   Priority: {rec.get('priority')}")
                print(f"   Frequency: {rec.get('frequency')}")
                print(f"   Rationale: {rec.get('rationale', 'N/A')[:100]}...")
                
                # Verify XAI elements
                has_rationale = bool(rec.get('rationale'))
                has_priority = bool(rec.get('priority'))
                has_frequency = bool(rec.get('frequency'))
                
                xai_complete = has_rationale and has_priority and has_frequency
                print(f"   XAI Complete: {'✅' if xai_complete else '❌'}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_ai_chat_xai():
    """Test AI chat with context-aware explanations"""
    print("\n" + "="*60)
    print("Testing AI Chat XAI Features")
    print("="*60)
    
    queries = [
        "Why is this patient on Metformin?",
        "Are there any drug interactions?",
        "What tests should I order next?"
    ]
    
    for query in queries:
        print(f"\n💬 Query: {query}")
        print("-" * 60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={
                    "abha_id": "ABHA001",
                    "query": query,
                    "history": []
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '')
                
                print(f"🤖 AI Response:")
                print(f"   {ai_response[:200]}...")
                
                # Check if response is contextual and explanatory
                is_contextual = len(ai_response) > 50
                print(f"\n   Contextual: {'✅' if is_contextual else '❌'}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("\n🚀 PrismCare XAI Feature Testing")
    print("="*60)
    print("Testing Explainable AI components...")
    
    # Run all tests
    test_drug_interaction_xai()
    test_test_recommendations_xai()
    test_ai_chat_xai()
    
    print("\n" + "="*60)
    print("✅ XAI Testing Complete!")
    print("="*60)
