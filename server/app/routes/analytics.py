from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import csv
import io
from fastapi.responses import StreamingResponse

from app.models.database import get_db
from app.models.schemas import Patient, MedicalSummary
from app.models.pydantic_models import DashboardStats, APIResponse
from app.routes.auth import get_current_user

router = APIRouter()

@router.get("/dashboard", response_model=APIResponse)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard analytics and statistics"""
    try:
        # Total patients
        total_patients = db.query(Patient).count()
        
        # Today's patients
        today = datetime.now().date()
        today_patients = db.query(Patient).filter(
            func.date(Patient.created_at) == today
        ).count()
        
        # Average consultation time (mock data for now)
        avg_consultation_time = 25.5  # minutes
        
        # Top symptoms (analyze symptoms text)
        symptoms_query = db.query(Patient.symptoms).all()
        symptom_counts = {}
        
        for (symptoms_text,) in symptoms_query:
            if symptoms_text:
                # Simple keyword extraction (in production, use more sophisticated NLP)
                words = symptoms_text.lower().split()
                common_symptoms = ['headache', 'fever', 'cough', 'pain', 'nausea', 'fatigue', 'dizziness']
                for symptom in common_symptoms:
                    if symptom in ' '.join(words):
                        symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
        
        top_symptoms = [
            {"symptom": symptom, "count": count} 
            for symptom, count in sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Patients by date (last 7 days)
        patients_by_date = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).date()
            count = db.query(Patient).filter(
                func.date(Patient.created_at) == date
            ).count()
            patients_by_date.append({
                "date": date.isoformat(),
                "count": count
            })
        
        stats = DashboardStats(
            total_patients=total_patients,
            today_patients=today_patients,
            avg_consultation_time=avg_consultation_time,
            top_symptoms=top_symptoms,
            patients_by_date=list(reversed(patients_by_date))
        )
        
        return APIResponse(
            success=True,
            data=stats.dict(),
            message="Dashboard statistics retrieved successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard stats: {str(e)}")

@router.get("/export")
async def export_analytics_csv(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export analytics data as CSV"""
    try:
        # Build query
        query = db.query(Patient)
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Patient.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Patient.created_at <= end_dt)
        
        patients = query.all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "ID", "Name", "Age", "Gender", "Symptoms", "Duration",
            "Medications", "Allergies", "Created At"
        ])
        
        # Data rows
        for patient in patients:
            writer.writerow([
                patient.id,
                patient.name,
                patient.age,
                patient.gender,
                patient.symptoms[:100] + "..." if len(patient.symptoms) > 100 else patient.symptoms,
                patient.duration,
                patient.medications or "None",
                patient.allergies or "None",
                patient.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=medq_analytics_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")

@router.get("/symptoms/trends")
async def get_symptom_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get symptom trends over time"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # Get patients from the specified period
        patients = db.query(Patient).filter(
            Patient.created_at >= start_date
        ).all()
        
        # Analyze symptoms by day
        symptom_trends = {}
        common_symptoms = ['headache', 'fever', 'cough', 'pain', 'nausea', 'fatigue', 'dizziness']
        
        for patient in patients:
            if patient.symptoms:
                date_key = patient.created_at.date().isoformat()
                if date_key not in symptom_trends:
                    symptom_trends[date_key] = {}
                
                symptoms_text = patient.symptoms.lower()
                for symptom in common_symptoms:
                    if symptom in symptoms_text:
                        if symptom not in symptom_trends[date_key]:
                            symptom_trends[date_key][symptom] = 0
                        symptom_trends[date_key][symptom] += 1
        
        return APIResponse(
            success=True,
            data=symptom_trends,
            message="Symptom trends retrieved successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving symptom trends: {str(e)}")
