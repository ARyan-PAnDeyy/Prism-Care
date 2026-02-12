"""
Mock ABDM (Ayushman Bharat Digital Mission) Server
Simulates government health records server with FHIR-compliant endpoints
Port: 8080
"""

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Mock patient database
PATIENTS_DB = {
    "ABHA001": {
        "id": "ABHA001",
        "name": "Rajesh Kumar",
        "age": 58,
        "gender": "Male",
        "medication_history": [
            {
                "medicine": "Warfarin",
                "dosage": "5mg",
                "frequency": "Once daily",
                "start_date": "2025-06-15",
                "status": "active"
            },
            {
                "medicine": "Metformin",
                "dosage": "500mg",
                "frequency": "Twice daily",
                "start_date": "2025-01-10",
                "status": "active"
            }
        ]
    },
    "ABHA002": {
        "id": "ABHA002",
        "name": "Priya Sharma",
        "age": 42,
        "gender": "Female",
        "medication_history": [
            {
                "medicine": "Lisinopril",
                "dosage": "10mg",
                "frequency": "Once daily",
                "start_date": "2025-03-20",
                "status": "active"
            },
            {
                "medicine": "Atorvastatin",
                "dosage": "20mg",
                "frequency": "Once daily at night",
                "start_date": "2025-03-20",
                "status": "active"
            }
        ]
    },
    "ABHA003": {
        "id": "ABHA003",
        "name": "Mohammed Ali",
        "age": 35,
        "gender": "Male",
        "medication_history": [
            {
                "medicine": "Ibuprofen",
                "dosage": "400mg",
                "frequency": "As needed",
                "start_date": "2025-12-01",
                "status": "completed"
            }
        ]
    }
}

@app.route('/fhir/Patient', methods=['GET'])
def get_patient():
    """
    FHIR-compliant endpoint to retrieve patient demographics
    Query param: identifier (ABHA ID)
    """
    identifier = request.args.get('identifier')
    
    if not identifier:
        return jsonify({
            "error": "Missing identifier parameter"
        }), 400
    
    patient = PATIENTS_DB.get(identifier)
    
    if not patient:
        return jsonify({
            "error": "Patient not found",
            "identifier": identifier
        }), 404
    
    # FHIR-compliant response structure
    return jsonify({
        "resourceType": "Patient",
        "id": patient["id"],
        "identifier": [{
            "system": "https://healthid.ndhm.gov.in",
            "value": patient["id"]
        }],
        "name": [{
            "text": patient["name"]
        }],
        "gender": patient["gender"].lower(),
        "birthDate": str(datetime.now().year - patient["age"]) + "-01-01",
        "age": patient["age"]
    }), 200

@app.route('/fhir/MedicationRequest', methods=['GET'])
def get_medication_history():
    """
    FHIR-compliant endpoint to retrieve patient's medication history
    Query param: patient (ABHA ID)
    """
    patient_id = request.args.get('patient')
    
    if not patient_id:
        return jsonify({
            "error": "Missing patient parameter"
        }), 400
    
    patient = PATIENTS_DB.get(patient_id)
    
    if not patient:
        return jsonify({
            "error": "Patient not found",
            "patient": patient_id
        }), 404
    
    # FHIR-compliant medication request bundle
    medication_requests = []
    for med in patient["medication_history"]:
        medication_requests.append({
            "resourceType": "MedicationRequest",
            "status": med["status"],
            "intent": "order",
            "medicationCodeableConcept": {
                "text": med["medicine"]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "dosageInstruction": [{
                "text": f"{med['dosage']} {med['frequency']}",
                "timing": {
                    "repeat": {
                        "frequency": med["frequency"]
                    }
                },
                "doseAndRate": [{
                    "doseQuantity": {
                        "value": med["dosage"]
                    }
                }]
            }],
            "authoredOn": med["start_date"]
        })
    
    return jsonify({
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(medication_requests),
        "entry": [{"resource": req} for req in medication_requests]
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Mock ABDM Server",
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 Mock ABDM Server Starting...")
    print("=" * 60)
    print(f"📍 Running on: http://localhost:8080")
    print(f"📊 Mock Patients: {len(PATIENTS_DB)}")
    print("\n📋 Available Endpoints:")
    print("  GET /fhir/Patient?identifier=<ABHA_ID>")
    print("  GET /fhir/MedicationRequest?patient=<ABHA_ID>")
    print("  GET /health")
    print("\n💡 Sample ABHA IDs: ABHA001, ABHA002, ABHA003")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8080, debug=True)
