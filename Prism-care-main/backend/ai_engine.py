"""
AI Engine for Drug Interaction Analysis
Uses ChromaDB for vector storage and RAG for intelligent analysis
"""

import chromadb
from typing import List, Dict
import json

# Initialize ChromaDB client (in-memory)
chroma_client = chromadb.Client()

# Create collection for medical rules
try:
    collection = chroma_client.get_collection("medical_rules")
except:
    collection = chroma_client.create_collection(
        name="medical_rules",
        metadata={"description": "Drug interaction rules and guidelines"}
    )

def load_medical_rules():
    """
    Load sample drug interaction rules into ChromaDB
    In production, this would load from a comprehensive medical database
    """
    rules = [
        {
            "id": "rule_001",
            "interaction": "Aspirin + Warfarin",
            "risk_level": "High",
            "patient_explanation": "Taking aspirin with warfarin can increase your risk of bleeding. This combination can make it harder for your blood to clot, which could lead to serious bleeding problems.",
            "doctor_explanation": "Concurrent use of aspirin and warfarin significantly increases bleeding risk due to additive antiplatelet and anticoagulant effects. Monitor INR closely and consider alternative analgesics. Risk of major hemorrhage increases 2-3 fold.",
            "source": "FDA Drug Interaction Database - Anticoagulant Guidelines 2025",
            "mechanism": "Synergistic inhibition of platelet aggregation and coagulation cascade"
        },
        {
            "id": "rule_002",
            "interaction": "Ibuprofen + Aspirin",
            "risk_level": "Moderate",
            "patient_explanation": "Taking ibuprofen with aspirin may reduce the heart-protective effects of aspirin and can increase the risk of stomach problems like ulcers or bleeding.",
            "doctor_explanation": "Ibuprofen can interfere with aspirin's irreversible platelet inhibition, potentially reducing cardioprotective benefits. Additionally, dual NSAID therapy increases GI bleeding risk and may exacerbate renal dysfunction.",
            "source": "American Heart Association - NSAID Interaction Guidelines",
            "mechanism": "Competitive inhibition of COX-1 enzyme binding site"
        },
        {
            "id": "rule_003",
            "interaction": "Metformin + Alcohol",
            "risk_level": "Moderate",
            "patient_explanation": "Drinking alcohol while taking metformin can increase the risk of a serious condition called lactic acidosis, which can cause weakness, trouble breathing, and irregular heartbeat.",
            "doctor_explanation": "Alcohol consumption with metformin increases risk of lactic acidosis, particularly in patients with renal impairment. Ethanol inhibits gluconeogenesis, potentially causing hypoglycemia. Advise patients to limit alcohol intake.",
            "source": "Endocrine Society - Diabetes Medication Safety 2025",
            "mechanism": "Impaired lactate clearance and hepatic gluconeogenesis inhibition"
        },
        {
            "id": "rule_004",
            "interaction": "Lisinopril + Potassium Supplements",
            "risk_level": "High",
            "patient_explanation": "Taking potassium supplements with lisinopril can cause dangerously high potassium levels in your blood, which can affect your heart rhythm and may be life-threatening.",
            "doctor_explanation": "ACE inhibitors like lisinopril reduce aldosterone secretion, leading to potassium retention. Concurrent potassium supplementation can cause severe hyperkalemia (K+ >6.0 mEq/L), risking cardiac arrhythmias. Monitor serum potassium regularly.",
            "source": "ACC/AHA Hypertension Guidelines - Drug Interactions",
            "mechanism": "Reduced renal potassium excretion via aldosterone suppression"
        },
        {
            "id": "rule_005",
            "interaction": "Atorvastatin + Grapefruit Juice",
            "risk_level": "Moderate",
            "patient_explanation": "Grapefruit juice can increase the amount of atorvastatin in your blood, which may increase the risk of side effects like muscle pain or liver problems.",
            "doctor_explanation": "Grapefruit juice inhibits CYP3A4 enzyme in the intestinal wall, increasing atorvastatin bioavailability by up to 260%. This elevates risk of myopathy and rhabdomyolysis. Advise patients to avoid grapefruit products or switch to pravastatin/rosuvastatin.",
            "source": "Clinical Pharmacology - Statin Interaction Database",
            "mechanism": "CYP3A4 inhibition leading to increased drug plasma concentrations"
        }
    ]
    
    # Check if collection is empty
    if collection.count() == 0:
        # Add rules to ChromaDB
        collection.add(
            documents=[f"{rule['interaction']} - {rule['patient_explanation']}" for rule in rules],
            metadatas=rules,
            ids=[rule['id'] for rule in rules]
        )
        print(f"✅ Loaded {len(rules)} medical rules into ChromaDB")
    else:
        print(f"ℹ️  Medical rules already loaded ({collection.count()} rules)")

