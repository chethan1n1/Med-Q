# MedQ - AI-Powered Medical Intake Assistant

A comprehensive full-stack AI-powered system for smart clinics that enables patients to submit symptoms via voice or text, generating structured medical summaries for healthcare providers.

## 🎯 Overview

MedQ revolutionizes the medical intake process by leveraging AI to:
- **Streamline Patient Communication**: Voice and text-based symptom collection
- **Generate Intelligent Summaries**: AI-powered medical analysis and structuring
- **Enhance Doctor Efficiency**: Pre-processed patient information with recommendations
- **Improve Patient Experience**: Natural conversation flow with AI assistant

## 🏗️ Architecture

- **Frontend**: React 18 + TypeScript + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + Python 3.11 + SQLAlchemy
- **Database**: PostgreSQL with structured medical data schema
- **AI**: OpenAI GPT-4 for analysis + Whisper for voice transcription
- **Authentication**: JWT-based secure login system
- **Deployment**: Docker containerization ready

## 📁 Project Structure

```
medq-app/
├── client/                 # React Frontend Application
│   ├── src/
│   │   ├── components/     # Reusable UI components (Shadcn/UI)
│   │   ├── pages/          # Page components (Welcome, Intake, Summary, Dashboard)
│   │   ├── services/       # API communication layer
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Helper functions and utilities
│   ├── public/             # Static assets
│   ├── package.json        # Dependencies and scripts
│   └── Dockerfile          # Container configuration
├── server/                 # FastAPI Backend API
│   ├── app/
│   │   ├── routes/         # API endpoints (intake, patients, auth, analytics)
│   │   ├── services/       # Business logic (AI, voice processing)
│   │   ├── models/         # Database models and Pydantic schemas
│   │   ├── utils/          # Configuration and helpers
│   │   └── main.py         # FastAPI application entry point
│   ├── tests/              # Unit and integration tests
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Container configuration
│   └── .env.example        # Environment variables template
├── docs/                   # Comprehensive documentation
│   ├── SETUP.md           # Setup and installation guide
│   └── API.md             # API documentation
├── docker-compose.yml      # Multi-container development setup
└── README.md              # This file
```

## 🚀 Quick Start

### Method 1: Docker (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd medq-app

# Set up environment variables
cp server/.env.example server/.env
cp client/.env.example client/.env
# Edit .env files with your OpenAI API key and database credentials

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Method 2: Manual Setup

#### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL 15+
- OpenAI API Key

#### Backend Setup
```bash
cd server
cp .env.example .env
# Edit .env with your credentials

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd client
cp .env.example .env

# Install dependencies
npm install

# Start development server
npm run dev
```

#### Database Setup
```bash
# Create PostgreSQL database
createdb medq_db

# Tables are created automatically on first run
```

#### Create Admin User
```bash
# Visit http://localhost:8000/api/auth/create-admin
# Creates: username=admin, password=admin123
```

## 📊 Core Features

### 🎤 Intelligent Patient Intake
- **Voice Input**: Real-time speech-to-text using OpenAI Whisper
- **Text Chat**: Natural language conversation with AI assistant
- **Smart Data Extraction**: Automatic parsing of medical information
- **Progressive Form**: Step-by-step guided intake process

### 🧠 AI-Powered Analysis
- **Symptom Analysis**: GPT-4 powered medical understanding
- **Severity Assessment**: Automatic classification (mild/moderate/severe)
- **ICD Code Suggestions**: Preliminary diagnostic code recommendations
- **Structured Summaries**: Organized medical data for healthcare providers

### 👨‍⚕️ Healthcare Provider Dashboard
- **Patient Management**: Complete patient history and summaries
- **Real-time Analytics**: Dashboard with patient trends and statistics
- **PDF Export**: Professional medical reports generation
- **Search & Filter**: Advanced patient search capabilities

### 📈 Administrative Features
- **Usage Analytics**: Patient volume, symptom trends, consultation metrics
- **Data Export**: CSV/PDF export for reporting and analysis
- **User Management**: Role-based access control (doctor/admin)
- **System Monitoring**: Health checks and performance metrics

## 🔧 Configuration

### Environment Variables

**Server (.env)**
```env
DATABASE_URL=postgresql://username:password@localhost/medq_db
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your-super-secret-jwt-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
```

**Client (.env)**
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=MedQ
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based user authentication
- **Password Hashing**: bcrypt encryption for user passwords
- **CORS Protection**: Configurable cross-origin resource sharing
- **Input Validation**: Comprehensive request validation with Pydantic
- **Environment Isolation**: Secure credential management
- **Role-based Access**: Differentiated permissions for doctors/admins

## 🧪 Testing

```bash
# Backend tests
cd server
pytest tests/

# Frontend tests (when implemented)
cd client
npm test
```

## 📚 API Documentation

- **Interactive Docs**: Visit http://localhost:8000/docs (Swagger UI)
- **API Reference**: See [docs/API.md](docs/API.md)
- **Setup Guide**: See [docs/SETUP.md](docs/SETUP.md)

## 🚀 Deployment

### Production Deployment Options

#### Frontend (Vercel/Netlify)
```bash
cd client
npm run build
# Deploy dist/ directory
```

#### Backend (Railway/Render/AWS)
```bash
# Set production environment variables
# Deploy from server/ directory
```

#### Database (Supabase/Neon/AWS RDS)
- Create PostgreSQL instance
- Update DATABASE_URL in production

## 🛣️ Future Roadmap

### Phase 2 Enhancements
- [ ] **Multi-language Support**: Spanish, Hindi, Chinese
- [ ] **Mobile App**: React Native implementation
- [ ] **EHR Integration**: HL7 FHIR compatibility
- [ ] **Telemedicine**: Video consultation integration
- [ ] **Advanced AI**: Specialized medical models

### Phase 3 Features
- [ ] **Wearable Integration**: Health data from devices
- [ ] **Prescription Management**: Digital prescriptions
- [ ] **Appointment Scheduling**: Integrated booking system
- [ ] **Insurance Processing**: Claims integration
- [ ] **Clinical Decision Support**: Treatment recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💡 Technical Highlights

- **Async FastAPI**: High-performance async Python backend
- **Type Safety**: Full TypeScript coverage on frontend
- **Modern UI**: Shadcn/UI components with Tailwind CSS
- **Real-time Processing**: WebSocket support for live interactions
- **Scalable Architecture**: Microservices-ready design
- **Production Ready**: Docker containerization and CI/CD ready

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check existing documentation
- Review API documentation at `/docs`

---

**Built with ❤️ for the healthcare community**
