"""
XAI RAG Engine for PrismCare
Retrieval-Augmented Generation (RAG) for Explainable AI explanations
Uses ChromaDB for retrieval and Gemini LLM for generation
"""

import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")

# ─── ChromaDB shared collection (imported from ai_engine_enhanced) ──────────
try:
    from ai_engine_enhanced import collection as drug_rules_collection
    _CHROMA_READY = True
except Exception as e:
    print(f"[XAI-RAG] ⚠️  Could not import ChromaDB collection: {e}")
    _CHROMA_READY = False

# ─── Gemini client ─────────────────────────────────────────────────────────
_gemini_model = None

def _get_gemini_model():
    """Lazy-load Gemini model (only when needed)."""
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model

    if not USE_LLM:
        return None
    if not GEMINI_API_KEY:
        print("[XAI-RAG] ⚠️  GEMINI_API_KEY not set — falling back to rule-based mode")
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(LLM_MODEL)
        print(f"[XAI-RAG] ✅ Gemini model loaded: {LLM_MODEL}")
        return _gemini_model
    except Exception as e:
        print(f"[XAI-RAG] ⚠️  Could not load Gemini: {e}")
        return None


# ─── RAG Retrieval ──────────────────────────────────────────────────────────

def retrieve_relevant_context(query: str, n_results: int = 5) -> List[Dict]:
    """
    Retrieve the most relevant drug interaction rules from ChromaDB.

    Args:
        query: Natural language query (e.g., "Aspirin + Warfarin interaction")
        n_results: Number of top results to return

    Returns:
        List of relevant rule dicts from ChromaDB metadata
    """
    if not _CHROMA_READY:
        return []

    try:
        results = drug_rules_collection.query(
            query_texts=[query],
            n_results=min(n_results, drug_rules_collection.count())
        )

        retrieved = []
        if results and results.get("metadatas") and results["metadatas"][0]:
            for meta in results["metadatas"][0]:
                retrieved.append(meta)

        print(f"[XAI-RAG] 🔍 Retrieved {len(retrieved)} rules for query: '{query[:60]}...'")
        return retrieved

    except Exception as e:
        print(f"[XAI-RAG] ⚠️  ChromaDB retrieval error: {e}")
        return []


# ─── Gemini Generation ──────────────────────────────────────────────────────

def _generate_with_gemini(prompt: str, fallback: str) -> str:
    """
    Generate text using Gemini. Returns fallback string if Gemini is unavailable.
    """
    model = _get_gemini_model()
    if model is None:
        return fallback

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        print(f"[XAI-RAG] ✅ Gemini generated response ({len(text)} chars)")
        return text
    except Exception as e:
        print(f"[XAI-RAG] ⚠️  Gemini generation error: {e} — using fallback")
        return fallback


# ─── Core XAI Functions ─────────────────────────────────────────────────────

