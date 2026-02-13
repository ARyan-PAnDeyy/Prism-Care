import { Link } from 'react-router-dom';
import { Heart, Mail, Phone, MapPin, Github, Linkedin, Twitter } from 'lucide-react';

export default function Footer() {
    return (
        <footer className="bg-slate-900 text-slate-300">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* Brand */}
                    <div className="space-y-4">
                        <div className="flex items-center space-x-2">
                            <Heart className="h-8 w-8 text-primary fill-primary" />
                            <span className="text-xl font-bold text-white">PrismCare</span>
                        </div>
                        <p className="text-sm text-slate-400">
                            Multi-View Transparency in Digital Health. AI-powered medication safety for everyone.
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h3 className="text-white font-semibold mb-4">Quick Links</h3>
                        <ul className="space-y-2">
                            <li><Link to="/about" className="text-sm hover:text-primary transition-colors">About</Link></li>
                            <li><Link to="/features" className="text-sm hover:text-primary transition-colors">Features</Link></li>
                            <li><Link to="/" className="text-sm hover:text-primary transition-colors">Privacy Policy</Link></li>
                            <li><Link to="/" className="text-sm hover:text-primary transition-colors">Terms of Service</Link></li>
                        </ul>
                    </div>

                    {/* Resources */}
                    <div>
                        <h3 className="text-white font-semibold mb-4">Resources</h3>
                        <ul className="space-y-2">
                            <li><Link to="/" className="text-sm hover:text-primary transition-colors">Documentation</Link></li>
                            <li><Link to="/" className="text-sm hover:text-primary transition-colors">API Reference</Link></li>
                            <li><Link to="/contact" className="text-sm hover:text-primary transition-colors">Support</Link></li>
                            <li><Link to="/contact" className="text-sm hover:text-primary transition-colors">FAQ</Link></li>
                        </ul>
                    </div>

                    {/* Contact */}
                    <div>
                        <h3 className="text-white font-semibold mb-4">Connect</h3>
                        <ul className="space-y-3">
                            <li className="flex items-center space-x-2 text-sm">
                                <Mail className="h-4 w-4" />
                                <span>prismcare@health.edu</span>
                            </li>
                            <li className="flex items-center space-x-2 text-sm">
                                <Phone className="h-4 w-4" />
                                <span>+91 XXXXX XXXXX</span>
                            </li>
                            <li className="flex items-center space-x-2 text-sm">
                                <MapPin className="h-4 w-4" />
                                <span>University Campus</span>
                            </li>
                        </ul>
                        <div className="flex space-x-4 mt-4">
                            <a href="#" className="hover:text-primary transition-colors">
                                <Github className="h-5 w-5" />
                            </a>
                            <a href="#" className="hover:text-primary transition-colors">
                                <Linkedin className="h-5 w-5" />
                            </a>
                            <a href="#" className="hover:text-primary transition-colors">
                                <Twitter className="h-5 w-5" />
                            </a>
                        </div>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="border-t border-slate-800 mt-8 pt-8 text-center text-sm text-slate-400">
                    <p>© 2026 PrismCare. All rights reserved. | Made with ❤️ for healthcare</p>
                </div>
            </div>
        </footer>
    );
}
