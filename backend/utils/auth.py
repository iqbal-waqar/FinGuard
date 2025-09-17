from datetime import datetime, timedelta
from typing import Optional
import os
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from backend.schemas.models import User, UserRole

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = None

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    test_hash = pwd_context.hash("test")
    pwd_context.verify("test", test_hash)
    print("bcrypt initialized successfully")
except Exception as e:
    print(f"Warning: bcrypt initialization failed: {e}")
    try:
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        print("Fallback to pbkdf2_sha256 successful")
    except Exception as e2:
        print(f"Warning: pbkdf2_sha256 fallback also failed: {e2}")
        pwd_context = None

security = HTTPBearer()

_USERS_DB_TEMPLATE = {
    "john_finance": {
        "username": "john_finance",
        "password": "finance123",
        "role": UserRole.FINANCE,
        "full_name": "John Smith",
        "email": "john@finguard.com"
    },
    "sarah_marketing": {
        "username": "sarah_marketing",
        "password": "marketing123",
        "role": UserRole.MARKETING,
        "full_name": "Sarah Johnson",
        "email": "sarah@finguard.com"
    },
    "mike_hr": {
        "username": "mike_hr",
        "password": "hr123",
        "role": UserRole.HR,
        "full_name": "Mike Wilson",
        "email": "mike@finguard.com"
    },
    "alex_engineering": {
        "username": "alex_engineering",
        "password": "engineering123",
        "role": UserRole.ENGINEERING,
        "full_name": "Alex Chen",
        "email": "alex@finguard.com"
    },
    "ceo": {
        "username": "ceo",
        "password": "ceo123",
        "role": UserRole.C_LEVEL,
        "full_name": "CEO Executive",
        "email": "ceo@finguard.com"
    },
    "employee": {
        "username": "employee",
        "password": "employee123",
        "role": UserRole.EMPLOYEE,
        "full_name": "General Employee",
        "email": "employee@finguard.com"
    }
}

USERS_DB = {}


def get_password_hash(password: str) -> str:
    if pwd_context is None:
        return f"sha256:{hashlib.sha256(password.encode()).hexdigest()}"
    
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Password hashing error: {e}")
        return f"sha256:{hashlib.sha256(password.encode()).hexdigest()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("sha256:"):
        expected_hash = f"sha256:{hashlib.sha256(plain_password.encode()).hexdigest()}"
        return expected_hash == hashed_password
    
    if pwd_context is None:
        return False
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return sha256_hash == hashed_password

def initialize_users_db():
    global USERS_DB
    if not USERS_DB:
        for username, user_data in _USERS_DB_TEMPLATE.items():
            user_copy = user_data.copy()
            user_copy["hashed_password"] = get_password_hash(user_data["password"])
            del user_copy["password"]  
            USERS_DB[username] = user_copy

initialize_users_db()


def get_user(username: str) -> Optional[dict]:
    return USERS_DB.get(username)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    
    return User(
        username=user["username"],
        role=user["role"],
        full_name=user.get("full_name"),
        email=user.get("email")
    )


def get_demo_credentials() -> dict:
    return {
        "Finance Team": {"username": "john_finance", "password": "finance123"},
        "Marketing Team": {"username": "sarah_marketing", "password": "marketing123"},
        "HR Team": {"username": "mike_hr", "password": "hr123"},
        "Engineering Team": {"username": "alex_engineering", "password": "engineering123"},
        "C-Level Executive": {"username": "ceo", "password": "ceo123"},
        "General Employee": {"username": "employee", "password": "employee123"}
    }