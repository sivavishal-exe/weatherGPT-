from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class UserCreate(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN, description="Valid email address")
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")
    full_name: Optional[str] = Field(None, max_length=255)


class UserLogin(BaseModel):
    email: str = Field(..., pattern=EMAIL_PATTERN)
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SavedLocationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=250)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    custom_alias: Optional[str] = None


class SavedLocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    location_id: int
    custom_alias: Optional[str] = None
    is_favorite: bool
    created_at: datetime
