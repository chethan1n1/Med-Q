export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  symptoms: string;
  duration: string;
  allergies: string;
  medications: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  isVoice?: boolean;
  isEmergency?: boolean;
}

export interface IntakeData {
  name?: string;
  age?: number;
  gender?: 'male' | 'female' | 'other' | '';
  symptoms?: string;
  duration?: string;
  allergies?: string;
  medications?: string;
  current_step: IntakeStep;
}

export type IntakeStep = 
  | 'name'
  | 'age'
  | 'gender'
  | 'symptoms'
  | 'duration'
  | 'medications'
  | 'allergies'
  | 'summary'
  | 'complete';

export interface MedicalSummary {
  id: string;
  patient_id: string;
  summary_text: string;
  structured_data: {
    chief_complaint: string;
    symptoms: string[];
    duration: string;
    severity: 'mild' | 'moderate' | 'severe';
    associated_symptoms: string[];
    medical_history: string;
    current_medications: string[];
    allergies: string[];
    recommendations: string[];
  };
  icd_codes?: string[];
  created_at: string;
}

export interface DoctorUser {
  id: string;
  username: string;
  email: string;
  role: 'doctor' | 'admin';
  created_at: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: DoctorUser | null;
  token: string | null;
}

export interface VoiceRecording {
  blob: Blob;
  duration: number;
  timestamp: Date;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface TextProcessResponse {
  response: string;
  extracted_data: Partial<IntakeData>;
  next_step: string;
  is_emergency?: boolean;
}

export interface VoiceTranscriptResponse {
  transcript: string;
}

export interface MedicalSummaryResponse {
  summary_text: string;
  structured_data: any;
}
