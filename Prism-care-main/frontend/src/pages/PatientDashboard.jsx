import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search, CheckCircle2, AlertTriangle, Loader2, Pill, Calendar,
    Activity, TrendingUp, FileText, AlertCircle, Heart, Beaker,
    Upload, X, Plus, ArrowRight, Shield, Stethoscope, Droplet, Brain,
    MessageSquare, Send, User, Bot, Paperclip
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import Button from '../components/Button';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';

export default function PatientDashboard() {
    const [abhaId, setAbhaId] = useState('');
    const [patient, setPatient] = useState(null);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');

    // Chat State
    const [chatHistory, setChatHistory] = useState([]);
    const [chatInput, setChatInput] = useState('');
    const [chatLoading, setChatLoading] = useState(false);
    const chatEndRef = useRef(null);

    // Lab Upload State
    const [showLabUpload, setShowLabUpload] = useState(false);
    const [labFile, setLabFile] = useState(null);
    const [labTestName, setLabTestName] = useState('');
    const [analyzingLab, setAnalyzingLab] = useState(false);
    const [labAnalysis, setLabAnalysis] = useState(null);

    // Safety Check State
    const [medicineCheck, setMedicineCheck] = useState('');
    const [safetyResult, setSafetyResult] = useState(null);
    const [checkingSafety, setCheckingSafety] = useState(false);

    // Data States
    const [aiSummary, setAiSummary] = useState(null);
    const [testRecommendations, setTestRecommendations] = useState([]);

    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [chatHistory]);

    const handleLogin = async (e) => {
        e.preventDefault();
        if (!abhaId.trim()) {
            toast.error('Please enter ABHA ID');
            return;
        }

        setLoading(true);
        try {
            const response = await axios.get(`http://localhost:5000/api/patient/${abhaId}`);
            setPatient(response.data);
            toast.success(`Welcome, ${response.data.name}!`);

            // Initialize fetchers
            fetchAISummary(abhaId);
            fetchTestRecommendations(abhaId);

            // Welcome message for chat
            setChatHistory([{
                sender: 'assistant',
                text: `Hello ${response.data.name}! I'm your PrismCare medical assistant. I have access to your health history. How can I help you today?`
            }]);

        } catch (error) {
            console.error(error);
            toast.error(error.response?.data?.error || 'Failed to login');
        } finally {
            setLoading(false);
        }
    };

    const fetchAISummary = async (id) => {
        try {
            const res = await axios.get(`http://localhost:5000/api/patient/${id}/summary`);
            setAiSummary(res.data);
        } catch (e) {
            console.error("Summary fetch failed", e);
        }
    };

    const fetchTestRecommendations = async (id) => {
        try {
            const res = await axios.get(`http://localhost:5000/api/patient/${id}/test-recommendations`);
            setTestRecommendations(res.data.recommendations || []);
        } catch (e) {
            console.error("Recommendations fetch failed", e);
        }
    };

    const handleChatSubmit = async (e) => {
        e.preventDefault();
        if (!chatInput.trim()) return;

        const userMsg = chatInput;
        setChatInput('');
        setChatHistory(prev => [...prev, { sender: 'user', text: userMsg }]);
        setChatLoading(true);

        try {
            const response = await axios.post('http://localhost:5000/api/chat', {
                abha_id: patient.id,
                query: userMsg,
                history: chatHistory
            });

            setChatHistory(prev => [...prev, { sender: 'assistant', text: response.data.response }]);
        } catch (error) {
            toast.error('Failed to get response');
            setChatHistory(prev => [...prev, { sender: 'assistant', text: "I'm sorry, I encountered an error. Please try again." }]);
        } finally {
            setChatLoading(false);
        }
    };

    const handleLabUpload = async (e) => {
        e.preventDefault();
        if (!labFile && !labTestName) {
            toast.error('Please provide a file or test name');
            return;
        }

        setAnalyzingLab(true);
        const formData = new FormData();
        if (labFile) formData.append('file', labFile);
        formData.append('test_name', labTestName);
        formData.append('patient_age', patient.age);
        formData.append('patient_gender', patient.gender);

        try {
            const response = await axios.post(
                `http://localhost:5000/api/patient/${patient.id}/upload-lab`,
                formData,
                { headers: { 'Content-Type': 'multipart/form-data' } }
            );

            setLabAnalysis(response.data);
            toast.success('Analysis Complete!');
            setShowLabUpload(false);
            setActiveTab('lab-analysis');
            setLabFile(null);
            setLabTestName('');
        } catch (error) {
            toast.error('Failed to analyze report');
            console.error(error);
        } finally {
            setAnalyzingLab(false);
        }
    };

    const handleSafetyCheck = async (e) => {
        e.preventDefault();
        if (!medicineCheck) return;

        setCheckingSafety(true);
        try {
            const response = await axios.post('http://localhost:5000/api/check-safety', {
                abha_id: patient.id,
                medicine: medicineCheck
            });
            setSafetyResult(response.data);
        } catch (error) {
            toast.error('Safety check failed');
        } finally {
            setCheckingSafety(false);
        }
    };

    const handleLogout = () => {
        setPatient(null);
        setAbhaId('');
        setChatHistory([]);
        setActiveTab('overview');
    };

    if (!patient) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 py-12 px-4 flex items-center justify-center">
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-md w-full">
                    <Card className="p-8 border-2 border-emerald-100 shadow-xl">
                        <div className="text-center mb-8">
                            <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                                <Stethoscope className="w-10 h-10 text-white" />
                            </div>
                            <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent mb-2">
                                PrismCare Portal
                            </h1>
                            <p className="text-gray-600">Secure Patient Access</p>
                        </div>
                        <form onSubmit={handleLogin} className="space-y-4">
                            <div>
                                <label className="block text-sm font-semibold text-emerald-700 mb-2">ABHA Health ID</label>
                                <div className="relative">
                                    <Shield className="absolute left-3 top-1/2 -translate-y-1/2 text-emerald-500 w-5 h-5" />
                                    <input
                                        type="text"
                                        value={abhaId}
                                        onChange={(e) => setAbhaId(e.target.value)}
                                        placeholder="e.g., ABHA001"
                                        className="w-full pl-10 pr-4 py-3 border-2 border-emerald-200 rounded-lg focus:ring-2 focus:ring-emerald-500"
                                        disabled={loading}
                                    />
                                </div>
                            </div>
                            <Button type="submit" disabled={loading} className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 text-white py-3">
                                {loading ? <Loader2 className="animate-spin mx-auto" /> : 'Access Records'}
                            </Button>
                        </form>
                    </Card>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 pb-12">
            {/* Header */}
            <header className="bg-white shadow-sm border-b border-emerald-100 sticky top-0 z-30">
                <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
                            <User className="w-6 h-6 text-emerald-600" />
                        </div>
                        <div>
                            <h1 className="font-bold text-gray-900">{patient.name}</h1>
                            <p className="text-xs text-gray-500">ABHA: {patient.id} • {patient.age}yrs • {patient.gender}</p>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" onClick={handleLogout} className="text-red-600 border-red-200 hover:bg-red-50">
                            Logout
                        </Button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-8">
                {/* Tabs */}
                <div className="flex overflow-x-auto gap-2 mb-6 pb-2 no-scrollbar">
                    {[
                        { id: 'overview', label: 'Overview', icon: Activity },
                        { id: 'records', label: 'Medical Records', icon: FileText },
                        { id: 'lab-upload', label: 'Upload Report', icon: Upload },
                        { id: 'chat', label: 'AI Assistant', icon: MessageSquare },
                        ...(labAnalysis ? [{ id: 'lab-analysis', label: 'Analysis Result', icon: Brain }] : [])
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center gap-2 px-6 py-3 rounded-full font-medium transition-all whitespace-nowrap ${activeTab === tab.id
                                    ? 'bg-emerald-600 text-white shadow-md'
                                    : 'bg-white text-gray-600 hover:bg-emerald-50 border border-gray-200'
                                }`}
                        >
                            <tab.icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    ))}
                </div>

                <AnimatePresence mode="wait">
                    {activeTab === 'overview' && (
                        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} key="overview" className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* AI Health Summary */}
                            <div className="lg:col-span-2 space-y-6">
                                <Card className="p-6 bg-gradient-to-br from-indigo-50 to-white border-indigo-100">
                                    <h2 className="text-xl font-bold text-indigo-900 mb-4 flex items-center gap-2">
                                        <Brain className="w-6 h-6 text-indigo-600" />
                                        Health Summary
                                    </h2>
                                    {aiSummary ? (
                                        <div className="prose prose-indigo max-w-none">
                                            <p className="text-gray-700 leading-relaxed whitespace-pre-line">{aiSummary.summary_text}</p>

                                            <div className="flex flex-wrap gap-2 mt-4">
                                                {aiSummary.key_conditions?.map((c, i) => (
                                                    <span key={i} className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold uppercase tracking-wide">
                                                        {c}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="flex items-center justify-center p-8">
                                            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
                                        </div>
                                    )}
                                </Card>

                                {/* Quick Safety Check */}
                                <Card className="p-6 border-orange-100 bg-white">
                                    <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                        <Shield className="w-5 h-5 text-orange-500" />
                                        Medication Safety Check
                                    </h3>
                                    <form onSubmit={handleSafetyCheck} className="flex gap-2">
                                        <input
                                            type="text"
                                            value={medicineCheck}
                                            onChange={(e) => setMedicineCheck(e.target.value)}
                                            placeholder="Enter medicine name..."
                                            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500"
                                        />
                                        <Button disabled={checkingSafety} type="submit" className="bg-orange-500 hover:bg-orange-600 text-white">
                                            {checkingSafety ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Check'}
                                        </Button>
                                    </form>
                                    {safetyResult && (
                                        <div className={`mt-4 p-4 rounded-lg flex items-start gap-3 ${safetyResult.status === 'Safe' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                                            {safetyResult.status === 'Safe' ? <CheckCircle2 className="w-5 h-5 mt-0.5" /> : <AlertTriangle className="w-5 h-5 mt-0.5" />}
                                            <div>
                                                <p className="font-bold">{safetyResult.status === 'Safe' ? 'Safe to take' : 'Potential Interaction Detected'}</p>
                                                <p className="text-sm mt-1">{safetyResult.patient_explanation}</p>
                                            </div>
                                        </div>
                                    )}
                                </Card>
                            </div>

                            {/* Recommendations Sidebar */}
                            <div className="space-y-6">
                                <Card className="p-6 border-cyan-100 bg-cyan-50/50">
                                    <h3 className="font-bold text-cyan-900 mb-4 flex items-center gap-2">
                                        <Beaker className="w-5 h-5 text-cyan-600" />
                                        Recommended Tests
                                    </h3>
                                    <div className="space-y-3">
                                        {testRecommendations.length > 0 ? testRecommendations.map((rec, i) => (
                                            <div key={i} className="bg-white p-3 rounded-lg border border-cyan-100 shadow-sm">
                                                <div className="flex justify-between items-start mb-1">
                                                    <span className="font-semibold text-gray-900 text-sm">{rec.test}</span>
                                                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${rec.priority === 'Critical' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                                                        }`}>{rec.priority}</span>
                                                </div>
                                                <p className="text-xs text-gray-500">{rec.rationale}</p>
                                            </div>
                                        )) : <p className="text-sm text-gray-500">No pending recommendations.</p>}
                                    </div>
                                </Card>
                            </div>
                        </motion.div>
                    )}

                    {activeTab === 'records' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} key="records" className="space-y-6">
                            {/* Medications */}
                            <Card className="p-6">
                                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <Pill className="w-5 h-5 text-purple-500" />
                                    Active Medications
                                </h3>
                                <div className="grid md:grid-cols-2 gap-4">
                                    {(patient.medications || []).map((entry, i) => (
                                        <div key={i} className="p-4 border rounded-lg bg-gray-50 flex items-center justify-between">
                                            <div>
                                                <p className="font-semibold text-gray-900">{entry.resource?.medicationCodeableConcept?.text || "Unknown Med"}</p>
                                                <p className="text-xs text-gray-500">Status: {entry.resource?.status}</p>
                                            </div>
                                            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Active</span>
                                        </div>
                                    ))}
                                    {(!patient.medications?.length) && <p className="text-gray-500 text-sm">No active medications found.</p>}
                                </div>
                            </Card>

                            {/* Conditions */}
                            <Card className="p-6">
                                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <Activity className="w-5 h-5 text-red-500" />
                                    Diagnosed Conditions
                                </h3>
                                <div className="space-y-2">
                                    {(patient.diagnoses || []).map((entry, i) => (
                                        <div key={i} className="flex items-center gap-3 p-3 bg-red-50 rounded-lg">
                                            <div className="w-2 h-2 rounded-full bg-red-500" />
                                            <p className="font-medium text-gray-900">{entry.resource?.code?.text}</p>
                                        </div>
                                    ))}
                                </div>
                            </Card>
                        </motion.div>
                    )}

                    {activeTab === 'lab-upload' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} key="upload" className="max-w-xl mx-auto">
                            <Card className="p-8 text-center border-2 border-dashed border-gray-300 hover:border-emerald-400 transition-colors">
                                <form onSubmit={handleLabUpload}>
                                    <div className="mb-8">
                                        <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                            <Upload className="w-8 h-8 text-emerald-600" />
                                        </div>
                                        <h3 className="text-xl font-bold text-gray-900">Upload Lab Report</h3>
                                        <p className="text-gray-500 mt-2">Supports PDF, JPG, PNG (Max 5MB)</p>
                                    </div>

                                    <div className="space-y-4 text-left">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Test Name (Optional)</label>
                                            <input
                                                type="text"
                                                className="w-full px-4 py-2 border rounded-lg"
                                                placeholder="e.g. Complete Blood Count"
                                                value={labTestName}
                                                onChange={e => setLabTestName(e.target.value)}
                                            />
                                        </div>

                                        <div className="border rounded-lg p-4 bg-gray-50">
                                            <input
                                                type="file"
                                                accept=".pdf,.jpg,.jpeg,.png"
                                                onChange={e => setLabFile(e.target.files[0])}
                                                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"
                                            />
                                        </div>

                                        <Button type="submit" disabled={analyzingLab} className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3">
                                            {analyzingLab ? (
                                                <span className="flex items-center justify-center gap-2">
                                                    <Loader2 className="animate-spin w-4 h-4" /> Analyzing Report...
                                                </span>
                                            ) : 'Upload & Analyze'}
                                        </Button>
                                    </div>
                                </form>
                            </Card>
                        </motion.div>
                    )}

                    {activeTab === 'lab-analysis' && labAnalysis && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} key="analysis" className="space-y-6">
                            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 rounded-2xl text-white shadow-lg">
                                <h2 className="text-2xl font-bold mb-2">Analysis Results</h2>
                                <p className="opacity-90">{labAnalysis.test_name}</p>
                            </div>

                            <Card className="p-6 border-l-4 border-yellow-400">
                                <h3 className="font-bold text-lg mb-2 text-gray-900">Summary</h3>
                                <p className="text-gray-700">{labAnalysis.overall_assessment}</p>
                            </Card>

                            <div className="grid md:grid-cols-2 gap-6">
                                <Card className="p-6">
                                    <h3 className="font-bold text-red-600 mb-4 flex items-center gap-2">
                                        <AlertCircle className="w-5 h-5" /> Abnormal Findings
                                    </h3>
                                    {labAnalysis.abnormal_findings?.length > 0 ? (
                                        <div className="space-y-3">
                                            {labAnalysis.abnormal_findings.map((finding, i) => (
                                                <div key={i} className="bg-red-50 p-3 rounded-lg border border-red-100">
                                                    <div className="flex justify-between">
                                                        <span className="font-bold text-gray-900">{finding.parameter}</span>
                                                        <span className="text-red-600 font-bold">{finding.value}</span>
                                                    </div>
                                                    <p className="text-xs text-red-500 mt-1">Ref: {finding.reference_range}</p>
                                                </div>
                                            ))}
                                        </div>
                                    ) : <p className="text-green-600">No abnormal findings detected.</p>}
                                </Card>

                                <Card className="p-6">
                                    <h3 className="font-bold text-emerald-600 mb-4 flex items-center gap-2">
                                        <CheckCircle2 className="w-5 h-5" /> Recommendations
                                    </h3>
                                    <ul className="space-y-2">
                                        {labAnalysis.recommendations?.map((rec, i) => (
                                            <li key={i} className="flex items-start gap-2 text-gray-700">
                                                <ArrowRight className="w-4 h-4 mt-1 text-emerald-500 shrink-0" />
                                                {rec}
                                            </li>
                                        ))}
                                    </ul>
                                </Card>
                            </div>
                        </motion.div>
                    )}

                    {activeTab === 'chat' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} key="chat" className="h-[600px] flex flex-col bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-200">
                            <div className="bg-indigo-600 p-4 text-white flex items-center gap-3">
                                <div className="p-2 bg-white/20 rounded-lg">
                                    <Bot className="w-6 h-6" />
                                </div>
                                <div>
                                    <h3 className="font-bold">PrismCare AI</h3>
                                    <p className="text-xs opacity-80">Context-Aware Medical Assistant</p>
                                </div>
                            </div>

                            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                                {chatHistory.map((msg, i) => (
                                    <div key={i} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[80%] p-3 rounded-2xl ${msg.sender === 'user'
                                                ? 'bg-indigo-600 text-white rounded-tr-none'
                                                : 'bg-white text-gray-800 shadow-sm border border-gray-100 rounded-tl-none'
                                            }`}>
                                            <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
                                        </div>
                                    </div>
                                ))}
                                {chatLoading && (
                                    <div className="flex justify-start">
                                        <div className="bg-white p-3 rounded-2xl shadow-sm border border-gray-100 rounded-tl-none">
                                            <Loader2 className="w-5 h-5 animate-spin text-indigo-500" />
                                        </div>
                                    </div>
                                )}
                                <div ref={chatEndRef} />
                            </div>

                            <form onSubmit={handleChatSubmit} className="p-4 bg-white border-t border-gray-100 flex gap-2">
                                <input
                                    type="text"
                                    value={chatInput}
                                    onChange={e => setChatInput(e.target.value)}
                                    placeholder="Ask about your medications, allergies, or reports..."
                                    className="flex-1 px-4 py-3 bg-gray-50 border-0 rounded-xl focus:ring-2 focus:ring-indigo-500"
                                />
                                <Button type="submit" disabled={chatLoading || !chatInput.trim()} className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl px-4">
                                    <Send className="w-5 h-5" />
                                </Button>
                            </form>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
}
