import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "MedQ API" in response.json()["message"]

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_patient():
    """Test patient creation"""
    patient_data = {
        "name": "John Doe",
        "age": 30,
        "gender": "male",
        "symptoms": "Headache and fever",
        "duration": "2 days",
        "allergies": "None",
        "medications": "Ibuprofen"
    }
    
    response = client.post("/api/patients/", json=patient_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "John Doe"

def test_get_patients():
    """Test getting patients list"""
    response = client.get("/api/patients/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

@pytest.fixture
def auth_headers():
    """Create authenticated user for testing"""
    # Create admin user first
    client.post("/api/auth/create-admin")
    
    # Login
    login_data = {"username": "admin", "password": "admin123"}
    response = client.post("/api/auth/login", json=login_data)
    token = response.json()["data"]["token"]
    
    return {"Authorization": f"Bearer {token}"}

def test_dashboard_stats(auth_headers):
    """Test dashboard analytics"""
    response = client.get("/api/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_patients" in data["data"]
