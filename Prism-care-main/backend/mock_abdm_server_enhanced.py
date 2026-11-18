"""
Enhanced Mock ABDM (Ayushman Bharat Digital Mission) Server
Simulates comprehensive government health records with FHIR-compliant endpoints
Includes: Lab Reports, Diagnoses, Treatment History, Visit Summaries
Port: 8080
"""

import sys
# Ensure emoji in log output don't crash on Windows consoles (cp1252)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Comprehensive Mock Patient Database with Complete Medical Records
PATIENTS_DB = {
    "ABHA001": {
        "id": "ABHA001",
        "name": "Rajesh Kumar",
        "age": 58,
        "gender": "Male",
        "blood_group": "B+",
        "height": 172,  # cm
        "weight": 78,   # kg
        "phone": "+91-9876543210",
        "email": "rajesh.kumar@email.com",
        
        # Diagnoses
        "diagnoses": [
            {
                "condition": "Type 2 Diabetes Mellitus",
                "icd_code": "E11",
                "diagnosed_date": "2020-06-15",
                "status": "active",
                "severity": "moderate",
                "notes": "Well-controlled with medication. HbA1c trending stable."
            },
            {
                "condition": "Atrial Fibrillation",
                "icd_code": "I48",
                "diagnosed_date": "2021-03-20",
                "status": "active",
                "severity": "moderate",
                "notes": "On anticoagulation therapy. Regular monitoring required."
            },
            {
                "condition": "Hypertension",
                "icd_code": "I10",
                "diagnosed_date": "2019-01-10",
                "status": "active",
                "severity": "mild",
                "notes": "Controlled with lifestyle modifications and medication."
            }
        ],
        
        # Medication History
        "medications": [
            {
                "medicine": "Warfarin",
                "dosage": "5mg",
                "frequency": "Once daily",
                "start_date": "2021-03-25",
                "status": "active",
                "purpose": "Anticoagulation for atrial fibrillation",
                "prescribing_doctor": "Dr. Sharma (Cardiologist)"
            },
            {
                "medicine": "Metformin",
                "dosage": "500mg",
                "frequency": "Twice daily",
                "start_date": "2020-06-20",
                "status": "active",
                "purpose": "Blood sugar control",
                "prescribing_doctor": "Dr. Verma (Endocrinologist)"
            },
            {
                "medicine": "Amlodipine",
                "dosage": "5mg",
                "frequency": "Once daily",
                "start_date": "2019-01-15",
                "status": "active",
                "purpose": "Blood pressure control",
                "prescribing_doctor": "Dr. Patel (General Physician)"
            }
        ],
        
        # Lab Reports
        "lab_reports": [
            {
                "report_id": "LAB001",
                "test_name": "Complete Blood Count (CBC)",
                "date": "2024-02-01",
                "ordered_by": "Dr. Sharma",
                "results": {
                    "hemoglobin": {"value": 13.5, "unit": "g/dL", "normal_range": "13-17", "status": "normal"},
                    "wbc": {"value": 7500, "unit": "cells/μL", "normal_range": "4000-11000", "status": "normal"},
                    "platelets": {"value": 250000, "unit": "cells/μL", "normal_range": "150000-450000", "status": "normal"},
                    "rbc": {"value": 4.8, "unit": "million/μL", "normal_range": "4.5-5.5", "status": "normal"}
                }
            },
            {
                "report_id": "LAB002",
                "test_name": "HbA1c (Glycated Hemoglobin)",
                "date": "2024-01-28",
                "ordered_by": "Dr. Verma",
                "results": {
                    "hba1c": {"value": 6.8, "unit": "%", "normal_range": "<5.7", "status": "elevated", "interpretation": "Diabetes controlled"}
                }
            },
            {
                "report_id": "LAB003",
                "test_name": "Lipid Profile",
                "date": "2024-01-25",
                "ordered_by": "Dr. Sharma",
                "results": {
                    "total_cholesterol": {"value": 210, "unit": "mg/dL", "normal_range": "<200", "status": "borderline"},
                    "ldl": {"value": 135, "unit": "mg/dL", "normal_range": "<100", "status": "high"},
                    "hdl": {"value": 45, "unit": "mg/dL", "normal_range": ">40", "status": "normal"},
                    "triglycerides": {"value": 150, "unit": "mg/dL", "normal_range": "<150", "status": "normal"}
                }
            },
            {
                "report_id": "LAB004",
                "test_name": "Kidney Function Test",
                "date": "2024-01-20",
                "ordered_by": "Dr. Verma",
                "results": {
                    "creatinine": {"value": 1.1, "unit": "mg/dL", "normal_range": "0.7-1.3", "status": "normal"},
                    "bun": {"value": 18, "unit": "mg/dL", "normal_range": "7-20", "status": "normal"},
                    "egfr": {"value": 75, "unit": "mL/min/1.73m²", "normal_range": ">60", "status": "normal"}
                }
            },
            {
                "report_id": "LAB005",
                "test_name": "INR (International Normalized Ratio)",
                "date": "2024-02-05",
                "ordered_by": "Dr. Sharma",
                "results": {
                    "inr": {"value": 2.3, "unit": "", "normal_range": "2.0-3.0", "status": "therapeutic", "interpretation": "Warfarin dose appropriate"}
                }
            },
            # HISTORICAL DATA ADDED HERE
            {
                "report_id": "LABH001",
                "test_name": "HbA1c (Glycated Hemoglobin)",
                "date": "2023-10-15",
                "ordered_by": "Dr. Verma",
                "results": {
                    "hba1c": {"value": 7.2, "unit": "%", "normal_range": "<5.7", "status": "high", "interpretation": "Diabetes slightly uncontrolled"}
                }
            },
            {
                "report_id": "LABH002",
                "test_name": "HbA1c (Glycated Hemoglobin)",
                "date": "2023-06-10",
                "ordered_by": "Dr. Verma",
                "results": {
                    "hba1c": {"value": 7.5, "unit": "%", "normal_range": "<5.7", "status": "high", "interpretation": "Diabetes uncontrolled"}
                }
            },
            {
                "report_id": "LABH003",
                "test_name": "INR (International Normalized Ratio)",
                "date": "2024-01-05",
                "ordered_by": "Dr. Sharma",
                "results": {
                    "inr": {"value": 1.8, "unit": "", "normal_range": "2.0-3.0", "status": "low", "interpretation": "Sub-therapeutic, dose adjustment needed"}
                }
            },
            {
                "report_id": "LABH004",
                "test_name": "Lipid Profile",
                "date": "2023-08-20",
                "ordered_by": "Dr. Sharma",
                "results": {
                    "total_cholesterol": {"value": 230, "unit": "mg/dL", "normal_range": "<200", "status": "high"},
                    "ldl": {"value": 155, "unit": "mg/dL", "normal_range": "<100", "status": "high"},
                    "hdl": {"value": 42, "unit": "mg/dL", "normal_range": ">40", "status": "normal"},
                    "triglycerides": {"value": 165, "unit": "mg/dL", "normal_range": "<150", "status": "borderline"}
                }
            }
        ],
        
        # Treatment History
        "treatment_history": [
            {
                "procedure": "ECG (Electrocardiogram)",
                "date": "2024-01-15",
                "performed_by": "Dr. Sharma",
                "facility": "City Heart Clinic",
                "outcome": "Atrial fibrillation confirmed, rate controlled",
                "notes": "Regular rhythm monitoring advised"
            },
            {
                "procedure": "Diabetes Education Session",
                "date": "2023-12-10",
                "performed_by": "Diabetes Educator",
                "facility": "Wellness Center",
                "outcome": "Patient educated on diet and exercise",
                "notes": "Follow-up in 3 months"
            },
            {
                "procedure": "Echocardiogram",
                "date": "2023-05-20",
                "performed_by": "Dr. Sharma",
                "facility": "City Heart Clinic",
                "outcome": "Mild left atrial enlargement, normal LV function",
                "notes": "LVEF 60%"
            }
        ],
        
        # Visit Summaries
        "visit_summaries": [
            {
                "visit_id": "V001",
                "date": "2024-02-05",
                "doctor": "Dr. Sharma (Cardiologist)",
                "facility": "City Heart Clinic",
                "chief_complaint": "Routine follow-up for atrial fibrillation",
                "vitals": {
                    "bp": "132/84 mmHg",
                    "pulse": "78 bpm (irregular)",
                    "temperature": "98.4°F",
                    "spo2": "97%"
                },
                "assessment": "Atrial fibrillation well-controlled on current medication. INR within therapeutic range.",
                "plan": "Continue Warfarin 5mg daily. Repeat INR in 4 weeks. Monitor for bleeding signs.",
                "next_visit": "2024-03-05"
            },
            {
                "visit_id": "V002",
                "date": "2024-01-28",
                "doctor": "Dr. Verma (Endocrinologist)",
                "facility": "Diabetes Care Center",
                "chief_complaint": "Diabetes management review",
                "vitals": {
                    "bp": "128/82 mmHg",
                    "pulse": "76 bpm",
                    "weight": "78 kg",
                    "bmi": "26.4"
                },
                "assessment": "Type 2 DM adequately controlled. HbA1c at 6.8%. No complications noted.",
                "plan": "Continue Metformin 500mg BD. Dietary counseling. Increase physical activity. Repeat HbA1c in 3 months.",
                "next_visit": "2024-04-28"
            },
            # HISTORICAL VISITS ADDED HERE
            {
                "visit_id": "V003",
                "date": "2023-10-15",
                "doctor": "Dr. Verma (Endocrinologist)",
                "facility": "Diabetes Care Center",
                "chief_complaint": "Follow-up for diabetes, feeling fatigued",
                "vitals": {
                    "bp": "135/85 mmHg",
                    "pulse": "80 bpm",
                    "weight": "80 kg",
                    "bmi": "27.0"
                },
                "assessment": "HbA1c elevated at 7.2%. Weight increased by 2kg. Dietary non-compliance suspected.",
                "plan": "Reinforce lifestyle changes. Retain current medication dose. Review in 3 months.",
                "next_visit": "2024-01-15"
            },
            {
                "visit_id": "V004",
                "date": "2023-08-20",
                "doctor": "Dr. Sharma (Cardiologist)",
                "facility": "City Heart Clinic",
                "chief_complaint": "Palpitations occasionally",
                "vitals": {
                    "bp": "140/90 mmHg",
                    "pulse": "88 bpm (irregular)",
                    "weight": "79 kg"
                },
                "assessment": "BP elevated. Lipid profile shows high LDL. HR controlled but slightly fast.",
                "plan": "Added Amlodipine 5mg. Dietary advice for cholesterol. Continue Warfarin.",
                "next_visit": "2023-11-20"
            }
        ]
    },
    
    "ABHA002": {
        "id": "ABHA002",
        "name": "Priya Sharma",
        "age": 42,
        "gender": "Female",
        "blood_group": "O+",
        "height": 165,
        "weight": 68,
        "phone": "+91-9876543211",
        "email": "priya.sharma@email.com",
        
        "diagnoses": [
            {
                "condition": "Essential Hypertension",
                "icd_code": "I10",
                "diagnosed_date": "2022-03-15",
                "status": "active",
                "severity": "moderate",
                "notes": "Controlled with ACE inhibitor and lifestyle modifications"
            },
            {
                "condition": "Hyperlipidemia",
                "icd_code": "E78.5",
                "diagnosed_date": "2022-03-15",
                "status": "active",
                "severity": "moderate",
                "notes": "On statin therapy with good response"
            },
            {
                "condition": "Vitamin D Deficiency",
                "icd_code": "E55.9",
                "diagnosed_date": "2023-06-10",
                "status": "resolved",
                "severity": "mild",
                "notes": "Treated with supplementation, levels normalized"
            }
        ],
        
        "medications": [
            {
                "medicine": "Lisinopril",
                "dosage": "10mg",
                "frequency": "Once daily",
                "start_date": "2022-03-20",
                "status": "active",
                "purpose": "Blood pressure control",
                "prescribing_doctor": "Dr. Gupta (Cardiologist)"
            },
            {
                "medicine": "Atorvastatin",
                "dosage": "20mg",
                "frequency": "Once daily at night",
                "start_date": "2022-03-20",
                "status": "active",
                "purpose": "Cholesterol management",
                "prescribing_doctor": "Dr. Gupta (Cardiologist)"
            }
        ],
        
        "lab_reports": [
            {
                "report_id": "LAB101",
                "test_name": "Lipid Profile",
                "date": "2024-01-30",
                "ordered_by": "Dr. Gupta",
                "results": {
                    "total_cholesterol": {"value": 185, "unit": "mg/dL", "normal_range": "<200", "status": "normal"},
                    "ldl": {"value": 105, "unit": "mg/dL", "normal_range": "<100", "status": "borderline"},
                    "hdl": {"value": 58, "unit": "mg/dL", "normal_range": ">50", "status": "normal"},
                    "triglycerides": {"value": 110, "unit": "mg/dL", "normal_range": "<150", "status": "normal"}
                }
            },
            {
                "report_id": "LAB102",
                "test_name": "Complete Blood Count",
                "date": "2024-01-30",
                "ordered_by": "Dr. Gupta",
                "results": {
                    "hemoglobin": {"value": 12.8, "unit": "g/dL", "normal_range": "12-16", "status": "normal"},
                    "wbc": {"value": 6800, "unit": "cells/μL", "normal_range": "4000-11000", "status": "normal"},
                    "platelets": {"value": 280000, "unit": "cells/μL", "normal_range": "150000-450000", "status": "normal"}
                }
            },
            {
                "report_id": "LAB103",
                "test_name": "Thyroid Function Test",
                "date": "2024-01-25",
                "ordered_by": "Dr. Gupta",
                "results": {
                    "tsh": {"value": 2.8, "unit": "μIU/mL", "normal_range": "0.4-4.0", "status": "normal"},
                    "t3": {"value": 1.2, "unit": "ng/mL", "normal_range": "0.8-2.0", "status": "normal"},
                    "t4": {"value": 8.5, "unit": "μg/dL", "normal_range": "5-12", "status": "normal"}
                }
            }
        ],
        
        "treatment_history": [
            {
                "procedure": "ECG",
                "date": "2024-01-15",
                "performed_by": "Dr. Gupta",
                "facility": "Heart Care Hospital",
                "outcome": "Normal sinus rhythm",
                "notes": "No cardiac abnormalities detected"
            }
        ],
        
        "visit_summaries": [
            {
                "visit_id": "V101",
                "date": "2024-01-30",
                "doctor": "Dr. Gupta (Cardiologist)",
                "facility": "Heart Care Hospital",
                "chief_complaint": "Routine BP and cholesterol check",
                "vitals": {
                    "bp": "124/78 mmHg",
                    "pulse": "72 bpm",
                    "weight": "68 kg",
                    "bmi": "25.0"
                },
                "assessment": "Hypertension and hyperlipidemia well-controlled on current regimen. No adverse effects reported.",
                "plan": "Continue Lisinopril 10mg and Atorvastatin 20mg. Maintain low-salt diet. Regular exercise. Follow-up in 6 months.",
                "next_visit": "2024-07-30"
            }
        ]
    },
    
    "ABHA003": {
        "id": "ABHA003",
        "name": "Mohammed Ali",
        "age": 35,
        "gender": "Male",
        "blood_group": "A+",
        "height": 178,
        "weight": 82,
        "phone": "+91-9876543212",
        "email": "mohammed.ali@email.com",
        
        "diagnoses": [
            {
                "condition": "Chronic Lower Back Pain",
                "icd_code": "M54.5",
                "diagnosed_date": "2023-08-10",
                "status": "active",
                "severity": "mild",
                "notes": "Managed with physiotherapy and NSAIDs as needed"
            }
        ],
        
        "medications": [
            {
                "medicine": "Ibuprofen",
                "dosage": "400mg",
                "frequency": "As needed (max 3 times daily)",
                "start_date": "2023-12-01",
                "end_date": "2024-01-15",
                "status": "completed",
                "purpose": "Pain relief for back pain",
                "prescribing_doctor": "Dr. Singh (Orthopedic)"
            }
        ],
        
        "lab_reports": [
            {
                "report_id": "LAB201",
                "test_name": "Complete Blood Count",
                "date": "2024-01-10",
                "ordered_by": "Dr. Singh",
                "results": {
                    "hemoglobin": {"value": 15.2, "unit": "g/dL", "normal_range": "13-17", "status": "normal"},
                    "wbc": {"value": 7200, "unit": "cells/μL", "normal_range": "4000-11000", "status": "normal"},
                    "platelets": {"value": 240000, "unit": "cells/μL", "normal_range": "150000-450000", "status": "normal"}
                }
            }
        ],
        
        "treatment_history": [
            {
                "procedure": "Physiotherapy Sessions",
                "date": "2023-09-01 to 2023-11-30",
                "performed_by": "Physiotherapist Team",
                "facility": "Wellness Physio Center",
                "outcome": "Significant improvement in mobility and pain reduction",
                "notes": "Completed 12 sessions. Home exercises prescribed."
            }
        ],
        
        "visit_summaries": [
            {
                "visit_id": "V201",
                "date": "2024-01-10",
                "doctor": "Dr. Singh (Orthopedic)",
                "facility": "Bone & Joint Clinic",
                "chief_complaint": "Follow-up for lower back pain",
                "vitals": {
                    "bp": "118/76 mmHg",
                    "pulse": "68 bpm",
                    "weight": "82 kg"
                },
                "assessment": "Back pain significantly improved with physiotherapy. No medication needed currently.",
                "plan": "Continue home exercises. Avoid heavy lifting. Return if pain recurs.",
                "next_visit": "As needed"
            }
        ]
    }
}

