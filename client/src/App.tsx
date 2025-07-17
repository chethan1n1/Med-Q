import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import WelcomePage from './pages/WelcomePage';
import ChatIntakePage from './pages/ChatIntakePage';
import SummaryPage from './pages/SummaryPage';
import DoctorDashboard from './pages/DoctorDashboard';
import AdminPanel from './pages/AdminPanel';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<WelcomePage />} />
          <Route path="/intake/:mode" element={<ChatIntakePage />} />
          <Route path="/summary" element={<SummaryPage />} />
          <Route path="/dashboard" element={<DoctorDashboard />} />
          <Route path="/admin" element={<AdminPanel />} />
          
          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
