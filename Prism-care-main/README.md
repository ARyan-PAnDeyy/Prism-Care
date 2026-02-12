# PrismCare - AI Medical Validator

**Multi-View Transparency in Digital Health**

A comprehensive healthcare AI platform for drug interaction analysis with tailored views for patients, doctors, and administrators.

This is the rough sketch of project and still under development....contributors and interested parties are invited to contribute in it.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (for backend)
- Node.js 18+ (for frontend)
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start Mock ABDM Server (Terminal 1)
python mock_abdm_server.py
# Server runs on http://localhost:8080

# Start Main API Server (Terminal 2)
python app.py
# Server runs on http://localhost:5000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# App runs on http://localhost:5173
```

---

## 📋 Testing the Application

### Sample ABHA IDs
- **ABHA001**: Rajesh Kumar (58M) - on Warfarin + Metformin
- **ABHA002**: Priya Sharma (42F) - on Lisinopril + Atorvastatin
- **ABHA003**: Mohammed Ali (35M) - previous Ibuprofen use

### Test Scenarios

#### Patient Flow
1. Go to `http://localhost:5173/patient`
2. Login with ABHA ID: `ABHA001`
3. Enter medicine: `Aspirin`
4. Click "Check Safety"
5. **Expected**: Red warning (Aspirin + Warfarin = bleeding risk)

#### Doctor Flow
1. Go to `http://localhost:5173/doctor`
2. Load patient: `ABHA002`
3. Enter medicine: `Ibuprofen`
4. Click "Analyze Prescription"
5. **Expected**: Clinical explanation with override option

#### Admin Flow
1. Go to `http://localhost:5173/admin`
2. **Expected**: Dashboard with statistics and override logs

---

## 🏗️ Project Structure

```
Project/
├── backend/
│   ├── mock_abdm_server.py    # Government health records simulator
│   ├── ai_engine.py            # Drug interaction AI (ChromaDB + RAG)
│   ├── app.py                  # Main Flask API
│   └── requirements.txt        # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/         # Reusable UI components
    │   │   ├── Navbar.jsx
    │   │   ├── Footer.jsx
    │   │   ├── Button.jsx
    │   │   ├── Card.jsx
    │   │   ├── Modal.jsx
    │   │   └── LoadingSpinner.jsx
    │   │
    │   ├── pages/              # Main application pages
    │   │   ├── LandingPage.jsx
    │   │   ├── PatientDashboard.jsx
    │   │   ├── DoctorDashboard.jsx
    │   │   ├── AdminDashboard.jsx
    │   │   ├── AboutPage.jsx
    │   │   ├── FeaturesPage.jsx
    │   │   └── ContactPage.jsx
    │   │
    │   ├── App.jsx              # Main router
    │   ├── main.jsx             # Entry point
    │   └── index.css            # Tailwind styles
    │
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

---

## 🎯 Key Features

### For Patients
- ✅ Simple, jargon-free explanations
- ✅ Traffic light visual system (Green = Safe, Red = Risky)
- ✅ Medication history tracking
- ✅ Instant safety checks

### For Doctors
- ✅ Clinical-grade analysis with mechanisms
- ✅ Evidence-based recommendations
- ✅ Override capability with audit trail
- ✅ Source citations (FDA, AHA guidelines)

### For Administrators
- ✅ Real-time analytics dashboard
- ✅ Override monitoring
- ✅ System health metrics
- ✅ Export capabilities

---

## 🧠 Technology Stack

**Backend**:
- Python 3.x
- Flask (REST API)
- ChromaDB (Vector Database)
- LangChain (RAG Framework)

**Frontend**:
- React 18
- Vite (Build Tool)
- Tailwind CSS (Styling)
- Framer Motion (Animations)
- Recharts (Analytics)
- React Router (Navigation)
- Axios (HTTP Client)

---

## 📊 API Endpoints

### Backend API (Port 5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | Patient/doctor authentication |
| POST | `/api/validate` | Drug interaction analysis |
| POST | `/api/admin/override` | Log doctor override |
| GET | `/api/admin/stats` | System statistics |
| GET | `/api/admin/overrides` | Override logs (paginated) |

### Mock ABDM Server (Port 8080)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/fhir/Patient?identifier={id}` | Patient demographics |
| GET | `/fhir/MedicationRequest?patient={id}` | Medication history |

---

## 🔬 Drug Interaction Rules

The AI engine includes 5 pre-loaded interaction rules:

1. **Aspirin + Warfarin** → High bleeding risk
2. **Ibuprofen + Aspirin** → GI issues, reduced cardioprotection
3. **Metformin + Alcohol** → Lactic acidosis risk
4. **Lisinopril + Potassium** → Hyperkalemia
5. **Atorvastatin + Grapefruit** → Increased statin levels

---

## 🎨 Design System

**Colors**:
- Primary (Teal): `#14B8A6` - Trust, healthcare
- Secondary (Indigo): `#6366F1` - Technology, AI
- Accent (Emerald): `#10B981` - Safety, success
- Warning (Amber): `#F59E0B` - Caution
- Danger (Rose): `#F43F5E` - Risk

**Typography**: Inter (Google Fonts)

**Spacing**: 8px grid system

---

## 🚧 Future Enhancements

See [frontend_enhancements.md](../brain/a2b3d02b-29cd-43c4-85cb-99307a3f2a62/frontend_enhancements.md) for detailed feature suggestions:

- Dark mode
- Voice input
- QR code scanner
- Real drug database integration
- PWA (offline capability)
- Multi-language support
- Predictive analytics

---

## License

This repository is under a proprietary license.

All rights are reserved. You may NOT:
- Copy, redistribute, or sublicense the code.
- Modify, adapt, or create derivative works.
- Use this code for commercial purposes.

Permission to use, modify, or redistribute this code may only be granted explicitly in writing by the copyright holder.

See the [LICENSE](./LICENSE) file for full details.

## 👥 Contact

For questions or feedback, visit the Contact page in the application.

---

## 🙏 Acknowledgments

- ABDM (Ayushman Bharat Digital Mission) for healthcare standards
- Medical guidelines from FDA, AHA, and Endocrine Society
- Open-source libraries: React, Flask, ChromaDB, Tailwind CSS

---

**Made with ❤️ for healthcare**
