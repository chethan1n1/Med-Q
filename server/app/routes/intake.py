from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models.database import get_db
from app.models.pydantic_models import (
    TextProcessRequest, TextProcessResponse, VoiceTranscriptResponse,
    IntakeData, APIResponse
)
from app.services.ai_service import AIService
from app.services.voice_service import VoiceService
from pydantic import BaseModel
from typing import List, Optional

class MedicalConversationRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None

class MedicalConversationResponse(BaseModel):
    response: str
    is_emergency: bool
    requires_followup: bool
    conversation_complete: bool

router = APIRouter()

@router.post("/voice", response_model=APIResponse)
async def process_voice(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Process voice input and return transcript"""
    try:
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Read audio file
        audio_data = await audio.read()
        
        # Transcribe using OpenAI Whisper
        voice_service = VoiceService()
        transcript = await voice_service.transcribe_audio(audio_data)
        
        return APIResponse(
            success=True,
            data=VoiceTranscriptResponse(transcript=transcript),
            message="Audio transcribed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing voice: {str(e)}")

@router.post("/text", response_model=APIResponse)
async def process_text(
    request: TextProcessRequest,
    db: Session = Depends(get_db)
):
    """Process text input and extract medical information"""
    try:
        ai_service = AIService()
        
        # Process the message and extract data
        response_data = await ai_service.process_intake_message(
            message=request.message,
            current_data=request.current_data
        )
        
        return APIResponse(
            success=True,
            data=response_data,
            message="Text processed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@router.post("/summarize", response_model=APIResponse)
async def generate_summary(
    intake_data: IntakeData,
    db: Session = Depends(get_db)
):
    """Generate AI medical summary from intake data"""
    try:
        ai_service = AIService()
        
        # Generate comprehensive medical summary
        summary = await ai_service.generate_medical_summary(intake_data)
        
        return APIResponse(
            success=True,
            data=summary,
            message="Medical summary generated successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@router.post("/medical-chat", response_model=APIResponse)
async def medical_conversation(
    request: MedicalConversationRequest,
    db: Session = Depends(get_db)
):
    """
    Handle intelligent medical conversation using the compassionate AI assistant.
    
    This endpoint provides empathetic, safety-aware medical assistance that:
    - Asks smart follow-up questions
    - Provides general wellness advice
    - Includes proper medical disclaimers
    - Handles emergency situations appropriately
    """
    try:
        ai_service = AIService()
        
        # Process the medical conversation
        response_data = await ai_service.intelligent_medical_conversation(
            user_message=request.message,
            conversation_history=request.conversation_history
        )
        
        return APIResponse(
            success=True,
            data=MedicalConversationResponse(**response_data),
            message="Medical conversation processed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in medical conversation: {str(e)}")