def explain_drug_interaction(
    medication_history: List[str],
    new_drug: str,
    interaction_data: Dict,
    patient_context: Dict,
    view_mode: str = "doctor"
) -> Dict:
    """
    Generate a rich XAI explanation for a drug interaction using RAG + Gemini.

    Args:
        medication_history: List of current medications
        new_drug: New drug being checked
        interaction_data: Result from analyze_prescription()
        patient_context: Patient allergies, conditions, age, gender
        view_mode: 'doctor' or 'patient'

    Returns:
        Dict with full XAI explanation including RAG-retrieved evidence
    """

    # 1. Build retrieval query
    drug_pair = f"{', '.join(medication_history[:3])} + {new_drug}"
    query = f"{drug_pair} drug interaction mechanism risk"

    # 2. Retrieve relevant rules from ChromaDB
    retrieved_rules = retrieve_relevant_context(query, n_results=5)

    # 3. Build context string from retrieved rules
    rag_context_parts = []
    for rule in retrieved_rules[:3]:  # Use top 3
        rag_context_parts.append(
            f"- {rule.get('interaction', '')}: {rule.get('mechanism', '')} "
            f"(Risk: {rule.get('risk_level', 'Unknown')}) — Source: {rule.get('source', 'Clinical DB')}"
        )
    rag_context = "\n".join(rag_context_parts) if rag_context_parts else "No specific rules found."

    # 4. Patient context string
    age = patient_context.get("age", "Unknown")
    gender = patient_context.get("gender", "Unknown")
    conditions = patient_context.get("conditions", [])
    allergies = patient_context.get("allergies", [])
    patient_info = (
        f"Age: {age}, Gender: {gender}, "
        f"Conditions: {', '.join(conditions) if conditions else 'None'}, "
        f"Allergies: {', '.join(allergies) if allergies else 'None'}"
    )

    # 5. Existing analysis data
    status = interaction_data.get("status", "Unknown")
    risk_level = interaction_data.get("risk_level", "N/A")
    existing_mechanism = interaction_data.get("mechanism", "Not specified")
    existing_recommendation = interaction_data.get("recommendation", "Consult healthcare provider")

    # 6. Build Gemini prompt — tailored for doctor or patient
    if view_mode == "patient":
        prompt = f"""You are a friendly medical AI assistant explaining a drug safety check to a patient.

PATIENT PROFILE: {patient_info}
MEDICATIONS BEING CHECKED: {drug_pair}
SAFETY STATUS: {status} (Risk: {risk_level})

RELEVANT MEDICAL KNOWLEDGE (from clinical database):
{rag_context}

Task: Write a clear, compassionate, and easy-to-understand explanation for this patient:
1. Start with what the safety check found (1-2 sentences, plain English)
2. Explain what risk means in everyday terms (avoid jargon)
3. Give 2-3 practical steps the patient should take
4. End with reassurance and encourage them to speak with their doctor

Keep the total response under 250 words. Use simple language — no medical abbreviations.
Format with clear sections using line breaks, no markdown headers."""

    else:  # doctor mode
        prompt = f"""You are a clinical decision support AI providing an XAI (Explainable AI) explanation to a healthcare provider.

PATIENT PROFILE: {patient_info}
MEDICATIONS BEING CHECKED: {drug_pair}
SAFETY STATUS: {status} (Risk: {risk_level})

RETRIEVED CLINICAL EVIDENCE (from RAG knowledge base):
{rag_context}

ANALYSIS DETAILS:
- Mechanism: {existing_mechanism}
- Recommendation: {existing_recommendation}

Task: Generate a comprehensive clinical XAI explanation with:
1. **Clinical Summary** (2-3 sentences): What interaction or risk was identified
2. **Pharmacological Mechanism**: How this interaction occurs at a molecular/physiological level
3. **Evidence Base**: Reference the retrieved clinical guidelines above
4. **Risk Stratification**: Factors that increase/decrease risk for this specific patient
5. **Clinical Recommendation**: Evidence-based management plan (dosing, monitoring, alternatives)

Keep response under 350 words. Use clinical terminology. Format with clear sections."""

    # 7. Generate with Gemini (or use rule-based fallback)
    fallback_explanation = (
        interaction_data.get("doctor_explanation") if view_mode == "doctor"
        else interaction_data.get("patient_explanation", "Please consult your healthcare provider for details.")
    )

    generated_explanation = _generate_with_gemini(prompt, fallback_explanation or "")

    # 8. Compile sources from retrieved rules
    sources = list({
        rule.get("source", "Clinical Database")
        for rule in retrieved_rules[:3]
        if rule.get("source")
    })
    if not sources:
        sources = ["PrismCare Clinical Knowledge Base"]

    return {
        "generated_explanation": generated_explanation,
        "rag_retrieved_rules": [
            {
                "interaction": rule.get("interaction"),
                "risk_level": rule.get("risk_level"),
                "mechanism": rule.get("mechanism"),
                "source": rule.get("source")
            }
            for rule in retrieved_rules[:3]
        ],
        "sources": sources,
        "rag_context_used": rag_context,
        "view_mode": view_mode,
        "llm_used": _get_gemini_model() is not None,
        "model": LLM_MODEL if _get_gemini_model() is not None else "rule-based-fallback"
    }


def generate_rag_chat_response(
    user_query: str,
    patient_context: Dict,
    history: List[Dict]
) -> str:
    """
    Generate a RAG-powered chat response using ChromaDB + Gemini.

    Args:
        user_query: User's question
        patient_context: Patient's medical info
        history: Previous conversation turns

    Returns:
        AI-generated response string
    """

    # 1. Retrieve relevant context from ChromaDB
    retrieved_rules = retrieve_relevant_context(user_query, n_results=4)

    rag_context_parts = []
    for rule in retrieved_rules:
        rag_context_parts.append(
            f"- {rule.get('interaction', '')}: Risk={rule.get('risk_level', '?')} | "
            f"Mechanism: {rule.get('mechanism', 'N/A')} | "
            f"Recommendation: {rule.get('recommendation', 'N/A')[:100]}"
        )
    rag_context = "\n".join(rag_context_parts) if rag_context_parts else "No specific drug rules retrieved."

    # 2. Patient context
    age = patient_context.get("age", "Unknown")
    gender = patient_context.get("gender", "Unknown")
    conditions = patient_context.get("conditions", [])
    allergies = patient_context.get("allergies", [])
    medications = patient_context.get("medications", [])

    # 3. Build conversation history
    history_text = ""
    if history:
        for turn in history[-4:]:  # Last 4 turns
            role = turn.get("role", "user")
            content = turn.get("content", "")
            history_text += f"\n{role.upper()}: {content[:200]}"

    # 4. Build Gemini prompt
    prompt = f"""You are PrismCare, an intelligent medical AI assistant with access to the patient's health records.

PATIENT PROFILE:
- Age: {age}, Gender: {gender}
- Conditions: {', '.join(conditions) if conditions else 'None recorded'}
- Allergies: {', '.join(allergies) if allergies else 'None recorded'}
- Active Medications: {', '.join(medications) if medications else 'None recorded'}

RELEVANT CLINICAL KNOWLEDGE (retrieved from medical database):
{rag_context}

CONVERSATION HISTORY:{history_text if history_text else ' [Start of conversation]'}

USER QUESTION: {user_query}

Instructions:
- Answer based on patient's specific health profile above
- Reference relevant retrieved clinical knowledge when applicable
- Be helpful, empathetic, and accurate
- If a question is outside your scope, recommend consulting a healthcare provider
- Keep response concise (under 300 words) but comprehensive
- Use markdown formatting for clarity (bold key points, bullet lists)
- NEVER make up medical facts — only use provided context"""

    # 5. Fallback response (keyword-based)
    fallback = _keyword_fallback_response(user_query, patient_context)

    # 6. Generate
    return _generate_with_gemini(prompt, fallback)


