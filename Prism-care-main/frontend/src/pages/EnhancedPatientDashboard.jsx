import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
    Search, CheckCircle2, AlertTriangle, Loader2, Pill, Calendar,
    Activity, TrendingUp, FileText, AlertCircle, Heart, Beaker
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Button from '../components/Button';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';

export default function EnhancedPatientDashboard() {
    const [abhaId, setAbhaId] = useState('');
    const [patient, setPatient] = useState(null);
    const [medicine, setMedicine] = useState('');
    const [loading, setLoading] = useState(false);
    const [checking, setChecking] = useState(false);
    const [result, setResult] = useState(null);
    const [aiSummary, setAiSummary] = useState(null);
    const [testRecommendations, setTestRecommendations] = useState([]);
    const [activeTab, setActiveTab] = useState('overview');

    const handleLogin = async (e) => {
        e.preventDefault();
        if (!abhaId.trim()) {
            toast.error('Please enter ABHA ID');
            return;
        }

        setLoading(true);
        setResult(null);

        try {
            const response = await axios.get(`http://localhost:5000/api/patient/${abhaId}`);
            setPatient(response.data);
            toast.success(`Welcome, ${response.data.name}!`);
            
            // Fetch AI summary
            fetchAISummary(abhaId);
            
            // Fetch test recommendations
            fetchTestRecommendations(abhaId);
        } catch (error) {
            if (error.response?.status === 404) {
                toast.error('Patient not found. Please check your ABHA ID.');
            } else if (error.response?.status === 503) {
                toast.error('Cannot connect to ABDM server. Please ensure it is running.');
            } else {
                toast.error('Failed to fetch patient data');
            }
            console.error('Login error:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchAISummary = async (id) => {
        try {
            const response = await axios.get(`http://localhost:5000/api/patient/${id}/summary`);
            setAiSummary(response.data);
        } catch (error) {
            console.error('Failed to fetch AI summary:', error);
        }
    };

    const fetchTestRecommendations = async (id) => {
        try {
            const response = await axios.get(`http://localhost:5000/api/patient/${id}/test-recommendations`);
            setTestRecommendations(response.data.recommendations || []);
        } catch (error) {
            console.error('Failed to fetch test recommendations:', error);
        }
    };

    const handleCheckSafety = async (e) => {
        e.preventDefault();
        if (!medicine.trim()) {
            toast.error('Please enter a medicine name');
            return;
        }

        setChecking(true);
        setResult(null);

        try {
            const response = await axios.post('http://localhost:5000/api/check-safety', {
                abha_id: patient.id,
                medicine: medicine
            });

            setResult(response.data);
            
            if (response.data.status === 'Safe') {
                toast.success('Medicine appears safe!');
            } else {
                toast.error('Potential interaction detected!');
            }
        } catch (error) {
            toast.error('Failed to check medicine safety');
            console.error('Safety check error:', error);
        } finally {
            setChecking(false);
        }
    };

    const handleLogout = () => {
        setPatient(null);
        setAbhaId('');
        setMedicine('');
        setResult(null);
        setAiSummary(null);
        setTestRecommendations([]);
        setActiveTab('overview');
        toast.success('Logged out successfully');
    };

    // Prepare chart data for lab trends
    const getLabTrendData = () => {
        if (!patient?.lab_reports) return [];
        
        // Example: HbA1c trend (simplified)
        const hba1cData = patient.lab_reports
            .filter(lab => lab.resource?.code?.text?.includes('HbA1c'))
            .map(lab => ({
                date: lab.resource?.effectiveDateTime || 'N/A',
                value: lab.resource?.result?.hba1c?.value || 0
            }));
        
        return hba1cData;
    };

    if (!patient) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="max-w-md mx-auto"
                >
                    <Card className="p-8">
                        <div className="text-center mb-8">
                            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Heart className="w-8 h-8 text-white" />
                            </div>
                            <h1 className="text-3xl font-bold text-gray-900 mb-2">Patient Portal</h1>
                            <p className="text-gray-600">Enter your ABHA ID to access your health records</p>
                        </div>

                        <form onSubmit={handleLogin} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    ABHA ID
                                </label>
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type="text"
                                        value={abhaId}
                                        onChange={(e) => setAbhaId(e.target.value)}
                                        placeholder="Enter ABHA ID (e.g., ABHA001)"
                                        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        disabled={loading}
                                    />
                                </div>
                            </div>

                            <Button
                                type="submit"
                                className="w-full"
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                        Logging in...
                                    </>
                                ) : (
                                    'Login'
                                )}
                            </Button>
                        </form>

                        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                            <p className="text-sm text-blue-800 font-medium mb-2">Demo ABHA IDs:</p>
                            <div className="space-y-1 text-sm text-blue-700">
                                <p>• ABHA001 - Rajesh Kumar (Diabetes, AFib)</p>
                                <p>• ABHA002 - Priya Sharma (Hypertension)</p>
                                <p>• ABHA003 - Mohammed Ali (Back Pain)</p>
                                <p>• ABHA004 - Sunita Devi (Multiple conditions)</p>
                                <p>• ABHA005 - Amit Patel (Allergies)</p>
                            </div>
                        </div>
                    </Card>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Welcome, {patient.name}</h1>
                            <p className="text-gray-600 mt-1">
                                {patient.age} years • {patient.gender} • ABHA ID: {patient.id}
                            </p>
                        </div>
                        <Button onClick={handleLogout} variant="outline">
                            Logout
                        </Button>
                    </div>
                </motion.div>

                {/* Tabs */}
                <div className="mb-6 border-b border-gray-200">
                    <div className="flex space-x-8">
                        {['overview', 'medications', 'labs', 'check-medicine'].map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`pb-4 px-2 font-medium transition-colors ${
                                    activeTab === tab
                                        ? 'border-b-2 border-blue-600 text-blue-600'
                                        : 'text-gray-500 hover:text-gray-700'
                                }`}
                            >
                                {tab.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* AI Summary */}
                        {aiSummary && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="lg:col-span-2"
                            >
                                <Card className="p-6">
                                    <div className="flex items-center mb-4">
                                        <Activity className="w-6 h-6 text-purple-600 mr-2" />
                                        <h2 className="text-xl font-bold text-gray-900">AI Health Summary</h2>
                                    </div>
                                    <div className="prose max-w-none">
                                        <p className="text-gray-700 whitespace-pre-line">{aiSummary.summary_text}</p>
                                    </div>
                                    
                                    {aiSummary.key_conditions && aiSummary.key_conditions.length > 0 && (
                                        <div className="mt-4">
                                            <h3 className="font-semibold text-gray-900 mb-2">Active Conditions:</h3>
                                            <div className="flex flex-wrap gap-2">
                                                {aiSummary.key_conditions.map((condition, idx) => (
                                                    <span key={idx} className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm">
                                                        {condition}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {aiSummary.recent_trends && aiSummary.recent_trends.length > 0 && (
                                        <div className="mt-4">
                                            <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                                                <TrendingUp className="w-4 h-4 mr-1" />
                                                Recent Trends:
                                            </h3>
                                            <ul className="space-y-1">
                                                {aiSummary.recent_trends.map((trend, idx) => (
                                                    <li key={idx} className="text-sm text-gray-700">• {trend}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </Card>
                            </motion.div>
                        )}

                        {/* Test Recommendations */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                        >
                            <Card className="p-6">
                                <div className="flex items-center mb-4">
                                    <Beaker className="w-6 h-6 text-blue-600 mr-2" />
                                    <h2 className="text-xl font-bold text-gray-900">Recommended Tests</h2>
                                </div>
                                {testRecommendations.length > 0 ? (
                                    <div className="space-y-3">
                                        {testRecommendations.map((test, idx) => (
                                            <div key={idx} className="p-3 bg-blue-50 rounded-lg">
                                                <div className="flex items-start justify-between">
                                                    <div className="flex-1">
                                                        <h3 className="font-semibold text-gray-900 text-sm">{test.test}</h3>
                                                        <p className="text-xs text-gray-600 mt-1">{test.rationale}</p>
                                                        <p className="text-xs text-blue-600 mt-1">Frequency: {test.frequency}</p>
                                                    </div>
                                                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                                                        test.priority === 'Critical' ? 'bg-red-100 text-red-800' :
                                                        test.priority === 'High' ? 'bg-orange-100 text-orange-800' :
                                                        'bg-green-100 text-green-800'
                                                    }`}>
                                                        {test.priority}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-gray-500 text-sm">No specific test recommendations at this time.</p>
                                )}
                            </Card>
                        </motion.div>
                    </div>
                )}

                {/* Medications Tab */}
                {activeTab === 'medications' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        <Card className="p-6">
                            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                                <Pill className="w-6 h-6 mr-2 text-blue-600" />
                                Current Medications
                            </h2>
                            {patient.medications && patient.medications.length > 0 ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {patient.medications.map((med, idx) => {
                                        const resource = med.resource || {};
                                        return (
                                            <div key={idx} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                                                <div className="flex items-start justify-between">
                                                    <div>
                                                        <h3 className="font-semibold text-gray-900">
                                                            {resource.medicationCodeableConcept?.text || 'Unknown'}
                                                        </h3>
                                                        <p className="text-sm text-gray-600 mt-1">
                                                            {resource.dosageInstruction?.[0]?.text || 'Dosage not specified'}
                                                        </p>
                                                        {resource.reasonCode?.[0]?.text && (
                                                            <p className="text-xs text-blue-600 mt-2">
                                                                Purpose: {resource.reasonCode[0].text}
                                                            </p>
                                                        )}
                                                    </div>
                                                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                                                        resource.status === 'active' 
                                                            ? 'bg-green-100 text-green-800' 
                                                            : 'bg-gray-100 text-gray-800'
                                                    }`}>
                                                        {resource.status || 'Unknown'}
                                                    </span>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <p className="text-gray-500">No medications on record.</p>
                            )}
                        </Card>
                    </motion.div>
                )}

                {/* Labs Tab */}
                {activeTab === 'labs' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        <Card className="p-6">
                            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                                <FileText className="w-6 h-6 mr-2 text-purple-600" />
                                Lab Reports
                            </h2>
                            {patient.lab_reports && patient.lab_reports.length > 0 ? (
                                <div className="space-y-4">
                                    {patient.lab_reports.map((lab, idx) => {
                                        const resource = lab.resource || {};
                                        return (
                                            <div key={idx} className="p-4 border border-gray-200 rounded-lg">
                                                <div className="flex justify-between items-start mb-3">
                                                    <div>
                                                        <h3 className="font-semibold text-gray-900">{resource.code?.text || 'Lab Test'}</h3>
                                                        <p className="text-sm text-gray-500">
                                                            {resource.effectiveDateTime || 'Date not specified'}
                                                        </p>
                                                    </div>
                                                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                                                        {resource.status || 'Final'}
                                                    </span>
                                                </div>
                                                {resource.result && typeof resource.result === 'object' && (
                                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-3">
                                                        {Object.entries(resource.result).map(([key, value]) => {
                                                            if (typeof value === 'object' && value !== null) {
                                                                return (
                                                                    <div key={key} className="p-2 bg-gray-50 rounded">
                                                                        <p className="text-xs text-gray-600 uppercase">{key.replace(/_/g, ' ')}</p>
                                                                        <p className="font-semibold text-gray-900">
                                                                            {value.value} {value.unit}
                                                                        </p>
                                                                        {value.status && (
                                                                            <span className={`text-xs ${
                                                                                value.status === 'normal' ? 'text-green-600' :
                                                                                value.status === 'high' || value.status === 'elevated' ? 'text-red-600' :
                                                                                'text-yellow-600'
                                                                            }`}>
                                                                                {value.status}
                                                                            </span>
                                                                        )}
                                                                    </div>
                                                                );
                                                            }
                                                            return null;
                                                        })}
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <p className="text-gray-500">No lab reports available.</p>
                            )}
                        </Card>
                    </motion.div>
                )}

                {/* Check Medicine Tab */}
                {activeTab === 'check-medicine' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="max-w-3xl mx-auto"
                    >
                        <Card className="p-6">
                            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                                <AlertCircle className="w-6 h-6 mr-2 text-blue-600" />
                                Check Medicine Safety
                            </h2>

                            <form onSubmit={handleCheckSafety} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Medicine Name
                                    </label>
                                    <input
                                        type="text"
                                        value={medicine}
                                        onChange={(e) => setMedicine(e.target.value)}
                                        placeholder="Enter medicine name (e.g., Aspirin)"
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        disabled={checking}
                                    />
                                </div>

                                <Button
                                    type="submit"
                                    className="w-full"
                                    disabled={checking}
                                >
                                    {checking ? (
                                        <>
                                            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                            Checking Safety...
                                        </>
                                    ) : (
                                        'Check Safety'
                                    )}
                                </Button>
                            </form>

                            {result && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mt-6"
                                >
                                    <div className={`p-6 rounded-lg ${
                                        result.status === 'Safe' 
                                            ? 'bg-green-50 border-2 border-green-200' 
                                            : 'bg-red-50 border-2 border-red-200'
                                    }`}>
                                        <div className="flex items-start">
                                            {result.status === 'Safe' ? (
                                                <CheckCircle2 className="w-8 h-8 text-green-600 mr-3 flex-shrink-0" />
                                            ) : (
                                                <AlertTriangle className="w-8 h-8 text-red-600 mr-3 flex-shrink-0" />
                                            )}
                                            <div className="flex-1">
                                                <h3 className={`text-xl font-bold mb-2 ${
                                                    result.status === 'Safe' ? 'text-green-900' : 'text-red-900'
                                                }`}>
                                                    {result.status === 'Safe' ? 'Medicine Appears Safe' : 'Potential Interaction Detected'}
                                                </h3>
                                                
                                                {result.risk_level && (
                                                    <div className="mb-3">
                                                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                                                            result.risk_level === 'Critical' ? 'bg-red-600 text-white' :
                                                            result.risk_level === 'High' ? 'bg-orange-500 text-white' :
                                                            'bg-yellow-500 text-white'
                                                        }`}>
                                                            Risk Level: {result.risk_level}
                                                        </span>
                                                    </div>
                                                )}

                                                <p className={`mb-4 ${
                                                    result.status === 'Safe' ? 'text-green-800' : 'text-red-800'
                                                }`}>
                                                    {result.patient_explanation}
                                                </p>

                                                {result.recommendation && (
                                                    <div className="mt-4 p-3 bg-white rounded border border-gray-200">
                                                        <h4 className="font-semibold text-gray-900 mb-1">Recommendation:</h4>
                                                        <p className="text-sm text-gray-700">{result.recommendation}</p>
                                                    </div>
                                                )}

                                                {result.source && (
                                                    <p className="text-xs text-gray-600 mt-3">
                                                        Source: {result.source}
                                                    </p>
                                                )}

                                                <div className="mt-4 p-3 bg-blue-50 rounded">
                                                    <p className="text-sm text-blue-900">
                                                        <strong>Important:</strong> This is an AI-powered analysis. Always consult your healthcare provider before making any changes to your medications.
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </Card>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
