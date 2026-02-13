"""
PrismCare Main API Server
Orchestrates backend services and provides REST API for frontend
Port: 5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import json
import os
from ai_engine import analyze_prescription

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
ABDM_SERVER_URL = "http://localhost:8080"
OVERRIDES_FILE = "overrides.json"
STATS_FILE = "stats.json"

# Initialize stats file
if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, 'w') as f:
        json.dump({
            "total_validations": 0,
            "risky_detections": 0,
            "safe_validations": 0,
            "total_overrides": 0
        }, f)

# Initialize overrides file
if not os.path.exists(OVERRIDES_FILE):
    with open(OVERRIDES_FILE, 'w') as f:
        json.dump([], f)

def update_stats(is_risky: bool, is_override: bool = False):
    """Update statistics"""
    with open(STATS_FILE, 'r') as f:
        stats = json.load(f)
    
    stats['total_validations'] += 1
    if is_risky:
        stats['risky_detections'] += 1
    else:
        stats['safe_validations'] += 1
    
    if is_override:
        stats['total_overrides'] += 1
    
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

@app.route('/api/login', methods=['POST'])
def login():
    """
    Patient/Doctor login endpoint
    Fetches patient details from mock ABDM server
    """
    data = request.get_json()
    abha_id = data.get('abha_id')
    
    if not abha_id:
        return jsonify({
            "error": "ABHA ID is required"
        }), 400
    
    try:
        # Query mock ABDM server for patient details
        patient_response = requests.get(
            f"{ABDM_SERVER_URL}/fhir/Patient",
            params={"identifier": abha_id},
            timeout=5
        )
        
        if patient_response.status_code == 404:
            return jsonify({
                "error": "Patient not found",
                "abha_id": abha_id
            }), 404
        
        patient_response.raise_for_status()
        patient_data = patient_response.json()
        
        # Get medication history
        med_response = requests.get(
            f"{ABDM_SERVER_URL}/fhir/MedicationRequest",
            params={"patient": abha_id},
            timeout=5
        )
        med_response.raise_for_status()
        med_data = med_response.json()
        
        # Extract medication list
        medications = []
        if med_data.get('entry'):
            for entry in med_data['entry']:
                resource = entry['resource']
                medications.append({
                    "name": resource['medicationCodeableConcept']['text'],
                    "dosage": resource['dosageInstruction'][0]['text'],
                    "status": resource['status'],
                    "start_date": resource['authoredOn']
                })
        
        return jsonify({
            "success": True,
            "patient": {
                "abha_id": patient_data['id'],
                "name": patient_data['name'][0]['text'],
                "age": patient_data.get('age'),
                "gender": patient_data['gender'],
                "medications": medications
            }
        }), 200
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Cannot connect to ABDM server. Please ensure mock_abdm_server.py is running on port 8080."
        }), 503
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch patient data: {str(e)}"
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate_prescription():
    """
    Validate prescription for drug interactions
    Uses AI engine for analysis
    """
    data = request.get_json()
    
    medication_history = data.get('history', [])
    new_medicine = data.get('new_medicine')
    
    if not new_medicine:
        return jsonify({
            "error": "new_medicine is required"
        }), 400
    
    try:
        # Call AI engine
        result = analyze_prescription(medication_history, new_medicine)
        
        # Update statistics
        is_risky = result['status'] == 'Risky'
        update_stats(is_risky)
        
        # Add timestamp
        result['timestamp'] = datetime.now().isoformat()
        result['medicine_checked'] = new_medicine
        result['current_medications'] = medication_history
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Analysis failed: {str(e)}"
        }), 500

@app.route('/api/admin/override', methods=['POST'])
def log_override():
    """
    Log doctor override of risk alert
    """
    data = request.get_json()
    
    required_fields = ['doctor_id', 'patient_id', 'drug', 'reason']
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": f"Missing required fields: {required_fields}"
        }), 400
    
    try:
        # Load existing overrides
        with open(OVERRIDES_FILE, 'r') as f:
            overrides = json.load(f)
        
        # Add new override
        override_entry = {
            "id": len(overrides) + 1,
            "timestamp": datetime.now().isoformat(),
            "doctor_id": data['doctor_id'],
            "doctor_name": data.get('doctor_name', 'Unknown'),
            "patient_id": data['patient_id'],
            "drug": data['drug'],
            "risk_level": data.get('risk_level', 'Unknown'),
            "reason": data['reason'],
            "status": "Pending Review"
        }
        
        overrides.append(override_entry)
        
        # Save to file
        with open(OVERRIDES_FILE, 'w') as f:
            json.dump(overrides, f, indent=2)
        
        # Update stats
        update_stats(is_risky=True, is_override=True)
        
        return jsonify({
            "success": True,
            "message": "Override logged successfully",
            "override_id": override_entry['id']
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to log override: {str(e)}"
        }), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    """
    Get system statistics for admin dashboard
    """
    try:
        # Load stats
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
        
        # Load overrides
        with open(OVERRIDES_FILE, 'r') as f:
            overrides = json.load(f)
        
        # Calculate additional metrics
        total = stats['total_validations']
        risk_percentage = (stats['risky_detections'] / total * 100) if total > 0 else 0
        override_rate = (stats['total_overrides'] / stats['risky_detections'] * 100) if stats['risky_detections'] > 0 else 0
        
        return jsonify({
            "total_validations": stats['total_validations'],
            "risky_detections": stats['risky_detections'],
            "safe_validations": stats['safe_validations'],
            "total_overrides": stats['total_overrides'],
            "risk_percentage": round(risk_percentage, 2),
            "override_rate": round(override_rate, 2),
            "recent_overrides": overrides[-10:] if len(overrides) > 10 else overrides,
            "system_uptime": "99.9%",
            "last_updated": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch stats: {str(e)}"
        }), 500

@app.route('/api/admin/overrides', methods=['GET'])
def get_all_overrides():
    """
    Get all override logs (with pagination)
    """
    try:
        with open(OVERRIDES_FILE, 'r') as f:
            overrides = json.load(f)
        
        # Get pagination params
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Calculate pagination
        start = (page - 1) * per_page
        end = start + per_page
        
        return jsonify({
            "overrides": overrides[start:end],
            "total": len(overrides),
            "page": page,
            "per_page": per_page,
            "total_pages": (len(overrides) + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch overrides: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "PrismCare API",
        "timestamp": datetime.now().isoformat(),
        "abdm_server": ABDM_SERVER_URL
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PrismCare API Server Starting...")
    print("=" * 60)
    print(f"📍 Running on: http://localhost:5000")
    print(f"🔗 ABDM Server: {ABDM_SERVER_URL}")
    print("\n📋 Available Endpoints:")
    print("  POST /api/login")
    print("  POST /api/validate")
    print("  POST /api/admin/override")
    print("  GET  /api/admin/stats")
    print("  GET  /api/admin/overrides")
    print("  GET  /health")
    print("\n⚠️  Make sure mock_abdm_server.py is running on port 8080!")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
