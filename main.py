import os
import logging

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import engine, get_db

# Configuración de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crea las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User API",
    description="API RESTful para la gestión de usuarios",
    version="1.0.0"
)

@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario en el sistema."""
    # Verificamos si el email o username ya existen (Manejo de edge cases)
    db_user = db.query(models.User).filter((models.User.email == user.email) | (models.User.username == user.username)).first()
    if db_user:
        logger.warning(f"Intento de crear usuario duplicado: {user.email}")
        raise HTTPException(status_code=400, detail="El email o el nombre de usuario ya están registrados")
    
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"Usuario creado exitosamente: {new_user.id}")
    return new_user

@app.get("/users/", response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtiene una lista de todos los usuarios con paginación."""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Obtiene un usuario específico por su ID."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        logger.error(f"Usuario no encontrado: {user_id}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Actualiza la información de un usuario existente."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    update_data = user_update.model_dump(exclude_unset=True) # Solo actualiza campos enviados
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    logger.info(f"Usuario actualizado: {user_id}")
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Elimina permanentemente un usuario de la base de datos."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(db_user)
    db.commit()
    logger.info(f"Usuario eliminado: {user_id}")
    return None

@app.get("/", include_in_schema=False)
def root():
    """Redirige la ruta principal a la documentación de la API."""
    return RedirectResponse(url="/docs")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Devuelve el ícono de la pestaña del navegador."""
    file_path = "favicon.ico"
    # Verificamos si pusiste el archivo en la carpeta
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        # Si olvidas poner el archivo, no se cae la aplicación, solo ignoramos la petición
        return {"message": "Favicon no encontrado"}