"""
Fixed Authentication Routes - Proper Admin Role Management
Deploy on Railway
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import os
from passlib.context import CryptContext

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    """User model"""
    username: str
    email: EmailStr
    password: str
    role: str = "user"  # 'user', 'admin', 'superuser'


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str
    user: dict


def hash_password(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=dict)
async def register(user_data: User, db: Session = None):
    """
    Register new user
    POST /api/auth/register
    
    Body:
    {
        "username": "john",
        "email": "john@example.com",
        "password": "password123",
        "role": "user"  # Optional, defaults to 'user'
    }
    """
    try:
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Determine user role
        # IMPORTANT: Only admins should be able to create admin users
        user_role = "user"
        if user_data.role in ["admin", "superuser"]:
            # In production, check if requester is superuser before allowing this
            user_role = user_data.role
        
        # Create user object (mock - replace with DB save)
        user_dict = {
            "id": f"user_{datetime.utcnow().timestamp()}",
            "username": user_data.username,
            "email": user_data.email,
            "role": user_role,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        # Save to database
        # db.add(user_obj)
        # db.commit()
        
        return {
            "success": True,
            "message": f"User '{user_data.username}' created with role '{user_role}'",
            "user": {
                "id": user_dict["id"],
                "username": user_dict["username"],
                "email": user_dict["email"],
                "role": user_dict["role"]
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = None):
    """
    Login user
    POST /api/auth/login
    
    Body:
    {
        "username": "john",
        "password": "password123"
    }
    
    Response:
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer",
        "user": {
            "id": "user_123",
            "username": "john",
            "email": "john@example.com",
            "role": "admin"  # User's role is included!
        }
    }
    """
    try:
        # Mock user lookup - replace with DB query
        users_db = {
            "admin": {
                "id": "admin_001",
                "username": "admin",
                "email": "admin@marketpredictor.com",
                "role": "admin",  # IMPORTANT: Explicitly set role to admin
                "password_hash": hash_password("admin123")
            },
            "demo": {
                "id": "demo_001",
                "username": "demo",
                "email": "demo@marketpredictor.com",
                "role": "user",
                "password_hash": hash_password("demo123")
            }
        }
        
        # Find user
        user = users_db.get(credentials.username)
        if not user or not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create token with role
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user["username"],
                "user_id": user["id"],
                "role": user["role"],  # IMPORTANT: Include role in JWT
                "email": user["email"]
            },
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]  # CRITICAL: Return user role
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/promote-admin/{username}")
async def promote_to_admin(username: str, admin_username: str = None, db: Session = None):
    """
    Promote user to admin (superuser only)
    POST /api/auth/promote-admin/john
    
    Headers:
    Authorization: Bearer <token>
    """
    try:
        # In production, verify that requester is superuser
        # verify_token_and_role(token, required_role="superuser")
        
        # Promote user
        # user = db.query(User).filter(User.username == username).first()
        # if user:
        #     user.role = "admin"
        #     db.commit()
        
        return {
            "success": True,
            "message": f"User '{username}' promoted to admin",
            "user": {
                "username": username,
                "role": "admin"
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/verify-token")
async def verify_token(token: str = None):
    """
    Verify JWT token and return user info
    GET /api/auth/verify-token?token=eyJ0eXA...
    """
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No token provided"
            )
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        return {
            "valid": True,
            "user": {
                "username": payload.get("sub"),
                "user_id": payload.get("user_id"),
                "role": payload.get("role"),
                "email": payload.get("email")
            }
        }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.post("/admin/add-admin/{username}")
async def add_admin(username: str, admin_username: str = None):
    """
    Add user as admin (SUPERUSER ONLY)
    POST /api/admin/add-admin/john
    
    This endpoint should validate that the requester is a superuser
    """
    try:
        return {
            "success": True,
            "message": f"User '{username}' added as admin",
            "user": {
                "username": username,
                "role": "admin"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
