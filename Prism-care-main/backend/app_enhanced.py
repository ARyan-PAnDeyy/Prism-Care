"""
Enhanced PrismCare Main API Server
Integrates all new components: Enhanced ABDM, Preprocessing, AI Summarization, Enhanced AI Engine
Port: 5000
"""

import sys
# Ensure emoji in log output don't crash on Windows consoles (cp1252)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Import new modules
from data_preprocessor import preprocess_patient_data
from ai_summarizer import generate_medical_summary
from ai_engine_enhanced import analyze_prescription, get_test_recommendations, get_treatment_suggestions, chat_with_context
from xai_rag_engine import explain_drug_interaction
from lab_analyzer import analyze_lab_report, parse_lab_report_text
import tempfile

app = Flask(__name__)
# Enable CORS for all routes, including file uploads
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
ABDM_SERVER_URL = "http://localhost:8080"
OVERRIDES_FILE = "overrides.json"
STATS_FILE = "stats.json"
UPLOAD_FOLDER = 'temp_uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize stats file
if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, 'w') as f:
        json.dump({"total_checks": 0, "safe_count": 0, "risky_count": 0}, f)


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        "status": "healthy",
        "service": "Enhanced PrismCare API",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0"
    }), 200


@app.route('/api/patient/<abha_id>', methods=['GET'])
def get_patient_info(abha_id):
    """
    Get comprehensive patient information with preprocessing and AI summary
    """
    try:
        # Fetch patient demographics from ABDM
        response = requests.get(f"{ABDM_SERVER_URL}/fhir/Patient", params={"identifier": abha_id})
        
        if response.status_code != 200:
            return jsonify({"error": "Patient not found"}), 404
        
        patient_data = response.json()
        
        # Fetch additional data
        medications_response = requests.get(f"{ABDM_SERVER_URL}/fhir/MedicationRequest", params={"patient": abha_id})
        diagnoses_response = requests.get(f"{ABDM_SERVER_URL}/fhir/Condition", params={"patient": abha_id})
        labs_response = requests.get(f"{ABDM_SERVER_URL}/fhir/DiagnosticReport", params={"patient": abha_id})
        visits_response = requests.get(f"{ABDM_SERVER_URL}/fhir/Encounter", params={"patient": abha_id})
        
        # Combine all data
        comprehensive_data = {
            "id": patient_data.get("id"),
            "name": patient_data.get("name", [{}])[0].get("text", ""),
            "age": patient_data.get("age", 0),
            "gender": patient_data.get("gender", "").capitalize(),
            "medications": medications_response.json().get("entry", []) if medications_response.status_code == 200 else [],
            "diagnoses": diagnoses_response.json().get("entry", []) if diagnoses_response.status_code == 200 else [],
            "lab_reports": labs_response.json().get("entry", []) if labs_response.status_code == 200 else [],
            "visit_summaries": visits_response.json().get("entry", []) if visits_response.status_code == 200 else []
        }
        
        return jsonify(comprehensive_data), 200
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Cannot connect to ABDM server",
            "message": "Please ensure mock_abdm_server_enhanced.py is running on port 8080"
        }), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/patient/<abha_id>/summary', methods=['GET'])
