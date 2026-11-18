"""
XAI Feature Testing Script — RAG Edition
Tests all Explainable AI features including the new RAG + Gemini endpoint
"""

import requests
import json

BASE_URL = "http://localhost:5000"


def test_drug_interaction_xai():
    """Test drug interaction analysis with XAI explanations"""
    print("\n" + "="*60)
    print("1. Testing Drug Interaction XAI (check-safety)")
    print("="*60)

    test_cases = [
        {"name": "Critical Risk: Aspirin + Warfarin", "abha_id": "ABHA001", "medicine": "Warfarin"},
        {"name": "Moderate Risk: Ibuprofen",          "abha_id": "ABHA001", "medicine": "Ibuprofen"},
        {"name": "Safe: Paracetamol",                 "abha_id": "ABHA001", "medicine": "Paracetamol"},
    ]

    for test in test_cases:
        print(f"\n📋 {test['name']}")
        print("-" * 60)
        try:
            response = requests.post(
                f"{BASE_URL}/api/check-safety",
                json={"abha_id": test['abha_id'], "medicine": test['medicine']}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Status:       {result.get('status')}")
                print(f"  ⚠️  Risk Level:   {result.get('risk_level', 'N/A')}")
                print(f"  🎯 Confidence:   {result.get('confidence', 0) * 100:.0f}%")
                print(f"  📖 Patient Exp:  {str(result.get('patient_explanation', ''))[:100]}")
                print(f"  🏥 Doctor Exp:   {str(result.get('doctor_explanation', ''))[:100]}")

                # Completeness score
                score = sum([
                    bool(result.get('patient_explanation')),
                    bool(result.get('doctor_explanation')),
                    bool(result.get('mechanism')),
                    bool(result.get('source')),
                    bool(result.get('recommendation')),
                    bool(result.get('confidence')),
                ])
                print(f"  📊 XAI Score:    {score}/6 components present")
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")


def test_xai_explain_endpoint():
    """Test the new RAG + Gemini /api/xai/explain endpoint"""
    print("\n" + "="*60)
    print("2. Testing /api/xai/explain (RAG + Gemini)")
    print("="*60)

    test_cases = [
        {"abha_id": "ABHA001", "medicine": "Aspirin",     "view_mode": "doctor",  "label": "Doctor view — Aspirin"},
        {"abha_id": "ABHA001", "medicine": "Aspirin",     "view_mode": "patient", "label": "Patient view — Aspirin"},
        {"abha_id": "ABHA001", "medicine": "Paracetamol", "view_mode": "doctor",  "label": "Safe drug — Paracetamol"},
    ]

    for test in test_cases:
        print(f"\n📋 {test['label']}")
        print("-" * 60)
        try:
            response = requests.post(
                f"{BASE_URL}/api/xai/explain",
                json={
                    "abha_id": test['abha_id'],
                    "medicine": test['medicine'],
                    "view_mode": test['view_mode']
                }
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Status:           {result.get('status')}")
                print(f"  ⚠️  Risk Level:       {result.get('risk_level', 'N/A')}")
                print(f"  🤖 LLM Used:         {result.get('llm_used')} ({result.get('model', 'N/A')})")
                print(f"  📚 RAG Rules Found:  {len(result.get('rag_retrieved_rules', []))}")
                print(f"  📝 Sources:          {result.get('sources', [])}")
                print(f"\n  💬 Generated Explanation (first 200 chars):")
                print(f"     {str(result.get('generated_explanation', ''))[:200]}")

                # Verify XAI completeness
                xai_complete = all([
                    result.get('generated_explanation'),
                    result.get('rag_retrieved_rules') is not None,
                    result.get('sources'),
                    result.get('status'),
                ])
                print(f"\n  {'✅' if xai_complete else '❌'} Full XAI response: {'complete' if xai_complete else 'incomplete'}")
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")


def test_rag_retrieval_direct():
    """Test ChromaDB retrieval directly (no server needed)"""
    print("\n" + "="*60)
    print("3. Testing RAG Retrieval (Direct — ChromaDB)")
    print("="*60)
    try:
        from xai_rag_engine import retrieve_relevant_context
        queries = [
            "Aspirin Warfarin bleeding interaction",
            "Metformin diabetes glucose",
            "statin CYP3A4 muscle rhabdomyolysis",
        ]
        for q in queries:
            rules = retrieve_relevant_context(q, n_results=3)
            print(f"\n  Query: '{q[:50]}'")
            print(f"  Retrieved {len(rules)} rules:")
            for r in rules:
                print(f"    → {r.get('interaction')} | Risk: {r.get('risk_level')}")
            print(f"  {'✅' if len(rules) > 0 else '❌'} Retrieval {'working' if len(rules) > 0 else 'returned 0 results'}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")


def test_test_recommendations_xai():
    """Test AI test recommendations with rationale"""
    print("\n" + "="*60)
    print("4. Testing Test Recommendations XAI")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/api/patient/ABHA001/test-recommendations")
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            print(f"\n  ✅ Found {len(recommendations)} recommendations")
            for idx, rec in enumerate(recommendations[:3], 1):
                xai_ok = bool(rec.get('rationale')) and bool(rec.get('priority'))
                print(f"\n  📋 #{idx}: {rec.get('test')}")
                print(f"     Priority:  {rec.get('priority')}")
                print(f"     Frequency: {rec.get('frequency')}")
                print(f"     Rationale: {str(rec.get('rationale', ''))[:80]}")
                print(f"     XAI: {'✅' if xai_ok else '❌'}")
        else:
            print(f"  ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")


def test_ai_chat_rag():
    """Test AI chat with RAG + Gemini"""
    print("\n" + "="*60)
    print("5. Testing AI Chat (RAG + Gemini)")
    print("="*60)

    queries = [
        "What drug interactions should I watch out for?",
        "Why am I on Metformin?",
        "What tests should I take?",
    ]
    for query in queries:
        print(f"\n  💬 Query: {query}")
        print("  " + "-" * 55)
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"abha_id": "ABHA001", "query": query, "history": []}
            )
            if response.status_code == 200:
                ai_resp = response.json().get('response', '')
                is_contextual = len(ai_resp) > 50
                print(f"  🤖 Response ({len(ai_resp)} chars):")
                print(f"     {ai_resp[:200]}...")
                print(f"  {'✅' if is_contextual else '❌'} Contextual: {is_contextual}")
            else:
                print(f"  ❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")


if __name__ == "__main__":
    print("\n" + "🚀 PrismCare XAI RAG Feature Testing")
    print("=" * 60)
    print("NOTE: Tests 1, 2, 4, 5 require both servers running:")
    print("  → python mock_abdm_server_enhanced.py  (port 8080)")
    print("  → python app_enhanced.py               (port 5000)")
    print("Test 3 runs directly (no server needed)")
    print("=" * 60)

    # Test 3 runs without any server
    test_rag_retrieval_direct()

    # These need the API server
    tests_needing_server = [
        test_drug_interaction_xai,
        test_xai_explain_endpoint,
        test_test_recommendations_xai,
        test_ai_chat_rag,
    ]
    for t in tests_needing_server:
        try:
            t()
        except requests.exceptions.ConnectionError:
            print(f"\n  ⚠️  Server not running — skipping {t.__name__}")

    print("\n" + "="*60)
    print("✅ XAI RAG Testing Complete!")
    print("="*60)
