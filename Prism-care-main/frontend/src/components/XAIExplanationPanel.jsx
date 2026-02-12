import { useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle, BookOpen, Lightbulb, Shield } from 'lucide-react';
import RiskGauge from './RiskGauge';

/**
 * XAI Explanation Panel Component
 * Displays AI explanations with expandable sections for mechanism, evidence, and recommendations
 */
export default function XAIExplanationPanel({
    explanation,
    mechanism,
    source,
    recommendation,
    riskLevel = 'Moderate',
    confidenceScore = null,
    patientExplanation = null,
    doctorExplanation = null,
    viewMode = 'doctor' // 'doctor' or 'patient'
}) {
    const [showMechanism, setShowMechanism] = useState(false);
    const [showEvidence, setShowEvidence] = useState(false);
    const [showRecommendations, setShowRecommendations] = useState(false);

    // Risk level color mapping
    const riskColors = {
        'Safe': 'bg-green-50 border-green-200 text-green-800',
        'Low': 'bg-blue-50 border-blue-200 text-blue-800',
        'Moderate': 'bg-yellow-50 border-yellow-200 text-yellow-800',
        'High': 'bg-orange-50 border-orange-200 text-orange-800',
        'Critical': 'bg-red-50 border-red-200 text-red-800'
    };

    const riskBadgeColors = {
        'Safe': 'bg-green-100 text-green-800 border-green-300',
        'Low': 'bg-blue-100 text-blue-800 border-blue-300',
        'Moderate': 'bg-yellow-100 text-yellow-800 border-yellow-300',
        'High': 'bg-orange-100 text-orange-800 border-orange-300',
        'Critical': 'bg-red-100 text-red-800 border-red-300'
    };

    const displayExplanation = viewMode === 'patient' && patientExplanation
        ? patientExplanation
        : (doctorExplanation || explanation);

    return (
        <div className={`rounded-lg border-2 p-4 ${riskColors[riskLevel] || riskColors['Moderate']}`}>
            {/* Header with Risk Level */}
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    <span className="font-bold text-lg">XAI Explanation</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold border ${riskBadgeColors[riskLevel]}`}>
                        {riskLevel} Risk
                    </span>
                    {confidenceScore && (
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-white border border-slate-300 text-slate-700">
                            {Math.round(confidenceScore * 100)}% Confidence
                        </span>
                    )}
                </div>
            </div>

            {/* Visual Risk Gauge */}
            <div className="mb-4">
                <RiskGauge riskLevel={riskLevel} confidenceScore={confidenceScore} />
            </div>

            {/* Main Explanation */}
            <div className="mb-4">
                <h4 className="font-semibold text-sm mb-2 flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    {viewMode === 'patient' ? 'What This Means For You' : 'Clinical Explanation'}
                </h4>
                <p className="text-sm leading-relaxed">{displayExplanation}</p>
            </div>

            {/* Collapsible Sections */}
            <div className="space-y-2">
                {/* Mechanism Section (Doctor view only) */}
                {mechanism && viewMode === 'doctor' && (
                    <div className="border-t pt-2">
                        <button
                            onClick={() => setShowMechanism(!showMechanism)}
                            className="flex items-center justify-between w-full text-left hover:bg-white/50 p-2 rounded transition-colors"
                        >
                            <span className="font-semibold text-sm flex items-center gap-2">
                                <Lightbulb className="w-4 h-4" />
                                Mechanism of Interaction
                            </span>
                            {showMechanism ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                        {showMechanism && (
                            <div className="mt-2 p-3 bg-white/70 rounded text-sm">
                                <p className="italic">{mechanism}</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Evidence Source Section */}
                {source && (
                    <div className="border-t pt-2">
                        <button
                            onClick={() => setShowEvidence(!showEvidence)}
                            className="flex items-center justify-between w-full text-left hover:bg-white/50 p-2 rounded transition-colors"
                        >
                            <span className="font-semibold text-sm flex items-center gap-2">
                                <Shield className="w-4 h-4" />
                                Evidence Source
                            </span>
                            {showEvidence ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                        {showEvidence && (
                            <div className="mt-2 p-3 bg-white/70 rounded text-sm">
                                <p className="font-medium text-xs text-slate-600 mb-1">Based on:</p>
                                <p className="font-mono text-xs">{source}</p>
                            </div>
                        )}
                    </div>
                )}

                {/* Recommendations Section */}
                {recommendation && (
                    <div className="border-t pt-2">
                        <button
                            onClick={() => setShowRecommendations(!showRecommendations)}
                            className="flex items-center justify-between w-full text-left hover:bg-white/50 p-2 rounded transition-colors"
                        >
                            <span className="font-semibold text-sm flex items-center gap-2">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Clinical Recommendations
                            </span>
                            {showRecommendations ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                        {showRecommendations && (
                            <div className="mt-2 p-3 bg-white/70 rounded text-sm">
                                <p className="font-medium">{recommendation}</p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* View Mode Toggle (if both explanations available) */}
            {patientExplanation && doctorExplanation && (
                <div className="mt-3 pt-3 border-t">
                    <p className="text-xs text-slate-600 italic">
                        💡 Tip: This explanation is optimized for {viewMode === 'patient' ? 'patients' : 'healthcare providers'}
                    </p>
                </div>
            )}
        </div>
    );
}
