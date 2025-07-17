import axios from 'axios';
import { Patient, MedicalSummary, IntakeData, APIResponse, DoctorUser } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('medq_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('medq_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const intakeService = {
  // Submit voice recording for transcription
  async submitVoice(audioBlob: Blob): Promise<APIResponse<{ transcript: string }>> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    const response = await api.post('/api/intake/voice', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Process text input and extract data
  async processText(message: string, currentData: IntakeData): Promise<APIResponse<{
    response: string;
    extracted_data: Partial<IntakeData>;
    next_step: string;
  }>> {
    const response = await api.post('/api/intake/text', {
      message,
      current_data: currentData,
    });
    return response.data;
  },

  // Generate medical summary
  async generateSummary(patientData: IntakeData): Promise<APIResponse<MedicalSummary>> {
    const response = await api.post('/api/intake/summarize', patientData);
    return response.data;
  },

  // Intelligent medical conversation
  async medicalChat(message: string, conversationHistory?: Array<{role: string, content: string}>): Promise<APIResponse<{
    response: string;
    is_emergency: boolean;
    requires_followup: boolean;
    conversation_complete: boolean;
  }>> {
    const response = await api.post('/api/intake/medical-chat', {
      message,
      conversation_history: conversationHistory,
    });
    return response.data;
  },

  // Submit final patient data
  async submitPatient(patientData: IntakeData): Promise<APIResponse<Patient>> {
    const response = await api.post('/api/patients', patientData);
    return response.data;
  },
};

export const patientService = {
  // Get all patients
  async getAll(): Promise<APIResponse<Patient[]>> {
    const response = await api.get('/api/patients');
    return response.data;
  },

  // Get patient by ID
  async getById(id: string): Promise<APIResponse<Patient>> {
    const response = await api.get(`/api/patients/${id}`);
    return response.data;
  },

  // Get patient's summary
  async getSummary(patientId: string): Promise<APIResponse<MedicalSummary>> {
    const response = await api.get(`/api/patients/${patientId}/summary`);
    return response.data;
  },

  // Export patient data as PDF
  async exportPDF(patientId: string): Promise<Blob> {
    const response = await api.get(`/api/export/pdf/${patientId}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export const authService = {
  // Login
  async login(username: string, password: string): Promise<APIResponse<{
    token: string;
    user: DoctorUser;
  }>> {
    const response = await api.post('/api/auth/login', {
      username,
      password,
    });
    return response.data;
  },

  // Get current user
  async getCurrentUser(): Promise<APIResponse<DoctorUser>> {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  // Logout
  async logout(): Promise<void> {
    localStorage.removeItem('medq_token');
  },
};

export const analyticsService = {
  // Get dashboard analytics
  async getDashboardStats(): Promise<APIResponse<{
    total_patients: number;
    today_patients: number;
    avg_consultation_time: number;
    top_symptoms: Array<{ symptom: string; count: number }>;
    patients_by_date: Array<{ date: string; count: number }>;
  }>> {
    const response = await api.get('/api/analytics/dashboard');
    return response.data;
  },

  // Export analytics data
  async exportCSV(startDate?: string, endDate?: string): Promise<Blob> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/api/analytics/export?${params}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export default api;
