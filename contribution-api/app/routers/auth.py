from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import hashlib
import secrets
import uuid

from app.database import get_db
from app.models import Contributor, ContributorType, ContributorStanding, RateLimitTier
from app.config import settings

router = APIRouter()
security = HTTPBearer()

# ─── Schemas ─────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    contributor_type: ContributorType
    contact_email: EmailStr
    preferred_name: Optional[str] = None
    pathway_interest: Optional[List[str]] = None
    agree_to_terms: bool

class RegisterResponse(BaseModel):
    contributor_id: str
    status: str
    api_key: str
    api_key_expires_at: Optional[datetime]
    rate_limit_tier: str
    message: str

class LoginRequest(BaseModel):
    contact_email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    contributor_id: str
    rate_limit_tier: str

class ContributorProfile(BaseModel):
    contributor_id: str
    contributor_type: str
    contact_email: str
    preferred_name: Optional[str]
    status: str
    rate_limit_tier: str
    since: datetime

# ─── Helpers ─────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

def generate_api_key() -> str:
    return f"pv_{secrets.token_urlsafe(32)}"

def generate_token() -> str:
    return secrets.token_urlsafe(64)

# ─── Auth dependency ─────────────────────────────────────────────
async def get_current_contributor(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Contributor:
    token = credentials.credentials

    # Try API key first
    contributor = db.query(Contributor).filter(Contributor.api_key == token).first()
    if contributor:
        if contributor.api_key_expires_at and contributor.api_key_expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="API key expired")
        return contributor

    # Try bearer token (simplified — in production, use JWT)
    # For now, treat token as API key
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# ─── Endpoints ───────────────────────────────────────────────────
@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if not req.agree_to_terms:
        raise HTTPException(status_code=400, detail="You must agree to the contribution standards")

    # Check if email already exists
    existing = db.query(Contributor).filter(Contributor.contact_email == req.contact_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    contributor_id = f"cust_{uuid.uuid4().hex[:12]}"
    api_key = generate_api_key()

    contributor = Contributor(
        id=contributor_id,
        contributor_type=req.contributor_type,
        contact_email=req.contact_email,
        preferred_name=req.preferred_name,
        standing=ContributorStanding.PENDING,
        rate_limit_tier=RateLimitTier.PUBLIC_REGISTERED,
        api_key=api_key,
        api_key_expires_at=datetime.utcnow() + timedelta(days=30),
        agree_to_terms=True,
    )
    db.add(contributor)
    db.commit()

    return RegisterResponse(
        contributor_id=contributor_id,
        status="pending",
        api_key=api_key,
        api_key_expires_at=contributor.api_key_expires_at,
        rate_limit_tier=contributor.rate_limit_tier.value,
        message="Account created. Submit your first contribution to complete onboarding.",
    )

@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    contributor = db.query(Contributor).filter(Contributor.contact_email == req.contact_email).first()
    if not contributor or not contributor.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(req.password, contributor.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate tokens
    access_token = generate_token()
    refresh_token = generate_token()

    return LoginResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        contributor_id=contributor.id,
        rate_limit_tier=contributor.rate_limit_tier.value,
    )

@router.get("/me", response_model=ContributorProfile)
async def get_me(contributor: Contributor = Depends(get_current_contributor)):
    return ContributorProfile(
        contributor_id=contributor.id,
        contributor_type=contributor.contributor_type.value,
        contact_email=contributor.contact_email,
        preferred_name=contributor.preferred_name,
        status=contributor.standing.value,
        rate_limit_tier=contributor.rate_limit_tier.value,
        since=contributor.created_at,
    )

@router.post("/revoke", status_code=204)
async def revoke_token(contributor: Contributor = Depends(get_current_contributor)):
    # In a real implementation, revoke the token here
    # For now, just return 204
    return None