def get_patient_summary(abha_id):
    """
    Get AI-generated medical summary for patient
    """
    try:
        # Fetch comprehensive patient data from enhanced ABDM server
        # For now, we'll fetch from the original endpoint structure
        response = requests.get(f"{ABDM_SERVER_URL}/fhir/Patient", params={"identifier": abha_id})
        
        if response.status_code != 200:
            return jsonify({"error": "Patient not found"}), 404
        
        # Get medications
        meds_response = requests.get(f"{ABDM_SERVER_URL}/fhir/MedicationRequest", params={"patient": abha_id})
        diagnoses_response = requests.get(f"{ABDM_SERVER_URL}/fhir/Condition", params={"patient": abha_id})
        labs_response = requests.get(f"{ABDM_SERVER_URL}/fhir/DiagnosticReport", params={"patient": abha_id})
        
        # Build patient data structure for AI summarization
        patient_data = {
            "id": abha_id,
            "name": response.json().get("name", [{}])[0].get("text", ""),
            "age": response.json().get("age", 0),
            "gender": response.json().get("gender", ""),
            "diagnoses": [],
            "medications": [],
            "lab_reports": []
        }

        # Parse Diagnoses
        if diagnoses_response.status_code == 200:
            for entry in diagnoses_response.json().get("entry", []):
                res = entry.get("resource", {})
                patient_data["diagnoses"].append({
                    "condition": res.get("code", {}).get("text", "Unknown"),
                    "diagnosed_date": res.get("onsetDateTime", "Unknown"),
                    "status": res.get("clinicalStatus", {}).get("coding", [{}])[0].get("code", "unknown"),
                    "severity": res.get("severity", {}).get("coding", [{}])[0].get("display", "unknown")
                })

        # Parse Medications
        if meds_response.status_code == 200:
            for entry in meds_response.json().get("entry", []):
                res = entry.get("resource", {})
                dosage_instr = res.get("dosageInstruction", [{}])[0]
                patient_data["medications"].append({
                    "medicine": res.get("medicationCodeableConcept", {}).get("text", "Unknown"),
                    "dosage": dosage_instr.get("text", ""),
                    "frequency": dosage_instr.get("timing", {}).get("repeat", {}).get("frequency", ""),
                    "status": res.get("status", "unknown"),
                    "purpose": res.get("reasonCode", [{}])[0].get("text", "")
                })

        # Parse Labs
        if labs_response.status_code == 200:
            for entry in labs_response.json().get("entry", []):
                res = entry.get("resource", {})
                patient_data["lab_reports"].append({
                    "test_name": res.get("code", {}).get("text", "Unknown"),
                    "date": res.get("effectiveDateTime", ""),
                    "result": res.get("result", {})
                })
        
        # For demo, return a structured summary
        target = request.args.get('target', 'doctor')
        summary = generate_medical_summary(patient_data, target_audience=target)
        
        return jsonify(summary), 200
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Cannot connect to ABDM server",
            "message": "Please ensure mock_abdm_server_enhanced.py is running on port 8080"
        }), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/check-safety', methods=['POST'])
