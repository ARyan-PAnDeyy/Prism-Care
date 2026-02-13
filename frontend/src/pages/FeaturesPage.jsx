import { CheckCircle2 } from 'lucide-react';
import Card from '../components/Card';

export default function FeaturesPage() {
    const patientFeatures = [
        "Simple, jargon-free explanations",
        "Instant safety checks",
        "Medication history tracking",
        "Traffic light visual system"
    ];

    const doctorFeatures = [
        "Clinical-grade analysis",
        "Evidence-based recommendations",
        "Override capability with justification",
        "Source citations and guidelines"
    ];

    const adminFeatures = [
        "Real-time analytics dashboard",
        "Comprehensive audit logs",
        "System health monitoring",
        "Export capabilities"
    ];

    return (
        <div className="min-h-screen bg-slate-50 py-16">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h1 className="text-5xl font-bold mb-4">Powerful Features</h1>
                    <p className="text-xl text-slate-600">Built for every user in the healthcare ecosystem</p>
                </div>

                <div className="space-y-12">
                    <div className="grid md:grid-cols-2 gap-8 items-center">
                        <div>
                            <h2 className="text-3xl font-bold mb-4">For Patients</h2>
                            <ul className="space-y-3">
                                {patientFeatures.map((feature, i) => (
                                    <li key={i} className="flex items-start">
                                        <CheckCircle2 className="h-6 w-6 text-accent mr-3 flex-shrink-0 mt-0.5" />
                                        <span className="text-lg">{feature}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <Card variant="gradient" className="h-64 flex items-center justify-center">
                            <p className="text-white text-center text-lg">Patient Dashboard Screenshot</p>
                        </Card>
                    </div>

                    <div className="grid md:grid-cols-2 gap-8 items-center">
                        <Card variant="gradient" className="h-64 flex items-center justify-center md:order-first">
                            <p className="text-white text-center text-lg">Doctor Dashboard Screenshot</p>
                        </Card>
                        <div>
                            <h2 className="text-3xl font-bold mb-4">For Doctors</h2>
                            <ul className="space-y-3">
                                {doctorFeatures.map((feature, i) => (
                                    <li key={i} className="flex items-start">
                                        <CheckCircle2 className="h-6 w-6 text-secondary mr-3 flex-shrink-0 mt-0.5" />
                                        <span className="text-lg">{feature}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-8 items-center">
                        <div>
                            <h2 className="text-3xl font-bold mb-4">For Administrators</h2>
                            <ul className="space-y-3">
                                {adminFeatures.map((feature, i) => (
                                    <li key={i} className="flex items-start">
                                        <CheckCircle2 className="h-6 w-6 text-primary mr-3 flex-shrink-0 mt-0.5" />
                                        <span className="text-lg">{feature}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <Card variant="gradient" className="h-64 flex items-center justify-center">
                            <p className="text-white text-center text-lg">Admin Dashboard Screenshot</p>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
