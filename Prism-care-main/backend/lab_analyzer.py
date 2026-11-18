"""
Lab Report Analysis Module
Analyzes uploaded lab reports using Gemini AI (Google's official API)
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
USE_LLM = os.getenv('USE_LLM', 'false').lower() == 'true'

if USE_LLM and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
    print("[LAB ANALYZER] Gemini API configured successfully")
else:
    gemini_model = None
    print("[LAB ANALYZER] Using local fallback analysis")


def analyze_lab_report(lab_data: Dict) -> Dict:
    """
    Analyze lab report and provide comprehensive insights using Gemini AI
    Supports both structured data and PDF file uploads
    
    Args:
        lab_data: Dictionary containing lab test results OR file_path to PDF
        
    Returns:
        Detailed analysis with interpretations, trends, and recommendations
    """
    
    if not gemini_model:
        print("[LAB ANALYZER] Gemini not available, using local analysis")
        return _fallback_analysis(lab_data)
    
    try:
        # Check if this is a PDF file upload
        if 'file_path' in lab_data:
            print(f"[LAB ANALYZER] PDF file detected: {lab_data['file_path']}")
            return _analyze_pdf_with_gemini(lab_data)
        
        # Otherwise, structured data analysis
        print("[LAB ANALYZER] Calling Gemini API for structured data analysis...")
        
        # Build comprehensive analysis prompt
        prompt = _build_gemini_analysis_prompt(lab_data)
        
        # Get AI analysis using Gemini
        response = gemini_model.generate_content(prompt)
        analysis_text = response.text
        
        print(f"[LAB ANALYZER] ✅ Gemini analysis complete ({len(analysis_text)} chars)")
        
        return _parse_gemini_response(analysis_text, lab_data)
        
    except Exception as e:
        print(f"[LAB ANALYZER] ❌ Gemini error: {e}")
        import traceback
        traceback.print_exc()
        print("[LAB ANALYZER] Falling back to local analysis")
        return _fallback_analysis(lab_data)


def _analyze_pdf_with_gemini(lab_data: Dict) -> Dict:
    """
    Analyze PDF lab report using Gemini Vision API
    """
    file_path = lab_data.get('file_path')
    test_name = lab_data.get('test_name', 'Lab Report')
    patient_age = lab_data.get('patient_age', 'Unknown')
    patient_gender = lab_data.get('patient_gender', 'Unknown')
    
    print(f"[LAB ANALYZER] Uploading PDF to Gemini: {file_path}")
    
    try:
        # Upload file to Gemini
        uploaded_file = genai.upload_file(path=file_path, display_name="Lab Report")
        print(f"[LAB ANALYZER] File uploaded successfully: {uploaded_file.name}")
        
        # Build comprehensive prompt for PDF analysis
        prompt = f"""You are an expert medical AI assistant analyzing a lab report PDF. Provide a COMPREHENSIVE, DETAILED analysis.

**Patient Information:**
- Age: {patient_age}
- Gender: {patient_gender}

**CRITICAL INSTRUCTIONS:**
Analyze this medical report/lab report PDF and provide an EXTREMELY DETAILED analysis (minimum 500 words). Be thorough and comprehensive!

**Format your response as follows:**

## Overall Assessment
(3-4 paragraphs summarizing overall health status, significance of findings, and urgency level. Mention what type of report this is.)

## Detailed Interpretations
(For EACH parameter/finding in the report - normal or abnormal - explain in detail):
- **Parameter/Finding Name**: What this measures, what the value means, why it matters
- If abnormal: Explain the medical significance, potential causes, and health implications
- Include ALL diagnoses, conditions, medications, and findings mentioned in the report

## Health Risks
(List all potential health risks based on these results):
- **Risk Category**: Detailed explanation of the risk, why it's concerning, long-term implications

## Immediate Recommendations
(Specific, actionable steps the patient should take):
- **Action Item**: Detailed explanation of what to do, when, and why it's important

