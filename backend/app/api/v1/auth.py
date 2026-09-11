from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories import user_repo, location_repo, saved_location_repo
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, SavedLocationCreate, SavedLocationResponse
from app.core.security import create_jwt_token, decode_jwt_token
from app.core.logging import logger

router = APIRouter(prefix="/auth", tags=["Authentication & User Security"])


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """FastAPI Dependency enforcing authenticated User Bearer Token access."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Bearer authentication token."
        )
    token = authorization.split(" ")[1]
    payload = decode_jwt_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token."
        )
    user = await user_repo.get_by_id(db, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account inactive or not found."
        )
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user with sanitized email and hashed password."""
    existing = await user_repo.get_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email already registered."
        )
    user = await user_repo.create_user(db, user_in.email, user_in.password, user_in.full_name)
    logger.info(f"New user registered: {user.email}")
    return user


@router.post("/login", response_model=Token)
async def login_user(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user credentials and issue signed JWT access token."""
    user = await user_repo.authenticate(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    access_token = create_jwt_token({"sub": user.id, "email": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    """Retrieve profile details for the authenticated user."""
    return current_user


@router.get("/saved-locations", response_model=List[SavedLocationResponse])
async def get_saved_locations(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve saved locations for authenticated user."""
    return await saved_location_repo.get_by_user(db, current_user.id)


@router.post("/saved-locations", response_model=SavedLocationResponse, status_code=status.HTTP_201_CREATED)
async def add_saved_location(
    loc_in: SavedLocationCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save a favorite location for authenticated user."""
    loc = await location_repo.get_or_create(db, loc_in.name, loc_in.latitude, loc_in.longitude)
    saved = await saved_location_repo.create(db, {
        "user_id": current_user.id,
        "location_id": loc.id,
        "custom_alias": loc_in.custom_alias or loc_in.name,
        "is_favorite": True
    })
    return saved
