from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from fastapi.responses import StreamingResponse

from app.models.database import get_db
from app.models.schemas import Patient, MedicalSummary
from app.models.pydantic_models import (
    PatientCreate, PatientResponse, MedicalSummaryResponse, APIResponse
)

router = APIRouter()

@router.get("/", response_model=APIResponse)
async def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all patients with pagination"""
    try:
        patients = db.query(Patient).offset(skip).limit(limit).all()
        patients_data = [PatientResponse.from_orm(patient) for patient in patients]
        
        return APIResponse(
            success=True,
            data=patients_data,
            message=f"Retrieved {len(patients_data)} patients"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patients: {str(e)}")

@router.get("/{patient_id}", response_model=APIResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific patient by ID"""
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return APIResponse(
            success=True,
            data=PatientResponse.from_orm(patient),
            message="Patient retrieved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient: {str(e)}")

@router.post("/", response_model=APIResponse)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db)
):
    """Create a new patient record"""
    try:
        # Create new patient
        db_patient = Patient(**patient_data.dict())
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        
        return APIResponse(
            success=True,
            data=PatientResponse.from_orm(db_patient),
            message="Patient created successfully"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating patient: {str(e)}")

@router.get("/{patient_id}/summary", response_model=APIResponse)
async def get_patient_summary(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Get medical summary for a specific patient"""
    try:
        # Check if patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get the latest summary
        summary = db.query(MedicalSummary).filter(
            MedicalSummary.patient_id == patient_id
        ).order_by(MedicalSummary.created_at.desc()).first()
        
        if not summary:
            raise HTTPException(status_code=404, detail="No summary found for this patient")
        
        return APIResponse(
            success=True,
            data=MedicalSummaryResponse.from_orm(summary),
            message="Summary retrieved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving summary: {str(e)}")

@router.get("/{patient_id}/export/pdf")
async def export_patient_pdf(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Export patient data as PDF"""
    try:
        # Get patient and summary
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        summary = db.query(MedicalSummary).filter(
            MedicalSummary.patient_id == patient_id
        ).order_by(MedicalSummary.created_at.desc()).first()
        
        # Create PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "MedQ - Medical Summary Report")
        
        # Patient Info
        y_position = height - 100
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Patient Information:")
        
        y_position -= 30
        p.setFont("Helvetica", 10)
        p.drawString(50, y_position, f"Name: {patient.name}")
        y_position -= 20
        p.drawString(50, y_position, f"Age: {patient.age}")
        y_position -= 20
        p.drawString(50, y_position, f"Gender: {patient.gender}")
        y_position -= 20
        p.drawString(50, y_position, f"Date: {patient.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Symptoms
        y_position -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Symptoms:")
        y_position -= 30
        p.setFont("Helvetica", 10)
        
        # Handle long text
        symptoms_lines = patient.symptoms.split('\n')
        for line in symptoms_lines:
            if y_position < 100:  # Start new page if needed
                p.showPage()
                y_position = height - 50
            p.drawString(50, y_position, line[:80])  # Truncate long lines
            y_position -= 15
        
        if summary:
            y_position -= 30
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y_position, "AI Summary:")
            y_position -= 30
            p.setFont("Helvetica", 10)
            
            summary_lines = summary.summary_text.split('\n')
            for line in summary_lines:
                if y_position < 100:
                    p.showPage()
                    y_position = height - 50
                p.drawString(50, y_position, line[:80])
                y_position -= 15
        
        p.save()
        buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=patient_{patient_id}_summary.pdf"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