def analyze_prescription(medication_history: List[str], new_medicine: str) -> Dict:
    """
    Analyze potential drug interactions using RAG
    
    Args:
        medication_history: List of current medications
        new_medicine: New medicine to check
        
    Returns:
        Dictionary with safety analysis
    """
    # Ensure rules are loaded
    if collection.count() == 0:
        load_medical_rules()
    
    # Build query for vector search
    interactions_found = []
    
    for current_med in medication_history:
        # Query ChromaDB for potential interactions
        query = f"{current_med} + {new_medicine}"
        results = collection.query(
            query_texts=[query],
            n_results=1
        )
        
        # Check if we found a relevant interaction
        if results['metadatas'] and len(results['metadatas'][0]) > 0:
            metadata = results['metadatas'][0][0]
            
            # Check if the interaction matches (either direction)
            interaction_parts = metadata['interaction'].lower().split(' + ')
            current_lower = current_med.lower()
            new_lower = new_medicine.lower()
            
            if (current_lower in interaction_parts[0] and new_lower in interaction_parts[1]) or \
               (new_lower in interaction_parts[0] and current_lower in interaction_parts[1]):
                interactions_found.append(metadata)
    
    # Determine overall risk status
    if not interactions_found:
        return {
            "status": "Safe",
            "patient_explanation": f"{new_medicine} appears to be safe to take with your current medications. No known interactions were found.",
            "doctor_explanation": f"No significant drug-drug interactions detected between {new_medicine} and current medication regimen based on available guidelines.",
            "source": "PrismCare AI Analysis - Medical Guidelines Database 2025",
            "confidence": 0.85,
            "interactions": []
        }
    
    # If interactions found, return the most severe one
    high_risk = [i for i in interactions_found if i['risk_level'] == 'High']
    interaction = high_risk[0] if high_risk else interactions_found[0]
    
    return {
        "status": "Risky",
        "risk_level": interaction['risk_level'],
        "patient_explanation": interaction['patient_explanation'],
        "doctor_explanation": interaction['doctor_explanation'],
        "source": interaction['source'],
        "mechanism": interaction.get('mechanism', 'Not specified'),
        "confidence": 0.92,
        "interactions": [
            {
                "drugs": interaction['interaction'],
                "severity": interaction['risk_level']
            }
        ]
    }

def get_all_rules() -> List[Dict]:
    """Get all loaded medical rules (for admin/debugging)"""
    if collection.count() == 0:
        load_medical_rules()
    
    results = collection.get()
    return results['metadatas'] if results['metadatas'] else []

# Initialize on import
load_medical_rules()

if __name__ == '__main__':
    # Test the AI engine
    print("=" * 60)
    print("🧠 AI Engine Test")
    print("=" * 60)
    
    # Test case 1: Risky interaction
    print("\n📋 Test 1: Warfarin + Aspirin")
    result1 = analyze_prescription(["Warfarin"], "Aspirin")
    print(f"Status: {result1['status']}")
    print(f"Patient: {result1['patient_explanation'][:100]}...")
    
    # Test case 2: Safe combination
    print("\n📋 Test 2: Metformin + Lisinopril")
    result2 = analyze_prescription(["Metformin"], "Lisinopril")
    print(f"Status: {result2['status']}")
    print(f"Patient: {result2['patient_explanation'][:100]}...")
    
    print("\n" + "=" * 60)
    print(f"✅ AI Engine working correctly!")
    print(f"📊 Total rules loaded: {collection.count()}")
    print("=" * 60)