# Add more patients for comprehensive testing
PATIENTS_DB.update({
    "ABHA004": {
        "id": "ABHA004",
        "name": "Sunita Devi",
        "age": 65,
        "gender": "Female",
        "blood_group": "AB+",
        "height": 158,
        "weight": 72,
        "phone": "+91-9876543213",
        "email": "sunita.devi@email.com",
        
        "diagnoses": [
            {
                "condition": "Osteoarthritis",
                "icd_code": "M19.90",
                "diagnosed_date": "2021-05-20",
                "status": "active",
                "severity": "moderate",
                "notes": "Bilateral knee osteoarthritis. Managed conservatively."
            },
            {
                "condition": "Type 2 Diabetes Mellitus",
                "icd_code": "E11",
                "diagnosed_date": "2018-03-10",
                "status": "active",
                "severity": "moderate",
                "notes": "On oral hypoglycemics with good control"
            },
            {
                "condition": "Hypothyroidism",
                "icd_code": "E03.9",
                "diagnosed_date": "2019-07-15",
                "status": "active",
                "severity": "mild",
                "notes": "Well-controlled on levothyroxine"
            }
        ],
        
        "medications": [
            {
                "medicine": "Glimepiride",
                "dosage": "2mg",
                "frequency": "Once daily before breakfast",
                "start_date": "2018-03-15",
                "status": "active",
                "purpose": "Blood sugar control",
                "prescribing_doctor": "Dr. Mehta (Endocrinologist)"
            },
            {
                "medicine": "Levothyroxine",
                "dosage": "75mcg",
                "frequency": "Once daily on empty stomach",
                "start_date": "2019-07-20",
                "status": "active",
                "purpose": "Thyroid hormone replacement",
                "prescribing_doctor": "Dr. Mehta (Endocrinologist)"
            },
            {
                "medicine": "Glucosamine",
                "dosage": "1500mg",
                "frequency": "Once daily",
                "start_date": "2021-06-01",
                "status": "active",
                "purpose": "Joint health support",
                "prescribing_doctor": "Dr. Kapoor (Orthopedic)"
            }
        ],
        
        "lab_reports": [
            {
                "report_id": "LAB301",
                "test_name": "HbA1c",
                "date": "2024-01-20",
                "ordered_by": "Dr. Mehta",
                "results": {
                    "hba1c": {"value": 6.5, "unit": "%", "normal_range": "<5.7", "status": "elevated", "interpretation": "Diabetes well-controlled"}
                }
            },
            {
                "report_id": "LAB302",
                "test_name": "Thyroid Function Test",
                "date": "2024-01-18",
                "ordered_by": "Dr. Mehta",
                "results": {
                    "tsh": {"value": 2.1, "unit": "μIU/mL", "normal_range": "0.4-4.0", "status": "normal"},
                    "t4": {"value": 9.2, "unit": "μg/dL", "normal_range": "5-12", "status": "normal"}
                }
            }
        ],
        
        "treatment_history": [],
        "visit_summaries": [
            {
                "visit_id": "V301",
                "date": "2024-01-20",
                "doctor": "Dr. Mehta (Endocrinologist)",
                "facility": "Diabetes & Thyroid Center",
                "chief_complaint": "Routine diabetes and thyroid check",
                "vitals": {
                    "bp": "138/86 mmHg",
                    "pulse": "74 bpm",
                    "weight": "72 kg"
                },
                "assessment": "Diabetes and hypothyroidism well-controlled. Knee pain managed with supplements.",
                "plan": "Continue current medications. Low-impact exercises for joints. Follow-up in 3 months.",
                "next_visit": "2024-04-20"
            }
        ]
    },
    
    "ABHA005": {
        "id": "ABHA005",
        "name": "Amit Patel",
        "age": 28,
        "gender": "Male",
        "blood_group": "B-",
        "height": 175,
        "weight": 75,
        "phone": "+91-9876543214",
        "email": "amit.patel@email.com",
        
        "diagnoses": [
            {
                "condition": "Seasonal Allergic Rhinitis",
                "icd_code": "J30.2",
                "diagnosed_date": "2023-03-15",
                "status": "active",
                "severity": "mild",
                "notes": "Seasonal allergies, well-managed with antihistamines"
            }
        ],
        
        "medications": [
            {
                "medicine": "Cetirizine",
                "dosage": "10mg",
                "frequency": "Once daily as needed",
                "start_date": "2023-03-20",
                "status": "active",
                "purpose": "Allergy relief",
                "prescribing_doctor": "Dr. Reddy (ENT Specialist)"
            }
        ],
        
        "lab_reports": [
            {
                "report_id": "LAB401",
                "test_name": "Complete Blood Count",
                "date": "2024-01-05",
                "ordered_by": "Dr. Reddy",
                "results": {
                    "hemoglobin": {"value": 14.8, "unit": "g/dL", "normal_range": "13-17", "status": "normal"},
                    "wbc": {"value": 8200, "unit": "cells/μL", "normal_range": "4000-11000", "status": "normal"},
                    "eosinophils": {"value": 6, "unit": "%", "normal_range": "1-4", "status": "elevated", "interpretation": "Mild eosinophilia consistent with allergies"}
                }
            }
        ],
        
        "treatment_history": [],
        "visit_summaries": [
            {
                "visit_id": "V401",
                "date": "2024-01-05",
                "doctor": "Dr. Reddy (ENT Specialist)",
                "facility": "ENT Care Clinic",
                "chief_complaint": "Seasonal allergy symptoms",
                "vitals": {
                    "bp": "120/78 mmHg",
                    "pulse": "70 bpm",
                    "weight": "75 kg"
                },
                "assessment": "Mild seasonal allergic rhinitis. No complications.",
                "plan": "Continue Cetirizine as needed. Avoid known allergens. Return if symptoms worsen.",
                "next_visit": "As needed"
            }
        ]
    }
})


