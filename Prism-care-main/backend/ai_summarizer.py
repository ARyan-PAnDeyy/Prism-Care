"""
AI-Powered Medical Summarization Engine
Uses OpenRouter (100+ models) for intelligent medical history analysis and summarization
"""

from openai import OpenAI
import os
from typing import Dict, List, Any
from datetime import datetime
import json

# Configure OpenRouter API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

if OPENROUTER_API_KEY and USE_LLM:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    model = LLM_MODEL
else:
    openrouter_client = None
    model = None
    print("WARNING: OpenRouter AI not configured. Using fallback summarization.")


class MedicalSummarizer:
    """AI-powered medical history summarization"""
    
    def __init__(self):
        self.client = openrouter_client
        self.model = model
    
    def summarize_medical_history(self, patient_data: Dict, target_audience: str = "doctor") -> Dict:
        """
        Generate comprehensive medical summary using OpenRouter AI
        
        Args:
            patient_data: Complete patient medical records
            target_audience: 'doctor' or 'patient'
            
        Returns:
            Structured summary with key insights
        """
        if not self.client:
            print("WARNING: OpenRouter client not initialized - using fallback")
            return self._fallback_summary(patient_data)
        
        try:
            # Prepare prompt for OpenRouter
            prompt = self._build_summary_prompt(patient_data, target_audience)
            
            print(f"[AI Summary] Calling OpenRouter API with model: {self.model}")
            print(f"[AI Summary] Prompt length: {len(prompt)} characters")
            
            # Generate summary using OpenRouter
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert medical AI assistant specialized in creating comprehensive, detailed medical summaries. Always provide thorough, in-depth analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Higher for more detailed, varied responses
                max_tokens=3000,  # Increased for comprehensive summaries
            )
            summary_text = response.choices[0].message.content
            
            print(f"[AI Summary] SUCCESS! Generated {len(summary_text)} characters")
            print(f"[AI Summary] First 100 chars: {summary_text[:100]}...")
            
            # Parse and structure the response
            summary = {
                "patient_id": patient_data.get("id"),
                "patient_name": patient_data.get("name"),
                "generated_at": datetime.now().isoformat(),
                "summary_text": summary_text,
                "key_conditions": self._extract_key_conditions(patient_data),
                "active_medications": self._extract_active_medications(patient_data),
                "recent_trends": self._analyze_trends(patient_data),
                "risk_factors": self._identify_risk_factors(patient_data),
                "recommendations": self._generate_recommendations(patient_data),
                "ai_generated": True  # Flag to indicate AI was used
            }
            
            return summary
            
        except Exception as e:
            print(f"ERROR: OpenRouter AI error: {str(e)}")
            print(f"ERROR: Full exception: {repr(e)}")
            import traceback
            traceback.print_exc()
            return self._fallback_summary(patient_data)
    
    def _build_summary_prompt(self, patient_data: Dict, target_audience: str = "doctor") -> str:
        """Build detailed prompt for comprehensive medical summaries"""
        
        # Extract key information
        demographics = f"{patient_data.get('name')}, {patient_data.get('age')}Y, {patient_data.get('gender')}"
        
        diagnoses = patient_data.get("diagnoses", [])
        diagnoses_text = "\n".join([
            f"- {d['condition']} (diagnosed {d['diagnosed_date']}, {d['status']}, {d['severity']})"
            for d in diagnoses
        ])
        
        medications = patient_data.get("medications", [])
        meds_text = "\n".join([
            f"- {m['medicine']} {m['dosage']} {m['frequency']} (for {m.get('purpose', 'N/A')})"
            for m in medications if m.get('status') == 'active'
        ])
        
        recent_labs = patient_data.get("lab_reports", [])[:3]  # Last 3 reports
        labs_text = "\n".join([
            f"- {lab['test_name']} ({lab['date']}): {lab.get('result', 'N/A')}"
            for lab in recent_labs
        ])
        
        if target_audience == "patient":
            prompt = f"""You are an expert medical AI assistant. Create a DETAILED, COMPREHENSIVE health summary for the patient.

**Patient:** {demographics}

**Health Records:**
- **Conditions:** {diagnoses_text if diagnoses_text else "None"}
- **Medications:** {meds_text if meds_text else "None"}
- **Recent Labs:** {labs_text if labs_text else "None"}

**IMPORTANT:** Provide a DETAILED, COMPREHENSIVE summary with AT LEAST 300 words. Include:

1. **Health Overview** (3-4 paragraphs):
   - Explain each condition in simple terms
   - How conditions relate to each other
   - Current health status and prognosis

2. **Your Medications** (Detailed):
   - What each medication does
   - Why it's important
   - How it helps your condition
   - Common side effects to watch for

3. **Recent Test Results** (Comprehensive):
   - What each test measures
   - What your results mean
   - Are they improving or concerning?
   - Comparison with normal ranges

4. **Warning Signs to Watch For**:
   - Specific symptoms that need immediate attention
   - When to call your doctor
   - Emergency situations

5. **Lifestyle Recommendations**:
   - Specific diet suggestions
   - Exercise guidelines
   - Sleep and stress management
   - Daily habits to improve health

6. **Next Steps**:
   - Upcoming tests or appointments
   - Goals for improvement
   - Timeline for reassessment

**Tone:** Empathetic, encouraging, but THOROUGH. Use simple language but don't skip important details. Aim for 400-500 words minimum."""
        else:
            prompt = f"""You are an expert medical AI assistant. Provide a COMPREHENSIVE, DETAILED clinical summary for healthcare providers.

**Patient:** {demographics}

**Active Diagnoses:**
{diagnoses_text if diagnoses_text else "None documented"}

**Current Medications:**
{meds_text if meds_text else "None"}

**Recent Lab Tests:**
{labs_text if labs_text else "None"}

**CRITICAL:** Generate a DETAILED clinical summary with AT LEAST 400 words. Include:

1. **Executive Summary** (2-3 paragraphs):
   - Overall health status and complexity
   - Primary vs secondary conditions
   - Current stability and trajectory

2. **Detailed Condition Analysis**:
   - Each diagnosis with severity assessment
   - Pathophysiology and progression
   - Comorbidity interactions
   - Evidence-based management status

3. **Medication Review** (Comprehensive):
   - Therapeutic appropriateness
   - Drug-drug interactions
   - Drug-disease interactions
   - Adherence considerations
   - Potential optimization opportunities

4. **Laboratory Trend Analysis**:
   - Key biomarker trends over time
   - Abnormal values and clinical significance
   - Response to therapy
   - Recommended monitoring frequency

5. **Risk Stratification**:
   - Cardiovascular risk
   - Metabolic risk
   - Complication risk
   - Hospitalization risk factors

6. **Clinical Recommendations** (Specific):
   - Diagnostic workup needed
   - Treatment modifications
   - Specialist referrals
   - Preventive measures
   - Follow-up timeline

7. **Quality Metrics**:
   - Guideline adherence
   - Care gaps
   - Preventive health status

**Tone:** Professional, evidence-based, actionable. Minimum 500 words. Be thorough and specific."""
        
        return prompt
    
    def _extract_key_conditions(self, patient_data: Dict) -> List[str]:
        """Extract active key conditions"""
        diagnoses = patient_data.get("diagnoses", [])
        return [
            d["condition"] 
            for d in diagnoses 
            if d.get("status") == "active"
        ]
    
    def _extract_active_medications(self, patient_data: Dict) -> List[Dict]:
        """Extract currently active medications"""
        medications = patient_data.get("medications", [])
        return [
            {
                "name": m["medicine"],
                "dosage": m["dosage"],
                "purpose": m.get("purpose", "")
            }
            for m in medications 
            if m.get("status") == "active"
        ]
    
    def _analyze_trends(self, patient_data: Dict) -> List[str]:
        """Analyze lab trends over time"""
        trends = []
        lab_reports = patient_data.get("lab_reports", [])
        
        # Group labs by test name
        labs_by_test = {}
        for lab in lab_reports:
            test_name = lab.get("test_name", "")
            if test_name not in labs_by_test:
                labs_by_test[test_name] = []
            labs_by_test[test_name].append(lab)
        
        # Analyze HbA1c trend if available
        if "HbA1c (Glycated Hemoglobin)" in labs_by_test or "HbA1c" in labs_by_test:
            hba1c_labs = labs_by_test.get("HbA1c (Glycated Hemoglobin)", labs_by_test.get("HbA1c", []))
            if len(hba1c_labs) >= 2:
                # Sort by date
                sorted_labs = sorted(hba1c_labs, key=lambda x: x.get("date", ""))
                latest = sorted_labs[-1].get("results", {}).get("hba1c", {}).get("value", 0)
                previous = sorted_labs[-2].get("results", {}).get("hba1c", {}).get("value", 0)
                
                if latest > previous:
                    trends.append(f"HbA1c trending upward ({previous}% → {latest}%)")
                elif latest < previous:
                    trends.append(f"HbA1c improving ({previous}% → {latest}%)")
                else:
                    trends.append(f"HbA1c stable at {latest}%")
        
        # Analyze cholesterol trends
        if "Lipid Profile" in labs_by_test:
            lipid_labs = labs_by_test["Lipid Profile"]
            if len(lipid_labs) >= 1:
                latest_lipid = lipid_labs[-1].get("results", {})
                ldl = latest_lipid.get("ldl", {})
                if ldl.get("status") == "high":
                    trends.append(f"LDL cholesterol elevated at {ldl.get('value')} mg/dL")
        
        return trends if trends else ["No significant trends identified"]
    
    def _identify_risk_factors(self, patient_data: Dict) -> List[str]:
        """Identify health risk factors"""
        risks = []
        
        # Check age-related risks
        age = patient_data.get("age", 0)
        if age > 60:
            risks.append("Advanced age - increased cardiovascular risk")
        
        # Check for diabetes
        diagnoses = patient_data.get("diagnoses", [])
        has_diabetes = any("diabetes" in d["condition"].lower() for d in diagnoses)
        if has_diabetes:
            risks.append("Diabetes - monitor for complications (retinopathy, nephropathy, neuropathy)")
        
        # Check for hypertension
        has_hypertension = any("hypertension" in d["condition"].lower() for d in diagnoses)
        if has_hypertension:
            risks.append("Hypertension - cardiovascular disease risk")
        
        # Check for anticoagulation
        medications = patient_data.get("medications", [])
        on_warfarin = any("warfarin" in m["medicine"].lower() for m in medications if m.get("status") == "active")
        if on_warfarin:
            risks.append("On anticoagulation - bleeding risk, requires INR monitoring")
        
        # Check lab abnormalities
        lab_reports = patient_data.get("lab_reports", [])
        for lab in lab_reports:
            results = lab.get("results", {})
            for test, values in results.items():
                if isinstance(values, dict) and values.get("status") in ["high", "elevated", "low"]:
                    risks.append(f"Abnormal {test}: {values.get('value')} {values.get('unit')}")
        
        return risks if risks else ["No major risk factors identified"]
    
    def _generate_recommendations(self, patient_data: Dict) -> List[str]:
        """Generate clinical recommendations"""
        recommendations = []
        
        # Check for missing recent tests
        lab_reports = patient_data.get("lab_reports", [])
        test_names = [lab.get("test_name", "") for lab in lab_reports]
        
        diagnoses = patient_data.get("diagnoses", [])
        has_diabetes = any("diabetes" in d["condition"].lower() for d in diagnoses)
        
        if has_diabetes:
            if "HbA1c" not in " ".join(test_names):
                recommendations.append("Recommend HbA1c test for diabetes monitoring")
            if "Kidney Function Test" not in " ".join(test_names):
                recommendations.append("Recommend kidney function test (diabetes complication screening)")
        
        # Check medication adherence
        medications = patient_data.get("medications", [])
        if len(medications) > 3:
            recommendations.append("Multiple medications - review for potential interactions and adherence")
        
        # Lifestyle recommendations
        if has_diabetes or any("hypertension" in d["condition"].lower() for d in diagnoses):
            recommendations.append("Lifestyle modifications: low-salt diet, regular exercise, weight management")
        
        return recommendations if recommendations else ["Continue current management plan"]
    
    def _fallback_summary(self, patient_data: Dict) -> Dict:
        """Fallback summary when Gemini is not available"""
        return {
            "patient_id": patient_data.get("id"),
            "patient_name": patient_data.get("name"),
            "generated_at": datetime.now().isoformat(),
            "summary_text": f"Patient {patient_data.get('name')}, {patient_data.get('age')}Y {patient_data.get('gender')}, with {len(patient_data.get('diagnoses', []))} active conditions on {len([m for m in patient_data.get('medications', []) if m.get('status') == 'active'])} medications.",
            "key_conditions": self._extract_key_conditions(patient_data),
            "active_medications": self._extract_active_medications(patient_data),
            "recent_trends": self._analyze_trends(patient_data),
            "risk_factors": self._identify_risk_factors(patient_data),
            "recommendations": self._generate_recommendations(patient_data),
            "note": "Generated using fallback logic (Gemini AI not configured)"
        }