def check_drug_safety():
    """
    Enhanced drug safety check with comprehensive analysis (Medications + Allergies + Conditions)
    """
    try:
        data = request.json
        abha_id = data.get('abha_id')
        new_medicine = data.get('medicine')
        
        if not abha_id or not new_medicine:
            return jsonify({"error": "Missing required fields"}), 400
        
        current_medications = []
        patient_context = {"allergies": [], "conditions": []}
        
        # Fetch patient data from ABDM
        try:
            # 1. Medications
            med_resp = requests.get(f"{ABDM_SERVER_URL}/fhir/MedicationRequest", params={"patient": abha_id})
            if med_resp.status_code == 200:
                for entry in med_resp.json().get("entry", []):
                    res = entry.get("resource", {})
                    if res.get("status") == "active":
                        med_name = res.get("medicationCodeableConcept", {}).get("text", "")
                        if med_name:
                            current_medications.append(med_name)

            # 2. Conditions
            cond_resp = requests.get(f"{ABDM_SERVER_URL}/fhir/Condition", params={"patient": abha_id})
            if cond_resp.status_code == 200:
                for entry in cond_resp.json().get("entry", []):
                    cond_name = entry.get("resource", {}).get("code", {}).get("text", "")
                    if cond_name:
                        patient_context["conditions"].append(cond_name)
            
            # 3. Allergies (Simulated implementation until endpoint exists)
            # In a real scenario: Fetch from AllergyIntolerance resource
            # Here we simulate an allergy if the patient has "Allergy" in their condition list or via mock logic
            # For testing: If ABHA003 is used, add 'Ibuprofen' allergy
            if abha_id == "ABHA003":
                patient_context["allergies"].append("Ibuprofen")
            if "Asthma" in patient_context["conditions"]:
                 patient_context["allergies"].append("Aspirin") # Common cross-sensitivity simulation
            
        except requests.exceptions.ConnectionError:
            return jsonify({
                "error": "Cannot connect to ABDM server",
                "message": "Please ensure mock_abdm_server_enhanced.py is running on port 8080"
            }), 503
        
        # Analyze using enhanced AI engine with context
        analysis_result = analyze_prescription(current_medications, new_medicine, patient_context)
        
        # Update statistics
        try:
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
            
            stats["total_checks"] += 1
            if analysis_result["status"] == "Safe":
                stats["safe_count"] += 1
            else:
                stats["risky_count"] += 1
            
            with open(STATS_FILE, 'w') as f:
                json.dump(stats, f)
        except Exception as e:
            print(f"Error updating stats: {e}")
        
        return jsonify(analysis_result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/patient/<abha_id>/test-recommendations', methods=['GET'])
def get_patient_test_recommendations(abha_id):
    """
    Get recommended tests based on patient's conditions and medications
    """
    try:
        # Fetch diagnoses and medications
        diagnoses_response = requests.get(f"{ABDM_SERVER_URL}/fhir/Condition", params={"patient": abha_id})
        meds_response = requests.get(f"{ABDM_SERVER_URL}/fhir/MedicationRequest", params={"patient": abha_id})
        
        if diagnoses_response.status_code != 200:
            return jsonify({"error": "Patient not found"}), 404
        
        # Parse data
        diagnoses = []
        medications = []
        
        for entry in diagnoses_response.json().get("entry", []):
            resource = entry.get("resource", {})
            diagnoses.append({
                "condition": resource.get("code", {}).get("text", ""),
                "status": resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code", "")
            })
        
        for entry in meds_response.json().get("entry", []):
            resource = entry.get("resource", {})
            medications.append({
                "medicine": resource.get("medicationCodeableConcept", {}).get("text", ""),
                "status": resource.get("status", "")
            })
        
        # Get recommendations
        recommendations = get_test_recommendations(diagnoses, medications)
        
        return jsonify({
            "patient_id": abha_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }), 200
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Cannot connect to ABDM server",
            "message": "Please ensure mock_abdm_server_enhanced.py is running on port 8080"
        }), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/patient/<abha_id>/treatment-suggestions', methods=['GET'])
