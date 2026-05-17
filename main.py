import os
import logging

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

import models, schemas, auth
from database import engine, get_db

# Configuración de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crea las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User API",
    description="API RESTful for user management",
    version="1.0.0"
)

@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login to obtain JWT token. Use 'username' and 'password'."""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout", status_code=status.HTTP_200_OK)
def logout(token: str = Depends(auth.oauth2_scheme)):
    """
    Closes current user revoking the current token
    """
    auth.add_token_to_blocklist(token)
    return {"message": "Closed session succesfully"}

@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Creates new user"""
    # Verificamos si el email o username ya existen (Manejo de edge cases)
    db_user = db.query(models.User).filter((models.User.email == user.email) | (models.User.username == user.username)).first()
    if db_user:
        logger.warning(f"Trying to create duplicated user: {user.email}")
        raise HTTPException(status_code=400, detail="Email or Username already registered")

    hashed_password = auth.get_password_hash(user.password)
    
    user_data = user.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password

    new_user = models.User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User created successfully {new_user.id}")
    return new_user

@app.get("/users/", response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Get all user list with pagination"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Get specific user by ID."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        logger.error(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Actualiza la información de un usuario existente."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True) # Solo actualiza campos enviados
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    logger.info(f"Updated user: {user_id}")
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Permanently Remove user from database"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    logger.info(f"Removed user: {user_id}")
    return None

@app.get("/", include_in_schema=False)
def root():
    """Redirects base URL to API Documentation."""
    return RedirectResponse(url="/docs")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Favicon"""
    file_path = "favicon.ico"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"message": "Favicon not found"}