# Utility function
def generate_medical_summary(patient_data: Dict, target_audience: str = "doctor") -> Dict:
    """
    Convenience function to generate medical summary
    
    Args:
        patient_data: Complete patient medical records
        target_audience: 'doctor' or 'patient'
        
    Returns:
        Comprehensive medical summary
    """
    summarizer = MedicalSummarizer()
    return summarizer.summarize_medical_history(patient_data, target_audience)


if __name__ == "__main__":
    # Test the summarizer
    print("=" * 60)
    print("🧠 AI Medical Summarizer Test")
    print("=" * 60)
    
    test_patient = {
        "id": "TEST001",
        "name": "Test Patient",
        "age": 58,
        "gender": "Male",
        "diagnoses": [
            {
                "condition": "Type 2 Diabetes Mellitus",
                "diagnosed_date": "2020-06-15",
                "status": "active",
                "severity": "moderate"
            }
        ],
        "medications": [
            {
                "medicine": "Metformin",
                "dosage": "500mg",
                "frequency": "Twice daily",
                "status": "active",
                "purpose": "Blood sugar control"
            }
        ],
        "lab_reports": [
            {
                "test_name": "HbA1c",
                "date": "2024-01-28",
                "results": {
                    "hba1c": {"value": 6.8, "unit": "%", "status": "elevated"}
                }
            }
        ]
    }
    
    summary = generate_medical_summary(test_patient)
    
    print(f"\n📋 Summary for: {summary['patient_name']}")
    print(f"\n📝 Summary Text:\n{summary['summary_text']}")
    print(f"\n🏥 Key Conditions: {', '.join(summary['key_conditions'])}")
    print(f"\n💊 Active Medications: {len(summary['active_medications'])}")
    print(f"\n📈 Trends:")
    for trend in summary['recent_trends']:
        print(f"   - {trend}")
    print(f"\n⚠️  Risk Factors:")
    for risk in summary['risk_factors']:
        print(f"   - {risk}")
    print(f"\n💡 Recommendations:")
    for rec in summary['recommendations']:
        print(f"   - {rec}")
    
    print("\n" + "=" * 60)
