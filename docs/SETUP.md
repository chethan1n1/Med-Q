# 🚀 Setup Instructions

## Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL
- OpenAI API Key

## Environment Setup

### 1. Clone and Setup
```bash
git clone <your-repo>
cd medq-app
```

### 2. Backend Setup
```bash
cd server
cp .env.example .env
# Edit .env with your database and OpenAI credentials

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd client
cp .env.example .env
# Edit .env if needed

# Install dependencies
npm install

# Run the development server
npm run dev
```

### 4. Database Setup
```bash
# Create PostgreSQL database
createdb medq_db

# The tables will be created automatically when you start the FastAPI server
```

### 5. Create Admin User
```bash
# Visit http://localhost:8000/api/auth/create-admin in your browser
# This creates admin user: username=admin, password=admin123
```

## Docker Setup (Alternative)

```bash
# Copy environment files
cp server/.env.example server/.env
cp client/.env.example client/.env

# Edit the .env files with your credentials

# Run with Docker Compose
docker-compose up --build
```

## Usage

1. **Patient Flow:**
   - Visit http://localhost:3000
   - Click "Start with Voice" or "Start with Text"
   - Complete the AI-guided intake process
   - Review and submit the generated summary

2. **Doctor Dashboard:**
   - Login at http://localhost:3000/login
   - Use admin/admin123 credentials
   - View patient summaries and analytics

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Key Features Implemented

✅ **Frontend:**
- React + TypeScript + Tailwind CSS
- Voice recording with Web API
- Chat-style intake interface
- AI-generated summary display
- Responsive design

✅ **Backend:**
- FastAPI with async support
- OpenAI GPT-4 integration
- OpenAI Whisper for voice transcription
- PostgreSQL database
- JWT authentication
- PDF export functionality

✅ **AI Features:**
- Voice-to-text transcription
- Intelligent conversation flow
- Medical data extraction
- Structured summary generation
- ICD code suggestions

## Production Deployment

### Frontend (Vercel)
```bash
cd client
npm run build
# Deploy to Vercel
```

### Backend (Railway/Render)
```bash
# Set environment variables in your hosting platform
# Deploy from the server directory
```

### Database (Supabase/Neon)
- Create a PostgreSQL database
- Update DATABASE_URL in production environment

## Security Considerations

- Change default SECRET_KEY in production
- Use environment variables for sensitive data
- Implement rate limiting for API endpoints
- Add input validation and sanitization
- Use HTTPS in production

## Future Enhancements

- Multi-language support
- Real-time notifications
- Advanced analytics
- Integration with EHR systems
- Mobile app development
- Telemedicine integration
