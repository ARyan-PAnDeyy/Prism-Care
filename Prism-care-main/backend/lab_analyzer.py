"""
Lab Report Analysis Module
Analyzes uploaded lab reports using Gemini AI
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
USE_LLM = os.getenv('USE_LLM', 'false').lower() == 'true'
LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.0-flash-exp')

if USE_LLM and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(LLM_MODEL)
else:
    model = None


def analyze_lab_report(lab_data: Dict) -> Dict:
    """
    Analyze lab report and provide insights
    
    Args:
        lab_data: Dictionary containing lab test results
        
    Returns:
        Analysis with interpretations, trends, and recommendations
    """
    
    
    
    if not model:
        return _fallback_analysis(lab_data)
    
    try:
        # Check if we have a file path or just text data
        file_path = lab_data.get('file_path')
        
        if file_path and os.path.exists(file_path):
            # Analyze file using Gemini Vision/PDF
            return _analyze_file_with_gemini(file_path, lab_data)
        else:
            # Build analysis prompt for structured data
            prompt = _build_analysis_prompt(lab_data)
            
            # Get AI analysis
            response = model.generate_content(prompt)
            analysis_text = response.text
            
            return _parse_ai_response(analysis_text, lab_data)
        
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        return _fallback_analysis(lab_data)



# Import pypdf for fallback text extraction
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

def _analyze_file_with_gemini(file_path: str, lab_data: Dict) -> Dict:
    """Analyze lab report file (Image/PDF) using Gemini with pypdf fallback"""
    
    # 1. Try Gemini Vision/PDF first (Multimodal)
    gemini_success = False
    analysis = None
    
    try:
        # Upload file to Gemini
        sample_file = genai.upload_file(path=file_path, display_name="Lab Report")
        
        # Build prompt
        patient_info = f"Patient Age: {lab_data.get('patient_age', 'Unknown')}, Gender: {lab_data.get('patient_gender', 'Unknown')}"
        prompt = f"""Analyze this lab report. {patient_info}
        
        Please provide a detailed but easy-to-understand analysis in the following JSON format.
        
        **IMPORTANT INSTRUCTIONS:**
        1. **Simple Language**: Explain everything in plain English that a non-medical person can understand. Avoid jargon.
        2. **Detailed Analysis**: Don't just say "Normal". Explain WHAT is normal and why it's good.
        3. **Context**: If a value is high/low, explain what that effectively means for the patient's daily life.
        
        JSON Structure:
        {{
            "test_name": "Name of the test",
            "overall_assessment": "Comprehensive summary of health status in simple terms",
            "abnormal_findings": [
                {{"parameter": "Parameter Name", "value": "Value", "status": "High/Low", "reference_range": "Range"}}
            ],
            "interpretations": "Detailed interpretation of results. Break it down simply.",
            "health_risks": ["Risk 1 (explained simply)", "Risk 2"],
            "recommendations": ["Rec 1 (actionable advice)", "Rec 2"],
            "follow_up_tests": ["Test 1"],
            "lifestyle_advice": ["Advice 1"]
        }}
        """
        
        # Generate content
        response = model.generate_content([sample_file, prompt])
        
        # Clean up response to ensure valid JSON
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3]
        elif text.startswith('```'):
            text = text[3:-3]
            
        try:
            analysis = json.loads(text)
            analysis['timestamp'] = datetime.now().isoformat()
            analysis['ai_generated'] = True
            gemini_success = True
            return analysis
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails, use text parsing
            pass # Continue to fallback logic below if needed, or return parsed text
            
    except Exception as e:
        print(f"Error analyzing file with Gemini: {e}")
        # Proceed to fallback

    # 2. Fallback: Extract text using pypdf (if PDF) and analyze as text
    if not gemini_success and file_path.lower().endswith('.pdf'):
        print("Falling back to pypdf extraction...")
        try:
            if PdfReader:
                reader = PdfReader(file_path)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
                
                # Now analyze this text as structured data
                # We reuse the logic from _build_analysis_prompt but pass the raw text instead of structured data
                # We need to adapt the prompt to take raw text
                
                prompt = f"""Analyze this lab report text.
                
                Report Text:
                {text_content[:5000]} 
                
                Patient Info: Age {lab_data.get('patient_age')}, Gender {lab_data.get('patient_gender')}
                
                **IMPORTANT INSTRUCTIONS:**
                1. **Simple Language**: Explain everything in plain English that a non-medical person can understand. Avoid jargon.
                2. **Detailed Analysis**: Don't just say "Normal". Explain WHAT is normal and why it's good.
                3. **Context**: If a value is high/low, explain what that effectively means for the patient's daily life.
                
                Extract values and provide analysis in the same JSON format as requested before.
                """
                
                response = model.generate_content(prompt)
                
                # Parse JSON again
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:-3]
                elif text.startswith('```'):
                    text = text[3:-3]
                
                analysis = json.loads(text)
                analysis['timestamp'] = datetime.now().isoformat()
                analysis['ai_generated'] = True
                analysis['method'] = "fallback_text_extraction"
                return analysis

        except Exception as e:
            print(f"Fallback extraction failed: {e}")

    return _fallback_analysis(lab_data)


def _parse_ai_response(analysis_text: str, lab_data: Dict) -> Dict:
    """Parse text response from AI"""
    return {
        "overall_assessment": _extract_section(analysis_text, "Overall Assessment"),
        "abnormal_findings": _extract_abnormal_findings(lab_data), # Fallback for text mode
        "interpretations": _extract_section(analysis_text, "Interpretations"),
        "health_risks": _extract_list_section(analysis_text, "Health Risks"),
        "recommendations": _extract_list_section(analysis_text, "Recommendations"),
        "follow_up_tests": _extract_list_section(analysis_text, "Follow-up Tests"),
        "lifestyle_advice": _extract_list_section(analysis_text, "Lifestyle Advice"),
        "timestamp": datetime.now().isoformat(),
        "ai_generated": True
    }


def _build_analysis_prompt(lab_data: Dict) -> str:
    """Build comprehensive analysis prompt"""
    
    test_name = lab_data.get('test_name', 'Lab Test')
    results = lab_data.get('results', {})
    patient_age = lab_data.get('patient_age', 'Unknown')
    patient_gender = lab_data.get('patient_gender', 'Unknown')
    
    # Format results
    results_text = "\n".join([
        f"- {key.replace('_', ' ').title()}: {value.get('value', 'N/A')} {value.get('unit', '')} "
        f"(Reference: {value.get('reference_range', 'N/A')}, Status: {value.get('status', 'N/A')})"
        for key, value in results.items()
        if isinstance(value, dict)
    ])
    
    prompt = f"""You are a medical AI assistant analyzing lab reports. Provide a comprehensive analysis.