## Lifestyle Modifications
(Comprehensive lifestyle changes):
- **Diet**: Specific foods to eat/avoid with explanations
- **Exercise**: Exact exercise recommendations with frequency and duration  
- **Habits**: Sleep, stress management, hydration, medications compliance, etc.

## Follow-up Tests
(Recommended additional tests):
- **Test Name**: Why this test is needed, what it will reveal

## When to Seek Medical Care
(Clear guidelines on urgency):
- Immediate (ER/911)
- Urgent (within 24-48 hours)
- Routine (schedule appointment)

**Tone:** Professional yet compassionate. Use simple language but don't oversimplify. Provide medical details but explain them clearly.

**IMPORTANT:** Extract ALL information from the PDF - diagnoses, medications, test results, doctor's notes, everything. Be extremely thorough!"""

        print("[LAB ANALYZER] Calling Gemini Vision API for PDF analysis...")
        
        # Analyze with Gemini Vision
        response = gemini_model.generate_content([prompt, uploaded_file])
        analysis_text = response.text
        
        print(f"[LAB ANALYZER] ✅ PDF analysis complete ({len(analysis_text)} chars)")
        
        # Parse and return structured response
        return {
            "test_name": test_name,
            "summary": "Detailed PDF analysis completed",
            "full_analysis": analysis_text,
            "overall_assessment": _extract_section(analysis_text, "Overall Assessment") or analysis_text[:500],
            "interpretations": [_extract_section(analysis_text, "Detailed Interpretations") or analysis_text],
            "health_risks": [_extract_section(analysis_text, "Health Risks") or "See detailed analysis above"],
            "recommendations": [_extract_section(analysis_text, "Immediate Recommendations") or "Consult with healthcare provider"],
            "lifestyle_changes": [_extract_section(analysis_text, "Lifestyle Modifications") or "Follow general healthy lifestyle"],
            "follow_up_tests": [_extract_section(analysis_text, "Follow-up Tests") or "As recommended by doctor"],
            "abnormal_findings": [],
            "timestamp": datetime.now().isoformat(),
            "ai_generated": True,
            "analysis_type": "Gemini Vision PDF Analysis"
        }
        
    except Exception as e:
        print(f"[LAB ANALYZER] ❌ PDF analysis error: {e}")
        import traceback
        traceback.print_exc()
        return _fallback_analysis(lab_data)


def _extract_section(text: str, section_name: str) -> str:
    """Extract a specific section from Gemini's response"""
    lines = text.split('\n')
    in_section = False
    section_content = []
    
    for line in lines:
        if section_name.lower() in line.lower() and ('##' in line or '**' in line):
            in_section = True
            continue
        elif in_section and ('##' in line or (line.startswith('**') and line.endswith('**'))):
            # Next section started
            break
        elif in_section and line.strip():
            section_content.append(line)
    
    return '\n'.join(section_content).strip() if section_content else ""



def _build_gemini_analysis_prompt(lab_data: Dict) -> str:
    """Build comprehensive prompt for Gemini analysis"""
    
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
    
    prompt = f"""You are an expert medical AI assistant analyzing lab reports. Provide a COMPREHENSIVE, DETAILED analysis that is both medically accurate and patient-friendly.

**Patient Information:**
- Age: {patient_age}
- Gender: {patient_gender}

**Test Name:** {test_name}

**Results:**
{results_text}

**CRITICAL INSTRUCTIONS:**
Provide an EXTREMELY DETAILED analysis (minimum 500 words). Be thorough and comprehensive!

**Format your response as follows:**

## Overall Assessment
(3-4 paragraphs summarizing overall health status, significance of findings, and urgency level)

## Detailed Interpretations
(For EACH parameter - normal or abnormal - explain in detail):
- **Parameter Name**: What this test measures, what the value means, why it matters
- If abnormal: Explain the medical significance, potential causes, and health implications

## Health Risks
(List all potential health risks based on these results):
- **Risk Category**: Detailed explanation of the risk, why it's concerning, long-term implications

## Immediate Recommendations
(Specific, actionable steps the patient should take):
- **Action Item**: Detailed explanation of what to do, when, and why it's important

## Lifestyle Modifications
(Comprehensive lifestyle changes):
- **Diet**: Specific foods to eat/avoid with explanations
- **Exercise**: Exact exercise recommendations with frequency and duration
- **Habits**: Sleep, stress management, hydration, etc.

## Follow-up Tests
(Recommended additional tests):
- **Test Name**: Why this test is needed, what it will reveal

## When to Seek Medical Care
(Clear guidelines on urgency):
- Immediate (ER/911)
- Urgent (within 24-48 hours)
- Routine (schedule appointment)

**Tone:** Professional yet compassionate. Use simple language but don't oversimplify. Provide medical details but explain them clearly."""

    return prompt