# FHIR-Compliant Endpoints

@app.route('/fhir/Patient', methods=['GET'])
def get_patient():
    """Get patient demographics"""
    identifier = request.args.get('identifier')
    
    if not identifier:
        return jsonify({"error": "Missing identifier parameter"}), 400
    
    patient = PATIENTS_DB.get(identifier)
    
    if not patient:
        return jsonify({"error": "Patient not found", "identifier": identifier}), 404
    
    return jsonify({
        "resourceType": "Patient",
        "id": patient["id"],
        "identifier": [{"system": "https://healthid.ndhm.gov.in", "value": patient["id"]}],
        "name": [{"text": patient["name"]}],
        "gender": patient["gender"].lower(),
        "birthDate": str(datetime.now().year - patient["age"]) + "-01-01",
        "age": patient["age"],
        "telecom": [
            {"system": "phone", "value": patient.get("phone", "")},
            {"system": "email", "value": patient.get("email", "")}
        ],
        "extension": [
            {"url": "blood_group", "valueString": patient.get("blood_group", "")},
            {"url": "height", "valueInteger": patient.get("height", 0)},
            {"url": "weight", "valueInteger": patient.get("weight", 0)}
        ]
    }), 200


@app.route('/fhir/MedicationRequest', methods=['GET'])
def get_medication_history():
    """Get patient's medication history"""
    patient_id = request.args.get('patient')
    
    if not patient_id:
        return jsonify({"error": "Missing patient parameter"}), 400
    
    patient = PATIENTS_DB.get(patient_id)
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    medication_requests = []
    for med in patient.get("medications", []):
        medication_requests.append({
            "resourceType": "MedicationRequest",
            "status": med["status"],
            "intent": "order",
            "medicationCodeableConcept": {"text": med["medicine"]},
            "subject": {"reference": f"Patient/{patient_id}"},
            "dosageInstruction": [{
                "text": f"{med['dosage']} {med['frequency']}",
                "timing": {"repeat": {"frequency": med["frequency"]}},
                "doseAndRate": [{"doseQuantity": {"value": med["dosage"]}}]
            }],
            "authoredOn": med["start_date"],
            "reasonCode": [{"text": med.get("purpose", "")}],
            "requester": {"display": med.get("prescribing_doctor", "")}
        })
    
    return jsonify({
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(medication_requests),
        "entry": [{"resource": req} for req in medication_requests]
    }), 200