def get_patient_treatment_suggestions(abha_id):
    """
    Get evidence-based treatment suggestions
    """
    try:
        diagnosis = request.args.get('diagnosis', '')
        
        if not diagnosis:
            return jsonify({"error": "Diagnosis parameter required"}), 400
        
        # Fetch current medications
        meds_response = requests.get(f"{ABDM_SERVER_URL}/fhir/MedicationRequest", params={"patient": abha_id})
        
        current_medications = []
        for entry in meds_response.json().get("entry", []):
            resource = entry.get("resource", {})
            if resource.get("status") == "active":
                med_name = resource.get("medicationCodeableConcept", {}).get("text", "")
                if med_name:
                    current_medications.append(med_name)
        
        # Get suggestions
        suggestions = get_treatment_suggestions(diagnosis, current_medications)
        
        return jsonify({
            "patient_id": abha_id,
            "diagnosis": diagnosis,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }), 200
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Cannot connect to ABDM server",
            "message": "Please ensure mock_abdm_server_enhanced.py is running on port 8080"
        }), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    try:
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/patient/<abha_id>/upload-lab', methods=['POST'])
def upload_lab_report(abha_id):
    """
    Upload and analyze lab report (Supports File Upload and JSON)
    """
    try:
        data = {}
        
        # Handle File Upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename:
                # Save file temporarily
                import werkzeug
                filename = werkzeug.utils.secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                data['file_path'] = filepath
                
                # Get other form data
                data['test_name'] = request.form.get('test_name', 'Uploaded Lab Report')
        
        # Handle JSON data (fallback or legacy)
        elif request.is_json:
            data = request.json
        else:
            # Maybe form data without file?
            data.update(request.form)

        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get patient info for context
        try:
            patient_response = requests.get(f"{ABDM_SERVER_URL}/fhir/Patient", params={"identifier": abha_id})
            if patient_response.status_code == 200:
                patient_data = patient_response.json()
                data['patient_age'] = patient_data.get('age', 'Unknown')
                data['patient_gender'] = patient_data.get('gender', 'Unknown')
        except:
            data['patient_age'] = 'Unknown'
            data['patient_gender'] = 'Unknown'
        
        # Analyze the lab report
        analysis = analyze_lab_report(data)
        
        # Add patient ID to response
        analysis['patient_id'] = abha_id
        
        # Clean up temp file
        if 'file_path' in data and os.path.exists(data['file_path']):
            try:
                os.remove(data['file_path'])
            except:
                pass
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/xai/explain', methods=['POST'])
def xai_explain():
    """
    RAG-powered XAI Explanation Endpoint
    Generates a detailed, Gemini-powered explanation for a drug safety decision
    with ChromaDB-retrieved evidence.

    Request body:
        { "abha_id": "ABHA001", "medicine": "Aspirin", "view_mode": "doctor" }

    Response:
        {
          "status": "Risky",
          "risk_level": "Critical",
          "generated_explanation": "...",
          "mechanism": "...",
          "recommendation": "...",
          "rag_retrieved_rules": [...],
          "sources": [...],
          "llm_used": true,
          "model": "gemini-2.0-flash-exp"
        }
    """
    try:
        data = request.json
        abha_id = data.get('abha_id')
        medicine = data.get('medicine')
        view_mode = data.get('view_mode', 'doctor')

        if not abha_id or not medicine:
            return jsonify({"error": "Missing required fields: abha_id and medicine"}), 400

        # 1. Fetch patient context from ABDM
        current_medications = []
        patient_context = {"allergies": [], "conditions": [], "age": None, "gender": None}

        try:
            # Patient demographics
            pat_resp = requests.get(f"{ABDM_SERVER_URL}/fhir/Patient", params={"identifier": abha_id})
            if pat_resp.status_code == 200:
                pat_data = pat_resp.json()
                patient_context["age"] = pat_data.get("age")
                patient_context["gender"] = pat_data.get("gender", "").capitalize()

            # Active medications
            med_resp = requests.get(f"{ABDM_SERVER_URL}/fhir/MedicationRequest", params={"patient": abha_id})
            if med_resp.status_code == 200:
                for entry in med_resp.json().get("entry", []):
                    res = entry.get("resource", {})
                    if res.get("status") == "active":
                        med_name = res.get("medicationCodeableConcept", {}).get("text", "")
                        if med_name:
                            current_medications.append(med_name)

            # Conditions
            cond_resp = requests.get(f"{ABDM_SERVER_URL}/fhir/Condition", params={"patient": abha_id})
            if cond_resp.status_code == 200:
                for entry in cond_resp.json().get("entry", []):
                    cond_name = entry.get("resource", {}).get("code", {}).get("text", "")
                    if cond_name:
                        patient_context["conditions"].append(cond_name)

            # Simulated allergies
            if abha_id == "ABHA003":
                patient_context["allergies"].append("Ibuprofen")
            if "Asthma" in patient_context["conditions"]:
                patient_context["allergies"].append("Aspirin")

        except requests.exceptions.ConnectionError:
            # Proceed without context if ABDM is down
            pass

        # 2. Run base drug safety analysis
        interaction_data = analyze_prescription(current_medications, medicine, patient_context)

        # 3. Generate XAI explanation via RAG + Gemini
        xai_result = explain_drug_interaction(
            medication_history=current_medications,
            new_drug=medicine,
            interaction_data=interaction_data,
            patient_context=patient_context,
            view_mode=view_mode
        )

        # 4. Combine and return
        return jsonify({
            "patient_id": abha_id,
            "medicine_checked": medicine,
            "view_mode": view_mode,
            "status": interaction_data.get("status"),
            "risk_level": interaction_data.get("risk_level", "Safe"),
            "confidence": interaction_data.get("confidence", 0.90),
            "mechanism": interaction_data.get("mechanism", "N/A"),
            "recommendation": interaction_data.get("recommendation", "Consult healthcare provider"),
            "patient_explanation": interaction_data.get("patient_explanation", ""),
            "doctor_explanation": interaction_data.get("doctor_explanation", ""),
            # XAI-specific fields
            "generated_explanation": xai_result["generated_explanation"],
            "rag_retrieved_rules": xai_result["rag_retrieved_rules"],
            "sources": xai_result["sources"],
            "llm_used": xai_result["llm_used"],
            "model": xai_result["model"],
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Context-aware Chat Endpoint
    """
    try:
        data = request.json
        abha_id = data.get('abha_id')
        user_query = data.get('query')
        history = data.get('history', [])
        
        if not abha_id or not user_query:
            return jsonify({"error": "Missing ABHA ID or query"}), 400
            
        # 1. Fetch Patient Context
        try:
            # Basic Info
            pat_resp = requests.get(f"{ABDM_SERVER_URL}/fhir/Patient", params={"identifier": abha_id})
            pat_data = pat_resp.json() if pat_resp.status_code == 200 else {}
            
            # Conditions
            cond_resp = requests.get(f"{ABDM_SERVER_URL}/fhir/Condition", params={"patient": abha_id})
            conditions = []
            if cond_resp.status_code == 200:
                for entry in cond_resp.json().get("entry", []):
                    conditions.append(entry["resource"]["code"]["text"])
            
            # Allergies (simulated for now as we don't have AllergyIntolerance endpoint mock yet, or we can use generic)
            # Checking if mock server has AllergyIntolerance, if not we assume none or extract from conditions if labeled
            allergies = []
            
            # Medications
            med_resp = requests.get(f"{ABDM_SERVER_URL}/fhir/MedicationRequest", params={"patient": abha_id})
            meds = []
            if med_resp.status_code == 200:
                 for entry in med_resp.json().get("entry", []):
                    if entry["resource"]["status"] == "active":
                        meds.append(entry["resource"]["medicationCodeableConcept"]["text"])
            
            patient_context = {
                "age": pat_data.get("age"),
                "gender": pat_data.get("gender"),
                "conditions": conditions,
                "allergies": allergies,  # Populate if available
                "medications": meds
            }
            
        except Exception as e:
            print(f"Context fetch error: {e}")
            patient_context = {}

        # 2. Call AI
        response_text = chat_with_context(history, user_query, patient_context)
        
        return jsonify({"response": response_text}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/override', methods=['POST'])
def set_override():
    """Admin endpoint to override AI decisions"""
    try:
        data = request.json
        interaction = data.get('interaction')
        override_decision = data.get('decision')
        
        if not interaction or not override_decision:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Load existing overrides
        try:
            with open(OVERRIDES_FILE, 'r') as f:
                overrides = json.load(f)
        except FileNotFoundError:
            overrides = {}
        
        # Add new override
        overrides[interaction] = {
            "decision": override_decision,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save
        with open(OVERRIDES_FILE, 'w') as f:
            json.dump(overrides, f, indent=2)
        
        return jsonify({"message": "Override saved successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("=" * 70)
    print("🏥 Enhanced PrismCare API Server Starting...")
    print("=" * 70)
    print(f"📍 Running on: http://localhost:5000")
    print(f"🔗 ABDM Server: {ABDM_SERVER_URL}")
    print("\n📋 Available Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/patient/<abha_id>")
    print("  GET  /api/patient/<abha_id>/summary")
    print("  POST /api/check-safety")
    print("  GET  /api/patient/<abha_id>/test-recommendations")
    print("  GET  /api/patient/<abha_id>/treatment-suggestions?diagnosis=<condition>")
    print("  POST /api/patient/<abha_id>/upload-lab")
    print("  GET  /api/stats")
    print("  POST /api/admin/override")
    print("\n🚀 New Features:")
    print("  ✅ AI-powered medical summarization")
    print("  ✅ 50+ drug interaction rules")
    print("  ✅ Test recommendations")
    print("  ✅ Treatment suggestions")
    print("  ✅ Lab report upload & AI analysis")
    print("  ✅ Data preprocessing pipeline")
    print("=" * 70)
    app.run(host='0.0.0.0', port=5000, debug=True)
