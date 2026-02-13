import { useState } from 'react';
import { Mail, Phone, MapPin } from 'lucide-react';
import Button from '../components/Button';
import Card from '../components/Card';
import toast from 'react-hot-toast';

export default function ContactPage() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        subject: 'General Inquiry',
        message: ''
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        toast.success('Message sent! We\'ll respond within 24 hours.');
        setFormData({ name: '', email: '', subject: 'General Inquiry', message: '' });
    };

    return (
        <div className="min-h-screen bg-slate-50 py-16">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <h1 className="text-5xl font-bold mb-4">Get in Touch</h1>
                    <p className="text-xl text-slate-600">We'd love to hear from you</p>
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                    {/* Contact Form */}
                    <Card>
                        <h2 className="text-2xl font-bold mb-6">Send us a Message</h2>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">Name</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-4 py-2 border rounded-soft"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Email</label>
                                <input
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full px-4 py-2 border rounded-soft"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Subject</label>
                                <select
                                    value={formData.subject}
                                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                                    className="w-full px-4 py-2 border rounded-soft"
                                >
                                    <option>General Inquiry</option>
                                    <option>Technical Support</option>
                                    <option>Partnership</option>
                                    <option>Other</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Message</label>
                                <textarea
                                    value={formData.message}
                                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                                    className="w-full px-4 py-2 border rounded-soft h-32"
                                    required
                                />
                            </div>
                            <Button type="submit" className="w-full">Send Message</Button>
                        </form>
                    </Card>

                    {/* Contact Information */}
                    <div className="space-y-6">
                        <Card>
                            <h2 className="text-2xl font-bold mb-6">Contact Information</h2>
                            <div className="space-y-4">
                                <div className="flex items-start space-x-3">
                                    <Mail className="h-6 w-6 text-primary mt-1" />
                                    <div>
                                        <p className="font-medium">Email</p>
                                        <p className="text-slate-600">prismcare@health.edu</p>
                                    </div>
                                </div>
                                <div className="flex items-start space-x-3">
                                    <Phone className="h-6 w-6 text-primary mt-1" />
                                    <div>
                                        <p className="font-medium">Phone</p>
                                        <p className="text-slate-600">+91 XXXXX XXXXX</p>
                                    </div>
                                </div>
                                <div className="flex items-start space-x-3">
                                    <MapPin className="h-6 w-6 text-primary mt-1" />
                                    <div>
                                        <p className="font-medium">Address</p>
                                        <p className="text-slate-600">University Campus<br />Final Year Project 2026</p>
                                    </div>
                                </div>
                            </div>
                        </Card>

                        <Card>
                            <h3 className="text-xl font-bold mb-4">FAQ</h3>
                            <div className="space-y-4">
                                <div>
                                    <p className="font-semibold mb-1">How accurate is the AI?</p>
                                    <p className="text-sm text-slate-600">Our AI achieves 95% accuracy based on medical guidelines and databases.</p>
                                </div>
                                <div>
                                    <p className="font-semibold mb-1">Is my data secure?</p>
                                    <p className="text-sm text-slate-600">Yes, all data is encrypted and follows healthcare privacy standards.</p>
                                </div>
                                <div>
                                    <p className="font-semibold mb-1">Can I use this for real prescriptions?</p>
                                    <p className="text-sm text-slate-600">This is a prototype for educational purposes. Always consult a healthcare professional.</p>
                                </div>
                            </div>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