@app.route('/fhir/DiagnosticReport', methods=['GET'])
def get_lab_reports():
    """Get patient's lab reports"""
    patient_id = request.args.get('patient')
    
    if not patient_id:
        return jsonify({"error": "Missing patient parameter"}), 400
    
    patient = PATIENTS_DB.get(patient_id)
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    reports = []
    for lab in patient.get("lab_reports", []):
        reports.append({
            "resourceType": "DiagnosticReport",
            "id": lab["report_id"],
            "status": "final",
            "code": {"text": lab["test_name"]},
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": lab["date"],
            "issued": lab["date"],
            "performer": [{"display": lab.get("ordered_by", "")}],
            "result": lab["results"]
        })
    
    return jsonify({
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(reports),
        "entry": [{"resource": rep} for rep in reports]
    }), 200


@app.route('/fhir/Condition', methods=['GET'])
def get_diagnoses():
    """Get patient's diagnoses/conditions"""
    patient_id = request.args.get('patient')
    
    if not patient_id:
        return jsonify({"error": "Missing patient parameter"}), 400
    
    patient = PATIENTS_DB.get(patient_id)
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    conditions = []
    for diag in patient.get("diagnoses", []):
        conditions.append({
            "resourceType": "Condition",
            "clinicalStatus": {"coding": [{"code": diag["status"]}]},
            "code": {
                "coding": [{"system": "ICD-10", "code": diag.get("icd_code", "")}],
                "text": diag["condition"]
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "onsetDateTime": diag["diagnosed_date"],
            "severity": {"text": diag.get("severity", "")},
            "note": [{"text": diag.get("notes", "")}]
        })
    
    return jsonify({
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(conditions),
        "entry": [{"resource": cond} for cond in conditions]
    }), 200


@app.route('/fhir/Procedure', methods=['GET'])
def get_treatment_history():
    """Get patient's treatment/procedure history"""
    patient_id = request.args.get('patient')
    
    if not patient_id:
        return jsonify({"error": "Missing patient parameter"}), 400
    
    patient = PATIENTS_DB.get(patient_id)
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    procedures = []
    for treatment in patient.get("treatment_history", []):
        procedures.append({
            "resourceType": "Procedure",
            "status": "completed",
            "code": {"text": treatment["procedure"]},
            "subject": {"reference": f"Patient/{patient_id}"},
            "performedDateTime": treatment["date"],
            "performer": [{"actor": {"display": treatment.get("performed_by", "")}}],
            "location": {"display": treatment.get("facility", "")},
            "outcome": {"text": treatment.get("outcome", "")},
            "note": [{"text": treatment.get("notes", "")}]
        })
    
    return jsonify({
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(procedures),
        "entry": [{"resource": proc} for proc in procedures]
    }), 200


@app.route('/fhir/Encounter', methods=['GET'])
def get_visit_summaries():
    """Get patient's visit summaries/encounters"""
    patient_id = request.args.get('patient')
    
    if not patient_id:
        return jsonify({"error": "Missing patient parameter"}), 400
    
    patient = PATIENTS_DB.get(patient_id)
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    
    encounters = []
    for visit in patient.get("visit_summaries", []):
        encounters.append({
            "resourceType": "Encounter",
            "id": visit["visit_id"],
            "status": "finished",
            "class": {"code": "AMB", "display": "ambulatory"},
            "subject": {"reference": f"Patient/{patient_id}"},
            "period": {"start": visit["date"]},
            "participant": [{"individual": {"display": visit.get("doctor", "")}}],
            "location": [{"location": {"display": visit.get("facility", "")}}],
            "reasonCode": [{"text": visit.get("chief_complaint", "")}],
            "extension": [
                {"url": "vitals", "valueString": str(visit.get("vitals", {}))},
                {"url": "assessment", "valueString": visit.get("assessment", "")},
                {"url": "plan", "valueString": visit.get("plan", "")},
                {"url": "next_visit", "valueString": visit.get("next_visit", "")}
            ]
        })
    
    return jsonify({
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(encounters),
        "entry": [{"resource": enc} for enc in encounters]
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Enhanced Mock ABDM Server",
        "timestamp": datetime.now().isoformat(),
        "total_patients": len(PATIENTS_DB)
    }), 200


if __name__ == '__main__':
    print("=" * 70)
    print("🏥 Enhanced Mock ABDM Server Starting...")
    print("=" * 70)
    print(f"📍 Running on: http://localhost:8080")
    print(f"📊 Mock Patients: {len(PATIENTS_DB)}")
    print("\n📋 Available FHIR Endpoints:")
    print("  GET /fhir/Patient?identifier=<ABHA_ID>")
    print("  GET /fhir/MedicationRequest?patient=<ABHA_ID>")
    print("  GET /fhir/DiagnosticReport?patient=<ABHA_ID>")
    print("  GET /fhir/Condition?patient=<ABHA_ID>")
    print("  GET /fhir/Procedure?patient=<ABHA_ID>")
    print("  GET /fhir/Encounter?patient=<ABHA_ID>")
    print("  GET /health")
    print("\n💡 Sample ABHA IDs: ABHA001, ABHA002, ABHA003, ABHA004, ABHA005")
    print("=" * 70)
    app.run(host='0.0.0.0', port=8080, debug=True)
