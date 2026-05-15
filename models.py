from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from datetime import datetime, timezone
import enum
from database import Base

# Roles permitidos
class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"
    guest = "guest"

def get_utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)
    
    # Usamos la nueva función para evitar el DeprecationWarning
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
    
    active = Column(Boolean, default=True)