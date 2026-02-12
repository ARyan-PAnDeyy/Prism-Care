"""
AI-Powered Medical Summarization Engine
Uses Google Gemini AI for intelligent medical history analysis and summarization
"""

import google.generativeai as genai
import os
from typing import Dict, List, Any
from datetime import datetime
import json

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")

if GEMINI_API_KEY and USE_LLM:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(LLM_MODEL)
else:
    model = None
    print("⚠️  Gemini AI not configured. Using fallback summarization.")


class MedicalSummarizer:
    """AI-powered medical history summarization"""
    
    def __init__(self):
        self.model = model
    
    def summarize_medical_history(self, patient_data: Dict, target_audience: str = "doctor") -> Dict:
        """
        Generate comprehensive medical summary using Gemini AI
        
        Args:
            patient_data: Complete patient medical records
            target_audience: 'doctor' or 'patient'
            
        Returns:
            Structured summary with key insights
        """
        if not self.model:
            return self._fallback_summary(patient_data)
        
        try:
            # Prepare prompt for Gemini
            prompt = self._build_summary_prompt(patient_data, target_audience)
            
            # Generate summary
            response = self.model.generate_content(prompt)
            summary_text = response.text
            
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
                "recommendations": self._generate_recommendations(patient_data)
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Gemini AI error: {str(e)}")
            return self._fallback_summary(patient_data)
    
    def _build_summary_prompt(self, patient_data: Dict, target_audience: str = "doctor") -> str:
        """Build detailed prompt for Gemini"""
        
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
            f"- {lab['test_name']} ({lab['date']})"
            for lab in recent_labs
        ])
        
        if target_audience == "patient":
            prompt = f"""You are a helpful and empathetic medical AI assistant for a patient. Provide a simple, easy-to-understand health summary.
            
**Patient:** {demographics}

**Health Records:**
- **Conditions:** {diagnoses_text if diagnoses_text else "None"}
- **Medications:** {meds_text if meds_text else "None"}
- **Recent Labs:** {labs_text if labs_text else "None"}

**Please provide a Patient-Friendly Summary:**
1. **Health Overview** (Simple language): "You have [Condition] which means..."
2. **Your Medications**: Explain simply what they are for.
3. **Recent Results**: "Your recent tests show..." (Good/Bad).
4. **What to Watch For**: Simple warning signs.
5. **Lifestyle Tips**: Diet/Exercise advice.

**Tone:** Empathetic, simple (5th-grade reading level), encouraging. No complex jargon without explanation."""
        else:
            prompt = f"""You are a medical AI assistant. Provide a comprehensive yet concise medical summary for this patient.

**Patient:** {demographics}

**Active Diagnoses:**
{diagnoses_text if diagnoses_text else "None documented"}

**Current Medications:**
{meds_text if meds_text else "None"}

**Recent Lab Tests:**
{labs_text if labs_text else "None"}

**Please provide:**
1. **Medical Summary** (2-3 sentences): Overall health status
2. **Key Health Concerns**: Most important conditions to monitor
3. **Medication Review**: Any potential issues or interactions
4. **Trend Analysis**: Are conditions improving, stable, or worsening?
5. **Risk Factors**: What should be monitored closely?
6. **Recommendations**: Suggested tests, lifestyle changes, or follow-ups

**Tone:** Professional, clear, and actionable for healthcare providers."""
        
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
                latest = sorted_labs[-1]["results"].get("hba1c", {}).get("value", 0)
                previous = sorted_labs[-2]["results"].get("hba1c", {}).get("value", 0)
                
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
                latest_lipid = lipid_labs[-1]["results"]
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
