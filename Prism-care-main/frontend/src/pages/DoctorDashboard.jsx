import { useState, useRef, useEffect } from 'react';
import { Search, FileText, AlertCircle, MessageSquare, Send, Activity, Clock, FileBarChart } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import Button from '../components/Button';
import FormattedText from '../components/FormattedText';
import Card from '../components/Card';
import Modal from '../components/Modal';
import XAIExplanationPanel from '../components/XAIExplanationPanel';

export default function DoctorDashboard() {
    const [patientId, setPatientId] = useState('');
    const [patient, setPatient] = useState(null);
    const [medicine, setMedicine] = useState('');
    const [dosage, setDosage] = useState('');
    const [result, setResult] = useState(null);
    const [showOverrideModal, setShowOverrideModal] = useState(false);
    const [overrideReason, setOverrideReason] = useState('');
    const [analyzing, setAnalyzing] = useState(false);

    // Chat State
    const [chatQuery, setChatQuery] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [chatLoading, setChatLoading] = useState(false);
    const chatEndRef = useRef(null);

    // Tabs State
    const [activeTab, setActiveTab] = useState('overview');

    // AI Recommendations State
    const [testRecommendations, setTestRecommendations] = useState([]);
    const [treatmentSuggestions, setTreatmentSuggestions] = useState([]);
    const [loadingRecommendations, setLoadingRecommendations] = useState(false);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [chatHistory]);

    const handlePatientLookup = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.get(`http://localhost:5000/api/patient/${patientId}`);
            setPatient(response.data);
            setChatHistory([]); // Reset chat for new patient
            toast.success('Patient loaded');

            // Fetch AI recommendations
            fetchRecommendations(patientId);
        } catch (error) {
            toast.error('Patient not found');
            setPatient(null);
        }
    };

    const fetchRecommendations = async (abhaId) => {
        setLoadingRecommendations(true);
        try {
            const [testsRes, treatmentsRes] = await Promise.all([
                axios.get(`http://localhost:5000/api/patient/${abhaId}/test-recommendations`),
                // We'll fetch treatment suggestions for the first diagnosis if available
                axios.get(`http://localhost:5000/api/patient/${abhaId}/treatment-suggestions?diagnosis=Type 2 Diabetes Mellitus`).catch(() => ({ data: { suggestions: [] } }))
            ]);

            setTestRecommendations(testsRes.data.recommendations || []);
            setTreatmentSuggestions(treatmentsRes.data.suggestions || []);
        } catch (error) {
            console.error('Failed to fetch recommendations:', error);
        } finally {
            setLoadingRecommendations(false);
        }
    };

    const handleAnalyze = async (e) => {
        e.preventDefault();
        setAnalyzing(true);
        try {
            const response = await axios.post('http://localhost:5000/api/check-safety', {
                abha_id: patient.id,
                medicine: medicine
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
                patient_id: patient.id,
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

    const handleChatSubmit = async (e) => {
        e.preventDefault();
        if (!chatQuery.trim()) return;

        const userMessage = { role: 'user', content: chatQuery };
        setChatHistory(prev => [...prev, userMessage]);
        setChatQuery('');
        setChatLoading(true);

        try {
            const response = await axios.post('http://localhost:5000/api/chat', {
                abha_id: patient.id,
                query: userMessage.content,
                history: chatHistory
            });

            const aiMessage = { role: 'ai', content: response.data.response };
            setChatHistory(prev => [...prev, aiMessage]);
        } catch (error) {
            toast.error('Failed to get AI response');
            setChatHistory(prev => [...prev, { role: 'ai', content: "Sorry, I couldn't process that request right now." }]);
        } finally {
            setChatLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold mb-8 text-slate-800">Doctor Dashboard</h1>

                {/* Patient Lookup & Main Grid */}
                <div className="grid lg:grid-cols-12 gap-6">

                    {/* LEFT COLUMN: Patient Info & Clinical Tools (7 columns) */}
                    <div className="lg:col-span-7 space-y-6">
                        {/* 1. Lookup */}
                        <Card>
                            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                <Search className="w-5 h-5 text-primary" /> Patient Lookup
                            </h2>
                            <form onSubmit={handlePatientLookup} className="flex gap-2">
                                <input
                                    type="text"
                                    value={patientId}
                                    onChange={(e) => setPatientId(e.target.value)}
                                    placeholder="Enter ABHA ID (e.g., ABHA001)"
                                    className="flex-1 px-4 py-2 border rounded-soft focus:ring-2 focus:ring-primary/20 outline-none"
                                    required
                                />
                                <Button type="submit">Load Patient</Button>
                            </form>
                        </Card>

                        {patient && (
                            <>
                                {/* 2. Patient Demographics Card */}
                                <Card className="bg-white border-l-4 border-primary">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h3 className="text-2xl font-bold text-slate-800">{patient.name}</h3>
                                            <div className="text-slate-500 text-sm mt-1 flex gap-4">
                                                <span>ID: {patient.id}</span>
                                                <span>•</span>
                                                <span>{patient.age} Years</span>
                                                <span>•</span>
                                                <span>{patient.gender}</span>
                                            </div>
                                        </div>
                                        <div className="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-bold">
                                            Active Patient
                                        </div>
                                    </div>
                                </Card>

                                {/* 3. Clinical Tabs */}
                                <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                                    <div className="flex border-b border-slate-100">
                                        <button
                                            onClick={() => setActiveTab('overview')}
                                            className={`flex-1 py-3 text-sm font-medium transition-colors ${activeTab === 'overview' ? 'bg-primary/5 text-primary border-b-2 border-primary' : 'text-slate-500 hover:text-slate-700'}`}
                                        >
                                            <Activity className="w-4 h-4 inline-block mr-2" /> Overview
                                        </button>
                                        <button
                                            onClick={() => setActiveTab('history')}
                                            className={`flex-1 py-3 text-sm font-medium transition-colors ${activeTab === 'history' ? 'bg-primary/5 text-primary border-b-2 border-primary' : 'text-slate-500 hover:text-slate-700'}`}
                                        >
                                            <Clock className="w-4 h-4 inline-block mr-2" /> History
                                        </button>
                                        <button
                                            onClick={() => setActiveTab('labs')}
                                            className={`flex-1 py-3 text-sm font-medium transition-colors ${activeTab === 'labs' ? 'bg-primary/5 text-primary border-b-2 border-primary' : 'text-slate-500 hover:text-slate-700'}`}
                                        >
                                            <FileBarChart className="w-4 h-4 inline-block mr-2" /> Labs
                                        </button>
                                    </div>

                                    <div className="p-6">
                                        {/* TAB: OVERVIEW */}
                                        {activeTab === 'overview' && (
                                            <div className="space-y-6">
                                                <div>
                                                    <h4 className="text-sm font-semibold text-slate-900 mb-3 uppercase tracking-wide">Active Medications</h4>
                                                    <div className="space-y-2">
                                                        {patient.medications && patient.medications.length > 0 ? (
                                                            patient.medications.map((entry, i) => {
                                                                const res = entry.resource;
                                                                if (res?.status !== 'active') return null;
                                                                return (
                                                                    <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100">
                                                                        <span className="font-medium text-slate-700">{res.medicationCodeableConcept?.text}</span>
                                                                        <span className="text-xs bg-white px-2 py-1 rounded border border-slate-200 text-slate-500">
                                                                            {res.dosageInstruction?.[0]?.text || 'As directed'}
                                                                        </span>
                                                                    </div>
                                                                );
                                                            })
                                                        ) : (
                                                            <p className="text-slate-500 italic">No active medications.</p>
                                                        )}
                                                    </div>
                                                </div>

                                                <div>
                                                    <h4 className="text-sm font-semibold text-slate-900 mb-3 uppercase tracking-wide">Recent Diagnoses</h4>
                                                    <div className="flex flex-wrap gap-2">
                                                        {patient.diagnoses && patient.diagnoses.length > 0 ? (
                                                            patient.diagnoses.map((entry, i) => (
                                                                <span key={i} className="px-3 py-1 rounded-full bg-red-50 text-red-600 border border-red-100 text-sm font-medium">
                                                                    {entry.resource?.code?.text || 'Unknown Condition'}
                                                                </span>
                                                            ))
                                                        ) : (
                                                            <p className="text-slate-500 italic">No diagnoses recorded.</p>
                                                        )}
                                                    </div>
                                                </div>

                                                {/* AI-Powered Recommendations */}
                                                <div className="border-t border-slate-200 pt-6">
                                                    <h4 className="text-sm font-semibold text-slate-900 mb-3 uppercase tracking-wide flex items-center gap-2">
                                                        <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                                        </svg>
                                                        AI-Recommended Tests
                                                    </h4>
                                                    {loadingRecommendations ? (
                                                        <div className="text-center py-4 text-slate-500">Loading recommendations...</div>
                                                    ) : testRecommendations.length > 0 ? (
                                                        <div className="space-y-3">
                                                            {testRecommendations.map((test, idx) => (
                                                                <div key={idx} className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
                                                                    <div className="flex items-start justify-between">
                                                                        <div className="flex-1">
                                                                            <h5 className="font-semibold text-blue-900">{test.test}</h5>
                                                                            <p className="text-sm text-blue-700 mt-1">{test.rationale}</p>
                                                                            <div className="flex gap-3 mt-2 text-xs">
                                                                                <span className="text-blue-600">Frequency: {test.frequency}</span>
                                                                                <span className="px-2 py-0.5 rounded-full bg-blue-200 text-blue-800 font-medium">
                                                                                    {test.priority}
                                                                                </span>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    ) : (
                                                        <p className="text-slate-500 italic">No test recommendations at this time.</p>
                                                    )}
                                                </div>

                                                {/* Treatment Suggestions */}
                                                {treatmentSuggestions.length > 0 && (
                                                    <div className="border-t border-slate-200 pt-6">
                                                        <h4 className="text-sm font-semibold text-slate-900 mb-3 uppercase tracking-wide flex items-center gap-2">
                                                            <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                            </svg>
                                                            Treatment Suggestions
                                                        </h4>
                                                        <div className="space-y-3">
                                                            {treatmentSuggestions.map((suggestion, idx) => (
                                                                <div key={idx} className="p-4 bg-green-50 border border-green-100 rounded-lg">
                                                                    <h5 className="font-semibold text-green-900">{suggestion.treatment || suggestion.category}</h5>
                                                                    <p className="text-sm text-green-700 mt-1">{suggestion.rationale || suggestion.recommendation}</p>
                                                                    {(suggestion.source || suggestion.evidence_level || suggestion.evidence) && (
                                                                        <p className="text-xs text-green-600 mt-2 italic">
                                                                            {suggestion.evidence_level ? `Evidence level ${suggestion.evidence_level}` : ''}
                                                                            {suggestion.evidence_level && suggestion.source ? ' · ' : ''}
                                                                            {suggestion.source || suggestion.evidence}
                                                                        </p>
                                                                    )}
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {/* TAB: HISTORY */}
                                        {activeTab === 'history' && (
                                            <div className="relative border-l-2 border-slate-200 ml-3 space-y-6 py-2">
                                                {patient.visit_summaries && patient.visit_summaries.length > 0 ? (
                                                    patient.visit_summaries.map((visit, i) => (
                                                        <div key={i} className="ml-6 relative">
                                                            <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-primary border-2 border-white shadow-sm ring-1 ring-slate-100"></div>
                                                            <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                                                                <div className="flex justify-between items-start mb-1">
                                                                    <h5 className="font-semibold text-slate-800">{visit.resource?.type?.[0]?.text || 'General Visit'}</h5>
                                                                    <span className="text-xs text-slate-500 font-mono">
                                                                        {visit.resource?.period?.start ? new Date(visit.resource.period.start).toLocaleDateString() : 'Date Unknown'}
                                                                    </span>
                                                                </div>
                                                                <p className="text-sm text-slate-600">
                                                                    {visit.resource?.reasonCode?.[0]?.text || 'Routine Checkup'}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    ))
                                                ) : (
                                                    <p className="ml-6 text-slate-500 italic">No visit history available.</p>
                                                )}
                                            </div>
                                        )}

                                        {/* TAB: LABS */}
                                        {activeTab === 'labs' && (
                                            <div className="grid gap-4">
                                                {patient.lab_reports && patient.lab_reports.length > 0 ? (
                                                    patient.lab_reports.map((report, i) => (
                                                        <div key={i} className="flex items-center p-4 bg-white border border-slate-200 rounded-lg hover:border-primary/50 transition-colors cursor-pointer group">
                                                            <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mr-4 group-hover:bg-blue-100">
                                                                <FileText className="w-5 h-5" />
                                                            </div>
                                                            <div className="flex-1">
                                                                <h5 className="font-semibold text-slate-800">{report.resource?.code?.text || 'Lab Report'}</h5>
                                                                <p className="text-xs text-slate-500">
                                                                    {report.resource?.effectiveDateTime ? new Date(report.resource.effectiveDateTime).toLocaleDateString() : 'Date Unknown'}
                                                                </p>
                                                            </div>
                                                            <div className="text-right">
                                                                <span className="text-sm font-mono font-bold text-slate-700">
                                                                    {report.resource?.valueQuantity?.value} {report.resource?.valueQuantity?.unit}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    ))
                                                ) : (
                                                    <p className="text-slate-500 italic text-center py-8">No lab reports found.</p>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* 4. Prescription Writer */}
                                <Card>
                                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                        <Activity className="w-5 h-5 text-green-600" /> Prescribe & Analyze
                                    </h2>
                                    <form onSubmit={handleAnalyze} className="space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium mb-1 text-slate-600">Medicine Name</label>
                                                <input
                                                    type="text"
                                                    value={medicine}
                                                    onChange={(e) => setMedicine(e.target.value)}
                                                    className="w-full px-4 py-2 border rounded-soft focus:ring-2 focus:ring-primary/20 outline-none"
                                                    placeholder="e.g., Aspirin"
                                                    required
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium mb-1 text-slate-600">Dosage</label>
                                                <input
                                                    type="text"
                                                    value={dosage}
                                                    onChange={(e) => setDosage(e.target.value)}
                                                    placeholder="e.g., 500mg daily"
                                                    className="w-full px-4 py-2 border rounded-soft focus:ring-2 focus:ring-primary/20 outline-none"
                                                />
                                            </div>
                                        </div>
                                        <Button type="submit" className="w-full" loading={analyzing}>
                                            Check Safety Interactions
                                        </Button>
                                    </form>
                                </Card>
                            </>
                        )}
                    </div>

                    {/* RIGHT COLUMN: AI Assistant & Safety Results (5 columns) */}
                    <div className="lg:col-span-5 space-y-6">

                        {/* 1. Safety Analysis Result with XAI */}
                        {result && (
                            <Card className={result.status === 'Risky' ? 'border-2 border-danger shadow-lg' : 'border-2 border-accent shadow-sm'}>
                                <div className="flex items-center gap-2 mb-4">
                                    {result.status === 'Risky' ? (
                                        <AlertCircle className="w-6 h-6 text-danger" />
                                    ) : (
                                        <Activity className="w-6 h-6 text-accent" />
                                    )}
                                    <h2 className="text-xl font-bold">AI Safety Analysis</h2>
                                </div>

                                <div className={`p-4 rounded-lg mb-4 text-center ${result.status === 'Risky' ? 'bg-danger/10 text-danger border border-danger/20' : 'bg-accent/10 text-accent border border-accent/20'}`}>
                                    <p className="font-bold text-lg">
                                        {result.status === 'Risky' ? '⚠️ RISK DETECTED' : '✓ SAFE TO PRESCRIBE'}
                                    </p>
                                    {result.risk_level && (
                                        <p className="text-sm mt-1 font-semibold">
                                            Risk Level: {result.risk_level}
                                        </p>
                                    )}
                                </div>

                                {/* XAI Explanation Panel */}
                                <XAIExplanationPanel
                                    explanation={result.doctor_explanation}
                                    patientExplanation={result.patient_explanation}
                                    doctorExplanation={result.doctor_explanation}
                                    mechanism={result.mechanism}
                                    source={result.source}
                                    recommendation={result.recommendation}
                                    riskLevel={result.risk_level || (result.status === 'Risky' ? 'High' : 'Safe')}
                                    confidenceScore={result.confidence}
                                    viewMode="doctor"
                                />

                                {/* Action Buttons */}
                                <div className="mt-4 space-y-2">
                                    {result.status === 'Risky' && (
                                        <Button
                                            variant="danger"
                                            className="w-full"
                                            onClick={() => setShowOverrideModal(true)}
                                        >
                                            Override Risk & Prescribe Anyway
                                        </Button>
                                    )}
                                    {result.status === 'Safe' && (
                                        <Button
                                            className="w-full"
                                            onClick={() => toast.success('Prescription can be safely issued')}
                                        >
                                            Proceed with Prescription
                                        </Button>
                                    )}
                                </div>
                            </Card>
                        )}

                        {/* 2. AI Chat Companion (Only show if patient loaded) */}
                        {patient && (
                            <div className="bg-white rounded-xl shadow-lg border border-slate-200 flex flex-col h-[600px] overflow-hidden">
                                <div className="p-4 bg-gradient-to-r from-slate-800 to-slate-900 text-white flex justify-between items-center">
                                    <div className="flex items-center gap-2">
                                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center backdrop-blur-sm">
                                            <MessageSquare className="w-4 h-4 text-primary-foreground" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-sm">Clinical AI Assistant</h3>
                                            <p className="text-xs text-slate-400">Context-aware for {patient.name}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Chat Messages */}
                                <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
                                    {chatHistory.length === 0 && (
                                        <div className="text-center py-8 text-slate-400">
                                            <div className="w-12 h-12 bg-slate-100 rounded-full mx-auto mb-3 flex items-center justify-center">
                                                <MessageSquare className="w-6 h-6 text-slate-300" />
                                            </div>
                                            <p className="text-sm">Ask about patient history, drug interactions, or guidelines.</p>
                                            <div className="mt-4 flex flex-wrap justify-center gap-2">
                                                <button onClick={() => setChatQuery("Summarize patient history")} className="text-xs bg-white border border-slate-200 px-3 py-1 rounded-full hover:bg-slate-50 transition-colors">Summarize history</button>
                                                <button onClick={() => setChatQuery("Show recent lab trends")} className="text-xs bg-white border border-slate-200 px-3 py-1 rounded-full hover:bg-slate-50 transition-colors">Lab trends</button>
                                            </div>
                                        </div>
                                    )}

                                    {chatHistory.map((msg, idx) => (
                                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${msg.role === 'user'
                                                ? 'bg-primary text-white rounded-br-none shadow-md'
                                                : 'bg-white text-slate-700 border border-slate-200 rounded-bl-none shadow-sm'
                                                }`}>
                                                <FormattedText text={msg.content} className="space-y-0.5" />
                                            </div>
                                        </div>
                                    ))}
                                    {chatLoading && (
                                        <div className="flex justify-start">
                                            <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-none px-4 py-3 shadow-sm">
                                                <div className="flex space-x-1">
                                                    <div className="w-2 h-2 bg-primary/40 rounded-full animate-bounce"></div>
                                                    <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                                    <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                    <div ref={chatEndRef} />
                                </div>

                                {/* Chat Input */}
                                <div className="p-3 bg-white border-t border-slate-100">
                                    <form onSubmit={handleChatSubmit} className="relative">
                                        <input
                                            type="text"
                                            value={chatQuery}
                                            onChange={(e) => setChatQuery(e.target.value)}
                                            placeholder="Ask about this patient..."
                                            className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary/50 text-sm"
                                        />
                                        <button
                                            type="submit"
                                            disabled={!chatQuery.trim() || chatLoading}
                                            className="absolute right-2 top-2 p-1.5 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                        >
                                            <Send className="w-4 h-4" />
                                        </button>
                                    </form>
                                </div>
                            </div>
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

// Add custom styles for scrollbar if needed
const style = document.createElement('style');
style.textContent = `
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  ::-webkit-scrollbar-track {
    background: transparent; 
  }
  ::-webkit-scrollbar-thumb {
    background: #cbd5e1; 
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: #94a3b8; 
  }
`;
document.head.appendChild(style);
