import { useState } from 'react';
import { Search, FileText, AlertCircle } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import Button from '../components/Button';
import Card from '../components/Card';
import Modal from '../components/Modal';

export default function DoctorDashboard() {
    const [patientId, setPatientId] = useState('');
    const [patient, setPatient] = useState(null);
    const [medicine, setMedicine] = useState('');
    const [dosage, setDosage] = useState('');
    const [result, setResult] = useState(null);
    const [showOverrideModal, setShowOverrideModal] = useState(false);
    const [overrideReason, setOverrideReason] = useState('');
    const [analyzing, setAnalyzing] = useState(false);

    const handlePatientLookup = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('/api/login', { abha_id: patientId });
            setPatient(response.data.patient);
            toast.success('Patient loaded');
        } catch (error) {
            toast.error('Patient not found');
        }
    };

    const handleAnalyze = async (e) => {
        e.preventDefault();
        setAnalyzing(true);
        try {
            const medicationHistory = patient.medications
                .filter(m => m.status === 'active')
                .map(m => m.name);

            const response = await axios.post('/api/validate', {
                history: medicationHistory,
                new_medicine: medicine
            });
            setResult(response.data);
        } catch (error) {
            toast.error('Analysis failed');
        } finally {
            setAnalyzing(false);
        }
    };

    const handleOverride = async () => {
        try {
            await axios.post('/api/admin/override', {
                doctor_id: 'DR001',
                doctor_name: 'Dr. Smith',
                patient_id: patient.abha_id,
                drug: medicine,
                risk_level: result.risk_level,
                reason: overrideReason
            });
            toast.success('Override logged successfully');
            setShowOverrideModal(false);
            setOverrideReason('');
        } catch (error) {
            toast.error('Failed to log override');
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold mb-8">Doctor Dashboard</h1>

                <div className="grid lg:grid-cols-5 gap-6">
                    {/* Left Panel - Prescription Workspace */}
                    <div className="lg:col-span-3 space-y-6">
                        <Card>
                            <h2 className="text-xl font-bold mb-4">Patient Lookup</h2>
                            <form onSubmit={handlePatientLookup} className="flex gap-2">
                                <input
                                    type="text"
                                    value={patientId}
                                    onChange={(e) => setPatientId(e.target.value)}
                                    placeholder="Enter ABHA ID"
                                    className="flex-1 px-4 py-2 border rounded-soft"
                                    required
                                />
                                <Button type="submit">Load Patient</Button>
                            </form>
                        </Card>

                        {patient && (
                            <>
                                <Card>
                                    <h3 className="font-bold mb-2">{patient.name}</h3>
                                    <p className="text-sm text-slate-600">Age: {patient.age} | Gender: {patient.gender}</p>
                                    <div className="mt-4">
                                        <p className="text-sm font-medium">Current Medications:</p>
                                        <ul className="text-sm text-slate-600 mt-2 space-y-1">
                                            {patient.medications.filter(m => m.status === 'active').map((med, i) => (
                                                <li key={i}>• {med.name} - {med.dosage}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </Card>

                                <Card>
                                    <h2 className="text-xl font-bold mb-4">New Prescription</h2>
                                    <form onSubmit={handleAnalyze} className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-2">Medicine Name</label>
                                            <input
                                                type="text"
                                                value={medicine}
                                                onChange={(e) => setMedicine(e.target.value)}
                                                className="w-full px-4 py-2 border rounded-soft"
                                                required
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium mb-2">Dosage</label>
                                            <input
                                                type="text"
                                                value={dosage}
                                                onChange={(e) => setDosage(e.target.value)}
                                                placeholder="e.g., 500mg twice daily"
                                                className="w-full px-4 py-2 border rounded-soft"
                                            />
                                        </div>
                                        <Button type="submit" className="w-full" loading={analyzing}>
                                            Analyze Prescription
                                        </Button>
                                    </form>
                                </Card>
                            </>
                        )}
                    </div>

                    {/* Right Panel - AI Analysis */}
                    <div className="lg:col-span-2">
                        {result && (
                            <Card className={result.status === 'Risky' ? 'border-2 border-danger' : 'border-2 border-accent'}>
                                <h2 className="text-xl font-bold mb-4">AI Analysis</h2>

                                <div className={`p-4 rounded-soft mb-4 ${result.status === 'Risky' ? 'bg-danger/10' : 'bg-accent/10'}`}>
                                    <p className={`font-bold ${result.status === 'Risky' ? 'text-danger' : 'text-accent'}`}>
                                        {result.status === 'Risky' ? '⚠ Risk Detected' : '✓ Safe'}
                                    </p>
                                </div>

                                <div className="space-y-4">
                                    <div>
                                        <h3 className="font-semibold text-sm text-slate-600 mb-2">Clinical Explanation</h3>
                                        <p className="text-sm">{result.doctor_explanation}</p>
                                    </div>

                                    {result.mechanism && (
                                        <div>
                                            <h3 className="font-semibold text-sm text-slate-600 mb-2">Mechanism</h3>
                                            <p className="text-sm">{result.mechanism}</p>
                                        </div>
                                    )}

                                    <div>
                                        <h3 className="font-semibold text-sm text-slate-600 mb-2">Source</h3>
                                        <p className="text-xs text-slate-500">{result.source}</p>
                                    </div>

                                    {result.status === 'Risky' && (
                                        <Button
                                            variant="danger"
                                            className="w-full"
                                            onClick={() => setShowOverrideModal(true)}
                                        >
                                            Override Risk
                                        </Button>
                                    )}
                                </div>
                            </Card>
                        )}
                    </div>
                </div>

                {/* Override Modal */}
                <Modal isOpen={showOverrideModal} onClose={() => setShowOverrideModal(false)}>
                    <Modal.Header>Confirm Risk Override</Modal.Header>
                    <Modal.Body>
                        <p className="text-sm text-slate-600 mb-4">
                            You are about to override a risk alert. Please provide justification.
                        </p>
                        <textarea
                            value={overrideReason}
                            onChange={(e) => setOverrideReason(e.target.value)}
                            placeholder="Enter reason for override..."
                            className="w-full px-4 py-2 border rounded-soft h-32"
                            required
                        />
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="ghost" onClick={() => setShowOverrideModal(false)}>
                            Cancel
                        </Button>
                        <Button variant="danger" onClick={handleOverride}>
                            Confirm Override
                        </Button>
                    </Modal.Footer>
                </Modal>
            </div>
        </div>
    );
}