def _parse_gemini_response(analysis_text: str, lab_data: Dict) -> Dict:
    """Parse Gemini's detailed response into structured format"""
    
    # Extract sections from Gemini's response
    sections = {
        'overall_assessment': '',
        'interpretations': [],
        'health_risks': [],
        'recommendations': [],
        'lifestyle_changes': [],
        'follow_up_tests': [],
        'urgency': ''
    }
    
    # Simple parsing - extract content between headers
    lines = analysis_text.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        line_lower = line.lower().strip()
        
        if 'overall assessment' in line_lower:
            current_section = 'overall_assessment'
            current_content = []
        elif 'interpretation' in line_lower:
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'interpretations'
            current_content = []
        elif 'health risk' in line_lower or 'risk' in line_lower:
            if current_section and current_content:
                if current_section == 'interpretations':
                    sections[current_section] = ['\n'.join(current_content).strip()]
                else:
                    sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'health_risks'
            current_content = []
        elif 'recommendation' in line_lower:
            if current_section and current_content:
                sections[current_section] = ['\n'.join(current_content).strip()] if isinstance(sections[current_section], list) else '\n'.join(current_content).strip()
            current_section = 'recommendations'
            current_content = []
        elif 'lifestyle' in line_lower or 'modification' in line_lower:
            if current_section and current_content:
                sections[current_section] = ['\n'.join(current_content).strip()] if isinstance(sections[current_section], list) else '\n'.join(current_content).strip()
            current_section = 'lifestyle_changes'
            current_content = []
        elif 'follow' in line_lower and 'test' in line_lower:
            if current_section and current_content:
                sections[current_section] = ['\n'.join(current_content).strip()] if isinstance(sections[current_section], list) else '\n'.join(current_content).strip()
            current_section = 'follow_up_tests'
            current_content = []
        elif line.strip() and not line.startswith('#'):
            current_content.append(line)
    
    # Add last section
    if current_section and current_content:
        if isinstance(sections[current_section], list):
            sections[current_section] = ['\n'.join(current_content).strip()]
        else:
            sections[current_section] = '\n'.join(current_content).strip()
    
    # Return structured analysis
    return {
        "test_name": lab_data.get('test_name', 'Lab Test'),
        "summary": "Detailed AI analysis completed",
        "overall_assessment": sections['overall_assessment'] or analysis_text[:500],
        "full_analysis": analysis_text,  # Include full Gemini response
        "abnormal_findings": _extract_abnormal_findings(lab_data),
        "interpretations": sections['interpretations'] if sections['interpretations'] else [analysis_text],
        "health_risks": sections['health_risks'] if sections['health_risks'] else ["See detailed analysis above"],
        "recommendations": sections['recommendations'] if sections['recommendations'] else ["Consult with healthcare provider"],
        "lifestyle_changes": sections['lifestyle_changes'] if sections['lifestyle_changes'] else ["Follow general healthy lifestyle"],
        "follow_up_tests": sections['follow_up_tests'] if sections['follow_up_tests'] else ["As recommended by doctor"],
        "timestamp": datetime.now().isoformat(),
        "ai_generated": True,
        "analysis_type": "Gemini AI Analysis"
    }



