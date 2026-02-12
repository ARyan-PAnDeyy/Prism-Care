"""
Data Preprocessing Pipeline for PrismCare
Cleans, standardizes, and validates medical data before AI analysis
"""

import re
from typing import Dict, List, Any
from datetime import datetime


class DataPreprocessor:
    """Handles all data cleaning and standardization"""
    
    # Medical term standardization mappings
    MEDICAL_TERM_MAPPINGS = {
        # Diabetes variations
        "diabetes": ["diabetes mellitus", "dm", "diabetic", "type 2 diabetes", "type 1 diabetes"],
        "hypertension": ["high blood pressure", "htn", "high bp", "elevated bp"],
        "hyperlipidemia": ["high cholesterol", "dyslipidemia", "elevated cholesterol"],
        
        # Common medications
        "metformin": ["glucophage", "fortamet"],
        "aspirin": ["acetylsalicylic acid", "asa"],
        "ibuprofen": ["advil", "motrin", "brufen"],
        "warfarin": ["coumadin"],
        "lisinopril": ["prinivil", "zestril"],
        "atorvastatin": ["lipitor"],
    }
    
    # Unit conversion factors
    UNIT_CONVERSIONS = {
        "glucose": {
            "mg/dL_to_mmol/L": 0.0555,
            "mmol/L_to_mg/dL": 18.0182
        },
        "cholesterol": {
            "mg/dL_to_mmol/L": 0.0259,
            "mmol/L_to_mg/dL": 38.67
        }
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def clean_patient_data(self, patient_data: Dict) -> Dict:
        """
        Main cleaning function - removes duplicates, handles missing values
        
        Args:
            patient_data: Raw patient data from ABDM
            
        Returns:
            Cleaned patient data
        """
        cleaned_data = patient_data.copy()
        
        # Remove duplicate medications
        if "medications" in cleaned_data:
            cleaned_data["medications"] = self._remove_duplicate_medications(
                cleaned_data["medications"]
            )
        
        # Remove duplicate lab reports
        if "lab_reports" in cleaned_data:
            cleaned_data["lab_reports"] = self._remove_duplicate_labs(
                cleaned_data["lab_reports"]
            )
        
        # Handle missing values
        cleaned_data = self._handle_missing_values(cleaned_data)
        
        # Validate data quality
        self._validate_data_quality(cleaned_data)
        
        return cleaned_data
    
    def _remove_duplicate_medications(self, medications: List[Dict]) -> List[Dict]:
        """Remove duplicate medication entries"""
        seen = set()
        unique_meds = []
        
        for med in medications:
            key = (med.get("medicine", "").lower(), med.get("dosage", ""), med.get("status", ""))
            if key not in seen:
                seen.add(key)
                unique_meds.append(med)
            else:
                self.warnings.append(f"Duplicate medication removed: {med.get('medicine')}")
        
        return unique_meds
    
    def _remove_duplicate_labs(self, lab_reports: List[Dict]) -> List[Dict]:
        """Remove duplicate lab reports, keep most recent"""
        seen = {}
        
        for lab in lab_reports:
            test_name = lab.get("test_name", "")
            date = lab.get("date", "")
            
            if test_name not in seen:
                seen[test_name] = lab
            else:
                # Keep the more recent one
                if date > seen[test_name].get("date", ""):
                    self.warnings.append(f"Duplicate lab replaced with newer: {test_name}")
                    seen[test_name] = lab
        
        return list(seen.values())
    
    def _handle_missing_values(self, data: Dict) -> Dict:
        """Handle missing or incomplete values"""
        # Set defaults for missing demographics
        if "age" not in data or data["age"] is None:
            self.errors.append("Missing age - cannot proceed")
        
        if "gender" not in data or data["gender"] is None:
            data["gender"] = "Unknown"
            self.warnings.append("Gender not specified, set to Unknown")
        
        # Ensure required fields exist
        data.setdefault("medications", [])
        data.setdefault("lab_reports", [])
        data.setdefault("diagnoses", [])
        data.setdefault("visit_summaries", [])
        data.setdefault("treatment_history", [])
        
        return data
    
    def standardize_units(self, lab_results: Dict, test_type: str) -> Dict:
        """
        Normalize measurement units to standard format
        
        Args:
            lab_results: Lab test results
            test_type: Type of test (glucose, cholesterol, etc.)
            
        Returns:
            Standardized results
        """
        standardized = lab_results.copy()
        
        # Example: Convert glucose from mmol/L to mg/dL if needed
        if test_type == "glucose":
            for key, value in lab_results.items():
                if isinstance(value, dict) and "unit" in value:
                    if value["unit"] == "mmol/L":
                        # Convert to mg/dL
                        original_value = value["value"]
                        value["value"] = round(original_value * 18.0182, 1)
                        value["unit"] = "mg/dL"
                        value["original_value"] = original_value
                        value["original_unit"] = "mmol/L"
        
        return standardized
    
    def normalize_medical_terms(self, text: str) -> str:
        """
        Map medical terms to standard vocabularies
        
        Args:
            text: Medical term or phrase
            
        Returns:
            Standardized term
        """
        text_lower = text.lower().strip()
        
        # Check against mappings
        for standard_term, variations in self.MEDICAL_TERM_MAPPINGS.items():
            if text_lower == standard_term or text_lower in variations:
                return standard_term
        
        return text  # Return original if no mapping found
    
    def extract_clinical_text(self, unstructured_text: str) -> Dict:
        """
        Parse unstructured clinical notes
        
        Args:
            unstructured_text: Free-text clinical notes
            
        Returns:
            Structured data extracted from text
        """
        extracted = {
            "medications_mentioned": [],
            "conditions_mentioned": [],
            "symptoms": [],
            "vital_signs": {}
        }
        
        # Extract blood pressure
        bp_pattern = r'(\d{2,3})/(\d{2,3})\s*mmHg'
        bp_match = re.search(bp_pattern, unstructured_text)
        if bp_match:
            extracted["vital_signs"]["bp"] = f"{bp_match.group(1)}/{bp_match.group(2)} mmHg"
        
        # Extract pulse
        pulse_pattern = r'(\d{2,3})\s*bpm'
        pulse_match = re.search(pulse_pattern, unstructured_text)
        if pulse_match:
            extracted["vital_signs"]["pulse"] = f"{pulse_match.group(1)} bpm"
        
        # Extract medications (simple pattern matching)
        for standard_term, variations in self.MEDICAL_TERM_MAPPINGS.items():
            for variation in variations + [standard_term]:
                if variation in unstructured_text.lower():
                    if standard_term not in ["diabetes", "hypertension", "hyperlipidemia"]:
                        extracted["medications_mentioned"].append(standard_term)
                    else:
                        extracted["conditions_mentioned"].append(standard_term)
        
        return extracted
    
    def _validate_data_quality(self, data: Dict) -> bool:
        """
        Check for inconsistencies and data quality issues
        
        Args:
            data: Patient data to validate
            
        Returns:
            True if valid, False otherwise
        """
        is_valid = True
        
        # Check age is reasonable
        age = data.get("age", 0)
        if age < 0 or age > 120:
            self.errors.append(f"Invalid age: {age}")
            is_valid = False
        
        # Check medications have required fields
        for med in data.get("medications", []):
            if not med.get("medicine"):
                self.errors.append("Medication missing name")
                is_valid = False
            if not med.get("dosage"):
                self.warnings.append(f"Medication {med.get('medicine')} missing dosage")
        
        # Check lab results are within plausible ranges
        for lab in data.get("lab_reports", []):
            results = lab.get("results", {})
            for test, values in results.items():
                if isinstance(values, dict):
                    value = values.get("value")
                    if value is not None and value < 0:
                        self.errors.append(f"Negative lab value for {test}: {value}")
                        is_valid = False
        
        return is_valid
    
    def get_preprocessing_report(self) -> Dict:
        """Get summary of preprocessing actions"""
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }


# Utility functions for easy access
def preprocess_patient_data(patient_data: Dict) -> tuple:
    """
    Convenience function to preprocess patient data
    
    Returns:
        (cleaned_data, preprocessing_report)
    """
    preprocessor = DataPreprocessor()
    cleaned_data = preprocessor.clean_patient_data(patient_data)
    report = preprocessor.get_preprocessing_report()
    
    return cleaned_data, report


if __name__ == "__main__":
    # Test the preprocessor
    print("=" * 60)
    print("🧹 Data Preprocessor Test")
    print("=" * 60)
    
    # Test data with duplicates and issues
    test_data = {
        "id": "TEST001",
        "name": "Test Patient",
        "age": 45,
        "medications": [
            {"medicine": "Metformin", "dosage": "500mg", "status": "active"},
            {"medicine": "metformin", "dosage": "500mg", "status": "active"},  # Duplicate
        ],
        "lab_reports": [
            {"test_name": "HbA1c", "date": "2024-01-01", "results": {}},
            {"test_name": "HbA1c", "date": "2024-02-01", "results": {}},  # Duplicate, newer
        ]
    }
    
    cleaned, report = preprocess_patient_data(test_data)
    
    print(f"\n✅ Cleaned medications: {len(cleaned['medications'])}")
    print(f"✅ Cleaned lab reports: {len(cleaned['lab_reports'])}")
    print(f"\n⚠️  Warnings: {report['warning_count']}")
    for warning in report['warnings']:
        print(f"   - {warning}")
    print(f"\n❌ Errors: {report['error_count']}")
    for error in report['errors']:
        print(f"   - {error}")
    
    print("\n" + "=" * 60)
