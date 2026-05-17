import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import models
from database import get_db

SECRET_KEY = "9a3f470ffd442a047cdfb39cfbf1320a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 

# TOKEN BLOCKLIST for logout method
TOKEN_BLOCKLIST = set()

def add_token_to_blocklist(token: str):
    """Agrega un token a la lista de revocados."""
    TOKEN_BLOCKLIST.add(token)

def is_token_revoked(token: str) -> bool:
    """Verifica si un token ha sido revocado."""
    return token in TOKEN_BLOCKLIST

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plains password to match with DB hash."""
    try:
        # bcrypt requires utf-8 encoding
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    """Generates secure has using bcrypt."""

    pwd_bytes = password.encode('utf-8')
    # Generate random salt and create hash
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    # Return as plain string
    return hashed_bytes.decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# get user dependency
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if is_token_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is Closed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credentials couldn't be validated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user