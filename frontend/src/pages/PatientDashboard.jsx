import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, CheckCircle2, AlertTriangle, Loader2, Pill, Calendar } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import Button from '../components/Button';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';

export default function PatientDashboard() {
    const [abhaId, setAbhaId] = useState('');
    const [patient, setPatient] = useState(null);
    const [medicine, setMedicine] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await axios.post('/api/login', { abha_id: abhaId });
            setPatient(response.data.patient);
            toast.success(`Welcome, ${response.data.patient.name}!`);
        } catch (error) {
            toast.error(error.response?.data?.error || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    const handleCheckSafety = async (e) => {
        e.preventDefault();
        setAnalyzing(true);
        setResult(null);

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
            toast.error('Analysis failed. Please try again.');
        } finally {
            setAnalyzing(false);
        }
    };

    if (!patient) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-primary/5 to-secondary/5 flex items-center justify-center p-4">
                <Card className="max-w-md w-full">
                    <h1 className="text-3xl font-bold text-center mb-6">Patient Login</h1>
                    <form onSubmit={handleLogin} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-2">
                                ABHA ID
                            </label>
                            <input
                                type="text"
                                value={abhaId}
                                onChange={(e) => setAbhaId(e.target.value)}
                                placeholder="Enter your ABHA ID (e.g., ABHA001)"
                                className="w-full px-4 py-2 border border-slate-300 rounded-soft focus:ring-2 focus:ring-primary focus:border-transparent"
                                required
                            />
                            <p className="text-sm text-slate-500 mt-1">Try: ABHA001, ABHA002, or ABHA003</p>
                        </div>
                        <Button type="submit" className="w-full" loading={loading}>
                            Login
                        </Button>
                    </form>
                </Card>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 py-8">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-slate-900">Hello, {patient.name}!</h1>
                    <p className="text-slate-600">ABHA ID: {patient.abha_id}</p>
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    {/* Main Section */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Medicine Check */}
                        <Card>
                            <h2 className="text-2xl font-bold mb-4">Check Medicine Safety</h2>
                            <form onSubmit={handleCheckSafety} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">
                                        Medicine Name
                                    </label>
                                    <div className="relative">
                                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
                                        <input
                                            type="text"
                                            value={medicine}
                                            onChange={(e) => setMedicine(e.target.value)}
                                            placeholder="Enter medicine name (e.g., Aspirin)"
                                            className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-soft focus:ring-2 focus:ring-primary focus:border-transparent text-lg"
                                            required
                                        />
                                    </div>
                                </div>
                                <Button type="submit" size="lg" className="w-full" loading={analyzing}>
                                    Check Safety
                                </Button>
                            </form>
                        </Card>

                        {/* Result Card */}
                        {analyzing && (
                            <Card className="text-center py-12">
                                <LoadingSpinner size="lg" />
                                <p className="mt-4 text-slate-600">Analyzing medication safety...</p>
                            </Card>
                        )}

                        {result && !analyzing && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ duration: 0.3 }}
                            >
                                {result.status === 'Safe' ? (
                                    <Card variant="default" className="border-4 border-accent">
                                        <div className="text-center py-8">
                                            <motion.div
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                transition={{ type: "spring", duration: 0.5 }}
                                            >
                                                <CheckCircle2 className="h-24 w-24 text-accent mx-auto mb-4" />
                                            </motion.div>
                                            <h3 className="text-3xl font-bold text-accent mb-4">✓ This medicine is safe for you</h3>
                                            <p className="text-lg text-slate-700 mb-4">{result.patient_explanation}</p>
                                            <div className="inline-block bg-accent/10 px-4 py-2 rounded-full">
                                                <span className="text-sm font-medium text-accent">Confidence: {(result.confidence * 100).toFixed(0)}%</span>
                                            </div>
                                        </div>
                                    </Card>
                                ) : (
                                    <Card variant="default" className="border-4 border-danger">
                                        <div className="text-center py-8">
                                            <motion.div
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1, rotate: [0, -10, 10, -10, 0] }}
                                                transition={{ duration: 0.5 }}
                                            >
                                                <AlertTriangle className="h-24 w-24 text-danger mx-auto mb-4" />
                                            </motion.div>
                                            <h3 className="text-3xl font-bold text-danger mb-4">⚠ Caution: Potential Interaction Detected</h3>
                                            <p className="text-lg text-slate-700 mb-6">{result.patient_explanation}</p>
                                            <div className="bg-danger/10 p-4 rounded-soft mb-4">
                                                <p className="font-semibold text-danger">⚠️ Please consult your doctor before taking this medicine</p>
                                            </div>
                                            <div className="inline-block bg-danger/10 px-4 py-2 rounded-full">
                                                <span className="text-sm font-medium text-danger">Risk Level: {result.risk_level}</span>
                                            </div>
                                        </div>
                                    </Card>
                                )}
                            </motion.div>
                        )}
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        {/* Current Medications */}
                        <Card>
                            <h3 className="text-xl font-bold mb-4 flex items-center">
                                <Pill className="h-5 w-5 mr-2 text-primary" />
                                Current Medications
                            </h3>
                            <div className="space-y-3">
                                {patient.medications.filter(m => m.status === 'active').map((med, index) => (
                                    <div key={index} className="p-3 bg-slate-50 rounded-soft">
                                        <div className="font-semibold text-slate-900">{med.name}</div>
                                        <div className="text-sm text-slate-600">{med.dosage}</div>
                                        <div className="text-xs text-slate-500 mt-1 flex items-center">
                                            <Calendar className="h-3 w-3 mr-1" />
                                            Since {med.start_date}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Card>

                        {/* Quick Actions */}
                        <Card>
                            <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
                            <div className="space-y-2">
                                <Button variant="outline" className="w-full justify-start">
                                    View Full History
                                </Button>
                                <Button variant="outline" className="w-full justify-start">
                                    Download Health Report
                                </Button>
                                <Button variant="ghost" className="w-full justify-start text-danger">
                                    Logout
                                </Button>
                            </div>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