# Import pypdf for fallback text extraction
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# File upload analysis removed - Groq doesn't support file uploads yet
# Using text-based analysis only
def _analyze_file_with_groq_fallback(file_path: str, lab_data: Dict) -> Dict:
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
    """
    COMPREHENSIVE FALLBACK ANALYSIS
    Provides detailed, medical-grade analysis without external API
    """
    
    print("\n[LAB ANALYSIS] Using Intelligent Local Analysis Engine")
    
    abnormal_findings = _extract_abnormal_findings(lab_data)
    test_name = lab_data.get('test_name', 'Lab Test')
    results = lab_data.get('results', {})
    
    # Detailed recommendations and health risks based on findings
    recommendations = []
    health_risks = []
    interpretations = []
    follow_up_tests = []
    lifestyle_changes = []
    
    # Track categories for comprehensive summary
    has_diabetes_risk = False
    has_cardiac_risk = False
    has_anemia_risk = False
    has_kidney_risk = False
    has_liver_risk = False
    has_thyroid_issue = False
    
    # Analyze each abnormal finding in detail
    for finding in abnormal_findings:
        param = finding['parameter'].lower()
        status = finding['status']
        value = finding['value']
        
        # GLUCOSE / DIABETES
        if 'glucose' in param or 'sugar' in param:
            has_diabetes_risk = True
            if status == 'high':
                interpretations.append(f"**{finding['parameter']}**: Your blood sugar level ({value}) is elevated. This could indicate prediabetes or diabetes. High blood sugar over time can damage blood vessels, nerves, and organs.")
                health_risks.extend([
                    "**Diabetes Risk**: Elevated blood sugar increases risk of Type 2 diabetes",
                    "**Cardiovascular Disease**: High glucose damages blood vessels",
                    "**Nerve Damage**: Prolonged high sugar can cause neuropathy",
                    "**Kidney Disease**: Diabetes is a leading cause of kidney failure"
                ])
                recommendations.extend([
                    "**Immediate**: Schedule appointment with doctor for diabetes screening (HbA1c test)",
                    "**Diet**: Reduce refined carbs, sugary foods, and beverages",
                    "**Exercise**: 30 minutes of moderate activity daily (walking, cycling)",
                    "**Monitoring**: Check fasting blood sugar weekly"
                ])
                lifestyle_changes.extend([
                    "Switch to whole grains instead of white rice/bread",
                    "Increase fiber intake (vegetables, legumes, oats)",
                    "Avoid sugary drinks - choose water or unsweetened tea",
                    "Eat smaller, more frequent meals to stabilize blood sugar"
                ])
                follow_up_tests.extend(["HbA1c (Glycated Hemoglobin)", "Fasting Insulin Level", "Oral Glucose Tolerance Test"])
        
        # CHOLESTEROL / CARDIAC HEALTH
        elif 'cholesterol' in param or 'ldl' in param or 'hdl' in param or 'triglyceride' in param:
            has_cardiac_risk = True
            if 'ldl' in param and status == 'high':
                interpretations.append(f"**{finding['parameter']}**: Your LDL cholesterol ({value}) is high. LDL is 'bad' cholesterol that builds up in arteries, increasing heart attack and stroke risk.")
                health_risks.extend([
                    "**Heart Disease**: High LDL causes plaque buildup in arteries (atherosclerosis)",
                    "**Heart Attack**: Blocked coronary arteries can cause myocardial infarction",
                    "**Stroke**: Plaque in carotid arteries increases stroke risk",
                    "**Peripheral Artery Disease**: Reduced blood flow to limbs"
                ])
                recommendations.extend([
                    "**Immediate**: Consult cardiologist for cardiovascular risk assessment",
                    "**Diet**: Follow heart-healthy diet (Mediterranean or DASH diet)",
                    "**Medication**: May need statins - discuss with doctor",
                    "**Exercise**: 150 minutes/week of moderate aerobic activity"
                ])
                lifestyle_changes.extend([
                    "Reduce saturated fats (red meat, butter, cheese)",
                    "Increase omega-3 fatty acids (salmon, walnuts, flaxseeds)",
                    "Add soluble fiber (oats, beans, apples)",
                    "Quit smoking if applicable - major risk factor"
                ])
                follow_up_tests.extend(["Lipid Panel (repeat in 3 months)", "Cardiac Risk Markers (CRP, Homocysteine)", "ECG/Stress Test"])
            
            elif 'hdl' in param and status == 'low':
                interpretations.append(f"**{finding['parameter']}**: Your HDL cholesterol ({value}) is low. HDL is 'good' cholesterol that removes bad cholesterol from arteries. Low HDL increases heart disease risk.")
                health_risks.append("**Cardiovascular Disease**: Low HDL fails to protect against plaque buildup")
                recommendations.extend([
                    "**Exercise**: Aerobic exercise raises HDL levels",
                    "**Healthy Fats**: Include olive oil, avocados, nuts",
                    "**Weight Loss**: If overweight, losing 5-10% body weight helps"
                ])
                lifestyle_changes.extend([
                    "30-60 minutes of cardio exercise 5 days/week",
                    "Replace trans fats with healthy fats",
                    "Moderate alcohol (if approved by doctor) may raise HDL"
                ])
        
        # HEMOGLOBIN / ANEMIA
        elif 'hemoglobin' in param or 'hematocrit' in param:
            has_anemia_risk = True
            if status == 'low':
                interpretations.append(f"**{finding['parameter']}**: Your hemoglobin ({value}) is low, indicating anemia. Hemoglobin carries oxygen in blood. Low levels cause fatigue, weakness, and shortness of breath.")
                health_risks.extend([
                    "**Chronic Fatigue**: Insufficient oxygen delivery to tissues",
                    "**Heart Problems**: Heart works harder to pump oxygen-poor blood",
                    "**Pregnancy Complications**: If pregnant, increases risk to baby",
                    "**Weakened Immunity**: May affect immune function"
                ])
                recommendations.extend([
                    "**Immediate**: See doctor to determine cause (iron deficiency, B12 deficiency, chronic disease)",
                    "**Diet**: Increase iron-rich foods (red meat, spinach, lentils)",
                    "**Supplements**: May need iron, B12, or folate supplements",
                    "**Vitamin C**: Helps iron absorption - take with iron-rich meals"
                ])
                lifestyle_changes.extend([
                    "Eat iron-rich foods with vitamin C (orange juice with spinach)",
                    "Avoid tea/coffee with meals (inhibits iron absorption)",
                    "Include fortified cereals and whole grains",
                    "Cook in cast iron pans to increase iron intake"
                ])
                follow_up_tests.extend(["Iron Studies (Serum Iron, Ferritin, TIBC)", "Vitamin B12 and Folate Levels", "Complete Blood Count (repeat)"])
        
        # KIDNEY FUNCTION
        elif 'creatinine' in param or 'bun' in param or 'urea' in param:
            has_kidney_risk = True
            if status == 'high':
                interpretations.append(f"**{finding['parameter']}**: Elevated {finding['parameter']} ({value}) suggests reduced kidney function. Kidneys filter waste from blood. High levels indicate kidneys aren't working efficiently.")
                health_risks.extend([
                    "**Chronic Kidney Disease**: Progressive loss of kidney function",
                    "**Kidney Failure**: May eventually need dialysis",
                    "**Cardiovascular Disease**: Kidney disease increases heart disease risk",
                    "**Electrolyte Imbalance**: Can cause dangerous heart rhythms"
                ])
                recommendations.extend([
                    "**Urgent**: Consult nephrologist for kidney function assessment",
                    "**Blood Pressure**: Control hypertension (major cause of kidney damage)",
                    "**Diabetes Control**: If diabetic, tight glucose control protects kidneys",
                    "**Hydration**: Drink adequate water unless doctor advises restriction",
                    "**Medications**: Avoid NSAIDs (ibuprofen) - harmful to kidneys"
                ])
                lifestyle_changes.extend([
                    "Reduce protein intake if advised by doctor",
                    "Limit sodium to reduce blood pressure",
                    "Avoid processed foods high in phosphorus",
                    "Monitor and control blood pressure daily"
                ])
                follow_up_tests.extend(["eGFR (Estimated Glomerular Filtration Rate)", "Urine Albumin-to-Creatinine Ratio", "Kidney Ultrasound"])
        
        # LIVER FUNCTION
        elif any(x in param for x in ['alt', 'ast', 'sgpt', 'sgot', 'bilirubin', 'alp']):
            has_liver_risk = True
            if status == 'high':
                interpretations.append(f"**{finding['parameter']}**: Elevated liver enzyme ({value}) indicates liver inflammation or damage. This could be due to fatty liver, hepatitis, alcohol, or medications.")
                health_risks.extend([
                    "**Liver Disease**: Chronic inflammation can lead to cirrhosis",
                    "**Fatty Liver Disease**: Common in obesity and diabetes",
                    "**Hepatitis**: Viral or autoimmune liver inflammation",
                    "**Liver Failure**: Severe cases can progress to liver failure"
                ])
                recommendations.extend([
                    "**Immediate**: See gastroenterologist or hepatologist",
                    "**Alcohol**: Avoid alcohol completely until liver function normalizes",
                    "**Medications**: Review all medications with doctor (some are hepatotoxic)",
                    "**Weight Loss**: If overweight, gradual weight loss improves fatty liver"
                ])
                lifestyle_changes.extend([
                    "Eliminate alcohol and limit processed foods",
                    "Reduce sugar and refined carbs (causes fatty liver)",
                    "Increase vegetables, fruits, whole grains",
                    "Avoid hepatotoxic substances (certain herbs, supplements)"
                ])
                follow_up_tests.extend(["Hepatitis Panel (A, B, C)", "Liver Ultrasound or FibroScan", "Repeat Liver Function Tests in 4-6 weeks"])
        
        # THYROID
        elif 'tsh' in param or 'thyroid' in param:
            has_thyroid_issue = True
            if status == 'high':
                interpretations.append(f"**{finding['parameter']}**: Elevated TSH ({value}) suggests hypothyroidism (underactive thyroid). This slows metabolism, causing fatigue, weight gain, and cold intolerance.")
                health_risks.extend([
                    "**Metabolic Slowdown**: Weight gain, fatigue, depression",
                    "**Heart Disease**: High cholesterol and heart problems",
                    "**Infertility**: Can affect reproductive health",
                    "**Myxedema**: Severe hypothyroidism (rare but serious)"
                ])
                recommendations.extend([
                    "**Immediate**: See endocrinologist for thyroid evaluation",
                    "**Medication**: May need levothyroxine (thyroid hormone replacement)",
                    "**Monitoring**: Regular TSH checks to adjust medication dose"
                ])
                lifestyle_changes.extend([
                    "Ensure adequate iodine intake (iodized salt, seafood)",
                    "Selenium-rich foods (Brazil nuts, fish) support thyroid",
                    "Avoid excessive soy (may interfere with thyroid function)"
                ])
                follow_up_tests.extend(["Free T3 and Free T4 Levels", "Thyroid Antibodies (TPO, TG)", "Thyroid Ultrasound"])
            elif status == 'low':
                interpretations.append(f"**{finding['parameter']}**: Low TSH ({value}) suggests hyperthyroidism (overactive thyroid). This speeds up metabolism, causing weight loss, rapid heartbeat, and anxiety.")
                health_risks.extend([
                    "**Heart Problems**: Rapid heart rate, atrial fibrillation",
                    "**Bone Loss**: Increased osteoporosis risk",
                    "**Thyroid Storm**: Life-threatening complication (rare)"
                ])
                recommendations.extend([
                    "**Urgent**: See endocrinologist immediately",
                    "**Medication**: May need anti-thyroid drugs or radioactive iodine",
                    "**Heart Monitoring**: May need beta-blockers for heart rate"
                ])
                follow_up_tests.extend(["Free T3 and Free T4", "Thyroid Scan", "TSH Receptor Antibodies"])
    
    # Generate comprehensive overall assessment
    if not abnormal_findings:
        overall_assessment = f"""**Excellent News!** Your {test_name} results are all within normal ranges. This indicates good health in the areas tested. Continue maintaining your healthy lifestyle with balanced diet, regular exercise, adequate sleep, and stress management. Schedule routine check-ups as recommended by your doctor (typically annually for preventive care)."""
        summary = "Normal results"
    else:
        risk_summary = []
        if has_diabetes_risk:
            risk_summary.append("metabolic health (blood sugar)")
        if has_cardiac_risk:
            risk_summary.append("cardiovascular health (cholesterol)")
        if has_anemia_risk:
            risk_summary.append("blood health (anemia)")
        if has_kidney_risk:
            risk_summary.append("kidney function")
        if has_liver_risk:
            risk_summary.append("liver function")
        if has_thyroid_issue:
            risk_summary.append("thyroid function")
        
        risk_areas = ", ".join(risk_summary) if risk_summary else "certain health parameters"
        
        overall_assessment = f"""**Important Findings Detected**: Your {test_name} shows {len(abnormal_findings)} abnormal value(s) affecting {risk_areas}. While this requires attention, early detection allows for timely intervention. Follow the detailed recommendations below and consult your healthcare provider promptly. Many of these conditions are manageable with lifestyle changes and/or medication. **Do not ignore these findings** - early action prevents serious complications."""
        summary = f"{len(abnormal_findings)} abnormal finding(s) detected"
    
    # Remove duplicates while preserving order
    recommendations = list(dict.fromkeys(recommendations))
    health_risks = list(dict.fromkeys(health_risks))
    lifestyle_changes = list(dict.fromkeys(lifestyle_changes))
    follow_up_tests = list(dict.fromkeys(follow_up_tests))
    
    # Add general recommendations if none specific
    if not recommendations:
        recommendations = [
            "Continue healthy lifestyle habits",
            "Schedule annual check-ups",
            "Maintain balanced diet and regular exercise"
        ]
    
    if not lifestyle_changes:
        lifestyle_changes = [
            "Eat a balanced diet rich in fruits, vegetables, and whole grains",
            "Exercise regularly (150 minutes/week of moderate activity)",
            "Get 7-9 hours of quality sleep",
            "Manage stress through relaxation techniques",
            "Stay hydrated (8-10 glasses of water daily)"
        ]
    
    print(f"[LAB ANALYSIS] Generated comprehensive analysis: {len(interpretations)} interpretations, {len(recommendations)} recommendations")
    
    return {
        "test_name": test_name,
        "summary": summary,
        "overall_assessment": overall_assessment,
        "abnormal_findings": abnormal_findings,
        "interpretations": interpretations if interpretations else ["All values are within normal ranges. No specific concerns detected."],
        "health_risks": health_risks if health_risks else ["No significant health risks identified from these results."],
        "recommendations": recommendations,
        "lifestyle_changes": lifestyle_changes,
        "follow_up_tests": follow_up_tests if follow_up_tests else ["Routine annual check-up"],
        "timestamp": datetime.now().isoformat(),
        "ai_generated": False,
        "analysis_type": "Comprehensive Local Analysis"
    }

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
