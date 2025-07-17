from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext

from app.models.database import get_db
from app.models.schemas import DoctorUser
from app.models.pydantic_models import (
    LoginRequest, Token, UserResponse, APIResponse
)
from app.utils.config import get_settings

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> DoctorUser:
    """Get current authenticated user"""
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = db.query(DoctorUser).filter(DoctorUser.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/login", response_model=APIResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    try:
        # Find user
        user = db.query(DoctorUser).filter(
            DoctorUser.username == login_data.username
        ).first()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return APIResponse(
            success=True,
            data={
                "token": access_token,
                "user": UserResponse.from_orm(user)
            },
            message="Login successful"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@router.get("/me", response_model=APIResponse)
async def get_current_user_info(
    current_user: DoctorUser = Depends(get_current_user)
):
    """Get current user information"""
    return APIResponse(
        success=True,
        data=UserResponse.from_orm(current_user),
        message="User information retrieved"
    )

@router.post("/create-admin")
async def create_admin_user(db: Session = Depends(get_db)):
    """Create default admin user (for development only)"""
    if settings.environment != "development":
        raise HTTPException(status_code=403, detail="Only available in development mode")
    
    try:
        # Check if admin already exists
        existing_admin = db.query(DoctorUser).filter(
            DoctorUser.username == "admin"
        ).first()
        
        if existing_admin:
            return {"message": "Admin user already exists"}
        
        # Create admin user
        admin_user = DoctorUser(
            username="admin",
            email="admin@medq.com",
            hashed_password=get_password_hash("admin123"),
            role="admin"
        )
        
        db.add(admin_user)
        db.commit()
        
        return {"message": "Admin user created successfully", "username": "admin", "password": "admin123"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating admin user: {str(e)}")

@router.post("/refresh", response_model=APIResponse)
async def refresh_token(
    current_user: DoctorUser = Depends(get_current_user)
):
    """Refresh access token for current user"""
    try:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": current_user.username}, expires_delta=access_token_expires
        )
        
        return APIResponse(
            success=True,
            data={"token": access_token},
            message="Token refreshed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh error: {str(e)}")

@router.post("/logout", response_model=APIResponse)
async def logout():
    """Logout user (client-side token removal)"""
    return APIResponse(
        success=True,
        message="Logged out successfully"
    )

@router.get("/verify", response_model=APIResponse)
async def verify_token(
    current_user: DoctorUser = Depends(get_current_user)
):
    """Verify if the current token is valid"""
    return APIResponse(
        success=True,
        data=UserResponse.from_orm(current_user),
        message="Token is valid"
    )
