import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import PatientDashboard from './pages/PatientDashboard';
import DoctorDashboard from './pages/DoctorDashboard';
import AdminDashboard from './pages/AdminDashboard';
import AboutPage from './pages/AboutPage';
import FeaturesPage from './pages/FeaturesPage';
import ContactPage from './pages/ContactPage';

function App() {
    return (
        <BrowserRouter>
            <div className="flex flex-col min-h-screen">
                <Navbar />
                <main className="flex-grow">
                    <Routes>
                        <Route path="/" element={<LandingPage />} />
                        <Route path="/patient" element={<PatientDashboard />} />
                        <Route path="/doctor" element={<DoctorDashboard />} />
                        <Route path="/admin" element={<AdminDashboard />} />
                        <Route path="/about" element={<AboutPage />} />
                        <Route path="/features" element={<FeaturesPage />} />
                        <Route path="/contact" element={<ContactPage />} />
                    </Routes>
                </main>
                <Footer />
                <Toaster position="top-right" />
            </div>
        </BrowserRouter>
    );
}

export default App;
