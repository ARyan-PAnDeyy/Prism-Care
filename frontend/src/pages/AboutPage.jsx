import { Brain, Users, Award } from 'lucide-react';
import Card from '../components/Card';

export default function AboutPage() {
    return (
        <div className="min-h-screen bg-slate-50 py-16">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h1 className="text-5xl font-bold mb-4">About PrismCare</h1>
                    <p className="text-xl text-slate-600">Multi-View Transparency in Digital Health</p>
                </div>

                <div className="space-y-12">
                    <Card>
                        <h2 className="text-2xl font-bold mb-4">Our Mission</h2>
                        <p className="text-slate-700 leading-relaxed">
                            PrismCare is a final year project aimed at revolutionizing medication safety through AI-powered drug interaction analysis.
                            We believe that healthcare information should be accessible and understandable to everyone - from patients to doctors to administrators.
                        </p>
                        <p className="text-slate-700 leading-relaxed mt-4">
                            Our unique multi-view approach ensures that the same safety analysis is presented in ways that make sense for each user type,
                            promoting transparency and informed decision-making across the healthcare ecosystem.
                        </p>
                    </Card>

                    <div className="grid md:grid-cols-3 gap-6">
                        <Card className="text-center">
                            <Brain className="h-12 w-12 text-primary mx-auto mb-4" />
                            <h3 className="font-bold mb-2">AI-Powered</h3>
                            <p className="text-sm text-slate-600">Using RAG and ChromaDB for intelligent analysis</p>
                        </Card>
                        <Card className="text-center">
                            <Users className="h-12 w-12 text-secondary mx-auto mb-4" />
                            <h3 className="font-bold mb-2">User-Centric</h3>
                            <p className="text-sm text-slate-600">Designed for patients, doctors, and admins</p>
                        </Card>
                        <Card className="text-center">
                            <Award className="h-12 w-12 text-accent mx-auto mb-4" />
                            <h3 className="font-bold mb-2">Evidence-Based</h3>
                            <p className="text-sm text-slate-600">Built on medical guidelines and research</p>
                        </Card>
                    </div>

                    <Card>
                        <h2 className="text-2xl font-bold mb-4">Technology Stack</h2>
                        <div className="grid md:grid-cols-2 gap-4">
                            <div>
                                <h3 className="font-semibold mb-2">Backend</h3>
                                <ul className="text-sm text-slate-600 space-y-1">
                                    <li>• Python & Flask</li>
                                    <li>• ChromaDB (Vector Database)</li>
                                    <li>• LangChain (RAG Framework)</li>
                                    <li>• FHIR-compliant APIs</li>
                                </ul>
                            </div>
                            <div>
                                <h3 className="font-semibold mb-2">Frontend</h3>
                                <ul className="text-sm text-slate-600 space-y-1">
                                    <li>• React & Vite</li>
                                    <li>• Tailwind CSS</li>
                                    <li>• Framer Motion</li>
                                    <li>• Recharts</li>
                                </ul>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
