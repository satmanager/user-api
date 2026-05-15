from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from models import RoleEnum

class UserBase(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "ecastro"})
    email: EmailStr = Field(..., json_schema_extra={"example": "ecastro@testing.com"})
    first_name: str = Field(..., json_schema_extra={"example": "Edgardo"})
    last_name: str = Field(..., json_schema_extra={"example": "Castro"})
    role: RoleEnum = Field(default=RoleEnum.user, json_schema_extra={"example": "user"}) #admin, user or guest
    active: bool = Field(default=True, json_schema_extra={"example": True})

# Creación (POST)
class UserCreate(UserBase):
    pass

# Update (PUT)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(default=None, json_schema_extra={"example": "ecastro"})
    email: Optional[EmailStr] = Field(default=None, json_schema_extra={"example": "ecastro@testing.com"})
    first_name: Optional[str] = Field(default=None, json_schema_extra={"example": "Edgardo"})
    last_name: Optional[str] = Field(default=None, json_schema_extra={"example": "Castro"})
    role: Optional[RoleEnum] = Field(default=None, json_schema_extra={"example": "admin"}) #admin, user or guest
    active: Optional[bool] = Field(default=None, json_schema_extra={"example": False})

class UserResponse(UserBase):
    id: int = Field(..., json_schema_extra={"example": 1})
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)