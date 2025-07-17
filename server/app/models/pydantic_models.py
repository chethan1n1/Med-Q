from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class Severity(str, Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"

class IntakeStep(str, Enum):
    name = "name"
    age = "age"
    gender = "gender"
    symptoms = "symptoms"
    duration = "duration"
    medications = "medications"
    allergies = "allergies"
    summary = "summary"
    complete = "complete"

# Patient Schemas
class PatientBase(BaseModel):
    name: str
    age: int
    gender: Gender
    symptoms: str
    duration: str
    allergies: Optional[str] = None
    medications: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Intake Schemas
class IntakeData(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None  # Changed from Gender enum to str to handle empty strings
    symptoms: Optional[str] = None
    duration: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    current_step: IntakeStep

class TextProcessRequest(BaseModel):
    message: str
    current_data: IntakeData

class TextProcessResponse(BaseModel):
    response: str
    extracted_data: Dict[str, Any]
    next_step: str

class VoiceTranscriptResponse(BaseModel):
    transcript: str

# Medical Summary Schemas
class StructuredData(BaseModel):
    chief_complaint: str
    symptoms: List[str]
    duration: str
    severity: Severity
    associated_symptoms: List[str]
    medical_history: str
    current_medications: List[str]
    allergies: List[str]
    recommendations: List[str]

class MedicalSummaryBase(BaseModel):
    summary_text: str
    structured_data: StructuredData
    icd_codes: Optional[List[str]] = None

class MedicalSummaryCreate(MedicalSummaryBase):
    patient_id: int

class MedicalSummaryResponse(MedicalSummaryBase):
    id: int
    patient_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth Schemas
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Analytics Schemas
class DashboardStats(BaseModel):
    total_patients: int
    today_patients: int
    avg_consultation_time: float
    top_symptoms: List[Dict[str, Any]]
    patients_by_date: List[Dict[str, Any]]

# API Response Wrapper
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