**Patient Information:**
- Age: {patient_age}
- Gender: {patient_gender}

**Test Name:** {test_name}

**Results:**
{results_text}

Please provide a detailed analysis in the following format:

**Overall Assessment:**
(2-3 sentences summarizing the overall health status based on these results)

**Interpretations:**
(Explain what each abnormal value means in simple, patient-friendly language)

**Health Risks:**
(List potential health risks if any values are concerning)
- Risk 1
- Risk 2

**Recommendations:**
(Actionable recommendations for the patient)
- Recommendation 1
- Recommendation 2

**Follow-up Tests:**
(Suggest any additional tests that might be needed)
- Test 1
- Test 2

**Lifestyle Advice:**
(Practical lifestyle changes based on results)
- Advice 1
- Advice 2

Keep explanations clear, empathetic, and actionable. Avoid medical jargon where possible.
"""
    
    return prompt


def _extract_section(text: str, section_name: str) -> str:
    """Extract a specific section from AI response"""
    try:
        start_marker = f"**{section_name}:**"
        if start_marker not in text:
            return ""
        
        start_idx = text.index(start_marker) + len(start_marker)
        
        # Find next section or end
        next_section_idx = text.find("**", start_idx)
        if next_section_idx == -1:
            section_text = text[start_idx:].strip()
        else:
            section_text = text[start_idx:next_section_idx].strip()
        
        return section_text
    except:
        return ""


def _extract_list_section(text: str, section_name: str) -> List[str]:
    """Extract a list section from AI response"""
    section_text = _extract_section(text, section_name)
    if not section_text:
        return []
    
    # Extract bullet points
    lines = section_text.split('\n')
    items = []
    for line in lines:
        line = line.strip()
        if line.startswith('-') or line.startswith('•'):
            items.append(line[1:].strip())
    
    return items


def _extract_abnormal_findings(lab_data: Dict) -> List[Dict]:
    """Extract abnormal findings from lab data"""
    abnormal = []
    results = lab_data.get('results', {})
    
    for key, value in results.items():
        if isinstance(value, dict):
            status = value.get('status', '').lower()
            if status in ['high', 'low', 'elevated', 'critical', 'abnormal']:
                abnormal.append({
                    "parameter": key.replace('_', ' ').title(),
                    "value": f"{value.get('value', 'N/A')} {value.get('unit', '')}",
                    "status": status,
                    "reference_range": value.get('reference_range', 'N/A')
                })
    
    return abnormal


def _fallback_analysis(lab_data: Dict) -> Dict:
    """Fallback analysis when AI is not available"""
    
    abnormal_findings = _extract_abnormal_findings(lab_data)
    
    # Generate basic recommendations based on abnormal findings
    recommendations = []
    health_risks = []
    
    for finding in abnormal_findings:
        param = finding['parameter'].lower()
        status = finding['status']
        
        if 'glucose' in param and status == 'high':
            recommendations.append("Monitor blood sugar levels regularly")
            recommendations.append("Consult with a doctor about diabetes management")
            health_risks.append("Risk of diabetes or prediabetes")
        
        elif 'cholesterol' in param and status == 'high':
            recommendations.append("Follow a heart-healthy diet low in saturated fats")
            recommendations.append("Increase physical activity")
            health_risks.append("Increased cardiovascular risk")
        
        elif 'hemoglobin' in param and status == 'low':
            recommendations.append("Include iron-rich foods in diet")
            recommendations.append("Consider iron supplementation after consulting doctor")
            health_risks.append("Risk of anemia")
    
    if not recommendations:
        recommendations.append("Continue maintaining healthy lifestyle")
        recommendations.append("Regular health checkups recommended")
    
    overall = "Normal results" if not abnormal_findings else f"Found {len(abnormal_findings)} abnormal value(s) requiring attention"
    
    return {
        "overall_assessment": overall,
        "abnormal_findings": abnormal_findings,
        "interpretations": "Basic analysis - AI analysis unavailable. Please consult your healthcare provider for detailed interpretation.",
        "health_risks": health_risks if health_risks else ["No immediate risks identified"],
        "recommendations": recommendations,
        "follow_up_tests": ["Consult your doctor for personalized recommendations"],
        "lifestyle_advice": [
            "Maintain a balanced diet",
            "Exercise regularly (30 minutes daily)",
            "Stay hydrated",
            "Get adequate sleep (7-8 hours)"
        ],
        "timestamp": datetime.now().isoformat(),
        "ai_generated": False
    }


def parse_lab_report_text(report_text: str) -> Dict:
    """
    Parse lab report text and extract values
    This is a simple parser - in production, use OCR or structured data
    """
    
    # Example parser for common formats
    results = {}
    
    # Common lab parameters with reference ranges
    parameters = {
        'hemoglobin': {'unit': 'g/dL', 'ref_male': '13.5-17.5', 'ref_female': '12.0-15.5'},
        'wbc': {'unit': '10^3/μL', 'ref': '4.5-11.0'},
        'platelets': {'unit': '10^3/μL', 'ref': '150-400'},
        'glucose': {'unit': 'mg/dL', 'ref': '70-100'},
        'hba1c': {'unit': '%', 'ref': '<5.7'},
        'cholesterol': {'unit': 'mg/dL', 'ref': '<200'},
        'ldl': {'unit': 'mg/dL', 'ref': '<100'},
        'hdl': {'unit': 'mg/dL', 'ref': '>40'},
        'triglycerides': {'unit': 'mg/dL', 'ref': '<150'},
        'creatinine': {'unit': 'mg/dL', 'ref': '0.7-1.3'},
    }
    
    # Simple extraction (in production, use better parsing)
    lines = report_text.lower().split('\n')
    for line in lines:
        for param, info in parameters.items():
            if param in line:
                # Try to extract number
                import re
                numbers = re.findall(r'\d+\.?\d*', line)
                if numbers:
                    value = float(numbers[0])
                    ref_range = info.get('ref', info.get('ref_male', ''))
                    
                    # Determine status
                    status = 'normal'
                    if '-' in ref_range:
                        low, high = map(float, ref_range.replace('<', '').replace('>', '').split('-'))
                        if value < low:
                            status = 'low'
                        elif value > high:
                            status = 'high'
                    elif '<' in ref_range:
                        threshold = float(ref_range.replace('<', ''))
                        status = 'high' if value >= threshold else 'normal'
                    elif '>' in ref_range:
                        threshold = float(ref_range.replace('>', ''))
                        status = 'low' if value <= threshold else 'normal'
                    
                    results[param] = {
                        'value': value,
                        'unit': info['unit'],
                        'reference_range': ref_range,
                        'status': status
                    }
    
    return results


# Test the module
if __name__ == "__main__":
    # Test with sample lab data
    sample_lab = {
        "test_name": "Complete Blood Count (CBC)",
        "patient_age": 58,
        "patient_gender": "Male",
        "results": {
            "hemoglobin": {"value": 11.2, "unit": "g/dL", "reference_range": "13.5-17.5", "status": "low"},
            "wbc": {"value": 7.5, "unit": "10^3/μL", "reference_range": "4.5-11.0", "status": "normal"},
            "platelets": {"value": 220, "unit": "10^3/μL", "reference_range": "150-400", "status": "normal"},
            "glucose": {"value": 145, "unit": "mg/dL", "reference_range": "70-100", "status": "high"}
        }
    }
    
    print("Testing Lab Report Analysis...")
    analysis = analyze_lab_report(sample_lab)
    print(json.dumps(analysis, indent=2))
