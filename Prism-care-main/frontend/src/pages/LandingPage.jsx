import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    Brain, Shield, Activity, ArrowRight, CheckCircle2,
    Users, TrendingUp, Star, ChevronDown
} from 'lucide-react';
import Button from '../components/Button';
import Card from '../components/Card';

export default function LandingPage() {
    const fadeIn = {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.6 }
    };

    const features = [
        {
            icon: <Brain className="h-12 w-12 text-primary" />,
            title: "AI-Powered Analysis",
            description: "Real-time drug interaction detection using advanced RAG technology and medical guidelines."
        },
        {
            icon: <Shield className="h-12 w-12 text-secondary" />,
            title: "Multi-View Transparency",
            description: "Tailored explanations for patients (simple) and doctors (clinical) - same data, different views."
        },
        {
            icon: <Activity className="h-12 w-12 text-accent" />,
            title: "Complete Audit Trail",
            description: "Comprehensive oversight for administrators with real-time analytics and override monitoring."
        }
    ];

    const steps = [
        { number: "01", title: "Patient Enters Medicine", desc: "Simple search interface" },
        { number: "02", title: "AI Analyzes History", desc: "Checks against current medications" },
        { number: "03", title: "Instant Safety Report", desc: "Clear, actionable results" }
    ];

    const stats = [
        { value: "10,000+", label: "Prescriptions Analyzed" },
        { value: "95%", label: "Risk Detection Accuracy" },
        { value: "500+", label: "Doctors Trust PrismCare" }
    ];

    const testimonials = [
        {
            quote: "PrismCare helped me understand my medications better. The simple explanations gave me peace of mind.",
            author: "Priya S.",
            role: "Patient",
            rating: 5
        },
        {
            quote: "The clinical insights are invaluable. It's like having a drug interaction specialist on call 24/7.",
            author: "Dr. Rajesh Kumar",
            role: "General Physician",
            rating: 5
        },
        {
            quote: "The audit trail feature ensures accountability. Perfect for hospital administration.",
            author: "Admin Team",
            role: "City Hospital",
            rating: 5
        }
    ];

    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-primary/10 via-secondary/10 to-accent/10">
                {/* Animated Background */}
                <div className="absolute inset-0 overflow-hidden">
                    <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/20 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary/20 rounded-full blur-3xl animate-pulse [animation-delay:1s]"></div>
                </div>

                <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <motion.div {...fadeIn}>
                        <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
                            PrismCare
                        </h1>
                        <p className="text-2xl md:text-3xl font-semibold text-slate-800 mb-4">
                            Your Personal AI Medical Validator
                        </p>
                        <p className="text-lg md:text-xl text-slate-600 mb-12 max-w-2xl mx-auto">
                            Multi-View Transparency in Digital Health. Ensuring medication safety with AI-powered insights tailored for everyone.
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Link to="/patient">
                                <Button size="lg" className="w-full sm:w-auto">
                                    Login as Patient
                                    <ArrowRight className="ml-2 h-5 w-5" />
                                </Button>
                            </Link>
                            <Link to="/doctor">
                                <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                                    Login as Doctor
                                    <ArrowRight className="ml-2 h-5 w-5" />
                                </Button>
                            </Link>
                        </div>
                    </motion.div>

                    {/* Scroll Indicator */}
                    <motion.div
                        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
                        animate={{ y: [0, 10, 0] }}
                        transition={{ repeat: Infinity, duration: 2 }}
                    >
                        <ChevronDown className="h-8 w-8 text-slate-400" />
                    </motion.div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-20 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-slate-900 mb-4">Powerful Features for Every User</h2>
                        <p className="text-xl text-slate-600">One platform, three perspectives, complete transparency</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {features.map((feature, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.2 }}
                                viewport={{ once: true }}
                            >
                                <Card variant="interactive" className="h-full text-center">
                                    <div className="flex justify-center mb-4">{feature.icon}</div>
                                    <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                                    <p className="text-slate-600">{feature.description}</p>
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="py-20 bg-slate-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-slate-900 mb-4">How It Works</h2>
                        <p className="text-xl text-slate-600">Simple, fast, and reliable</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {steps.map((step, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, x: -20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.2 }}
                                viewport={{ once: true }}
                                className="relative"
                            >
                                <div className="flex items-start space-x-4">
                                    <div className="flex-shrink-0">
                                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-2xl font-bold">
                                            {step.number}
                                        </div>
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-slate-900 mb-2">{step.title}</h3>
                                        <p className="text-slate-600">{step.desc}</p>
                                    </div>
                                </div>
                                {index < steps.length - 1 && (
                                    <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-primary to-secondary transform -translate-x-1/2"></div>
                                )}
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Statistics */}
            <section className="py-20 bg-gradient-to-br from-primary to-secondary text-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid md:grid-cols-3 gap-8 text-center">
                        {stats.map((stat, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, scale: 0.8 }}
                                whileInView={{ opacity: 1, scale: 1 }}
                                transition={{ delay: index * 0.1 }}
                                viewport={{ once: true }}
                            >
                                <div className="text-5xl font-bold mb-2">{stat.value}</div>
                                <div className="text-xl opacity-90">{stat.label}</div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Testimonials */}
            <section className="py-20 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-slate-900 mb-4">Trusted by Healthcare Professionals</h2>
                        <p className="text-xl text-slate-600">See what our users have to say</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {testimonials.map((testimonial, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.2 }}
                                viewport={{ once: true }}
                            >
                                <Card className="h-full">
                                    <div className="flex mb-4">
                                        {[...Array(testimonial.rating)].map((_, i) => (
                                            <Star key={i} className="h-5 w-5 text-warning fill-warning" />
                                        ))}
                                    </div>
                                    <p className="text-slate-700 mb-6 italic">"{testimonial.quote}"</p>
                                    <div>
                                        <div className="font-semibold text-slate-900">{testimonial.author}</div>
                                        <div className="text-sm text-slate-600">{testimonial.role}</div>
                                    </div>
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Final CTA */}
            <section className="py-20 bg-slate-900 text-white">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h2 className="text-4xl font-bold mb-6">Ready to Ensure Medication Safety?</h2>
                    <p className="text-xl text-slate-300 mb-8">
                        Join thousands of patients and doctors using PrismCare for safer prescriptions.
                    </p>
                    <Link to="/patient">
                        <Button size="lg" className="bg-white text-primary hover:bg-slate-100">
                            Get Started Now
                            <ArrowRight className="ml-2 h-5 w-5" />
                        </Button>
                    </Link>
                </div>
            </section>
        </div>
    );
}