def _keyword_fallback_response(query: str, patient_context: Dict) -> str:
    """Simple keyword-based fallback when Gemini is unavailable."""
    query_lower = query.lower()
    conditions = patient_context.get("conditions", [])
    medications = patient_context.get("medications", [])
    allergies = patient_context.get("allergies", [])
    age = patient_context.get("age", "Unknown")
    gender = patient_context.get("gender", "Unknown")

    if any(w in query_lower for w in ["hello", "hi", "hey"]):
        return (
            f"Hello! I'm your PrismCare AI assistant.\n\n"
            f"**Your Profile:** {age} year old {gender}\n"
            f"**Conditions:** {', '.join(conditions) if conditions else 'None'}\n"
            f"**Medications:** {', '.join(medications) if medications else 'None'}\n\n"
            f"How can I help you today?"
        )

    if any(w in query_lower for w in ["medication", "medicine", "drug", "pill"]):
        if medications:
            meds_str = "\n".join([f"- **{m}**" for m in medications[:5]])
            return f"**Your current medications:**\n{meds_str}\n\n⚠️ Never stop medications without consulting your doctor."
        return "No medications recorded in your profile."

    if any(w in query_lower for w in ["condition", "disease", "diagnosis"]):
        if conditions:
            conds_str = "\n".join([f"- **{c}**" for c in conditions])
            return f"**Your conditions:**\n{conds_str}\n\nRegular monitoring and medication adherence are key."
        return "No chronic conditions recorded in your profile."

    if any(w in query_lower for w in ["allerg"]):
        if allergies:
            return f"**Known allergies:** {', '.join(allergies)}\n\n⚠️ Always inform healthcare providers of these allergies."
        return "No allergies recorded in your profile."

    return (
        "I'm here to help with your health questions! I can assist with:\n"
        "- 💊 Medication information\n"
        "- 🏥 Your health conditions\n"
        "- 📊 Lab result interpretation\n"
        "- ⚠️ Drug interaction checks\n\n"
        "Could you be more specific about what you'd like to know?"
    )


# ─── Standalone Test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 XAI RAG Engine — Standalone Test")
    print("=" * 70)

    # 1. Test retrieval
    print("\n📡 Test 1: ChromaDB Retrieval")
    rules = retrieve_relevant_context("Aspirin Warfarin bleeding interaction", n_results=3)
    print(f"   Retrieved {len(rules)} rules")
    for r in rules:
        print(f"   → {r.get('interaction')} | Risk: {r.get('risk_level')}")

    # 2. Test XAI explanation
    print("\n🧠 Test 2: XAI Drug Interaction Explanation (Doctor Mode)")
    sample_interaction = {
        "status": "Risky",
        "risk_level": "Critical",
        "mechanism": "Synergistic inhibition of platelet aggregation",
        "recommendation": "Avoid combination if possible",
        "doctor_explanation": "Concurrent use significantly increases bleeding risk",
        "patient_explanation": "This combination increases your bleeding risk"
    }
    sample_context = {
        "age": 65,
        "gender": "Male",
        "conditions": ["Hypertension", "Atrial Fibrillation"],
        "allergies": [],
        "medications": ["Warfarin"]
    }

    xai = explain_drug_interaction(
        medication_history=["Warfarin"],
        new_drug="Aspirin",
        interaction_data=sample_interaction,
        patient_context=sample_context,
        view_mode="doctor"
    )
    print(f"   LLM Used: {xai['llm_used']} ({xai['model']})")
    print(f"   Sources: {xai['sources']}")
    print(f"   RAG Rules Retrieved: {len(xai['rag_retrieved_rules'])}")
    print(f"\n   Explanation Preview:")
    print(f"   {xai['generated_explanation'][:300]}...")

    # 3. Test RAG chat
    print("\n💬 Test 3: RAG Chat Response")
    chat_resp = generate_rag_chat_response(
        user_query="What drug interactions should I watch out for?",
        patient_context=sample_context,
        history=[]
    )
    print(f"   Response ({len(chat_resp)} chars):")
    print(f"   {chat_resp[:250]}...")

    print("\n" + "=" * 70)
    print("✅ XAI RAG Engine Test Complete")
    print("=" * 70)
